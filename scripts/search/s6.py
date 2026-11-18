#!/usr/bin/env python3
"""S6 (confirmatory, docs/search_prereg_s6.md): active-learning NSGA-II vs Abacus-style (next-best fill).

    python3 scripts/search/s6.py sim      # part (b): reads results/search/s6/s6b_sweep_SIMULATED.csv
    python3 scripts/search/s6.py x3       # part (a): runs on x3_cross_family once its plans exist
Decision per cell: paired (same seed) difference active minus abacus; PASS if the lower bound of its 95% t-CI
is above tau = 0.0134. A part is HELD if every cell passes, PARTIAL if some, FAILED if none. Strict HV
(reference accuracy = all_small) is reported, not used for the decision.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agentqo.search.ground_truth import available, hv2, load_setting  # noqa: E402
from agentqo.search.methods import run_abacus, run_active  # noqa: E402
from agentqo.search.metrics import budget_for  # noqa: E402
from agentqo.search.surrogates import label_terms  # noqa: E402
from scripts.search.summarize import TAU, ci  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "results" / "search" / "s6"
SIM_CELLS = {"n_agents": (20, 30), "interaction_scale": (1.0, 2.0), "budget": (100, 200)}
X3_FRACS = (0.02, 0.05, 0.10)
SEEDS = range(30)  # part (a); part (b) uses seeds 1000-1029


def decide(diff):
    lo, hi = ci(diff)
    return float(np.mean(diff)), lo, hi, ("PASS" if lo > TAU else "fail")


def verdict(res):
    k = sum(r == "PASS" for r in res)
    return "HELD" if k == len(res) else "PARTIAL" if k else "FAILED"


def part_b():
    d = pd.read_csv(OUT / "s6b_sweep_SIMULATED.csv")
    assert d.seed.min() == 1000 and d.seed.max() == 1029 and d.seed.nunique() == 30
    rows = []
    for (n, s, b), g in d.groupby(["n_agents", "interaction_scale", "budget"]):
        x = g[g.method == "nsga2_active"].set_index("seed")
        y = g[g.method == "abacus_nextbest"].set_index("seed")
        m, lo, hi, res = decide((x.hv_ratio - y.hv_ratio).values)
        sm, slo, shi, _ = decide((x.strict_hv_ratio - y.strict_hv_ratio).values)
        rows.append({"n_agents": n, "scale": s, "B": b, "active": x.hv_ratio.mean(), "abacus_nextbest": y.hv_ratio.mean(),
                     "diff": m, "ci_low": lo, "ci_high": hi, "decision": res,
                     "strict_active": x.strict_hv_ratio.mean(), "strict_abacus": y.strict_hv_ratio.mean(),
                     "strict_diff": sm, "strict_ci_low": slo, "strict_ci_high": shi})
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "s6b_cells.csv", index=False)
    return t, verdict(t.decision.tolist())


def part_a(name="x3_cross_family", out=OUT):
    """Registered call: defaults. Exploratory size-priced call: name="x3_cross_family@size", own folder."""
    s = load_setting(name, with_latency=False)
    terms = label_terms(s)
    base = s.acc[s.row(np.zeros(s.n, dtype=int))]
    strict = lambda rows: hv2(np.maximum(s.acc[rows] - base, 0), s.cost[rows], s.cost.max())
    hv = lambda rows: hv2(s.acc[rows], s.cost[rows], s.cost.max())
    full, full_s = hv(list(range(s.size))), strict(list(range(s.size)))
    runs, rows = [], []
    for f in X3_FRACS:
        b = budget_for(s.size, f)
        ab = run_abacus(s, b, terms=terms).rows
        for seed in SEEDS:
            ac = run_active(s, b, np.random.default_rng(seed), terms=terms).rows
            runs.append({"budget_frac": f, "B": b, "seed": seed, "active": hv(ac) / full, "abacus_nextbest": hv(ab) / full,
                         "strict_active": strict(ac) / full_s, "strict_abacus": strict(ab) / full_s})
        g = pd.DataFrame([r for r in runs if r["budget_frac"] == f])
        m, lo, hi, res = decide((g.active - g.abacus_nextbest).values)
        sm, slo, shi, _ = decide((g.strict_active - g.strict_abacus).values)
        rows.append({"budget_frac": f, "B": b, "active": g.active.mean(), "abacus_nextbest": g.abacus_nextbest.mean(),
                     "diff": m, "ci_low": lo, "ci_high": hi, "decision": res, "strict_active": g.strict_active.mean(),
                     "strict_abacus": g.strict_abacus.mean(), "strict_diff": sm, "strict_ci_low": slo, "strict_ci_high": shi})
    pd.DataFrame(runs).to_csv(out / "s6a_runs.csv", index=False)
    t = pd.DataFrame(rows)
    t.to_csv(out / "s6a_cells.csv", index=False)
    return t, verdict(t.decision.tolist()), s


def table(t):
    cols = list(t.columns)
    return ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + [
        "| " + " | ".join(f"{v:.4f}" if isinstance(v, float) else str(v) for v in r) + " |" for r in t.itertuples(index=False)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    what = sys.argv[1] if len(sys.argv) > 1 else "sim"
    md_path = OUT / "S6.md"
    parts = md_path.read_text().split("\n<!-- part -->\n") if md_path.exists() else []
    keep = {p[:8]: p for p in parts if p.startswith("## S6(")}  # key "## S6(a)" / "## S6(b)"
    if what == "sim":
        t, v = part_b()
        keep["## S6(b)"] = "\n".join([f"## S6(b) simulated, seeds 1000-1029: {v}", "",
                                      f"Decision: PASS if the paired 95% CI lower bound of (active - abacus_nextbest) > tau = {TAU}.", ""]
                                     + table(t) + [""])
    else:
        if not available("x3_cross_family"):
            sys.exit("X3 plans not on this branch yet; S6(a) stays PENDING")
        t, v, s = part_a()
        keep["## S6(a)"] = "\n".join([f"## S6(a) X3 cross-family ({s.size} plans, {len(s.problems)} problems): {v}", "",
                                      f"Decision: PASS if the paired 95% CI lower bound of (active - abacus_nextbest) > tau = {TAU}.", ""]
                                     + table(t) + [""])
    head = ["# S6 (confirmatory; docs/search_prereg_s6.md)", ""]
    body = [keep.get("## S6(a)", "## S6(a) X3 cross-family: PENDING (X3 plans not landed)\n"), keep.get("## S6(b)", "## S6(b): PENDING\n")]
    md_path.write_text("\n".join(head) + "\n<!-- part -->\n" + "\n<!-- part -->\n".join(body))
    print(md_path.read_text())


if __name__ == "__main__":
    main()
