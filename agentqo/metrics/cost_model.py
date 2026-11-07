"""M1 cost model: price each plan from its per-call trace.

A call is a mapping with plan, task_id, fidelity (small/large),
prompt_tokens, completion_tokens, latency_s. All outputs are means per
problem, so plans run on different problem counts stay comparable.

Two GPU prices:
- gpu_usd_latency (the original M1 column): each call is charged its latency on
  the whole GPU (gpu_seconds), or its memory fraction of a shared GPU
  (gpu_seconds_shared). Under batching this overcounts GPU time; kept for comparison.
- gpu_usd_throughput (FIX 5, A7): GPUs reserved x wall-clock seconds / problems completed.
  Measured directly for P5 placement runs (measured_throughput_costs). For quality
  phases it is estimated (A11): GPU time per call = a_m x prompt_tokens + b_m x
  completion_tokens, with a_m, b_m fitted per model and placement from P5 per-call data
  (fit_token_rates). A plan or placement without fitted rates falls back to the latency
  price and says so in gpu_cost_basis_<placement> = "fallback_latency".
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

import numpy as np
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
    models: Dict[str, Dict[str, str]] = defaultdict(dict)
    for c in calls:
        plan, tier = c["plan"], c["fidelity"]
        tin, tout, lat = float(c["prompt_tokens"]), float(c["completion_tokens"]), float(c["latency_s"])
        problems[plan].add(c["task_id"])
        t = totals[plan]
        t["tokens_in"] += tin
        t["tokens_out"] += tout
        t["api_usd"] += api_usd(prices, tier, tin, tout)
        t[f"tokens_out_{tier}"] += tout
        t[f"tokens_in_{tier}"] += tin
        if c.get("model"):
            models[plan][tier] = c["model"]
        t["gpu_seconds"] += lat
        t["gpu_seconds_shared"] += lat * prices["shared_memory_fraction"][tier]
        t["cost_units"] += prices["cost_units"][tier]
    rows = []
    for plan, t in totals.items():
        n = len(problems[plan])
        row: Dict[str, Any] = {"plan": plan, "n_problems": n, "tokens_out_small": 0.0, "tokens_out_large": 0.0,
                               "tokens_in_small": 0.0, "tokens_in_large": 0.0,
                               **{k: v / n for k, v in t.items()},
                               "model_small": models[plan].get("small", ""), "model_large": models[plan].get("large", "")}
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
    """P5: per (run, plan, placement), GPUs reserved x wall / problems, priced; mean over repeats.
    ``run`` names the P5 directory (model set and task), when the caller sets it."""
    cells: Dict[tuple, List[float]] = defaultdict(list)
    for r in summary_rows:
        tput = float(r["throughput_per_s"])  # problems completed / wall seconds
        cells[(r.get("run", ""), r["plan"], r["placement"])].append(GPUS_RESERVED[r["placement"]] / tput)
    return [{"run": run, "plan": plan, "placement": placement, "gpu_seconds_per_problem": sum(v) / len(v),
             "gpu_usd_throughput": gpu_usd(sum(v) / len(v), gpu_hour_usd), "source": "measured", "repeats": len(v)}
            for (run, plan, placement), v in sorted(cells.items())]


def fit_token_rates(runs: Iterable[tuple]) -> Dict[tuple, Dict[str, float]]:
    """A11: (model, placement) -> {a, b, n_calls}: GPU-seconds per prompt token (a, prefill)
    and per completion token (b, decode), from P5 runs given as (summary_rows, call_rows).

    Shape: per-call latency = alpha x prompt + beta x completion (non-negative least squares).
    Scale: a = s alpha, b = s beta, with s chosen so the calls of each run add up to the GPU
    time the model held: the run's wall time on its own GPU (separate), or its share of the
    one GPU's wall time by alpha/beta-weighted work (shared, shared_mps).
    ponytail: one scale per (model, placement) over all its runs; per-run scales if the fit
    misses the P5 measurements by more than A7's 10%."""
    from scipy.optimize import nnls
    runs = list(runs)
    placement_of = {}
    cells: Dict[tuple, List[Mapping]] = defaultdict(list)
    for summary_rows, call_rows in runs:
        place = {(r["plan"], str(r["repeat"])): r["placement"] for r in summary_rows}
        for c in call_rows:
            key = (c["model"], place[(c["plan"], str(c["repeat"]))])
            cells[key].append(c)
            placement_of[key] = key[1]
    shape = {}
    for key, calls in cells.items():
        x = np.array([[float(c["prompt_tokens"]), float(c["completion_tokens"])] for c in calls])
        y = np.array([float(c["latency_s"]) for c in calls])
        shape[key] = nnls(x, y)[0]
    held: Dict[tuple, float] = defaultdict(float)
    work: Dict[tuple, float] = defaultdict(float)
    for summary_rows, call_rows in runs:
        for r in summary_rows:
            wall = float(r["n"]) / float(r["throughput_per_s"])
            w: Dict[tuple, float] = defaultdict(float)
            for c in call_rows:
                if c["plan"] == r["plan"] and str(c["repeat"]) == str(r["repeat"]):
                    al, be = shape[(c["model"], r["placement"])]
                    w[(c["model"], r["placement"])] += al * float(c["prompt_tokens"]) + be * float(c["completion_tokens"])
            total = sum(w.values())
            for key, v in w.items():
                work[key] += v
                held[key] += wall if r["placement"] == "separate" else (wall * v / total if total else 0.0)
    out = {}
    for key, (al, be) in shape.items():
        scale = held[key] / work[key] if work[key] else float("nan")
        out[key] = {"a": al * scale, "b": be * scale, "alpha_latency": al, "beta_latency": be,
                    "n_calls": len(cells[key])}
    return out


def estimated_throughput_costs(rows: List[Dict[str, Any]], rates: Mapping[tuple, Mapping[str, float]],
                               gpu_hour_usd: float) -> None:
    """Add gpu_usd_throughput_<placement> and gpu_cost_basis_<placement> to price_plans rows.

    separate: 2 GPUs held for the busier model's time; shared: 1 GPU for both models' time;
    time per tier = a_m x prompt tokens + b_m x completion tokens. Without rates for a model
    the plan uses, the latency price stands in (memory fraction on a shared GPU) with basis
    "fallback_latency"."""
    for row in rows:
        for placement, gpus in GPUS_RESERVED.items():
            secs, ok = [], True
            for tier in TIERS:
                tin, tout = float(row.get(f"tokens_in_{tier}", 0.0)), float(row.get(f"tokens_out_{tier}", 0.0))
                if tin == 0 and tout == 0:
                    secs.append(0.0)
                    continue
                r = rates.get((row.get(f"model_{tier}", ""), placement))
                if not r or r["a"] != r["a"]:
                    ok = False
                    break
                secs.append(r["a"] * tin + r["b"] * tout)
            if ok:
                busy = max(secs) if placement == "separate" else sum(secs)
                row[f"gpu_usd_throughput_{placement}"] = gpu_usd(gpus * busy, gpu_hour_usd)
                row[f"gpu_cost_basis_{placement}"] = "estimated_rates"
            else:
                lat = row["gpu_seconds"] if placement == "separate" else row["gpu_seconds_shared"]
                row[f"gpu_usd_throughput_{placement}"] = gpu_usd(lat, gpu_hour_usd)
                row[f"gpu_cost_basis_{placement}"] = "fallback_latency"


def rank_agreement(rows: Iterable[Mapping[str, Any]], a: str, b: str) -> float:
    """Kendall tau-b between two cost columns over plans (A3); NaN if either is missing."""
    from scipy.stats import kendalltau
    pairs = [(float(r[a]), float(r[b])) for r in rows if r.get(a) not in (None, "") and r.get(b) not in (None, "")]
    pairs = [p for p in pairs if p[0] == p[0] and p[1] == p[1]]
    if len(pairs) < 3:
        return float("nan")
    return float(kendalltau(*zip(*pairs)).statistic)
