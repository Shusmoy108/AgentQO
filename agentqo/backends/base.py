"""
Backend interface for model execution.

Defines:
- NodeResult: Output from running a node
- ModelBackend: Protocol for backends that can execute nodes

The backend abstraction enables:
- MockBackend for simulation (fills from quality channel)
- VLLMHTTPBackend for a live OpenAI-compatible vLLM server (Ask 1)
- Swapping backends without changing AgentQO logic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from agentqo.workflows.dag import Fidelity, NodeSpec, Workflow


@dataclass
class NodeResult:
    """Result from executing a node.
    
    Attributes:
        node_id: ID of the node that was executed
        output: The generated output (task-specific)
        correctness: Whether output is correct (for labeling/eval only, not used in production)
        confidence: Model's confidence in output [0, 1]
        embedding: Recycled embedding for EC prediction (shape: [embedding_dim])
        cost: Actual cost incurred (may differ from fidelity.cost due to variance)
        fidelity_used: Name of the fidelity level used
        metadata: Additional task-specific metadata
        
    Note: 
        - correctness is ground truth from simulator or task scorer, NOT available at runtime
        - embedding is the recycled internal representation (like TRAIL's layer embedding)
    """
    node_id: str
    output: Any
    correctness: bool
    confidence: float
    embedding: np.ndarray
    cost: float
    fidelity_used: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")
        if self.cost < 0:
            raise ValueError(f"cost must be non-negative, got {self.cost}")


class ModelBackend(Protocol):
    """Protocol for model backends that execute workflow nodes.
    
    A backend takes a node specification, input data, and fidelity choice,
    then returns a NodeResult with output, correctness signal, confidence,
    recycled embedding, and cost.
    
    Implementations:
    - MockBackend: Simulates execution using quality channel
    - VLLMHTTPBackend: Calls a vLLM OpenAI-compatible HTTP API
    """
    
    def execute_node(
        self,
        node: "NodeSpec",
        inputs: Dict[str, "NodeResult"],
        fidelity: "Fidelity",
        task_context: Dict[str, Any],
        rng: Optional[np.random.Generator] = None,
    ) -> NodeResult:
        """Execute a single node and return the result.
        
        Args:
            node: Specification of the node to execute
            inputs: Results from input nodes (node_id -> NodeResult)
            fidelity: The fidelity level to use for execution
            task_context: Task-specific context (e.g., problem description, ground truth)
            rng: Random number generator for reproducibility
            
        Returns:
            NodeResult containing output, correctness, confidence, embedding, cost
        """
        ...
    
    @property
    def embedding_dim(self) -> int:
        """Dimension of the recycled embedding vector."""
        ...
    
    def get_info(self) -> Dict[str, Any]:
        """Return backend metadata and configuration."""
        ...
