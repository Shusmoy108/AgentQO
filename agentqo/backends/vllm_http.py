"""OpenAI-compatible HTTP client for a vLLM OpenAI server.

This is the real ModelBackend (``vllm serve``; the fake server and Ollama
backends reuse it). It does **not** require a live server at construction
time. Embeddings are placeholders unless wrapped in a ``CompositeBackend``
with a probe; do not use placeholder embeddings for H2 claims. Correctness
comes only from an optional scorer in ``task_context``.

Per request: role prompt from ``prompt_fn`` (generic fallback), fixed seed,
per-role temperature, usage capture, and an optional generation cache.
Nodes that ``code_fn`` computes (majority vote) make no request at all.
"""

from __future__ import annotations

import json
import math
import os
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, TYPE_CHECKING
from zlib import crc32

import numpy as np

from agentqo.backends.base import NodeResult
from agentqo.workflows.dag import NodeRole

if TYPE_CHECKING:
    from agentqo.workflows.dag import Fidelity, NodeSpec


ScorerFn = Callable[[str, "NodeSpec", Dict[str, Any]], bool]
PromptFn = Callable[["NodeSpec", Dict[str, NodeResult], Dict[str, Any]], str]
CodeFn = Callable[["NodeSpec", Dict[str, NodeResult], Dict[str, Any]], Optional[str]]


@dataclass
class VLLMHTTPConfig:
    """Client config for one OpenAI-compatible vLLM endpoint."""

    base_url: str = "http://localhost:8000"
    api_key: str = "EMPTY"
    small_model: str = "Qwen/Qwen2.5-1.5B-Instruct"
    large_model: str = "Qwen/Qwen2.5-7B-Instruct"
    max_tokens: int = 512
    temperature: float = 0.7
    # Samplers (self-consistency branches) use this; other roles use temperature.
    sampler_temperature: float = 0.7
    top_p: float = 1.0
    timeout_s: float = 120.0
    embedding_dim: int = 256
    # Optional map: fidelity.name or fidelity.model_id -> served model id.
    model_map: Dict[str, str] = field(default_factory=dict)
    # Optional map: fidelity.name -> base URL (one server per model).
    endpoints: Dict[str, str] = field(default_factory=dict)
    allow_missing_logprobs: bool = False

    @classmethod
    def from_env(cls) -> "VLLMHTTPConfig":
        """Build config from ``VLLM_*`` environment variables."""
        return cls(
            base_url=os.environ.get("VLLM_BASE_URL", "http://localhost:8000"),
            api_key=os.environ.get("VLLM_API_KEY", "EMPTY"),
            small_model=os.environ.get("VLLM_SMALL_MODEL", cls.small_model),
            large_model=os.environ.get("VLLM_LARGE_MODEL", cls.large_model),
            endpoints=json.loads(os.environ.get("VLLM_ENDPOINTS", "{}")),
            max_tokens=int(os.environ.get("VLLM_MAX_TOKENS", "512")),
            temperature=float(os.environ.get("VLLM_TEMPERATURE", "0.7")),
            timeout_s=float(os.environ.get("VLLM_TIMEOUT_S", "120")),
            embedding_dim=int(os.environ.get("VLLM_EMBEDDING_DIM", "256")),
        )


class VLLMConnectionError(RuntimeError):
    """Raised when the vLLM HTTP endpoint is unreachable or returns an error."""


class MissingLogprobsError(RuntimeError):
    """Too many responses without logprobs: confidence would be a constant."""


MISSING_LOGPROBS_MAX = 0.05
MISSING_LOGPROBS_MIN_CALLS = 20


class VLLMHTTPBackend:
    """ModelBackend that calls a vLLM OpenAI-compatible HTTP API.

    Construct anytime; calls fail only when ``execute_node`` cannot reach the
    server. Multi-GPU physical placement is out of scope (Ask 2).
    """

    def __init__(
        self,
        config: Optional[VLLMHTTPConfig] = None,
        *,
        request_fn: Optional[Callable[[str, Dict[str, Any], Mapping[str, str], float], Dict[str, Any]]] = None,
        prompt_fn: Optional[PromptFn] = None,
        code_fn: Optional[CodeFn] = None,
        cache: Optional[Any] = None,
    ) -> None:
        self.config = config or VLLMHTTPConfig.from_env()
        self._embedding_dim = int(self.config.embedding_dim)
        # Injectable for unit tests (no live network).
        self._request_fn = request_fn or _http_json_post
        self.prompt_fn = prompt_fn
        self.code_fn = code_fn
        self.cache = cache
        self._stats_lock = threading.Lock()
        self.n_calls = 0
        self.n_http_calls = 0
        self.n_missing_logprobs = 0

    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim

    def get_info(self) -> Dict[str, Any]:
        return {
            "backend_type": "vllm_http",
            "base_url": self.config.base_url,
            "endpoints": dict(self.config.endpoints),
            "small_model": self.config.small_model,
            "large_model": self.config.large_model,
            "embedding_dim": self._embedding_dim,
            "embeddings": "placeholder",
            "status": "ready",
        }

    def health_check(self) -> bool:
        """Return True if ``/v1/models`` responds. Does not raise."""
        url = self._url("/v1/models")
        try:
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {self.config.api_key}"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=min(5.0, self.config.timeout_s)) as resp:
                return 200 <= getattr(resp, "status", 200) < 300
        except (urllib.error.URLError, TimeoutError, OSError):
            return False

    def execute_node(
        self,
        node: "NodeSpec",
        inputs: Dict[str, NodeResult],
        fidelity: "Fidelity",
        task_context: Dict[str, Any],
        rng: Optional[np.random.Generator] = None,
    ) -> NodeResult:
        code_fn = task_context.get("code_fn") or self.code_fn
        code_text = code_fn(node, inputs, task_context) if code_fn else None
        if code_text is not None:
            return self._code_result(node, code_text, task_context)

        model = self._resolve_model(fidelity)
        prompt_fn = task_context.get("prompt_fn") or self.prompt_fn
        prompt = prompt_fn(node, inputs, task_context) if prompt_fn else self._build_prompt(node, inputs, task_context)
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a node in an LLM-agent workflow. "
                        "Follow the role instructions and return only the node output."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self._temperature(node, task_context),
            "top_p": self.config.top_p,
            "seed": self._seed(node, task_context),
            "logprobs": True,
            "top_logprobs": 1,
        }
        data, latency, cache_hit = self._request(payload, fidelity)

        text = _extract_text(data)
        has_logprobs = _has_logprobs(data)
        self._record_call(has_logprobs)
        confidence = _confidence_from_logprobs(data)
        embedding = _placeholder_embedding(text, self._embedding_dim)
        usage = data.get("usage") or {}

        correctness, unknown = self._score(text, node, task_context)
        return NodeResult(
            node_id=node.node_id,
            output={
                "text": text,
                "node_id": node.node_id,
                "role": getattr(node.role, "value", str(node.role)),
            },
            correctness=correctness,
            confidence=confidence,
            embedding=embedding,
            cost=float(latency),
            fidelity_used=fidelity.name,
            metadata={
                "model": model,
                "latency_s": latency,
                "correctness_unknown": unknown,
                "embedding_kind": "placeholder",
                "base_url": self._base_for(fidelity),
                "prompt": prompt,
                "temperature": payload["temperature"],
                "seed": payload["seed"],
                "prompt_tokens": int(usage.get("prompt_tokens") or 0),
                "completion_tokens": int(usage.get("completion_tokens") or 0),
                "confidence_source": "logprobs" if has_logprobs else "missing",
                "cache_hit": cache_hit,
            },
        )

    def _request(self, payload: Dict[str, Any], fidelity: "Fidelity") -> tuple[Dict[str, Any], float, bool]:
        if self.cache is not None:
            hit = self.cache.get(payload)
            if hit is not None:
                return hit[0], hit[1], True
        t0 = time.perf_counter()
        try:
            data = self._request_fn(
                self._url("/v1/chat/completions", fidelity),
                payload,
                {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
                self.config.timeout_s,
            )
        except VLLMConnectionError:
            raise
        except Exception as exc:  # noqa: BLE001 — surface as connection error
            raise VLLMConnectionError(f"vLLM request failed: {exc}") from exc
        latency = time.perf_counter() - t0
        with self._stats_lock:
            self.n_http_calls += 1
        if self.cache is not None:
            self.cache.put(payload, data, latency)
        return data, latency, False

    def _record_call(self, has_logprobs: bool) -> None:
        with self._stats_lock:
            self.n_calls += 1
            self.n_missing_logprobs += 0 if has_logprobs else 1
            n, missing = self.n_calls, self.n_missing_logprobs
        if (
            not self.config.allow_missing_logprobs
            and n >= MISSING_LOGPROBS_MIN_CALLS
            and missing / n > MISSING_LOGPROBS_MAX
        ):
            raise MissingLogprobsError(
                f"{missing}/{n} responses had no logprobs; confidence would be a constant 0.5. "
                "Fix the server/endpoint, or pass allow_missing_logprobs for debugging only."
            )

    def _code_result(self, node: "NodeSpec", text: str, task_context: Dict[str, Any]) -> NodeResult:
        correctness, unknown = self._score(text, node, task_context)
        return NodeResult(
            node_id=node.node_id,
            output={"text": text, "node_id": node.node_id,
                    "role": getattr(node.role, "value", str(node.role))},
            correctness=correctness,
            confidence=1.0,
            embedding=_placeholder_embedding(text, self._embedding_dim),
            cost=0.0,
            fidelity_used="code",
            metadata={"code_node": True, "correctness_unknown": unknown,
                      "embedding_kind": "placeholder", "latency_s": 0.0,
                      "prompt_tokens": 0, "completion_tokens": 0},
        )

    def _temperature(self, node: "NodeSpec", task_context: Dict[str, Any]) -> float:
        if "temperature" in task_context:
            return float(task_context["temperature"])
        if node.role == NodeRole.SAMPLER:
            return float(self.config.sampler_temperature)
        return float(self.config.temperature)

    @staticmethod
    def _seed(node: "NodeSpec", task_context: Dict[str, Any]) -> int:
        """Fixed per (task, node, sample): same inputs -> same request."""
        if "seed" in task_context:
            return int(task_context["seed"])
        task = task_context.get("task")
        task_id = getattr(task, "task_id", "") or str(task_context.get("problem", ""))
        sample = task_context.get("sample_index", 0)
        return crc32(f"{task_id}|{node.node_id}|{sample}".encode()) & 0x7FFFFFFF

    def _resolve_model(self, fidelity: "Fidelity") -> str:
        name = fidelity.name
        mid = fidelity.model_id or ""
        if name in self.config.model_map:
            return self.config.model_map[name]
        if mid in self.config.model_map:
            return self.config.model_map[mid]
        if name == "large" or mid in {"llm-70b", "large"}:
            return self.config.large_model
        return self.config.small_model

    def _build_prompt(
        self,
        node: "NodeSpec",
        inputs: Dict[str, NodeResult],
        task_context: Dict[str, Any],
    ) -> str:
        role = getattr(node.role, "value", str(node.role))
        desc = node.description or f"Execute {role} node '{node.node_id}'."
        problem = str(task_context.get("problem") or task_context.get("query") or "")
        if not problem:
            task = task_context.get("task")
            if task is not None:
                meta = getattr(task, "metadata", None) or {}
                if isinstance(meta, dict):
                    problem = str(meta.get("problem") or meta.get("query") or "")

        parts = [
            f"Role: {role}",
            f"Node: {node.node_id}",
            f"Instructions: {desc}",
        ]
        if problem:
            parts.append(f"Task: {problem}")

        if inputs:
            parts.append("Upstream outputs:")
            for inp_id, result in inputs.items():
                text = _output_as_text(result.output)
                parts.append(f"- {inp_id}: {text}")
        parts.append("Produce the output for this node.")
        return "\n".join(parts)

    def _score(
        self,
        text: str,
        node: "NodeSpec",
        task_context: Dict[str, Any],
    ) -> tuple[bool, bool]:
        scorer = task_context.get("scorer")
        if callable(scorer):
            return bool(scorer(text, node, task_context)), False
        return False, True

    def _base_for(self, fidelity: Optional["Fidelity"]) -> str:
        if fidelity is not None and fidelity.name in self.config.endpoints:
            return self.config.endpoints[fidelity.name]
        return self.config.base_url

    def _url(self, path: str, fidelity: Optional["Fidelity"] = None) -> str:
        base = self._base_for(fidelity).rstrip("/")
        if not path.startswith("/"):
            path = "/" + path
        return base + path


def _http_json_post(
    url: str,
    payload: Dict[str, Any],
    headers: Mapping[str, str],
    timeout_s: float,
) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise VLLMConnectionError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise VLLMConnectionError(
            f"Cannot reach vLLM at {url} ({exc.reason}). "
            "Start a server, e.g. "
            "`vllm serve meta-llama/Meta-Llama-3-8B-Instruct --port 8000`."
        ) from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise VLLMConnectionError(f"Invalid JSON from vLLM: {raw[:200]}") from exc


def _extract_text(data: Dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if not choices:
        return ""
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    if content is None:
        content = choices[0].get("text", "")
    return str(content).strip()


def _has_logprobs(data: Dict[str, Any]) -> bool:
    choices = data.get("choices") or []
    lp = choices[0].get("logprobs") if choices else None
    content = lp.get("content") if isinstance(lp, dict) else None
    return bool(content) and any(isinstance(i, dict) and "logprob" in i for i in content)


def _confidence_from_logprobs(data: Dict[str, Any]) -> float:
    """Mean token probability from chat logprobs, else neutral 0.5."""
    choices = data.get("choices") or []
    if not choices:
        return 0.5
    lp = choices[0].get("logprobs")
    if not lp:
        return 0.5
    # OpenAI chat format: logprobs.content = [{token, logprob, ...}, ...]
    content = lp.get("content") if isinstance(lp, dict) else None
    if not content:
        return 0.5
    probs: List[float] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        if "logprob" in item:
            probs.append(math.exp(float(item["logprob"])))
    if not probs:
        return 0.5
    return float(np.clip(float(np.mean(probs)), 0.01, 0.99))


def _placeholder_embedding(text: str, dim: int) -> np.ndarray:
    """Deterministic hash embedding — not a TRAIL recycled activation."""
    vec = np.zeros(dim, dtype=np.float32)
    if not text:
        return vec
    seed = crc32(text.encode("utf-8")) & 0xFFFFFFFF
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal(dim).astype(np.float32)
    norm = float(np.linalg.norm(raw) + 1e-8)
    return raw / norm


def _output_as_text(output: Any) -> str:
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    if isinstance(output, dict):
        if "text" in output:
            return str(output["text"])
        return json.dumps(output, default=str)
    return str(output)
