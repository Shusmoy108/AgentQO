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

--plans all_subsets (M2) runs every small/large assignment (2^n plans) with
5000-resample CIs (seed 0) against all_small. It is resumable through the cache
and never reuses a directory holding a different run. Every plan set also
writes h3_per_problem.csv and h3_calls.csv (per-call tokens and latency for M1).

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
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
from pathlib import Path
from typing import Dict, List

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scipy.stats import spearmanr  # noqa: E402

from agentqo.executor import FidelityPlan, WorkflowExecutor  # noqa: E402
from agentqo.backends.vllm_http import _output_as_text  # noqa: E402
from agentqo.metrics.io import args_config, mark_done, resolve_output_dir, write_csv, write_json  # noqa: E402
from agentqo.policies.v2_rules import plan_name  # noqa: E402
from agentqo.tasks.real_task_model import RealTaskModel, answer_node  # noqa: E402
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


def all_subset_plans(workflow) -> Dict[str, FidelityPlan]:
    """Every small/large assignment, smallest upgrades first (64 for the math chain)."""
    topo = list(workflow.topological_order)
    plans = {}
    for r in range(len(topo) + 1):
        for nodes in combinations(topo, r):
            if r == len(topo):
                plans["all_large"] = FidelityPlan(default_fidelity=LARGE_FIDELITY)
            else:
                plans[plan_name(nodes, topo)] = _upgrade(nodes)
    return plans


def make_plans(workflow, ec: Dict[str, float], extra: bool = False) -> Dict[str, FidelityPlan]:
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
        plans["qplus_top2"] = _upgrade(["aggregator", "planner"])
    return plans


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--backend", choices=["fake", "ollama", "vllm"], default="ollama")
    ap.add_argument("--workflow", default="math", choices=list(WORKFLOWS))
    ap.add_argument("--n-tasks", type=int, default=30)
    ap.add_argument("--split", choices=["dev", "eval", "all", "label", "eval_ext"], default="dev")
    ap.add_argument("--dataset", choices=["gsm8k", "hotpotqa"], default="gsm8k")
    ap.add_argument("--plans", default="",
                    help="comma list to run a subset, e.g. all_small,only_verifier; or all_subsets (M2)")
    ap.add_argument("--workers", type=int, default=1, help="problems in flight")
    ap.add_argument("--dry-run", action="store_true", help="with all_subsets: print the work, make no calls")
    ap.add_argument("--h1-summary", default="", help="h1_summary.json from run_real_pipeline.py")
    ap.add_argument("--compare", action="append", default=[], metavar="A:B",
                    help="paired difference of plan A minus plan B, as in C11 (repeatable)")
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
    if args.workflow.startswith("hotpot") != (args.dataset == "hotpotqa"):
        ap.error("--workflow hotpot and --dataset hotpotqa go together")
    all_subsets = args.plans == "all_subsets"
    if args.dry_run and not all_subsets:
        ap.error("--dry-run is for --plans all_subsets")

    out = Path(args.output_dir)
    display, make = WORKFLOWS[args.workflow]
    workflow = make()
    if all_subsets:
        out, finished = resolve_output_dir(out, args_config(args), create=not args.dry_run)
        n = len(workflow.nodes)
        if args.dry_run:
            print(f"would run {2 ** n} plans of {workflow.name} on {args.n_tasks} {args.dataset} {args.split} problems "
                  f"with {args.backend}: at most {2 ** (n + 1) - 2} calls per problem, into {out}")
            return
        if finished:
            print(f"already finished: {out}")
            return
    problems = load_problems(args)
    backend = build_backend(args, problems)
    task_model = RealTaskModel(problems, dataset=args.dataset)
    executor = WorkflowExecutor(backend, task_model)

    ec: Dict[str, float] = {}
    if args.h1_summary:
        summary = json.loads(Path(args.h1_summary).read_text())
        ec = {nid: float(d["ec"]) for nid, d in summary["by_node"].items()}

    plans = all_subset_plans(workflow) if all_subsets else make_plans(workflow, ec, extra=bool(args.plans))
    if args.plans and not all_subsets:
        keep = {p.strip() for p in args.plans.split(",") if p.strip()}
        keep.add("all_small")  # the reference for paired differences
        missing = keep - set(plans)
        if missing:
            print(f"WARNING: unknown plans ignored: {sorted(missing)}", flush=True)
        plans = {k: v for k, v in plans.items() if k in keep}

    tasks = [task_model.generate_task(workflow, None) for _ in range(len(problems))]

    def run_plan(task, name, plan):
        rec = executor.run_workflow(workflow, task, fidelity_plan=plan, seed=0)
        units = n_large = lat = 0.0
        calls = []
        for nid, r in rec.node_results.items():
            if r.metadata.get("code_node"):
                continue
            fid = plan.get_fidelity(workflow.nodes[nid])
            units += fid.cost
            n_large += fid.name == LARGE_FIDELITY.name
            lat += float(r.metadata.get("latency_s") or 0.0)
            calls.append({"plan": name, "task_id": task.task_id, "node_id": nid, "model": r.metadata.get("model"),
                          "fidelity": fid.name, "prompt_tokens": r.metadata.get("prompt_tokens", 0),
                          "completion_tokens": r.metadata.get("completion_tokens", 0),
                          "latency_s": r.metadata.get("latency_s", 0.0), "cache_hit": r.metadata.get("cache_hit")})
        answer = _output_as_text(rec.node_results[answer_node(workflow, rec.node_results)].output)
        return {
            "correct": float(rec.final_quality), "units": units, "n_large": n_large, "lat": lat, "calls": calls,
            "f1": task_model.f1_text(answer, task.ground_truth),
            "trace": {"task_id": task.task_id, "gold": task.ground_truth, "correct": float(rec.final_quality),
                      "keys": {nid: task_model.extract(_output_as_text(r.output))
                               for nid, r in rec.node_results.items()}},
        }

    progress = {"done": 0}

    def run_problem(task):
        # One problem's plans run one after another, so a shared prefix is generated
        # once and later plans read it from the cache; problems never share a prompt.
        out_ = {name: run_plan(task, name, plan) for name, plan in plans.items()}
        progress["done"] += 1
        print(f"problem {progress['done']}/{len(tasks)} done (HTTP calls so far: {backend.n_http_calls})", flush=True)
        return out_

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        by_problem = list(pool.map(run_problem, tasks))

    rows, per_task, traces, per_problem, call_rows = [], {}, {}, [], []
    for name, plan in plans.items():
        results = [p[name] for p in by_problem]
        correct = [r["correct"] for r in results]
        traces[name] = [r["trace"] for r in results]
        call_rows += [c for r in results for c in r["calls"]]
        for task, r in zip(tasks, results):
            per_problem.append({"plan": name, "task_id": task.task_id, "correct": r["correct"],
                                **({"f1": r["f1"]} if args.dataset == "hotpotqa" else {})})
        per_task[name] = np.array(correct)
        cost = float(np.mean([r["units"] for r in results]))
        n_large = float(np.mean([r["n_large"] for r in results]))
        rows.append({
            "plan": name,
            "upgraded": ",".join(sorted(plan.assignments)) or ("all" if name == "all_large" else "none"),
            "accuracy": float(np.mean(correct)),
            "cost_units": cost,
            "large_calls": n_large,
            "latency_s": float(np.mean([r["lat"] for r in results])),
            **({"f1": float(np.mean([r["f1"] for r in results]))} if args.dataset == "hotpotqa" else {}),
        })
        print(f"{name:<18} acc={np.mean(correct):.3f}  cost_units={cost:5.1f}  large_calls={n_large:.1f}", flush=True)

    base = per_task["all_small"]
    full = per_task.get("all_large")
    full_gain = float(full.mean() - base.mean()) if full is not None else None
    base_cost = next(r["cost_units"] for r in rows if r["plan"] == "all_small")
    full_cost = next((r["cost_units"] for r in rows if r["plan"] == "all_large"), None)
    for r in rows:
        if all_subsets:
            c = paired_compare(per_task[r["plan"]], base)
            d, lo, hi = c["diff"], c["ci_low"], c["ci_high"]
        else:
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

    comparisons = {}
    for spec in args.compare:
        a, b = spec.split(":")
        c = comparisons[spec] = paired_compare(per_task[a], per_task[b])
        print(f"\n{a} - {b} = {c['diff']:+.3f}  95% CI [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]  "
              f"({c['wins']} wins, {c['losses']} losses)")

    print(f"\nHTTP calls: {backend.n_http_calls}  cache hits: {backend.cache.hits}  "
          f"misses: {backend.cache.misses}")
    write_csv(out / "h3_plans.csv", rows)
    write_csv(out / "h3_per_problem.csv", per_problem)
    write_csv(out / "h3_calls.csv", call_rows)
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
    if all_subsets:
        mark_done(out)
    print(f"Artifacts in {out}")


def budget_plot(rows: List[dict], path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    by = {r["plan"]: r for r in rows}
    base = by["all_small"]
    fig, ax = plt.subplots(figsize=(6, 4))
    for prefix, label in (("ec_top", "EC order"), ("struct_top", "structure order")):
        pts = [base] + [by[f"{prefix}{k}"] for k in range(1, 5) if f"{prefix}{k}" in by]
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
