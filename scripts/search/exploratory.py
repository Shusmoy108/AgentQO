#!/usr/bin/env python3
"""EXPLORATORY analyses, NOT registered (docs/search_prereg.md is unchanged by this script).

    python3 scripts/search/exploratory.py [--seeds 30] [--workers 9]

1. Strict hypervolume: reference accuracy = the all_small plan's accuracy (area above "do nothing"), plus IGD
   and regret at p25/p50/p75 cost, budgets 1-20%, on complex_q15_7 and math_tiers, every 2-objective method.
2. Variant: pairwise_corrected with pair plans capped at 25% of B (m 3 and m 5) on the 32/64-plan spaces.
3. Budget accounting: effective B per %, and how many plans the pairwise surrogates spend on pair plans.
4. S4 diagnostics: how the joint search spends its budget (distinct plans, both placements of one plan).
Outputs: results/search/exploratory/*.csv, EXPLORATORY.md, figures/fronts_3obj.png.
"""

from __future__ import annotations

import argparse
import os
import sys
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agentqo.search.ground_truth import PLACEMENTS, SETTINGS, hv2, hv3, latsim_predictions, load_setting, pareto_mask  # noqa: E402
from agentqo.search.metrics import true_hv3  # noqa: E402
from agentqo.search.methods import METHODS_2D, METHODS_3D, METHODS_EXPLORATORY, run_s4_plans_only  # noqa: E402
from agentqo.search.metrics import BUDGET_FRACS, budget_for, metrics_2d  # noqa: E402
from agentqo.search.surrogates import adaptive_pairs, label_terms, make_surrogate, max_pairs  # noqa: E402
from scripts.search.summarize import TAU, ci  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "search" / "exploratory"
FIG = ROOT / "results" / "search" / "figures"
LARGE = ["complex_q15_7", "math_tiers"]


def strict_hv(s, rows):
    """HV with reference (cost 1, accuracy = all_small accuracy); plans below all_small add nothing."""
    base = s.acc[s.row(np.zeros(s.n, dtype=int))]
    rows = list(rows)
    return hv2(np.maximum(s.acc[rows] - base, 0), s.cost[rows], s.cost.max())


def job_strict(args):
    name, seeds = args
    s = load_setting(name, with_latency=False)
    t = label_terms(s)
    full = strict_hv(s, range(s.size))
    out = []
    for frac in BUDGET_FRACS:
        b = budget_for(s.size, frac)
        for seed in seeds:
            for m, fn in METHODS_2D.items():
                V = fn(s, b, np.random.default_rng(seed), terms=t)
                out.append({"setting": name, "method": m, "budget_frac": frac, "budget": b, "seed": seed,
                            "strict_hv_ratio": strict_hv(s, V.rows) / full, **metrics_2d(s, V.rows)})
    return out


def job_adapt(args):
    name, seeds = args
    s = load_setting(name, with_latency=False)
    t = label_terms(s)
    out = []
    for frac in BUDGET_FRACS:
        b = budget_for(s.size, frac)
        for seed in seeds:
            for m, fn in METHODS_EXPLORATORY.items():
                V = fn(s, b, np.random.default_rng(seed), terms=t)
                out.append({"setting": name, "method": m, "budget_frac": frac, "budget": b, "seed": seed,
                            "pair_plans": len(V.surrogate.verified) - 1, **metrics_2d(s, V.rows, V.surrogate)})
    return out


def job_s4(args):
    name, seeds = args
    s = load_setting(name)
    t = label_terms(s)
    out = []
    for frac in BUDGET_FRACS:
        b = budget_for(s.size, frac)
        for seed in seeds:
            for m in ("joint_nsga2_pairwise_m3", "plan_first_nsga2_pairwise_m3"):
                V = METHODS_3D[m](s, b, np.random.default_rng(seed), terms=t)
                rows = [r for r, _ in V.items]
                out.append({"setting": name, "method": m, "budget_frac": frac, "budget": b, "seed": seed,
                            "verified": len(V.items), "distinct_plans": len(set(rows)),
                            "plans_at_both_placements": len(rows) - len(set(rows)),
                            "share_shared": float(np.mean([p == 1 for _, p in V.items])),
                            "hv2_acc_cost_of_plans": hv2(s.acc[rows], s.cost[rows], s.cost.max())})
    return out


def job_s4_redesign(args):
    """Budget = plans; each verified plan scored at both placements. hv3 with true latency (X1 measured where
    timed, else latsim) and, separately, with latsim predictions everywhere."""
    name, seeds = args
    s = load_setting(name)
    t = label_terms(s)
    pred = latsim_predictions()
    lat_pred = np.r_[[pred[(name, n, "separate")] for n in s.names], [pred[(name, n, "shared")] for n in s.names]]
    acc2, cost2 = np.r_[s.acc, s.acc], np.r_[s.cost, s.cost]
    lat_true = np.r_[s.latency["separate"], s.latency["shared"]]
    full_true, full_pred = true_hv3(s), hv3(acc2, cost2, lat_pred, cost2.max(), lat_pred.max())
    out = []
    for frac in BUDGET_FRACS:
        b = budget_for(s.size, frac)
        for seed in seeds:
            for mode in ("joint", "plan_first"):
                rows = run_s4_plans_only(s, b, np.random.default_rng(seed), mode, terms=t)
                idx = np.r_[rows, np.array(rows) + s.size]
                out.append({"setting": name, "method": mode, "budget_frac": frac, "budget": b, "seed": seed,
                            "plans_verified": len(rows),
                            "hv3_ratio_true_latency": hv3(acc2[idx], cost2[idx], lat_true[idx], cost2.max(), lat_true.max()) / full_true,
                            "hv3_ratio_pred_latency": hv3(acc2[idx], cost2[idx], lat_pred[idx], cost2.max(), lat_pred.max()) / full_pred})
    return out


def wtl_cells(d, metric, a, b, keys=("setting", "budget_frac")):
    res, diffs = [], []
    for _, g in d.groupby(list(keys)):
        x = g[g.method == a].set_index("seed")[metric]; y = g[g.method == b].set_index("seed")[metric]
        dd = (x - y).dropna(); lo, hi = ci(dd)
        res.append("W" if dd.mean() > TAU and lo > 0 else "L" if dd.mean() < -TAU and hi < 0 else "T")
        diffs.append(dd.mean())
    return res.count("W"), res.count("T"), res.count("L"), float(np.mean(diffs))


def md_table(df):
    cols = list(df.columns)
    return "\n".join(["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
                     + ["| " + " | ".join(f"{v:.3f}" if isinstance(v, float) else str(v) for v in r) + " |"
                        for r in df.itertuples(index=False)])


def pair_table():
    rows = []
    for name in SETTINGS:
        s = load_setting(name, with_latency=False)
        t = label_terms(s)
        for frac in BUDGET_FRACS:
            b = budget_for(s.size, frac)
            r = {"setting": name, "n_plans": s.size, "budget_pct": int(frac * 100), "B": b}
            for m in (3, 5):
                for cap_name, cap in (("registered", max_pairs), ("adapt25", adaptive_pairs)):
                    sur = make_surrogate(f"pairwise_corrected_m{m}", s, b, t, pair_cap=cap)
                    r[f"pairs_m{m}_{cap_name}"] = len(sur.verified) - 1
            rows.append(r)
    return pd.DataFrame(rows)


def fronts_3obj():
    """Verified (plan, placement) sets, seed 0, 10% budget: cost vs accuracy, colour = p95 latency."""
    names = ["math_q15_7", "math_tiers"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    for row, name in enumerate(names):
        s = load_setting(name)
        t = label_terms(s)
        b = budget_for(s.size, 0.10)
        lat = np.r_[s.latency["separate"], s.latency["shared"]]
        vmin, vmax = np.quantile(lat, [0.02, 0.98])
        for col, m in enumerate(("joint_nsga2_pairwise_m3", "plan_first_nsga2_pairwise_m3")):
            ax = axes[row, col]
            V = METHODS_3D[m](s, b, np.random.default_rng(0), terms=t)
            c = s.cost / s.cost.max()
            ax.scatter(c, s.acc, s=6, color="#d6d5cf", label="all plans")
            r = np.array([i for i, _ in V.items]); p = np.array([q for _, q in V.items])
            L = np.array([s.latency[PLACEMENTS[q]][i] for i, q in V.items])
            front = pareto_mask(np.c_[s.cost[r], L, -s.acc[r]])
            for q, mk in ((0, "o"), (1, "s")):
                sel = p == q
                sc = ax.scatter(c[r][sel], s.acc[r][sel], c=L[sel], cmap="viridis", vmin=vmin, vmax=vmax, marker=mk,
                                s=np.where(front[sel], 60, 22), edgecolors=np.where(front[sel], "#111", "none"),
                                linewidths=0.8, label=f"verified, {PLACEMENTS[q]}")
            ax.set_title(f"{name}: {m} (registered S4 setup)\nB={b} (10%), seed 0; outlined = 3-objective front", fontsize=8)
            ax.set_xlabel("API cost / max plan cost"); ax.set_ylabel("accuracy"); ax.grid(alpha=0.2)
            ax.legend(fontsize=7, loc="lower right")
        fig.colorbar(sc, ax=axes[row, :].tolist(), label="p95 latency (s), K=16")
    fig.savefig(FIG / "fronts_3obj.png", dpi=130, bbox_inches="tight"); plt.close(fig)


def summ(d, keys, cols):
    g = d.groupby(keys)
    out = g[cols].mean().add_suffix("_mean")
    for c in cols:
        lohi = g[c].apply(lambda x: ci(x))
        out[f"{c}_ci_low"] = [x[0] for x in lohi]; out[f"{c}_ci_high"] = [x[1] for x in lohi]
    return out.reset_index()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--workers", type=int, default=9)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    chunks = [list(range(k, min(k + 5, a.seeds))) for k in range(0, a.seeds, 5)]
    small = [n for n in SETTINGS if load_setting(n, with_latency=False).size <= 64]
    with Pool(a.workers) as pool:
        st = pd.DataFrame([r for rs in pool.map(job_strict, [(n, c) for n in LARGE for c in chunks]) for r in rs])
        ad = pd.DataFrame([r for rs in pool.map(job_adapt, [(n, c) for n in small for c in chunks]) for r in rs])
        s4 = pd.DataFrame([r for rs in pool.map(job_s4, [(n, c) for n in SETTINGS for c in chunks]) for r in rs])
        s4r = pd.DataFrame([r for rs in pool.map(job_s4_redesign, [(n, c) for n in SETTINGS for c in chunks]) for r in rs])
    s4r.to_csv(OUT / "s4_redesign_plans_only.csv", index=False)
    st.to_csv(OUT / "strict_hv_large.csv", index=False)
    ad.to_csv(OUT / "adaptive_pairs_small.csv", index=False)
    s4.to_csv(OUT / "s4_budget_use.csv", index=False)
    pt = pair_table(); pt.to_csv(OUT / "pair_plan_budget.csv", index=False)
    fronts_3obj()

    md = ["# EXPLORATORY analyses (not registered)", "",
          "Everything in this file is exploratory and NOT part of the registered analysis (docs/search_prereg.md,",
          "results/search/hypotheses_search.md are unchanged). Generated by scripts/search/exploratory.py; 30 seeds,",
          "mean [95% CI].", ""]
    # 3. budget accounting
    md += ["## Effective budget and pair plans", "",
           "B = max(4, round(% x plans)). On the 32- and 64-plan spaces the 1%, 2% and 5% budgets are all the 4-plan",
           "minimum, so those three columns are the same experiment. pairwise_corrected spends 1 plan on all_small plus",
           "the pair plans below (registered cap floor(B/2) - 1; adapt25 = exploratory cap floor(0.25 B)); m 3 has at",
           "most 3 pairs, m 5 at most 10 (fewer when two of the top options are the same agent, math_tiers).", "",
           "| setting | plans | 1% | 2% | 5% | 10% | 20% |", "|---|---|---|---|---|---|---|"]
    for name, g in pt.groupby("setting", sort=False):
        g = g.sort_values("budget_pct")
        md.append(f"| {name} | {g.n_plans.iloc[0]} | " + " | ".join(
            f"B={r.B}: m3 {r.pairs_m3_registered}/{r.pairs_m3_adapt25}, m5 {r.pairs_m5_registered}/{r.pairs_m5_adapt25}"
            for r in g.itertuples()) + " |")
    md += ["", "Cells: pair plans registered/adapt25. Add 1 (all_small) for the surrogate's total verified plans.", ""]

    # 1. strict HV on large spaces
    ss = summ(st, ["setting", "method", "budget_frac", "budget"],
              ["strict_hv_ratio", "hv_ratio", "igd", "regret_p25", "regret_p50", "regret_p75"])
    ss.to_csv(OUT / "strict_hv_large_summary.csv", index=False)
    md += ["## Strict hypervolume, IGD and regret on the >= 256-plan spaces (exploratory, not registered)", "",
           "Strict HV: reference accuracy = all_small's accuracy (only the area above 'do nothing' counts), cost",
           "reference 1 as registered. IGD in (cost / max cost, accuracy). Regret = best true accuracy at cost <= the",
           "p25/p50/p75 plan cost minus the best verified one (accuracy points; X4 tie level 0.0375).", ""]
    for name in LARGE:
        for metric, lab in (("strict_hv_ratio", "strict HV ratio"), ("igd", "IGD (lower better)"),
                            ("regret_p25", "regret @p25 cost"), ("regret_p50", "regret @p50 cost"),
                            ("regret_p75", "regret @p75 cost")):
            g = ss[ss.setting == name]
            bud = g.drop_duplicates("budget_frac").sort_values("budget_frac")
            md += [f"### {name}: {lab}", "", "| method | " + " | ".join(
                f"{int(r.budget_frac*100)}% (B={r.budget})" for r in bud.itertuples()) + " |",
                   "|---|" + "---|" * len(bud)]
            for m in METHODS_2D:
                h = g[g.method == m].sort_values("budget_frac")
                md.append(f"| {m} | " + " | ".join(
                    f"{v:.3f}" if abs(hi - lo) < 5e-4 else f"{v:.3f} [{lo:.3f}, {hi:.3f}]"
                    for v, lo, hi in zip(h[f"{metric}_mean"], h[f"{metric}_ci_low"], h[f"{metric}_ci_high"])) + " |")
            md.append("")

    # 2. adaptive pair cap
    reg = pd.read_csv(ROOT / "results" / "search" / "results.csv")
    reg = reg[(reg.objectives == "acc_cost") & reg.setting.isin(small)
              & reg.method.isin(["nsga2_pairwise_m3", "nsga2_pairwise_m5", "nsga2_indep_add"])]
    both = pd.concat([reg[["setting", "method", "budget_frac", "budget", "seed", "hv_ratio"]],
                      ad[["setting", "method", "budget_frac", "budget", "seed", "hv_ratio"]]])
    piv = both.groupby(["method", "budget_frac"]).hv_ratio.mean().unstack()
    md += ["## Variant: pair plans capped at 25% of B, 32/64-plan spaces (exploratory, not registered)", "",
           "Registered HV ratio definition; mean over the 9 small settings x 30 seeds. Registered rows copied from",
           "results.csv for comparison (same seeds). On these spaces the cap only changes B = 6/7 (1 pair instead of 2)",
           "and, for m 5, B = 13 (3 instead of 5); at B = 4 both caps allow 1 pair.", "",
           "| method | " + " | ".join(f"{int(f*100)}%" for f in piv.columns) + " | all |", "|---|" + "---|" * (len(piv.columns) + 1)]
    for m in ["nsga2_pairwise_m3", "nsga2_pairwise_m3_adapt25", "nsga2_pairwise_m5", "nsga2_pairwise_m5_adapt25", "nsga2_indep_add"]:
        md.append(f"| {m} | " + " | ".join(f"{v:.4f}" for v in piv.loc[m]) + f" | {both[both.method == m].hv_ratio.mean():.4f} |")
    md += ["", "Paired, adapt25 minus registered (same m), per setting x budget cell, tie threshold tau = 0.0134:", ""]
    for m in (3, 5):
        x = ad[ad.method == f"nsga2_pairwise_m{m}_adapt25"].set_index(["setting", "budget_frac", "seed"]).hv_ratio
        y = reg[reg.method == f"nsga2_pairwise_m{m}"].set_index(["setting", "budget_frac", "seed"]).hv_ratio
        dd = (x - y).dropna().groupby(level=[0, 1])
        res = [("W" if d.mean() > TAU and ci(d)[0] > 0 else "L" if d.mean() < -TAU and ci(d)[1] < 0 else "T") for _, d in dd]
        md.append(f"- m {m}: W/T/L {res.count('W')}/{res.count('T')}/{res.count('L')} of {len(res)} cells, mean diff {(x - y).mean():+.4f}")
    md.append("")

    # 4. S4 diagnostics
    g4 = s4.groupby(["method", "budget_frac"])[["verified", "distinct_plans", "plans_at_both_placements", "share_shared",
                                                 "hv2_acc_cost_of_plans"]].mean().round(3)
    md += ["## S4 diagnostics: how the 3-objective searches spend the budget (exploratory)", "",
           "Means over 11 settings x 30 seeds. hv2_acc_cost_of_plans = registered 2-objective HV of the distinct plans",
           "verified (ignores latency).", "", md_table(g4.reset_index()), "",
           "Figure: results/search/figures/fronts_3obj.png (verified sets at 10%, seed 0, math_q15_7 measured latency and",
           "math_tiers mostly predicted latency).", ""]
    # S4 redesign
    md += ["## S4 redesign: budget counts plans, both placements free from latsim (exploratory, not registered)", "",
           "Accuracy and API cost do not depend on placement, so only plans are verified (B plans); each verified plan",
           "is scored at both placements with the latsim frozen p95 (no budget cost). Joint = 3-objective NSGA-II over",
           "plan + placement gene, verifying distinct plans in its surrogate order; plan-first = registered 2-objective",
           "search. HV3 evaluated with the true latency (X1 measured where timed, else latsim) and with latsim everywhere.",
           f"Paired W/T/L over 55 cells (joint minus plan-first), tau = {TAU}:", ""]
    for metric in ("hv3_ratio_true_latency", "hv3_ratio_pred_latency"):
        w, tt, l, md_ = wtl_cells(s4r.rename(columns={}), metric, "joint", "plan_first")
        md.append(f"- {metric}: W/T/L {w}/{tt}/{l}, mean diff {md_:+.4f}")
    g = s4r.groupby(["method", "budget_frac"])[["hv3_ratio_true_latency", "hv3_ratio_pred_latency"]].mean().unstack(0).round(4)
    g.columns = [f"{a} ({b})" for a, b in g.columns]
    md += ["", md_table(g.reset_index()), ""]
    big4 = s4r[s4r.setting.isin(LARGE)]
    for metric in ("hv3_ratio_true_latency",):
        w, tt, l, md_ = wtl_cells(big4, metric, "joint", "plan_first")
        md.append(f"- >= 256-plan settings only, {metric}: W/T/L {w}/{tt}/{l}, mean diff {md_:+.4f}")
    md.append("")

    # active learning on the real settings (registered exploratory variant nsga2_active_m3, from results.csv)
    r2 = pd.read_csv(ROOT / "results" / "search" / "results.csv")
    r2 = r2[r2.objectives == "acc_cost"]
    md += ["## Active learning on the real settings (registered exploratory variant nsga2_active_m3)", "",
           "NSGA-II + pairwise m 3, verifying in 4 rounds and re-fitting a ridge model of pair residuals on every plan",
           "verified so far. Rows from results.csv (registered run). Paired W/T/L over 55 cells, tau = 0.0134:", "",
           "| comparison | W | T | L | mean diff | >= 256-plan cells W/T/L |", "|---|---|---|---|---|---|"]
    for other in ("nsga2_pairwise_m3", "nsga2_indep_add", "abacus", "greedy_uv", "random"):
        w, tt, l, md_ = wtl_cells(r2, "hv_ratio", "nsga2_active_m3", other)
        wb, tb, lb, _ = wtl_cells(r2[r2.setting.isin(LARGE)], "hv_ratio", "nsga2_active_m3", other)
        md.append(f"| active vs {other} | {w} | {tt} | {l} | {md_:+.4f} | {wb}/{tb}/{lb} |")
    piv = r2[r2.method.isin(["nsga2_active_m3", "nsga2_pairwise_m3", "abacus"]) & r2.setting.isin(LARGE)] \
        .groupby(["setting", "method", "budget_frac"]).hv_ratio.mean().unstack().round(3)
    md += ["", "HV ratio on the >= 256-plan settings by budget:", "", md_table(piv.reset_index()), ""]

    (OUT / "EXPLORATORY.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
