#!/usr/bin/env python3
"""M1: price every plan in an h3_calls.csv.

    python3 scripts/v2/cost_report.py --calls results/v2/P2/math/h3_calls.csv \
        --output-dir results/v2/P6/math/cost
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agentqo.metrics.cost_model import large_small_ratio, load_prices, price_plans  # noqa: E402
from agentqo.metrics.io import args_config, mark_done, read_csv, resolve_output_dir, write_csv, write_json  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--calls", required=True)
    ap.add_argument("--prices", default="configs/v2_prices.yaml")
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
    rows = price_plans(read_csv(args.calls), load_prices(args.prices))
    write_csv(out / "plan_costs.csv", rows)
    ratio = large_small_ratio(rows)
    write_json(out / "cost_summary.json", {"n_plans": len(rows), "api_large_small_ratio": ratio})
    mark_done(out)
    print(f"{len(rows)} plans priced, API all_large/all_small = {ratio:.2f}; wrote {out}/plan_costs.csv")


if __name__ == "__main__":
    main()
