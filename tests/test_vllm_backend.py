"""Unit tests for VLLMHTTPBackend with mocked HTTP (no live GPU)."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pytest

from agentqo.backends.vllm_http import (
    VLLMConnectionError,
    VLLMHTTPBackend,
    VLLMHTTPConfig,
    _confidence_from_logprobs,
    _extract_text,
    _placeholder_embedding,
)
from agentqo.workflows.dag import LARGE_FIDELITY, SMALL_FIDELITY, NodeRole, NodeSpec


def _fake_chat_response(text: str = "42", with_logprobs: bool = True) -> Dict[str, Any]:
    choice: Dict[str, Any] = {
        "message": {"role": "assistant", "content": text},
        "finish_reason": "stop",
    }
    if with_logprobs:
        choice["logprobs"] = {
            "content": [
                {"token": "4", "logprob": -0.1},
                {"token": "2", "logprob": -0.2},
            ]
        }
    return {"id": "chatcmpl-test", "choices": [choice], "model": "test-model"}


def _planner() -> NodeSpec:
    return NodeSpec(
        node_id="planner",
        role=NodeRole.PLANNER,
        description="Decompose the math problem",
        fidelities=[SMALL_FIDELITY, LARGE_FIDELITY],
    )


def test_execute_node_returns_node_result():
    captured = {}

    def fake_post(url, payload, headers, timeout_s):
        captured["url"] = url
        captured["payload"] = payload
        return _fake_chat_response("answer is 42")

    backend = VLLMHTTPBackend(
        VLLMHTTPConfig(base_url="http://vllm.test:8000", small_model="m-8b"),
        request_fn=fake_post,
    )
    result = backend.execute_node(
        node=_planner(),
        inputs={},
        fidelity=SMALL_FIDELITY,
        task_context={"problem": "17+25"},
    )
    assert result.node_id == "planner"
    assert result.output["text"] == "answer is 42"
    assert result.fidelity_used == "small"
    assert result.cost >= 0.0
    assert result.embedding.shape == (backend.embedding_dim,)
    assert result.metadata["embedding_kind"] == "placeholder"
    assert result.metadata["correctness_unknown"] is True
    assert result.correctness is False
    assert captured["url"].endswith("/v1/chat/completions")
    assert captured["payload"]["model"] == "m-8b"
    assert "17+25" in captured["payload"]["messages"][1]["content"]


def test_large_fidelity_selects_large_model():
    models = []

    def fake_post(url, payload, headers, timeout_s):
        models.append(payload["model"])
        return _fake_chat_response("ok")

    backend = VLLMHTTPBackend(
        VLLMHTTPConfig(small_model="small-id", large_model="large-id"),
        request_fn=fake_post,
    )
    backend.execute_node(_planner(), {}, LARGE_FIDELITY, {"problem": "x"})
    assert models == ["large-id"]


def test_scorer_sets_correctness():
    def fake_post(url, payload, headers, timeout_s):
        return _fake_chat_response("42")

    def scorer(text, node, ctx):
        return text.strip() == "42"

    backend = VLLMHTTPBackend(VLLMHTTPConfig(), request_fn=fake_post)
    result = backend.execute_node(
        _planner(), {}, SMALL_FIDELITY, {"problem": "x", "scorer": scorer}
    )
    assert result.correctness is True
    assert result.metadata["correctness_unknown"] is False


def test_connection_error_propagates():
    def boom(url, payload, headers, timeout_s):
        raise VLLMConnectionError("down")

    backend = VLLMHTTPBackend(VLLMHTTPConfig(), request_fn=boom)
    with pytest.raises(VLLMConnectionError):
        backend.execute_node(_planner(), {}, SMALL_FIDELITY, {"problem": "x"})


def test_health_check_false_on_failure(monkeypatch):
    import agentqo.backends.vllm_http as mod

    def fail_urlopen(*args, **kwargs):
        raise OSError("refused")

    monkeypatch.setattr(mod.urllib.request, "urlopen", fail_urlopen)
    backend = VLLMHTTPBackend(VLLMHTTPConfig(base_url="http://127.0.0.1:9"))
    assert backend.health_check() is False


def test_extract_text_and_confidence():
    data = _fake_chat_response("hi", with_logprobs=True)
    assert _extract_text(data) == "hi"
    conf = _confidence_from_logprobs(data)
    assert 0.01 <= conf <= 0.99
    assert _confidence_from_logprobs({"choices": [{}]}) == 0.5


def test_placeholder_embedding_is_deterministic():
    a = _placeholder_embedding("same", 64)
    b = _placeholder_embedding("same", 64)
    c = _placeholder_embedding("other", 64)
    assert np.allclose(a, b)
    assert not np.allclose(a, c)
    assert a.shape == (64,)


def test_get_info():
    info = VLLMHTTPBackend(VLLMHTTPConfig()).get_info()
    assert info["backend_type"] == "vllm_http"
    assert info["embeddings"] == "placeholder"
