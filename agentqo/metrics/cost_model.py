"""M1 cost model: price each plan from its per-call trace.

A call is a mapping with plan, task_id, fidelity (small/large),
prompt_tokens, completion_tokens, latency_s. All outputs are means per
problem, so plans run on different problem counts stay comparable.

gpu_seconds charges the whole GPU for a call (separate placement).
gpu_seconds_shared charges the call's memory fraction of a shared GPU, using
the latency in the trace; pareto.py adds the interference slowdown.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

import yaml


def load_prices(path: Any = "configs/v2_prices.yaml") -> Dict[str, Any]:
    prices = yaml.safe_load(Path(path).read_text())
    frac = prices["shared_memory_fraction"]
    if sum(frac.values()) > 1.0:
        raise ValueError(f"shared_memory_fraction sums above 1: {frac}")
    return prices


def api_usd(prices: Mapping[str, Any], tier: str, tokens_in: float, tokens_out: float) -> float:
    p = prices["api_usd_per_million"][tier]
    return (tokens_in * p["input"] + tokens_out * p["output"]) / 1e6


def gpu_usd(seconds: float, gpu_hour_usd: float) -> float:
    return seconds * gpu_hour_usd / 3600


def price_plans(calls: Iterable[Mapping[str, Any]], prices: Mapping[str, Any]) -> List[Dict[str, Any]]:
    totals: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    problems: Dict[str, set] = defaultdict(set)
    for c in calls:
        plan, tier = c["plan"], c["fidelity"]
        tin, tout, lat = float(c["prompt_tokens"]), float(c["completion_tokens"]), float(c["latency_s"])
        problems[plan].add(c["task_id"])
        t = totals[plan]
        t["tokens_in"] += tin
        t["tokens_out"] += tout
        t["api_usd"] += api_usd(prices, tier, tin, tout)
        t["gpu_seconds"] += lat
        t["gpu_seconds_shared"] += lat * prices["shared_memory_fraction"][tier]
        t["cost_units"] += prices["cost_units"][tier]
    rows = []
    for plan, t in totals.items():
        n = len(problems[plan])
        row: Dict[str, Any] = {"plan": plan, "n_problems": n, **{k: v / n for k, v in t.items()}}
        row["gpu_usd"] = gpu_usd(row["gpu_seconds"], prices["gpu_hour_usd"])
        for rate in prices["gpu_hour_sweep"]:
            row[f"gpu_usd_{rate:g}"] = gpu_usd(row["gpu_seconds"], rate)
            row[f"gpu_usd_shared_{rate:g}"] = gpu_usd(row["gpu_seconds_shared"], rate)
        rows.append(row)
    return rows


def large_small_ratio(rows: Iterable[Mapping[str, Any]], column: str = "api_usd") -> float:
    """Per-problem cost of all_large over all_small (H4b); NaN if either is missing."""
    by = {r["plan"]: float(r[column]) for r in rows}
    if not by.get("all_small") or "all_large" not in by:
        return float("nan")
    return by["all_large"] / by["all_small"]
