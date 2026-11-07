"""M3 realistic labels and M8 HotpotQA, on the fake server."""

import json

import numpy as np
import pytest

from agentqo.backends.cache import GenerationCache
from agentqo.backends.fake_server import FakeServer
from agentqo.backends.vllm_http import VLLMHTTPBackend, VLLMHTTPConfig
from agentqo.executor import FidelityPlan, WorkflowExecutor
from agentqo.labeling.ec_labeler import ECLabeler
from agentqo.labeling.labels_v2 import labels_rows, per_problem_rows, strategy_rows
from agentqo.tasks.answers import extract_hotpot_answer
from agentqo.tasks.hotpotqa import N_EVAL, N_LABEL, format_problem, split_rows
from agentqo.tasks.prompts import build_prompt, code_output
from agentqo.tasks.real_task_model import RealTaskModel
from agentqo.workflows.dag import LARGE_FIDELITY, SMALL_FIDELITY
from agentqo.workflows.library import create_hotpot_chain_workflow, create_math_reasoning_workflow
from tests._real_fixtures import PROBLEMS, fake_backend

HOTPOT = [{"qid": f"hotpot-{i}", "gold": f"answer {i}",
           "question": format_problem({"question": f"Who is number {i}?",
                                       "context": [[f"T{i}", [f"A sentence on {i}. ", "Another one."]]]})}
          for i in range(10)]


def hotpot_backend(small_err=0.3, large_err=0.05, cache=None):
    cfg = VLLMHTTPConfig(temperature=0.0)
    server = FakeServer(HOTPOT, {cfg.small_model: small_err, cfg.large_model: large_err})
    return VLLMHTTPBackend(cfg, request_fn=server, prompt_fn=build_prompt, code_fn=code_output, cache=cache), server


def label(wf, backend, tm, n, **kw):
    return ECLabeler(backend, tm, mode="substitute", n_corruptions=3, k_samples=5, max_workers=4, **kw) \
        .label_workflow(wf, num_tasks=n, show_progress=False)


def test_realistic_records_have_every_required_field():
    backend, _, tm = fake_backend()
    wf = create_math_reasoning_workflow(3)
    res = label(wf, backend, tm, 6, realistic=True)
    for r in res.records:
        assert {"q_base", "q_plus", "baseline_agrees", "sample_keys", "consequence_by_strategy",
                "consequence_real"} <= set(r)
        assert len(r["sample_keys"]) == (3 if r["node_id"] == "planner" else 5)  # planner cap in p_err.py
    # The planner has no key but still gets a real-error consequence (None only if the
    # resampled plan is byte-identical to the reference, as the fake's good plans are).
    planners = [r for r in res.records if r["node_id"] == "planner"]
    assert any(r["consequence_real"] is not None for r in planners)
    assert all("resample_disagree" not in r["consequence_by_strategy"] for r in res.records)


def test_labels_v2_definitions():
    backend, _, tm = fake_backend()
    wf = create_math_reasoning_workflow(3)
    res = label(wf, backend, tm, 12, realistic=True)
    rows = {r["agent"]: r for r in labels_rows(res.records)}
    assert set(rows) == set(wf.nodes)
    for agent, row in rows.items():
        recs = [r for r in res.records if r["node_id"] == agent]
        gain = [r["q_plus"] - r["q_base"] for r in recs]
        assert row["uv"] == pytest.approx(np.mean(gain))
        assert row["uv_ci_low"] <= row["uv"] <= row["uv_ci_high"]
        assert row["n"] == 12 and row["reruns_used"] == row["reruns_full"]  # full mode
    assert rows["verifier"]["reruns_full"] == 0  # no descendants to rerun
    assert any(s["strategy"] == "resample_disagree" for s in strategy_rows(res.records))
    assert len(per_problem_rows(res.records)) == 72


def test_disagree_only_saves_reruns_and_matches_on_disagreements():
    wf = create_math_reasoning_workflow(3)
    b1, _, tm1 = fake_backend()
    full = label(wf, b1, tm1, 12, realistic=True)
    b2, _, tm2 = fake_backend()
    fast = label(wf, b2, tm2, 12, disagree_only=True)
    f_rows = {r["agent"]: r for r in labels_rows(full.records)}
    d_rows = {r["agent"]: r for r in labels_rows(fast.records)}
    assert sum(r["reruns_used"] for r in d_rows.values()) < sum(r["reruns_used"] for r in f_rows.values())
    by_key = {(r["task_id"], r["node_id"]): r for r in full.records}
    skipped = [r for r in fast.records if r["skipped_plus"]]
    assert skipped
    for r in skipped:
        assert r["q_plus"] == r["q_base"]
    for r in fast.records:
        if not r["skipped_plus"]:
            assert r["q_plus"] == by_key[(r["task_id"], r["node_id"])]["q_plus"]


def test_realistic_mode_does_not_change_the_existing_labels():
    wf = create_math_reasoning_workflow(3)
    b1, _, tm1 = fake_backend()
    old = label(wf, b1, tm1, 6)
    b2, _, tm2 = fake_backend()
    new = label(wf, b2, tm2, 6, realistic=True)
    for a, b in zip(old.records, new.records):
        assert all(a[k] == b[k] for k in a)
    assert all("sample_keys" not in r for r in old.records)


def test_plus_costs_count_the_large_call_when_skipped(tmp_path):
    wf = create_math_reasoning_workflow(3)
    backend, _, tm = fake_backend(small_err=0.0, large_err=0.0)
    res = label(wf, backend, tm, 3, disagree_only=True)
    rec = next(r for r in res.records if r["skipped_plus"])
    assert rec["calls_plus"]["large_out"] > 0
    assert rec["calls_samples"]["small_out"] > 0


def test_hotpot_extraction_and_exact_match():
    assert extract_hotpot_answer("work\nFinal answer: The Beatles.") == "beatles"
    assert extract_hotpot_answer("x\nFINDING: Paris") == "paris"
    assert extract_hotpot_answer("VERDICT: correct\n#### Yes") == "yes"
    assert extract_hotpot_answer("only a line") == "only line"
    assert extract_hotpot_answer("   ") is None
    tm = RealTaskModel(HOTPOT, dataset="hotpotqa")
    assert tm.score_text("Final answer: the Answer 3", "answer 3") == 1.0
    assert tm.score_text("Final answer: answer 3 extra", "answer 3") == 0.0
    assert tm.f1_text("Final answer: answer 3 extra", "answer 3") == pytest.approx(0.8)


def test_hotpot_chain_shape_and_prompts():
    wf = create_hotpot_chain_workflow()
    assert list(wf.topological_order) == ["planner", "hop_1", "hop_2", "aggregator", "verifier"]
    assert wf.answer_nodes[0] == "verifier"
    backend, _ = hotpot_backend(small_err=0.0)
    tm = RealTaskModel(HOTPOT, dataset="hotpotqa")
    task = tm.generate_task(wf, None)
    rec = WorkflowExecutor(backend, tm).run_workflow(wf, task, FidelityPlan(default_fidelity=SMALL_FIDELITY), seed=0)
    assert rec.final_quality == 1.0
    prompts = {n: r.metadata["prompt"] for n, r in rec.node_results.items()}
    assert all("[T0] A sentence on 0. Another one." in p for p in prompts.values())
    assert "hop 2 only" in prompts["hop_2"] and rec.node_results["hop_1"].output["text"] in prompts["hop_2"]
    assert rec.node_results["hop_1"].output["text"] in prompts["aggregator"]
    assert "repeat the original answer exactly" in prompts["verifier"]


def test_hotpot_labels_run_end_to_end():
    wf = create_hotpot_chain_workflow()
    backend, _ = hotpot_backend()
    res = label(wf, backend, RealTaskModel(HOTPOT, dataset="hotpotqa"), 8, realistic=True)
    assert {r["agent"] for r in labels_rows(res.records)} == set(wf.nodes)


def test_hotpot_split_is_fixed_and_disjoint():
    rows = [{"id": f"{i:05d}"} for i in range(1000)]
    a, b = split_rows(rows), split_rows(rows)
    assert a == b
    label_ids, eval_ids = {r["id"] for r in a["label"]}, {r["id"] for r in a["eval"]}
    assert len(label_ids) == N_LABEL and len(eval_ids) == N_EVAL and not label_ids & eval_ids
