#!/usr/bin/env python3
"""H5a: simulate adaptive checking on per-problem plan results (no generation).

Adds --step problems at a time in random order and stops once the 95% bootstrap
CI of (leader - runner-up) excludes 0. Repeats over --replicates orders.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agentqo.metrics.io import args_config, mark_done, read_csv, resolve_output_dir, write_csv, write_json  # noqa: E402


def simulate_stop(scores: np.ndarray, step: int, rng: np.random.Generator, n_boot: int = 1000) -> tuple:
    """scores[plan, problem]. Returns (index of the chosen plan, problems used)."""
    n = scores.shape[1]
    order = rng.permutation(n)
    used = min(step, n)
    while True:
        seen = scores[:, order[:used]]
        mean = seen.mean(1)
        lead, runner = np.argsort(-mean, kind="stable")[:2]
        diff = seen[lead] - seen[runner]
        boots = diff[rng.integers(0, used, (n_boot, used))].mean(1)
        if np.percentile(boots, 2.5) > 0 or used >= n:
            return int(lead), used
        used = min(used + step, n)


def run(per_problem, step: int, replicates: int, fixed_n: int, seed: int) -> Dict:
    by_plan = defaultdict(dict)
    for r in per_problem:
        by_plan[r["plan"]][r["task_id"]] = float(r["correct"])
    plans = list(by_plan)
    tasks = sorted(next(iter(by_plan.values())))
    scores = np.array([[by_plan[p][t] for t in tasks] for p in plans])
    truth = scores.mean(1)
    rng = np.random.default_rng(seed)
    picks = [simulate_stop(scores, step, rng) for _ in range(replicates)]
    gap = np.array([truth.max() - truth[i] for i, _ in picks])
    used = np.array([u for _, u in picks], dtype=float)
    within = gap <= 0.02
    half = used <= fixed_n / 2
    return {"n_plans": len(plans), "n_problems": len(tasks), "fixed_n": fixed_n, "step": step, "replicates": replicates,
            "best_plan": plans[int(truth.argmax())], "best_accuracy": float(truth.max()),
            "mean_problems_used": float(used.mean()), "median_problems_used": float(np.median(used)),
            "mean_gap": float(gap.mean()), "share_within_2_points": float(within.mean()),
            "share_at_most_half": float(half.mean()), "share_both": float((within & half).mean()),
            "picks": [{"plan": plans[i], "problems_used": u, "gap": float(truth.max() - truth[i])} for i, u in picks]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--per-problem", required=True, help="h3_per_problem.csv")
    ap.add_argument("--step", type=int, default=25)
    ap.add_argument("--fixed-n", type=int, default=400)
    ap.add_argument("--replicates", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--output-dir", default="results/v2/adaptive")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    out, done = resolve_output_dir(args.output_dir, args_config(args), create=not args.dry_run)
    if args.dry_run:
        print(f"would simulate {args.replicates} adaptive checks on {args.per_problem}, into {out}")
        return
    if done:
        print(f"already finished: {out}")
        return
    res = run(read_csv(args.per_problem), args.step, args.replicates, args.fixed_n, args.seed)
    write_csv(out / "adaptive_picks.csv", res.pop("picks"))
    if res["n_problems"] < args.fixed_n:
        print(f"WARNING: only {res['n_problems']} problems; a fixed {args.fixed_n}-problem check needs more")
    write_json(out / "adaptive_summary.json", res)
    mark_done(out)
    print(f"mean problems {res['mean_problems_used']:.0f}, within 2 points {res['share_within_2_points']:.2f}; wrote {out}")


if __name__ == "__main__":
    main()
