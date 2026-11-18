#!/usr/bin/env python3
"""S5b (confirmatory, docs/search_prereg_s5b.md): complex_q15_7 plans chosen on the 200 eval problems, re-scored
on 200 new GSM8K problems (X8).

    python3 scripts/search/s5b.py                 # reads results/v2/X8*/complex_q15_7/plans/h3_plans.csv
    python3 scripts/search/s5b.py --x8 FILE --out DIR   # dry run on another file (used once, on eval data, pre-tag)
Refuses to run on the real X8 file unless the S5b registration tag exists. Per method and seed: the verified
front (non-dominated by eval accuracy and eval API cost among the plans the method verified); retention = HV of
those plans with X8 accuracy / HV with eval accuracy. Plans not scored in X8 are dropped from both HVs and counted.
HELD if mean retention >= 0.95 for both methods, PARTIAL if for one, FAILED if neither.
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
from agentqo.search.metrics import budget_for  # noqa: E402
from agentqo.search.surrogates import label_terms  # noqa: E402
from scripts.search.summarize import ci  # noqa: E402

TAG_PREFIX = "search-prereg-s5b-"
SETTING, FRAC, SEEDS = "complex_q15_7", 0.10, range(30)
METHODS = ("nsga2_pairwise_m3", "nsga2_active_m3")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x8", default=None)
    ap.add_argument("--out", default=str(ROOT / "results" / "search" / "s5b"))
    a = ap.parse_args()
    if a.x8 is None:
        tags = subprocess.run(["git", "-C", str(ROOT), "tag", "-l", TAG_PREFIX + "*"], capture_output=True, text=True).stdout
        if not tags.strip():
            sys.exit("S5b registration tag missing; refusing to read X8")
        files = sorted(V2.glob(f"X8*/{SETTING}/plans/h3_plans.csv"))
        if not files:
            sys.exit("X8 not landed; S5b stays PENDING")
        f = files[0]
    else:
        f = Path(a.x8)
    s = load_setting(SETTING, with_latency=False)
    x8 = {r["plan"]: float(r["accuracy"]) for r in csv.DictReader(open(f))}
    terms, b, cmax = label_terms(s), budget_for(s.size, FRAC), s.cost.max()
    scored = [i for i, n in enumerate(s.names) if n in x8]
    xa = np.array([x8[s.names[i]] for i in scored])
    hv_x8_best = hv2(xa, s.cost[scored], cmax)  # best possible front among the plans X8 scored
    rows = []
    for m in METHODS:
        for seed in SEEDS:
            vr = sorted(set(METHODS_2D[m](s, b, np.random.default_rng(seed), terms=terms).rows))
            front = [r for r, k in zip(vr, pareto_mask(np.c_[s.cost[vr], -s.acc[vr]])) if k]
            have = [r for r in front if s.names[r] in x8]
            he = hv2(s.acc[have], s.cost[have], cmax)
            hx = hv2(np.array([x8[s.names[r]] for r in have]), s.cost[have], cmax)
            rows.append({"method": m, "budget": b, "seed": seed, "front_plans": len(front),
                         "missing_in_x8": len(front) - len(have), "hv_eval": he, "hv_x8": hx,
                         "retention": hx / he if he else np.nan, "x8_vs_best_x8_front": hx / hv_x8_best})
    d = pd.DataFrame(rows)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    d.to_csv(out / "s5b_runs.csv", index=False)
    res = {}
    md_rows = []
    for m, g in d.groupby("method", sort=False):
        lo, hi = ci(g.retention)
        res[m] = g.retention.mean() >= 0.95
        md_rows.append(f"| {m} | {g.retention.mean():.4f} [{lo:.4f}, {hi:.4f}] | {g.x8_vs_best_x8_front.mean():.4f} | "
                       f"{g.front_plans.mean():.1f} | {g.missing_in_x8.sum()} |")
    k = sum(res.values())
    v = "HELD" if k == len(res) else "PARTIAL" if k else "FAILED"
    md = [f"## S5b: {v}", "",
          f"complex_q15_7, B = {b} (10%), seeds 0-29. X8 file: {f.relative_to(ROOT) if f.is_relative_to(ROOT) else f} "
          f"({len(x8)} plans scored of {s.size}). Retention = HV of the verified front's plans with X8 accuracy / with",
          "eval accuracy (eval API cost). Decision: mean retention >= 0.95 per method (docs/search_prereg_s5b.md).", "",
          "| method | retention [95% CI] | X8 HV / best X8 front HV | front plans | front plans missing in X8 (sum) |",
          "|---|---|---|---|---|"] + md_rows + [""]
    (out / "S5b.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
