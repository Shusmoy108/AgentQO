"""M1 cost model: price each plan from its per-call trace.

A call is a mapping with plan, task_id, fidelity (small/large),
prompt_tokens, completion_tokens, latency_s. All outputs are means per
problem, so plans run on different problem counts stay comparable.

Two GPU prices:
- gpu_usd_latency (the original M1 column): each call is charged its latency on
  the whole GPU (gpu_seconds), or its memory fraction of a shared GPU
  (gpu_seconds_shared). Under batching this overcounts GPU time; kept for comparison.
- gpu_usd_throughput (FIX 5): GPUs reserved x wall-clock seconds / problems completed.
  Measured directly for P5 placement runs (measured_throughput_costs). For quality
  phases it is estimated from each plan's output tokens and the tokens/s that P5
  measured per model and placement (estimated_throughput_costs), labelled "estimated".
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
        t[f"tokens_out_{tier}"] += tout
        t["gpu_seconds"] += lat
        t["gpu_seconds_shared"] += lat * prices["shared_memory_fraction"][tier]
        t["cost_units"] += prices["cost_units"][tier]
    rows = []
    for plan, t in totals.items():
        n = len(problems[plan])
        row: Dict[str, Any] = {"plan": plan, "n_problems": n, "tokens_out_small": 0.0, "tokens_out_large": 0.0,
                               **{k: v / n for k, v in t.items()}}
        row["gpu_usd_latency"] = gpu_usd(row["gpu_seconds"], prices["gpu_hour_usd"])
        for rate in prices["gpu_hour_sweep"]:
            row[f"gpu_usd_latency_{rate:g}"] = gpu_usd(row["gpu_seconds"], rate)
            row[f"gpu_usd_latency_shared_{rate:g}"] = gpu_usd(row["gpu_seconds_shared"], rate)
        rows.append(row)
    return rows


def large_small_ratio(rows: Iterable[Mapping[str, Any]], column: str = "api_usd") -> float:
    """Per-problem cost of all_large over all_small (H4b); NaN if either is missing."""
    by = {r["plan"]: float(r[column]) for r in rows}
    if not by.get("all_small") or "all_large" not in by:
        return float("nan")
    return by["all_large"] / by["all_small"]


# GPUs a placement reserves: separate puts each model on its own GPU.
GPUS_RESERVED = {"separate": 2, "shared": 1, "shared_mps": 1}
TIERS = ("small", "large")


def measured_throughput_costs(summary_rows: Iterable[Mapping[str, Any]], gpu_hour_usd: float) -> List[Dict[str, Any]]:
    """P5: per (plan, placement), GPUs reserved x wall / problems, priced; mean over repeats."""
    cells: Dict[tuple, List[float]] = defaultdict(list)
    for r in summary_rows:
        tput = float(r["throughput_per_s"])  # problems completed / wall seconds
        cells[(r["plan"], r["placement"])].append(GPUS_RESERVED[r["placement"]] / tput)
    return [{"plan": plan, "placement": placement, "gpu_seconds_per_problem": sum(v) / len(v),
             "gpu_usd_throughput": gpu_usd(sum(v) / len(v), gpu_hour_usd), "source": "measured", "repeats": len(v)}
            for (plan, placement), v in sorted(cells.items())]


def tokens_per_second(runs: Iterable[tuple]) -> Dict[tuple, float]:
    """(placement, tier) -> output tokens/s, from P5 runs given as (summary_rows, call_rows).

    Per run (plan, repeat) the rate is the tier's output tokens over the run's wall time; the
    highest rate over runs is kept, as the one closest to a busy GPU.
    ponytail: output tokens only (prefill ignored), max over runs; fit a prefill term if
    HotpotQA's long prompts make the estimates miss the P5 measurements."""
    best: Dict[tuple, float] = {}
    for summary_rows, call_rows in runs:
        tokens: Dict[tuple, float] = defaultdict(float)
        for c in call_rows:
            tokens[(c["plan"], str(c["repeat"]), c["fidelity"])] += float(c["completion_tokens"])
        for r in summary_rows:
            wall = float(r["n"]) / float(r["throughput_per_s"])
            for tier in TIERS:
                tok = tokens.get((r["plan"], str(r["repeat"]), tier), 0.0)
                if tok > 0:
                    key = (r["placement"], tier)
                    best[key] = max(best.get(key, 0.0), tok / wall)
    return best


def estimated_throughput_costs(rows: List[Dict[str, Any]], tps: Mapping[tuple, float], gpu_hour_usd: float) -> None:
    """Add gpu_usd_throughput_<placement> (estimated) to price_plans rows, in place.

    separate: 2 GPUs held for the busier model's time; shared: 1 GPU for both models' time.
    NaN when P5 has no rate for a tier the plan uses."""
    for row in rows:
        for placement, gpus in GPUS_RESERVED.items():
            secs = []
            for tier in TIERS:
                tok = float(row.get(f"tokens_out_{tier}", 0.0))
                rate = tps.get((placement, tier))
                secs.append(0.0 if tok == 0 else (tok / rate if rate else float("nan")))
            busy = max(secs) if placement == "separate" else sum(secs)
            row[f"gpu_usd_throughput_{placement}"] = gpu_usd(gpus * busy, gpu_hour_usd)
        row["gpu_usd_throughput_source"] = "estimated"


def rank_agreement(rows: Iterable[Mapping[str, Any]], a: str, b: str) -> float:
    """Kendall tau-b between two cost columns over plans (A3); NaN if either is missing."""
    from scipy.stats import kendalltau
    pairs = [(float(r[a]), float(r[b])) for r in rows if r.get(a) not in (None, "") and r.get(b) not in (None, "")]
    pairs = [p for p in pairs if p[0] == p[0] and p[1] == p[1]]
    if len(pairs) < 3:
        return float("nan")
    return float(kendalltau(*zip(*pairs)).statistic)
