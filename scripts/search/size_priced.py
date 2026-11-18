#!/usr/bin/env python3
"""EXPLORATORY, not registered: size-priced cross-family / cross-size settings next to the tier-priced results.

    python3 scripts/search/run_search.py --settings x3_cross_family@size,math_q7_32@size,hotpot_q7_32@size,code_c15_7@size \
        --out results/search/exploratory/size_priced/results.csv
    python3 scripts/search/size_priced.py
Size pricing (agentqo/search/ground_truth.py SIZE_B): each tier's per-token rate = main-table "large" rate x model
parameters / 7B. Tier-priced rows come from results/search/new_settings/results.csv; the registered S6(a) from
results/search/s6/s6a_cells.csv. Also runs the frozen S6(a) procedure on x3_cross_family@size.
Writes results/search/exploratory/size_priced/SIZE_PRICED.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agentqo.search.ground_truth import SIZE, SIZE_B, _calls, V2, EXTRA, load_setting, true_front  # noqa: E402
from agentqo.search.methods import METHODS_2D  # noqa: E402
from scripts.search import s6  # noqa: E402
from scripts.search.summarize import COMPARATORS, MAIN, OUT, paired, wtl  # noqa: E402

EX = OUT / "exploratory" / "size_priced"
SETS = ["x3_cross_family", "math_q7_32", "math500_q7_32", "hotpot_q7_32", "code_c15_7"]
KEY = ["nsga2_pairwise_m3", "nsga2_active_m3", "nsga2_indep_add", "abacus", "greedy_uv", "random"]


def main():
    tier = pd.read_csv(OUT / "new_settings" / "results.csv")
    size = pd.read_csv(EX / "results.csv")
    size["setting"] = size.setting.str.removesuffix(SIZE)
    md = ["# Size-priced settings (exploratory: size-priced; not registered)", "",
          "Tier pricing (registered, and used for every result outside this section) charges each tier the main",
          "price table's rate by tier NAME. In X3 the tiers are different model families (small = Qwen2.5-7B, large =",
          "Granite-3.1-8B, xl = Phi-4 14B), so tier pricing makes Granite 20x Qwen 7B. Size pricing charges each call",
          "from its token counts at a per-model rate proportional to parameter count, anchored at Qwen 7B = the main",
          "table's large rate (2.00 / 10.00 USD per M input / output tokens). The same rule prices the label runs, so",
          "the surrogates' cost terms change with it. X6 (7B vs 32B) and X7 (Coder 1.5B vs 7B) are a sensitivity check.",
          "Accuracy is unchanged; only cost, hence the fronts, budgets' targets and HV, change.", "",
          "## Pricing and true fronts", "",
          "| setting | tier: model (rate x large) | all-top / all-small cost, tier -> size | true front plans, tier -> size | shared |",
          "|---|---|---|---|---|"]
    for n in SETS:
        st, ss = load_setting(n, False), load_setting(n + SIZE, False)
        calls = _calls(V2 / str(EXTRA[n]["plans"]))
        tm = {}
        for c in calls[:20000]:
            tm.setdefault(c["fidelity"], c["model"])
        models = "; ".join(f"{t}: {tm[t].split('/')[-1]} ({SIZE_B[tm[t]] / 7:.3g})" for t in st.tiers)
        top, z = np.full(st.n, len(st.tiers) - 1), np.zeros(st.n, int)
        r = lambda s: s.cost[s.row(top)] / s.cost[s.row(z)]
        ft, fs = set(true_front(st)), set(true_front(ss))
        md.append(f"| {n} | {models} | {r(st):.1f} -> {r(ss):.2f} | {len(ft)} -> {len(fs)} | {len(ft & fs)} |")
    md.append("")

    md += ["## Mean HV ratio, tier-priced -> size-priced (30 seeds; each distinct budget once)", ""]
    for n in SETS:
        gt, gs = tier[(tier.setting == n) & (tier.objectives == "acc_cost")], size[(size.setting == n) & (size.objectives == "acc_cost")]
        fr = gt.groupby("budget").budget_frac.min().sort_values()  # one fraction per distinct B
        md += [f"### {n}", "", "| method | " + " | ".join(f"B={b}" for b in fr.index) + " |", "|---|" + "---|" * len(fr)]
        pt = gt.groupby(["method", "budget_frac"]).hv_ratio.mean()
        ps = gs.groupby(["method", "budget_frac"]).hv_ratio.mean()
        for m in METHODS_2D:
            if (m, fr.iloc[0]) in pt:
                md.append(f"| {m} | " + " | ".join(f"{pt[(m, f)]:.3f} -> {ps[(m, f)]:.3f}" for f in fr) + " |")
        md += ["", f"{MAIN} minus comparator, W/T/L over the distinct budgets (tau = 0.0134), tier -> size:", "",
               "| comparator | tier | size |", "|---|---|---|"]
        for k, v in COMPARATORS.items():
            if v in set(gt.method):
                a = wtl(paired(gt[gt.budget_frac.isin(fr)], "hv_ratio", MAIN, v))
                b = wtl(paired(gs[gs.budget_frac.isin(fr)], "hv_ratio", MAIN, v))
                md.append(f"| {k} | {'/'.join(map(str, a))} | {'/'.join(map(str, b))} |")
        md.append("")

    # S6(a) frozen procedure on the size-priced X3 (exploratory), next to the registered tier-priced S6(a)
    ts, v, s = s6.part_a("x3_cross_family" + SIZE, EX)
    reg = pd.read_csv(OUT / "s6" / "s6a_cells.csv")
    md += ["## S6(a) procedure under size pricing (exploratory: size-priced; the registered S6(a) stays FAILED)", "",
           "Same frozen code, seeds, budgets and decision rule (PASS if the paired 95% CI lower bound of active minus",
           f"abacus_nextbest > tau = {s6.TAU}); only the cost model differs. Size-priced result: {v}.", "",
           "| B | tier: active / abacus_nextbest / diff / decision | size: active / abacus_nextbest / diff [CI] / decision | size strict diff |",
           "|---|---|---|---|"]
    for (_, a), (_, b) in zip(reg.iterrows(), ts.iterrows()):
        md.append(f"| {int(b.B)} | {a.active:.4f} / {a.abacus_nextbest:.4f} / {a['diff']:+.4f} / {a.decision} | "
                  f"{b.active:.4f} / {b.abacus_nextbest:.4f} / {b['diff']:+.4f} [{b.ci_low:+.4f}, {b.ci_high:+.4f}] / {b.decision} | "
                  f"{b.strict_diff:+.4f} |")
    md.append("")
    (EX / "SIZE_PRICED.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
