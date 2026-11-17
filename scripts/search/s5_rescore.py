#!/usr/bin/env python3
"""S5: re-score each method's final front (chosen on the eval problems) on the X2 held-out problems.

    python3 scripts/search/s5_rescore.py [--budget-frac 0.10] [--seeds 30]
Refuses to run unless the registration tag exists (X2 must not be opened before it). X2 accuracy is read
from results/v2/X2*/<setting>/plans/h3_plans.csv (same format as P2). Retention = HV of the verified
front's plans with X2 accuracy / HV of the same plans with eval accuracy (S5 HELD if >= 0.95 everywhere).
Plans missing from X2 are counted and dropped from both HVs.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agentqo.search.ground_truth import ROOT, V2, hv2, load_setting, pareto_mask  # noqa: E402
from agentqo.search.methods import METHODS_2D  # noqa: E402
from agentqo.search.metrics import budget_for  # noqa: E402
from agentqo.search.surrogates import label_terms  # noqa: E402

TAG = "search-prereg-20261117T2127Z"


def x2_files():
    return {f.parent.parent.name: f for d in sorted(V2.glob("X2*")) for f in d.glob("*/plans/h3_plans.csv")}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget-frac", type=float, default=0.10)
    ap.add_argument("--seeds", type=int, default=30)
    a = ap.parse_args()
    subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--verify", f"refs/tags/{TAG}"], check=True, capture_output=True)
    files = x2_files()
    if not files:
        sys.exit("no X2 plan results under results/v2/X2*; S5 stays PENDING")
    out = []
    for name, f in files.items():
        s = load_setting(name, with_latency=False)
        x2 = {r["plan"]: float(r["accuracy"]) for r in csv.DictReader(open(f))}
        terms = label_terms(s)
        b = budget_for(s.size, a.budget_frac)
        for m, fn in METHODS_2D.items():
            for seed in range(a.seeds):
                rows = sorted(set(fn(s, b, np.random.default_rng(seed), terms=terms).rows))
                front = [r for r, k in zip(rows, pareto_mask(np.c_[s.cost[rows], -s.acc[rows]])) if k]
                have = [r for r in front if s.names[r] in x2]
                he = hv2(s.acc[have], s.cost[have], s.cost.max())
                hx = hv2(np.array([x2[s.names[r]] for r in have]), s.cost[have], s.cost.max())
                out.append({"setting": name, "x2_file": str(f.relative_to(ROOT)), "method": m, "budget": b, "seed": seed,
                            "front_plans": len(front), "missing_in_x2": len(front) - len(have),
                            "hv_eval": he, "hv_x2": hx, "retention": hx / he if he else float("nan")})
    p = ROOT / "results" / "search" / "s5_x2_rescore.csv"
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, list(out[0]))
        w.writeheader(); w.writerows(out)
    print(f"wrote {len(out)} rows to {p}")


if __name__ == "__main__":
    main()
