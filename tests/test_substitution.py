"""WP3/WP4: output-substitution labeling on real text (fake server)."""

import numpy as np
import pytest

from agentqo.backends.vllm_http import _output_as_text
from agentqo.executor import ExecutionOverrides, WorkflowExecutor, verify_partial_recompute_invariant
from agentqo.labeling.corruptions import numeric_perturb
from agentqo.labeling.ec_labeler import ECLabeler
from agentqo.labeling.p_err import p_err_from_keys
from agentqo.workflows.library import create_complex_workflow, create_math_reasoning_workflow, create_multihop_qa_workflow
from tests._real_fixtures import fake_backend


def _text(rec, nid):
    return _output_as_text(rec.node_results[nid].output)


def test_substituting_planner_changes_every_descendant_input():
    backend, server, tm = fake_backend(small_err=0.0)
    wf = create_math_reasoning_workflow(3)
    ex = WorkflowExecutor(backend, tm)
    task = tm.generate_task(wf, None)
    base = ex.run_workflow(wf, task, seed=0)
    bad_plan = "PLAN:\n1. Subtract instead. [plan-bad]"
    rec = ex.run_with_partial_recompute(wf, task, base.node_results, {"planner"},
                                        ExecutionOverrides(force_outputs={"planner": bad_plan}), seed=0)
    assert _text(rec, "planner") == bad_plan
    for d in wf.get_descendants("planner"):
        assert bad_plan in rec.node_results[d].metadata["prompt"] or d != "step_1"
        assert rec.node_results[d].metadata["prompt"] != base.node_results[d].metadata["prompt"]
    assert rec.final_quality == 0.0 and base.final_quality == 1.0


def test_non_descendants_byte_identical_and_forced_node_not_executed():
    backend, server, tm = fake_backend()
    wf = create_multihop_qa_workflow(3)
    ex = WorkflowExecutor(backend, tm)
    task = tm.generate_task(wf, None)
    base = ex.run_workflow(wf, task, seed=0)
    calls = server.n_requests
    rec = ex.run_with_partial_recompute(wf, task, base.node_results, {"researcher_1"},
                                        ExecutionOverrides(force_outputs={"researcher_1": "RESULT: 0"}), seed=0)
    ok, violations = verify_partial_recompute_invariant(base, rec, {"researcher_1"}, wf)
    assert ok, violations
    for nid in ("planner", "researcher_2", "researcher_3"):
        assert rec.node_results[nid] is base.node_results[nid]
    # researcher_1 was forced (no call); aggregator + verifier recomputed.
    assert server.n_requests - calls == 2


def test_labeler_refuses_flag_mode_on_real_backend():
    backend, _, tm = fake_backend()
    with pytest.raises(ValueError):
        ECLabeler(backend, tm)


def test_numeric_perturb_changes_key():
    assert numeric_perturb("so\n#### 1,234", "1234", 0) == "so\n#### 1235"
    assert numeric_perturb("RESULT: 7", "7", 1) == "RESULT: 14"
    assert numeric_perturb("PLAN: go", None, 0) is None


def test_p_err_extremes():
    assert p_err_from_keys(["5"] * 5, "5") == 0.0
    assert p_err_from_keys(["6", "7", None, "8", "9"], "5") == 1.0


def test_p_err_on_fake_server_agree_and_disagree():
    wf = create_math_reasoning_workflow(2, include_verifier=False)
    always_right, *_ = fake_backend(small_err=0.0, large_err=0.0)
    always_wrong, *_ = fake_backend(small_err=0.95, large_err=0.0, sampler_temperature=0.7)
    for backend, expected in ((always_right, 0.0), (always_wrong, 1.0)):
        tm = fake_backend()[2]
        res = ECLabeler(backend, tm, mode="substitute", k_samples=5, max_workers=4).label_workflow(
            wf, num_tasks=3, show_progress=False)
        # small_err 0.95 at temperature 0.7 is capped at 0.95 per sample: allow one agreement.
        assert abs(res.labels["aggregator"].local_error_prob - expected) <= 0.2


def test_h1_sanity_on_real_text():
    """Corrupting the aggregator lowers quality; the formatter has lower EC than aggregator and planner.

    On real text the formatter is the answer node, so its *consequence* is
    high; it is harmless because it almost never errs (p_err ~ 0).
    """
    backend, _, tm = fake_backend(small_err=0.2)
    wf = create_complex_workflow(2, 2)
    res = ECLabeler(backend, tm, mode="substitute", max_workers=8).label_workflow(
        wf, num_tasks=8, show_progress=False)
    agg, fmt = res.labels["aggregator"], res.labels["formatter"]
    assert np.mean(agg.raw_qualities_incorrect) < np.mean(agg.raw_qualities_correct)
    assert fmt.ec_score < agg.ec_score and fmt.ec_score <= res.labels["planner"].ec_score
    keyed = [c for r in res.records for c in r["corruptions"] if c["key_differs"] is not None]
    assert np.mean([c["key_differs"] for c in keyed]) >= 0.9
    assert all(not r["invariant_violations"] for r in res.records)
