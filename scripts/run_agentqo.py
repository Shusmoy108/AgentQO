#!/usr/bin/env python3
"""Run the AgentQO runtime optimizer from the proposal.

This is not the H1–H3 labeling pipeline. It is the event-driven joint
logical/physical scheduler: edits, placement via AgentIconq, KV value,
and speculative stopping.

EC scores given to the runtime come from ``--ec-source``:
- ``structure``: downstream reach (the old heuristic)
- ``predicted``: the H2 predictor, trained on suite workflows *other than*
  the runtime workflow (leave-one-workflow-out)
- ``oracle``: fault-injection labels of the runtime workflow (upper bound)
Every source is max-normalized to [0, 1] so the optimizer's lambdas see the
same scale regardless of source.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentqo.experiments.dataset import (
    filter_samples,
    labeling_results_to_maps,
    matrix_from_samples,
    observations_to_samples,
)
from agentqo.experiments.scoring import predict_node_scores
from agentqo.experiments.suite import default_suite
from agentqo.labeling.ec_labeler import ECLabeler, LabelingResult, compute_bootstrap_ci
from agentqo.metrics.io import append_results_entry, write_csv, write_json
from agentqo.predictors.ec_predictor import GBTECPredictor
from agentqo.predictors.features import FeatureExtractor
from agentqo.runtime.system import AgentQO, Arrival, FCFSFixed, FixedPlanEC
from agentqo.simulator.task_model import MockBackend, task_model_for_workflow
from agentqo.workflows.dag import Workflow
from agentqo.workflows.library import (
    create_math_reasoning_workflow,
    create_multihop_qa_workflow,
    create_refinement_workflow,
    create_self_consistency_workflow,
)

EMBEDDING_DIM = 64
LOADS = {"low": 16.0, "med": 8.0, "high": 4.0}  # mean inter-arrival time


def _structure_ec(workflow) -> dict:
    n = max(len(workflow.nodes), 1)
    return {nid: (workflow.get_downstream_reach(nid) + 1) / n for nid in workflow.nodes}


def _normalize(scores: Dict[str, float]) -> Dict[str, float]:
    clipped = {k: max(float(v), 0.0) for k, v in scores.items()}
    top = max(clipped.values(), default=0.0)
    return {k: v / top for k, v in clipped.items()} if top > 0 else clipped


def label_suite(n_tasks: int, seed: int, quick: bool) -> Tuple[Dict[str, LabelingResult], Dict[str, Workflow]]:
    labeling: Dict[str, LabelingResult] = {}
    workflows: Dict[str, Workflow] = {}
    for member in default_suite(quick=quick):
        backend = MockBackend(member.task_model, embedding_dim=EMBEDDING_DIM)
        labeling[member.workflow.name] = ECLabeler(backend, member.task_model).label_workflow(
            member.workflow, num_tasks=n_tasks, base_seed=seed, show_progress=False,
        )
        workflows[member.workflow.name] = member.workflow
    return labeling, workflows


def train_runtime_predictor(
    labeling: Dict[str, LabelingResult],
    workflows: Dict[str, Workflow],
    exclude: str,
    extractor: FeatureExtractor,
    seed: int,
) -> Tuple[GBTECPredictor, Set[str]]:
    """Fit the H2 predictor on every labeled workflow except ``exclude``.

    Returns the predictor and the set of workflow names it saw, so callers
    (and the leakage test) can check the runtime workflow is unseen.
    """
    labels_map, observations = labeling_results_to_maps(labeling)
    samples = observations_to_samples(observations, labels_map, workflows, extractor)
    train_names = [n for n in workflows if n != exclude]
    train = filter_samples(samples, train_names)
    trained_on = {s.workflow_name for s in train}
    if exclude in trained_on or not train:
        raise RuntimeError(f"predictor for {exclude} would train on it or on nothing")
    X, y, _ = matrix_from_samples(train, "agentqo")
    predictor = GBTECPredictor(n_estimators=80, max_depth=3, random_state=seed)
    predictor.fit(X, y)
    return predictor, trained_on


def ec_scores_for(
    workflow: Workflow,
    source: str,
    seed: int,
    n_label_tasks: int,
    suite_labels: Optional[Tuple[Dict[str, LabelingResult], Dict[str, Workflow]]] = None,
) -> Tuple[Dict[str, float], Set[str]]:
    """EC scores for one runtime workflow, plus the predictor's training set."""
    if source == "structure":
        return _normalize(_structure_ec(workflow)), set()
    model = task_model_for_workflow(workflow)
    backend = MockBackend(model, embedding_dim=EMBEDDING_DIM)
    if source == "oracle":
        result = ECLabeler(backend, model).label_workflow(
            workflow, num_tasks=n_label_tasks, base_seed=seed + 5, show_progress=False,
        )
        return _normalize({nid: lab.ec_score for nid, lab in result.labels.items()}), set()
    if source == "predicted":
        assert suite_labels is not None
        labeling, workflows = suite_labels
        extractor = FeatureExtractor(EMBEDDING_DIM)
        predictor, trained_on = train_runtime_predictor(
            labeling, workflows, workflow.name, extractor, seed,
        )
        scores = predict_node_scores(
            workflow, model, backend, predictor, extractor,
            n_probes=8, view="agentqo", seed=seed + 7,
        )
        return _normalize(scores), trained_on
    raise ValueError(f"unknown ec source {source}")


def _arrivals(workflow, n_jobs: int, seed: int, ec: Dict[str, float], mean_gap: float):
    model = task_model_for_workflow(workflow)
    rng = np.random.default_rng(seed)
    jobs = []
    t = 0.0
    for i in range(n_jobs):
        task = model.generate_task(workflow, np.random.default_rng(seed + i + 1))
        jobs.append(Arrival(workflow=workflow, task=task, seed=seed + i, time=t, ec_scores=ec))
        t += float(rng.exponential(mean_gap))
    return model, jobs


def _ci(values: List[float], seed: int) -> Tuple[float, float, float]:
    arr = np.asarray(values, dtype=np.float64)
    lo, hi = compute_bootstrap_ci(arr, rng=np.random.default_rng(seed))
    return float(arr.mean()), lo, hi


def runtime_workflows() -> List[Workflow]:
    return [
        create_math_reasoning_workflow(3, include_verifier=True),
        create_multihop_qa_workflow(3, include_verifier=True),
        create_self_consistency_workflow(k=2, k_max=5),
        create_refinement_workflow(max_rounds=2),
    ]


def run_agentqo_experiment(
    n_jobs: int = 8,
    n_gpus: int = 2,
    output_dir: str = "data/agentqo",
    seed: int = 42,
    ec_source: str = "predicted",
    n_seeds: int = 1,
    loads: Tuple[str, ...] = ("med",),
    n_label_tasks: int = 30,
    quick_suite: bool = True,
    record_results: bool = False,
) -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    workflows = runtime_workflows()
    print("=" * 64)
    print(f"AgentQO runtime  (ec_source={ec_source}, seeds={n_seeds}, loads={','.join(loads)})")
    print("=" * 64)

    suite_labels = label_suite(n_label_tasks, seed, quick_suite) if ec_source == "predicted" else None
    ec_by_wf: Dict[str, Dict[str, float]] = {}
    trained_on: Dict[str, List[str]] = {}
    for wf in workflows:
        ec_by_wf[wf.name], seen = ec_scores_for(wf, ec_source, seed, n_label_tasks, suite_labels)
        trained_on[wf.name] = sorted(seen)
        print(f"{wf.name}: EC {({k: round(v, 3) for k, v in ec_by_wf[wf.name].items()})}")

    rows = []
    for wf in workflows:
        for load in loads:
            for s in range(n_seeds):
                run_seed = seed + 1000 * s
                model, jobs = _arrivals(wf, n_jobs, run_seed, ec_by_wf[wf.name], LOADS[load])
                backend = MockBackend(model, embedding_dim=EMBEDDING_DIM)
                for policy in (
                    FCFSFixed(backend, model, n_gpus=n_gpus),
                    FixedPlanEC(backend, model, n_gpus=n_gpus),
                    AgentQO(backend, model, n_gpus=n_gpus),
                ):
                    report = policy.serve(list(jobs))
                    rows.append({
                        "workflow": wf.name,
                        "load": load,
                        "seed": run_seed,
                        "policy": policy.name,
                        "ec_source": ec_source,
                        "quality": report.mean_quality,
                        "completion": report.mean_completion,
                        "p95_completion": float(np.percentile(report.completions, 95)),
                        "gpu_hours": report.gpu_hours,
                        "quality_per_gpu_hour": report.quality_per_gpu_hour,
                        "makespan": report.makespan,
                        "n_edits": sum(report.edits_used.values()),
                    })
    write_csv(output / "agentqo_runtime.csv", rows)

    # Aggregate: mean + 95% bootstrap CI over seeds; paired AgentQO - FCFS.
    summary: Dict[str, dict] = {}
    table = []
    metrics = ("quality", "completion", "quality_per_gpu_hour")
    for wf in workflows:
        for load in loads:
            cell = [r for r in rows if r["workflow"] == wf.name and r["load"] == load]
            by_policy = {p: sorted((r for r in cell if r["policy"] == p), key=lambda r: r["seed"])
                         for p in ("FCFS-Fixed", "FixedPlan-EC", "AgentQO")}
            key = f"{wf.name}|{load}"
            summary[key] = {}
            for p, rs in by_policy.items():
                entry = {m: _ci([r[m] for r in rs], seed) for m in metrics}
                entry["edits"] = float(np.mean([r["n_edits"] for r in rs]))
                summary[key][p] = entry
                table.append({"workflow": wf.name, "load": load, "policy": p,
                              **{f"{m}_{s}": v for m in metrics
                                 for s, v in zip(("mean", "ci_low", "ci_high"), entry[m])},
                              "edits": entry["edits"]})
            summary[key]["AgentQO - FCFS"] = {
                m: _ci([a[m] - b[m] for a, b in zip(by_policy["AgentQO"], by_policy["FCFS-Fixed"])], seed)
                for m in metrics
            }
    write_csv(output / "agentqo_runtime_summary.csv", table)
    write_json(output / "agentqo_runtime.json", {
        "config": {"n_jobs": n_jobs, "n_gpus": n_gpus, "seed": seed, "ec_source": ec_source,
                   "n_seeds": n_seeds, "loads": list(loads), "n_label_tasks": n_label_tasks},
        "ec_scores": ec_by_wf,
        "predictor_trained_on": trained_on,
        "summary": summary,
    })

    def fmt(t):
        return f"{t[0]:.3f} [{t[1]:.3f}, {t[2]:.3f}]"

    for key, cell in summary.items():
        print(f"\n{key}")
        for p in ("FCFS-Fixed", "FixedPlan-EC", "AgentQO"):
            e = cell[p]
            print(f"  {p:<14} Q={fmt(e['quality'])}  T={e['completion'][0]:.1f}  "
                  f"Q/GPU-h={e['quality_per_gpu_hour'][0]:.1f}  edits={e['edits']:.1f}")
        d = cell["AgentQO - FCFS"]
        print(f"  {'AgentQO-FCFS':<14} dQ={fmt(d['quality'])}  "
              f"dQ/GPU-h={d['quality_per_gpu_hour'][0]:+.1f} "
              f"[{d['quality_per_gpu_hour'][1]:+.1f}, {d['quality_per_gpu_hour'][2]:+.1f}]")

    fig_path = output / "agentqo_pareto.png"
    _save_pareto(summary, workflows, loads, fig_path)
    print(f"\nWrote {output}")

    if record_results:
        wins = [k for k, c in summary.items()
                if c["AgentQO - FCFS"]["quality_per_gpu_hour"][1] > 0]
        q_losses = [k for k, c in summary.items()
                    if c["AgentQO - FCFS"]["quality"][2] < 0]
        append_results_entry(
            "S-RT",
            {"ec_source": ec_source, "seeds": n_seeds, "loads": ",".join(loads),
             "n_jobs": n_jobs, "n_gpus": n_gpus},
            f"AgentQO Q/GPU-hour above FCFS (paired CI excludes 0) in {len(wins)}/{len(summary)} "
            f"cells; quality below FCFS (CI excludes 0) in {len(q_losses)}/{len(summary)} cells. "
            f"Table: {output / 'agentqo_runtime_summary.csv'}",
            str(fig_path),
            "Simulated clock and GPU cost; efficiency wins that come with a quality loss are not wins "
            "under the WP15 criterion (accuracy within 2 points of FCFS).",
        )
    return summary


def _save_pareto(summary, workflows, loads, path: Path) -> None:
    from agentqo.metrics.figures import _pyplot

    plt = _pyplot()
    fig, axes = plt.subplots(1, len(workflows), figsize=(4.2 * len(workflows), 3.8), squeeze=False)
    colors = {"FCFS-Fixed": "#9b9b9b", "FixedPlan-EC": "#e76f51", "AgentQO": "#2a9d8f"}
    markers = {"low": "o", "med": "s", "high": "^"}
    for ax, wf in zip(axes[0], workflows):
        for load in loads:
            cell = summary[f"{wf.name}|{load}"]
            for p, color in colors.items():
                q, t = cell[p]["quality"], cell[p]["completion"]
                ax.errorbar(t[0], q[0], xerr=[[t[0] - t[1]], [t[2] - t[0]]],
                            yerr=[[q[0] - q[1]], [q[2] - q[0]]], fmt=markers[load],
                            color=color, label=f"{p} ({load})", capsize=2)
        ax.set_title(wf.name, fontsize=9)
        ax.set_xlabel("mean completion time (sim s)")
        ax.set_ylabel("quality")
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=8,
               bbox_to_anchor=(0.5, -0.12 - 0.04 * len(loads)))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AgentQO runtime optimizer")
    parser.add_argument("--n-jobs", type=int, default=8)
    parser.add_argument("--n-gpus", type=int, default=2)
    parser.add_argument("--output-dir", type=str, default="data/agentqo")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ec-source", choices=["structure", "predicted", "oracle"],
                        default="predicted")
    parser.add_argument("--seeds", type=int, default=1, help="number of seeds")
    parser.add_argument("--loads", type=str, default="med",
                        help="comma list of low,med,high (mean inter-arrival 16/8/4)")
    parser.add_argument("--label-tasks", type=int, default=30)
    parser.add_argument("--full-suite", action="store_true",
                        help="train the predictor on the full H2 suite, not the quick one")
    args = parser.parse_args()
    loads = tuple(x.strip() for x in args.loads.split(",") if x.strip())
    bad = [x for x in loads if x not in LOADS]
    if bad:
        parser.error(f"unknown loads {bad}; choose from {list(LOADS)}")
    run_agentqo_experiment(
        n_jobs=args.n_jobs,
        n_gpus=args.n_gpus,
        output_dir=args.output_dir,
        seed=args.seed,
        ec_source=args.ec_source,
        n_seeds=args.seeds,
        loads=loads,
        n_label_tasks=args.label_tasks,
        quick_suite=not args.full_suite,
        record_results=True,
    )


if __name__ == "__main__":
    main()
