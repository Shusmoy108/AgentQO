"""M3: labels_v2.csv and its per-problem and per-strategy tables, from substitute records."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

import numpy as np

TIERS = ("small_in", "small_out", "small_s", "large_in", "large_out", "large_s")


def bootstrap_mean_ci(x: np.ndarray, n_boot: int = 5000, seed: int = 0) -> tuple:
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, len(x), (n_boot, len(x)))].mean(1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def per_problem_rows(records: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for r in records:
        if r["code_node"]:
            continue
        row = {
            "agent": r["node_id"], "task_id": r["task_id"], "baseline_correct": r["q_base"],
            "q_plus": r["q_plus"], "baseline_agrees": r["baseline_agrees"], "p_err": r["p_err"],
            "base_key": r["base_key"], "sample_keys": r["sample_keys"],
            "consequence_by_strategy": r["consequence_by_strategy"], "consequence_real": r["consequence_real"],
            "skipped_plus": r["skipped_plus"], "has_descendants": r["has_descendants"],
            "outputs_identical": r.get("outputs_identical"),
        }
        for prefix, calls in (("base", r["calls_base"]), ("plus", r["calls_plus"]), ("samples", r["calls_samples"])):
            row.update({f"{prefix}_{t}": calls.get(t, 0.0) for t in TIERS})
        rows.append(row)
    return rows


def labels_rows(records: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_agent: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        if not r["code_node"]:
            by_agent.setdefault(r["node_id"], []).append(r)
    rows = []
    for agent, recs in by_agent.items():
        gain = np.array([r["q_plus"] - r["q_base"] for r in recs])
        dis = np.array([not r["baseline_agrees"] for r in recs])
        low, high = bootstrap_mean_ci(gain)
        p_err = float(np.mean([r["p_err"] for r in recs]))
        synth = [v for r in recs for v in r["consequence_by_strategy"].values()]
        real = [r["consequence_real"] for r in recs if r["consequence_real"] is not None]
        rows.append({
            "agent": agent, "n": len(recs), "p_dis": float(dis.mean()),
            "g_dis": float(gain[dis].mean()) if dis.any() else 0.0,
            "uv": float(gain.mean()), "uv_ci_low": low, "uv_ci_high": high,
            "ec_synthetic": float(np.mean(synth)) * p_err if synth else 0.0,
            # Real-error consequence only on problems with a disagreeing small resample;
            # undefined (blank) when there are none, never 0.
            "ec_real": float(np.mean(real)) * p_err if real else None,
            "ec_real_n_used": len(real),
            "reruns_used": sum(r["has_descendants"] and not r["skipped_plus"] for r in recs),
            "reruns_full": sum(bool(r["has_descendants"]) for r in recs),
        })
    return rows


def strategy_rows(records: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Consequence per agent and strategy; resample_disagree is the real-error row (H1a)."""
    pool: Dict[tuple, List[float]] = {}
    for r in records:
        if r["code_node"]:
            continue
        for s, v in r["consequence_by_strategy"].items():
            pool.setdefault((r["node_id"], s), []).append(v)
        if r["consequence_real"] is not None:
            pool.setdefault((r["node_id"], "resample_disagree"), []).append(r["consequence_real"])
    return [{"agent": a, "strategy": s, "n": len(v), "consequence": float(np.mean(v))}
            for (a, s), v in pool.items()]


def skip_variants(per_problem: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Offline, from full-mode per-problem rows: rerun share and per-agent UV error of
    skipping Q+ (taking Q+ = baseline) under the key rule (A1/A10) and the exact-text rule (E3)."""
    truth = lambda r: str(r) in ("True", "1", "1.0")
    rules = {"key": lambda r: truth(r["baseline_agrees"]) and r["base_key"] not in (None, "") and r["agent"] != "planner",
             "exact": lambda r: truth(r["outputs_identical"])}
    by_agent: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_problem:
        by_agent.setdefault(r["agent"], []).append(r)
    full = sum(truth(r["has_descendants"]) for r in per_problem)
    out: Dict[str, Any] = {"reruns_full": full}
    for name, skip in rules.items():
        used = sum(truth(r["has_descendants"]) and not skip(r) for r in per_problem)
        err = {}
        for agent, rows in by_agent.items():
            gain = [float(r["q_plus"]) - float(r["baseline_correct"]) for r in rows]
            fast = [0.0 if skip(r) else g for r, g in zip(rows, gain)]
            err[agent] = abs(float(np.mean(fast)) - float(np.mean(gain)))
        out[name] = {"reruns_used": used, "share": used / full if full else float("nan"),
                     "uv_abs_error": err, "max_uv_abs_error": max(err.values(), default=float("nan"))}
    return out
