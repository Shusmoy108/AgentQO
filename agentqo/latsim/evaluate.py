"""Score frozen predictions against measured placement runs (held-out X1 / X1b / X6).

    python3 -m agentqo.latsim.evaluate --name X1 \
        --measured 'results/v2/X1*/*/*/placement_summary.csv' --out results/latsim

Measured value per (setting, plan, placement, K) = mean over repeats of p50_s / p95_s
(setting = the folder two levels above the summary). Predictors: latsim, h3c, mean_sum.
Metrics per (setting, placement, K) and pooled: share of plans with p95 within 10% / 20%,
MAPE of p50 and p95, Kendall tau between predicted and measured p95 over plans.
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
from collections import defaultdict
from typing import Dict, List

import numpy as np
from scipy.stats import kendalltau

PREDICTORS = ("latsim", "h3c", "mean_sum")


def load_measured(pattern: str) -> List[dict]:
    acc = defaultdict(list)
    for path in sorted(glob.glob(pattern)):
        setting = os.path.basename(os.path.dirname(os.path.dirname(path)))
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                acc[(setting, r["plan"], r["placement"], int(r["k"]))].append((float(r["p50_s"]), float(r["p95_s"])))
    return [{"setting": s, "plan": p, "placement": pl, "k": k, "n_repeats": len(v),
             "meas_p50": float(np.mean([x[0] for x in v])), "meas_p95": float(np.mean([x[1] for x in v]))}
            for (s, p, pl, k), v in sorted(acc.items())]


def load_predictions(path: str) -> Dict[tuple, dict]:
    with open(path, newline="") as f:
        return {(r["setting"], r["plan"], r["placement"], int(r["k"])): r for r in csv.DictReader(f)}


def n_upgraded(plan: str) -> int:
    """Agents off the small tier: 0 for all_small, -1 for all_large (all), else the count."""
    if plan == "all_small":
        return 0
    if plan == "all_large":
        return -1
    if plan.startswith("only_"):
        return 1
    return plan.count("+") + 1


def plan_type(plan: str) -> str:
    n = n_upgraded(plan)
    if "=" in plan:
        return "tiers:" + ("has_xl" if "=xl" in plan else "large_only")
    return {0: "all_small", -1: "all_large", 1: "one_large"}.get(n, "two_large" if n == 2 else "3+_large")


def join(measured: List[dict], preds: Dict[tuple, dict]) -> List[dict]:
    rows = []
    for m in measured:
        p = preds.get((m["setting"], m["plan"], m["placement"], m["k"]))
        if p is None:
            continue
        row = {**m, "plan_type": plan_type(m["plan"])}
        for name in PREDICTORS:
            for q in ("p50", "p95"):
                v = p.get(f"{name}_{q}", p.get(f"pred_{q}") if name == "latsim" else "")
                row[f"{name}_{q}"] = float(v) if v not in ("", None) else float("nan")
        rows.append(row)
    return rows


def metrics(rows: List[dict], name: str) -> dict:
    p95 = np.array([r[f"{name}_p95"] for r in rows])
    p50 = np.array([r[f"{name}_p50"] for r in rows])
    m95 = np.array([r["meas_p95"] for r in rows])
    m50 = np.array([r["meas_p50"] for r in rows])
    ok = ~np.isnan(p95)
    if not ok.any():
        return {f"{name}_n": 0}
    e95, e50 = p95[ok] / m95[ok] - 1, p50[ok] / m50[ok] - 1
    tau = kendalltau(p95[ok], m95[ok])[0] if ok.sum() >= 3 else float("nan")
    return {f"{name}_n": int(ok.sum()), f"{name}_w10": float(np.mean(np.abs(e95) <= 0.10)),
            f"{name}_w20": float(np.mean(np.abs(e95) <= 0.20)), f"{name}_mape50": float(np.mean(np.abs(e50))),
            f"{name}_mape95": float(np.mean(np.abs(e95))), f"{name}_bias95": float(np.median(e95)),
            f"{name}_tau": float(tau)}


def grouped(rows: List[dict], keys) -> List[dict]:
    by = defaultdict(list)
    for r in rows:
        by[tuple(r[k] for k in keys)].append(r)
    out = []
    for key, rs in sorted(by.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
        row = {**dict(zip(keys, key)), "n_plans": len(rs)}
        for name in PREDICTORS:
            row.update(metrics(rs, name))
        out.append(row)
    return out


def write_csv(path: str, rows: List[dict]) -> None:
    if not rows:
        return
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def coverage(pattern: str, results: str) -> List[dict]:
    """Measured plans vs each setting's plan list (plans.txt, or every plan of h3_calls)."""
    out = []
    for path in sorted(glob.glob(pattern)):
        setting = os.path.basename(os.path.dirname(os.path.dirname(path)))
        root = os.path.dirname(os.path.dirname(path))
        listed = os.path.join(root, "plans.txt")
        with open(path, newline="") as f:
            rs = list(csv.DictReader(f))
        want = [l.strip() for l in open(listed) if l.strip()] if os.path.exists(listed) else None
        reps = defaultdict(set)
        for r in rs:
            reps[(r["plan"], r["k"])].add(r["repeat"])
        for k in sorted({r["k"] for r in rs}, key=int):
            got = {p for (p, kk), v in reps.items() if kk == k}
            out.append({"summary": os.path.relpath(path, results), "setting": setting,
                        "placement": rs[0]["placement"] if rs else "", "k": k,
                        "plans_measured": len(got), "plans_listed": len(want) if want else "",
                        "min_repeats": min(len(v) for (p, kk), v in reps.items() if kk == k)})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--name", required=True, help="test set label, e.g. X1 or X1b")
    ap.add_argument("--measured", required=True, help="glob of placement_summary.csv files")
    ap.add_argument("--predictions", default="results/latsim/predictions.csv")
    ap.add_argument("--results", default="results/v2")
    ap.add_argument("--out", default="results/latsim")
    args = ap.parse_args()
    rows = join(load_measured(args.measured), load_predictions(args.predictions))
    os.makedirs(args.out, exist_ok=True)
    write_csv(f"{args.out}/{args.name}_per_plan.csv", rows)
    write_csv(f"{args.out}/{args.name}_by_setting.csv", grouped(rows, ("setting", "placement", "k")))
    write_csv(f"{args.out}/{args.name}_by_plan_type.csv", grouped(rows, ("placement", "k", "plan_type")))
    write_csv(f"{args.out}/{args.name}_pooled.csv", grouped(rows, ("placement", "k")) + grouped(
        [{**r, "all": "all"} for r in rows], ("all",)))
    write_csv(f"{args.out}/{args.name}_coverage.csv", coverage(args.measured, args.results))
    pooled = grouped([{**r, "all": "all"} for r in rows], ("all",))
    print(f"{args.name}: {len(rows)} (setting, plan, placement, K) points")
    for r in pooled:
        print("  " + ", ".join(f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}" for k, v in r.items()))


if __name__ == "__main__":
    main()
