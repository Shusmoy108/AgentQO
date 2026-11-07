#!/usr/bin/env python3
"""M4 report: what each rule picks at each budget, and how good plan estimators are.

    python3 scripts/v2/rules_report.py --workflow math --labels .../labels_v2.csv \
        --plans .../h3_plans.csv --output-dir .../rules

--labels-disagree adds h1c.json: rerun share and top-2 agreement of a
--disagree-only labels file against the full one.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, FrozenSet, List

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agentqo.metrics.io import args_config, mark_done, read_csv, resolve_output_dir, write_csv, write_json  # noqa: E402
from agentqo.policies.v2_rules import (  # noqa: E402
    all_rules,
    confident_uv_order,
    independence_additive,
    independence_multiplicative,
    pairs_to_measure,
    pairwise_corrected,
)
from scripts.run_real_pipeline import WORKFLOWS  # noqa: E402


def parse_upgraded(text: str, agents) -> FrozenSet[str]:
    if text == "all":
        return frozenset(agents)
    return frozenset() if text in ("", "none") else frozenset(text.split(","))


def plan_label(plan: FrozenSet[str], agents) -> str:
    return "all" if plan == frozenset(agents) else (",".join(sorted(plan)) or "none")


def rule_rows(rules, true_acc: Dict[FrozenSet[str], float], agents) -> List[dict]:
    rows = []
    for rule, by_k in rules.items():
        for k, plan in by_k.items():
            best = max((a for p, a in true_acc.items() if len(p) <= k), default=float("nan"))
            acc = true_acc.get(plan, float("nan"))
            rows.append({"rule": rule, "budget": k, "upgraded": plan_label(plan, agents), "accuracy": acc,
                         "best_accuracy_at_budget": best, "regret": best - acc,
                         "is_best": bool(acc >= best - 1e-12)})
    return rows


def estimator_tables(true_acc, agents, m: int):
    """Errors over all plans and over held-out plans (no estimator was given their accuracy)."""
    ests = {"independence_additive": independence_additive(true_acc),
            "independence_multiplicative": independence_multiplicative(true_acc),
            "pairwise_corrected": pairwise_corrected(true_acc, agents, m)}
    inputs = {frozenset(), *[frozenset({v}) for v in agents], *pairs_to_measure(true_acc, agents, m)}
    plans = list(true_acc)
    truth = np.array([true_acc[p] for p in plans])
    held = np.array([p not in inputs for p in plans])
    thresholds = {f"p{q}": float(np.percentile(truth, q)) for q in (25, 50, 75)}
    summary, detail = [], []
    for name, est in ests.items():
        e = np.array([est(p) for p in plans])
        row = {"estimator": name, "m": m, "n_plans": len(plans), "n_held_out": int(held.sum()),
               "mae_all": float(np.abs(e - truth).mean()),
               "mae_held_out": float(np.abs(e - truth)[held].mean()) if held.any() else float("nan")}
        for label, a in thresholds.items():
            row[f"feasibility_wrong_{label}"] = float(((e >= a) != (truth >= a))[held].mean()) if held.any() else float("nan")
        summary.append(row)
        detail += [{"estimator": name, "upgraded": plan_label(p, agents), "estimate": float(x), "accuracy": float(t),
                    "held_out": bool(h)} for p, x, t, h in zip(plans, e, truth, held)]
    return summary, detail, thresholds


def h1c(full: List[dict], fast: List[dict], wf=None) -> dict:
    """Original H1c and its replacement A1: UV change per agent, top-2 agents and the
    confident_uv budget-1/2 picks, full labels against --disagree-only labels."""
    top2 = lambda rows: {r["agent"] for r in sorted(rows, key=lambda r: -float(r["uv"]))[:2]}
    used, total = sum(int(r["reruns_used"]) for r in fast), sum(int(r["reruns_full"]) for r in fast)
    f_by, d_by = {r["agent"]: r for r in full}, {r["agent"]: r for r in fast}
    uv_diff = {a: abs(float(f_by[a]["uv"]) - float(d_by[a]["uv"])) for a in f_by if a in d_by}
    share = used / total if total else float("nan")
    out = {"reruns_used": used, "reruns_full": total, "share": share,
           "top2_full": sorted(top2(full)), "top2_disagree_only": sorted(top2(fast)),
           "top2_same": top2(full) == top2(fast),
           "a1_uv_abs_diff": uv_diff, "a1_max_uv_abs_diff": max(uv_diff.values(), default=float("nan")),
           "a1_share_le_half": share <= 0.5}
    if wf is not None:
        picks = lambda by: {k: sorted(confident_uv_order(by, wf)[:k]) for k in (1, 2)}
        out["a1_confident_uv_full"], out["a1_confident_uv_disagree_only"] = picks(f_by), picks(d_by)
        out["a1_confident_uv_same"] = picks(f_by) == picks(d_by)
        out["a1_holds_without_share"] = (out["a1_max_uv_abs_diff"] <= 0.02 and out["top2_same"]
                                         and out["a1_confident_uv_same"])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workflow", default="math", choices=list(WORKFLOWS))
    ap.add_argument("--labels", required=True)
    ap.add_argument("--plans", default="", help="h3_plans.csv of an all_subsets run")
    ap.add_argument("--labels-disagree", default="")
    ap.add_argument("--pairs-m", type=int, default=3)
    ap.add_argument("--output-dir", default="results/v2/rules")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    out, done = resolve_output_dir(args.output_dir, args_config(args), create=not args.dry_run)
    if args.dry_run:
        print(f"would apply the rules to {args.labels} and {args.plans or 'no plans'}, into {out}")
        return
    if done:
        print(f"already finished: {out}")
        return
    wf = WORKFLOWS[args.workflow][1]()
    agents = list(wf.topological_order)
    labels = {r["agent"]: r for r in read_csv(args.labels)}
    true_acc = {parse_upgraded(r["upgraded"], agents): float(r["accuracy"]) for r in read_csv(args.plans)} if args.plans else {}
    rules = all_rules(labels, wf)
    write_csv(out / "rule_plans.csv", rule_rows(rules, true_acc, agents))
    summary = {}
    if len(true_acc) == 2 ** len(agents):
        rows, detail, thresholds = estimator_tables(true_acc, agents, args.pairs_m)
        write_csv(out / "estimator_errors.csv", rows)
        write_csv(out / "plan_estimates.csv", detail)
        summary["accuracy_thresholds"] = thresholds
    elif args.plans:
        print(f"{len(true_acc)} plans of {2 ** len(agents)}: estimator errors need all_subsets, skipped")
    if args.labels_disagree:
        summary["h1c"] = h1c(read_csv(args.labels), read_csv(args.labels_disagree), wf)
        write_json(out / "h1c.json", summary["h1c"])
    write_json(out / "rules_summary.json", summary)
    mark_done(out)
    print(f"wrote {out}/rule_plans.csv")


if __name__ == "__main__":
    main()
