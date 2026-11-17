#!/usr/bin/env python3
"""Run every search method on every available setting x budget x seed; write results/search/results.csv.

    python3 scripts/search/run_search.py [--settings a,b] [--seeds 30] [--workers 8]
CPU only; truth is looked up from the lease results, no model is called.
"""

from __future__ import annotations

import argparse
import os
import csv
import sys
import time
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agentqo.search.ground_truth import PLACEMENTS, SETTINGS, load_setting  # noqa: E402
from agentqo.search.methods import METHODS_2D, METHODS_3D  # noqa: E402
from agentqo.search.metrics import BUDGET_FRACS, budget_for, metrics_2d, metrics_3d, true_hv3  # noqa: E402
from agentqo.search.surrogates import label_terms  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "results" / "search"
COLS = ["setting", "n_plans", "objectives", "method", "budget_frac", "budget", "seed", "hv_ratio", "hv3_ratio",
        "igd", "regret_p25", "regret_p50", "regret_p75", "n_verified", "surrogate_rho", "wall_s", "latency_source"]


def job(args):
    name, seeds = args  # seeds: list of seed ints
    s = load_setting(name)
    t = label_terms(s)
    meas = {p: int((~s.lat_predicted[p]).sum()) for p in PLACEMENTS}
    src = ("measured" if all(v == s.size for v in meas.values())
           else "predicted" if not any(meas.values()) else
           "mixed(" + ",".join(f"{p}:{v}/{s.size}" for p, v in meas.items()) + ")")
    hv3t = true_hv3(s)
    rows = []
    for frac in BUDGET_FRACS:
        b = budget_for(s.size, frac)
        for seed in seeds:
            for m, fn in METHODS_2D.items():
                t0 = time.time()
                V = fn(s, b, np.random.default_rng(seed), terms=t)
                rows.append({"setting": name, "n_plans": s.size, "objectives": "acc_cost", "method": m,
                             "budget_frac": frac, "budget": b, "seed": seed, "wall_s": time.time() - t0,
                             **metrics_2d(s, V.rows, getattr(V, "surrogate", None)), "latency_source": ""})
            for m, fn in METHODS_3D.items():
                t0 = time.time()
                V = fn(s, b, np.random.default_rng(seed), terms=t)
                rows.append({"setting": name, "n_plans": s.size, "objectives": "acc_cost_p95", "method": m,
                             "budget_frac": frac, "budget": b, "seed": seed, "wall_s": time.time() - t0,
                             **metrics_3d(s, V.items, hv3t), "latency_source": src})
    print(f"{name} seeds {seeds[0]}-{seeds[-1]}: {len(rows)} runs", flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--settings", default=",".join(SETTINGS))
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=str(OUT / "results.csv"))
    a = ap.parse_args()
    names = a.settings.split(",")
    jobs = [(n, list(range(k, min(k + 5, a.seeds)))) for n in names for k in range(0, a.seeds, 5)]
    with Pool(a.workers) as pool:
        allrows = [r for rows in pool.map(job, jobs) for r in rows]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, COLS)
        w.writeheader()
        for r in allrows:
            w.writerow({k: r.get(k, "") for k in COLS})
    print(f"wrote {len(allrows)} rows to {a.out}")


if __name__ == "__main__":
    main()
