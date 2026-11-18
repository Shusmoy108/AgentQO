#!/usr/bin/env python3
"""Settings that landed after the registered run (X5 MATH-500, ...): same methods, budgets, seeds and metrics.

    python3 scripts/search/run_search.py --settings math500_q15_7 --out results/search/new_settings/results.csv
    python3 scripts/search/new_settings.py
Writes results/search/new_settings/NEW_SETTINGS.md. The registered S1-S4 verdicts stay on the 11 original settings;
this reports the same S2 comparisons and the S3 quantities on each new setting, plus S3's rho recomputed with them
(supplementary).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agentqo.search.methods import METHODS_2D  # noqa: E402
from scripts.search.summarize import COMPARATORS, MAIN, OUT, paired, wtl  # noqa: E402

NEW = OUT / "new_settings"


def indep_mae(name):
    from agentqo.search.ground_truth import load_setting
    st = load_setting(name, with_latency=False)
    z = np.zeros(st.n, dtype=int)
    b = st.acc[st.row(z)]
    single = np.zeros((st.n, len(st.tiers)))
    for i in range(st.n):
        for t in range(1, len(st.tiers)):
            g = z.copy(); g[i] = t
            single[i, t] = st.acc[st.row(g)] - b
    est = np.clip(b + single[np.arange(st.n), st.genomes].sum(1), 0, 1)
    return np.abs(est - st.acc).mean()


def main():
    d = pd.read_csv(NEW / "results.csv")
    d = d[d.objectives == "acc_cost"]
    md = ["## New settings (landed after the registered run; not part of the S1-S4 verdicts)", "",
          "Same 14 methods, 5 budgets, 30 seeds and metrics as the registered run. 2 objectives only (no latency truth).", ""]
    s3 = pd.read_csv(OUT / "s3_interaction_vs_gap.csv")
    for s, g in d.groupby("setting"):
        fr = sorted(g.budget_frac.unique())
        bs = [int(g[g.budget_frac == f].budget.iloc[0]) for f in fr]
        md += [f"### {s} ({int(g.n_plans.iloc[0])} plans)", "",
               "Mean HV ratio over 30 seeds; B = " + "/".join(map(str, bs)) + " (1/2/5/10/20%; equal B values repeat one",
               "experiment, so a W or L there counts more than once).", "",
               "| method | " + " | ".join(f"{int(f*100)}%" for f in fr) + " |", "|---|" + "---|" * len(fr)]
        piv = g.groupby(["method", "budget_frac"]).hv_ratio.mean().unstack()
        md += [f"| {m} | " + " | ".join(f"{piv.loc[m, f]:.3f}" for f in fr) + " |" for m in METHODS_2D]
        md += ["", f"S2 comparisons ({MAIN} minus comparator, paired per budget, tau = 0.0134):", "",
               "| comparator | W | T | L | per budget |", "|---|---|---|---|---|"]
        for k, v in COMPARATORS.items():
            p = paired(g, "hv_ratio", MAIN, v).sort_values("budget_frac")
            md.append(f"| {k} | " + " | ".join(map(str, wtl(p))) + " | " + " ".join(f"{r.res}({r.diff:+.3f})" for r in p.itertuples()) + " |")
        gap = g[g.method == MAIN].hv_ratio.mean() - g[g.method == "nsga2_indep_add"].hv_ratio.mean()
        s3 = pd.concat([s3, pd.DataFrame([{"setting": s, "indep_error_mae": indep_mae(s), "gap_pairwise_minus_indep": gap}])])
        md += ["", f"S3 quantities: independence MAE {s3.indep_error_mae.iloc[-1]:.4f}, gap (pairwise m3 minus indep) {gap:+.4f}.", ""]
    rho, p = stats.spearmanr(s3.indep_error_mae, s3.gap_pairwise_minus_indep)
    md += [f"S3 rho recomputed with the new settings ({len(s3)} settings, supplementary): {rho:.3f} (p = {p:.3f}).", ""]
    (NEW / "NEW_SETTINGS.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
