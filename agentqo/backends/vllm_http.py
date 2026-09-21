"""OpenAI-compatible HTTP client for a vLLM OpenAI server.

This is the real ModelBackend for Ask 1 (one GPU + ``vllm serve``).
It does **not** require a live server at construction time. Embeddings are
placeholders until a TRAIL-style mid-layer hook exists — do not use this
backend for H2 claims. Correctness comes only from an optional scorer in
``task_context``.
"""

from __future__ import annotations

import json
import math
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, TYPE_CHECKING
from zlib import crc32

import numpy as np

from agentqo.backends.base import NodeResult

if TYPE_CHECKING:
    from agentqo.workflows.dag import Fidelity, NodeSpec


ScorerFn = Callable[[str, "NodeSpec", Dict[str, Any]], bool]


@dataclass
class VLLMHTTPConfig:
    """Client config for one OpenAI-compatible vLLM endpoint."""

    base_url: str = "http://localhost:8000"
    api_key: str = "EMPTY"
    small_model: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    large_model: str = "meta-llama/Meta-Llama-3-70B-Instruct"
    max_tokens: int = 512
    temperature: float = 0.7
    timeout_s: float = 120.0
    embedding_dim: int = 256
    # Optional map: fidelity.name or fidelity.model_id -> served model id.
    model_map: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "VLLMHTTPConfig":
        """Build config from ``VLLM_*`` environment variables."""
        return cls(
            base_url=os.environ.get("VLLM_BASE_URL", "http://localhost:8000"),
            api_key=os.environ.get("VLLM_API_KEY", "EMPTY"),
            small_model=os.environ.get(
                "VLLM_SMALL_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct"
            ),
            large_model=os.environ.get(
                "VLLM_LARGE_MODEL", "meta-llama/Meta-Llama-3-70B-Instruct"
            ),
            max_tokens=int(os.environ.get("VLLM_MAX_TOKENS", "512")),
            temperature=float(os.environ.get("VLLM_TEMPERATURE", "0.7")),
            timeout_s=float(os.environ.get("VLLM_TIMEOUT_S", "120")),
            embedding_dim=int(os.environ.get("VLLM_EMBEDDING_DIM", "256")),
        )


class VLLMConnectionError(RuntimeError):
    """Raised when the vLLM HTTP endpoint is unreachable or returns an error."""


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
    ) -> None:
        self.config = config or VLLMHTTPConfig.from_env()
        self._embedding_dim = int(self.config.embedding_dim)
        # Injectable for unit tests (no live network).
        self._request_fn = request_fn or _http_json_post

    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim

    def get_info(self) -> Dict[str, Any]:
        return {
            "backend_type": "vllm_http",
            "base_url": self.config.base_url,
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
        model = self._resolve_model(fidelity)
        prompt = self._build_prompt(node, inputs, task_context)
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
            "temperature": self.config.temperature,
            "logprobs": True,
            "top_logprobs": 1,
        }
        t0 = time.perf_counter()
        try:
            data = self._request_fn(
                self._url("/v1/chat/completions"),
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

        text = _extract_text(data)
        confidence = _confidence_from_logprobs(data)
        embedding = _placeholder_embedding(text, self._embedding_dim)

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
                "base_url": self.config.base_url,
            },
        )

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

    def _url(self, path: str) -> str:
        base = self.config.base_url.rstrip("/")
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
