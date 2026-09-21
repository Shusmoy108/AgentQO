"""Score a workflow with a fitted EC predictor using cheap probe runs."""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np

from agentqo.executor import WorkflowExecutor
from agentqo.predictors.ec_predictor import ECPredictor
from agentqo.predictors.features import FeatureExtractor
from agentqo.simulator.task_model import TaskModel
from agentqo.workflows.dag import Workflow


def predict_node_scores(
    workflow: Workflow,
    task_model: TaskModel,
    backend,
    predictor: ECPredictor,
    extractor: Optional[FeatureExtractor] = None,
    n_probes: int = 8,
    view: str = "agentqo",
    seed: int = 0,
) -> Dict[str, float]:
    """Average probe embeddings, then predict EC for every node.

    This is what the scheduler actually gets at runtime: a few cheap
    executions, not fault-injection labels.
    """
    extractor = extractor or FeatureExtractor(
        embedding_dim=int(getattr(backend, "embedding_dim", 256))
    )
    executor = WorkflowExecutor(backend, task_model)
    rng = np.random.default_rng(seed)
    run_features = []
    for _ in range(n_probes):
        task_seed = int(rng.integers(0, 2**31))
        task = task_model.generate_task(workflow, np.random.default_rng(task_seed))
        record = executor.run_workflow(workflow, task, seed=task_seed)
        run_features.append(
            extractor.extract_all_features_with_results(workflow, record.node_results)
        )
    averaged = extractor.average_features_over_runs(run_features)
    scores: Dict[str, float] = {}
    node_ids = []
    rows = []
    for node_id, feats in averaged.items():
        if feats.embedding is None:
            continue
        node_ids.append(node_id)
        rows.append(feats.as_vector(view))
    if not rows:
        return {nid: 0.0 for nid in workflow.nodes}
    pred = predictor.predict(np.stack(rows))
    for node_id, value in zip(node_ids, pred):
        scores[node_id] = float(value)
    for nid in workflow.nodes:
        scores.setdefault(nid, 0.0)
    return scores


def mean_confidence(
    workflow: Workflow,
    task_model: TaskModel,
    backend,
    n_probes: int = 8,
    seed: int = 0,
) -> Dict[str, float]:
    executor = WorkflowExecutor(backend, task_model)
    rng = np.random.default_rng(seed)
    sums = {nid: 0.0 for nid in workflow.nodes}
    counts = {nid: 0 for nid in workflow.nodes}
    for _ in range(n_probes):
        task_seed = int(rng.integers(0, 2**31))
        task = task_model.generate_task(workflow, np.random.default_rng(task_seed))
        record = executor.run_workflow(workflow, task, seed=task_seed)
        for nid, res in record.node_results.items():
            sums[nid] += res.confidence
            counts[nid] += 1
    return {nid: sums[nid] / max(counts[nid], 1) for nid in workflow.nodes}
