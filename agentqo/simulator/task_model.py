"""
Quality channel and MockBackend.

The quality channel is the reason this simulator can test epistemic
criticality. It maps a vector of node correctness bits to a final task
quality, with three properties the proposal requires:

1. Quality degrades when important nodes fail, and importance differs
   across nodes. H1 is then a measurement, not an assumption.
2. Importance correlates with structure (role, fan-out, reach) *plus
   independent noise*. Structure is therefore a real but incomplete
   predictor of EC — the gap embeddings are supposed to close.
3. Confidence tracks *local* correctness, not downstream criticality.
   A low-confidence formatter is not a high-EC node. That gap is what
   AgentQO exploits.

EC labels are produced by fault injection (see ``labeling.ec_labeler``),
never by reading ``task.node_importance`` at evaluation time.
"""

from __future__ import annotations

import abc
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, TYPE_CHECKING

import numpy as np

from agentqo.backends.base import NodeResult
from agentqo.workflows.dag import NodeRole

if TYPE_CHECKING:
    from agentqo.workflows.dag import Fidelity, NodeSpec, Workflow

logger = logging.getLogger("agentqo.simulator")


@dataclass
class TaskInstance:
    """A single task instance with hidden properties.

    ``node_importance`` and ``node_difficulties`` are *simulator internals*.
    Predictors and policies must not read them; they exist so the quality
    channel can be non-circular and so embeddings can carry a recoverable
    signal that confidence does not.
    """

    task_id: str
    task_type: str
    difficulty: float
    node_difficulties: Dict[str, float]
    node_importance: Dict[str, float]
    ground_truth: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskModel(abc.ABC):
    """Ground-truth mapping from node correctness to final task quality."""

    @abc.abstractmethod
    def generate_task(
        self,
        workflow: "Workflow",
        rng: np.random.Generator,
    ) -> TaskInstance:
        """Generate a task instance for the given workflow."""

    @abc.abstractmethod
    def compute_quality(
        self,
        task: TaskInstance,
        node_results: Dict[str, NodeResult],
        workflow: "Workflow",
    ) -> float:
        """Compute final task quality given node results. Range [0, 1]."""

    @abc.abstractmethod
    def compute_node_error_prob(
        self,
        node: "NodeSpec",
        fidelity: "Fidelity",
        task: TaskInstance,
        input_results: Dict[str, NodeResult],
    ) -> float:
        """P(error) for a node given fidelity, hidden difficulty, and inputs."""


def _role_factor(role: NodeRole) -> float:
    """Structural role prior. Formatters are almost irrelevant by construction."""
    return {
        NodeRole.PLANNER: 1.6,
        NodeRole.RESEARCHER: 1.0,
        NodeRole.AGGREGATOR: 1.35,
        NodeRole.VERIFIER: 0.55,
        NodeRole.SAMPLER: 0.9,
        NodeRole.FORMATTER: 0.08,
    }.get(role, 1.0)


def _hidden_importance(
    workflow: "Workflow",
    rng: np.random.Generator,
    importance_noise: float,
) -> Dict[str, float]:
    """Importance = structure × role × log-normal noise, then L1-normalized.

    The noise term is the whole point: a structure-only predictor should
    do well but not perfectly. Embeddings that carry this hidden residual
    can beat structure.
    """
    n = max(len(workflow.nodes), 1)
    raw: Dict[str, float] = {}
    for node_id, node in workflow.nodes.items():
        reach = workflow.get_downstream_reach(node_id)
        fan_out = workflow.get_fan_out(node_id)
        structural = (reach + 0.5 * fan_out + 1.0) / n
        noise = float(np.exp(rng.normal(0.0, importance_noise)))
        value = structural * _role_factor(node.role) * noise
        if node.role == NodeRole.FORMATTER:
            value = min(value, 0.03)
        if node.optional:
            value *= 0.7
        raw[node_id] = max(value, 1e-6)
    total = sum(raw.values())
    return {k: v / total for k, v in raw.items()}


def _clip_prob(p: float) -> float:
    return float(np.clip(p, 0.0, 0.99))


def _correctness_map(
    node_results: Dict[str, NodeResult],
) -> Dict[str, bool]:
    return {nid: res.correctness for nid, res in node_results.items()}


def _ancestor_survival(
    workflow: "Workflow",
    node_id: str,
    correctness: Dict[str, bool],
    importance: Dict[str, float],
    propagation: float,
) -> float:
    """How much of this node's contribution survives upstream errors.

    An incorrect, high-importance ancestor suppresses descendants. An
    incorrect formatter barely does. This is the mechanistic source of
    heterogeneous consequence.
    """
    survival = 1.0
    for anc in workflow.get_ancestors(node_id):
        if anc in correctness and not correctness[anc]:
            survival *= 1.0 - propagation * importance.get(anc, 0.0)
    return float(np.clip(survival, 0.0, 1.0))


class MathReasoningTaskModel(TaskModel):
    """Sequential math reasoning (GSM8K-style).

    Later steps depend on earlier ones. Planner errors propagate far;
    formatter errors (if present) do not.
    """

    def __init__(
        self,
        base_difficulty: float = 0.5,
        difficulty_variance: float = 0.2,
        propagation_factor: float = 0.85,
        verifier_catch_prob: float = 0.55,
        importance_noise: float = 0.45,
    ) -> None:
        self.base_difficulty = base_difficulty
        self.difficulty_variance = difficulty_variance
        self.propagation_factor = propagation_factor
        self.verifier_catch_prob = verifier_catch_prob
        self.importance_noise = importance_noise

    def generate_task(
        self,
        workflow: "Workflow",
        rng: np.random.Generator,
    ) -> TaskInstance:
        difficulty = float(np.clip(
            rng.normal(self.base_difficulty, self.difficulty_variance),
            0.1, 0.9,
        ))
        max_depth = max(workflow.get_depth(nid) for nid in workflow.nodes) or 1
        node_difficulties = {}
        for node_id in workflow.topological_order:
            depth_factor = (workflow.get_depth(node_id) / max_depth) * 0.25
            node_difficulties[node_id] = float(np.clip(
                difficulty + depth_factor + rng.normal(0, 0.1),
                0.05, 0.95,
            ))
        return TaskInstance(
            task_id=f"math_{int(rng.integers(0, 2**31))}",
            task_type="math_reasoning",
            difficulty=difficulty,
            node_difficulties=node_difficulties,
            node_importance=_hidden_importance(
                workflow, rng, self.importance_noise
            ),
            ground_truth=int(rng.integers(0, 1000)),
            metadata={"propagation_factor": self.propagation_factor},
        )

    def compute_quality(
        self,
        task: TaskInstance,
        node_results: Dict[str, NodeResult],
        workflow: "Workflow",
    ) -> float:
        required = [nid for nid, n in workflow.nodes.items() if not n.optional]
        if not all(nid in node_results for nid in required):
            return 0.0

        correctness = _correctness_map(node_results)
        weighted = 0.0
        for node_id in workflow.topological_order:
            if node_id not in correctness:
                continue
            w = task.node_importance.get(node_id, 0.0)
            if workflow.nodes[node_id].role == NodeRole.FORMATTER:
                w = min(w, 0.02)
            survival = _ancestor_survival(
                workflow, node_id, correctness, task.node_importance,
                self.propagation_factor,
            )
            if correctness[node_id]:
                weighted += w * survival

        # A correct verifier recovers a fraction of lost quality.
        for node_id, node in workflow.nodes.items():
            if node.role != NodeRole.VERIFIER or node_id not in correctness:
                continue
            if correctness[node_id]:
                weighted = min(1.0, weighted + 0.12 * self.verifier_catch_prob)
        return float(np.clip(weighted, 0.0, 1.0))

    def compute_node_error_prob(
        self,
        node: "NodeSpec",
        fidelity: "Fidelity",
        task: TaskInstance,
        input_results: Dict[str, NodeResult],
    ) -> float:
        node_diff = task.node_difficulties.get(node.node_id, task.difficulty)
        difficulty_factor = 0.5 + node_diff
        input_factor = 1.0
        for inp_id in node.inputs:
            if inp_id in input_results and not input_results[inp_id].correctness:
                input_factor *= 1.0 + self.propagation_factor
        return _clip_prob(
            fidelity.base_error_rate * difficulty_factor * input_factor
        )


class MultiHopQATaskModel(TaskModel):
    """Parallel evidence gathering (HotpotQA-style).

    Quality needs a planner that asks the right questions, enough correct
    evidence, and an aggregator that can synthesize. Individual researchers
    are partially redundant, so one researcher's EC is lower than the
    planner's — the fan-out pattern the proposal cares about.
    """

    def __init__(
        self,
        base_difficulty: float = 0.5,
        difficulty_variance: float = 0.2,
        min_evidence_ratio: float = 0.5,
        importance_noise: float = 0.45,
        propagation_factor: float = 0.7,
    ) -> None:
        self.base_difficulty = base_difficulty
        self.difficulty_variance = difficulty_variance
        self.min_evidence_ratio = min_evidence_ratio
        self.importance_noise = importance_noise
        self.propagation_factor = propagation_factor

    def generate_task(
        self,
        workflow: "Workflow",
        rng: np.random.Generator,
    ) -> TaskInstance:
        difficulty = float(np.clip(
            rng.normal(self.base_difficulty, self.difficulty_variance),
            0.1, 0.9,
        ))
        node_difficulties = {
            node_id: float(np.clip(difficulty + rng.normal(0, 0.15), 0.05, 0.95))
            for node_id in workflow.topological_order
        }
        return TaskInstance(
            task_id=f"qa_{int(rng.integers(0, 2**31))}",
            task_type="multihop_qa",
            difficulty=difficulty,
            node_difficulties=node_difficulties,
            node_importance=_hidden_importance(
                workflow, rng, self.importance_noise
            ),
            ground_truth="placeholder_answer",
            metadata={"min_evidence_ratio": self.min_evidence_ratio},
        )

    def compute_quality(
        self,
        task: TaskInstance,
        node_results: Dict[str, NodeResult],
        workflow: "Workflow",
    ) -> float:
        required = [nid for nid, n in workflow.nodes.items() if not n.optional]
        if not all(nid in node_results for nid in required):
            return 0.0

        correctness = _correctness_map(node_results)
        planners = [
            nid for nid, n in workflow.nodes.items()
            if n.role == NodeRole.PLANNER
        ]
        researchers = [
            nid for nid, n in workflow.nodes.items()
            if n.role == NodeRole.RESEARCHER
        ]
        aggregators = [
            nid for nid, n in workflow.nodes.items()
            if n.role == NodeRole.AGGREGATOR
        ]

        planner_ok = all(correctness.get(p, False) for p in planners) if planners else True
        evidence_ratio = (
            sum(1 for r in researchers if correctness.get(r, False)) / len(researchers)
            if researchers else 1.0
        )
        agg_ok = all(correctness.get(a, False) for a in aggregators) if aggregators else True

        if not planner_ok:
            quality = 0.15 * evidence_ratio
        elif evidence_ratio < self.min_evidence_ratio:
            quality = 0.25 * evidence_ratio
        elif not agg_ok:
            quality = 0.45 * evidence_ratio
        else:
            quality = 0.55 + 0.35 * evidence_ratio

        # Residual from hidden importance so H1 is not *only* the discrete
        # evidence rule (structure-only would then be a perfect predictor).
        residual = 0.0
        for node_id, ok in correctness.items():
            if ok:
                residual += 0.15 * task.node_importance.get(node_id, 0.0)
        quality = 0.85 * quality + residual

        for node_id, node in workflow.nodes.items():
            if node.role == NodeRole.VERIFIER and correctness.get(node_id, False):
                quality = min(1.0, quality + 0.08)
            if node.role == NodeRole.FORMATTER:
                # Formatter correctness is almost irrelevant.
                pass
        return float(np.clip(quality, 0.0, 1.0))

    def compute_node_error_prob(
        self,
        node: "NodeSpec",
        fidelity: "Fidelity",
        task: TaskInstance,
        input_results: Dict[str, NodeResult],
    ) -> float:
        node_diff = task.node_difficulties.get(node.node_id, task.difficulty)
        error_prob = fidelity.base_error_rate * (0.5 + node_diff)
        if node.role == NodeRole.AGGREGATOR:
            n_bad = sum(
                1 for inp in node.inputs
                if inp in input_results and not input_results[inp].correctness
            )
            if n_bad:
                error_prob *= 1.0 + 0.3 * n_bad
        return _clip_prob(error_prob)


class SelfConsistencyTaskModel(TaskModel):
    """Speculative sampling with any-correct group semantics.

    One more branch has diminishing returns. That is the allocation signal:
    the first sampler is high-EC; the k-th is not.
    """

    def __init__(
        self,
        base_difficulty: float = 0.5,
        difficulty_variance: float = 0.2,
        importance_noise: float = 0.4,
        saturation: float = 0.45,
    ) -> None:
        self.base_difficulty = base_difficulty
        self.difficulty_variance = difficulty_variance
        self.importance_noise = importance_noise
        self.saturation = saturation

    def generate_task(
        self,
        workflow: "Workflow",
        rng: np.random.Generator,
    ) -> TaskInstance:
        difficulty = float(np.clip(
            rng.normal(self.base_difficulty, self.difficulty_variance),
            0.1, 0.9,
        ))
        node_difficulties = {
            nid: float(np.clip(difficulty + rng.normal(0, 0.12), 0.05, 0.95))
            for nid in workflow.topological_order
        }
        return TaskInstance(
            task_id=f"sc_{int(rng.integers(0, 2**31))}",
            task_type="self_consistency",
            difficulty=difficulty,
            node_difficulties=node_difficulties,
            node_importance=_hidden_importance(
                workflow, rng, self.importance_noise
            ),
            ground_truth=int(rng.integers(0, 1000)),
            metadata={"saturation": self.saturation},
        )

    def compute_quality(
        self,
        task: TaskInstance,
        node_results: Dict[str, NodeResult],
        workflow: "Workflow",
    ) -> float:
        required = [nid for nid, n in workflow.nodes.items() if not n.optional]
        if not all(nid in node_results for nid in required):
            return 0.0

        correctness = _correctness_map(node_results)
        groups = workflow.get_speculative_groups()
        group_value = 0.0
        n_groups = max(len(groups), 1)
        for node_ids in groups.values():
            n_correct = sum(1 for nid in node_ids if correctness.get(nid, False))
            # 1 - (1-p)^k saturates: first correct branch is worth a lot.
            group_value += 1.0 - (1.0 - self.saturation) ** n_correct
        group_value /= n_groups

        encoder_ids = [
            nid for nid, n in workflow.nodes.items()
            if n.role == NodeRole.PLANNER
        ]
        encoder_ok = all(correctness.get(e, False) for e in encoder_ids) if encoder_ids else True
        agg_ids = [
            nid for nid, n in workflow.nodes.items()
            if n.role == NodeRole.AGGREGATOR
        ]
        agg_ok = all(correctness.get(a, False) for a in agg_ids) if agg_ids else True

        if not encoder_ok:
            quality = 0.2 * group_value
        else:
            quality = 0.15 + 0.65 * group_value + 0.2 * (1.0 if agg_ok else 0.0)

        residual = sum(
            0.05 * task.node_importance.get(nid, 0.0)
            for nid, ok in correctness.items() if ok
        )
        return float(np.clip(0.95 * quality + residual, 0.0, 1.0))

    def compute_node_error_prob(
        self,
        node: "NodeSpec",
        fidelity: "Fidelity",
        task: TaskInstance,
        input_results: Dict[str, NodeResult],
    ) -> float:
        node_diff = task.node_difficulties.get(node.node_id, task.difficulty)
        error_prob = fidelity.base_error_rate * (0.5 + node_diff)
        if node.role == NodeRole.AGGREGATOR:
            n_ok = sum(
                1 for inp in node.inputs
                if inp in input_results and input_results[inp].correctness
            )
            # Aggregator is easier when at least one branch is good.
            if n_ok == 0:
                error_prob = min(0.99, error_prob * 1.5)
            else:
                error_prob *= 0.7
        return _clip_prob(error_prob)


class MockBackend:
    """Simulated backend with a recycled embedding that carries hidden EC.

    Design (matches the implementation plan):
    - Correctness is sampled from the quality channel.
    - Confidence is a noisy readout of *local* correctness. It is not EC.
    - The embedding encodes hidden importance and difficulty, plus noise.
      It does *not* encode DAG structure: that is already a feature view.
      A predictor that sees structure + embedding can recover the residual
      importance signal; confidence cannot.
    """

    def __init__(
        self,
        task_model: TaskModel,
        embedding_dim: int = 256,
        confidence_noise: float = 0.15,
        embedding_signal_strength: float = 0.7,
        embedding_signal: str = "hidden",
    ) -> None:
        """``embedding_signal="none"`` emits pure-noise embeddings: the WP0.4
        circularity check that H2's embedding gain is not free."""
        if embedding_dim < 48:
            raise ValueError("embedding_dim must be >= 48 to hold EC signals")
        if embedding_signal not in ("hidden", "none"):
            raise ValueError(f"embedding_signal must be 'hidden' or 'none', got {embedding_signal}")
        self.embedding_signal = embedding_signal
        self.task_model = task_model
        self._embedding_dim = embedding_dim
        self.confidence_noise = confidence_noise
        self.embedding_signal_strength = embedding_signal_strength

    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim

    def execute_node(
        self,
        node: "NodeSpec",
        inputs: Dict[str, NodeResult],
        fidelity: "Fidelity",
        task_context: Dict[str, Any],
        rng: Optional[np.random.Generator] = None,
    ) -> NodeResult:
        if rng is None:
            rng = np.random.default_rng()

        task: TaskInstance = task_context["task"]
        workflow: "Workflow" = task_context["workflow"]

        error_prob = self.task_model.compute_node_error_prob(
            node, fidelity, task, inputs
        )
        correctness = bool(rng.random() > error_prob)

        # Confidence tracks local correctness, *not* downstream importance.
        if correctness:
            base_confidence = 0.72 + 0.18 * rng.random()
        else:
            base_confidence = 0.22 + 0.28 * rng.random()
        confidence = float(np.clip(
            base_confidence + rng.normal(0, self.confidence_noise),
            0.01, 0.99,
        ))

        embedding = self._generate_embedding(node, task, correctness, rng)
        cost = float(fidelity.cost * (0.92 + 0.16 * rng.random()))

        return NodeResult(
            node_id=node.node_id,
            output={
                "node_id": node.node_id,
                "correctness": correctness,
                "simulated": True,
            },
            correctness=correctness,
            confidence=confidence,
            embedding=embedding,
            cost=cost,
            fidelity_used=fidelity.name,
            metadata={
                "error_prob": error_prob,
                "task_id": task.task_id,
                "model_id": fidelity.model_id,
                "num_gpus": fidelity.num_gpus,
            },
        )

    def _generate_embedding(
        self,
        node: "NodeSpec",
        task: TaskInstance,
        correctness: bool,
        rng: np.random.Generator,
    ) -> np.ndarray:
        embedding = rng.standard_normal(self._embedding_dim).astype(np.float32)
        if self.embedding_signal == "none":
            return embedding / float(np.linalg.norm(embedding) + 1e-8)
        importance = task.node_importance.get(node.node_id, 0.5)
        difficulty = task.node_difficulties.get(node.node_id, 0.5)
        s = self.embedding_signal_strength

        # Hidden EC residual — this is the signal TRAIL-style recycling
        # is supposed to recover. Deliberately *not* DAG structure.
        embedding[0:16] = s * importance + (1 - s) * embedding[0:16]
        embedding[16:32] = s * difficulty + (1 - s) * embedding[16:32]
        # Weak local-correctness cue, weaker than the confidence scalar.
        embedding[32:40] = (
            0.25 * (1.0 if correctness else 0.0) + 0.75 * embedding[32:40]
        )
        norm = float(np.linalg.norm(embedding) + 1e-8)
        return embedding / norm

    def get_info(self) -> Dict[str, Any]:
        return {
            "backend_type": "mock",
            "task_model": type(self.task_model).__name__,
            "embedding_dim": self._embedding_dim,
            "confidence_noise": self.confidence_noise,
            "embedding_signal_strength": self.embedding_signal_strength,
            "embedding_signal": self.embedding_signal,
        }


def compute_speculative_group_correctness(
    group_id: str,
    node_results: Dict[str, NodeResult],
    workflow: "Workflow",
) -> bool:
    """A speculative group is correct if ANY branch is correct."""
    groups = workflow.get_speculative_groups()
    if group_id not in groups:
        raise ValueError(f"Unknown speculative group: {group_id}")
    return any(
        nid in node_results and node_results[nid].correctness
        for nid in groups[group_id]
    )


def task_model_for_workflow(workflow: "Workflow") -> TaskModel:
    """Pick the quality channel that matches a library workflow name."""
    name = workflow.name
    if name.startswith("math_reasoning"):
        return MathReasoningTaskModel()
    if name.startswith("multihop_qa"):
        return MultiHopQATaskModel()
    if name.startswith("self_consistency"):
        return SelfConsistencyTaskModel()
    if name.startswith("complex"):
        return MultiHopQATaskModel()
    if name.startswith("refinement"):
        return MathReasoningTaskModel()
    logger.warning("Unknown workflow %s; defaulting to math quality channel", name)
    return MathReasoningTaskModel()
