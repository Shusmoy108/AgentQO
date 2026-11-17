"""Baseline predictions, from the same fit-side data P6 used (no test data):

* h3c: scripts/v2/pareto.py LatencyModel as P6 ran it for H3c: per problem the longest
  path of per-(problem, node, tier) median call latency, times the placement's factor
  from h4_fit.simulate's fixed point with configs/v2_interference.yaml (Session 1 betas)
  at the given K; percentiles over problems. Latency base: P5/separate placement_calls for
  math_q15_7 (as P6), else the setting's h3_calls. Binary (small/large) plans only, so
  math_tiers has no h3c prediction. p50 is the same model's median (P6 reported p95 only).
* mean_sum: sum over the plan's calls of the mean (node, tier) call latency in the same
  base; one number for p50 and p95, any placement and K.
"""

from __future__ import annotations

import csv
import gzip
import os
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import List

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentqo.latsim.predict import KS, PLACEMENTS, SETTINGS  # noqa: E402

def workflow_of(setting: str) -> str:
    return "hotpot_iso" if setting.startswith("hotpot_iso") else setting.split("_")[0]


def base_calls(results: str, setting: str) -> List[dict]:
    if setting == "math_q15_7" and os.path.exists(f"{results}/P5/separate/placement_calls.csv"):
        path = f"{results}/P5/separate/placement_calls.csv"
    else:
        path = f"{results}/{SETTINGS[setting]}/plans/h3_calls.csv"
    f = open(path, newline="") if os.path.exists(path) else gzip.open(path + ".gz", "rt", newline="")
    with f:
        return list(csv.DictReader(f))


def baselines(results: str, setting: str, interference: str = "configs/v2_interference.yaml") -> List[dict]:
    from scripts.run_real_pipeline import WORKFLOWS
    from scripts.v2.pareto import LatencyModel
    from scripts.h4_fit import pct
    from agentqo.policies.v2_rules import parse_plan_name

    wf = WORKFLOWS[workflow_of(setting)][1]()
    topo = list(wf.topological_order)
    calls = base_calls(results, setting)
    plans = sorted({c["plan"] for c in calls})
    if setting == "math_q15_7":  # the P5 base has 7 plans; predict every plan of the setting
        with open(f"{results}/{SETTINGS[setting]}/plans/h3_calls.csv", newline="") as f:
            plans = sorted({r["plan"] for r in csv.DictReader(f)})
    betas = yaml.safe_load(open(ROOT / interference))["placements"]
    binary = setting != "math_tiers"
    model = LatencyModel(calls, wf) if binary else None
    node_mean = defaultdict(list)
    for c in calls:
        node_mean[(c["node_id"], c["fidelity"])].append(float(c["latency_s"]))
    node_mean = {k: statistics.mean(v) for k, v in node_mean.items()}
    tiers_of = {}
    for c in calls:
        tiers_of.setdefault(c["plan"], {})[c["node_id"]] = c["fidelity"]
    out = []
    for name in plans:
        if binary:
            plan = parse_plan_name(name, topo)
            tier = {n: model.tier(n, plan) for n in topo}
        else:
            tier = tiers_of[name]
        mean_sum = sum(node_mean.get((n, tier[n]), 0.0) for n in topo if n in tier)
        for pl in PLACEMENTS:
            for k in KS:
                row = {"setting": setting, "plan": name, "placement": pl, "k": k,
                       "mean_sum_p50": mean_sum, "mean_sum_p95": mean_sum, "h3c_p50": "", "h3c_p95": ""}
                if binary:
                    fac = model.factors(plan, betas[pl], k)
                    lengths = []
                    for task in model.tasks:
                        finish = {}
                        for n in model.topo:
                            t = model.tier(n, plan)
                            lat = model.cell.get((task, n, t), model.node_mean.get((n, t), 0.0))
                            ready = max((finish[i] for i in model.wf.nodes[n].inputs), default=0.0)
                            finish[n] = ready + lat * fac[t]
                        lengths.append(max(finish.values()))
                    row["h3c_p50"], row["h3c_p95"] = pct(lengths, 0.5), pct(lengths, 0.95)
                out.append(row)
    return out
