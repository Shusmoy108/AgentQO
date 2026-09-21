#!/usr/bin/env python3
"""Run the AgentQO runtime optimizer from the proposal.

This is not the H1–H3 labeling pipeline. It is the event-driven joint
logical/physical scheduler: edits, placement via AgentIconq, KV value,
and speculative stopping.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentqo.metrics.io import write_csv, write_json
from agentqo.runtime.system import AgentQO, Arrival, FCFSFixed, FixedPlanEC
from agentqo.simulator.task_model import MockBackend, task_model_for_workflow
from agentqo.workflows.library import (
    create_math_reasoning_workflow,
    create_multihop_qa_workflow,
    create_refinement_workflow,
    create_self_consistency_workflow,
)


def _structure_ec(workflow) -> dict:
    n = max(len(workflow.nodes), 1)
    return {nid: (workflow.get_downstream_reach(nid) + 1) / n for nid in workflow.nodes}


def _arrivals(workflow, n_jobs: int, seed: int):
    model = task_model_for_workflow(workflow)
    rng = np.random.default_rng(seed)
    jobs = []
    t = 0.0
    for i in range(n_jobs):
        task = model.generate_task(workflow, np.random.default_rng(seed + i + 1))
        jobs.append(Arrival(
            workflow=workflow,
            task=task,
            seed=seed + i,
            time=t,
            ec_scores=_structure_ec(workflow),
        ))
        t += float(rng.exponential(8.0))
    return model, jobs


def run_agentqo_experiment(
    n_jobs: int = 8,
    n_gpus: int = 2,
    output_dir: str = "data/agentqo",
    seed: int = 42,
) -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    workflows = [
        create_math_reasoning_workflow(3, include_verifier=True),
        create_multihop_qa_workflow(3, include_verifier=True),
        create_self_consistency_workflow(k=2, k_max=5),
        create_refinement_workflow(max_rounds=2),
    ]
    rows = []
    summaries = {}
    print("=" * 64)
    print("AgentQO runtime  (proposal §V: joint logical + physical)")
    print("=" * 64)
    for workflow in workflows:
        model, jobs = _arrivals(workflow, n_jobs, seed)
        backend = MockBackend(model, embedding_dim=64)
        policies = [
            FCFSFixed(backend, model, n_gpus=n_gpus),
            FixedPlanEC(backend, model, n_gpus=n_gpus),
            AgentQO(backend, model, n_gpus=n_gpus),
        ]
        summaries[workflow.name] = {}
        print(f"\n{workflow.name}")
        for policy in policies:
            # Fresh backend/model is fine; jobs carry their tasks.
            report = policy.serve(list(jobs))
            summaries[workflow.name][policy.name] = {
                "quality": report.mean_quality,
                "completion": report.mean_completion,
                "gpu_time": report.gpu_hours,
                "quality_per_gpu": report.quality_per_gpu_hour,
                "makespan": report.makespan,
                "edits": report.edits_used,
            }
            rows.append({
                "workflow": workflow.name,
                "policy": policy.name,
                "quality": report.mean_quality,
                "completion": report.mean_completion,
                "gpu_time": report.gpu_hours,
                "quality_per_gpu": report.quality_per_gpu_hour,
                "makespan": report.makespan,
                "n_edits": sum(report.edits_used.values()),
            })
            print(
                f"  {policy.name:<14}  Q={report.mean_quality:.3f}  "
                f"T={report.mean_completion:.1f}  "
                f"Q/GPU={report.quality_per_gpu_hour:.4f}  "
                f"edits={sum(report.edits_used.values())}"
            )
    write_csv(output / "agentqo_runtime.csv", rows)
    write_json(output / "agentqo_runtime.json", summaries)
    print(f"\nWrote {output}")
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AgentQO runtime optimizer")
    parser.add_argument("--n-jobs", type=int, default=8)
    parser.add_argument("--n-gpus", type=int, default=2)
    parser.add_argument("--output-dir", type=str, default="data/agentqo")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    run_agentqo_experiment(
        n_jobs=args.n_jobs,
        n_gpus=args.n_gpus,
        output_dir=args.output_dir,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
