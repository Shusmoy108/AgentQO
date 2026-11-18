"""Per setting x placement x K comparison of every predictor, with a paired bootstrap vs H3c-fair.

    python3 -m agentqo.latsim.compare --name X1 \
        --measured 'results/v2/X1/*/*/placement_summary.csv,results/v2/X1_vm*/*/*/placement_summary.csv'

Predictors: latsim_frozen and h3c (registered) from results/latsim/predictions.csv,
latsim_rev1 / latsim_rev2 from results/latsim/rev{1,2}/predictions.csv, h3cfair and mean_sum_fair from
results/latsim/h3cfair/predictions.csv. Measured = mean over repeats (evaluate.load_measured).
Per group: n plans, share with p95 within 10% / 20%, MAPE p95, Kendall tau of the p95 ranking
within the group. Bootstrap: 5,000 resamples (numpy default_rng(0)) of the group's plans with
replacement, the same resample for both predictors (paired); statistic = within-10% share of
latsim (frozen, rev1) minus H3c-fair's; 95% CI = 2.5 / 97.5 percentiles. Pooled: plans are
resampled within each group (stratified), then pooled.
"""

from __future__ import annotations

import argparse
import csv
import os
from collections import defaultdict
from typing import Dict, List

import numpy as np
from scipy.stats import kendalltau

from agentqo.latsim.evaluate import load_measured, write_csv

SOURCES = {  # predictor -> (file, p50 column, p95 column)
    "latsim_frozen": ("results/latsim/predictions.csv", "pred_p50", "pred_p95"),
    "latsim_rev1": ("results/latsim/rev1/predictions.csv", "pred_p50", "pred_p95"),
    "latsim_rev2": ("results/latsim/rev2/predictions.csv", "pred_p50", "pred_p95"),
    "h3c": ("results/latsim/predictions.csv", "h3c_p50", "h3c_p95"),
    "h3cfair": ("results/latsim/h3cfair/predictions.csv", "h3cfair_p50", "h3cfair_p95"),
    "mean_sum_fair": ("results/latsim/h3cfair/predictions.csv", "mean_sum_fair_p50", "mean_sum_fair_p95"),
}
B, SEED = 5000, 0


def load(sources=SOURCES) -> Dict[tuple, Dict[str, float]]:
    out: Dict[tuple, Dict[str, float]] = defaultdict(dict)
    for name, (path, _, c95) in sources.items():
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                v = r[c95]
                out[(r["setting"], r["plan"], r["placement"], int(r["k"]))][name] = float(v) if v != "" else np.nan
    return out


def group_metrics(pred: np.ndarray, meas: np.ndarray) -> dict:
    ok = ~np.isnan(pred)
    if not ok.any():
        return {"n": 0, "w10": np.nan, "w20": np.nan, "mape95": np.nan, "tau": np.nan}
    e = np.abs(pred[ok] / meas[ok] - 1)
    tau = kendalltau(pred[ok], meas[ok])[0] if ok.sum() >= 3 else np.nan
    return {"n": int(ok.sum()), "w10": float(np.mean(e <= 0.10)), "w20": float(np.mean(e <= 0.20)),
            "mape95": float(np.mean(e)), "tau": float(tau)}


def within10(pred: np.ndarray, meas: np.ndarray) -> np.ndarray:
    return (np.abs(pred / meas - 1) <= 0.10).astype(float)


def bootstrap(groups: List[tuple], a: str, b: str, rng) -> np.ndarray:
    """groups = [(hits dict predictor -> array over plans)]; returns B pooled differences."""
    sizes = [len(g[a]) for g in groups]
    total = sum(sizes)
    out = np.zeros(B)
    for i in range(B):
        s = 0.0
        for g, n in zip(groups, sizes):
            idx = rng.integers(0, n, n)
            s += (g[a][idx] - g[b][idx]).sum()
        out[i] = s / total
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--name", required=True)
    ap.add_argument("--measured", required=True, help="comma-separated globs of placement_summary.csv")
    ap.add_argument("--out", default="results/latsim/compare")
    ap.add_argument("--exclude-k", default="", help="comma-separated K values to leave out")
    args = ap.parse_args()
    ex = {int(x) for x in args.exclude_k.split(",") if x}
    preds = load()
    by = defaultdict(list)
    for m in load_measured(args.measured, ex):
        p = preds.get((m["setting"], m["plan"], m["placement"], m["k"]))
        if p is not None:
            by[(m["setting"], m["placement"], m["k"])].append({**m, **p})
    rows, boot_rows, hit_groups = [], [], []
    rng = np.random.default_rng(SEED)
    rng2 = np.random.default_rng(SEED)  # rev2 on its own stream, so frozen / rev1 draws are as first reported
    for key, rs in sorted(by.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
        meas = np.array([r["meas_p95"] for r in rs])
        row = {"setting": key[0], "placement": key[1], "k": key[2], "n_plans": len(rs)}
        for name in SOURCES:
            for mk, v in group_metrics(np.array([r[name] for r in rs]), meas).items():
                row[f"{name}_{mk}"] = v
        rows.append(row)
        hits = {name: within10(np.array([r[name] for r in rs]), meas) for name in ("latsim_frozen", "latsim_rev1", "latsim_rev2", "h3cfair")}
        hit_groups.append(hits)
        for a in ("latsim_frozen", "latsim_rev1", "latsim_rev2"):
            d = bootstrap([hits], a, "h3cfair", rng2 if a == "latsim_rev2" else rng)
            boot_rows.append({"setting": key[0], "placement": key[1], "k": key[2], "n_plans": len(rs),
                              "comparison": f"{a} - h3cfair", "diff_w10": float(hits[a].mean() - hits["h3cfair"].mean()),
                              "ci_low": float(np.percentile(d, 2.5)), "ci_high": float(np.percentile(d, 97.5))})
    allm = np.concatenate([[r["meas_p95"] for r in rs] for rs in by.values()])
    pooled = {"setting": "ALL", "placement": "all", "k": "all", "n_plans": len(allm)}
    for name in SOURCES:
        pv = np.concatenate([[r[name] for r in rs] for rs in by.values()])
        for mk, v in group_metrics(pv, allm).items():
            pooled[f"{name}_{mk}"] = v
    rows.append(pooled)
    for a in ("latsim_frozen", "latsim_rev1", "latsim_rev2"):
        d = bootstrap(hit_groups, a, "h3cfair", rng2 if a == "latsim_rev2" else rng)
        diff = float(np.concatenate([g[a] for g in hit_groups]).mean() - np.concatenate([g["h3cfair"] for g in hit_groups]).mean())
        boot_rows.append({"setting": "ALL (stratified)", "placement": "all", "k": "all", "n_plans": len(allm),
                          "comparison": f"{a} - h3cfair", "diff_w10": diff,
                          "ci_low": float(np.percentile(d, 2.5)), "ci_high": float(np.percentile(d, 97.5))})
    os.makedirs(args.out, exist_ok=True)
    write_csv(f"{args.out}/{args.name}_by_setting.csv", rows)
    write_csv(f"{args.out}/{args.name}_bootstrap.csv", boot_rows)
    print(f"{args.name}: {len(allm)} points in {len(by)} groups; wrote {args.out}/{args.name}_*.csv")


if __name__ == "__main__":
    main()
