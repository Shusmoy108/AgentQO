"""
Epistemic Criticality labeling via fault injection.

For each node v of each task:
  1. Pin v correct, recompute only descendants, record quality Q+
  2. Pin v incorrect, recompute only descendants, record quality Q-
  3. consequence(v) = Q+ - Q-

Aggregate over tasks with a bootstrap CI. EC = E[consequence] * p_err.

H1 is the distribution of consequence across nodes. Labels used by H2/H3
are these measured quantities, never the simulator's hidden importance.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from tqdm import tqdm

from agentqo.backends.base import ModelBackend, NodeResult
from agentqo.database import AgentQODatabase
from agentqo.executor import (
    ExecutionOverrides,
    FidelityPlan,
    WorkflowExecutor,
)
from agentqo.simulator.task_model import TaskInstance, TaskModel
from agentqo.workflows.dag import NodeRole, Workflow

logger = logging.getLogger("agentqo.labeling")


@dataclass
class ECLabel:
    """Aggregated EC label for one node of one workflow."""

    node_id: str
    workflow_name: str
    num_samples: int
    consequence_mean: float
    consequence_std: float
    consequence_ci_low: float
    consequence_ci_high: float
    local_error_prob: float
    ec_score: float
    raw_qualities_correct: List[float] = field(default_factory=list)
    raw_qualities_incorrect: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload.pop("raw_qualities_correct", None)
        payload.pop("raw_qualities_incorrect", None)
        return payload


@dataclass
class NodeObservation:
    """One (task, node) sample for EC prediction.

    Features come from the *baseline* run (what a scheduler would see).
    The label is the measured fault-injection consequence for that task,
    plus the workflow-level p_err so EC = consequence * p_err can be
    attached after aggregation.
    """

    workflow_name: str
    node_id: str
    task_id: str
    consequence: float
    baseline_correct: bool
    confidence: float
    embedding: np.ndarray
    cost: float
    fidelity_used: str


@dataclass
class LabelingResult:
    """Full labeling output for one workflow."""

    workflow_name: str
    labels: Dict[str, ECLabel]
    observations: List[NodeObservation]
    num_tasks: int
    seed: int


def compute_bootstrap_ci(
    data: np.ndarray,
    confidence: float = 0.95,
    n_bootstrap: int = 1000,
    rng: Optional[np.random.Generator] = None,
) -> Tuple[float, float]:
    """Percentile bootstrap CI for the mean."""
    if rng is None:
        rng = np.random.default_rng()
    if len(data) == 0:
        return (0.0, 0.0)
    if len(data) == 1:
        return (float(data[0]), float(data[0]))

    idx = rng.integers(0, len(data), size=(n_bootstrap, len(data)))
    means = data[idx].mean(axis=1)
    alpha = 1.0 - confidence
    lower = float(np.percentile(means, 100 * alpha / 2))
    upper = float(np.percentile(means, 100 * (1 - alpha / 2)))
    return (lower, upper)


class ECLabeler:
    """Fault-inject every node, with descendant-only recompute."""

    def __init__(
        self,
        backend: ModelBackend,
        task_model: TaskModel,
        db: Optional[AgentQODatabase] = None,
    ) -> None:
        self.backend = backend
        self.task_model = task_model
        self.executor = WorkflowExecutor(backend, task_model)
        self.db = db

    def label_workflow(
        self,
        workflow: Workflow,
        num_tasks: int = 100,
        fidelity_plan: Optional[FidelityPlan] = None,
        base_seed: int = 42,
        use_partial_recompute: bool = True,
        show_progress: bool = True,
    ) -> LabelingResult:
        rng = np.random.default_rng(base_seed)
        node_ids = list(workflow.nodes.keys())
        qualities_correct: Dict[str, List[float]] = {nid: [] for nid in node_ids}
        qualities_incorrect: Dict[str, List[float]] = {nid: [] for nid in node_ids}
        error_counts: Dict[str, int] = {nid: 0 for nid in node_ids}
        observations: List[NodeObservation] = []

        task_iterator = range(num_tasks)
        if show_progress:
            task_iterator = tqdm(
                task_iterator, desc=f"Labeling {workflow.name}", leave=False
            )

        for _ in task_iterator:
            task_seed = int(rng.integers(0, 2**31))
            task = self.task_model.generate_task(
                workflow, np.random.default_rng(task_seed)
            )
            if self.db:
                self.db.save_task(task)

            baseline = self.executor.run_workflow(
                workflow=workflow,
                task=task,
                fidelity_plan=fidelity_plan,
                seed=task_seed,
            )
            if self.db:
                self.db.save_run(baseline)

            for node_id in node_ids:
                if node_id in baseline.node_results:
                    if not baseline.node_results[node_id].correctness:
                        error_counts[node_id] += 1

            per_node_consequence: Dict[str, float] = {}
            for node_id in node_ids:
                if node_id in baseline.skipped_nodes:
                    continue
                q_plus = self._forced_quality(
                    workflow, task, baseline.node_results, node_id, True,
                    fidelity_plan, task_seed + 1, use_partial_recompute,
                )
                q_minus = self._forced_quality(
                    workflow, task, baseline.node_results, node_id, False,
                    fidelity_plan, task_seed + 2, use_partial_recompute,
                )
                qualities_correct[node_id].append(q_plus)
                qualities_incorrect[node_id].append(q_minus)
                per_node_consequence[node_id] = q_plus - q_minus

            for node_id, consequence in per_node_consequence.items():
                result = baseline.node_results[node_id]
                observations.append(
                    NodeObservation(
                        workflow_name=workflow.name,
                        node_id=node_id,
                        task_id=task.task_id,
                        consequence=float(consequence),
                        baseline_correct=bool(result.correctness),
                        confidence=float(result.confidence),
                        embedding=np.array(result.embedding, copy=True),
                        cost=float(result.cost),
                        fidelity_used=result.fidelity_used,
                    )
                )

        labels = self._aggregate_labels(
            workflow, node_ids, qualities_correct, qualities_incorrect,
            error_counts, num_tasks, rng,
        )
        return LabelingResult(
            workflow_name=workflow.name,
            labels=labels,
            observations=observations,
            num_tasks=num_tasks,
            seed=base_seed,
        )

    def _forced_quality(
        self,
        workflow: Workflow,
        task: TaskInstance,
        baseline_results: Dict[str, NodeResult],
        node_id: str,
        forced: bool,
        fidelity_plan: Optional[FidelityPlan],
        seed: int,
        use_partial_recompute: bool,
    ) -> float:
        overrides = ExecutionOverrides(forced_correctness={node_id: forced})
        if use_partial_recompute:
            record = self.executor.run_with_partial_recompute(
                workflow=workflow,
                task=task,
                baseline_results=baseline_results,
                changed_nodes={node_id},
                overrides=overrides,
                fidelity_plan=fidelity_plan,
                seed=seed,
            )
        else:
            record = self.executor.run_workflow(
                workflow=workflow,
                task=task,
                fidelity_plan=fidelity_plan,
                overrides=overrides,
                seed=seed,
            )
        return float(record.final_quality)

    def _aggregate_labels(
        self,
        workflow: Workflow,
        node_ids: List[str],
        qualities_correct: Dict[str, List[float]],
        qualities_incorrect: Dict[str, List[float]],
        error_counts: Dict[str, int],
        num_tasks: int,
        rng: np.random.Generator,
    ) -> Dict[str, ECLabel]:
        labels: Dict[str, ECLabel] = {}
        for node_id in node_ids:
            q_correct = np.asarray(qualities_correct[node_id], dtype=np.float64)
            q_incorrect = np.asarray(qualities_incorrect[node_id], dtype=np.float64)
            if len(q_correct) == 0 or len(q_incorrect) == 0:
                labels[node_id] = ECLabel(
                    node_id=node_id,
                    workflow_name=workflow.name,
                    num_samples=0,
                    consequence_mean=0.0,
                    consequence_std=0.0,
                    consequence_ci_low=0.0,
                    consequence_ci_high=0.0,
                    local_error_prob=0.0,
                    ec_score=0.0,
                )
                continue

            consequences = q_correct - q_incorrect
            consequence_mean = float(np.mean(consequences))
            consequence_std = float(np.std(consequences))
            ci_low, ci_high = compute_bootstrap_ci(consequences, rng=rng)
            local_error_prob = error_counts[node_id] / max(num_tasks, 1)
            ec_score = consequence_mean * local_error_prob
            labels[node_id] = ECLabel(
                node_id=node_id,
                workflow_name=workflow.name,
                num_samples=len(q_correct),
                consequence_mean=consequence_mean,
                consequence_std=consequence_std,
                consequence_ci_low=ci_low,
                consequence_ci_high=ci_high,
                local_error_prob=local_error_prob,
                ec_score=ec_score,
                raw_qualities_correct=list(q_correct),
                raw_qualities_incorrect=list(q_incorrect),
            )
            if self.db:
                self.db.save_ec_label(
                    workflow_name=workflow.name,
                    node_id=node_id,
                    num_samples=len(q_correct),
                    consequence_mean=consequence_mean,
                    consequence_std=consequence_std,
                    consequence_ci_low=ci_low,
                    consequence_ci_high=ci_high,
                    local_error_prob=local_error_prob,
                    ec_score=ec_score,
                )
        return labels

    def label_multiple_workflows(
        self,
        workflows: List[Workflow],
        num_tasks_per_workflow: int = 100,
        fidelity_plan: Optional[FidelityPlan] = None,
        base_seed: int = 42,
        show_progress: bool = True,
    ) -> Dict[str, LabelingResult]:
        results: Dict[str, LabelingResult] = {}
        for i, workflow in enumerate(workflows):
            logger.info("Labeling workflow %s (%d/%d)", workflow.name, i + 1, len(workflows))
            results[workflow.name] = self.label_workflow(
                workflow=workflow,
                num_tasks=num_tasks_per_workflow,
                fidelity_plan=fidelity_plan,
                base_seed=base_seed + i * 10_000,
                show_progress=show_progress,
            )
        return results


def analyze_h1_results(
    labels: Dict[str, ECLabel],
    workflow: Workflow,
) -> Dict[str, Any]:
    """Does consequence vary across nodes? That is H1."""
    node_data = []
    consequences = []
    for node_id, label in labels.items():
        if label.num_samples <= 0:
            continue
        node = workflow.nodes[node_id]
        consequences.append(label.consequence_mean)
        node_data.append({
            "node_id": node_id,
            "consequence": label.consequence_mean,
            "consequence_ci": (label.consequence_ci_low, label.consequence_ci_high),
            "ec_score": label.ec_score,
            "p_err": label.local_error_prob,
            "role": node.role.value,
            "depth": workflow.get_depth(node_id),
            "fan_out": workflow.get_fan_out(node_id),
            "downstream_reach": workflow.get_downstream_reach(node_id),
            "has_downstream_verifier": workflow.has_downstream_verifier(node_id),
            "optional": node.optional,
            "speculative": node.speculative,
        })

    if not consequences:
        return {"h1_holds": False, "reason": "no labeled nodes", "statistics": {}}

    consequences_arr = np.asarray(consequences, dtype=np.float64)
    mean = float(np.mean(consequences_arr))
    stats = {
        "mean": mean,
        "std": float(np.std(consequences_arr)),
        "min": float(np.min(consequences_arr)),
        "max": float(np.max(consequences_arr)),
        "range": float(np.max(consequences_arr) - np.min(consequences_arr)),
        "cv": float(np.std(consequences_arr) / mean) if mean > 0 else 0.0,
    }

    correlations = {"depth": 0.0, "fan_out": 0.0, "downstream_reach": 0.0}
    if len(node_data) > 3:
        for key in correlations:
            xs = np.asarray([d[key] for d in node_data], dtype=np.float64)
            if np.std(xs) > 0 and np.std(consequences_arr) > 0:
                corr = float(np.corrcoef(consequences_arr, xs)[0, 1])
                correlations[key] = 0.0 if np.isnan(corr) else corr

    h1_holds = stats["range"] > 0.1 and stats["cv"] > 0.2
    ranked = sorted(node_data, key=lambda x: x["consequence"], reverse=True)

    smoke = _h1_smoke_test(labels, workflow)

    n = len(ranked)
    k_high = min(3, n)
    k_low = min(3, max(0, n - k_high))
    return {
        "workflow_name": workflow.name,
        "statistics": stats,
        "correlations": correlations,
        "h1_holds": h1_holds and smoke["passed"],
        "h1_evidence": {
            "range_threshold": 0.1,
            "range_actual": stats["range"],
            "cv_threshold": 0.2,
            "cv_actual": stats["cv"],
        },
        "smoke_test": smoke,
        "node_ranking": ranked,
        "high_criticality_nodes": [n["node_id"] for n in ranked[:k_high]],
        "low_criticality_nodes": [n["node_id"] for n in ranked[-k_low:]] if k_low else [],
    }


def _h1_smoke_test(
    labels: Dict[str, ECLabel],
    workflow: Workflow,
) -> Dict[str, Any]:
    """Corrupting a planner/aggregator should hurt more than a formatter."""
    by_role: Dict[str, List[float]] = {}
    for node_id, label in labels.items():
        if label.num_samples <= 0:
            continue
        role = workflow.nodes[node_id].role.value
        by_role.setdefault(role, []).append(label.consequence_mean)

    def _mean(role: str) -> Optional[float]:
        vals = by_role.get(role)
        return float(np.mean(vals)) if vals else None

    planner = _mean(NodeRole.PLANNER.value)
    formatter = _mean(NodeRole.FORMATTER.value)
    verifier = _mean(NodeRole.VERIFIER.value)
    critical = planner
    if critical is None:
        critical = _mean(NodeRole.AGGREGATOR.value)

    passed = True
    notes = []
    if critical is not None and formatter is not None:
        passed = critical > formatter + 0.02
        notes.append(
            f"critical={critical:.3f} vs formatter={formatter:.3f}"
        )
    elif critical is not None and verifier is not None:
        # No formatter on this DAG: verifier should be below the planner.
        passed = critical >= verifier - 0.02
        notes.append(f"critical={critical:.3f} vs verifier={verifier:.3f}")
    else:
        notes.append("insufficient roles for smoke test; skipped")

    return {
        "passed": passed,
        "planner_consequence": planner,
        "formatter_consequence": formatter,
        "verifier_consequence": verifier,
        "notes": notes,
    }
