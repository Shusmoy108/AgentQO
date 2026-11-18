#!/usr/bin/env python3
"""EXPLORATORY, not registered: summary of the SIMULATED interaction-strength x agents x budget sweep.

    python3 scripts/search/sweep_summary.py
Reads results/search/exploratory/scalability_interaction_SIMULATED.csv; writes SCALABILITY_INTERACTION.md and
results/search/figures/sweep_vs_abacus_SIMULATED.png.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.search.summarize import TAU, ci  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EX = ROOT / "results" / "search" / "exploratory"
AWARE = ["nsga2_pairwise", "nsga2_active"]


def cell(g, a, b):
    x = g[g.method == a].set_index("seed").hv_ratio
    y = g[g.method == b].set_index("seed").hv_ratio
    d = (x - y).dropna()
    lo, hi = ci(d)
    return d.mean(), ("W" if d.mean() > TAU and lo > 0 else "L" if d.mean() < -TAU and hi < 0 else "T")


def main():
    d = pd.read_csv(EX / "scalability_interaction_SIMULATED.csv")
    ns, scales, budgets = sorted(d.n_agents.unique()), sorted(d.interaction_scale.unique()), sorted(d.budget.unique())
    md = ["# Scalability x interaction strength (SIMULATED; exploratory, not registered)", "",
          "Synthetic 3-tier workflows (agentqo/search/scalability.py --interaction-sweep). Each (agents, seed) instance",
          "is drawn once; the sampled pair interactions are then multiplied by 0, 0.5, 1, 2, 4 (1 = the measured",
          "distribution; 0 = purely additive truth, label noise still present). HV ratio vs the best known front",
          "(oracle NSGA-II pop 200 x 300 gens, union with every method's verified plans). 30 seeds per cell.",
          "Methods: nsga2_pairwise (pairwise m 3, registered surrogate), nsga2_active (re-fits pair terms from verified",
          "plans in 4 rounds), nsga2_independence, abacus (exact Pareto DP over the independence estimate),",
          "greedy_uv (stops after 2n+1 plans), random.", "",
          f"## Where interaction-aware search beats Abacus-style (paired over 30 seeds, tau = {TAU}, 95% CI)", "",
          "Cell = mean HV-ratio difference (method minus abacus) and W/T/L.", ""]
    grids = {}
    for a in AWARE:
        for b in budgets:
            md += [f"### {a} vs abacus, B = {b}", "", "| agents \\ scale | " + " | ".join(f"x{s:g}" for s in scales) + " |",
                   "|---|" + "---|" * len(scales)]
            G = np.zeros((len(ns), len(scales))); R = np.empty_like(G, dtype=object)
            for i, n in enumerate(ns):
                row = []
                for j, s in enumerate(scales):
                    g = d[(d.n_agents == n) & (d.interaction_scale == s) & (d.budget == b)]
                    G[i, j], R[i, j] = cell(g, a, "abacus")
                    row.append(f"{G[i, j]:+.3f} {R[i, j]}")
                md.append(f"| {n} | " + " | ".join(row) + " |")
            grids[(a, b)] = (G, R)
            md.append("")
    wins = {(a, b): [(ns[i], scales[j]) for i in range(len(ns)) for j in range(len(scales)) if grids[(a, b)][1][i, j] == "W"]
            for a in AWARE for b in budgets}
    md += ["Cells where the interaction-aware method WINS against abacus:", ""]
    md += [f"- {a}, B={b}: " + (", ".join(f"{n} agents x{s:g}" for n, s in w) or "none") for (a, b), w in wins.items()]
    md.append("")

    piv = d.groupby(["budget", "interaction_scale", "method"]).hv_ratio.mean().unstack().round(3)
    md += ["## Mean HV ratio by budget and interaction scale (averaged over 10-30 agents)", "",
           "| B | scale | " + " | ".join(piv.columns) + " |", "|---|---|" + "---|" * len(piv.columns)]
    md += [f"| {b} | x{s:g} | " + " | ".join(f"{v:.3f}" for v in r) + " |" for (b, s), r in piv.iterrows()]
    md.append("")

    ab = d[d.method == "abacus"].groupby("n_agents").agg(front=("abacus_front_size", "mean"), front_max=("abacus_front_size", "max"),
                                                          dp_s=("abacus_dp_s", "mean"))
    md += ["## How Abacus-style scales", "",
           "Abacus-style never enumerates the 3^n plans. With additive (independence) estimates of cost and accuracy,",
           "the estimated Pareto front can be built agent by agent: keep only the non-dominated partial plans (cost,",
           "estimated accuracy), extend each by the 3 tiers of the next agent, prune again. Work is about n x 3|F|",
           "dominance checks per step, where |F| is the size of the estimated front, not 3^n:", "",
           "| agents | plans (3^n) | mean estimated-front size | max | mean DP time (s) |", "|---|---|---|---|---|"]
    md += [f"| {n} | {3**n:.2e} | {r.front:.0f} | {r.front_max:.0f} | {r.dp_s:.3f} |" for n, r in ab.iterrows()]
    md += ["", "The pruning is exact only for the independence estimate. When true pair interactions are strong, the",
           "true front contains plans the additive estimate ranks as dominated, and Abacus-style can only reach",
           "them by its budget-filling picks; that is the regime where the interaction-aware searches can win.",
           "Budget filling: Abacus-style verifies its estimated front spread along cost; when the front is smaller than",
           "B (typical at 10-15 agents, e.g. 34 plans at 10 agents vs B = 50-200) the rest of B is filled with random",
           "plans (logged choice), so at small n its extra budget is effectively random search.", ""]
    (EX / "SCALABILITY_INTERACTION.md").write_text("\n".join(md) + "\n")

    # figure: diverging grids (orange = abacus better, blue = interaction-aware better, gray midpoint)
    cmap = LinearSegmentedColormap.from_list("div", ["#eb6834", "#f0efec", "#2a78d6"])
    fig, axes = plt.subplots(len(AWARE), len(budgets), figsize=(13, 7.5))
    lim = max(np.abs(g[0]).max() for g in grids.values())
    for i, a in enumerate(AWARE):
        for j, b in enumerate(budgets):
            ax = axes[i, j]
            G, R = grids[(a, b)]
            im = ax.imshow(G, cmap=cmap, vmin=-lim, vmax=lim, aspect="auto")
            for r in range(len(ns)):
                for c in range(len(scales)):
                    ax.text(c, r, f"{G[r, c]:+.3f}\n{R[r, c]}", ha="center", va="center", fontsize=8, color="#111")
            ax.set_xticks(range(len(scales))); ax.set_xticklabels([f"x{s:g}" for s in scales])
            ax.set_yticks(range(len(ns))); ax.set_yticklabels(ns)
            ax.set_title(f"{a} minus abacus, B={b}", fontsize=9)
            ax.set_xlabel("pair-interaction scale (x measured)"); ax.set_ylabel("agents")
    fig.colorbar(im, ax=axes, label="HV ratio difference (blue: interaction-aware better)")
    fig.suptitle("SIMULATED, exploratory: interaction-aware search vs Abacus-style (W/T/L, tau = 0.0134)", fontsize=10)
    fig.savefig(ROOT / "results" / "search" / "figures" / "sweep_vs_abacus_SIMULATED.png", dpi=130, bbox_inches="tight")
    print("\n".join(md))


if __name__ == "__main__":
    main()
