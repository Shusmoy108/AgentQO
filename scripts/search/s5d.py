#!/usr/bin/env python3
"""S5d (confirmatory, docs/search_prereg_s5d.md): math500_q15_7 and code_c15_7 fronts re-scored on X11 held-out problems.

    python3 scripts/search/s5d.py                       # reads results/v2/X11*/<setting>/plans/h3_plans.csv
    python3 scripts/search/s5d.py --held FILE_math500 FILE_code --out DIR   # dry run (used once, on eval data, pre-tag)
Refuses to read X11 unless the S5d registration tag exists. Same procedure as S5 (scripts/search/s5_rescore.py):
every registered 2-objective method that ran in the new-settings run (code_c15_7: no rule_* methods), budgets
1/2/5/10/20%, seeds 0-29. Per run, the verified front (non-dominated on eval accuracy and eval API cost among the
verified plans); retention = HV of those plans with X11 accuracy / with eval accuracy (eval API cost); plans X11 did
not score are dropped from both HVs and counted. Decision: nsga2_pairwise_m3 at 10%, mean retention over the 30
seeds; HELD if >= 0.95 in both settings, PARTIAL if in one, FAILED if in neither.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agentqo.search.ground_truth import ROOT, V2, hv2, load_setting, pareto_mask  # noqa: E402
from agentqo.search.methods import METHODS_2D  # noqa: E402
from agentqo.search.metrics import BUDGET_FRACS, budget_for  # noqa: E402
from agentqo.search.surrogates import label_terms  # noqa: E402

TAG_PREFIX = "search-prereg-s5d-"
SETTINGS = ("math500_q15_7", "code_c15_7")
MAIN, MAIN_FRAC, SEEDS = "nsga2_pairwise_m3", 0.10, range(30)


def methods(name):
    return {m: f for m, f in METHODS_2D.items() if not (m.startswith("rule_") and name.startswith("code"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--held", nargs=2, default=None)
    ap.add_argument("--out", default=str(ROOT / "results" / "search" / "s5d"))
    a = ap.parse_args()
    if a.held is None:
        tags = subprocess.run(["git", "-C", str(ROOT), "tag", "-l", TAG_PREFIX + "*"], capture_output=True, text=True).stdout
        if not tags.strip():
            sys.exit("S5d registration tag missing; refusing to read X11")
        files = {}
        for n in SETTINGS:
            fs = sorted(V2.glob(f"X11*/{n}/plans/h3_plans.csv"))
            if not fs:
                sys.exit(f"X11 {n} not landed; S5d stays PENDING")
            files[n] = fs[0]
    else:
        files = dict(zip(SETTINGS, map(Path, a.held)))
    rows = []
    for name, f in files.items():
        s = load_setting(name, with_latency=False)
        held = {r["plan"]: float(r["accuracy"]) for r in csv.DictReader(open(f))}
        terms, cmax = label_terms(s), s.cost.max()
        scored = [i for i, n in enumerate(s.names) if n in held]
        hv_best = hv2(np.array([held[s.names[i]] for i in scored]), s.cost[scored], cmax)
        for frac in BUDGET_FRACS:
            b = budget_for(s.size, frac)
            for m, fn in methods(name).items():
                for seed in SEEDS:
                    vr = sorted(set(fn(s, b, np.random.default_rng(seed), terms=terms).rows))
                    front = [r for r, k in zip(vr, pareto_mask(np.c_[s.cost[vr], -s.acc[vr]])) if k]
                    have = [r for r in front if s.names[r] in held]
                    he = hv2(s.acc[have], s.cost[have], cmax)
                    hx = hv2(np.array([held[s.names[r]] for r in have]), s.cost[have], cmax)
                    rows.append({"setting": name, "held_file": str(f), "method": m, "budget_frac": frac, "budget": b,
                                 "seed": seed, "front_plans": len(front), "missing_in_held": len(front) - len(have),
                                 "hv_eval": he, "hv_held": hx, "retention": hx / he if he else np.nan,
                                 "held_vs_best_held_front": hx / hv_best})
    d = pd.DataFrame(rows)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    d.to_csv(out / "s5d_runs.csv", index=False)
    main_rows = d[(d.method == MAIN) & (d.budget_frac == MAIN_FRAC)].groupby("setting", sort=False)
    ok = {n: g.retention.mean() >= 0.95 for n, g in main_rows}
    k = sum(ok.values())
    v = "HELD" if k == len(ok) else "PARTIAL" if k else "FAILED"
    md = [f"## S5d: {v}", "",
          f"{MAIN} at 10% budget, mean over 30 seeds (decision; docs/search_prereg_s5d.md). Retention = HV of the verified",
          "front's plans with X11 accuracy / with eval accuracy (eval API cost).", "",
          "| setting | held-out file | B | retention | X11 HV / best X11 front HV | front plans | missing in X11 |",
          "|---|---|---|---|---|---|---|"]
    for n, g in main_rows:
        md.append(f"| {n} | {Path(g.held_file.iloc[0]).relative_to(ROOT) if Path(g.held_file.iloc[0]).is_relative_to(ROOT) else g.held_file.iloc[0]} | "
                  f"{g.budget.iloc[0]} | {g.retention.mean():.4f} | {g.held_vs_best_held_front.mean():.4f} | "
                  f"{g.front_plans.mean():.1f} | {g.missing_in_held.sum()} |")
    t = d.groupby(["setting", "method", "budget_frac"]).agg(B=("budget", "first"), retention=("retention", "mean"),
                                                            ratio=("held_vs_best_held_front", "mean")).reset_index()
    md += ["", "All registered methods and budgets (reported, not in the decision):", "",
           "| setting | method | budget | B | retention | X11 HV / best X11 front HV |", "|---|---|---|---|---|---|"]
    md += [f"| {r.setting} | {r.method} | {int(r.budget_frac * 100)}% | {r.B} | {r.retention:.4f} | {r.ratio:.4f} |"
           for r in t.itertuples()]
    (out / "S5d.md").write_text("\n".join(md) + "\n")
    print("\n".join(md[:12]))


if __name__ == "__main__":
    main()
