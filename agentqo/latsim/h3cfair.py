"""H3c-fair and mean_sum-fair: the registered baselines' formulas, with inputs from latsim's fit data only.

    python3 -m agentqo.latsim.h3cfair --out results/latsim/h3cfair/predictions.csv

Formula (unchanged from scripts/v2/pareto.py LatencyModel, the registered H3c):
  per problem, the longest path through the workflow DAG of base call latency x the factor of
  the call's model; p50 / p95 over problems. Factor: the h4_fit.simulate fixed point (busy
  shares u, overlap) with K problems in flight, 1 + sum_o beta[o -> m] * u_o * overlap,
  generalised from two models to n (for two models it is exactly H3c's). mean_sum-fair: sum
  over the plan's nodes of the mean base latency of (node, model), no factor (as mean_sum).

Inputs (all from the fit data, never from P2-P4 latency):
  * Base call latency for (problem, node, model): median of the measured calls in P5
    separate-placement runs of the same workflow at the matching K (results/v2/P5/separate*,
    cal_*_separate). K without its own runs: linear in log2(K) between the nearest measured
    Ks, clamped to the measured range (only math with Qwen 1.5B/7B has K = 1, 16, 32; every
    calibration set is K = 16 only).
  * Borrowing, where no P5 run has that (workflow, problem, node, model) cell (hotpot_iso_*,
    complex_q15_7, hotpot_phi): the model's per-call rate at the matching K, latency =
    r0 + r1 * prompt_tokens + r2 * completion_tokens by least squares over all of that model's
    P5 separate calls at that K (any workflow), applied to the call's h3_calls tokens. This is
    latsim's rule: per-model parameters from P5, tokens from the setting's h3_calls.
  * Betas: latsim's (params.json of the frozen latsim: h4grid fit, quantile p50, pairs without
    a grid borrow the closest pair in log model size: Phi -> q3_14; math_tiers pairs with the
    14B -> q3_14). Separate placement: factor 1.
  * Problems: the first 64 of the setting's h3_calls (the X1 / P5 problem set).
Placement enters only through the factor, as in the registered H3c (its base is separate-
placement calls). P5's shared calibration runs are not used as a base: they run all_small or
all_large only, so the other model is idle and no interference is in them.
"""

from __future__ import annotations

import argparse
import csv
import glob
import gzip
import json
import math
import os
import statistics
from collections import defaultdict
from multiprocessing import Pool
from typing import Dict, List, Mapping, Tuple

import numpy as np

from agentqo.latsim.fit import betas_for, read_rows
from agentqo.latsim.predict import KS, N_PROBLEMS, PLACEMENTS, SETTINGS, write_csv
from agentqo.latsim.sim import pct


def load_inputs(results: str):
    """cells[(workflow, task, node, model)][k] = median latency; rates[model][k] = (r0, r1, r2)."""
    raw = defaultdict(list)
    rate_rows = defaultdict(list)
    for path in sorted(glob.glob(f"{results}/P5/*/placement_calls.csv")):
        d = os.path.dirname(path)
        cfg = json.load(open(f"{d}/run_config.v2.json"))
        if cfg["placement"] != "separate":
            continue
        wf, k = cfg["workflow"], int(cfg["k"])
        for c in read_rows(path):
            lat = float(c["latency_s"])
            raw[(wf, c["task_id"], c["node_id"], c["model"], k)].append(lat)
            rate_rows[(c["model"], k)].append((1.0, float(c["prompt_tokens"]), float(c["completion_tokens"]), lat))
    cells: Dict[tuple, Dict[int, float]] = defaultdict(dict)
    for (wf, t, n, m, k), v in raw.items():
        cells[(wf, t, n, m)][k] = statistics.median(v)
    rates: Dict[str, Dict[int, np.ndarray]] = defaultdict(dict)
    for (m, k), rows in rate_rows.items():
        a = np.array(rows)
        rates[m][k] = np.linalg.lstsq(a[:, :3], a[:, 3], rcond=None)[0]
    return cells, rates


def at_k(by_k: Mapping[int, object], k: int):
    """Value at K: exact, else linear in log2(K) between neighbours, clamped to the range."""
    ks = sorted(by_k)
    if k in by_k:
        return by_k[k]
    if k <= ks[0]:
        return by_k[ks[0]]
    if k >= ks[-1]:
        return by_k[ks[-1]]
    lo = max(x for x in ks if x < k)
    hi = min(x for x in ks if x > k)
    w = (math.log2(k) - math.log2(lo)) / (math.log2(hi) - math.log2(lo))
    return (1 - w) * by_k[lo] + w * by_k[hi]


def fixed_point(node_lat: List[Tuple[str, float]], betas: Mapping[Tuple[str, str], float], k: int,
                iters: int = 200) -> Dict[str, float]:
    """h4_fit.simulate as pareto.LatencyModel.factors uses it (one mean problem, iso = identity),
    for n models: factor_m = 1 + sum_o beta[o->m] * u_o * overlap, overlap = prod of the pair's u."""
    models = sorted({m for m, _ in node_lat})
    u = {m: 0.5 for m in models}

    def factor(m):
        return 1.0 + sum(b * u[o] * (u[m] * u[o]) for (o, mm), b in betas.items() if mm == m and o in u)

    for _ in range(iters):
        t_m = {m: 0.0 for m in models}
        for m, lat in node_lat:
            t_m[m] += lat * factor(m)
        total = sum(t_m.values())
        new_u = {m: 1 - (1 - t_m[m] / total) ** k for m in models} if total > 0 else u
        u = {m: 0.5 * u[m] + 0.5 * new_u[m] for m in models}
    return {m: factor(m) for m in models}


def load_plans(results: str, setting: str, n: int = N_PROBLEMS):
    """plan -> {task: [(node, model, P, C)]}, first n tasks of h3_calls; and the task order."""
    base = f"{results}/{SETTINGS[setting]}/plans/h3_calls.csv"
    f = open(base, newline="") if os.path.exists(base) else gzip.open(base + ".gz", "rt", newline="")
    tasks: Dict[str, int] = {}
    plans: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
    with f:
        for r in csv.DictReader(f):
            t = r["task_id"]
            if t not in tasks:
                if len(tasks) >= n:
                    continue
                tasks[t] = len(tasks)
            plans[r["plan"]][t].append((r["node_id"], r["model"], float(r["prompt_tokens"]), float(r["completion_tokens"])))
    return plans, sorted(tasks, key=tasks.get)


def predict_setting(args) -> List[dict]:
    results, setting, cells, rates, params, betas_override = args
    from agentqo.latsim.baselines import workflow_of
    from scripts.run_real_pipeline import WORKFLOWS
    wf_name = workflow_of(setting)
    wf = WORKFLOWS[wf_name][1]()
    topo = list(wf.topological_order)
    plans, order = load_plans(results, setting)
    out = []
    for plan, by_task in sorted(plans.items()):
        model_of = {n: m for calls in by_task.values() for n, m, _, _ in calls}
        models = sorted(set(model_of.values()))
        for k in KS:
            lat: Dict[Tuple[str, str], float] = {}
            borrowed = 0
            for t in order:
                for n, m, p, c in by_task[t]:
                    cell = cells.get((wf_name, t, n, m))
                    if cell:
                        lat[(t, n)] = float(at_k(cell, k))
                    else:
                        borrowed += 1
                        lat[(t, n)] = float(np.dot(at_k(rates[m], k), [1.0, p, c]))
            node_mean = {n: statistics.mean(lat[(t, n)] for t in order if (t, n) in lat) for n in topo if n in model_of}
            mean_sum = sum(node_mean.values())
            for pl in PLACEMENTS:
                betas = betas_override[pl] if betas_override is not None else betas_for(models, pl, params)
                fac = fixed_point([(model_of[n], node_mean[n]) for n in topo if n in model_of], betas, k) \
                    if betas else {m: 1.0 for m in models}
                lengths = []
                for t in order:
                    finish: Dict[str, float] = {}
                    for n in topo:
                        if n not in model_of:
                            continue
                        ready = max((finish[i] for i in wf.nodes[n].inputs if i in finish), default=0.0)
                        finish[n] = ready + lat.get((t, n), node_mean[n]) * fac[model_of[n]]
                    lengths.append(max(finish.values()))
                out.append({"setting": setting, "plan": plan, "placement": pl, "k": k,
                            "h3cfair_p50": pct(lengths, 0.5), "h3cfair_p95": pct(lengths, 0.95),
                            "mean_sum_fair_p50": mean_sum, "mean_sum_fair_p95": mean_sum,
                            "borrowed_share": borrowed / max(1, len(lat))})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", default="results/v2")
    ap.add_argument("--params", default="results/latsim/params.json", help="latsim frozen params (betas)")
    ap.add_argument("--out", default="results/latsim/h3cfair/predictions.csv")
    args = ap.parse_args()
    cells, rates = load_inputs(args.results)
    params = json.load(open(args.params))
    with Pool() as pool:
        rows = [r for rs in pool.map(predict_setting, [(args.results, s, cells, rates, params, None)
                                                         for s in SETTINGS]) for r in rs]
    write_csv(args.out, rows)
    print(f"wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
