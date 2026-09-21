"""Build EC prediction datasets without leaking simulator internals.

Every y value is a fault-injection measurement. Splits are by workflow
name so a test DAG is unseen at training time.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from agentqo.labeling.ec_labeler import ECLabel, LabelingResult, NodeObservation
from agentqo.predictors.features import FeatureExtractor, NodeFeatures
from agentqo.workflows.dag import Workflow


@dataclass
class Split:
    """Train / test partition keyed by workflow name."""

    train_workflows: List[str]
    test_workflows: List[str]

    def contains_leak(self) -> bool:
        return bool(set(self.train_workflows) & set(self.test_workflows))

    def to_dict(self) -> Dict[str, List[str]]:
        return {
            "train_workflows": list(self.train_workflows),
            "test_workflows": list(self.test_workflows),
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2))


def leave_one_workflow_out(workflow_names: Sequence[str]) -> List[Split]:
    names = list(dict.fromkeys(workflow_names))
    if len(names) < 2:
        raise ValueError("leave-one-workflow-out needs at least two workflows")
    return [
        Split(
            train_workflows=[n for n in names if n != held],
            test_workflows=[held],
        )
        for held in names
    ]


def canonical_split(workflow_names: Sequence[str]) -> Split:
    """Deterministic held-out split used for the H2 figure.

    Last workflow is the test set so the split is stable across runs.
    """
    names = list(dict.fromkeys(workflow_names))
    if len(names) < 2:
        raise ValueError("need at least two workflows for a held-out split")
    return Split(train_workflows=names[:-1], test_workflows=names[-1:])


@dataclass
class LabeledSample:
    workflow_name: str
    node_id: str
    task_id: str
    y_ec: float
    y_consequence: float
    features: NodeFeatures


def observations_to_samples(
    observations: Iterable[NodeObservation],
    labels: Dict[str, Dict[str, ECLabel]],
    workflows: Dict[str, Workflow],
    extractor: Optional[FeatureExtractor] = None,
) -> List[LabeledSample]:
    """Join per-task observations with aggregated p_err from H1 labels.

    y_ec = consequence_task * p_err_node. p_err is estimated from the
    same workflow's baseline runs (evaluation label, not a feature).
    """
    extractor = extractor or FeatureExtractor()
    samples: List[LabeledSample] = []
    for obs in observations:
        wf = workflows.get(obs.workflow_name)
        if wf is None or obs.node_id not in wf.nodes:
            continue
        label = labels.get(obs.workflow_name, {}).get(obs.node_id)
        p_err = label.local_error_prob if label is not None else (
            0.0 if obs.baseline_correct else 1.0
        )
        feats = extractor.extract_structural_features(wf, obs.node_id)
        feats.embedding = obs.embedding
        feats.confidence = obs.confidence
        samples.append(
            LabeledSample(
                workflow_name=obs.workflow_name,
                node_id=obs.node_id,
                task_id=obs.task_id,
                y_ec=float(obs.consequence) * float(p_err),
                y_consequence=float(obs.consequence),
                features=feats,
            )
        )
    return samples


def matrix_from_samples(
    samples: Sequence[LabeledSample],
    view: str,
    target: str = "ec",
) -> Tuple[np.ndarray, np.ndarray, List[Tuple[str, str, str]]]:
    if not samples:
        return np.empty((0, 0)), np.empty((0,)), []
    X = np.stack([s.features.as_vector(view) for s in samples])
    if target == "ec":
        y = np.asarray([s.y_ec for s in samples], dtype=np.float64)
    elif target == "consequence":
        y = np.asarray([s.y_consequence for s in samples], dtype=np.float64)
    else:
        raise ValueError(f"unknown target {target}")
    ids = [(s.workflow_name, s.node_id, s.task_id) for s in samples]
    return X, y, ids


def filter_samples(
    samples: Sequence[LabeledSample],
    workflow_names: Sequence[str],
) -> List[LabeledSample]:
    allowed = set(workflow_names)
    return [s for s in samples if s.workflow_name in allowed]


def labeling_results_to_maps(
    results: Dict[str, LabelingResult],
) -> Tuple[Dict[str, Dict[str, ECLabel]], List[NodeObservation]]:
    labels = {name: res.labels for name, res in results.items()}
    observations: List[NodeObservation] = []
    for res in results.values():
        observations.extend(res.observations)
    return labels, observations
