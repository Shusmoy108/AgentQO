"""Fit latsim parameters on P5 and P5/h4grid only.

    python3 -m agentqo.latsim.fit --results results/v2 --out results/latsim/params.json

Per model (o, c, a, b, e; the server model in latsim.sim), fitted jointly for the two
models of a family pair by least squares on the log latency of every separate-placement
call:
  * P5 runs (main sweep and calibration sets, every K): closed loop, each run re-simulated
    with its own problems (start order), per-call tokens and K, as run_placement ran it.
    Closed loop matters: HotpotQA runs the server near saturation, where an open-loop
    replay of measured arrival times lets the queue grow without bound.
  * h4grid separate levels: open loop, each request issued at its recorded start time
    (short prompts, far from saturation).
  * rev1: runs where a model first meets the block's problems (cold prefix cache) are left
    out, so parameters describe warm servers (see cold_runs).
Betas: directed AgentIconq fits per pair from h4grid (shared: fit_results.json full_fit;
MPS: mps_fit.json shared_mps). Which quantile's fit (p50 or p95) to use is chosen on P5's
own shared / shared_mps runs.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
from collections import defaultdict
from multiprocessing import Pool
from typing import Dict, List

import numpy as np
from scipy.optimize import least_squares

from agentqo.latsim.sim import replay, simulate

PAIRS = {  # h4grid pair -> (small model, large model)
    "q15_7": ("Qwen/Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-7B-Instruct"),
    "q3_14": ("Qwen/Qwen2.5-3B-Instruct", "Qwen/Qwen2.5-14B-Instruct"),
    "g2_8": ("ibm-granite/granite-3.1-2b-instruct", "ibm-granite/granite-3.1-8b-instruct"),
}
FAMILIES = {**PAIRS, "phi": ("microsoft/Phi-3.5-mini-instruct", "microsoft/phi-4")}  # fitted jointly
SIZE_B = {  # parameters (billions), only to borrow betas for pairs without a grid
    "Qwen/Qwen2.5-1.5B-Instruct": 1.5, "Qwen/Qwen2.5-3B-Instruct": 3.0, "Qwen/Qwen2.5-7B-Instruct": 7.0,
    "Qwen/Qwen2.5-14B-Instruct": 14.0, "ibm-granite/granite-3.1-2b-instruct": 2.5,
    "ibm-granite/granite-3.1-8b-instruct": 8.0, "microsoft/Phi-3.5-mini-instruct": 3.8, "microsoft/phi-4": 14.0,
}
NAMES = ("o", "c", "a", "b", "e")
LOW = np.log([1e-4, 1e-8, 1e-5, 1e-7, 1e-7])
HIGH = np.log([1, 1e-2, 0.2, 0.05, 0.05])


def read_rows(path: str) -> List[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def cold_runs(folder: str, calls) -> set:
    """(plan, repeat) runs in which a model serves these problems for the first time in the
    block: run_placement runs plans in run_config order, all repeats of a plan back to back,
    on fresh servers, so that is repeat 0 of the first plan using each model. Its prompts
    miss vLLM's prefix cache (P5 Qwen HotpotQA: p95 2.1x the later repeats); rev1 fits
    warm runs only and so predicts warm (steady-state) latency."""
    plans = json.load(open(f"{folder}/run_config.v2.json"))["plans"].split(",")
    seen, cold = set(), set()
    for plan in plans:
        models = {c[0] for (p, r, _), cs in calls.items() if p == plan and r == "0" for c in cs}
        if models - seen:
            cold.add((plan, "0"))
        seen |= models
    return cold


def p5_runs(results: str, separate_only: bool = True, skip_cold: bool = True):
    """Yield (folder, k, problems, starts) per P5 run; problems in start order, each a list
    of (model, P, C, measured latency) in call order; starts = the problems' start_s."""
    for path in sorted(glob.glob(f"{results}/P5/*/placement_calls.csv")):
        d = os.path.dirname(path)
        if separate_only and "separate" not in os.path.basename(d):
            continue
        yield from folder_runs(d, skip_cold)


def folder_runs(d: str, skip_cold: bool = True):
    """p5_runs for one run folder (placement_calls.csv, run_*.csv, run_config.v2.json)."""
    path = f"{d}/placement_calls.csv"
    calls = defaultdict(list)
    for c in read_rows(path):
        calls[(c["plan"], c["repeat"], c["task_id"])].append(
            (c["model"], float(c["prompt_tokens"]), float(c["completion_tokens"]), float(c["latency_s"])))
    cold = cold_runs(d, calls) if skip_cold else set()
    for run in sorted(glob.glob(f"{d}/run_*.csv")):
        rows = sorted(read_rows(run), key=lambda r: float(r["start_s"]))
        if (rows[0]["plan"], rows[0]["repeat"]) in cold:
            continue
        yield (os.path.basename(d), int(rows[0]["k"]), [calls[(r["plan"], r["repeat"], r["task_id"])] for r in rows],
               [float(r["start_s"]) for r in rows])


def grid_levels(results: str):
    """Yield (pair, calls) per separate-placement h4grid level, calls = (start, model, P, C, latency);
    superseded files (P5/h4grid/<pair>/superseded_*) are left out."""
    for pair, (small, large) in PAIRS.items():
        for path in sorted(glob.glob(f"{results}/P5/h4grid/{pair}/*/placement_separate_*_requests.csv")):
            if "superseded" in path:
                continue
            levels = defaultdict(list)
            for r in read_rows(path):
                levels[r["concurrency"]].append(r)
            for rs in levels.values():
                yield pair, sorted((float(r["start_s"]), small if r["model"] == "small" else large,
                                    float(r["prompt_tokens"]), float(r["completion_tokens"]), float(r["latency_s"]))
                                   for r in rs)


def family_data(results: str) -> Dict[str, list]:
    """family -> [("closed", source, k, problems, starts) | ("open", source, calls)]."""
    fam_of = {m: f for f, ms in FAMILIES.items() for m in ms}
    out = defaultdict(list)
    for src, k, problems, starts in p5_runs(results):
        models = {c[0] for p in problems for c in p}
        out[fam_of[next(iter(models))]].append(("closed", src, k, problems, starts))
    for pair, calls in grid_levels(results):
        out[pair].append(("open", f"h4grid/{pair}", calls))
    return out


def open_loop(item: tuple) -> tuple:
    """A P5 run as open-loop calls: a problem's calls run back to back from its start
    (per-problem overhead ~2 ms, measured), so call i is issued at start_s + earlier latencies."""
    _, src, _, problems, starts = item
    calls = []
    for p, t in zip(problems, starts):
        for m, pr, co, lat in p:
            calls.append((t, m, pr, co, lat))
            t += lat
    return ("open", src, calls)


def residuals(params: Dict[str, Dict[str, float]], data: list) -> np.ndarray:
    """log(predicted / measured) per call, in data order (the call order within an open item
    is its own; only sums and means over items are used)."""
    out = []
    for item in data:
        if item[0] == "closed":
            _, _, k, problems, _ = item
            lat: List[List[float]] = []
            simulate(problems, params, k, call_latency=lat)
            pred = [x for p in lat for x in p]
            meas = [c[3] for p in problems for c in p]
        else:
            calls = item[2]
            pred = replay([c[:4] for c in calls], params)
            meas = [c[4] for c in calls]
        out.append(np.log(np.maximum(pred, 1e-6)) - np.log(meas))
    return np.concatenate(out)


def isolated_start(data: list, model: str) -> np.ndarray:
    """Start point: regression latency = o + c P + d C over the model's calls, b and e small."""
    rows = [c for item in data for c in ([x for p in item[3] for x in p] if item[0] == "closed"
                                          else [(x[1], x[2], x[3], x[4]) for x in item[2]]) if c[0] == model]
    a = np.array([r[1:] for r in rows], dtype=float)
    coef = np.linalg.lstsq(np.c_[np.ones(len(a)), a[:, 0], a[:, 1]], a[:, 2], rcond=None)[0]
    d = max(coef[2], 1e-4)
    return np.clip(np.log([max(coef[0], 1e-3), max(coef[1], 1e-6), 0.9 * d, 0.02 * d, 0.02 * d]), LOW, HIGH)


def fit_family(args) -> Dict[str, dict]:
    fam, data = args
    models = [m for m in FAMILIES[fam] if any(
        c[0] == m for item in data for c in ([x for p in item[3] for x in p] if item[0] == "closed" else
                                              [(x[1],) for x in item[2]]))]
    unpack = lambda z: {m: dict(zip(NAMES, np.exp(z[5 * i:5 * i + 5]))) for i, m in enumerate(models)}
    bounds = (np.tile(LOW, len(models)), np.tile(HIGH, len(models)))
    # Stage 1, open loop (stable start); stage 2, closed loop from there. Started from a
    # pooled regression, the closed-loop fit can settle where a saturated server stays
    # saturated (Qwen 1.5B/7B HotpotQA +76%), so stage 2 starts from stage 1.
    opened = [open_loop(it) if it[0] == "closed" else it for it in data]
    x0 = np.concatenate([isolated_start(data, m) for m in models])
    st1 = least_squares(lambda z: residuals(unpack(z), opened), x0, diff_step=1e-3, max_nfev=60, bounds=bounds)
    sol = least_squares(lambda z: residuals(unpack(z), data), st1.x, diff_step=1e-3, max_nfev=80, bounds=bounds)
    if np.sum(residuals(unpack(st1.x), data) ** 2) < 2 * sol.cost:  # keep stage 1 if stage 2 got worse
        sol = st1
    params = unpack(sol.x)
    r = residuals(params, data)
    srcs = [item[1] for item in data for _ in range(sum(len(p) for p in item[3]) if item[0] == "closed" else len(item[2]))]
    by = defaultdict(list)
    for s, x in zip(srcs, r):
        by[s].append(x)
    for m in models:
        params[m] = {k: float(v) for k, v in params[m].items()}
        params[m]["family"] = fam
    params["_fit"] = {"family": fam, "n_calls": int(len(r)), "rmse_log": float(np.sqrt(np.mean(r ** 2))),
                      "mean_log_residual_by_source": {s: float(np.mean(v)) for s, v in sorted(by.items())},
                      "nfev": int(sol.nfev)}
    return params


def grid_betas(results: str) -> dict:
    """quantile -> pair -> placement -> {large_to_small, small_to_large}."""
    out = {"p50": {}, "p95": {}}
    names = ("large_to_small", "small_to_large")
    for pair in PAIRS:
        fr = json.load(open(f"{results}/P5/h4grid/{pair}/fit/fit_results.json"))["full_fit"]
        mp = json.load(open(f"{results}/P5/h4grid/{pair}/fit/mps_fit.json"))["shared_mps"]
        for q in out:
            out[q][pair] = {"shared": dict(zip(names, fr[f"AgentIconq_{q}"]["params"])),
                            "shared_mps": dict(zip(names, mp[f"AgentIconq_{q}"]["params"]))}
    return out


def nearest_pair(a: str, b: str) -> str:
    """The grid pair holding both models, else the one closest in log size."""
    for pair, models in PAIRS.items():
        if {a, b} == set(models):
            return pair
    lo, hi = sorted((SIZE_B[a], SIZE_B[b]))
    return min(PAIRS, key=lambda p: abs(math.log(SIZE_B[PAIRS[p][0]] / lo)) + abs(math.log(SIZE_B[PAIRS[p][1]] / hi)))


def betas_for(models, placement: str, params: dict) -> Dict[tuple, float]:
    """betas[(other, model)] for the models served on one GPU; {} for separate."""
    if placement == "separate":
        return {}
    out = {}
    for m in models:
        for o in models:
            if o == m:
                continue
            b = params["betas"][grid_pair(o, m, params)][placement]
            out[(o, m)] = b["large_to_small"] if SIZE_B[o] > SIZE_B[m] else b["small_to_large"]
            # rev2: factors measured for this exact directed pair (X1c A16 runs) replace the borrowed ones
            out[(o, m)] = params.get("pair_betas", {}).get(placement, {}).get(f"{o}->{m}", out[(o, m)])
    return out


def grid_pair(a: str, b: str, params: dict) -> str:
    """A grid in params["betas"] measured on exactly these two models (rev2 adds "phi"), else nearest_pair."""
    for fam in params["betas"]:
        if fam in FAMILIES and {a, b} == set(FAMILIES[fam]):
            return fam
    return nearest_pair(a, b)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", default="results/v2")
    ap.add_argument("--out", default="results/latsim/params.json")
    args = ap.parse_args()
    data = family_data(args.results)
    with Pool(len(data)) as pool:
        fits = pool.map(fit_family, sorted(data.items()))
    models, fit_info = {}, {}
    for f in fits:
        info = f.pop("_fit")
        fit_info[info["family"]] = info
        models.update(f)
    for m, p in sorted(models.items()):
        print(f"{m}: " + ", ".join(f"{k}={v:.4g}" for k, v in p.items() if k != "family"))
    for fam, info in fit_info.items():
        print(f"{fam}: rmse_log {info['rmse_log']:.3f}, mean residual by source "
              + ", ".join(f"{s} {v:+.3f}" for s, v in info["mean_log_residual_by_source"].items()))
    params = {"models": models, "fit": fit_info, "betas_by_quantile": grid_betas(args.results)}
    from agentqo.latsim.predict import p5_check  # noqa: E402 (avoids an import cycle)
    scores = {}
    for q in ("p50", "p95"):
        params["betas"] = params["betas_by_quantile"][q]
        rows = [r for r in p5_check(args.results, params) if r["placement"] != "separate"]
        scores[q] = float(np.mean([abs(r["pred_p95"] / r["meas_p95"] - 1) <= 0.10 for r in rows]))
    q = max(scores, key=lambda x: (scores[x], x == "p50"))
    params["beta_quantile"], params["beta_choice_scores"] = q, scores
    params["betas"] = params["betas_by_quantile"][q]
    print(f"beta quantile {q} (P5 shared/MPS share of plans with p95 within 10%: {scores})")
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(params, open(args.out, "w"), indent=1)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
