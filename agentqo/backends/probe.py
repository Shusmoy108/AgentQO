"""Probe embeddings: a hidden state of one fixed model over prompt + output (WP6).

Every node is embedded by the same probe model (the small model by default),
whatever fidelity executed it, so all embeddings share one feature space.
"""

from __future__ import annotations

import threading
import time
from typing import Dict, Literal, Optional, Protocol

import numpy as np

from agentqo.backends.vllm_http import _placeholder_embedding


class ProbeEncoder(Protocol):
    dim: int
    kind: str

    def encode(self, prompt: str, output: Optional[str]) -> np.ndarray: ...


class PlaceholderProbe:
    """Hash embedding, for CI and dry runs only. H2 refuses it by default."""

    kind = "placeholder"

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def encode(self, prompt: str, output: Optional[str]) -> np.ndarray:
        return _placeholder_embedding(f"{prompt}\n{output or ''}", self.dim)


class HFHiddenStateProbe:
    """One prefill-only forward pass; pooled hidden state of ``layer``.

    ``layer=None`` picks about 40% depth. Layer 0 is the token embeddings.
    Forward passes are serialized with a lock (labeling calls this from
    many threads) and memoized on the exact text.
    """

    kind = "probe_hidden_state"

    def __init__(
        self,
        model_id: str,
        layer: Optional[int] = None,
        pool: Literal["mean", "last"] = "mean",
        device: Optional[str] = None,
        max_tokens: int = 1024,
    ) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self._torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available()
                                 else "mps" if torch.backends.mps.is_available() else "cpu")
        dtype = torch.float32 if self.device == "cpu" else torch.float16
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype).to(self.device).eval()
        n_layers = int(self.model.config.num_hidden_layers)
        self.layer = int(round(0.4 * n_layers)) if layer is None else layer
        if not 0 <= self.layer <= n_layers:
            raise ValueError(f"layer must be in [0, {n_layers}], got {self.layer}")
        self.pool = pool
        self.max_tokens = max_tokens
        self.dim = int(self.model.config.hidden_size)
        self.model_id = model_id
        self.last_ms = 0.0
        self._lock = threading.Lock()
        # ponytail: unbounded memo; bound it (LRU) if a run embeds millions of texts.
        self._memo: Dict[str, np.ndarray] = {}

    def encode(self, prompt: str, output: Optional[str]) -> np.ndarray:
        text = f"{prompt}\n{output or ''}"
        with self._lock:
            if text in self._memo:
                return self._memo[text]
            t0 = time.perf_counter()
            ids = self.tokenizer(text, return_tensors="pt", truncation=True,
                                 max_length=self.max_tokens).to(self.device)
            with self._torch.no_grad():
                hs = self.model(**ids, output_hidden_states=True).hidden_states[self.layer][0]
            vec = hs.mean(dim=0) if self.pool == "mean" else hs[-1]
            out = vec.float().cpu().numpy()
            self.last_ms = (time.perf_counter() - t0) * 1000
            self._memo[text] = out
            return out
