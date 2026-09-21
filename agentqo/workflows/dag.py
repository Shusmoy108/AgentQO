"""
Core DAG abstractions for AgentQO workflows.

Defines:
- Fidelity: (cost, base_error_rate) option for a node
- NodeSpec: Node specification with role, inputs, flags, fidelities
- NodeRole: Enumeration of node roles (planner, researcher, verifier, etc.)
- Workflow: The DAG plus graph helpers
- WorkflowBuilder: Fluent API for constructing workflows
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Set, Tuple


class NodeRole(enum.Enum):
    """Role of a node in the workflow DAG.
    
    Roles determine expected behavior and structural position:
    - PLANNER: Creates execution plans, typically root nodes
    - RESEARCHER: Gathers information, fan-out from planners
    - AGGREGATOR: Combines results from multiple inputs
    - VERIFIER: Validates outputs, may be optional
    - SAMPLER: Generates candidate outputs (for speculative groups)
    - FORMATTER: Formats final output, low criticality expected
    """
    PLANNER = "planner"
    RESEARCHER = "researcher"
    AGGREGATOR = "aggregator"
    VERIFIER = "verifier"
    SAMPLER = "sampler"
    FORMATTER = "formatter"


@dataclass(frozen=True)
class Fidelity:
    """A resource option for running a node.

    In the multi-LLM / multi-GPU setting a fidelity is a concrete serving
    choice, not just a cost scalar: which model, how many GPUs, which GPU
    type. The simulator uses ``cost`` and ``base_error_rate``; a real backend
    uses ``model_id`` / ``num_gpus`` to dispatch.

    Invariants:
        - Higher cost should correlate with lower error rate
        - cost > 0, num_gpus >= 1
        - 0 <= base_error_rate <= 1
    """

    name: str
    cost: float
    base_error_rate: float
    model_id: str = ""
    num_gpus: int = 1
    gpu_type: str = "sim"

    def __post_init__(self) -> None:
        if self.cost <= 0:
            raise ValueError(f"cost must be positive, got {self.cost}")
        if not 0 <= self.base_error_rate <= 1:
            raise ValueError(
                f"base_error_rate must be in [0, 1], got {self.base_error_rate}"
            )
        if self.num_gpus < 1:
            raise ValueError(f"num_gpus must be >= 1, got {self.num_gpus}")
        if not self.model_id:
            object.__setattr__(self, "model_id", self.name)

    @property
    def upgrade_key(self) -> Tuple[str, int, str]:
        """Identity of the serving choice for co-location / cost models."""
        return (self.model_id, self.num_gpus, self.gpu_type)


# Standard fidelity levels used across experiments.
# Small = cheap 7B-class model on one GPU. Large = 70B-class, more GPUs.
SMALL_FIDELITY = Fidelity(
    name="small",
    cost=1.0,
    base_error_rate=0.30,
    model_id="llm-7b",
    num_gpus=1,
    gpu_type="sim",
)
LARGE_FIDELITY = Fidelity(
    name="large",
    cost=4.0,
    base_error_rate=0.05,
    model_id="llm-70b",
    num_gpus=2,
    gpu_type="sim",
)
DEFAULT_FIDELITIES = [SMALL_FIDELITY, LARGE_FIDELITY]


@dataclass
class NodeSpec:
    """Specification of a node in the workflow DAG.
    
    Attributes:
        node_id: Unique identifier within the workflow
        role: Functional role (planner, researcher, verifier, etc.)
        inputs: List of node_ids this node depends on
        fidelities: Available (cost, error_rate) options for this node
        optional: If True, scheduler can skip this node
        speculative: If True, this is part of a speculative execution group
        speculative_group_id: ID grouping speculative branches (None if not speculative)
        description: Human-readable description of what this node does
        
    The optional and speculative flags enable:
    - optional: Scheduler can add, skip, or cancel this work
    - speculative: Groups of branches where any-correct counts as success
    """
    node_id: str
    role: NodeRole
    inputs: List[str] = field(default_factory=list)
    fidelities: List[Fidelity] = field(default_factory=lambda: list(DEFAULT_FIDELITIES))
    optional: bool = False
    speculative: bool = False
    speculative_group_id: Optional[str] = None
    description: str = ""
    
    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id cannot be empty")
        if not self.fidelities:
            raise ValueError("fidelities cannot be empty")
        if self.speculative and self.speculative_group_id is None:
            raise ValueError(
                "speculative nodes must have speculative_group_id"
            )


@dataclass
class Workflow:
    """A workflow DAG with graph analysis utilities.
    
    The workflow is a directed acyclic graph where:
    - Nodes represent LLM agent calls
    - Edges represent data dependencies (output -> input)
    
    Provides graph helpers for:
    - Topological ordering
    - Descendant computation
    - Fan-out and downstream reach analysis
    - Speculative group identification
    """
    name: str
    nodes: Dict[str, NodeSpec] = field(default_factory=dict)
    description: str = ""
    
    # Cached computed properties (invalidated on modification)
    _topo_order: Optional[List[str]] = field(default=None, repr=False)
    _descendants: Optional[Dict[str, FrozenSet[str]]] = field(default=None, repr=False)
    _ancestors: Optional[Dict[str, FrozenSet[str]]] = field(default=None, repr=False)
    _depths: Optional[Dict[str, int]] = field(default=None, repr=False)
    
    def __post_init__(self) -> None:
        self._validate_dag()
    
    def _invalidate_cache(self) -> None:
        """Invalidate all cached computed properties."""
        self._topo_order = None
        self._descendants = None
        self._ancestors = None
        self._depths = None
    
    def _validate_dag(self) -> None:
        """Validate that the graph is a valid DAG."""
        # Check all inputs reference existing nodes
        for node_id, node in self.nodes.items():
            for inp in node.inputs:
                if inp not in self.nodes:
                    raise ValueError(
                        f"Node '{node_id}' has input '{inp}' which does not exist"
                    )
        
        # Check for cycles using DFS
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            # Check all nodes that depend on this one (reverse edges for cycle detection)
            for other_id, other_node in self.nodes.items():
                if node_id in other_node.inputs:
                    if other_id not in visited:
                        if has_cycle(other_id):
                            return True
                    elif other_id in rec_stack:
                        return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in self.nodes:
            if node_id not in visited:
                if has_cycle(node_id):
                    raise ValueError(f"Workflow contains a cycle involving '{node_id}'")
    
    def add_node(self, node: NodeSpec) -> "Workflow":
        """Add a node to the workflow. Returns self for chaining."""
        if node.node_id in self.nodes:
            raise ValueError(f"Node '{node.node_id}' already exists")
        self.nodes[node.node_id] = node
        self._invalidate_cache()
        self._validate_dag()
        return self
    
    @property
    def topological_order(self) -> List[str]:
        """Return nodes in topological order (dependencies before dependents)."""
        if self._topo_order is not None:
            return self._topo_order
        
        in_degree: Dict[str, int] = {nid: 0 for nid in self.nodes}
        for node in self.nodes.values():
            for inp in node.inputs:
                # inp -> node edge means node has one more in-degree
                pass
            in_degree[node.node_id] = len(node.inputs)
        
        # Kahn's algorithm
        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        result: List[str] = []
        
        while queue:
            # Sort for deterministic order
            queue.sort()
            node_id = queue.pop(0)
            result.append(node_id)
            
            # For each node that depends on this one
            for other_id, other_node in self.nodes.items():
                if node_id in other_node.inputs:
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)
        
        self._topo_order = result
        return self._topo_order
    
    def get_descendants(self, node_id: str) -> FrozenSet[str]:
        """Get all descendants (transitive dependents) of a node."""
        if self._descendants is None:
            self._compute_descendants()
        return self._descendants[node_id]
    
    def _compute_descendants(self) -> None:
        """Compute descendants for all nodes."""
        self._descendants = {nid: frozenset() for nid in self.nodes}
        
        # Process in reverse topological order
        for node_id in reversed(self.topological_order):
            children = frozenset(
                other_id
                for other_id, other_node in self.nodes.items()
                if node_id in other_node.inputs
            )
            # Descendants = direct children + their descendants
            desc = set(children)
            for child_id in children:
                desc.update(self._descendants[child_id])
            self._descendants[node_id] = frozenset(desc)
    
    def get_ancestors(self, node_id: str) -> FrozenSet[str]:
        """Get all ancestors (transitive dependencies) of a node."""
        if self._ancestors is None:
            self._compute_ancestors()
        return self._ancestors[node_id]
    
    def _compute_ancestors(self) -> None:
        """Compute ancestors for all nodes."""
        self._ancestors = {nid: frozenset() for nid in self.nodes}
        
        # Process in topological order
        for node_id in self.topological_order:
            node = self.nodes[node_id]
            parents = frozenset(node.inputs)
            # Ancestors = direct parents + their ancestors
            anc = set(parents)
            for parent_id in parents:
                anc.update(self._ancestors[parent_id])
            self._ancestors[node_id] = frozenset(anc)
    
    def get_depth(self, node_id: str) -> int:
        """Get depth of a node (longest path from any root)."""
        if self._depths is None:
            self._compute_depths()
        return self._depths[node_id]
    
    def _compute_depths(self) -> None:
        """Compute depths for all nodes."""
        self._depths = {}
        
        for node_id in self.topological_order:
            node = self.nodes[node_id]
            if not node.inputs:
                self._depths[node_id] = 0
            else:
                self._depths[node_id] = 1 + max(
                    self._depths[inp] for inp in node.inputs
                )
    
    def get_fan_out(self, node_id: str) -> int:
        """Get fan-out (number of direct dependents) of a node."""
        return sum(
            1 for other_node in self.nodes.values()
            if node_id in other_node.inputs
        )
    
    def get_downstream_reach(self, node_id: str) -> int:
        """Get downstream reach (total number of descendants)."""
        return len(self.get_descendants(node_id))
    
    def has_downstream_verifier(self, node_id: str) -> bool:
        """Check if any descendant is a verifier node."""
        descendants = self.get_descendants(node_id)
        return any(
            self.nodes[desc_id].role == NodeRole.VERIFIER
            for desc_id in descendants
        )
    
    def get_speculative_groups(self) -> Dict[str, List[str]]:
        """Get mapping from speculative_group_id to list of node_ids."""
        groups: Dict[str, List[str]] = {}
        for node_id, node in self.nodes.items():
            if node.speculative and node.speculative_group_id:
                if node.speculative_group_id not in groups:
                    groups[node.speculative_group_id] = []
                groups[node.speculative_group_id].append(node_id)
        return groups
    
    def get_root_nodes(self) -> List[str]:
        """Get nodes with no inputs (entry points)."""
        return [
            node_id for node_id, node in self.nodes.items()
            if not node.inputs
        ]
    
    def get_leaf_nodes(self) -> List[str]:
        """Get nodes with no dependents (outputs)."""
        all_inputs = set()
        for node in self.nodes.values():
            all_inputs.update(node.inputs)
        return [
            node_id for node_id in self.nodes
            if node_id not in all_inputs or self.get_fan_out(node_id) == 0
        ]
    
    def get_terminal_nodes(self) -> List[str]:
        """Alias for get_leaf_nodes for clarity."""
        return self.get_leaf_nodes()
    
    def subgraph(self, node_ids: Set[str]) -> "Workflow":
        """Create a subgraph containing only the specified nodes."""
        new_nodes = {}
        for node_id in node_ids:
            if node_id not in self.nodes:
                raise ValueError(f"Node '{node_id}' not in workflow")
            old_node = self.nodes[node_id]
            # Filter inputs to only include nodes in subgraph
            new_inputs = [inp for inp in old_node.inputs if inp in node_ids]
            new_nodes[node_id] = NodeSpec(
                node_id=old_node.node_id,
                role=old_node.role,
                inputs=new_inputs,
                fidelities=old_node.fidelities,
                optional=old_node.optional,
                speculative=old_node.speculative,
                speculative_group_id=old_node.speculative_group_id,
                description=old_node.description,
            )
        
        return Workflow(
            name=f"{self.name}_subgraph",
            nodes=new_nodes,
            description=f"Subgraph of {self.name}",
        )


class WorkflowBuilder:
    """Fluent API for constructing workflows."""
    
    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._nodes: Dict[str, NodeSpec] = {}
    
    def add_node(
        self,
        node_id: str,
        role: NodeRole,
        inputs: Optional[List[str]] = None,
        fidelities: Optional[List[Fidelity]] = None,
        optional: bool = False,
        speculative: bool = False,
        speculative_group_id: Optional[str] = None,
        description: str = "",
    ) -> "WorkflowBuilder":
        """Add a node to the workflow being built."""
        if node_id in self._nodes:
            raise ValueError(f"Node '{node_id}' already exists")
        
        self._nodes[node_id] = NodeSpec(
            node_id=node_id,
            role=role,
            inputs=inputs or [],
            fidelities=fidelities or list(DEFAULT_FIDELITIES),
            optional=optional,
            speculative=speculative,
            speculative_group_id=speculative_group_id,
            description=description,
        )
        return self
    
    def add_planner(
        self,
        node_id: str,
        inputs: Optional[List[str]] = None,
        **kwargs,
    ) -> "WorkflowBuilder":
        """Convenience method to add a planner node."""
        return self.add_node(node_id, NodeRole.PLANNER, inputs, **kwargs)
    
    def add_researcher(
        self,
        node_id: str,
        inputs: Optional[List[str]] = None,
        **kwargs,
    ) -> "WorkflowBuilder":
        """Convenience method to add a researcher node."""
        return self.add_node(node_id, NodeRole.RESEARCHER, inputs, **kwargs)
    
    def add_aggregator(
        self,
        node_id: str,
        inputs: Optional[List[str]] = None,
        **kwargs,
    ) -> "WorkflowBuilder":
        """Convenience method to add an aggregator node."""
        return self.add_node(node_id, NodeRole.AGGREGATOR, inputs, **kwargs)
    
    def add_verifier(
        self,
        node_id: str,
        inputs: Optional[List[str]] = None,
        optional: bool = True,
        **kwargs,
    ) -> "WorkflowBuilder":
        """Convenience method to add a verifier node (optional by default)."""
        return self.add_node(node_id, NodeRole.VERIFIER, inputs, optional=optional, **kwargs)
    
    def add_sampler(
        self,
        node_id: str,
        inputs: Optional[List[str]] = None,
        speculative_group_id: Optional[str] = None,
        **kwargs,
    ) -> "WorkflowBuilder":
        """Convenience method to add a sampler node."""
        speculative = speculative_group_id is not None
        return self.add_node(
            node_id,
            NodeRole.SAMPLER,
            inputs,
            speculative=speculative,
            speculative_group_id=speculative_group_id,
            **kwargs,
        )
    
    def add_formatter(
        self,
        node_id: str,
        inputs: Optional[List[str]] = None,
        **kwargs,
    ) -> "WorkflowBuilder":
        """Convenience method to add a formatter node."""
        return self.add_node(node_id, NodeRole.FORMATTER, inputs, **kwargs)
    
    def build(self) -> Workflow:
        """Build and return the workflow."""
        return Workflow(
            name=self.name,
            nodes=self._nodes,
            description=self.description,
        )
