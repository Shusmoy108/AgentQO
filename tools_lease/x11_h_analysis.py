#!/usr/bin/env python3
"""L2-X11 confirmatory analyses (offline, no model calls), exactly as registered in prereg/v2_amendments.md:
H1d (d488d333), H5c (7a67f064), H5c-b2 (b9fe2c9e). Selection data: X5 / X7 plan-evaluation per-problem data; scoring data:
X11 held-out per-problem data. usage: x11_h_analysis.py OUT_DIR   (reads the Mac mirror ~/AgentQO_results/v2)"""
import csv, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.expanduser("~/AgentQO_x"))
from scripts.run_real_pipeline import WORKFLOWS          # noqa: E402
from agentqo.policies.v2_rules import structural_order   # noqa: E402

M = os.path.expanduser("~/AgentQO_results/v2")
SET = {"math500_q15_7": ("math", f"{M}/vm-A/results/v2/X5/math500_q15_7/plans", f"{M}/vm-A/results/v2/X11/math500_q15_7/plans"),
       "code_c15_7": ("code", f"{M}/vm-B/results/v2/X7/code_c15_7/plans", f"{M}/vm-A/results/v2/X11/code_c15_7/plans")}
TAU, EPS, SEEDS = 0.0134, 0.0134, range(30)

def load(d):
    plans = {r["plan"]: r for r in csv.DictReader(open(f"{d}/h3_plans.csv"))}
    pp = {}
    for r in csv.DictReader(open(f"{d}/h3_per_problem.csv")):
        pp.setdefault(r["plan"], {})[r["task_id"]] = float(r["correct"])
    tasks = sorted(next(iter(pp.values())))
    mat = {p: np.array([pp[p][t] for t in tasks]) for p in pp}
    return plans, mat, tasks

def ups(plan, agents):
    if plan == "all_small": return frozenset()
    if plan == "all_large": return frozenset(agents)
    if plan.startswith("only_"): return frozenset([plan[5:]])
    return frozenset(plan.split("+"))

def key(plan, acc, cost):  # tie-break: higher accuracy, then lower cost_units, then plan name
    return (-acc, cost[plan], plan)

def pick_best(cands, acc, cost):
    return min(cands, key=lambda p: key(p, acc[p], cost))

def h1d(name, wf, ev, ho):
    (eplans, emat, _), (_, hmat, _) = ev, ho
    agents = list(wf.topological_order); struct = structural_order(wf)
    up = {p: ups(p, agents) for p in emat}; by_set = {v: p for p, v in up.items()}
    cost = {p: float(eplans[p]["cost_units"]) for p in emat}
    eacc = {p: emat[p].mean() for p in emat}; hacc = {p: hmat[p].mean() for p in hmat}
    base = emat["all_small"]
    uv = {a: emat[f"only_{a}"].mean() - base.mean() for a in agents}
    rng = np.random.default_rng(0); n = len(base); idx = rng.integers(0, n, size=(2000, n))
    lo = {a: float(np.percentile((emat[f"only_{a}"] - base)[idx].mean(axis=1), 2.5)) for a in agents}
    sidx = {a: struct.index(a) for a in agents}
    rank_uv = sorted(agents, key=lambda a: (-uv[a], sidx[a]))
    sure = sorted([a for a in agents if lo[a] > 0], key=lambda a: (-uv[a], sidx[a]))
    rank_conf = sure + [a for a in struct if a not in sure]
    out = {"uv": {a: round(uv[a], 4) for a in agents}, "uv_ci_low": {a: round(lo[a], 4) for a in agents},
           "rank_uv": rank_uv, "rank_confident_uv": rank_conf, "rank_structural": struct, "k": {}}
    for k in (1, 2, 3):
        elig = [p for p in emat if len(up[p]) <= k]
        best_ho = max(hacc[p] for p in elig)
        picks = {"uv": by_set[frozenset(rank_uv[:k])], "confident_uv": by_set[frozenset(rank_conf[:k])],
                 "structural_topk": by_set[frozenset(struct[:k])], "eval_exhaustive": pick_best(elig, eacc, cost)}
        out["k"][k] = {m: {"plan": p, "eval_acc": round(eacc[p], 4), "heldout_acc": round(hacc[p], 4),
                           "regret": round(best_ho - hacc[p], 4)} for m, p in picks.items()}
        out["k"][k]["best_heldout_le_k"] = round(best_ho, 4)
    r = lambda k, m: out["k"][k][m]["regret"]
    out["criterion"] = {f"k{k}": {"uv_regret_le_0.02": bool(r(k, "uv") <= 0.02 + 1e-12),
                                  "uv_minus_exhaustive": round(r(k, "uv") - r(k, "eval_exhaustive"), 4),
                                  "uv_not_worse_than_exhaustive_by_tau": bool(r(k, "uv") - r(k, "eval_exhaustive") <= TAU + 1e-12)} for k in (1, 2)}
    out["held_in_setting"] = all(all(v for kk, v in c.items() if isinstance(v, bool)) for c in out["criterion"].values())
    return out

def race(emat, cost, order, rule):
    plans = sorted(emat); N = len(order); n = 25; live = list(plans); seen = {p: 0 for p in plans}
    while True:
        n = min(n, N)
        for p in live: seen[p] = max(seen[p], n)
        sub = {p: emat[p][order[:n]] for p in live}; acc = {p: sub[p].mean() for p in live}
        leader = pick_best(live, acc, cost)
        if len(live) == 1: break
        ub = {}
        for p in live:
            if p == leader: continue
            d = sub[p] - sub[leader]; sd = d.std(ddof=1) if n > 1 else 0.0
            if rule == "b2" and sd == 0: sd = 0.5
            ub[p] = d.mean() + 1.96 * sd / math.sqrt(n)
        drop = (lambda u: u < -EPS) if rule == "b" else (lambda u: u < 0)
        live = [p for p in live if p == leader or not drop(ub[p])]
        if len(live) == 1: break
        if rule == "b2" and all(ub[p] <= EPS for p in live if p != leader): break
        if n == N: break
        n += 25
    acc = {p: emat[p][order[:n]].mean() for p in live}
    return pick_best(live, acc, cost), sum(seen.values())

def halving(emat, cost, order):
    N = len(order); n = 25; live = sorted(emat); seen = {p: 0 for p in live}
    while True:
        n = min(n, N)
        for p in live: seen[p] = max(seen[p], n)
        acc = {p: emat[p][order[:n]].mean() for p in live}
        if len(live) == 1 or n == N: return pick_best(live, acc, cost), sum(seen.values())
        live = sorted(live, key=lambda p: key(p, acc[p], cost))[:math.ceil(len(live) / 3)]
        if len(live) == 1: return live[0], sum(seen.values())
        n *= 3

def h5c(name, ev, ho):
    (eplans, emat, etasks), (_, hmat, _) = ev, ho
    cost = {p: float(eplans[p]["cost_units"]) for p in emat}
    hacc = {p: hmat[p].mean() for p in hmat}; best_ho = max(hacc.values())
    exh = pick_best(list(emat), {p: emat[p].mean() for p in emat}, cost); exh_cells = len(emat) * len(etasks)
    out = {"exhaustive": {"plan": exh, "heldout_regret": round(best_ho - hacc[exh], 4), "evaluations": exh_cells}, "methods": {}}
    for m in ("a_halving", "b_racing", "b2_racing_good_enough"):
        regs, cells, picks = [], [], []
        for s in SEEDS:
            order = np.random.default_rng(s).permutation(len(etasks))
            p, c = halving(emat, cost, order) if m == "a_halving" else race(emat, cost, order, "b" if m == "b_racing" else "b2")
            regs.append(best_ho - hacc[p]); cells.append(c); picks.append(p)
        mr, mc = float(np.mean(regs)), float(np.mean(cells))
        out["methods"][m] = {"mean_heldout_regret": round(mr, 4), "regret_minus_exhaustive": round(mr - (best_ho - hacc[exh]), 4),
                             "mean_evaluations": round(mc, 1), "evaluation_share": round(mc / exh_cells, 4),
                             "within_tau": bool(mr - (best_ho - hacc[exh]) <= TAU + 1e-12), "le_40pct": bool(mc <= 0.4 * exh_cells),
                             "picks": {p: picks.count(p) for p in sorted(set(picks))}}
    return out

def main():
    od = sys.argv[1]; os.makedirs(f"{od}/H1d", exist_ok=True); os.makedirs(f"{od}/H5c", exist_ok=True)
    r1, r5 = {}, {}
    for name, (wfk, edir, hdir) in SET.items():
        wf = WORKFLOWS[wfk][1](); ev, ho = load(edir), load(hdir)
        assert set(ev[1]) == set(ho[1]), f"{name}: plan sets differ"
        assert not set(ev[2]) & set(ho[2]), f"{name}: eval and held-out problems overlap"
        r1[name], r5[name] = h1d(name, wf, ev, ho), h5c(name, ev, ho)
    v1 = all(r["held_in_setting"] for r in r1.values())
    v5 = {m: all(r5[s]["methods"][m]["within_tau"] and r5[s]["methods"][m]["le_40pct"] for s in r5) for m in ("a_halving", "b_racing", "b2_racing_good_enough")}
    h5c_held = v5["a_halving"] and v5["b_racing"]
    json.dump({"settings": r1, "H1d": "HELD" if v1 else "NOT HELD"}, open(f"{od}/H1d/h1d.json", "w"), indent=1)
    json.dump({"settings": r5, "H5c (a and b)": "HELD" if h5c_held else "NOT HELD",
               "H5c-b2": "HELD" if v5["b2_racing_good_enough"] else "NOT HELD", "per_method_both_settings": v5}, open(f"{od}/H5c/h5c.json", "w"), indent=1)
    print(json.dumps({"H1d": "HELD" if v1 else "NOT HELD", "H5c": "HELD" if h5c_held else "NOT HELD",
                      "H5c-b2": "HELD" if v5["b2_racing_good_enough"] else "NOT HELD"}))

if __name__ == "__main__":
    main()
