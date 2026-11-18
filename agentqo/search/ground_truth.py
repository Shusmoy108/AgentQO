"""Ground truth for offline plan search: per-plan accuracy, API cost and p95 latency.

A plan is a genome: one tier index per agent (0 = small, 1 = large, 2 = xl). Truth values are
looked up from the exhaustive lease runs (results/v2/P*), never from a model call.

- accuracy: h3_plans.csv (mean over eval problems); per problem from h3_per_problem.csv.
- API cost (USD per problem): P6/<setting>/cost/plan_costs.csv api_usd (math_tiers: tier_pareto.csv),
  the same files tools_lease/search_gt.py used for results/v2/P6/search_ground_truth.md.
- latency (3rd objective): X1 measured p95 at K=16 (mean over repeats) per placement; where X1 did
  not time a plan, the latsim FROZEN tag prediction (pred_p95, K=16), flagged predicted=True.
"""

from __future__ import annotations

import csv
import io
import subprocess
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "results" / "v2"
LATSIM_TAG = "latsim-frozen-20261117T133315Z"
PLACEMENTS = ("separate", "shared")
K = 16

# setting, label dir(s), plan phase. math_tiers: large labels from P1/math_q15_7 (same 1.5B -> 7B
# pair, as scripts/v2/tiers_report.py), xl labels from P2b/math_tiers (1.5B -> 14B).
SETTINGS: Dict[str, Tuple[Dict[str, str], str]] = {
    "math_q15_7": ({"large": "P1/math_q15_7"}, "P2"),
    "hotpot_q15_7": ({"large": "P1/hotpot_q15_7"}, "P2"),
    "hotpot_iso_q15_7": ({"large": "P1/hotpot_iso_q15_7"}, "P2"),
    "math_q3_14": ({"large": "P3/math_q3_14"}, "P3"),
    "math_granite": ({"large": "P4/math_granite"}, "P4"),
    "hotpot_granite": ({"large": "P4/hotpot_granite"}, "P4"),
    "hotpot_iso_granite": ({"large": "P4/hotpot_iso_granite"}, "P4"),
    "math_phi": ({"large": "P4b/math_phi"}, "P4b"),
    "hotpot_phi": ({"large": "P4b/hotpot_phi"}, "P4b"),
    "complex_q15_7": ({"large": "P2c/complex_q15_7"}, "P2c"),
    "math_tiers": ({"large": "P1/math_q15_7", "xl": "P2b/math_tiers"}, "P2b"),
}


# Settings whose files do not follow <phase>/<setting>/plans: plans folder, API cost priced from h3_calls with
# agentqo.metrics.cost_model.price_plans (reproduces P6's math_tiers api_usd exactly).
# x3_cross_family (L2-X3): small = Qwen2.5-7B, large = Granite 8B, xl = Phi-4; tiers priced by tier name.
EXTRA: Dict[str, Dict[str, object]] = {
    "x3_cross_family": {"labels": {"large": "X3_vmB/labels_q7_G8", "xl": "X3_vmB/labels_q7_P4"},
                        "plans": "X3_vmB/plans_2"},
    # X5 MATH-500 (Qwen2.5 1.5B -> 7B, 6-agent math workflow, 300 eval problems); no latency truth.
    "math500_q15_7": {"labels": {"large": "X5/math500_q15_7"}, "plans": "X5/math500_q15_7/plans"},
}


def calls_cost(plans_dir: Path) -> Dict[str, float]:
    import gzip
    from agentqo.metrics.cost_model import load_prices, price_plans
    f = plans_dir / "h3_calls.csv"
    fh = open(f) if f.exists() else gzip.open(str(f) + ".gz", "rt")
    with fh:
        rows = price_plans(csv.DictReader(fh), load_prices(ROOT / "configs" / "v2_prices.yaml"))
    return {r["plan"]: float(r["api_usd"]) for r in rows}


def available(name: str) -> bool:
    if name in EXTRA:
        return (V2 / str(EXTRA[name]["plans"]) / "h3_plans.csv").exists()
    return (V2 / SETTINGS[name][1] / name / "plans" / "h3_plans.csv").exists()


def rd(p) -> List[Dict[str, str]]:
    with open(p) as f:
        return list(csv.DictReader(f))


@dataclass
class Setting:
    name: str
    agents: List[str]                 # topological order (tier_* column order)
    tiers: List[str]                  # ["small", "large"] or ["small", "large", "xl"]
    names: List[str]                  # plan names, row i
    genomes: np.ndarray               # (P, n) tier index
    acc: np.ndarray                   # (P,)
    cost: np.ndarray                  # (P,) api_usd per problem
    per_problem: np.ndarray           # (P, problems) 0/1
    problems: List[str]
    label_dirs: Dict[str, str]
    latency: Dict[str, np.ndarray] = field(default_factory=dict)   # placement -> (P,) p95 s
    lat_predicted: Dict[str, np.ndarray] = field(default_factory=dict)  # placement -> (P,) bool
    index: Dict[Tuple[int, ...], int] = field(default_factory=dict)

    def __post_init__(self):
        self.index = {tuple(int(x) for x in g): i for i, g in enumerate(self.genomes)}

    @property
    def n(self) -> int:
        return len(self.agents)

    @property
    def size(self) -> int:
        return len(self.names)

    def row(self, genome) -> int:
        return self.index[tuple(int(x) for x in genome)]


def _git_show(tag: str, path: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{tag}:{path}"], check=True,
                          capture_output=True, text=True).stdout


@lru_cache(maxsize=1)
def latsim_predictions() -> Dict[Tuple[str, str, str], float]:
    """(setting, plan, placement) -> pred_p95 at K=16, read from the frozen latsim tag (read only)."""
    out = {}
    for r in csv.DictReader(io.StringIO(_git_show(LATSIM_TAG, "results/latsim/predictions.csv"))):
        if int(r["k"]) == K:
            out[(r["setting"], r["plan"], r["placement"])] = float(r["pred_p95"])
    return out


def measured_latency(setting: str, placement: str) -> Dict[str, float]:
    """X1 p95 at K=16, mean over repeats; X1 (VM-A) and X1_vmB folders."""
    vals: Dict[str, List[float]] = {}
    for d in ("X1", "X1_vmB"):
        f = V2 / d / setting / placement / "placement_summary.csv"
        if f.exists():
            for r in rd(f):
                if int(r["k"]) == K:
                    vals.setdefault(r["plan"], []).append(float(r["p95_s"]))
    return {p: float(np.mean(v)) for p, v in vals.items()}


def load_setting(name: str, with_latency: bool = True) -> Setting:
    if name in EXTRA:
        label_dirs, pdir = dict(EXTRA[name]["labels"]), V2 / str(EXTRA[name]["plans"])
    else:
        label_dirs, phase = SETTINGS[name]
        pdir = V2 / phase / name / "plans"
    rows = rd(pdir / "h3_plans.csv")
    agents = [k[5:] for k in rows[0] if k.startswith("tier_")]
    tiers = ["small", "large"] + (["xl"] if "xl" in label_dirs else [])
    names = [r["plan"] for r in rows]
    genomes = np.array([[tiers.index(r[f"tier_{a}"]) for a in agents] for r in rows], dtype=np.int8)
    acc = np.array([float(r["accuracy"]) for r in rows])
    if name in EXTRA:
        cmap = calls_cost(pdir)
    else:
        cfile = (V2 / "P6/math_tiers/tiers/tier_pareto.csv" if name == "math_tiers"
                 else V2 / "P6" / name / "cost" / "plan_costs.csv")
        cmap = {r["plan"]: float(r["api_usd"]) for r in rd(cfile)}
    cost = np.array([cmap[n] for n in names])
    pp = rd(pdir / "h3_per_problem.csv")
    problems = sorted({r["task_id"] for r in pp})
    pi, ni = {p: j for j, p in enumerate(problems)}, {n: i for i, n in enumerate(names)}
    per = np.full((len(names), len(problems)), np.nan)
    for r in pp:
        per[ni[r["plan"]], pi[r["task_id"]]] = float(r["correct"])
    s = Setting(name, agents, tiers, names, genomes, acc, cost, per, problems, label_dirs)
    if with_latency:
        attach_latency(s)
    return s


def attach_latency(s: Setting) -> None:
    pred = latsim_predictions()
    for pl in PLACEMENTS:
        meas = measured_latency(s.name, pl)
        lat, flag = np.empty(s.size), np.zeros(s.size, bool)
        for i, n in enumerate(s.names):
            if n in meas:
                lat[i] = meas[n]
            else:
                lat[i], flag[i] = pred[(s.name, n, pl)], True
        s.latency[pl], s.lat_predicted[pl] = lat, flag


# ------------------------------------------------------------------ fronts and hypervolume
def pareto_mask(F: np.ndarray) -> np.ndarray:
    """F: (N, d) objectives, all minimised. True for non-dominated rows (duplicates all kept)."""
    F = np.asarray(F, float)
    if F.ndim == 2 and F.shape[1] == 2 and len(F) > 256:  # O(N log N) sweep on distinct rows
        U, inv = np.unique(F, axis=0, return_inverse=True)   # sorted by F0 then F1
        prev_min = np.r_[np.inf, np.minimum.accumulate(U[:, 1])[:-1]]
        return (~(prev_min <= U[:, 1]))[inv.ravel()]
    le =(F[None, :, :] <= F[:, None, :]).all(-1)
    lt = (F[None, :, :] < F[:, None, :]).any(-1)
    return ~(le & lt).any(1)


def hv2(acc: np.ndarray, cost: np.ndarray, cmax: float) -> float:
    """Area dominated by (cost/cmax, acc) points; reference (cost 1, accuracy 0). Same as search_gt.py."""
    if len(acc) == 0:
        return 0.0
    c = np.minimum(np.asarray(cost, float) / cmax, 1.0)
    a = np.asarray(acc, float)
    m = pareto_mask(np.c_[c, -a])
    order = np.argsort(c[m], kind="stable")
    c, a = c[m][order], a[m][order]
    nxt = np.r_[c[1:], 1.0]
    return float(((nxt - c) * a).sum())


def hv3(acc, cost, lat, cmax: float, lmax: float) -> float:
    """Volume dominated in (cost/cmax, latency/lmax, -accuracy); reference (1, 1, accuracy 0).
    Exact slicing over latency levels: volume = sum over slices of 2D HV of points at or below."""
    acc, cost, lat = map(lambda x: np.asarray(x, float), (acc, cost, lat))
    if len(acc) == 0:
        return 0.0
    ln = np.minimum(lat / lmax, 1.0)
    m = pareto_mask(np.c_[cost, ln, -acc])  # dominated points add no volume
    acc, cost, ln = acc[m], cost[m], ln[m]
    levels = np.unique(ln)
    vol = 0.0
    for i, l0 in enumerate(levels):
        l1 = levels[i + 1] if i + 1 < len(levels) else 1.0
        m = ln <= l0
        vol += (l1 - l0) * hv2(acc[m], cost[m], cmax)
    return vol


def true_front(s: Setting) -> np.ndarray:
    return np.flatnonzero(pareto_mask(np.c_[s.cost, -s.acc]))


def true_hv(s: Setting) -> float:
    return hv2(s.acc, s.cost, s.cost.max())


def load_all(names: Optional[List[str]] = None) -> Dict[str, Setting]:
    return {n: load_setting(n) for n in (names or SETTINGS)}
