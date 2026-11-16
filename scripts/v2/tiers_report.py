#!/usr/bin/env python3
"""A16: estimator errors and the accuracy-API-cost Pareto front over multi-tier plans.

    python3 scripts/v2/tiers_report.py --plans P2b/math_tiers/plans/h3_plans.csv \
        --calls P2b/math_tiers/plans/h3_calls.csv --labels-large P1/math_q15_7/labels/labels_v2.csv \
        --labels-xl P2b/math_tiers/labels/labels_v2.csv --output-dir P6/math_tiers/tiers

A plan is the set of options "agent=tier" for its agents not on the small tier, so the binary
estimators (rules_report.estimator_tables, m = 3, held-out plans as in H2a) apply unchanged:
singles are one agent at one tier, pairs are two agents. Also reported: independence from the
labels (all_small eval accuracy + each agent's label UV for its tier, 1.5B->7B or 1.5B->14B).
Predictions: (a) independence MAE >= 0.05 (additive and multiplicative, held out); (b)
pairwise_corrected MAE below both; (c) at most 10% of plans on the accuracy-API-cost front.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, FrozenSet, List

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agentqo.metrics.cost_model import load_prices, price_plans  # noqa: E402
from agentqo.metrics.io import args_config, mark_done, read_csv, resolve_output_dir, write_csv, write_json  # noqa: E402
from scripts.v2.rules_report import estimator_tables  # noqa: E402


def plan_options(row: Dict[str, str]) -> FrozenSet[str]:
    return frozenset(f"{k[5:]}={v}" for k, v in row.items() if k.startswith("tier_") and v != "small")


def pareto_front(acc: np.ndarray, cost: np.ndarray) -> np.ndarray:
    """True where no other plan is at least as accurate and as cheap, and better in one."""
    dom = ((acc[None, :] >= acc[:, None]) & (cost[None, :] <= cost[:, None])
           & ((acc[None, :] > acc[:, None]) | (cost[None, :] < cost[:, None])))
    return ~dom.any(axis=1)


def label_estimates(plans: List[FrozenSet[str]], base: float, uv: Dict[str, float]) -> np.ndarray:
    return np.clip([base + sum(uv[o] for o in p) for p in plans], 0, 1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--plans", required=True)
    ap.add_argument("--calls", required=True)
    ap.add_argument("--labels-large", default="", help="labels_v2.csv, small -> large (1.5B -> 7B)")
    ap.add_argument("--labels-xl", default="", help="labels_v2.csv, small -> xl (1.5B -> 14B)")
    ap.add_argument("--prices", default="configs/v2_prices.yaml")
    ap.add_argument("--pairs-m", type=int, default=3)
    ap.add_argument("--output-dir", default="results/v2/tiers")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    out, done = resolve_output_dir(args.output_dir, args_config(args), create=not args.dry_run)
    if args.dry_run:
        print(f"would analyse tier plans {args.plans} into {out}")
        return
    if done:
        print(f"already finished: {out}")
        return

    rows = read_csv(args.plans)
    true_acc = {plan_options(r): float(r["accuracy"]) for r in rows}
    options = sorted({o for p in true_acc for o in p})
    summary_rows, detail, thresholds = estimator_tables(true_acc, options, args.pairs_m)

    plans = list(true_acc)
    truth = np.array([true_acc[p] for p in plans])
    held = {d["upgraded"]: d["held_out"] for d in detail if d["estimator"] == "independence_additive"}
    held_mask = np.array([held[",".join(sorted(p)) or "none"] for p in plans])
    if args.labels_large and args.labels_xl:  # independence from the labels
        uv = {f"{r['agent']}=large": float(r["uv"]) for r in read_csv(args.labels_large)}
        uv.update({f"{r['agent']}=xl": float(r["uv"]) for r in read_csv(args.labels_xl)})
        e = label_estimates(plans, true_acc[frozenset()], uv)
        summary_rows.append({"estimator": "independence_labels", "m": args.pairs_m, "n_plans": len(plans),
                             "n_held_out": int(held_mask.sum()), "mae_all": float(np.abs(e - truth).mean()),
                             "mae_held_out": float(np.abs(e - truth)[held_mask].mean())})
    write_csv(out / "tier_estimator_errors.csv", summary_rows)
    write_csv(out / "tier_plan_estimates.csv", detail)

    cost = {r["plan"]: float(r["api_usd"]) for r in price_plans(read_csv(args.calls), load_prices(args.prices))}
    names = [r["plan"] for r in rows]
    acc, usd = np.array([float(r["accuracy"]) for r in rows]), np.array([cost[n] for n in names])
    front = pareto_front(acc, usd)
    write_csv(out / "tier_pareto.csv", [{"plan": n, "accuracy": a, "api_usd": c, "on_front": bool(f)}
                                        for n, a, c, f in zip(names, acc, usd, front)])

    mae = {r["estimator"]: r["mae_held_out"] for r in summary_rows}
    indep = [mae["independence_additive"], mae["independence_multiplicative"]]
    summary = {"n_plans": len(rows), "n_options": len(options), "accuracy_thresholds": thresholds,
               "mae_held_out": mae, "front_size": int(front.sum()), "front_share": float(front.mean()),
               "a16_a_independence_mae_ge_5pt": bool(min(indep) >= 0.05),
               "a16_b_pairwise_lower": bool(mae["pairwise_corrected"] < min(indep)),
               "a16_c_front_share_le_10pct": bool(front.mean() <= 0.10)}
    write_json(out / "tiers_summary.json", summary)
    mark_done(out)
    print(f"{len(rows)} plans, front {front.sum()} ({100 * front.mean():.1f}%), held-out MAE "
          + ", ".join(f"{k} {v:.3f}" for k, v in mae.items()))


if __name__ == "__main__":
    main()
