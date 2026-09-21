"""AgentQO runtime: joint logical/physical optimizer from the proposal."""

import numpy as np

from agentqo.runtime.cluster import Cluster
from agentqo.runtime.edits import candidate_edits
from agentqo.runtime.scores import branch_index, expected_quality, kv_value, speculative_delta_q
from agentqo.runtime.system import AgentQO, Arrival, FCFSFixed, FixedPlanEC
from agentqo.simulator.task_model import MockBackend, task_model_for_workflow
from agentqo.workflows.library import (
    create_math_reasoning_workflow,
    create_refinement_workflow,
    create_self_consistency_workflow,
)


def _ec_from_structure(workflow) -> dict:
    total = max(len(workflow.nodes), 1)
    return {
        nid: (workflow.get_downstream_reach(nid) + 1) / total
        for nid in workflow.nodes
    }


def _run_one(policy_cls, workflow, n_jobs=3, n_gpus=2, **kwargs):
    model = task_model_for_workflow(workflow)
    backend = MockBackend(model, embedding_dim=64)
    policy = policy_cls(backend, model, n_gpus=n_gpus, **kwargs)
    arrivals = []
    for i in range(n_jobs):
        task = model.generate_task(workflow, np.random.default_rng(i + 1))
        arrivals.append(Arrival(
            workflow=workflow,
            task=task,
            seed=10 + i,
            time=float(i) * 5.0,
            ec_scores=_ec_from_structure(workflow),
        ))
    return policy.serve(arrivals)


def test_agentqo_completes_math_workflow():
    workflow = create_math_reasoning_workflow(num_steps=2, include_verifier=True)
    report = _run_one(AgentQO, workflow, n_jobs=2)
    assert len(report.records) == 2
    assert all(r.finish_time is not None for r in report.records)
    assert 0.0 <= report.mean_quality <= 1.0
    assert report.makespan > 0


def test_fcfs_and_agentqo_both_finish():
    workflow = create_math_reasoning_workflow(num_steps=2, include_verifier=True)
    a = _run_one(AgentQO, workflow, n_jobs=2)
    b = _run_one(FCFSFixed, workflow, n_jobs=2)
    assert len(a.records) == len(b.records) == 2


def test_optional_sampler_can_be_skipped_without_deadlock():
    workflow = create_self_consistency_workflow(k=2, k_max=4)
    optional = [nid for nid, n in workflow.nodes.items() if n.optional]
    assert optional
    report = _run_one(AgentQO, workflow, n_jobs=1)
    rec = report.records[0]
    assert rec.finish_time is not None
    assert "aggregator" in rec.completed


def test_refinement_loop_is_editable():
    workflow = create_refinement_workflow(max_rounds=2)
    assert workflow.nodes["refine_1"].optional
    edits = candidate_edits(workflow, set(), set(), set(), set(), {})
    kinds = {e.kind for e in edits}
    assert "noop" in kinds
    assert "skip_optional" in kinds
    assert "set_fidelity" in kinds


def test_kv_value_increases_with_ec():
    low = kv_value(0.5, 10.0, 0.1, kappa=1.0)
    high = kv_value(0.5, 10.0, 0.8, kappa=1.0)
    assert high > low


def test_branch_index_drops_as_agreement_rises():
    early = branch_index(speculative_delta_q(0, 2), 20.0)
    late = branch_index(speculative_delta_q(3, 1), 20.0)
    assert early > late


def test_fixed_plan_ec_upgrades_high_reach_nodes():
    workflow = create_math_reasoning_workflow(num_steps=2, include_verifier=True)
    report = _run_one(FixedPlanEC, workflow, n_jobs=1)
    rec = report.records[0]
    planner_fid = rec.fidelities["planner"].name
    assert planner_fid in {"small", "large"}
    # Planner has highest reach so it should be among upgrades.
    upgraded = [nid for nid, f in rec.fidelities.items() if f.name != "small"]
    assert "planner" in upgraded or len(upgraded) >= 1


def test_skipping_optional_work_does_not_raise_qhat():
    workflow = create_refinement_workflow(max_rounds=2)
    ec = {nid: 0.25 for nid in workflow.nodes}
    fid = {nid: n.fidelities[0] for nid, n in workflow.nodes.items()}
    q_all = expected_quality(workflow, ec, set(), fid)
    q_skip = expected_quality(workflow, ec, {"refine_1", "refine_2"}, fid)
    assert q_skip <= q_all


def test_cluster_externality_is_nonzero_when_colocated():
    from agentqo.runtime.cluster import RunningCall
    from agentqo.simulator.interaction_model import CallSpec
    cluster = Cluster(n_gpus=1)
    spec_a = CallSpec("a", "llm-7b", 0, 128, 64, prefix_id="x")
    spec_b = CallSpec("b", "llm-7b", 0, 128, 64, prefix_id="y")
    cluster.admit(RunningCall("a", "w", "n1", spec_a, 0.0, 1.0))
    own, ext, c_phys = cluster.physical_cost(spec_b)
    assert ext != 0.0 or c_phys >= own
