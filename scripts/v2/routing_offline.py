#!/usr/bin/env python3
"""M7: per-problem routing, estimated offline from M3's labels_v2_per_problem.csv.

A routed problem takes its Q+ outcome (agent v on the large model), any other
its baseline outcome. Every problem pays for the K small samples. Planners have
no key, so their samples are final answers and the cost includes those runs.

A4 (amendment): the one pre-registered test is rule samples_disagree (the K small
samples are not unanimous) for the agent confident_uv picks at budget 1, given
--labels and --workflow; it is marked primary in routing.csv and reported in
routing_summary.json. Every other row is exploratory.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Sequence

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agentqo.metrics.cost_model import api_usd, load_prices  # noqa: E402
from agentqo.metrics.io import args_config, mark_done, read_csv, resolve_output_dir, write_csv, write_json  # noqa: E402
from agentqo.policies.v2_rules import confident_uv_order  # noqa: E402
from scripts.run_real_pipeline import WORKFLOWS  # noqa: E402


def key_entropy(keys: Sequence) -> float:
    """Entropy in bits over sampled keys; a missing key counts as its own value."""
    counts = Counter("" if k is None else k for k in keys)
    total = sum(counts.values())
    return -sum(c / total * math.log2(c / total) for c in counts.values()) if total else 0.0


def disagree_each_other(keys, base_key) -> bool:
    return len(set(keys)) > 1


def disagree_with_majority(keys, base_key) -> bool:
    """The greedy small answer is not what most samples say."""
    return bool(keys) and Counter(keys).most_common(1)[0][0] != base_key


def rules(thresholds: Sequence[float]) -> List[tuple]:
    out = [("samples_disagree", "", disagree_each_other), ("baseline_vs_majority", "", disagree_with_majority)]
    for t in thresholds:
        out.append(("entropy", t, lambda keys, base, t=t: key_entropy(keys) > t))
    return out


def row_api(row: Mapping, prefix: str, prices: Mapping) -> float:
    return sum(api_usd(prices, tier, float(row[f"{prefix}_{tier}_in"]), float(row[f"{prefix}_{tier}_out"]))
               for tier in ("small", "large"))


def evaluate(rows: Sequence[Mapping], route: Callable, prices: Mapping) -> Dict[str, float]:
    routed = [route(json.loads(r["sample_keys"]), r["base_key"] or None) for r in rows]
    acc = [float(r["q_plus"]) if go else float(r["baseline_correct"]) for r, go in zip(rows, routed)]
    cost = [row_api(r, "plus" if go else "base", prices) + row_api(r, "samples", prices) for r, go in zip(rows, routed)]
    return {"routed_share": float(np.mean(routed)), "accuracy": float(np.mean(acc)), "cost": float(np.mean(cost))}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--labels-per-problem", required=True)
    ap.add_argument("--labels", default="", help="labels_v2.csv: picks the A4 primary agent by confident_uv")
    ap.add_argument("--workflow", default="", choices=["", *WORKFLOWS])
    ap.add_argument("--prices", default="configs/v2_prices.yaml")
    ap.add_argument("--entropy-thresholds", default="0,0.5,1.0")
    ap.add_argument("--output-dir", default="results/v2/routing")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    out, done = resolve_output_dir(args.output_dir, args_config(args), create=not args.dry_run)
    if args.dry_run:
        print(f"would evaluate routing rules on {args.labels_per_problem}, into {out}")
        return
    if done:
        print(f"already finished: {out}")
        return
    prices = load_prices(args.prices)
    by_agent: Dict[str, List[dict]] = defaultdict(list)
    for r in read_csv(args.labels_per_problem):
        by_agent[r["agent"]].append(r)
    primary = ""
    if args.labels and args.workflow:
        labels = {r["agent"]: r for r in read_csv(args.labels)}
        primary = confident_uv_order(labels, WORKFLOWS[args.workflow][1]())[0]
    table = []
    for agent, rows in by_agent.items():
        fixed_acc = float(np.mean([float(r["q_plus"]) for r in rows]))
        fixed_cost = float(np.mean([row_api(r, "plus", prices) for r in rows]))
        base_acc = float(np.mean([float(r["baseline_correct"]) for r in rows]))
        for name, threshold, route in rules([float(x) for x in args.entropy_thresholds.split(",")]):
            res = evaluate(rows, route, prices)
            table.append({"agent": agent, "rule": name, "threshold": threshold, **res, "baseline_accuracy": base_acc,
                          "fixed_accuracy": fixed_acc, "fixed_cost": fixed_cost,
                          "h6_match": res["accuracy"] >= fixed_acc - 0.01 and res["cost"] < fixed_cost,
                          "primary": agent == primary and name == "samples_disagree"})
    write_csv(out / "routing.csv", table)
    main_row = next((t for t in table if t["primary"]), None)
    write_json(out / "routing_summary.json", {
        "a4_agent": primary or None, "a4_rule": "samples_disagree (K small samples not unanimous)",
        "a4_k_samples": len(json.loads(by_agent[primary][0]["sample_keys"])) if primary in by_agent else None,
        "a4_h6_match": main_row["h6_match"] if main_row else None, "a4_row": main_row,
        "note": "all other rows in routing.csv are exploratory"})
    mark_done(out)
    print(f"{len(table)} rows; H6 matches: {sum(t['h6_match'] for t in table)}; wrote {out}/routing.csv")


if __name__ == "__main__":
    main()
