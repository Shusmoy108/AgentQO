#!/usr/bin/env python3
"""P6: hypotheses.md, the numbers behind each hypothesis and amendment, per setting.

    python3 scripts/v2/hypotheses_report.py --p6 results/v2/P6 --output-dir results/v2/P6/hypotheses

Reads the P6 step outputs (cost, rules, pareto, routing, adaptive) of every setting and
prints the values the pre-registration and its amendments name. It reports values and the
code's yes/no flags; it does not judge a hypothesis whose reading needs more than one flag.
The "Cost basis" section says which GPU costs are measured, estimated from P5 rates, or a
latency fallback (A7, A11).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agentqo.metrics.io import args_config, mark_done, resolve_output_dir, write_json  # noqa: E402

SETTINGS = ("math_q15_7", "hotpot_q15_7", "math_q3_14", "math_granite")


def _json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def _f(x: Any) -> str:
    if isinstance(x, bool) or x is None:
        return "-" if x is None else ("yes" if x else "no")
    if isinstance(x, float):
        return f"{x:.3f}"
    return str(x)


def collect(step: Path) -> Dict[str, Any]:
    cost, rules = _json(step / "cost/cost_summary.json"), _json(step / "rules/rules_summary.json")
    pareto, routing = _json(step / "pareto/pareto_summary.json"), _json(step / "routing/routing_summary.json")
    adaptive, h1c = _json(step / "adaptive/adaptive_summary.json"), rules.get("h1c", {})
    plans = _csv(step / "rules/rule_plans.csv")
    est = {r["estimator"]: r for r in _csv(step / "rules/estimator_errors.csv")}
    best = lambda rule: sum(r["is_best"] == "True" for r in plans if r["rule"] == rule and r["budget"] in ("1", "2"))
    regret = [float(r["regret"]) for r in plans if r["rule"] == "confident_uv" and r["budget"] in ("1", "2")]
    e3 = h1c.get("e3_skip_variants", {})
    out = {
        "H1a ec_real / ec_synthetic best picks at budgets 1-2": f"{best('ec_real_topk')} / {best('ec_topk')}" if plans else None,
        "H1b confident_uv max regret, budgets 1-2": max(regret) if regret else None,
        "A1 rerun share (<= 0.5)": h1c.get("share"),
        "A1 max UV change (<= 0.02)": h1c.get("a1_max_uv_abs_diff"),
        "A1/A10 top-2 agents same": h1c.get("top2_same"),
        "A1/A10 confident_uv budget-1/2 picks same": h1c.get("a1_confident_uv_same"),
        "E3 exact-skip rerun share / max UV error": (f"{_f(e3['exact']['share'])} / {_f(e3['exact']['max_uv_abs_error'])}"
                                                     if e3 else None),
        "E3 key-skip rerun share / max UV error": (f"{_f(e3['key']['share'])} / {_f(e3['key']['max_uv_abs_error'])}"
                                                   if e3 else None),
    }
    for name in ("independence_additive", "independence_multiplicative", "pairwise_corrected", "logit_additive"):
        out[f"H2 MAE held-out, {name}"] = float(est[name]["mae_held_out"]) if name in est else None
    for q in ("p25", "p50", "p75"):
        out[f"H2b feasibility wrong {q}: additive / pairwise"] = (
            f"{_f(float(est['independence_additive'][f'feasibility_wrong_{q}']))} / "
            f"{_f(float(est['pairwise_corrected'][f'feasibility_wrong_{q}']))}" if est else None)
    out.update({
        "H3a best allocation differs, separate vs shared": pareto.get("h3a_best_differs"),
        "A2 joint hypervolume strictly higher": pareto.get("a2_hv_strictly_higher"),
        "A2 max accuracy gap under (cost, p95) limits": pareto.get("a2_max_limit_gap"),
        "H3c share of plans within 10% of measured p95": pareto.get("h3c_share_within_10pct"),
        "H4a best plan differs, API vs GPU pricing": pareto.get("h4a_any_budget_differs"),
        "A3 Kendall tau, separate": cost.get("a3_kendall_tau_separate"),
        "A3 Kendall tau, shared": cost.get("a3_kendall_tau_shared"),
        "A3 Kendall tau, shared_mps": cost.get("a3_kendall_tau_shared_mps"),
        "H5a mean gap / mean problems used": (f"{_f(adaptive['mean_gap'])} / {_f(adaptive['mean_problems_used'])}"
                                              if adaptive else None),
        "A4 agent (K samples), H6 match": (f"{routing['a4_agent']} ({routing['a4_k_samples']}), {_f(routing['a4_h6_match'])}"
                                           if routing else None),
    })
    basis = {"p5_runs": cost.get("p5_runs", []), "gpu_cost_basis": cost.get("gpu_cost_basis", {}),
             "a3_basis": {p: cost.get(f"a3_basis_{p}") for p in ("separate", "shared", "shared_mps")},
             "pareto_cost_metric": pareto.get("cost_metric"), "pareto_any_fallback": pareto.get("any_fallback"),
             "pareto_cost_basis_counts": pareto.get("cost_basis_counts")}
    return {"values": out, "cost_basis": basis}


def render(data: Dict[str, Dict[str, Any]]) -> str:
    settings = list(data)
    md = ["# Hypotheses: values per setting", "",
          "Values and the code's flags as read in `prereg/v2_lease1.md` and `prereg/v2_amendments.md`. "
          "E-rows are exploratory. `-` = no data for that setting.", ""]
    md += ["| item | " + " | ".join(settings) + " |", "|---|" + "---|" * len(settings)]
    keys = list(next(iter(data.values()))["values"]) if data else []
    for k in keys:
        md.append(f"| {k} | " + " | ".join(_f(data[s]["values"][k]) for s in settings) + " |")
    md += ["", "## Cost basis (A7, A11)", "",
           "GPU cost per plan is `measured` only for P5 placement runs (`placement_costs.csv`). Every quality-phase "
           "plan cost is `estimated_rates` (a_m x prompt + b_m x completion, rates fitted on P5) or "
           "`fallback_latency` (no P5 rates for a model and placement: the per-call latency price).", ""]
    md += ["| setting | P5 runs used | separate | shared | shared_mps | Pareto metric | Pareto has fallback |",
           "|---|---|---|---|---|---|---|"]
    for s in settings:
        b = data[s]["cost_basis"]
        cell = lambda p: ", ".join(f"{k} {v}" for k, v in b["gpu_cost_basis"].get(p, {}).items()) or "-"
        md.append(f"| {s} | {', '.join(b['p5_runs']) or 'none'} | {cell('separate')} | {cell('shared')} | "
                  f"{cell('shared_mps')} | {b['pareto_cost_metric'] or '-'} | {_f(b['pareto_any_fallback'])} |")
    return "\n".join(md) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--p6", required=True, help="the P6 results directory")
    ap.add_argument("--output-dir", default="results/v2/P6/hypotheses")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    out, done = resolve_output_dir(args.output_dir, args_config(args), create=not args.dry_run)
    if args.dry_run:
        print(f"would write hypotheses.md for {args.p6} into {out}")
        return
    if done:
        print(f"already finished: {out}")
        return
    p6 = Path(args.p6)
    data = {s: collect(p6 / s) for s in SETTINGS if (p6 / s / "cost").exists()}
    (out / "hypotheses.md").write_text(render(data))
    write_json(out / "hypotheses.json", data)
    mark_done(out)
    print(f"wrote {out}/hypotheses.md ({len(data)} settings)")


if __name__ == "__main__":
    main()
