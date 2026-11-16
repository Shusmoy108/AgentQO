"""L2-X lease-time code changes (branch v2-lease2-x): one test per change."""

from __future__ import annotations

import json
import time
from types import SimpleNamespace

from agentqo.backends.vllm_http import VLLMHTTPBackend, VLLMHTTPConfig
from agentqo.tasks.datasets import extended_eval, extended_eval_x2, extended_label
from agentqo.tasks.hotpotqa import extra_rows, load_hotpotqa, split_rows
from agentqo.workflows.dag import LARGE_FIDELITY, SMALL_FIDELITY, XL_FIDELITY, NodeRole, NodeSpec
from scripts.run_real_pipeline import WORKFLOWS
from scripts.v2.run_placement import build_plans, call_row


def _planner() -> NodeSpec:
    return NodeSpec(node_id="planner", role=NodeRole.PLANNER, description="plan",
                    fidelities=[SMALL_FIDELITY, LARGE_FIDELITY])


def _reply(payload):
    return {"choices": [{"message": {"content": "42"}}], "usage": {"prompt_tokens": 3, "completion_tokens": 1}}


# X1(i): per-request wall-clock start/end in node metadata and in placement_calls.csv rows
def test_request_start_end_recorded():
    backend = VLLMHTTPBackend(VLLMHTTPConfig(base_url="http://vllm.test:8000"),
                              request_fn=lambda url, payload, headers, t: _reply(payload))
    before = time.time()
    res = backend.execute_node(node=_planner(), inputs={}, fidelity=SMALL_FIDELITY, task_context={"problem": "1+1"})
    after = time.time()
    s, e = res.metadata["request_start_s"], res.metadata["request_end_s"]
    assert before <= s <= e <= after


def test_call_row_carries_request_times():
    r = SimpleNamespace(fidelity_used="large", metadata={"model": "m", "prompt_tokens": 5, "completion_tokens": 2,
                                                         "latency_s": 0.5, "request_start_s": 10.0,
                                                         "request_end_s": 10.5})
    row = call_row("all_large", "t1", "planner", r, 1)
    assert row["request_start_s"] == 10.0 and row["request_end_s"] == 10.5
    assert {k: row[k] for k in ("plan", "task_id", "node_id", "model", "fidelity", "repeat")} == \
        {"plan": "all_large", "task_id": "t1", "node_id": "planner", "model": "m", "fidelity": "large", "repeat": 1}


# X1(ii): run_placement builds A16 tier plans when V2_TIERS has xl; binary plans unchanged
def test_build_plans_binary_and_tiers():
    wf = WORKFLOWS["math"][1]()
    binary = build_plans(["all_small", "only_verifier", "all_large"], wf, ["small", "large"])
    assert binary["all_small"].assignments == {}
    assert binary["only_verifier"].assignments == {"verifier": LARGE_FIDELITY}
    assert set(binary["all_large"].assignments) == set(wf.topological_order)
    tiers = build_plans(["all_xl", "verifier=large", "all_small"], wf, ["small", "large", "xl"])
    assert tiers["all_xl"].default_fidelity == XL_FIDELITY
    assert tiers["verifier=large"].assignments == {"verifier": LARGE_FIDELITY}
    assert tiers["all_small"].default_fidelity == SMALL_FIDELITY


# X2: GSM8K eval_x2 = the 719 test problems in neither label 200 nor eval_ext 400
def test_eval_x2_split(tmp_path):
    rows = [{"question": f"q{i}", "answer": f"#### {i}"} for i in range(1319)]
    (tmp_path / "gsm8k_test.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    x2 = extended_eval_x2(cache_dir=tmp_path)
    ids = [p["qid"] for p in x2]
    used = {p["qid"] for p in extended_label(200, tmp_path) + extended_eval(400, tmp_path)}
    assert len(ids) == 719 == len(set(ids))
    assert not used & set(ids)
    assert {p["qid"] for p in extended_eval(500, tmp_path)[400:]} <= set(ids)  # eval_ext 401-500 included
    assert [p["qid"] for p in extended_eval_x2(10, tmp_path)] == ids[:10]       # fixed order


# X2: HotpotQA "extra" = 600 dev rows outside the frozen label/eval split
def test_hotpot_extra_split(tmp_path):
    rows = [{"id": f"id{i:05d}", "question": f"q{i}", "answer": f"a{i}", "context": [["T", ["s."]]]}
            for i in range(7405)]
    parts = split_rows(rows)
    split_file = tmp_path / "split.json"
    split_file.write_text(json.dumps({k: [r["id"] for r in v] for k, v in parts.items()}))
    extra = extra_rows(rows, split_file)
    used = {r["id"] for v in parts.values() for r in v}
    assert len(extra) == 600 == len({r["id"] for r in extra})
    assert not used & {r["id"] for r in extra}
    assert extra == extra_rows(rows, split_file)
    (tmp_path / "hotpot_dev_distractor.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    loaded = load_hotpotqa("extra", cache_dir=tmp_path, split_file=split_file)
    assert [p["qid"] for p in loaded] == [f"hotpot-{r['id']}" for r in extra]


# X4: AGENTQO_SEED_SALT changes request seeds; unset leaves the registered seeds
def test_seed_salt(monkeypatch):
    node, ctx = _planner(), {"task": SimpleNamespace(task_id="gsm8k-test-1"), "sample_index": 0}
    monkeypatch.delenv("AGENTQO_SEED_SALT", raising=False)
    base = VLLMHTTPBackend._seed(node, ctx)
    from zlib import crc32
    assert base == crc32(b"gsm8k-test-1|planner|0") & 0x7FFFFFFF
    monkeypatch.setenv("AGENTQO_SEED_SALT", "1")
    salted = VLLMHTTPBackend._seed(node, ctx)
    assert salted != base and salted == VLLMHTTPBackend._seed(node, ctx)
    monkeypatch.setenv("AGENTQO_SEED_SALT", "2")
    assert VLLMHTTPBackend._seed(node, ctx) not in (base, salted)
