"""Backward-compatible exports for the vLLM HTTP backend.

Prefer importing from ``agentqo.backends.vllm_http``.
"""

from __future__ import annotations

from agentqo.backends.vllm_http import (
    VLLMConnectionError,
    VLLMHTTPBackend,
    VLLMHTTPConfig,
)

# Historical names used in docs / older imports.
VLLMBackendConfig = VLLMHTTPConfig
VLLMBackend = VLLMHTTPBackend

__all__ = [
    "VLLMHTTPConfig",
    "VLLMHTTPBackend",
    "VLLMConnectionError",
    "VLLMBackendConfig",
    "VLLMBackend",
]
