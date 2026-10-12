"""Ollama backend for the local real-model tier on the Mac (plan WP7b).

A ``VLLMHTTPBackend`` pointed at Ollama, with three Ollama-specific fixes:

- logprobs: call the OpenAI-compatible ``/v1/chat/completions`` first; if a
  response has no logprobs, switch (for the rest of the run) to the native
  ``/api/chat`` and convert its reply to the OpenAI shape;
- token counts: if Ollama reports ``prompt_tokens == 0`` (prompt served from
  its cache), count prompt tokens with the tokenizer instead;
- cache key: includes the model digest, so a different quantization under
  the same tag never reuses old generations.

Numbers from this backend are for debugging only: default Ollama builds are
4-bit quantized and are not the bf16 models served on Chameleon.
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional

from agentqo.backends.vllm_http import (
    VLLMConnectionError,
    VLLMHTTPBackend,
    VLLMHTTPConfig,
    _has_logprobs,
    _http_json_post,
)

DEFAULT_URL = "http://localhost:11434"


def ollama_config(**overrides: Any) -> VLLMHTTPConfig:
    cfg = VLLMHTTPConfig(
        base_url=os.environ.get("OLLAMA_URL", DEFAULT_URL),
        small_model=os.environ.get("OLLAMA_SMALL_MODEL", "qwen2.5:1.5b-instruct"),
        large_model=os.environ.get("OLLAMA_LARGE_MODEL", "qwen2.5:7b-instruct"),
        timeout_s=600.0,
    )
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


@dataclass
class _Stats:
    native_fallback: bool = False
    prompt_tokens_patched: int = 0


class OllamaRequester:
    """``request_fn`` for VLLMHTTPBackend: OpenAI endpoint, native fallback."""

    def __init__(self, base_url: str, count_tokens: Callable[[str], int],
                 post: Callable[..., Dict[str, Any]] = _http_json_post) -> None:
        self.base_url = base_url.rstrip("/")
        self.count_tokens = count_tokens
        self.post = post
        self.stats = _Stats()

    def __call__(self, url: str, payload: Dict[str, Any], headers: Mapping[str, str], timeout_s: float) -> Dict[str, Any]:
        if not self.stats.native_fallback:
            data = self.post(url, payload, headers, timeout_s)
            if _has_logprobs(data):
                return self._fix_usage(data, payload)
            self.stats.native_fallback = True
        return self._fix_usage(self._native(payload, headers, timeout_s), payload)

    def _native(self, payload: Dict[str, Any], headers: Mapping[str, str], timeout_s: float) -> Dict[str, Any]:
        body = {
            "model": payload["model"],
            "messages": payload["messages"],
            "stream": False,
            "logprobs": True,
            "top_logprobs": payload.get("top_logprobs", 1),
            "options": {"temperature": payload.get("temperature", 0.0),
                        "top_p": payload.get("top_p", 1.0),
                        "seed": payload.get("seed"),
                        "num_predict": payload.get("max_tokens")},
        }
        d = self.post(self.base_url + "/api/chat", body, headers, timeout_s)
        return {
            "choices": [{"message": d.get("message") or {},
                         "logprobs": {"content": d.get("logprobs") or []}}],
            "usage": {"prompt_tokens": d.get("prompt_eval_count") or 0,
                      "completion_tokens": d.get("eval_count") or 0},
            "model": d.get("model"),
        }

    def _fix_usage(self, data: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        usage = data.setdefault("usage", {})
        if not usage.get("prompt_tokens"):
            text = "\n".join(str(m.get("content", "")) for m in payload["messages"])
            usage["prompt_tokens"] = self.count_tokens(text)
            self.stats.prompt_tokens_patched += 1
        return data


class OllamaBackend(VLLMHTTPBackend):
    def __init__(
        self,
        config: Optional[VLLMHTTPConfig] = None,
        tokenizer_id: str = "Qwen/Qwen2.5-1.5B-Instruct",
        post: Callable[..., Dict[str, Any]] = _http_json_post,
        digests: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        config = config or ollama_config()
        self._tokenizer_id = tokenizer_id
        self._tokenizer = None
        self.requester = OllamaRequester(config.base_url, self._count_tokens, post)
        super().__init__(config, request_fn=self.requester, **kwargs)
        self.digests = digests if digests is not None else self._fetch_digests()
        for model in (config.small_model, config.large_model):
            if model not in self.digests:
                raise VLLMConnectionError(
                    f"Ollama has no model '{model}'. Run: ollama pull {model}"
                )

    def _fetch_digests(self) -> Dict[str, str]:
        try:
            with urllib.request.urlopen(self._url("/api/tags"), timeout=10) as resp:
                tags = json.loads(resp.read().decode())
        except OSError as exc:
            raise VLLMConnectionError(
                f"Cannot reach Ollama at {self.config.base_url} ({exc}). Start it with `ollama serve`."
            ) from exc
        return {m["name"]: m.get("digest", "") for m in tags.get("models", [])}

    def _cache_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        digest = self.digests.get(payload["model"], "")[:12]
        return {**payload, "model": f"ollama:{payload['model']}@{digest}"}

    def _count_tokens(self, text: str) -> int:
        if self._tokenizer is None:
            from transformers import AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(self._tokenizer_id)
        return len(self._tokenizer(text)["input_ids"])

    def get_info(self) -> Dict[str, Any]:
        return {**super().get_info(), "backend_type": "ollama",
                "digests": {m: self.digests.get(m, "")[:12]
                            for m in (self.config.small_model, self.config.large_model)},
                "native_fallback": self.requester.stats.native_fallback,
                "prompt_tokens_patched": self.requester.stats.prompt_tokens_patched}
