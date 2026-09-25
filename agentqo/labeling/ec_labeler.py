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
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from zlib import crc32

import numpy as np
from tqdm import tqdm

from agentqo.backends.base import ModelBackend, NodeResult
from agentqo.database import AgentQODatabase
from agentqo.backends.vllm_http import _output_as_text
from agentqo.executor import (
    ExecutionOverrides,
    FidelityPlan,
    RunRecord,
    WorkflowExecutor,
    verify_partial_recompute_invariant,
)
from agentqo.labeling.corruptions import CorruptionMaker, rewrite_prompt
from agentqo.labeling.p_err import estimate_p_err
from agentqo.tasks.real_task_model import answer_node
from agentqo.simulator.task_model import TaskInstance, TaskModel
from agentqo.workflows.dag import LARGE_FIDELITY, SMALL_FIDELITY, NodeRole, Workflow

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
    # Substitute mode only: per (task, node) substitution chains and per-task traces.
    records: List[Dict[str, Any]] = field(default_factory=list)
    traces: List[Dict[str, Any]] = field(default_factory=list)


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
    """Fault-inject every node, with descendant-only recompute.

    ``mode="flag"`` pins a correctness bit (simulator only: with a real LLM
    descendants would still read the same text). ``mode="substitute"``
    replaces the node's *output text* with a reference (good side) or with
    corruptions (bad side) and recomputes descendants on that text.
    """

    def __init__(
        self,
        backend: ModelBackend,
        task_model: TaskModel,
        db: Optional[AgentQODatabase] = None,
        mode: str = "flag",
        n_corruptions: int = 3,
        k_samples: int = 5,
        max_workers: int = 32,
    ) -> None:
        from agentqo.simulator.task_model import MockBackend

        if mode not in ("flag", "substitute"):
            raise ValueError(f"mode must be 'flag' or 'substitute', got {mode}")
        if mode == "flag" and not isinstance(backend, MockBackend):
            raise ValueError(
                "flag mode only changes a correctness bit, so with a real backend descendants "
                "still see the same text; use mode='substitute'"
            )
        self.backend = backend
        self.task_model = task_model
        self.executor = WorkflowExecutor(backend, task_model)
        self.db = db
        self.mode = mode
        self.n_corruptions = n_corruptions
        self.k_samples = k_samples
        self.max_workers = max_workers

    def label_workflow(
        self,
        workflow: Workflow,
        num_tasks: int = 100,
        fidelity_plan: Optional[FidelityPlan] = None,
        base_seed: int = 42,
        use_partial_recompute: bool = True,
        show_progress: bool = True,
    ) -> LabelingResult:
        if self.mode == "substitute":
            return self._label_substitute(workflow, num_tasks, fidelity_plan, base_seed, show_progress)
        # Mix the workflow name into the seed. With a bare base_seed, every
        # workflow saw the same task seeds, so task i (difficulty, RNG stream,
        # embedding noise) was shared across workflows and leaked across
        # leave-one-workflow-out folds.
        rng = np.random.default_rng([base_seed, crc32(workflow.name.encode())])
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

    def _label_substitute(
        self,
        workflow: Workflow,
        num_tasks: int,
        fidelity_plan: Optional[FidelityPlan],
        base_seed: int,
        show_progress: bool,
    ) -> LabelingResult:
        """Two phases on a thread pool: all baselines, then per-task labeling.

        Baselines come first so "swap from another task" donors are fixed
        regardless of thread timing. Within a task, work is sequential.
        """
        rng = np.random.default_rng([base_seed, crc32(workflow.name.encode())])
        tasks = [
            self.task_model.generate_task(workflow, np.random.default_rng(int(rng.integers(0, 2**31))))
            for _ in range(num_tasks)
        ]
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            baselines = list(pool.map(
                lambda t: self.executor.run_workflow(workflow, t, fidelity_plan=fidelity_plan, seed=0),
                tasks,
            ))
            jobs = pool.map(
                lambda i: self._label_task_substitute(workflow, tasks, baselines, i, fidelity_plan),
                range(num_tasks),
            )
            if show_progress:
                jobs = tqdm(jobs, total=num_tasks, desc=f"Labeling {workflow.name}", leave=False)
            per_task = list(jobs)

        node_ids = list(workflow.nodes.keys())
        q_plus: Dict[str, List[float]] = {nid: [] for nid in node_ids}
        q_minus: Dict[str, List[float]] = {nid: [] for nid in node_ids}
        p_err_sum: Dict[str, float] = {nid: 0.0 for nid in node_ids}
        observations: List[NodeObservation] = []
        records: List[Dict[str, Any]] = []
        traces: List[Dict[str, Any]] = []
        for task, base, out in zip(tasks, baselines, per_task):
            traces.append(out["trace"])
            for rec in out["records"]:
                nid = rec["node_id"]
                q_plus[nid].append(rec["q_plus"])
                q_minus[nid].append(rec["q_minus"])
                p_err_sum[nid] += rec["p_err"]
                result = base.node_results[nid]
                observations.append(NodeObservation(
                    workflow_name=workflow.name,
                    node_id=nid,
                    task_id=task.task_id,
                    consequence=rec["consequence"],
                    baseline_correct=rec["baseline_agrees"],
                    confidence=float(result.confidence),
                    embedding=np.array(result.embedding, copy=True),
                    cost=float(result.cost),
                    fidelity_used=result.fidelity_used,
                ))
                records.append(rec)
        labels = self._aggregate_labels(
            workflow, node_ids, q_plus, q_minus, p_err_sum, num_tasks, rng,
        )
        return LabelingResult(
            workflow_name=workflow.name,
            labels=labels,
            observations=observations,
            num_tasks=num_tasks,
            seed=base_seed,
            records=records,
            traces=traces,
        )

    def _label_task_substitute(
        self,
        workflow: Workflow,
        tasks: List[TaskInstance],
        baselines: List[RunRecord],
        i: int,
        fidelity_plan: Optional[FidelityPlan],
    ) -> Dict[str, Any]:
        task, base = tasks[i], baselines[i]
        extract = self.task_model.extract

        def run_node(nid: str, fidelity, **extra) -> NodeResult:
            node = workflow.nodes[nid]
            inputs = {x: base.node_results[x] for x in node.inputs if x in base.node_results}
            ctx = {"task": task, "workflow": workflow, "results": base.node_results, **extra}
            return self.backend.execute_node(node, inputs, fidelity, ctx)

        def substituted(nid: str, output: Any) -> RunRecord:
            return self.executor.run_with_partial_recompute(
                workflow, task, base.node_results, {nid},
                ExecutionOverrides(force_outputs={nid: output}),
                fidelity_plan=fidelity_plan, seed=0,
            )

        def final_key(rec: RunRecord) -> Optional[str]:
            a = answer_node(workflow, rec.node_results)
            return extract(_output_as_text(rec.node_results[a].output)) if a else None

        def descendants_text(nid: str, rec: RunRecord) -> Dict[str, str]:
            return {d: _output_as_text(rec.node_results[d].output)
                    for d in workflow.get_descendants(nid) if d in rec.node_results}

        def donor(nid: str, c: int) -> Optional[str]:
            j = (i + 1 + c) % len(baselines)
            res = baselines[j].node_results.get(nid) if j != i else None
            return _output_as_text(res.output) if res is not None else None

        records = []
        for nid in workflow.topological_order:
            if nid not in base.node_results:
                continue
            role = workflow.nodes[nid].role
            reference = run_node(nid, LARGE_FIDELITY, temperature=0.0)
            ref_text = _output_as_text(reference.output)
            plus = substituted(nid, reference)
            ref_final = final_key(plus)

            def sample(temp: float, idx: int, nid=nid) -> NodeResult:
                return run_node(nid, SMALL_FIDELITY, temperature=temp, sample_index=idx)

            def rewrite(text: str, c: int, nid=nid) -> str:
                return _output_as_text(run_node(
                    nid, SMALL_FIDELITY, temperature=0.7, sample_index=2000 + c,
                    prompt_fn=lambda *_: rewrite_prompt(text), code_fn=lambda *_: None,
                ).output)

            maker = CorruptionMaker(extract, sample, lambda c, nid=nid: donor(nid, c), rewrite)
            corruptions = maker.make(role, ref_text, self.n_corruptions)
            minus_runs = [substituted(nid, c.text) for c in corruptions]
            q_p = float(plus.final_quality)
            q_m = float(np.mean([r.final_quality for r in minus_runs]))

            ref_key = None if role == NodeRole.PLANNER else extract(ref_text)
            p = estimate_p_err(
                keyed=ref_key is not None,
                k=self.k_samples,
                sample_key=lambda idx: extract(_output_as_text(sample(0.7, idx).output)),
                sample_final_key=lambda idx: final_key(substituted(nid, sample(0.7, idx))),
                reference_key=ref_key,
                reference_final_key=ref_final,
            )
            base_text = _output_as_text(base.node_results[nid].output)
            agrees = (extract(base_text) == ref_key) if ref_key is not None else (final_key(base) == ref_final)
            violations = []
            for rec in [plus, *minus_runs]:
                violations += verify_partial_recompute_invariant(base, rec, {nid}, workflow)[1]
            records.append({
                "task_id": task.task_id,
                "node_id": nid,
                "role": role.value,
                "reference": ref_text,
                "reference_key": ref_key,
                "final_key_plus": ref_final,
                "q_plus": q_p,
                "q_minus": q_m,
                "consequence": q_p - q_m,
                "p_err": p,
                "baseline_agrees": bool(agrees),
                "descendants_plus": descendants_text(nid, plus),
                "corruptions": [
                    {**c.to_dict(), "quality": float(r.final_quality), "final_key": final_key(r),
                     "final_differs": final_key(r) != ref_final, "descendants": descendants_text(nid, r)}
                    for c, r in zip(corruptions, minus_runs)
                ],
                "invariant_violations": violations,
            })
        trace = {
            "task_id": task.task_id,
            "gold": task.ground_truth,
            "problem": task.metadata.get("problem"),
            "final_quality": float(base.final_quality),
            "final_key": final_key(base),
            "nodes": {
                nid: {
                    "prompt": r.metadata.get("prompt"),
                    "output": _output_as_text(r.output),
                    "key": extract(_output_as_text(r.output)),
                    "confidence": r.confidence,
                    "fidelity": r.fidelity_used,
                    **{k: r.metadata.get(k) for k in
                       ("prompt_tokens", "completion_tokens", "latency_s", "cache_hit", "code_node")},
                }
                for nid, r in base.node_results.items()
            },
        }
        return {"records": records, "trace": trace}

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
