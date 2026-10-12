"""Guards for the runtime fixes (Q̂ saturation, hysteresis, no ground truth)."""

import numpy as np

from agentqo.runtime.edits import Edit, apply_edit
from agentqo.runtime.scores import expected_quality
from agentqo.runtime.system import AgentQO, Arrival
from agentqo.simulator.task_model import MockBackend, task_model_for_workflow
from agentqo.workflows.library import (
    create_math_reasoning_workflow,
    create_self_consistency_workflow,
)


def _structure_ec(wf):
    n = len(wf.nodes)
    raw = {nid: (wf.get_downstream_reach(nid) + 1) / n for nid in wf.nodes}
    top = max(raw.values())
    return {k: v / top for k, v in raw.items()}


def _serve(wf, ec, n_jobs=4):
    model = task_model_for_workflow(wf)
    jobs = [
        Arrival(workflow=wf, task=model.generate_task(wf, np.random.default_rng(i + 1)),
                seed=10 + i, time=4.0 * i, ec_scores=ec)
        for i in range(n_jobs)
    ]
    return AgentQO(MockBackend(model, embedding_dim=64), model, n_gpus=2).serve(jobs)


def test_qhat_not_saturated_and_verifier_skip_costs_quality():
    wf = create_math_reasoning_workflow(3, include_verifier=True)
    ec = _structure_ec(wf)
    fid = {nid: node.fidelities[0] for nid, node in wf.nodes.items()}
    q0 = expected_quality(wf, ec, set(), fid)
    assert q0 < 1.0, "Q̂ must not clip at 1.0, or quality-reducing edits look free"
    q_skip = expected_quality(wf, ec, {"verifier"}, fid)
    assert q_skip < q0


def test_upgrade_value_scales_with_ec():
    wf = create_math_reasoning_workflow(3, include_verifier=True)
    ec = _structure_ec(wf)
    fid = {nid: node.fidelities[0] for nid, node in wf.nodes.items()}
    q0 = expected_quality(wf, ec, set(), fid)
    gains = {}
    for nid in ("planner", "verifier"):
        f2 = dict(fid)
        f2[nid] = wf.nodes[nid].fidelities[-1]
        gains[nid] = expected_quality(wf, ec, set(), f2) - q0
    assert gains["planner"] > gains["verifier"] > 0


def test_no_edit_reversal_per_episode():
    wf = create_self_consistency_workflow(k=2, k_max=5)
    report = _serve(wf, _structure_ec(wf))
    for rec in report.records:
        touched = [e.split("(")[1].split("->")[0].rstrip(")") for e in rec.edits if "(" in e]
        assert len(touched) == len(set(touched)), f"node edited twice: {rec.edits}"


def test_cancelled_branch_is_not_revived_by_width_edit():
    wf = create_self_consistency_workflow(k=2, k_max=5)
    optional = sorted(n for n, node in wf.nodes.items() if node.optional)
    skipped, cancelled = {optional[0]}, {optional[0]}
    fid = {nid: node.fidelities[0] for nid, node in wf.nodes.items()}
    apply_edit(Edit(kind="set_width", k=5), skipped, cancelled, fid, wf)
    assert optional[0] in skipped


def test_runtime_never_reads_ground_truth_correctness():
    import inspect
    from agentqo.runtime import optimizer, system

    for mod in (system, optimizer):
        src = inspect.getsource(mod)
        code = "\n".join(l.split("#")[0] for l in src.splitlines())
        assert ".correctness" not in code, f"{mod.__name__} reads ground truth"
