"""Quality-channel invariants: H1 must be a measurement, not a tautology."""

import numpy as np
import pytest

from agentqo.experiments.dataset import canonical_split, leave_one_workflow_out
from agentqo.experiments.suite import default_suite
from agentqo.executor import ExecutionOverrides, WorkflowExecutor
from agentqo.simulator.task_model import (
    MathReasoningTaskModel,
    MockBackend,
    MultiHopQATaskModel,
    SelfConsistencyTaskModel,
)
from agentqo.workflows.library import (
    create_complex_workflow,
    create_math_reasoning_workflow,
    create_multihop_qa_workflow,
    create_self_consistency_workflow,
)


def test_workflow_names_are_unique_in_suite():
    names = [m.workflow.name for m in default_suite(quick=False)]
    assert len(names) == len(set(names))


def test_leave_one_workflow_out_does_not_leak():
    names = [m.workflow.name for m in default_suite(quick=True)]
    for split in leave_one_workflow_out(names):
        assert not split.contains_leak()
        assert len(split.test_workflows) == 1
        assert split.test_workflows[0] not in split.train_workflows
    canon = canonical_split(names)
    assert not canon.contains_leak()


def test_formatter_error_barely_changes_quality():
    workflow = create_complex_workflow(num_researchers=2, num_steps_per_researcher=1)
    task_model = MultiHopQATaskModel(importance_noise=0.2)
    backend = MockBackend(task_model, embedding_dim=64)
    executor = WorkflowExecutor(backend, task_model)
    task = task_model.generate_task(workflow, np.random.default_rng(0))

    q_fmt_ok = executor.run_workflow(
        workflow, task,
        overrides=ExecutionOverrides(forced_correctness={"formatter": True}),
        seed=1,
    ).final_quality
    q_fmt_bad = executor.run_workflow(
        workflow, task,
        overrides=ExecutionOverrides(forced_correctness={"formatter": False}),
        seed=1,
    ).final_quality
    q_plan_ok = executor.run_workflow(
        workflow, task,
        overrides=ExecutionOverrides(forced_correctness={"planner": True}),
        seed=1,
    ).final_quality
    q_plan_bad = executor.run_workflow(
        workflow, task,
        overrides=ExecutionOverrides(forced_correctness={"planner": False}),
        seed=1,
    ).final_quality

    fmt_gap = q_fmt_ok - q_fmt_bad
    plan_gap = q_plan_ok - q_plan_bad
    assert plan_gap > fmt_gap
    assert fmt_gap < 0.15


def test_importance_is_not_a_deterministic_function_of_structure():
    workflow = create_math_reasoning_workflow(num_steps=3)
    model = MathReasoningTaskModel(importance_noise=0.5)
    imps = []
    for seed in range(12):
        task = model.generate_task(workflow, np.random.default_rng(seed))
        imps.append(task.node_importance["planner"])
    assert np.std(imps) > 0.005


def test_self_consistency_any_correct_semantics():
    workflow = create_self_consistency_workflow(k=3)
    model = SelfConsistencyTaskModel()
    backend = MockBackend(model, embedding_dim=64)
    executor = WorkflowExecutor(backend, model)
    task = model.generate_task(workflow, np.random.default_rng(3))

    all_bad = executor.run_workflow(
        workflow, task,
        overrides=ExecutionOverrides(forced_correctness={
            "sampler_1": False, "sampler_2": False, "sampler_3": False,
        }),
        seed=4,
    )
    one_good = executor.run_workflow(
        workflow, task,
        overrides=ExecutionOverrides(forced_correctness={
            "sampler_1": True, "sampler_2": False, "sampler_3": False,
        }),
        seed=4,
    )
    assert one_good.final_quality > all_bad.final_quality


def test_embedding_does_not_copy_dag_structure_into_every_dim():
    """Embeddings carry hidden importance; structural features are separate."""
    workflow = create_multihop_qa_workflow(num_researchers=3, include_verifier=False)
    model = MultiHopQATaskModel()
    backend = MockBackend(model, embedding_dim=64, embedding_signal_strength=0.8)
    executor = WorkflowExecutor(backend, model)
    task = model.generate_task(workflow, np.random.default_rng(5))
    record = executor.run_workflow(workflow, task, seed=5)
    # Hidden importance should correlate with embedding[:16] mean, not with
    # a one-hot of role packed into the whole vector.
    scores = []
    imps = []
    for nid, res in record.node_results.items():
        scores.append(float(res.embedding[:16].mean()))
        imps.append(task.node_importance[nid])
    corr = np.corrcoef(scores, imps)[0, 1]
    assert corr > 0.2
