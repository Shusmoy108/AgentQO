#!/usr/bin/env python3
"""F4 analysis helpers (run from ~/AgentQO).

  curve        label-size curve from an H1 run on LABEL (F4a)
  f4b-check    F4b vs F3b: per-problem results equal for identical node sets
  candidates   candidate node sets per budget for a setting -> JSON (+ --custom-plan args)
  select       plan-level selector from a VALID run, scored on EVAL
"""
import argparse
import csv
import glob
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, ".")


def boot_ci(x, f=np.mean, n=2000):
    x = np.asarray(x, dtype=float)
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(x), (n, len(x)))
    m = np.array([f(x[i]) for i in idx])
    return float(f(x)), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def plans_csv(d):
    return {r["plan"]: r for r in csv.DictReader(open(Path(d) / "h3_plans.csv"))}


# ---------------------------------------------------------------- curve
def cmd_curve(a):
    os.environ.setdefault("AGENTQO_VERIFIER", "passthrough")
    from scripts.run_real_h3 import is_llm_node
    from scripts.run_real_pipeline import WORKFLOWS
    wf = WORKFLOWS["math"][1]()
    llm = [n for n in wf.topological_order if is_llm_node(wf, n)]
    d = Path(a.h1) / "h1" / "math_reasoning_s3_ver"
    qids = json.load(open(Path(a.h1) / "run_config.json"))["qids"]
    base = {json.load(open(t))["task_id"]: float(json.load(open(t))["final_quality"]) for t in glob.glob(f"{d}/traces/*.json")}
    sub = defaultdict(dict)
    for f in glob.glob(f"{d}/substitutions/*.json"):
        r = json.load(open(f))
        sub[r["node_id"]][r["task_id"]] = r
    gains = {r["plan"][5:]: float(r["gain_vs_small"]) for r in plans_csv(a.f3b).values() if r["plan"].startswith("only_")}
    rows = []
    for n in a.ns:
        tasks = qids[:n]
        node = {}
        for nid in llm:
            qp = [sub[nid][t]["q_plus"] - base[t] for t in tasks]
            cons = [sub[nid][t]["consequence"] for t in tasks]
            perr = [sub[nid][t]["p_err"] for t in tasks]
            pair = np.array([cons, perr]).T
            ec = boot_ci(np.arange(n), lambda i: np.mean(pair[i.astype(int), 0]) * np.mean(pair[i.astype(int), 1]))
            node[nid] = {"qplus": boot_ci(qp), "consequence": boot_ci(cons), "ec": ec}
        rank_q = sorted(llm, key=lambda x: -node[x]["qplus"][0])
        rank_e = sorted(llm, key=lambda x: -node[x]["ec"][0])
        common = [x for x in llm if x in gains]
        rq = spearmanr([node[x]["qplus"][0] for x in common], [gains[x] for x in common])[0]
        re_ = spearmanr([node[x]["ec"][0] for x in common], [gains[x] for x in common])[0]
        diff = boot_ci([sub["planner"][t]["q_plus"] - sub["aggregator"][t]["q_plus"] for t in tasks])
        row = {"n": n, "rank_qplus": " > ".join(rank_q), "rank_ec": " > ".join(rank_e),
               "spearman_qplus_vs_f3b_gain": rq, "spearman_ec_vs_f3b_gain": re_,
               "qplus_planner_minus_aggregator": diff[0], "diff_ci_low": diff[1], "diff_ci_high": diff[2]}
        for nid in llm:
            for m in ("qplus", "consequence", "ec"):
                row[f"{nid}_{m}"], row[f"{nid}_{m}_lo"], row[f"{nid}_{m}_hi"] = node[nid][m]
        rows.append(row)
        print(f"n={n:<4} Q+ rank: {row['rank_qplus']:<55} rho(Q+)={rq:+.2f}  rho(EC)={re_:+.2f}  "
              f"Q+(planner)-Q+(aggregator)={diff[0]:+.3f} [{diff[1]:+.3f},{diff[2]:+.3f}]")
        print("        " + "  ".join(f"{x}: Q+ {node[x]['qplus'][0]:+.3f} [{node[x]['qplus'][1]:+.3f},{node[x]['qplus'][2]:+.3f}]"
                                     f" EC {node[x]['ec'][0]:+.3f}" for x in llm))
    out = Path(a.h1) / "label_size_curve.csv"
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for x in llm:
        ax[0].errorbar(a.ns, [r[f"{x}_qplus"] for r in rows],
                       yerr=[[r[f"{x}_qplus"] - r[f"{x}_qplus_lo"] for r in rows], [r[f"{x}_qplus_hi"] - r[f"{x}_qplus"] for r in rows]],
                       marker="o", capsize=3, label=x)
    ax[0].axhline(0, color="k", lw=0.6)
    ax[0].set_xlabel("label problems n")
    ax[0].set_ylabel("Q+ - baseline (95% CI)")
    ax[0].legend(fontsize=8)
    ax[1].plot(a.ns, [r["spearman_qplus_vs_f3b_gain"] for r in rows], marker="o", label="Q+")
    ax[1].plot(a.ns, [r["spearman_ec_vs_f3b_gain"] for r in rows], marker="o", label="EC")
    ax[1].axhline(0, color="k", lw=0.6)
    ax[1].set_xlabel("label problems n")
    ax[1].set_ylabel("Spearman vs F3b single-node gain (EVAL)")
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(Path(a.h1) / "label_size_curve.png", dpi=130)
    print(f"wrote {out} and label_size_curve.png")


# ---------------------------------------------------------------- f4b check
def cmd_f4b_check(a):
    p3, p4 = plans_csv(a.f3b), plans_csv(a.f4b)
    t3, t4 = json.load(open(Path(a.f3b) / "h3_traces.json")), json.load(open(Path(a.f4b) / "h3_traces.json"))
    by_set3 = {r["upgraded"]: name for name, r in p3.items()}
    ok = True
    for name, r in p4.items():
        other = by_set3.get(r["upgraded"])
        if other is None:
            print(f"{name:<16} {r['upgraded']:<32} no plan with this node set in F3b")
            continue
        same = t4[name] == t3[other]
        ok &= same
        print(f"{name:<16} {r['upgraded']:<32} = F3b {other:<16} per-problem identical: {same}")
    sys.exit(0 if ok else 1)


# ---------------------------------------------------------------- candidates
def label(nodes):
    return "set_" + "+".join(sorted(nodes))


def cmd_candidates(a):
    os.environ["AGENTQO_VERIFIER"] = a.verifier
    from scripts.run_real_h3 import load_qplus, make_plans
    from scripts.run_real_pipeline import WORKFLOWS
    wf = WORKFLOWS[a.workflow][1]()
    evals = {}
    named = {}
    for d in a.eval_dirs:
        for name, r in plans_csv(d).items():
            evals.setdefault(r["upgraded"], (float(r["accuracy"]), f"{Path(d).name}:{name}"))
            named.setdefault(name, r["upgraded"])
    ec = {}
    if a.h1:
        ec = {n: float(v["ec"]) for n, v in json.load(open(Path(a.h1) / "h1_summary.json"))["by_node"].items()}
    defs = make_plans(wf, ec, extra=True)
    out = {"setting": a.setting, "workflow": a.workflow, "verifier": a.verifier, "budgets": {}, "missing": []}
    for k in (1, 2, 3):
        cands = {}
        for fam in a.families:
            name = f"{fam}_top{k}"
            if name in named:                       # run on EVAL under this name in this setting
                up = named[name]
            elif fam in ("struct", "output", "ec") and name in defs and (fam != "ec" or ec):
                up = ",".join(sorted(defs[name].assignments))
            else:
                continue
            if up not in evals:
                out["missing"].append(f"{name} ({up}): no EVAL result for this node set")
                continue
            cands.setdefault(up, []).append(name)
        out["budgets"][str(k)] = [{"upgraded": up, "rules": rules, "custom": label(up.split(",")),
                                   "eval_accuracy": evals[up][0], "eval_source": evals[up][1]} for up, rules in sorted(cands.items())]
    json.dump(out, open(a.out, "w"), indent=1)
    customs = sorted({c["custom"] + ":" + c["upgraded"].replace(",", "+") for b in out["budgets"].values() for c in b})
    print(" ".join(f"--custom-plan {c}" for c in customs))
    print(",".join(["all_small"] + [c.split(":")[0] for c in customs]), file=sys.stderr)


# ---------------------------------------------------------------- select
def cmd_select(a):
    cand = json.load(open(a.candidates))
    valid = plans_csv(a.valid)
    qp = {}
    if a.qplus_n500:
        from scripts.run_real_h3 import load_qplus
        qp = {n: v["q_plus_minus_baseline"] for n, v in load_qplus(a.qplus_n500).items()}
    res = []
    print(f"setting {cand['setting']}  (VALID: {a.valid})")
    for k, cs in cand["budgets"].items():
        if not cs:
            continue
        for c in cs:
            c["valid_accuracy"] = float(valid[c["custom"]]["accuracy"])
            c["cost"] = float(valid[c["custom"]]["cost_units"])
        best_eval = max(c["eval_accuracy"] for c in cs)

        def pick(pool):
            return sorted(pool, key=lambda c: (-c["valid_accuracy"], c["cost"], c["custom"]))[0]
        p = pick(cs)
        row = {"setting": cand["setting"], "k": int(k), "n_candidates": len(cs), "pick": p["upgraded"],
               "pick_valid": p["valid_accuracy"], "pick_eval": p["eval_accuracy"], "best_eval": best_eval,
               "shortfall": best_eval - p["eval_accuracy"]}
        if qp:
            top2 = sorted(cs, key=lambda c: (-sum(qp.get(n, 0) for n in c["upgraded"].split(",")), c["custom"]))[:2]
            pc = pick(top2)
            row.update({"cheap_pool": " | ".join(c["upgraded"] for c in top2), "cheap_pick": pc["upgraded"],
                        "cheap_pick_eval": pc["eval_accuracy"], "cheap_shortfall": best_eval - pc["eval_accuracy"]})
        res.append(row)
        print(f"  k={k}: " + "; ".join(f"{c['upgraded']} [{'/'.join(c['rules'])}] VALID {c['valid_accuracy']:.3f} EVAL {c['eval_accuracy']:.3f}" for c in cs))
        print(f"       pick {p['upgraded']} (VALID {p['valid_accuracy']:.3f}) EVAL {p['eval_accuracy']:.3f}; best EVAL {best_eval:.3f}; shortfall {row['shortfall']:+.3f}"
              + (f" | cheap pick {row['cheap_pick']} EVAL {row['cheap_pick_eval']:.3f}, shortfall {row['cheap_shortfall']:+.3f}" if qp else ""))
    if cand.get("missing"):
        print("  excluded (no EVAL result): " + "; ".join(cand["missing"]))
    json.dump({"rows": res, "candidates": cand}, open(a.out, "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("curve"); c.add_argument("--h1"); c.add_argument("--f3b"); c.add_argument("--ns", type=int, nargs="+", default=[100, 200, 300, 400, 500]); c.set_defaults(f=cmd_curve)
    c = sub.add_parser("f4b-check"); c.add_argument("--f3b"); c.add_argument("--f4b"); c.set_defaults(f=cmd_f4b_check)
    c = sub.add_parser("candidates"); c.add_argument("--setting"); c.add_argument("--workflow"); c.add_argument("--verifier")
    c.add_argument("--eval-dirs", nargs="+"); c.add_argument("--h1", default=""); c.add_argument("--families", nargs="+", default=["struct", "output", "ec", "qplus"])
    c.add_argument("--out"); c.set_defaults(f=cmd_candidates)
    c = sub.add_parser("select"); c.add_argument("--candidates"); c.add_argument("--valid"); c.add_argument("--qplus-n500", default=""); c.add_argument("--out"); c.set_defaults(f=cmd_select)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
