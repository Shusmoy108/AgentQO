"""WP7b: Ollama backend logic with mocked HTTP (no server needed)."""

import pytest

from agentqo.backends.cache import GenerationCache
from agentqo.backends.ollama_backend import OllamaBackend, ollama_config
from agentqo.backends.vllm_http import MissingLogprobsError, VLLMConnectionError
from agentqo.workflows.dag import SMALL_FIDELITY, NodeRole, NodeSpec

DIGESTS = {"qwen2.5:1.5b-instruct": "aaaa1111bbbb2222", "qwen2.5:7b-instruct": "cccc3333dddd4444"}
NODE = NodeSpec(node_id="planner", role=NodeRole.PLANNER)


def _openai(text="#### 4", logprobs=True, prompt_tokens=10):
    return {"choices": [{"message": {"content": text},
                         "logprobs": {"content": [{"token": "4", "logprob": -0.1}]} if logprobs else None}],
            "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": 2}}


def _backend(post, **kw):
    b = OllamaBackend(ollama_config(), post=post, digests=dict(DIGESTS), **kw)
    b._count_tokens = lambda text: 99
    b.requester.count_tokens = b._count_tokens
    return b


def test_openai_endpoint_used_when_logprobs_present():
    urls = []
    b = _backend(lambda url, payload, h, t: urls.append(url) or _openai())
    r = b.execute_node(NODE, {}, SMALL_FIDELITY, {"problem": "2+2"})
    assert urls == ["http://localhost:11434/v1/chat/completions"]
    assert r.metadata["confidence_source"] == "logprobs"
    assert r.metadata["model"] == "qwen2.5:1.5b-instruct"


def test_falls_back_to_native_api_and_stays_there():
    urls = []

    def post(url, payload, h, t):
        urls.append(url)
        if url.endswith("/api/chat"):
            assert payload["options"]["seed"] is not None and payload["stream"] is False
            return {"message": {"content": "#### 4"}, "logprobs": [{"token": "4", "logprob": -0.2}],
                    "prompt_eval_count": 12, "eval_count": 3}
        return _openai(logprobs=False)

    b = _backend(post)
    r1 = b.execute_node(NODE, {}, SMALL_FIDELITY, {"problem": "a"})
    r2 = b.execute_node(NODE, {}, SMALL_FIDELITY, {"problem": "b"})
    assert urls[0].endswith("/v1/chat/completions") and urls[1].endswith("/api/chat")
    assert urls[2].endswith("/api/chat")  # sticky: no second OpenAI attempt
    assert r1.metadata["confidence_source"] == r2.metadata["confidence_source"] == "logprobs"
    assert r1.metadata["prompt_tokens"] == 12


def test_zero_prompt_tokens_patched_from_tokenizer():
    b = _backend(lambda url, payload, h, t: _openai(prompt_tokens=0))
    r = b.execute_node(NODE, {}, SMALL_FIDELITY, {"problem": "x"})
    assert r.metadata["prompt_tokens"] == 99
    assert b.requester.stats.prompt_tokens_patched == 1


def test_cache_key_includes_model_digest(tmp_path):
    calls = []
    post = lambda url, payload, h, t: calls.append(1) or _openai()
    cache = GenerationCache(tmp_path / "c.sqlite")
    _backend(post, cache=cache).execute_node(NODE, {}, SMALL_FIDELITY, {"problem": "x"})
    _backend(post, cache=cache).execute_node(NODE, {}, SMALL_FIDELITY, {"problem": "x"})
    assert len(calls) == 1  # same digest: cache hit
    other = OllamaBackend(ollama_config(), post=post, cache=cache,
                          digests={**DIGESTS, "qwen2.5:1.5b-instruct": "eeee5555"})
    other.execute_node(NODE, {}, SMALL_FIDELITY, {"problem": "x"})
    assert len(calls) == 2  # new quantization/digest: miss


def test_missing_model_is_a_clear_error():
    with pytest.raises(VLLMConnectionError, match="ollama pull"):
        OllamaBackend(ollama_config(), post=lambda *a: _openai(), digests={})


def test_missing_logprobs_fails_loudly():
    def post(url, payload, h, t):
        if url.endswith("/api/chat"):
            return {"message": {"content": "4"}, "logprobs": None, "prompt_eval_count": 1, "eval_count": 1}
        return _openai(logprobs=False)

    b = _backend(post)
    with pytest.raises(MissingLogprobsError):
        for i in range(25):
            b.execute_node(NODE, {}, SMALL_FIDELITY, {"problem": f"p{i}"})
