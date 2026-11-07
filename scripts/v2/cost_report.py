#!/usr/bin/env python3
"""M1: price every plan in an h3_calls.csv.

    python3 scripts/v2/cost_report.py --calls results/v2/P2/math/h3_calls.csv \
        --output-dir results/v2/P6/math/cost [--placement results/v2/P5/separate,results/v2/P5/shared,...]

With --placement (P5 run directories) it also writes the throughput GPU cost (FIX 5):
measured per (plan, placement) in placement_costs.csv, and estimated per plan from the
P5 prefill/decode rates in plan_costs.csv (gpu_usd_throughput_<placement>, with
gpu_cost_basis_<placement> = estimated_rates or fallback_latency), and token_rates.csv (A11).
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agentqo.metrics.cost_model import (GPUS_RESERVED, estimated_throughput_costs, large_small_ratio, load_prices,  # noqa: E402
                                        fit_token_rates, measured_throughput_costs, price_plans, rank_agreement)
from agentqo.metrics.io import args_config, mark_done, read_csv, resolve_output_dir, write_csv, write_json  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--calls", required=True)
    ap.add_argument("--prices", default="configs/v2_prices.yaml")
    ap.add_argument("--placement", default="", help="P5 run directories, comma separated (FIX 5)")
    ap.add_argument("--output-dir", default="results/v2/cost")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    out, done = resolve_output_dir(args.output_dir, args_config(args), create=not args.dry_run)
    if args.dry_run:
        print(f"would price {args.calls} with {args.prices} into {out}")
        return
    if done:
        print(f"already finished: {out}")
        return
    prices = load_prices(args.prices)
    rows = price_plans(read_csv(args.calls), prices)
    summary = {"n_plans": len(rows), "api_large_small_ratio": large_small_ratio(rows),
               "a3_kendall_tau_latency_vs_units": rank_agreement(rows, "gpu_usd_latency", "cost_units")}
    dirs = [Path(d) for d in args.placement.split(",") if d]
    runs = []
    for d in dirs:
        if (d / "placement_summary.csv").exists():
            summ = [{**r, "run": d.name} for r in read_csv(d / "placement_summary.csv")]
            runs.append((summ, read_csv(d / "placement_calls.csv")))
    rate = prices["gpu_hour_usd"]
    rates = fit_token_rates(runs) if runs else {}
    if runs:
        write_csv(out / "placement_costs.csv", measured_throughput_costs([r for s_, _ in runs for r in s_], rate))
    write_csv(out / "token_rates.csv", [{"model": m, "placement": p, **v} for (m, p), v in sorted(rates.items())],
              fieldnames=["model", "placement", "a", "b", "alpha_latency", "beta_latency", "n_calls"])
    estimated_throughput_costs(rows, rates, rate)
    summary["p5_runs"] = [d.name for d in dirs if (d / "placement_summary.csv").exists()]
    summary["gpu_cost_basis"] = {p: dict(sorted(Counter(r[f"gpu_cost_basis_{p}"] for r in rows).items()))
                                 for p in GPUS_RESERVED}
    for placement in GPUS_RESERVED:  # A3: GPU-time ranking vs the 1-vs-4 cost units
        summary[f"a3_kendall_tau_{placement}"] = rank_agreement(rows, f"gpu_usd_throughput_{placement}", "cost_units")
        summary[f"a3_basis_{placement}"] = ("fallback" if any(r[f"gpu_cost_basis_{placement}"] != "estimated_rates"
                                                               for r in rows) else "estimated_rates")
    write_csv(out / "plan_costs.csv", rows)
    write_json(out / "cost_summary.json", summary)
    mark_done(out)
    print(f"{len(rows)} plans priced, API all_large/all_small = {summary['api_large_small_ratio']:.2f}; "
          f"throughput GPU cost from {len(runs)} P5 runs; wrote {out}/plan_costs.csv")


if __name__ == "__main__":
    main()
