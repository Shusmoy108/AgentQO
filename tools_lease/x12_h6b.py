#!/usr/bin/env python3
"""L2-X12 H6b (registered 5cc73094), offline, no model calls: logistic verifier-upgrade router trained on the eval problems,
threshold chosen on eval, tested on the X2 problems. Also reports the share of problems whose X12 final answer matches the
stored all_small answer. usage: x12_h6b.py OUT_DIR   (reads the Mac mirror ~/AgentQO_results/v2)"""
import csv, json, os, sys
import numpy as np
from sklearn.linear_model import LogisticRegression
sys.path.insert(0, os.path.expanduser("~/AgentQO_x"))
from agentqo.tasks.answers import extract_gsm8k_number   # noqa: E402

M = os.path.expanduser("~/AgentQO_results/v2")
A, B = f"{M}/vm-A/results/v2", f"{M}/vm-B/results/v2"
SET = {"math_q15_7": {"eval": f"{A}/P2/math_q15_7/plans", "x2": f"{A}/X2/math_q15_7/plans", "x12": f"{A}/X12/math_q15_7"},
       "math_granite": {"eval": f"{B}/P4/math_granite/plans", "x2": f"{B}/X2/math_granite/plans", "x12": f"{A}/X12/math_granite"}}
PRICE = {"small": (0.10, 0.50), "large": (2.00, 10.00)}   # USD per 1M input / output tokens (configs/v2_prices.yaml)
AGENTS = ["planner", "step_1", "step_2", "step_3", "aggregator", "verifier"]

def usd(row):
    pi, po = PRICE[row["fidelity"]]
    return (int(row["prompt_tokens"]) * pi + int(row["completion_tokens"]) * po) / 1e6

def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None

def canon(a):
    return extract_gsm8k_number(a) if a not in (None, "", "None") else None

def stored(d):  # per task: all_small and only_verifier correctness, only_verifier cost, its verifier call, all_small pred
    pp = {}
    for r in csv.DictReader(open(f"{d}/h3_per_problem.csv")):
        if r["plan"] in ("all_small", "only_verifier"): pp.setdefault(r["task_id"], {})[r["plan"]] = float(r["correct"])
    ov_cost, ov_ver = {}, {}
    for r in csv.DictReader(open(f"{d}/h3_calls.csv")):
        if r["plan"] == "only_verifier":
            ov_cost[r["task_id"]] = ov_cost.get(r["task_id"], 0.0) + usd(r)
            if r["node_id"] == "verifier": ov_ver[r["task_id"]] = usd(r)
    pred = {t["task_id"]: t["pred"] for t in json.load(open(f"{d}/h3_traces.json"))["all_small"]}
    return pp, ov_cost, ov_ver, pred

def x12(d):  # per task: X12 all_small correctness, cost, features, final pred
    cor = {r["task_id"]: float(r["correct"]) for r in csv.DictReader(open(f"{d}/h3_per_problem.csv"))}
    pred = {t["task_id"]: t["pred"] for t in json.load(open(f"{d}/h3_traces.json"))["all_small"]}
    calls = {}
    for r in csv.DictReader(open(f"{d}/h3_calls.csv")):
        calls.setdefault(r["task_id"], {})[r["node_id"]] = r
    feats, cost = {}, {}
    for t, c in calls.items():
        cost[t] = sum(usd(r) for r in c.values())
        ans = {a: canon(c[a].get("answer_text")) for a in AGENTS if a in c}
        v = ans.get("verifier"); others = [a for a in AGENTS if a != "verifier" and ans.get(a) is not None]
        agree = (sum(ans[a] == v for a in others) / len(others)) if (others and v is not None) else None
        alp = [num(c[a].get("answer_logprob")) for a in AGENTS if a in c]
        feats[t] = [agree,
                    float(ans.get("aggregator") is not None and ans.get("aggregator") == v),
                    float(len({x for x in ans.values() if x is not None})),
                    num(c.get("verifier", {}).get("mean_logprob")),
                    num(c.get("verifier", {}).get("answer_logprob")),
                    num(c.get("aggregator", {}).get("answer_logprob")),
                    min([x for x in alp if x is not None], default=None),
                    float(np.mean([num(c[a]["mean_logprob"]) for a in AGENTS if a in c and num(c[a].get("mean_logprob")) is not None]))]
    return cor, cost, feats, pred

FEATS = ["agree_share_with_verifier", "aggregator_eq_verifier", "n_distinct_answers", "verifier_mean_logprob",
         "verifier_answer_logprob", "aggregator_answer_logprob", "min_answer_logprob", "mean_of_mean_logprob"]

def matrix(feats, tasks, fill=None):
    X = np.array([[np.nan if v is None else v for v in feats[t]] for t in tasks], dtype=float)
    if fill is None: fill = np.nanmean(X, axis=0)
    X = np.where(np.isnan(X), fill, X)
    return X, fill

def evaluate(tasks, p, t, small, up, cost_small, cost_ver):
    route = p >= t
    acc = np.mean([up[x] if r else small[x] for x, r in zip(tasks, route)])
    cost = np.mean([cost_small[x] + (cost_ver[x] if r else 0.0) for x, r in zip(tasks, route)])
    return float(acc), float(cost), float(route.mean())

def run(name, cfg):
    out = {}
    parts = {}
    for part in ("eval", "x2"):
        pp, ov_cost, ov_ver, spred = stored(cfg[part])
        cor, cost, feats, xpred = x12(f"{cfg['x12']}/{part}")
        tasks = sorted(cor)
        assert set(tasks) == set(pp), f"{name} {part}: X12 and stored problems differ"
        parts[part] = dict(tasks=tasks, small={t: cor[t] for t in tasks}, up={t: pp[t]["only_verifier"] for t in tasks},
                           cs=cost, cv=ov_ver, fixed_cost=float(np.mean([ov_cost[t] for t in tasks])),
                           fixed_acc=float(np.mean([pp[t]["only_verifier"] for t in tasks])), feats=feats,
                           match=float(np.mean([str(xpred.get(t)) == str(spred.get(t)) for t in tasks])),
                           x12_small=float(np.mean([cor[t] for t in tasks])), stored_small=float(np.mean([pp[t]["all_small"] for t in tasks])))
        out[f"{part}_answer_match_share_vs_stored_all_small"] = round(parts[part]["match"], 4)
        out[f"{part}_all_small_acc_x12_vs_stored"] = [round(parts[part]["x12_small"], 4), round(parts[part]["stored_small"], 4)]
    e, h = parts["eval"], parts["x2"]
    Xe, fill = matrix(e["feats"], e["tasks"]); mu, sd = Xe.mean(0), Xe.std(0); sd[sd == 0] = 1
    ye = np.array([1 - e["small"][t] for t in e["tasks"]])
    clf = LogisticRegression(C=1.0, max_iter=1000).fit((Xe - mu) / sd, ye)
    pe = clf.predict_proba((Xe - mu) / sd)[:, 1]
    Xh, _ = matrix(h["feats"], h["tasks"], fill); ph = clf.predict_proba((Xh - mu) / sd)[:, 1]
    best = None
    for t in sorted(set(pe.tolist()) | {0.0, 1.01}):
        acc, cost, share = evaluate(e["tasks"], pe, t, e["small"], e["up"], e["cs"], e["cv"])
        if acc >= e["fixed_acc"] - 0.01 and (best is None or cost < best[1] or (cost == best[1] and t > best[0])):
            best = (t, cost, acc, share)
    t = best[0] if best else 0.0
    ea, ec, es = evaluate(e["tasks"], pe, t, e["small"], e["up"], e["cs"], e["cv"])
    ha, hc, hs = evaluate(h["tasks"], ph, t, h["small"], h["up"], h["cs"], h["cv"])
    out.update({"features": FEATS, "coef": [round(c, 4) for c in clf.coef_[0]], "intercept": round(float(clf.intercept_[0]), 4),
                "threshold": t, "threshold_rule": "cheapest eval cost with eval acc >= fixed - 0.01" if best else "none qualified: t = 0",
                "eval": {"router_acc": round(ea, 4), "fixed_acc": round(e["fixed_acc"], 4), "router_cost": ec, "fixed_cost": e["fixed_cost"],
                         "cost_ratio": round(ec / e["fixed_cost"], 4), "upgrade_share": round(es, 4)},
                "heldout_x2": {"router_acc": round(ha, 4), "fixed_acc": round(h["fixed_acc"], 4), "router_cost": hc, "fixed_cost": h["fixed_cost"],
                               "cost_ratio": round(hc / h["fixed_cost"], 4), "upgrade_share": round(hs, 4),
                               "acc_ok": bool(ha >= h["fixed_acc"] - 0.0134 - 1e-12), "cost_ok": bool(hc <= 0.70 * h["fixed_cost"] + 1e-15)}})
    out["held_in_setting"] = out["heldout_x2"]["acc_ok"] and out["heldout_x2"]["cost_ok"]
    return out

def main():
    od = sys.argv[1]; os.makedirs(f"{od}/H6b", exist_ok=True)
    res = {s: run(s, c) for s, c in SET.items()}
    verdict = "HELD" if all(r["held_in_setting"] for r in res.values()) else "NOT HELD"
    json.dump({"settings": res, "H6b": verdict}, open(f"{od}/H6b/h6b.json", "w"), indent=1)
    print(json.dumps({"H6b": verdict, **{s: {"x2": r["heldout_x2"], "match": [r["eval_answer_match_share_vs_stored_all_small"], r["x2_answer_match_share_vs_stored_all_small"]]} for s, r in res.items()}}, indent=1))

if __name__ == "__main__":
    main()
