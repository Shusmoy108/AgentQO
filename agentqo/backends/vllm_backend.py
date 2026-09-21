"""
vLLM backend for real model execution (stub for later implementation).

This backend will:
- Run nodes on a served LLM via vLLM
- Extract recycled layer embeddings (TRAIL-style hook)
- Compute confidence from logprobs
- Return measured cost

Implementation deferred to GPU phase (Step 5 in the plan).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, TYPE_CHECKING

import numpy as np

from agentqo.backends.base import NodeResult

if TYPE_CHECKING:
    from agentqo.workflows.dag import Fidelity, NodeSpec


@dataclass
class VLLMBackendConfig:
    """Configuration for vLLM backend."""
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    embedding_layer: int = 11  # TRAIL default
    api_url: str = "http://localhost:8000"
    max_tokens: int = 512
    temperature: float = 0.7
    tensor_parallel_size: int = 1
    small_model: Optional[str] = "meta-llama/Meta-Llama-3-8B-Instruct"
    large_model: Optional[str] = "meta-llama/Meta-Llama-3-70B-Instruct"


class VLLMBackend:
    """Backend that runs nodes on vLLM-served models.
    
    Implements the ModelBackend protocol for real LLM execution.
    
    NOT YET IMPLEMENTED - This is a stub for the GPU phase (Step 5).
    """
    
    def __init__(self, config: VLLMBackendConfig) -> None:
        self.config = config
        self._embedding_dim = 4096  # LLaMA-3-8B hidden dimension
        raise NotImplementedError(
            "VLLMBackend is not yet implemented. "
            "Use MockBackend for simulation. "
            "Real model execution will be added in Step 5 (GPU phase)."
        )
    
    def execute_node(
        self,
        node: "NodeSpec",
        inputs: Dict[str, NodeResult],
        fidelity: "Fidelity",
        task_context: Dict[str, Any],
        rng: Optional[np.random.Generator] = None,
    ) -> NodeResult:
        """Execute node on vLLM backend."""
        raise NotImplementedError("VLLMBackend not yet implemented")
    
    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "backend_type": "vllm",
            "model_name": self.config.model_name,
            "embedding_layer": self.config.embedding_layer,
            "embedding_dim": self._embedding_dim,
            "status": "not_implemented",
        }
