"""M3 realistic labels and M8 HotpotQA, on the fake server."""

import json
from pathlib import Path

import numpy as np
import pytest

from agentqo.backends.cache import GenerationCache
from agentqo.backends.fake_server import FakeServer
from agentqo.backends.vllm_http import VLLMHTTPBackend, VLLMHTTPConfig
from agentqo.executor import FidelityPlan, WorkflowExecutor
from agentqo.labeling.ec_labeler import ECLabeler
from agentqo.labeling.labels_v2 import labels_rows, per_problem_rows, strategy_rows
from agentqo.tasks.answers import extract_hotpot_answer
from agentqo.tasks.hotpotqa import N_EVAL, N_LABEL, format_problem, frozen_rows, split_rows
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


def test_disagree_only_skips_only_on_equal_keys_and_keeps_uv():
    """FIX 2: skip Q+ only when small and large keys agree; never for the planner.
    With the fake backend equal keys give equal downstream answers, so UV per agent
    is identical in full and disagree-only mode."""
    wf = create_math_reasoning_workflow(3)
    b1, _, tm1 = fake_backend()
    full = label(wf, b1, tm1, 12, realistic=True)
    b2, _, tm2 = fake_backend()
    fast = label(wf, b2, tm2, 12, disagree_only=True)
    by_key = {(r["task_id"], r["node_id"]): r for r in full.records}
    for r in fast.records:
        if r["node_id"] == "planner":
            assert not r["skipped_plus"]
        if r["skipped_plus"]:
            assert r["base_key"] == r["reference_key"] is not None
            assert by_key[(r["task_id"], r["node_id"])]["q_plus"] == r["q_base"]
    f_uv = {r["agent"]: r["uv"] for r in labels_rows(full.records)}
    d_uv = {r["agent"]: r["uv"] for r in labels_rows(fast.records)}
    assert f_uv == pytest.approx(d_uv)


def test_ec_real_excludes_problems_without_a_disagreeing_resample():
    base = {"code_node": False, "q_base": 0.0, "q_plus": 1.0, "baseline_agrees": False, "p_err": 0.5,
            "consequence_by_strategy": {"swap_other_task": 1.0}, "has_descendants": True, "skipped_plus": False}
    recs = [{**base, "node_id": "a", "task_id": "t1", "consequence_real": 1.0},
            {**base, "node_id": "a", "task_id": "t2", "consequence_real": None},
            {**base, "node_id": "b", "task_id": "t1", "consequence_real": None}]
    rows = {r["agent"]: r for r in labels_rows(recs)}
    assert rows["a"]["ec_real"] == pytest.approx(0.5) and rows["a"]["ec_real_n_used"] == 1  # not (1+0)/2
    assert rows["b"]["ec_real"] is None and rows["b"]["ec_real_n_used"] == 0


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
    assert "repeat the proposed short answer exactly" in prompts["verifier"]
    # FIX 1: the question is restated next to the answer slot, and yes/no is conditional.
    question = HOTPOT[0]["question"].split("\n", 1)[0].removeprefix("Question: ")
    for nid in ("aggregator", "verifier"):
        assert f"Question: {question}\nAnswer" in prompts[nid] or f"Question: {question}\nDoes" in prompts[nid]
        assert "whether something is true" in prompts[nid]


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


def test_hotpot_frozen_split_reads_ids_and_fails_on_missing(tmp_path):
    rows = [{"id": f"{i:05d}"} for i in range(10)]
    f = tmp_path / "split.json"
    f.write_text(json.dumps({"label": ["00003", "00001"], "eval": ["00007"]}))
    parts = frozen_rows(rows, f)
    assert [r["id"] for r in parts["label"]] == ["00003", "00001"] and [r["id"] for r in parts["eval"]] == ["00007"]
    with pytest.raises(RuntimeError, match="not in the dev file"):
        frozen_rows(rows[:5], f)
    with pytest.raises(FileNotFoundError):
        frozen_rows(rows, tmp_path / "nope.json")


@pytest.mark.skipif(not (Path("data/tasks/gsm8k_test.jsonl").exists() and Path("data/tasks/split.json").exists()),
                    reason="GSM8K working set not downloaded")
def test_gsm8k_v2_label_and_eval_pools_are_disjoint_and_keep_session1_order():
    """FIX 4: label 200 = Session 1 dev 100 + the next 100 of Session 1 LABEL; eval_ext 400 =
    Session 1 EVAL 200 + EVAL2[:200]. No overlap."""
    from agentqo.tasks.datasets import _dev_eval, extended_eval, extended_label, session1_extra
    split = _dev_eval(Path("data/tasks"))
    lab, ev = [p["qid"] for p in extended_label(200)], [p["qid"] for p in extended_eval(400)]
    assert lab[:100] == [p["qid"] for p in split["dev"]] and ev[:200] == [p["qid"] for p in split["eval"]]
    assert len(set(lab)) == 200 and len(set(ev)) == 400 and not set(lab) & set(ev)
    assert ev[200:] == [p["qid"] for p in session1_extra()[500:700]]
