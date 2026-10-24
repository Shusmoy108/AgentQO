#!/usr/bin/env python3
"""F5b: EVALBIG reference truth and selector comparison (no GPU). Run from ~/AgentQO."""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from scripts.run_real_h3 import load_qplus  # noqa: E402

D = Path("data/vllm")
CAND = json.load(open(D / "f4_granite_valid_plans/candidates.json"))
QP = {n: v["q_plus_minus_baseline"] for n, v in load_qplus("data/vllm/f4_granite_h1_n500/h1/math_reasoning_s3_ver").items()}


def plans(d):
    return {r["plan"]: r for r in csv.DictReader(open(D / d / "h3_plans.csv"))}


def traces(d):
    return json.load(open(D / d / "h3_traces.json"))


def vec(ts):
    return np.array([t["correct"] for t in ts], dtype=float)


# per-problem vectors for every candidate node set
EVAL = {}
for d in ("f3_granite512_h3_eval200", "f4_granite_h3_eval200"):
    tr = traces(d)
    for name, r in plans(d).items():
        EVAL.setdefault(r["upgraded"], vec(tr[name]))
V1, V2, E2 = traces("f4_granite_valid_plans"), traces("f5_granite_valid2"), traces("f5_granite_eval2")
rule = {}  # rule plan name -> node set, from F3b / F4b
for d in ("f3_granite512_h3_eval200", "f4_granite_h3_eval200"):
    for name, r in plans(d).items():
        rule.setdefault(name, r["upgraded"])


def acc_ci(x, n=2000):
    rng = np.random.default_rng(0)
    m = x[rng.integers(0, len(x), (n, len(x)))].mean(1)
    return float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def paired(a, b):  # C11 method
    d = a - b
    rng = np.random.default_rng(0)
    m = d[rng.integers(0, len(d), (5000, len(d)))].mean(1)
    return float(d.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def pick(cands, score):
    return sorted(cands, key=lambda c: (-score(c), c["cost"], c["custom"]))[0]


out = {"budgets": {}}
rows = []
print("EVALBIG = EVAL (200) + EVAL2 (300); check sets VALID (100, test) + VALID2 (300, train)\n")
for k, cs in CAND["budgets"].items():
    for c in cs:
        c["evalbig"] = np.concatenate([EVAL[c["upgraded"]], vec(E2[c["custom"]])])
        c["check"] = np.concatenate([vec(V1[c["custom"]]), vec(V2[c["custom"]])])  # VALID then VALID2 (400)
        c["cost"] = 3 * len(c["upgraded"].split(","))  # 3 extra units per upgraded node (equal within a budget)
        c["acc"] = acc_ci(c["evalbig"])
    ranked = sorted(cs, key=lambda c: -c["acc"][0])
    best = ranked[0]
    top2 = paired(ranked[0]["evalbig"], ranked[1]["evalbig"])
    print(f"=== budget k={k}: {len(cs)} candidates")
    print(f"  {'node set':<30}{'rules':<34}{'EVALBIG [95% CI]':>24}{'EVAL':>7}{'EVAL2':>7}{'VALID':>7}{'VALID2':>8}{'V+V2':>7}")
    for c in ranked:
        print(f"  {c['upgraded']:<30}{'/'.join(c['rules']):<34}{c['acc'][0]:>8.3f} [{c['acc'][1]:.3f},{c['acc'][2]:.3f}]"
              f"{EVAL[c['upgraded']].mean():7.3f}{vec(E2[c['custom']]).mean():7.3f}{c['check'][:100].mean():7.3f}"
              f"{c['check'][100:].mean():8.3f}{c['check'].mean():7.3f}")
    print(f"  best: {best['upgraded']}; best - second ({ranked[1]['upgraded']}) = {top2[0]:+.3f} [{top2[1]:+.3f}, {top2[2]:+.3f}]")

    def short(c):
        return best["acc"][0] - c["acc"][0]
    by_set = {c["upgraded"]: c for c in cs}
    sel = {}
    sel["S100"] = (pick(cs, lambda c: c["check"][:100].mean()), 100 * len(cs))
    sel["S400"] = (pick(cs, lambda c: c["check"].mean()), 400 * len(cs))
    # successive halving
    alive, n, used = list(cs), 100, 0
    while True:
        used += 100 * len(alive) if n == 100 else 100 * len(alive)
        ranked_n = sorted(alive, key=lambda c: (-c["check"][:n].mean(), c["cost"], c["custom"]))
        if len(ranked_n) == 1:
            break
        ci = paired(ranked_n[0]["check"][:n], ranked_n[1]["check"][:n])
        if ci[1] > 0 or ci[2] < 0 or n >= 400:
            break
        alive = ranked_n[:max(2, math.ceil(len(ranked_n) / 2))]
        n += 100
    sel["SH"] = (ranked_n[0], used)
    sh_n = n
    q_top2 = sorted(cs, key=lambda c: (-sum(QP.get(x, 0) for x in c["upgraded"].split(",")), c["custom"]))[:2]
    sel["Hybrid"] = (pick(q_top2, lambda c: c["check"].mean()), 400 * 2)
    for label, name in (("Q+ (500 labels)", f"qplus500_top{k}"), ("Structure", f"struct_top{k}"),
                        ("Closest-to-answer", f"output_top{k}"), ("EC (100 labels)", f"ec_top{k}")):
        sel[label] = (by_set[rule[name]], 0)
    print("  selectors:")
    res = {}
    for label, (c, cost) in sel.items():
        extra = f"  (check problems: {sh_n}; plan-runs {cost})" if label == "SH" else ""
        print(f"    {label:<18} {c['upgraded']:<30} EVALBIG {c['acc'][0]:.3f}  shortfall {short(c):+.3f}{extra}")
        res[label] = {"pick": c["upgraded"], "evalbig": c["acc"][0], "shortfall": short(c)}
        rows.append({"k": int(k), "selector": label, "pick": c["upgraded"], "evalbig": c["acc"][0], "shortfall": short(c),
                     "sh_problems": sh_n if label == "SH" else ""})
    res["SH"]["problems_used"] = sh_n
    out["budgets"][k] = {"candidates": [{"upgraded": c["upgraded"], "rules": c["rules"], "evalbig": c["acc"],
                                         "valid": c["check"][:100].mean(), "valid2": c["check"][100:].mean(),
                                         "check400": c["check"].mean()} for c in ranked],
                         "best": best["upgraded"], "best_minus_second": top2, "selectors": res}
    print()

# predictions
pl = [c for cs in CAND["budgets"].values() for c in cs]
gs = {c["upgraded"]: c["evalbig"] for c in pl}
p1 = paired(gs["planner"], gs["aggregator"])
p2 = paired(gs["aggregator,planner"], gs["planner,step_1"])
s400 = [out["budgets"][k]["selectors"]["S400"]["shortfall"] for k in out["budgets"]]
sh = [out["budgets"][k]["selectors"]["SH"]["shortfall"] for k in out["budgets"]]
shn = [out["budgets"][k]["selectors"]["SH"]["problems_used"] for k in out["budgets"]]
pred = {
    "P1 planner - aggregator (EVALBIG)": {"value": p1, "held": p1[1] > 0},
    "P2 aggregator+planner - planner+step_1 (EVALBIG)": {"value": p2, "held": p2[1] <= 0 <= p2[2]},
    "P3 S400 shortfalls": {"value": s400, "held": all(x <= 0.03 + 1e-9 for x in s400)},
    "P4 SH shortfalls / mean problems": {"value": [sh, float(np.mean(shn))],
                                          "held": all(x <= 0.03 + 1e-9 for x in sh) and np.mean(shn) < 300},
}
for kk, v in pred.items():
    print(f"{kk}: {v['value']} -> {'HELD' if v['held'] else 'FAILED'}")
out["predictions"] = pred
Path(D / "f5_analysis").mkdir(exist_ok=True)
json.dump(out, open(D / "f5_analysis/f5_results.json", "w"), indent=1, default=float)
with open(D / "f5_analysis/f5_selectors.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print("wrote data/vllm/f5_analysis/f5_results.json and f5_selectors.csv")
