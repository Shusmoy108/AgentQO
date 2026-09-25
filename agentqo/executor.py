"""
Workflow executor with override support for fault injection.

The executor:
1. Runs a workflow under a chosen per-node fidelity plan
2. Supports optional skipping of optional nodes
3. Supports forced correctness for chosen nodes (fault injection)
4. Supports descendant-only recompute when only a subgraph changes

This enables correct and cheap EC labeling via fault injection.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from agentqo.backends.base import ModelBackend, NodeResult
from agentqo.workflows.dag import Fidelity, NodeSpec, Workflow


@dataclass
class FidelityPlan:
    """Per-node fidelity assignment for workflow execution.
    
    Attributes:
        assignments: Mapping from node_id to fidelity to use
        default_fidelity: Fidelity to use for nodes not in assignments
    """
    assignments: Dict[str, Fidelity] = field(default_factory=dict)
    default_fidelity: Optional[Fidelity] = None
    
    def get_fidelity(self, node: NodeSpec) -> Fidelity:
        """Get fidelity for a node."""
        if node.node_id in self.assignments:
            return self.assignments[node.node_id]
        if self.default_fidelity:
            return self.default_fidelity
        # Use first fidelity from node's options
        return node.fidelities[0]


@dataclass
class ExecutionOverrides:
    """Overrides for workflow execution (used in fault injection).
    
    Attributes:
        forced_correctness: Mapping from node_id to forced correctness value
        skip_nodes: Set of optional node_ids to skip
        force_outputs: Mapping from node_id to forced output value (a
            NodeResult is used as-is; anything else becomes the output)
        skip_forced_execution: If True, a forced-output node is not executed
            at all (no wasted backend call before the output is replaced)
    """
    forced_correctness: Dict[str, bool] = field(default_factory=dict)
    skip_nodes: Set[str] = field(default_factory=set)
    force_outputs: Dict[str, Any] = field(default_factory=dict)
    skip_forced_execution: bool = True


@dataclass
class RunRecord:
    """Record of a complete workflow run.
    
    Attributes:
        run_id: Unique identifier for this run
        workflow_name: Name of the workflow that was run
        task_id: ID of the task instance
        final_quality: Final task quality score [0, 1]
        total_cost: Sum of costs across all executed nodes
        node_results: Per-node execution results
        skipped_nodes: Set of nodes that were skipped
        cancelled_nodes: Set of nodes cancelled during execution
        fidelity_plan: The fidelity assignments used
        overrides: Any execution overrides applied
        seed: Random seed used for reproducibility
        metadata: Additional run-specific data
    """
    run_id: str
    workflow_name: str
    task_id: str
    final_quality: float
    total_cost: float
    node_results: Dict[str, NodeResult]
    skipped_nodes: Set[str] = field(default_factory=set)
    cancelled_nodes: Set[str] = field(default_factory=set)
    fidelity_plan: Optional[FidelityPlan] = None
    overrides: Optional[ExecutionOverrides] = None
    seed: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowExecutor:
    """Executes workflows with support for fault injection and partial recompute.
    
    The executor provides:
    1. Full workflow execution with per-node fidelity control
    2. Optional node skipping
    3. Forced correctness overrides for fault injection
    4. Descendant-only recompute for efficient labeling
    """
    
    def __init__(
        self,
        backend: ModelBackend,
        task_model: Any,  # TaskModel
    ) -> None:
        """Initialize executor.
        
        Args:
            backend: The model backend to use for node execution
            task_model: The task quality model for computing final quality
        """
        self.backend = backend
        self.task_model = task_model
        self._run_counter = 0
    
    def run_workflow(
        self,
        workflow: Workflow,
        task: Any,  # TaskInstance
        fidelity_plan: Optional[FidelityPlan] = None,
        overrides: Optional[ExecutionOverrides] = None,
        seed: Optional[int] = None,
    ) -> RunRecord:
        """Execute a complete workflow.
        
        Args:
            workflow: The workflow DAG to execute
            task: The task instance with hidden properties
            fidelity_plan: Per-node fidelity assignments (uses defaults if None)
            overrides: Execution overrides for fault injection
            seed: Random seed for reproducibility
            
        Returns:
            RunRecord with all results and quality score
        """
        if seed is None:
            seed = np.random.default_rng().integers(0, 2**31)
        
        rng = np.random.default_rng(seed)
        
        if fidelity_plan is None:
            fidelity_plan = FidelityPlan()
        
        if overrides is None:
            overrides = ExecutionOverrides()
        
        # Generate run ID
        self._run_counter += 1
        run_id = f"run_{self._run_counter}_{seed}"
        
        # Execute nodes in topological order
        node_results: Dict[str, NodeResult] = {}
        skipped_nodes: Set[str] = set()
        total_cost = 0.0
        
        task_context = {
            "task": task,
            "workflow": workflow,
            "results": node_results,
        }
        
        for node_id in workflow.topological_order:
            node = workflow.nodes[node_id]
            
            if node_id in overrides.skip_nodes:
                if not _skippable(node):
                    raise ValueError(
                        f"Cannot skip required node '{node_id}'"
                    )
                skipped_nodes.add(node_id)
                continue

            if not _inputs_satisfied(node, node_results, skipped_nodes, workflow):
                if node.optional:
                    skipped_nodes.add(node_id)
                    continue
                raise ValueError(
                    f"Required inputs missing for node '{node_id}'"
                )
            
            # Gather input results
            input_results = {
                inp: node_results[inp] for inp in node.inputs
                if inp in node_results
            }
            
            # Get fidelity for this node
            fidelity = fidelity_plan.get_fidelity(node)
            
            result = self._execute(node, input_results, fidelity, task_context, rng, overrides)
            node_results[node_id] = result
            total_cost += result.cost
        
        # Compute final quality
        final_quality = self.task_model.compute_quality(
            task, node_results, workflow
        )
        
        return RunRecord(
            run_id=run_id,
            workflow_name=workflow.name,
            task_id=task.task_id,
            final_quality=final_quality,
            total_cost=total_cost,
            node_results=node_results,
            skipped_nodes=skipped_nodes,
            cancelled_nodes=set(),
            fidelity_plan=fidelity_plan,
            overrides=overrides,
            seed=seed,
            metadata={
                "task_type": task.task_type,
                "task_difficulty": task.difficulty,
            },
        )
    
    def _execute(
        self,
        node: NodeSpec,
        inputs: Dict[str, NodeResult],
        fidelity: Fidelity,
        task_context: Dict[str, Any],
        rng: np.random.Generator,
        overrides: ExecutionOverrides,
    ) -> NodeResult:
        nid = node.node_id
        if overrides.skip_forced_execution and nid in overrides.force_outputs:
            return _forced_result(node, overrides, self.backend)
        result = self.backend.execute_node(
            node=node,
            inputs=inputs,
            fidelity=fidelity,
            task_context=task_context,
            rng=rng,
        )
        return _apply_overrides(result, nid, overrides)

    def run_with_partial_recompute(
        self,
        workflow: Workflow,
        task: Any,
        baseline_results: Dict[str, NodeResult],
        changed_nodes: Set[str],
        overrides: ExecutionOverrides,
        fidelity_plan: Optional[FidelityPlan] = None,
        seed: Optional[int] = None,
    ) -> RunRecord:
        """Execute a workflow recomputing only affected nodes.
        
        This is used for efficient fault injection labeling:
        1. Run baseline once
        2. For each node v, force v to different correctness
        3. Only recompute v and its descendants
        
        Args:
            workflow: The workflow DAG
            task: The task instance
            baseline_results: Results from a previous full run
            changed_nodes: Nodes whose state has changed (must recompute)
            overrides: Execution overrides (including forced correctness)
            fidelity_plan: Fidelity assignments
            seed: Random seed
            
        Returns:
            RunRecord with mixed baseline + recomputed results
            
        Invariant:
            Nodes not in descendants(changed_nodes) ∪ changed_nodes
            have byte-identical results to baseline.
        """
        if seed is None:
            seed = np.random.default_rng().integers(0, 2**31)
        
        rng = np.random.default_rng(seed)
        
        if fidelity_plan is None:
            fidelity_plan = FidelityPlan()
        
        # Compute nodes that need recomputation
        nodes_to_recompute: Set[str] = set(changed_nodes)
        for node_id in changed_nodes:
            nodes_to_recompute.update(workflow.get_descendants(node_id))
        
        # Generate run ID
        self._run_counter += 1
        run_id = f"partial_run_{self._run_counter}_{seed}"
        
        # Start with baseline results for unchanged nodes
        node_results: Dict[str, NodeResult] = {}
        skipped_nodes: Set[str] = set()
        total_cost = 0.0
        
        task_context = {
            "task": task,
            "workflow": workflow,
            "results": node_results,
        }
        
        for node_id in workflow.topological_order:
            node = workflow.nodes[node_id]
            
            if node_id in overrides.skip_nodes:
                if not _skippable(node):
                    raise ValueError(
                        f"Cannot skip required node '{node_id}'"
                    )
                skipped_nodes.add(node_id)
                continue

            available = {
                inp for inp in node.inputs
                if inp in node_results or inp in baseline_results
            }
            skipped_or_done = skipped_nodes | set(node_results) | set(baseline_results)
            if not _inputs_satisfied_from_sets(node, available, skipped_or_done, workflow):
                if node.optional:
                    skipped_nodes.add(node_id)
                    continue
                raise ValueError(
                    f"Required inputs missing for node '{node_id}'"
                )
            
            if node_id not in nodes_to_recompute:
                # Use baseline result (must exist)
                if node_id not in baseline_results:
                    raise ValueError(
                        f"Baseline missing result for node '{node_id}'"
                    )
                result = baseline_results[node_id]
                node_results[node_id] = result
                total_cost += result.cost
            else:
                # Recompute this node
                # Gather input results (may be mix of baseline and recomputed)
                input_results = {}
                for inp in node.inputs:
                    if inp in node_results:
                        input_results[inp] = node_results[inp]
                    elif inp in baseline_results:
                        input_results[inp] = baseline_results[inp]
                
                fidelity = fidelity_plan.get_fidelity(node)
                
                result = self._execute(node, input_results, fidelity, task_context, rng, overrides)
                node_results[node_id] = result
                total_cost += result.cost
        
        # Compute final quality
        final_quality = self.task_model.compute_quality(
            task, node_results, workflow
        )
        
        return RunRecord(
            run_id=run_id,
            workflow_name=workflow.name,
            task_id=task.task_id,
            final_quality=final_quality,
            total_cost=total_cost,
            node_results=node_results,
            skipped_nodes=skipped_nodes,
            cancelled_nodes=set(),
            fidelity_plan=fidelity_plan,
            overrides=overrides,
            seed=seed,
            metadata={
                "partial_recompute": True,
                "changed_nodes": list(changed_nodes),
                "recomputed_nodes": list(nodes_to_recompute),
            },
        )


def verify_partial_recompute_invariant(
    baseline_record: RunRecord,
    partial_record: RunRecord,
    changed_nodes: Set[str],
    workflow: Workflow,
) -> Tuple[bool, List[str]]:
    """Verify the partial recompute invariant holds.
    
    Invariant: Nodes not in descendants(changed_nodes) ∪ changed_nodes
    have identical results to baseline.
    
    Args:
        baseline_record: The full baseline run
        partial_record: The partial recompute run  
        changed_nodes: Nodes that were changed
        workflow: The workflow DAG
        
    Returns:
        (is_valid, list_of_violations)
    """
    # Compute nodes that should be unchanged
    affected_nodes: Set[str] = set(changed_nodes)
    for node_id in changed_nodes:
        affected_nodes.update(workflow.get_descendants(node_id))
    
    unchanged_nodes = set(workflow.nodes.keys()) - affected_nodes
    
    violations = []
    for node_id in unchanged_nodes:
        if node_id in baseline_record.skipped_nodes:
            if node_id not in partial_record.skipped_nodes:
                violations.append(f"{node_id}: baseline skipped but partial not skipped")
            continue
        
        if node_id in partial_record.skipped_nodes:
            violations.append(f"{node_id}: partial skipped but baseline not skipped")
            continue
        
        baseline_result = baseline_record.node_results.get(node_id)
        partial_result = partial_record.node_results.get(node_id)
        
        if baseline_result is None and partial_result is None:
            continue
        
        if baseline_result is None or partial_result is None:
            violations.append(f"{node_id}: result missing in one record")
            continue
        
        if baseline_result.correctness != partial_result.correctness:
            violations.append(f"{node_id}: correctness differs")
        if baseline_result.fidelity_used != partial_result.fidelity_used:
            violations.append(f"{node_id}: fidelity differs")
        if baseline_result is not partial_result:
            # Plan invariant: non-descendants are byte-identical, not merely
            # equal after a fresh sample. Same object ⇒ same embedding bytes.
            if baseline_result.confidence != partial_result.confidence:
                violations.append(f"{node_id}: confidence differs")
            if not np.array_equal(baseline_result.embedding, partial_result.embedding):
                violations.append(f"{node_id}: embedding differs")
            if baseline_result.cost != partial_result.cost:
                violations.append(f"{node_id}: cost differs")

    return len(violations) == 0, violations


def _apply_overrides(
    result: NodeResult,
    node_id: str,
    overrides: ExecutionOverrides,
) -> NodeResult:
    """Apply forced correctness / output without resampling the node."""
    meta = dict(result.metadata)
    updates: Dict[str, Any] = {}
    if node_id in overrides.forced_correctness:
        updates["correctness"] = overrides.forced_correctness[node_id]
        meta["correctness_forced"] = True
    if node_id in overrides.force_outputs:
        updates["output"] = overrides.force_outputs[node_id]
        meta["output_forced"] = True
    if not updates:
        return result
    updates["metadata"] = meta
    return replace(result, **updates)


def _forced_result(node: NodeSpec, overrides: ExecutionOverrides, backend: Any) -> NodeResult:
    """Result for a forced node that was never executed."""
    nid = node.node_id
    value = overrides.force_outputs[nid]
    if isinstance(value, NodeResult):
        result = replace(value, node_id=nid, metadata={**value.metadata, "output_forced": True})
    else:
        result = NodeResult(
            node_id=nid,
            output=value,
            correctness=False,
            confidence=0.5,
            embedding=np.zeros(int(getattr(backend, "embedding_dim", 1)), dtype=np.float32),
            cost=0.0,
            fidelity_used="forced",
            metadata={"output_forced": True},
        )
    if nid in overrides.forced_correctness:
        result = replace(result, correctness=overrides.forced_correctness[nid],
                         metadata={**result.metadata, "correctness_forced": True})
    return result


def _skippable(node: NodeSpec) -> bool:
    """Optional and speculative nodes are the proposal's runtime edit points."""
    return bool(node.optional or node.speculative)


def _inputs_satisfied(
    node: NodeSpec,
    node_results: Dict[str, NodeResult],
    skipped_nodes: Set[str],
    workflow: Workflow,
) -> bool:
    for inp in node.inputs:
        if inp in node_results:
            continue
        if inp in skipped_nodes and _skippable(workflow.nodes[inp]):
            continue
        return False
    return True


def _inputs_satisfied_from_sets(
    node: NodeSpec,
    available: Set[str],
    skipped_or_done: Set[str],
    workflow: Workflow,
) -> bool:
    for inp in node.inputs:
        if inp in available:
            continue
        if inp in skipped_or_done and _skippable(workflow.nodes[inp]):
            continue
        return False
    return True
