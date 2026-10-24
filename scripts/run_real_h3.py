#!/usr/bin/env python3
"""Real-model H3 pilot: which single upgrade buys the most accuracy?

Runs the math workflow on the same tasks under several fidelity plans and
reports accuracy, cost and paired confidence intervals against all-small.

Plans (default):
  all_small        every node on the small model
  all_large        every node on the large model
  only_<node>      one node on the large model, the rest small (one plan per node)
  ec_top2          the two highest-EC nodes from an H1 run on the large model
  struct_top2      the two nodes with the largest downstream reach (structural baseline)

Extra plans, built only when named in --plans (the default set above is unchanged):
  ec_top1/3/4      the k highest-EC nodes (ec_top1 = only the top-EC node)
  struct_top1/3/4  the k nodes with the largest downstream reach, ordered as struct_top2
  qplus_top2       aggregator + planner (top two by single-upgrade accuracy, Q+)
  output_top1/2/3  the k LLM nodes nearest the final node (longest path to it, shortest
                   first; ties go to the later node in topological order)
With --qplus-from <h1 run>/h1/<workflow>, qplus_top2/3 are instead the nodes with the
highest mean Q+ minus baseline correctness in that run's substitution files.

If --h1-summary points to an h1_summary.json, the script also checks whether
each node's measured EC predicts the accuracy gain from upgrading that node
(Spearman over nodes), and builds ec_top2 from it.

    python3 scripts/run_real_h3.py --backend ollama --n-tasks 30 \\
        --h1-summary data/ollama/h1_n30/h1/math_reasoning_s3_ver/h1_summary.json

Every generation goes through the same SQLite cache as run_real_pipeline.py,
so all_small reuses the H1 baseline runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scipy.stats import spearmanr  # noqa: E402

from agentqo.executor import FidelityPlan, WorkflowExecutor  # noqa: E402
from agentqo.backends.vllm_http import _output_as_text  # noqa: E402
from agentqo.metrics.io import write_csv, write_json  # noqa: E402
from agentqo.tasks.answers import extract_gsm8k_number  # noqa: E402
from agentqo.tasks.prompts import code_output  # noqa: E402
from agentqo.tasks.real_task_model import RealTaskModel  # noqa: E402
from agentqo.workflows.dag import LARGE_FIDELITY, SMALL_FIDELITY  # noqa: E402
from scripts.run_real_pipeline import WORKFLOWS, build_backend, load_problems  # noqa: E402


def paired_ci(diff: np.ndarray, seed: int, n_boot: int = 2000):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(diff), size=(n_boot, len(diff)))
    means = diff[idx].mean(axis=1)
    return float(diff.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def paired_compare(a: np.ndarray, b: np.ndarray) -> Dict[str, float]:
    """a - b per task, bootstrapped exactly as the C11 comparison (5000 resamples, seed 0)."""
    d = a - b
    rng = np.random.default_rng(0)
    m = d[rng.integers(0, len(d), (5000, len(d)))].mean(1)
    return {"diff": float(d.mean()), "ci_low": float(np.percentile(m, 2.5)),
            "ci_high": float(np.percentile(m, 97.5)), "wins": int((d > 0).sum()), "losses": int((d < 0).sum())}


def _upgrade(nodes) -> FidelityPlan:
    return FidelityPlan(assignments={n: LARGE_FIDELITY for n in nodes}, default_fidelity=SMALL_FIDELITY)


def is_llm_node(workflow, nid: str) -> bool:
    """False for nodes computed in code (passthrough verifier, SC majority vote)."""
    return code_output(workflow.nodes[nid], {}, {"workflow": workflow}) is None


def output_order(workflow) -> List[str]:
    """Upgradable LLM nodes nearest the final node first."""
    topo = list(workflow.topological_order)
    dist = {topo[-1]: 0}
    for n in reversed(topo[:-1]):
        succ = [d for d in topo if n in workflow.nodes[d].inputs and d in dist]
        if succ:
            dist[n] = 1 + max(dist[d] for d in succ)
    cand = [n for n in topo if n in dist and len(workflow.nodes[n].fidelities) > 1 and is_llm_node(workflow, n)]
    return sorted(cand, key=lambda n: (dist[n], -topo.index(n)))


def load_qplus(h1_dir: str) -> Dict[str, Dict[str, float]]:
    """Per node: mean Q+, mean Q-, and mean (Q+ - baseline correctness) over an H1 run's substitutions."""
    d = Path(h1_dir)
    base = {json.loads(t.read_text())["task_id"]: float(json.loads(t.read_text())["final_quality"])
            for t in sorted((d / "traces").glob("*.json"))}
    acc: Dict[str, List[tuple]] = {}
    for f in sorted((d / "substitutions").glob("*.json")):
        r = json.loads(f.read_text())
        acc.setdefault(r["node_id"], []).append((float(r["q_plus"]), float(r["q_minus"]), base[r["task_id"]]))
    return {n: {"q_plus": float(np.mean([a for a, _, _ in v])), "q_minus": float(np.mean([b for _, b, _ in v])),
                "baseline": float(np.mean([c for _, _, c in v])),
                "q_plus_minus_baseline": float(np.mean([a - c for a, _, c in v])), "n": len(v)}
            for n, v in acc.items()}


def make_plans(workflow, ec: Dict[str, float], extra: bool = False,
               qplus: Optional[Dict[str, Dict[str, float]]] = None) -> Dict[str, FidelityPlan]:
    nodes = list(workflow.topological_order)
    plans = {
        "all_small": FidelityPlan(default_fidelity=SMALL_FIDELITY),
        "all_large": FidelityPlan(default_fidelity=LARGE_FIDELITY),
    }
    for nid in nodes:
        if len(workflow.nodes[nid].fidelities) > 1:
            plans[f"only_{nid}"] = FidelityPlan(assignments={nid: LARGE_FIDELITY},
                                                default_fidelity=SMALL_FIDELITY)
    # Structural baseline: the two nodes with the largest downstream reach.
    upgradable = [n for n in nodes if len(workflow.nodes[n].fidelities) > 1]
    struct = sorted(upgradable, key=lambda n: (-workflow.get_downstream_reach(n), nodes.index(n)))[:2]
    plans["struct_top2"] = FidelityPlan(assignments={n: LARGE_FIDELITY for n in struct},
                                        default_fidelity=SMALL_FIDELITY)
    if ec:
        top2 = [n for n, _ in sorted(ec.items(), key=lambda kv: -kv[1])[:2]]
        plans["ec_top2"] = FidelityPlan(assignments={n: LARGE_FIDELITY for n in top2},
                                        default_fidelity=SMALL_FIDELITY)
    if extra:
        struct_order = sorted(upgradable, key=lambda n: (-workflow.get_downstream_reach(n), nodes.index(n)))
        for k in (1, 3, 4):
            plans[f"struct_top{k}"] = _upgrade(struct_order[:k])
        if ec:
            ec_order = [n for n, _ in sorted(ec.items(), key=lambda kv: -kv[1])]
            for k in (1, 3, 4):
                plans[f"ec_top{k}"] = _upgrade(ec_order[:k])
        out = output_order(workflow)
        for k in (1, 2, 3):
            plans[f"output_top{k}"] = _upgrade(out[:k])
        if qplus is None:
            plans["qplus_top2"] = _upgrade(["aggregator", "planner"])
        else:
            q_order = sorted((n for n in qplus if n in upgradable and is_llm_node(workflow, n)),
                             key=lambda n: (-qplus[n]["q_plus_minus_baseline"], nodes.index(n)))
            for k in (2, 3):
                plans[f"qplus_top{k}"] = _upgrade(q_order[:k])
    return plans


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--backend", choices=["fake", "ollama", "vllm"], default="ollama")
    ap.add_argument("--workflow", default="math", choices=list(WORKFLOWS))
    ap.add_argument("--n-tasks", type=int, default=30)
    ap.add_argument("--split", choices=["dev", "eval", "all"], default="dev")
    ap.add_argument("--plans", default="", help="comma list to run a subset, e.g. all_small,only_verifier")
    ap.add_argument("--h1-summary", default="", help="h1_summary.json from run_real_pipeline.py")
    ap.add_argument("--compare", action="append", default=[], metavar="A:B",
                    help="paired difference of plan A minus plan B, as in C11 (repeatable)")
    ap.add_argument("--qplus-from", default="",
                    help="h1/<workflow> dir of an H1 run: build qplus_top2/3 from its substitutions")
    ap.add_argument("--budget-plot", action="store_true",
                    help="write budget_curve.png: accuracy vs extra cost for ec_top* and struct_top*")
    ap.add_argument("--cache", default="data/cache/ollama.sqlite")
    ap.add_argument("--output-dir", default="data/ollama/h3_math")
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--allow-missing-logprobs", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    # Accepted so build_backend/make_probe see the attributes they expect.
    ap.add_argument("--probe", default="placeholder")
    ap.add_argument("--probe-model", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--probe-layer", type=int, default=None)
    ap.add_argument("--probe-pool", default="mean")
    args = ap.parse_args()

    out = Path(args.output_dir)
    problems = load_problems(args)
    backend = build_backend(args, problems)
    display, make = WORKFLOWS[args.workflow]
    workflow = make()
    task_model = RealTaskModel(problems)
    executor = WorkflowExecutor(backend, task_model)

    ec: Dict[str, float] = {}
    if args.h1_summary:
        summary = json.loads(Path(args.h1_summary).read_text())
        ec = {nid: float(d["ec"]) for nid, d in summary["by_node"].items()}

    qplus = load_qplus(args.qplus_from) if args.qplus_from else None
    if qplus:
        print(f"Q+ from {args.qplus_from}:")
        print(f"  {'node':<14}{'Q+':>7}{'Q-':>7}{'base':>7}{'Q+-base':>9}{'n':>5}")
        for n, q in qplus.items():
            print(f"  {n:<14}{q['q_plus']:7.3f}{q['q_minus']:7.3f}{q['baseline']:7.3f}"
                  f"{q['q_plus_minus_baseline']:+9.3f}{q['n']:5d}")
    plans = make_plans(workflow, ec, extra=bool(args.plans), qplus=qplus)
    if args.plans:
        keep = {p.strip() for p in args.plans.split(",") if p.strip()}
        keep.add("all_small")  # the reference for paired differences
        missing = keep - set(plans)
        if missing:
            print(f"WARNING: unknown plans ignored: {sorted(missing)}", flush=True)
        plans = {k: v for k, v in plans.items() if k in keep}
        print(f"workflow {workflow.name}; output order: {output_order(workflow)}")
        for k, v in plans.items():
            print(f"  plan {k:<16} upgrades {sorted(v.assignments) if v.assignments else ('all' if k == 'all_large' else 'none')}")
        print(flush=True)

    rows, per_task, traces = [], {}, {}
    for name, plan in plans.items():
        task_model.reset()
        correct, cost_units, large_calls, latency = [], [], [], []
        for _ in range(len(problems)):
            task = task_model.generate_task(workflow, None)
            rec = executor.run_workflow(workflow, task, fidelity_plan=plan, seed=0)
            correct.append(float(rec.final_quality))
            traces.setdefault(name, []).append({
                "task_id": task.task_id, "gold": task.ground_truth,
                "correct": float(rec.final_quality),
                "keys": {nid: extract_gsm8k_number(_output_as_text(r.output))
                         for nid, r in rec.node_results.items()},
            })
            units = n_large = lat = 0.0
            for nid, r in rec.node_results.items():
                if r.metadata.get("code_node"):
                    continue
                fid = plan.get_fidelity(workflow.nodes[nid])
                units += fid.cost
                n_large += fid.name == LARGE_FIDELITY.name
                lat += float(r.metadata.get("latency_s") or 0.0)
            cost_units.append(units)
            large_calls.append(n_large)
            latency.append(lat)
        per_task[name] = np.array(correct)
        rows.append({
            "plan": name,
            "upgraded": ",".join(sorted(plan.assignments)) or ("all" if name == "all_large" else "none"),
            "accuracy": float(np.mean(correct)),
            "cost_units": float(np.mean(cost_units)),
            "large_calls": float(np.mean(large_calls)),
            "latency_s": float(np.mean(latency)),
        })
        print(f"{name:<18} acc={np.mean(correct):.3f}  cost_units={np.mean(cost_units):5.1f}  "
              f"large_calls={np.mean(large_calls):.1f}", flush=True)

    base = per_task["all_small"]
    full = per_task.get("all_large")
    full_gain = float(full.mean() - base.mean()) if full is not None else None
    base_cost = next(r["cost_units"] for r in rows if r["plan"] == "all_small")
    full_cost = next((r["cost_units"] for r in rows if r["plan"] == "all_large"), None)
    for r in rows:
        d, lo, hi = paired_ci(per_task[r["plan"]] - base, args.seed)
        r.update({"gain_vs_small": d, "gain_ci_low": lo, "gain_ci_high": hi})
        if full_gain:
            r["share_of_full_gain"] = d / full_gain
        if full_cost and full_cost > base_cost:
            r["share_of_full_extra_cost"] = (r["cost_units"] - base_cost) / (full_cost - base_cost)

    print(f"\n{'plan':<18}{'acc':>7}{'gain vs small [95% CI]':>28}{'%gain':>8}{'%cost':>8}")
    for r in sorted(rows, key=lambda r: -r["accuracy"]):
        share = f"{100 * r['share_of_full_gain']:.0f}%" if "share_of_full_gain" in r else "-"
        cshare = f"{100 * r['share_of_full_extra_cost']:.0f}%" if "share_of_full_extra_cost" in r else "-"
        ci = f"{r['gain_vs_small']:+.3f} [{r['gain_ci_low']:+.3f},{r['gain_ci_high']:+.3f}]"
        print(f"{r['plan']:<18}{r['accuracy']:7.3f}{ci:>28}{share:>8}{cshare:>8}")

    ec_check = None
    singles = {r["plan"][5:]: r["gain_vs_small"] for r in rows if r["plan"].startswith("only_")}
    if ec and len(singles) >= 3:
        common = [n for n in singles if n in ec]
        rho, p = spearmanr([ec[n] for n in common], [singles[n] for n in common])
        ec_check = {"spearman_ec_vs_gain": float(rho), "p_value": float(p), "nodes": common}
        print(f"\nDoes measured EC predict the gain from upgrading a node? "
              f"Spearman = {rho:+.2f} (p = {p:.2f}, n = {len(common)} nodes)")
    if ec and qplus and len(singles) >= 3:
        cons = {nid: float(d["consequence"]) for nid, d in summary["by_node"].items()}
        llm = [n for n in singles if is_llm_node(workflow, n) and n in ec and n in qplus]
        ec_check = dict(ec_check or {}, llm_nodes=llm)
        print(f"Spearman vs single-node gain over {len(llm)} LLM nodes:")
        for label, src in (("EC", ec), ("consequence", cons),
                           ("Q+ - baseline", {n: q["q_plus_minus_baseline"] for n, q in qplus.items()})):
            rho, p = spearmanr([src[n] for n in llm], [singles[n] for n in llm])
            ec_check[f"spearman_{label}"] = {"rho": float(rho), "p_value": float(p)}
            print(f"  {label:<14} rho = {rho:+.2f} (p = {p:.2f})")

    comparisons = {}
    for spec in args.compare:
        a, b = spec.split(":")
        c = comparisons[spec] = paired_compare(per_task[a], per_task[b])
        print(f"\n{a} - {b} = {c['diff']:+.3f}  95% CI [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]  "
              f"({c['wins']} wins, {c['losses']} losses)")

    print(f"\nHTTP calls: {backend.n_http_calls}  cache hits: {backend.cache.hits}  "
          f"misses: {backend.cache.misses}")
    write_csv(out / "h3_plans.csv", rows)
    if args.budget_plot:
        budget_plot(rows, out / "budget_curve.png")
    write_json(out / "h3_traces.json", traces)

    # How does the final node change the answer it receives, per plan?
    last = workflow.topological_order[-1]
    prev = [n for n in workflow.nodes[last].inputs]
    if prev:
        print(f"\n{last} vs {prev[0]} (per plan):  changed / fixed / broke / {prev[0]} acc -> final acc")
        for name, ts in traces.items():
            def ok(k, g):
                try:
                    return k is not None and abs(float(str(k).replace(",", "")) - float(str(g).replace(",", ""))) < 1e-6
                except ValueError:
                    return False
            ch = fx = br = up_ok = 0
            for t in ts:
                a, v, g = t["keys"].get(prev[0]), t["keys"].get(last), t["gold"]
                up_ok += ok(a, g)
                if not ok(a, v) and a != v:
                    ch += 1
                    fx += (not ok(a, g)) and ok(v, g)
                    br += ok(a, g) and (not ok(v, g))
            n = len(ts)
            print(f"  {name:<18}{ch:>3}/{n}  {fx:>3}  {br:>3}   {up_ok / n:.2f} -> {np.mean([t['correct'] for t in ts]):.2f}")
    summary_out = {
        "config": vars(args), "workflow": workflow.name, "n_tasks": len(problems),
        "plans": rows, "ec_from_h1": ec, "ec_check": ec_check,
        "qids": [p["qid"] for p in problems],
    }
    if comparisons:
        summary_out["comparisons"] = comparisons
    write_json(out / "h3_summary.json", summary_out)
    print(f"Artifacts in {out}")


def budget_plot(rows: List[dict], path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    by = {r["plan"]: r for r in rows}
    base = by["all_small"]
    fig, ax = plt.subplots(figsize=(6, 4))
    for prefix, label in (("ec_top", "EC order"), ("qplus_top", "Q+ order"), ("struct_top", "structure order"),
                          ("output_top", "output order")):
        pts = [base] + [by[f"{prefix}{k}"] for k in range(1, 5) if f"{prefix}{k}" in by]
        if len(pts) == 1:
            continue
        ax.plot([r["cost_units"] - base["cost_units"] for r in pts], [r["accuracy"] for r in pts],
                marker="o", label=label)
    for name in ("all_small", "all_large"):
        if name in by:
            r = by[name]
            ax.scatter([r["cost_units"] - base["cost_units"]], [r["accuracy"]], color="black", zorder=3)
            ax.annotate(name, (r["cost_units"] - base["cost_units"], r["accuracy"]),
                        textcoords="offset points", xytext=(5, -12))
    ax.set_xlabel("extra cost units vs all_small")
    ax.set_ylabel("accuracy")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
