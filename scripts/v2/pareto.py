#!/usr/bin/env python3
"""M5: joint search over allocation and placement, against the two-step baseline.

    python3 scripts/v2/pareto.py --workflow math --plans .../h3_plans.csv \
        --costs .../plan_costs.csv --calls .../h3_calls.csv --output-dir .../pareto

Predicted plan latency is, per problem, the longest path through the workflow
of per-agent latency, times 1 + beta_{n->m} * u_n * overlap on shared
placements; p95 is taken over problems. u_n and overlap come from the fixed
point in h4_fit.simulate with --k problems in flight.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, FrozenSet, List, Mapping, Sequence

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agentqo.metrics.io import args_config, mark_done, read_csv, resolve_output_dir, write_csv, write_json  # noqa: E402
from agentqo.policies.v2_rules import parse_plan_name, plan_name  # noqa: E402
from scripts.h4_fit import pct, simulate  # noqa: E402
from scripts.run_real_pipeline import WORKFLOWS  # noqa: E402
from scripts.v2.rules_report import parse_upgraded  # noqa: E402

PLACEMENTS = ("separate", "shared", "shared_mps")


class LatencyModel:
    """Per-(problem, node, tier) latency, with the node's mean for missing problems."""

    def __init__(self, calls: Sequence[Mapping], workflow) -> None:
        self.wf, self.topo = workflow, list(workflow.topological_order)
        cells: Dict[tuple, List[float]] = defaultdict(list)
        for c in calls:
            cells[(c["task_id"], c["node_id"], c["fidelity"])].append(float(c["latency_s"]))
        self.tasks = sorted({k[0] for k in cells})
        self.cell = {k: statistics.median(v) for k, v in cells.items()}
        node: Dict[tuple, List[float]] = defaultdict(list)
        for (_, n, tier), v in self.cell.items():
            node[(n, tier)].append(v)
        self.node_mean = {k: float(np.mean(v)) for k, v in node.items()}

    def tier(self, node: str, plan: FrozenSet[str]) -> str:
        return "large" if node in plan else "small"

    def factors(self, plan: FrozenSet[str], betas, k: int) -> Dict[str, float]:
        """Per-tier latency multiplier of this plan on a placement."""
        if betas is None:
            return {"small": 1.0, "large": 1.0}
        nodes = {n: {"fidelity": self.tier(n, plan), "completion_tokens": self.node_mean.get((n, self.tier(n, plan)), 0.0)}
                 for n in self.topo}
        # simulate() reads "tokens" through iso; handing it latency makes iso the identity.
        beta = {"small": betas["large_to_small"], "large": betas["small_to_large"]}
        state = simulate({"mean": nodes}, lambda m, tok, conc: tok, k,
                         lambda m, u_other, ov, conc: 1.0 + beta[m] * u_other * ov)
        return {m: 1.0 + beta[m] * state["busy"]["large" if m == "small" else "small"] * state["overlap"]
                for m in beta}

    def p95(self, plan: FrozenSet[str], factors: Mapping[str, float]) -> float:
        lengths = []
        for task in self.tasks:
            finish: Dict[str, float] = {}
            for n in self.topo:
                tier = self.tier(n, plan)
                lat = self.cell.get((task, n, tier), self.node_mean.get((n, tier), 0.0))
                ready = max((finish[i] for i in self.wf.nodes[n].inputs), default=0.0)
                finish[n] = ready + lat * factors[tier]
            lengths.append(max(finish.values()))
        return pct(lengths, 0.95)


# ------------------------------------------------------------ front + volume
def dominates(a: Mapping, b: Mapping) -> bool:
    no_worse = a["accuracy"] >= b["accuracy"] and a["cost"] <= b["cost"] and a["p95_latency"] <= b["p95_latency"]
    better = a["accuracy"] > b["accuracy"] or a["cost"] < b["cost"] or a["p95_latency"] < b["p95_latency"]
    return no_worse and better


def pareto_front(points: Sequence[Mapping]) -> List[Mapping]:
    return [p for p in points if not any(dominates(q, p) for q in points)]


def hypervolume(points: Sequence[Mapping], cost_max: float, lat_max: float) -> float:
    """Volume dominated in (1-accuracy, cost/cost_max, latency/lat_max), reference (1, 1, 1)."""
    pts = sorted({(1 - p["accuracy"], p["cost"] / cost_max, p["p95_latency"] / lat_max)
                  for p in points if p["cost"] <= cost_max and p["p95_latency"] <= lat_max})
    volume = 0.0
    for i, (x, *_rest) in enumerate(pts):
        next_x = pts[i + 1][0] if i + 1 < len(pts) else 1.0
        if next_x <= x:
            continue
        area, best_z = 0.0, 1.0  # dominated y-z area of the points with x_j <= x
        for y, z in sorted((q[1], q[2]) for q in pts[: i + 1]):
            if z < best_z:
                area += (1.0 - y) * (best_z - z)
                best_z = z
        volume += area * (next_x - x)
    return volume


def two_step(points: Sequence[Mapping], n_agents: int) -> List[Mapping]:
    """Best allocation per budget k by accuracy, then that allocation's fastest placement."""
    chosen = []
    for k in range(n_agents + 1):
        pool = [p for p in points if len(p["plan_set"]) <= k]
        best = max(p["accuracy"] for p in pool)
        allocation = min((p for p in pool if p["accuracy"] == best), key=lambda p: (p["cost"], sorted(p["plan_set"])))
        chosen.append(min((p for p in pool if p["plan_set"] == allocation["plan_set"]), key=lambda p: p["p95_latency"]))
    return chosen


def limit_gaps(points: Sequence[Mapping], baseline: Sequence[Mapping]) -> List[dict]:
    """A2: on a grid of (cost limit, p95 limit) = deciles 10..100 of the candidates' cost
    and p95, the most accurate joint choice minus the most accurate two-step choice that
    fits both limits. Pairs where the two-step baseline has nothing feasible are left out."""
    costs = [p["cost"] for p in points]
    lats = [p["p95_latency"] for p in points]
    rows = []
    for qc in range(10, 101, 10):
        for ql in range(10, 101, 10):
            c, l = float(np.percentile(costs, qc)), float(np.percentile(lats, ql))
            fits = lambda pool: [p for p in pool if p["cost"] <= c and p["p95_latency"] <= l]
            two = max((p["accuracy"] for p in fits(baseline)), default=None)
            if two is None:
                continue
            joint = max(p["accuracy"] for p in fits(points))
            rows.append({"cost_pct": qc, "p95_pct": ql, "cost_limit": c, "p95_limit_s": l,
                         "joint_accuracy": joint, "two_step_accuracy": two, "gap": joint - two})
    return rows


def constrained_best(points: Sequence[Mapping], limit: float) -> List[dict]:
    """H3a: best-accuracy plan per placement under the latency limit."""
    rows = []
    for placement in PLACEMENTS:
        ok = [p for p in points if p["placement"] == placement and p["p95_latency"] <= limit]
        best = max(ok, key=lambda p: (p["accuracy"], -p["cost"]), default=None)
        rows.append({"placement": placement, "limit_s": limit, "plan": best["plan"] if best else "",
                     "accuracy": best["accuracy"] if best else float("nan")})
    return rows


def budget_best(acc: Mapping[FrozenSet[str], float], costs: Sequence[Mapping], topo, fracs,
                gpu_col: str = "gpu_usd_throughput_separate") -> List[dict]:
    """H4a: best plan at the same relative budget under API and GPU pricing (separate placement)."""
    rows = []
    for frac in fracs:
        row = {"budget_fraction": frac}
        for column in ("api_usd", gpu_col):
            by = {parse_plan_name(c["plan"], topo): float(c[column]) for c in costs}
            low, high = by[frozenset()], by[frozenset(topo)]
            ok = [p for p in by if p in acc and by[p] <= low + frac * (high - low)]
            best = max(ok, key=lambda p: (acc[p], -by[p]))
            row[f"{column}_plan"], row[f"{column}_accuracy"] = plan_name(best, topo), acc[best]
        row["gpu_column"] = gpu_col
        row["gpu_usd_plan"], row["gpu_usd_accuracy"] = row.pop(f"{gpu_col}_plan"), row.pop(f"{gpu_col}_accuracy")
        row["differs"] = row["api_usd_plan"] != row["gpu_usd_plan"]
        rows.append(row)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workflow", default="math", choices=list(WORKFLOWS))
    ap.add_argument("--plans", required=True, help="h3_plans.csv (measured) or plan_estimates.csv")
    ap.add_argument("--estimator", default="", help="with plan_estimates.csv: which estimator's accuracy to use")
    ap.add_argument("--true-plans", default="", help="exhaustive h3_plans.csv, for regret to the true front")
    ap.add_argument("--costs", required=True, help="plan_costs.csv from cost_report.py")
    ap.add_argument("--calls", required=True, help="h3_calls.csv: per-agent latency")
    ap.add_argument("--interference", default="configs/v2_interference.yaml")
    ap.add_argument("--cost-metric", choices=["gpu_usd_throughput", "gpu_usd_latency", "api_usd"],
                    default="gpu_usd_throughput",
                    help="gpu_usd_throughput (FIX 5) falls back to gpu_usd_latency when plan_costs.csv has no P5 rates")
    ap.add_argument("--k", type=int, default=16, help="problems in flight")
    ap.add_argument("--limit-factor", type=float, default=1.5, help="H3a: limit = factor x separate all_small p95")
    ap.add_argument("--budget-fractions", default="0.25,0.5,0.75")
    ap.add_argument("--measured", default="", help="placement_summary.csv files, comma separated, for H3c")
    ap.add_argument("--output-dir", default="results/v2/pareto")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    out, done = resolve_output_dir(args.output_dir, args_config(args), create=not args.dry_run)
    if args.dry_run:
        print(f"would search {args.plans} x {PLACEMENTS} on {args.cost_metric}, into {out}")
        return
    if done:
        print(f"already finished: {out}")
        return

    wf = WORKFLOWS[args.workflow][1]()
    topo = list(wf.topological_order)
    rows = read_csv(args.plans)
    if args.estimator:
        rows = [r for r in rows if r["estimator"] == args.estimator]
    acc_col = "estimate" if args.estimator else "accuracy"
    accuracy = {parse_upgraded(r["upgraded"], topo): float(r[acc_col]) for r in rows}
    cost_rows = read_csv(args.costs)
    costs = {parse_plan_name(c["plan"], topo): c for c in cost_rows}
    model = LatencyModel(read_csv(args.calls), wf)
    betas = yaml.safe_load(Path(args.interference).read_text())["placements"]
    rate_col = "gpu_seconds_shared"
    metric = args.cost_metric
    have_tput = all(str(c.get("gpu_usd_throughput_separate", "")) not in ("", "nan") for c in cost_rows)
    if metric == "gpu_usd_throughput" and not have_tput:
        print("WARNING: no throughput GPU cost (no P5 runs); using gpu_usd_latency")
        metric = "gpu_usd_latency"

    points, skipped = [], set()
    missing = [p for p in accuracy if p not in costs]
    if missing:
        print(f"WARNING: {len(missing)} plans have no cost row and are left out")
    for plan, acc in accuracy.items():
        if plan not in costs:
            continue
        separate_p95 = model.p95(plan, {"small": 1.0, "large": 1.0})
        for placement in PLACEMENTS:
            p95 = model.p95(plan, model.factors(plan, betas[placement], args.k))
            if metric == "gpu_usd_throughput":
                cost = float(costs[plan][f"gpu_usd_throughput_{placement}"])
            else:
                cost = float(costs[plan][metric])
            if metric == "gpu_usd_latency" and placement != "separate":
                # The GPU is shared by memory fraction, and calls run slower by the predicted factor.
                cost *= float(costs[plan][rate_col]) / float(costs[plan]["gpu_seconds"]) * (p95 / separate_p95)
            if cost != cost:  # NaN: no P5 throughput for this placement
                skipped.add(placement)
                continue
            points.append({"plan": plan_name(plan, topo), "plan_set": plan, "placement": placement,
                           "accuracy": acc, "cost": cost, "p95_latency": p95})

    if skipped:
        print(f"WARNING: no {metric} for placements {sorted(skipped)} (no P5 run); left out")
    cost_max, lat_max = max(p["cost"] for p in points), max(p["p95_latency"] for p in points)
    front, baseline = pareto_front(points), two_step(points, len(topo))
    hv_joint, hv_two = hypervolume(front, cost_max, lat_max), hypervolume(baseline, cost_max, lat_max)
    fields = ["plan", "placement", "accuracy", "cost", "p95_latency"]
    write_csv(out / "pareto_candidates.csv", points, fieldnames=fields)
    write_csv(out / "pareto_front.csv", sorted(front, key=lambda p: -p["accuracy"]), fieldnames=fields)
    write_csv(out / "two_step_baseline.csv", baseline, fieldnames=fields)

    gaps = limit_gaps(points, baseline)
    write_csv(out / "limit_gaps.csv", gaps)
    all_small = next(p for p in points if p["plan"] == "all_small" and p["placement"] == "separate")
    limit = args.limit_factor * all_small["p95_latency"]
    con = constrained_best(points, limit)
    write_csv(out / "constrained_best.csv", con)
    fracs = [float(x) for x in args.budget_fractions.split(",")]
    budgets = budget_best(accuracy, cost_rows, topo, fracs,
                          "gpu_usd_throughput_separate" if have_tput else "gpu_usd_latency")
    write_csv(out / "budget_best.csv", budgets)

    summary = {"cost_metric": metric, "cost_metric_requested": args.cost_metric,
               "placements_left_out": sorted(skipped), "k": args.k, "n_candidates": len(points), "n_front": len(front),
               "hypervolume_joint": hv_joint, "hypervolume_two_step": hv_two,
               "a2_hv_strictly_higher": hv_joint > hv_two + 1e-12,
               "a2_max_limit_gap": max((g["gap"] for g in gaps), default=float("nan")),
               "a2_gap_ge_2_points": any(g["gap"] >= 0.02 - 1e-12 for g in gaps),
               "h3a_limit_s": limit, "h3a_best_differs": len({r["plan"] for r in con if r["placement"] in ("separate", "shared")}) > 1,
               "h4a_any_budget_differs": any(b["differs"] for b in budgets)}

    if args.true_plans:
        truth = {parse_upgraded(r["upgraded"], topo): float(r["accuracy"]) for r in read_csv(args.true_plans)}
        true_points = [{**p, "accuracy": truth[p["plan_set"]]} for p in points if p["plan_set"] in truth]
        true_front = pareto_front(true_points)
        picked = {(p["plan"], p["placement"]) for p in front}
        realized = [p for p in true_points if (p["plan"], p["placement"]) in picked]
        gaps = [t["accuracy"] - max((r["accuracy"] for r in realized if r["cost"] <= t["cost"]
                                     and r["p95_latency"] <= t["p95_latency"]), default=0.0) for t in true_front]
        summary["regret_hypervolume"] = hypervolume(true_front, cost_max, lat_max) - hypervolume(realized, cost_max, lat_max)
        summary["regret_accuracy_mean"] = float(np.mean(gaps))

    if args.measured:
        predicted = {(p["plan"], p["placement"]): p["p95_latency"] for p in points}
        check = []
        for path in args.measured.split(","):
            for m in read_csv(path):
                pred = predicted.get((m["plan"], m["placement"]))
                if pred is not None:
                    check.append({"plan": m["plan"], "placement": m["placement"], "k": m["k"], "repeat": m["repeat"],
                                  "predicted_p95": pred, "measured_p95": float(m["p95_s"]),
                                  "rel_error": pred / float(m["p95_s"]) - 1})
        write_csv(out / "latency_check.csv", check)
        if check:
            summary["h3c_share_within_10pct"] = float(np.mean([abs(c["rel_error"]) <= 0.10 for c in check]))
    write_json(out / "pareto_summary.json", summary)
    mark_done(out)
    print(f"front {len(front)} of {len(points)}; hypervolume joint {hv_joint:.4f}, two-step {hv_two:.4f}; wrote {out}")


if __name__ == "__main__":
    main()
