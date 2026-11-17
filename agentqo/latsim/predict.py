"""Predict p50/p95 of every plan of every setting, per placement and K, from h3_calls tokens.

    python3 -m agentqo.latsim.predict --params results/latsim/params.json \
        --out results/latsim/predictions.csv

Problems = the first 64 task_ids of the setting's h3_calls (P5's and X1's problem set:
"the first 64 problems of P5's split"; checked equal to P5's for math_q15_7). Each
problem replays its calls in h3_calls order (the executor's topological order).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import os
from collections import defaultdict
from multiprocessing import Pool
from typing import Dict, List

import numpy as np

from agentqo.latsim.fit import betas_for, read_rows
from agentqo.latsim.sim import pct, simulate

SETTINGS = {
    "math_q15_7": "P2/math_q15_7", "hotpot_q15_7": "P2/hotpot_q15_7", "hotpot_iso_q15_7": "P2/hotpot_iso_q15_7",
    "math_tiers": "P2b/math_tiers", "complex_q15_7": "P2c/complex_q15_7", "math_q3_14": "P3/math_q3_14",
    "math_granite": "P4/math_granite", "hotpot_granite": "P4/hotpot_granite",
    "hotpot_iso_granite": "P4/hotpot_iso_granite", "math_phi": "P4b/math_phi", "hotpot_phi": "P4b/hotpot_phi",
}
P5_SETTING = {  # P5 folder prefix -> setting whose h3_calls tokens it ran
    "separate": "math_q15_7", "shared": "math_q15_7", "cal_qwen_hotpot": "hotpot_q15_7",
    "cal_qwen3_14_math": "math_q3_14", "cal_granite_math": "math_granite",
    "cal_granite_hotpot": "hotpot_granite", "cal_phi_math": "math_phi",
}
PLACEMENTS = ("separate", "shared", "shared_mps")
KS = (1, 4, 8, 16, 32)
N_PROBLEMS = 64


def load_setting(results: str, setting: str, n: int = N_PROBLEMS) -> Dict[str, List[list]]:
    """plan -> per problem [(model, prompt, completion)], first n tasks in file order."""
    base = f"{results}/{SETTINGS[setting]}/plans/h3_calls.csv"
    f = gzip.open(base + ".gz", "rt", newline="") if not os.path.exists(base) else open(base, newline="")
    tasks: Dict[str, int] = {}
    calls: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
    with f:
        for r in csv.DictReader(f):
            t = r["task_id"]
            if t not in tasks:
                if len(tasks) >= n:
                    continue
                tasks[t] = len(tasks)
            calls[r["plan"]][t].append((r["model"], float(r["prompt_tokens"]), float(r["completion_tokens"])))
    order = sorted(tasks, key=tasks.get)
    return {plan: [by[t] for t in order] for plan, by in calls.items()}


def predict_plan(problems, params, placement: str, k: int) -> dict:
    models = sorted({c[0] for p in problems for c in p})
    lat = simulate(problems, params["models"], k, betas_for(models, placement, params))
    return {"pred_p50": pct(lat, 0.5), "pred_p95": pct(lat, 0.95)}


def _job(a):
    setting, plan, problems, params, placements, ks = a
    return [{"setting": setting, "plan": plan, "placement": pl, "k": k, **predict_plan(problems, params, pl, k)}
            for pl in placements for k in ks]


def predict_all(results: str, params: dict, settings=SETTINGS, placements=PLACEMENTS, ks=KS, procs=None):
    jobs = [(s, plan, probs, params, placements, ks)
            for s in settings for plan, probs in sorted(load_setting(results, s).items())]
    with Pool(procs) as pool:
        return [r for rows in pool.imap(_job, jobs, chunksize=4) for r in rows]


def p5_check(results: str, params: dict) -> List[dict]:
    """In-sample: predicted vs measured (mean over repeats) for every P5 placement run."""
    import glob
    out, cache = [], {}
    for path in sorted(glob.glob(f"{results}/P5/*/placement_summary.csv")):
        d = os.path.basename(os.path.dirname(path))
        prefix = next((p for p in sorted(P5_SETTING, key=len, reverse=True) if d.startswith(p)), None)
        if prefix is None:
            continue
        setting = P5_SETTING[prefix]
        if setting not in cache:
            cache[setting] = load_setting(results, setting)
        meas = defaultdict(list)
        for r in read_rows(path):
            meas[(r["plan"], r["placement"], int(r["k"]))].append((float(r["p50_s"]), float(r["p95_s"])))
        for (plan, placement, k), v in sorted(meas.items()):
            pred = predict_plan(cache[setting][plan], params, placement, k)
            out.append({"source": d, "setting": setting, "plan": plan, "placement": placement, "k": k,
                        "n_repeats": len(v), "meas_p50": float(np.mean([x[0] for x in v])),
                        "meas_p95": float(np.mean([x[1] for x in v])), **pred})
    return out


def write_csv(path: str, rows: List[dict]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    import json
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", default="results/v2")
    ap.add_argument("--params", default="results/latsim/params.json")
    ap.add_argument("--out", default="results/latsim/predictions.csv")
    ap.add_argument("--p5-out", default="results/latsim/p5_insample.csv")
    args = ap.parse_args()
    params = json.load(open(args.params))
    write_csv(args.p5_out, p5_check(args.results, params))
    rows = predict_all(args.results, params)
    from agentqo.latsim.baselines import baselines
    with Pool() as pool:
        base = {(b["setting"], b["plan"], b["placement"], b["k"]): b
                for bs in pool.starmap(baselines, [(args.results, s) for s in SETTINGS]) for b in bs}
    empty = {"h3c_p50": "", "h3c_p95": "", "mean_sum_p50": "", "mean_sum_p95": ""}
    for r in rows:
        b = base.get((r["setting"], r["plan"], r["placement"], r["k"]), empty)
        r.update({k: b[k] for k in empty})
    write_csv(args.out, rows)
    print(f"wrote {len(rows)} predictions to {args.out}")


if __name__ == "__main__":
    main()
