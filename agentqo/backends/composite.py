"""Text from one backend, embedding from a probe (WP6)."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict, Optional

import numpy as np

from agentqo.backends.base import NodeResult
from agentqo.backends.vllm_http import _output_as_text


class CompositeBackend:
    def __init__(self, text_backend: Any, probe: Any) -> None:
        self.text_backend = text_backend
        self.probe = probe

    @property
    def embedding_dim(self) -> int:
        return int(self.probe.dim)

    def execute_node(self, node, inputs, fidelity, task_context: Dict[str, Any],
                     rng: Optional[np.random.Generator] = None) -> NodeResult:
        result = self.text_backend.execute_node(node, inputs, fidelity, task_context, rng)
        emb = self.probe.encode(result.metadata.get("prompt") or "", _output_as_text(result.output))
        meta = {**result.metadata, "embedding_kind": self.probe.kind,
                "probe_ms": getattr(self.probe, "last_ms", 0.0)}
        return replace(result, embedding=emb, metadata=meta)

    def get_info(self) -> Dict[str, Any]:
        return {**self.text_backend.get_info(), "embeddings": self.probe.kind,
                "embedding_dim": self.embedding_dim,
                "probe_model": getattr(self.probe, "model_id", None),
                "probe_layer": getattr(self.probe, "layer", None)}

    def __getattr__(self, name: str) -> Any:
        # Call counters, cache, and config live on the text backend.
        return getattr(self.text_backend, name)
