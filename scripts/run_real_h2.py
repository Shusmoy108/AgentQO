#!/usr/bin/env python3
"""H2 on real labels from the Chameleon session: can a cheap predictor (no fault injection)
propose candidate plans as good as label-based ones?

    python scripts/run_real_h2.py a1      # label efficiency (no learning)
    python scripts/run_real_h2.py a2      # cheap predictors, splits P/C/W/F, decision value
    python scripts/run_real_h2.py a3      # permutation importance and shortlist failures (G2)

Reads data/vllm/ (H1 label folders, H3 plan results, VALID check-set results); writes data/h2/.
Features never use q_plus, q_minus, consequence, corrupted or descendant texts, the large-model
reference, or held-out plan results. p_err is used only in the "with p_err" variants.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentqo.predictors.features import FeatureExtractor, NUM_ROLES  # noqa: E402
from agentqo.tasks.prompts import code_output  # noqa: E402
from scripts.run_real_pipeline import WORKFLOWS  # noqa: E402

V = Path("data/vllm")
OUT = Path("data/h2")

# label sets: workflow, AGENTQO_VERIFIER, family, H1 folder, EVAL folders, check-set (VALID) folders, F4 candidates
SETS = {
    "L1": dict(wf="math", ver=None, fam="Qwen", h1="h1_n100", evals=[], valid=[], cands=None),
    "L2": dict(wf="math", ver="passthrough", fam="Qwen", h1="h1_math_passthrough_n100",
               evals=["h3_eval_n200", "c12_qplus_top2", "c13_budget_curve"],
               valid=["f4_qwen_valid_plans/math_passthrough"], cands="f4_qwen_valid_plans/math_passthrough/candidates.json"),
    "L3": dict(wf="math", ver="cautious", fam="Qwen", h1="c14_h1_cautious_n100",
               evals=["c14_h3_cautious_eval200", "e1_output_cautious"],
               valid=["f4_qwen_valid_plans/math_cautious"], cands="f4_qwen_valid_plans/math_cautious/candidates.json"),
    "L4": dict(wf="complex", ver="cautious", fam="Qwen", h1="e2_complex_h1_n100",
               evals=["e2_complex_h3_eval200"],
               valid=["f4_qwen_valid_plans/complex_cautious"], cands="f4_qwen_valid_plans/complex_cautious/candidates.json"),
    "L5": dict(wf="complex", ver="passthrough", fam="Qwen", h1="f1_complex_passthrough_h1_n100",
               evals=["f1_complex_passthrough_h3_eval200"],
               valid=["f4_qwen_valid_plans/complex_passthrough"], cands="f4_qwen_valid_plans/complex_passthrough/candidates.json"),
    "L6": dict(wf="math", ver="passthrough", fam="Granite", h1="f3_granite512_h1_n100",
               evals=["f3_granite512_h3_eval200", "f4_granite_h3_eval200"],
               valid=["f4_granite_valid_plans", "f5_granite_valid2"], cands="f4_granite_valid_plans/candidates.json"),
    "L7": dict(wf="math", ver="passthrough", fam="Granite", h1="f4_granite_h1_n500",
               evals=["f3_granite512_h3_eval200", "f4_granite_h3_eval200"],
               valid=["f4_granite_valid_plans", "f5_granite_valid2"], cands="f4_granite_valid_plans/candidates.json"),
}


@contextmanager
def verifier_env(ver):
    old = os.environ.get("AGENTQO_VERIFIER")
    if ver is None:
        os.environ.pop("AGENTQO_VERIFIER", None)
    else:
        os.environ["AGENTQO_VERIFIER"] = ver
    try:
        yield
    finally:
        if old is None:
            os.environ.pop("AGENTQO_VERIFIER", None)
        else:
            os.environ["AGENTQO_VERIFIER"] = old


def log(msg=""):
    print(msg, flush=True)


# ------------------------------------------------------------------ loading
class LabelSet:
    def __init__(self, sid: str):
        c = SETS[sid]
        self.sid, self.cfg, self.family = sid, c, c["fam"]
        self.wf = WORKFLOWS[c["wf"]][1]()
        topo = list(self.wf.topological_order)
        self.topo = topo
        with verifier_env(c["ver"]):
            self.llm = [n for n in topo if code_output(self.wf.nodes[n], {}, {"workflow": self.wf}) is None]
            self.final_is_code = code_output(self.wf.nodes[topo[-1]], {}, {"workflow": self.wf}) is not None
        d = V / c["h1"] / "h1" / self.wf.name
        self.qids = json.load(open(V / c["h1"] / "run_config.json"))["qids"]
        self.traces = {t: json.load(open(d / "traces" / f"{t}.json")) for t in self.qids}
        self.subs = {}
        for t in self.qids:
            for n in self.llm:
                r = json.load(open(d / "substitutions" / f"{t}_{n}.json"))
                self.subs[(t, n)] = r
        self.base = np.array([float(self.traces[t]["final_quality"]) for t in self.qids])
        # per-problem arrays [problem, node]
        self.cons = np.array([[self.subs[(t, n)]["consequence"] for n in self.llm] for t in self.qids], dtype=float)
        self.perr = np.array([[self.subs[(t, n)]["p_err"] for n in self.llm] for t in self.qids], dtype=float)
        self.qplus = np.array([[self.subs[(t, n)]["q_plus"] for n in self.llm] for t in self.qids], dtype=float)
        self.uv = self.qplus - self.base[:, None]
        self._structure()
        self._plans()

    # structure orders (run_real_h3 definitions)
    def _structure(self):
        wf, topo = self.wf, self.topo
        dist = {topo[-1]: 0}
        for n in reversed(topo[:-1]):
            succ = [x for x in topo if n in wf.nodes[x].inputs and x in dist]
            if succ:
                dist[n] = 1 + max(dist[x] for x in succ)
        self.dist = dist
        self.reach = {n: wf.get_downstream_reach(n) for n in topo}
        self.struct_order = sorted(self.llm, key=lambda n: (-self.reach[n], topo.index(n)))
        self.output_order = sorted(self.llm, key=lambda n: (dist[n], -topo.index(n)))

    def _plans(self):
        """EVAL accuracy by node set, VALID (check) accuracy by node set, F4 candidate universe."""
        self.eval_acc, self.only_gain, self.all_small = {}, {}, None
        for d in self.cfg["evals"]:
            for r in csv.DictReader(open(V / d / "h3_plans.csv")):
                up = r["upgraded"]
                self.eval_acc.setdefault(up, float(r["accuracy"]))
                if r["plan"] == "all_small":
                    self.all_small = float(r["accuracy"])
                if r["plan"].startswith("only_"):
                    self.only_gain.setdefault(r["plan"][5:], float(r["gain_vs_small"]))
        self.valid_acc = {}
        sizes = []
        for d in self.cfg["valid"]:
            rows = list(csv.DictReader(open(V / d / "h3_plans.csv")))
            n = len(json.load(open(V / d / "h3_summary.json"))["qids"])
            sizes.append(n)
            for r in rows:
                acc = self.valid_acc.setdefault(r["upgraded"], [0.0, 0])
                acc[0] += float(r["accuracy"]) * n
                acc[1] += n
        self.valid_acc = {k: v[0] / v[1] for k, v in self.valid_acc.items() if v[1] == sum(sizes)}
        self.universe = {}
        if self.cfg["cands"]:
            cj = json.load(open(V / self.cfg["cands"]))
            for k, cs in cj["budgets"].items():
                self.universe[int(k)] = {c["upgraded"]: c["eval_accuracy"] for c in cs}

    # helpers
    def node_scores(self, idx=None):
        i = slice(None) if idx is None else idx
        ec = self.cons[i].mean(0) * self.perr[i].mean(0)
        uv = self.uv[i].mean(0)
        cons = self.cons[i].mean(0)
        return {"EC": dict(zip(self.llm, ec)), "UV": dict(zip(self.llm, uv)), "CONS": dict(zip(self.llm, cons))}

    def rank(self, score: Dict[str, float]) -> List[str]:
        return sorted(self.llm, key=lambda n: (-score[n], self.topo.index(n)))

    def plan_eval(self, nodes):
        """(accuracy, measured?) of the plan upgrading exactly these nodes, on EVAL."""
        key = ",".join(sorted(nodes))
        if key in self.eval_acc:
            return self.eval_acc[key], True
        if self.all_small is not None and all(n in self.only_gain for n in nodes):
            return self.all_small + sum(self.only_gain[n] for n in nodes), False
        return None, False


def key(nodes):
    return ",".join(sorted(nodes))


# ------------------------------------------------------------------ A1
def cmd_a1(_):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    f5 = json.load(open(V / "f5_analysis" / "f5_results.json"))
    big2 = {c["upgraded"]: c["evalbig"][0] for c in f5["budgets"]["2"]["candidates"]}
    for sid in SETS:
        L = LabelSet(sid)
        N = len(L.qids)
        full = L.node_scores()
        ns = [10, 20, 30, 50, 100] + ([200, 300, 400, 500] if sid == "L7" else [])
        log(f"\n=== {sid} ({L.family}, {L.cfg['wf']}, verifier={L.cfg['ver'] or 'original LLM'}), {N} problems, LLM nodes {L.llm}")
        for m in ("UV", "EC"):
            fr = L.rank(full[m])
            log(f"  full-set {m} ranking: " + " > ".join(f"{n} {full[m][n]:+.3f}" for n in fr))
        rng = np.random.default_rng(0)
        for n in ns:
            if n > N:
                continue
            draws = 1 if n == N else 1000
            for m in ("UV", "EC"):
                fr = L.rank(full[m])
                t1 = t2 = 0
                accs, measured, bigs = [], 0, []
                for _ in range(draws):
                    idx = rng.choice(N, size=n, replace=False) if n < N else np.arange(N)
                    s = L.node_scores(idx)[m]
                    r = L.rank(s)
                    t1 += r[0] == fr[0]
                    t2 += set(r[:2]) == set(fr[:2])
                    a, meas = L.plan_eval(r[:2])
                    if a is not None:
                        accs.append(a)
                        measured += meas
                    if sid == "L7" and key(r[:2]) in big2:
                        bigs.append(big2[key(r[:2])])
                row = {"set": sid, "family": L.family, "n": n, "draws": draws, "metric": m,
                       "top1_match": t1 / draws, "top2_set_match": t2 / draws,
                       "exp_eval_acc_top2": float(np.mean(accs)) if accs else "",
                       "eval_acc_measured_share": measured / len(accs) if accs else "",
                       "eval_acc_available_share": len(accs) / draws,
                       "exp_evalbig_acc_top2": float(np.mean(bigs)) if bigs else "",
                       "evalbig_available_share": len(bigs) / draws if sid == "L7" else ""}
                rows.append(row)
                ea = f"{row['exp_eval_acc_top2']:.3f} ({100 * row['eval_acc_measured_share']:.0f}% measured)" if accs else "n/a"
                eb = f"  EVALBIG {row['exp_evalbig_acc_top2']:.3f} ({100 * row['evalbig_available_share']:.0f}% of draws)" if bigs else ""
                log(f"  n={n:<4} {m}: top-1 match {t1 / draws:.3f}  top-2 set match {t2 / draws:.3f}  exp. EVAL acc of top-2 plan {ea}{eb}")
    with open(OUT / "a1_label_efficiency.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    plot_a1(rows)
    log("\nPredictions:")
    q = {r["set"]: r["top1_match"] for r in rows if r["metric"] == "UV" and r["n"] == 30 and r["set"] in ("L2", "L3", "L4", "L5")}
    log(f"  P-A1-1 Qwen L2-L5, n=30, UV top-1 match >= 0.70 in each: {q} -> {'HELD' if all(v >= 0.70 for v in q.values()) else 'FAILED'}")
    g = [r for r in rows if r["metric"] == "UV" and r["n"] == 100 and r["set"] == "L7"][0]
    L7 = LabelSet("L7")
    top_full = L7.rank(L7.node_scores()["UV"])[0]
    log(f"  P-A1-2 L7, n=100, UV top-1 (full-500 top-1 = {top_full}) match < 0.50: {g['top1_match']:.3f} -> "
        f"{'HELD' if g['top1_match'] < 0.50 else 'FAILED'}")
    log(f"wrote {OUT}/a1_label_efficiency.csv and a1_match_vs_n.png")


def plot_a1(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ax, m in zip(axes, ("UV", "EC")):
        for sid in SETS:
            pts = sorted((r["n"], r["top1_match"]) for r in rows if r["set"] == sid and r["metric"] == m)
            ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", label=sid)
        ax.set_xscale("log")
        ax.set_xlabel("label problems n")
        ax.set_title(f"top-1 match with the full label set ({'upgrade value' if m == 'UV' else 'EC'})")
        ax.axhline(0.7, color="grey", lw=0.6, ls="--")
    axes[0].set_ylabel("share of 1000 random subsets")
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "a1_match_vs_n.png", dpi=130)


# ------------------------------------------------------------------ A2: samples and features
STRUCT_NAMES = [f"role_{i}" for i in range(NUM_ROLES)] + [
    "depth", "fan_out", "downstream_reach", "has_downstream_verifier", "is_optional", "is_speculative", "num_inputs",
    "n_downstream", "n_downstream_llm", "dist_to_final", "final_is_code", "repair_capacity"]
OUTPUT_NAMES = ["out_tokens", "answer_extracted", "confidence", "copies_parent"]
PROBLEM_NAMES = ["problem_words", "problem_numbers"]
_NUM = re.compile(r"\d+(?:[.,]\d+)?")


def build_samples(L: LabelSet):
    """Rows: (problem, node) for LLM nodes. Returns dict of arrays + feature matrix with named columns."""
    ex = FeatureExtractor()
    first = L.traces[L.qids[0]]
    prob0 = first["problem"].strip()
    sfeat = {}
    for n in L.llm:
        desc = L.wf.get_descendants(n)
        desc_llm = [d for d in desc if d in L.llm]
        repair = sum(prob0 in first["nodes"][d]["prompt"] for d in desc_llm)
        sfeat[n] = list(ex.extract_structural_features(L.wf, n).structural_features) + [
            len(desc), len(desc_llm), L.dist[n], float(L.final_is_code), repair]
    X, groups, nodes, t1, t2, perr = [], [], [], [], [], []
    for i, t in enumerate(L.qids):
        tr = L.traces[t]
        words = len(tr["problem"].split())
        nums = len(_NUM.findall(tr["problem"]))
        for j, n in enumerate(L.llm):
            nd = tr["nodes"][n]
            ins = list(L.wf.nodes[n].inputs)
            parent_key = tr["nodes"][ins[0]]["key"] if ins and ins[0] in tr["nodes"] else None
            conf = nd.get("confidence")
            X.append(sfeat[n] + [float(nd.get("completion_tokens") or 0), float(nd.get("key") is not None),
                                 float(conf) if conf is not None else 0.0,
                                 float(parent_key is not None and nd.get("key") == parent_key), words, nums])
            groups.append(f"{L.sid}:{t}")
            nodes.append(n)
            t1.append(L.cons[i, j])
            t2.append(L.uv[i, j])
            perr.append(L.perr[i, j])
    return dict(X=np.array(X, dtype=float), group=np.array(groups), node=np.array(nodes),
                T1=np.array(t1), T2=np.array(t2), perr=np.array(perr),
                family=np.full(len(X), 1.0 if L.family == "Granite" else 0.0), set=np.array([L.sid] * len(X)))


TRAIN_SETS = ["L1", "L2", "L3", "L4", "L5", "L7"]
GRID = [dict(n_estimators=ne, max_depth=md, learning_rate=lr) for ne in (100, 300) for md in (2, 3) for lr in (0.05, 0.1)]


def design(S, idx, model, use_family):
    cols = [S["X"][idx]]
    names = STRUCT_NAMES + OUTPUT_NAMES + PROBLEM_NAMES
    if use_family:
        cols.append(S["family"][idx, None])
        names = names + ["family_granite"]
    if model == "G2":
        cols.append(S["perr"][idx, None])
        names = names + ["p_err"]
    return np.hstack(cols), names


def fit_gbt(X, y, groups):
    from joblib import Parallel, delayed
    from sklearn.model_selection import GroupKFold
    from agentqo.predictors.ec_predictor import GBTECPredictor

    folds = list(GroupKFold(n_splits=3).split(X, y, groups))

    def cv(params):
        err = 0.0
        for tr, va in folds:
            m = GBTECPredictor(random_state=42, **params)
            m.fit(X[tr], y[tr])
            err += float(np.mean((m.predict(X[va]) - y[va]) ** 2))
        return err / len(folds)
    errs = Parallel(n_jobs=-1)(delayed(cv)(p) for p in GRID)
    best = GRID[int(np.argmin(errs))]
    m = GBTECPredictor(random_state=42, **best)
    m.fit(X, y)
    return m, best


def split_defs():
    """(split, [(train_sets, test_sets, problem_fold_or_None)])"""
    out = {"P": [], "C": [], "W": [], "F": []}
    for s in TRAIN_SETS:
        for f in range(5):
            out["P"].append(([s], [s], f))
        out["C"].append(([x for x in TRAIN_SETS if x != s], [s], None))
    math, cplx = ["L1", "L2", "L3", "L7"], ["L4", "L5"]
    out["W"] = [(math, cplx, None), (cplx, math, None)]
    out["F"] = [(["L1", "L2", "L3", "L4", "L5"], ["L7"], None), (["L7"], ["L1", "L2", "L3", "L4", "L5"], None)]
    return out


def node_level(L, node_arr, values):
    return {n: float(np.mean(values[node_arr == n])) for n in L.llm}


def spearman(a, b):
    from scipy.stats import spearmanr
    r = spearmanr(a, b)[0]
    return 0.0 if r is None or np.isnan(r) else float(r)


def run_predictions(SETS_DATA, LS):
    """Predictions for every split, test set, model and target. Returns {(split, test_set): {model: {target: per-sample preds}}}."""
    from sklearn.model_selection import GroupKFold
    from agentqo.predictors.ec_predictor import ConfidenceBaseline

    preds, chosen = {}, []
    for split, jobs in split_defs().items():
        use_family = split != "F"
        for train_sets, test_sets, fold in jobs:
            if fold is not None:  # split P: 5-fold by problem within one set
                S = SETS_DATA[train_sets[0]]
                tr, te = list(GroupKFold(n_splits=5).split(S["X"], groups=S["group"]))[fold]
                tr_parts, te_parts = [(train_sets[0], tr)], [(train_sets[0], te)]
            else:
                tr_parts = [(s, np.arange(len(SETS_DATA[s]["X"]))) for s in train_sets]
                te_parts = [(s, np.arange(len(SETS_DATA[s]["X"]))) for s in test_sets]
            for target in ("T1", "T2"):
                for model in ("G1", "G2", "S2"):
                    if model == "S2":
                        conf_col = len(STRUCT_NAMES) + OUTPUT_NAMES.index("confidence")
                        Xtr = np.concatenate([SETS_DATA[s]["X"][i][:, [conf_col]] for s, i in tr_parts])
                        ytr = np.concatenate([SETS_DATA[s][target][i] for s, i in tr_parts])
                        m = ConfidenceBaseline()
                        m.fit(Xtr, ytr)
                        for s, i in te_parts:
                            p = m.predict(SETS_DATA[s]["X"][i][:, [conf_col]])
                            preds.setdefault((split, s), {}).setdefault(model, {}).setdefault(target, {}).update(dict(zip(i, p)))
                        continue
                    Xtr = np.concatenate([design(SETS_DATA[s], i, model, use_family)[0] for s, i in tr_parts])
                    ytr = np.concatenate([SETS_DATA[s][target][i] for s, i in tr_parts])
                    gtr = np.concatenate([SETS_DATA[s]["group"][i] for s, i in tr_parts])
                    m, best = fit_gbt(Xtr, ytr, gtr)
                    chosen.append({"split": split, "train": "+".join(train_sets), "test": "+".join(test_sets),
                                   "fold": fold, "target": target, "model": model, **best})
                    for s, i in te_parts:
                        p = m.predict(design(SETS_DATA[s], i, model, use_family)[0])
                        preds.setdefault((split, s), {}).setdefault(model, {}).setdefault(target, {}).update(dict(zip(i, p)))
            log(f"  {split}: trained on {'+'.join(train_sets)}{'' if fold is None else f' fold {fold}'} -> tested on {'+'.join(test_sets)}")
    # rule baselines (no training): constant per node
    for (split, s), d in preds.items():
        L, S = LS[s], SETS_DATA[s]
        for model, score in (("S0", {n: L.reach[n] for n in L.llm}),
                             ("S1", {n: -L.dist[n] + 1e-3 * L.topo.index(n) for n in L.llm})):
            v = np.array([score[n] for n in S["node"]])
            d[model] = {"T1": dict(enumerate(v)), "T2": dict(enumerate(v))}
    return preds, chosen


def decision(L, ranking, k):
    """Own top-k plan and shortlist test for one ranking."""
    own = ranking[:k]
    alt = ranking[:k - 1] + [ranking[k]] if len(ranking) > k else None
    short = {key(own)} | ({key(alt)} if alt else set())
    rules = {key(L.struct_order[:k]), key(L.output_order[:k])}
    return own, short, rules


def check(L, k, cands):
    uni = L.universe[k]
    best_acc = max(uni.values())
    best = sorted(s for s, a in uni.items() if a == best_acc)
    checkable = [c for c in cands if c in L.valid_acc]
    if not checkable:
        return best, best_acc, None, None, sorted(cands)
    pick = sorted(checkable, key=lambda c: (-L.valid_acc[c], c))[0]
    return best, best_acc, pick, best_acc - L.eval_acc[pick], sorted(c for c in cands if c not in L.valid_acc)


def cmd_a2(_):
    from sklearn.metrics import roc_auc_score
    OUT.mkdir(parents=True, exist_ok=True)
    LS = {s: LabelSet(s) for s in TRAIN_SETS}
    SD = {s: build_samples(LS[s]) for s in TRAIN_SETS}
    log("samples: " + ", ".join(f"{s} {len(SD[s]['X'])}" for s in TRAIN_SETS) + f" (total {sum(len(SD[s]['X']) for s in TRAIN_SETS)})")
    preds, chosen = run_predictions(SD, LS)
    sample_rows, node_rows, dec_rows = [], [], []
    for (split, s), d in sorted(preds.items()):
        L, S = LS[s], SD[s]
        meas = {t: node_level(L, S["node"], S[t]) for t in ("T1", "T2")}
        for model, bt in d.items():
            for target, pm in bt.items():
                p = np.array([pm[i] for i in range(len(S["X"]))])
                y = S[target]
                try:
                    auc = float(roc_auc_score(y > 0, p)) if 0 < (y > 0).sum() < len(y) else float("nan")
                except ValueError:
                    auc = float("nan")
                sample_rows.append({"split": split, "test": s, "model": model, "target": target,
                                    "spearman": spearman(p, y), "auroc": auc})
                pn = node_level(L, S["node"], p)
                rp, rm = L.rank(pn), L.rank(meas[target])
                node_rows.append({"split": split, "test": s, "model": model, "target": target,
                                  "top1_match": float(rp[0] == rm[0]), "top2_match": float(set(rp[:2]) == set(rm[:2])),
                                  "spearman": spearman([pn[n] for n in L.llm], [meas[target][n] for n in L.llm]),
                                  "pred_ranking": " > ".join(rp), "measured_ranking": " > ".join(rm)})
                if not L.universe:
                    continue
                for k in (1, 2, 3):
                    own, short, rules = decision(L, rp, k)
                    a, measured = L.plan_eval(own)
                    best, best_acc, pick, sf, unc = check(L, k, short | rules)
                    dec_rows.append({"split": split, "test": s, "model": model, "target": target, "k": k,
                                     "own_plan": key(own), "own_eval_acc": a, "own_measured": measured,
                                     "shortlist": " | ".join(sorted(short | rules)), "best": " / ".join(best),
                                     "best_eval_acc": best_acc, "contains_best": any(b in short | rules for b in best),
                                     "check_pick": pick, "check_shortfall": sf, "unchecked": " | ".join(unc)})
    # references from real labels (no split)
    ref_rows = []
    for s in TRAIN_SETS:
        L = LS[s]
        if not L.universe:
            continue
        full = L.node_scores()
        for k in (1, 2, 3):
            for name, cands in (("labels (EC + upgrade value) + rules",
                                 {key(L.rank(full["EC"])[:k]), key(L.rank(full["UV"])[:k]), key(L.struct_order[:k]), key(L.output_order[:k])}),
                                ("rules only (structure + closest-to-answer)", {key(L.struct_order[:k]), key(L.output_order[:k])})):
                best, best_acc, pick, sf, unc = check(L, k, cands)
                ref_rows.append({"test": s, "k": k, "reference": name, "shortlist": " | ".join(sorted(cands)),
                                 "contains_best": any(b in cands for b in best), "check_pick": pick, "check_shortfall": sf,
                                 "unchecked": " | ".join(unc)})
    for name, rows in (("a2_sample_metrics", sample_rows), ("a2_node_metrics", node_rows), ("a2_decision", dec_rows),
                       ("a2_reference_shortlists", ref_rows), ("a2_chosen_hyperparameters", chosen)):
        with open(OUT / f"{name}.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    report_a2(sample_rows, node_rows, dec_rows, ref_rows)


def _mean(rows, field, **kw):
    v = [r[field] for r in rows if all(r[k] == x for k, x in kw.items()) and r[field] is not None and r[field] == r[field]]
    return float(np.mean(v)) if v else float("nan")


def report_a2(sample_rows, node_rows, dec_rows, ref_rows):
    models = ["S0", "S1", "S2", "G1", "G2"]
    for target in ("T1", "T2"):
        log(f"\n=== {target} ({'consequence' if target == 'T1' else 'upgrade value'}): means over test sets")
        log(f"  {'split':<6}{'model':<6}{'sample rho':>11}{'AUROC':>8}{'node top1':>10}{'node top2':>10}{'node rho':>9}")
        for split in ("P", "C", "W", "F"):
            for m in models:
                log(f"  {split:<6}{m:<6}{_mean(sample_rows, 'spearman', split=split, model=m, target=target):>11.3f}"
                    f"{_mean(sample_rows, 'auroc', split=split, model=m, target=target):>8.3f}"
                    f"{_mean(node_rows, 'top1_match', split=split, model=m, target=target):>10.2f}"
                    f"{_mean(node_rows, 'top2_match', split=split, model=m, target=target):>10.2f}"
                    f"{_mean(node_rows, 'spearman', split=split, model=m, target=target):>9.3f}")
    log("\n=== decision value (ranking from the T2-trained model; test sets L2-L5, L7; k = 1, 2, 3)")
    log(f"  {'split':<6}{'model':<6}{'own plan acc':>13}{'contains best':>15}{'mean shortfall':>16}{'max shortfall':>15}")
    for split in ("P", "C", "W", "F"):
        for m in models:
            rs = [r for r in dec_rows if r["split"] == split and r["model"] == m and r["target"] == "T2"]
            if split == "P":  # five folds per set: one row per (set, k) per fold; summarise all
                pass
            sf = [r["check_shortfall"] for r in rs if r["check_shortfall"] is not None]
            log(f"  {split:<6}{m:<6}{np.mean([r['own_eval_acc'] for r in rs if r['own_eval_acc'] is not None]):>13.3f}"
                f"{np.mean([r['contains_best'] for r in rs]):>15.2f}{np.mean(sf):>16.3f}{max(sf):>15.3f}")
    for name in ("labels (EC + upgrade value) + rules", "rules only (structure + closest-to-answer)"):
        rs = [r for r in ref_rows if r["reference"] == name]
        sf = [r["check_shortfall"] for r in rs if r["check_shortfall"] is not None]
        log(f"  reference: {name}: contains best {np.mean([r['contains_best'] for r in rs]):.2f}, "
            f"mean shortfall {np.mean(sf):.3f}, max {max(sf):.3f}")
    log("\n=== split C, G2 (T2): per test set and budget")
    for r in [r for r in dec_rows if r["split"] == "C" and r["model"] == "G2" and r["target"] == "T2"]:
        log(f"  {r['test']} k={r['k']}: own {r['own_plan']} ({r['own_eval_acc']}{'' if r['own_measured'] else ', est.'}); "
            f"best {r['best']} {r['best_eval_acc']:.3f}; contains best {r['contains_best']}; pick {r['check_pick']}; "
            f"shortfall {r['check_shortfall']}" + (f"; unchecked {r['unchecked']}" if r['unchecked'] else ""))
    # predictions
    log("\nPredictions:")
    c2 = [r for r in dec_rows if r["split"] == "C" and r["model"] == "G2" and r["target"] == "T2"]
    share = np.mean([r["contains_best"] for r in c2])
    log(f"  P-A2-1 C, G2 shortlist+rules contains best in >= 80% of {len(c2)} cases: {share:.3f} -> {'HELD' if share >= 0.8 else 'FAILED'}")
    sfs = [r["check_shortfall"] for r in c2]
    mx = max(x for x in sfs if x is not None) if any(x is not None for x in sfs) else float("nan")
    ok2 = all(x is not None and x <= 0.06 + 1e-9 for x in sfs)
    log(f"  P-A2-2 C, G2 check shortfall never > 0.06: max {mx:.3f}{'' if all(x is not None for x in sfs) else ' (some cases uncheckable)'} -> {'HELD' if ok2 else 'FAILED'}")
    t1c = {t: _mean(node_rows, "top1_match", split="C", model="G2", target=t) for t in ("T1", "T2")}
    t1f = {t: _mean(node_rows, "top1_match", split="F", model="G2", target=t) for t in ("T1", "T2")}
    log(f"  P-A2-3 G2 node top-1 rate F < C for both targets: C {t1c}, F {t1f} -> {'HELD' if all(t1f[t] < t1c[t] for t in t1c) else 'FAILED'}")
    diffs = [r2["spearman"] - r1["spearman"] for r1 in node_rows for r2 in node_rows
             if r1["split"] == r2["split"] == "C" and r1["model"] == "G1" and r2["model"] == "G2"
             and r1["test"] == r2["test"] and r1["target"] == r2["target"]]
    log(f"  P-A2-4 mean node rho (G2 - G1) under C > 0: {np.mean(diffs):+.3f} over {len(diffs)} (set, target) pairs -> {'HELD' if np.mean(diffs) > 0 else 'FAILED'}")
    s1 = {t: _mean([r for r in node_rows if r["split"] == "C"], "spearman", model="S1", target=t) for t in ("T1", "T2")}
    log(f"  P-A2-5 S1 node rho with T1 > with T2 (L1-L5, L7): T1 {s1['T1']:+.3f}, T2 {s1['T2']:+.3f} -> {'HELD' if s1['T1'] > s1['T2'] else 'FAILED'}")


# ------------------------------------------------------------------ A3
def cmd_a3(_):
    OUT.mkdir(parents=True, exist_ok=True)
    LS = {s: LabelSet(s) for s in TRAIN_SETS}
    SD = {s: build_samples(LS[s]) for s in TRAIN_SETS}
    imp_rows = []
    rng = np.random.default_rng(0)
    for split in ("C", "F"):
        use_family = split != "F"
        for train_sets, test_sets, _ in split_defs()[split]:
            for target in ("T1", "T2"):
                Xtr = np.concatenate([design(SD[s], np.arange(len(SD[s]["X"])), "G2", use_family)[0] for s in train_sets])
                ytr = np.concatenate([SD[s][target] for s in train_sets])
                gtr = np.concatenate([SD[s]["group"] for s in train_sets])
                m, _best = fit_gbt(Xtr, ytr, gtr)
                for s in test_sets:
                    L, S = LS[s], SD[s]
                    Xte, names = design(S, np.arange(len(S["X"])), "G2", use_family)
                    meas = node_level(L, S["node"], S[target])

                    def node_rho(X):
                        pn = node_level(L, S["node"], m.predict(X))
                        return spearman([pn[n] for n in L.llm], [meas[n] for n in L.llm])
                    base = node_rho(Xte)
                    for j, nm in enumerate(names):
                        drops = []
                        for _ in range(20):
                            Xp = Xte.copy()
                            Xp[:, j] = rng.permutation(Xp[:, j])
                            drops.append(base - node_rho(Xp))
                        imp_rows.append({"split": split, "test": s, "target": target, "feature": nm,
                                         "importance": float(np.mean(drops)), "base_node_rho": base})
    with open(OUT / "a3_permutation_importance.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(imp_rows[0]))
        w.writeheader()
        w.writerows(imp_rows)
    for split in ("C", "F"):
        for target in ("T1", "T2"):
            feats = sorted({r["feature"] for r in imp_rows if r["split"] == split})
            mean = {f: _mean(imp_rows, "importance", split=split, target=target, feature=f) for f in feats}
            top = sorted(mean.items(), key=lambda kv: -kv[1])[:8]
            log(f"\n=== permutation importance (drop in node-level rho), G2, split {split}, {target}")
            for f, v in top:
                log(f"  {f:<24}{v:+.3f}")
    # failures: G2 (T2) shortlist missed the best plan under C or F
    dec = list(csv.DictReader(open(OUT / "a2_decision.csv")))
    log("\n=== shortlist misses, G2 trained on T2, splits C and F")
    for r in dec:
        if r["model"] != "G2" or r["target"] != "T2" or r["split"] not in ("C", "F") or r["contains_best"] == "True":
            continue
        L, S = LS[r["test"]], SD[r["test"]]
        nodes = sorted({x for part in (r["best"].split(" / ")[0].split(","), r["own_plan"].split(",")) for x in part})
        meas = node_level(L, S["node"], S["T2"])
        log(f"  [{r['split']}] {r['test']} k={r['k']}: best {r['best']} ({float(r['best_eval_acc']):.3f}); G2 top-k {r['own_plan']}; "
            f"shortlist {r['shortlist']}; check pick {r['check_pick'] or '-'}; shortfall {r['check_shortfall'] or 'n/a'}")
        for n in nodes:
            sel = S["node"] == n
            log(f"      {n:<14} measured UV {meas[n]:+.3f}  p_err {S['perr'][sel].mean():.2f}  conf {S['X'][sel, len(STRUCT_NAMES) + 2].mean():.3f}"
                f"  tokens {S['X'][sel, len(STRUCT_NAMES)].mean():.0f}  copies_parent {S['X'][sel, len(STRUCT_NAMES) + 3].mean():.2f}"
                f"  dist {L.dist[n]}  reach {L.reach[n]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("a1").set_defaults(f=cmd_a1)
    sub.add_parser("a2").set_defaults(f=cmd_a2)
    sub.add_parser("a3").set_defaults(f=cmd_a3)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
