"""
Value-aware allocation policies (H3).

Every node starts on the small fidelity. Given a per-node score and a fixed
budget, greedily upgrade the highest value-per-cost nodes to the large,
lower-error fidelity.

Policies:
1. AgentQO (ECPolicy): Score is predicted EC
2. ConfidencePolicy: Score is confidence
3. UniformPolicy: Upgrade uniformly (random selection)
4. AllSmallPolicy: No upgrades (baseline)
5. AllLargePolicy: All nodes on large (oracle upper bound)

Success for H3: AgentQO's quality-versus-cost curve sits above
confidence and uniform at equal cost.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from agentqo.workflows.dag import Fidelity, Workflow, SMALL_FIDELITY, LARGE_FIDELITY
from agentqo.executor import FidelityPlan


@dataclass
class AllocationResult:
    """Result of a budget allocation decision.
    
    Attributes:
        fidelity_plan: The resulting fidelity assignments
        nodes_upgraded: Set of nodes upgraded to large fidelity
        budget_used: Actual budget consumed
        budget_remaining: Unused budget
        allocation_scores: Per-node scores used for allocation
    """
    fidelity_plan: FidelityPlan
    nodes_upgraded: Set[str]
    budget_used: float
    budget_remaining: float
    allocation_scores: Dict[str, float]


class AllocationPolicy(abc.ABC):
    """Abstract base class for allocation policies."""
    
    @abc.abstractmethod
    def allocate(
        self,
        workflow: Workflow,
        budget: float,
        node_scores: Dict[str, float],
        small_fidelity: Fidelity = SMALL_FIDELITY,
        large_fidelity: Fidelity = LARGE_FIDELITY,
    ) -> AllocationResult:
        """Allocate budget to nodes.
        
        Args:
            workflow: The workflow DAG
            budget: Total budget available
            node_scores: Per-node scores (interpretation depends on policy)
            small_fidelity: Default (cheap) fidelity
            large_fidelity: Upgrade (expensive) fidelity
            
        Returns:
            AllocationResult with fidelity plan and metadata
        """
        ...
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Policy name for reporting."""
        ...


class UniformPolicy(AllocationPolicy):
    """Uniform allocation: upgrade nodes randomly within budget.
    
    Baseline that doesn't use any score information.
    """
    
    def __init__(self, random_state: int = 42) -> None:
        self.rng = np.random.default_rng(random_state)
    
    @property
    def name(self) -> str:
        return "Uniform"
    
    def allocate(
        self,
        workflow: Workflow,
        budget: float,
        node_scores: Dict[str, float],
        small_fidelity: Fidelity = SMALL_FIDELITY,
        large_fidelity: Fidelity = LARGE_FIDELITY,
    ) -> AllocationResult:
        # Base cost if all nodes use small fidelity
        base_cost = sum(small_fidelity.cost for _ in workflow.nodes)
        available_for_upgrades = budget - base_cost
        
        if available_for_upgrades <= 0:
            # Can't afford any upgrades
            return AllocationResult(
                fidelity_plan=FidelityPlan(default_fidelity=small_fidelity),
                nodes_upgraded=set(),
                budget_used=base_cost,
                budget_remaining=budget - base_cost,
                allocation_scores={},
            )
        
        # Shuffle nodes randomly
        node_ids = list(workflow.nodes.keys())
        self.rng.shuffle(node_ids)
        
        # Greedily upgrade until budget exhausted
        upgrade_cost = large_fidelity.cost - small_fidelity.cost
        nodes_upgraded: Set[str] = set()
        budget_used = base_cost
        
        for node_id in node_ids:
            if budget_used + upgrade_cost <= budget:
                nodes_upgraded.add(node_id)
                budget_used += upgrade_cost
        
        # Build fidelity plan
        assignments = {nid: large_fidelity for nid in nodes_upgraded}
        
        return AllocationResult(
            fidelity_plan=FidelityPlan(
                assignments=assignments,
                default_fidelity=small_fidelity,
            ),
            nodes_upgraded=nodes_upgraded,
            budget_used=budget_used,
            budget_remaining=budget - budget_used,
            allocation_scores={nid: 0.0 for nid in workflow.nodes},
        )


class ConfidencePolicy(AllocationPolicy):
    """Confidence-based allocation: upgrade low-confidence nodes first.
    
    Intuition: Uncertain nodes benefit most from more compute.
    """
    
    @property
    def name(self) -> str:
        return "Confidence"
    
    def allocate(
        self,
        workflow: Workflow,
        budget: float,
        node_scores: Dict[str, float],  # Confidence values
        small_fidelity: Fidelity = SMALL_FIDELITY,
        large_fidelity: Fidelity = LARGE_FIDELITY,
    ) -> AllocationResult:
        base_cost = sum(small_fidelity.cost for _ in workflow.nodes)
        available_for_upgrades = budget - base_cost
        
        if available_for_upgrades <= 0:
            return AllocationResult(
                fidelity_plan=FidelityPlan(default_fidelity=small_fidelity),
                nodes_upgraded=set(),
                budget_used=base_cost,
                budget_remaining=budget - base_cost,
                allocation_scores=node_scores,
            )
        
        # Sort by confidence (ascending - low confidence first)
        sorted_nodes = sorted(
            node_scores.items(),
            key=lambda x: x[1],  # Lower confidence = higher priority
        )
        
        upgrade_cost = large_fidelity.cost - small_fidelity.cost
        nodes_upgraded: Set[str] = set()
        budget_used = base_cost
        
        for node_id, confidence in sorted_nodes:
            if budget_used + upgrade_cost <= budget:
                nodes_upgraded.add(node_id)
                budget_used += upgrade_cost
        
        assignments = {nid: large_fidelity for nid in nodes_upgraded}
        
        return AllocationResult(
            fidelity_plan=FidelityPlan(
                assignments=assignments,
                default_fidelity=small_fidelity,
            ),
            nodes_upgraded=nodes_upgraded,
            budget_used=budget_used,
            budget_remaining=budget - budget_used,
            allocation_scores=node_scores,
        )


class ECPolicy(AllocationPolicy):
    """EC-based allocation: upgrade high-EC nodes first.
    
    This is the AgentQO policy. Nodes with high epistemic criticality
    get more resources because their errors have larger downstream impact.
    """
    
    @property
    def name(self) -> str:
        return "AgentQO"
    
    def allocate(
        self,
        workflow: Workflow,
        budget: float,
        node_scores: Dict[str, float],  # EC scores
        small_fidelity: Fidelity = SMALL_FIDELITY,
        large_fidelity: Fidelity = LARGE_FIDELITY,
    ) -> AllocationResult:
        base_cost = sum(small_fidelity.cost for _ in workflow.nodes)
        available_for_upgrades = budget - base_cost
        
        if available_for_upgrades <= 0:
            return AllocationResult(
                fidelity_plan=FidelityPlan(default_fidelity=small_fidelity),
                nodes_upgraded=set(),
                budget_used=base_cost,
                budget_remaining=budget - base_cost,
                allocation_scores=node_scores,
            )
        
        # Rank by value per extra GPU cost, not raw score. When every
        # upgrade costs the same this is equivalent to ranking by EC;
        # it stays correct if node fidelities later differ.
        upgrade_cost = large_fidelity.cost - small_fidelity.cost
        ranked = sorted(
            node_scores.items(),
            key=lambda x: -x[1] / max(upgrade_cost, 1e-9),
        )
        
        upgrade_cost = large_fidelity.cost - small_fidelity.cost
        nodes_upgraded: Set[str] = set()
        budget_used = base_cost
        
        for node_id, _score in ranked:
            if budget_used + upgrade_cost <= budget:
                nodes_upgraded.add(node_id)
                budget_used += upgrade_cost
        
        assignments = {nid: large_fidelity for nid in nodes_upgraded}
        
        return AllocationResult(
            fidelity_plan=FidelityPlan(
                assignments=assignments,
                default_fidelity=small_fidelity,
            ),
            nodes_upgraded=nodes_upgraded,
            budget_used=budget_used,
            budget_remaining=budget - budget_used,
            allocation_scores=node_scores,
        )


class OracleECPolicy(ECPolicy):
    """Upper bound: allocate by measured (oracle) EC, not predicted EC."""

    @property
    def name(self) -> str:
        return "Oracle-EC"


class AllSmallPolicy(AllocationPolicy):
    """All-small baseline: No upgrades, everything on small fidelity.

    Lower bound baseline.
    """

    @property
    def name(self) -> str:
        return "All-Small"
    
    def allocate(
        self,
        workflow: Workflow,
        budget: float,
        node_scores: Dict[str, float],
        small_fidelity: Fidelity = SMALL_FIDELITY,
        large_fidelity: Fidelity = LARGE_FIDELITY,
    ) -> AllocationResult:
        base_cost = sum(small_fidelity.cost for _ in workflow.nodes)
        
        return AllocationResult(
            fidelity_plan=FidelityPlan(default_fidelity=small_fidelity),
            nodes_upgraded=set(),
            budget_used=base_cost,
            budget_remaining=budget - base_cost,
            allocation_scores=node_scores,
        )


class AllLargePolicy(AllocationPolicy):
    """All-large policy: Everything on large fidelity.
    
    Upper bound (ignores budget constraint).
    """
    
    @property
    def name(self) -> str:
        return "All-Large"
    
    def allocate(
        self,
        workflow: Workflow,
        budget: float,
        node_scores: Dict[str, float],
        small_fidelity: Fidelity = SMALL_FIDELITY,
        large_fidelity: Fidelity = LARGE_FIDELITY,
    ) -> AllocationResult:
        total_cost = sum(large_fidelity.cost for _ in workflow.nodes)
        
        return AllocationResult(
            fidelity_plan=FidelityPlan(default_fidelity=large_fidelity),
            nodes_upgraded=set(workflow.nodes.keys()),
            budget_used=total_cost,
            budget_remaining=budget - total_cost,
            allocation_scores=node_scores,
        )


def allocate_budget(
    workflow: Workflow,
    budget: float,
    ec_scores: Dict[str, float],
    confidence_scores: Dict[str, float],
    policies: Optional[List[AllocationPolicy]] = None,
) -> Dict[str, AllocationResult]:
    """Allocate budget using multiple policies.
    
    Args:
        workflow: The workflow DAG
        budget: Total budget available
        ec_scores: Per-node EC scores (for ECPolicy)
        confidence_scores: Per-node confidence (for ConfidencePolicy)
        policies: List of policies to use (defaults to all standard policies)
        
    Returns:
        Dictionary mapping policy name to allocation result
    """
    if policies is None:
        policies = [
            ECPolicy(),
            ConfidencePolicy(),
            UniformPolicy(),
            AllSmallPolicy(),
        ]
    
    results = {}
    for policy in policies:
        if policy.name in ["AgentQO", "EC"]:
            scores = ec_scores
        elif policy.name == "Oracle-EC":
            scores = ec_scores
        elif policy.name == "Confidence":
            scores = confidence_scores
        else:
            scores = {}
        
        results[policy.name] = policy.allocate(
            workflow=workflow,
            budget=budget,
            node_scores=scores,
        )
    
    return results


def compute_quality_cost_curve(
    workflow: Workflow,
    task_model: Any,
    backend: Any,
    ec_scores: Dict[str, float],
    confidence_scores: Dict[str, float],
    budget_fractions: List[float] = [0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0],
    num_runs: int = 50,
    base_seed: int = 42,
    oracle_ec_scores: Optional[Dict[str, float]] = None,
) -> Dict[str, List[Tuple[float, float]]]:
    """Compute quality-vs-cost curves for different policies.
    
    Args:
        workflow: The workflow DAG
        task_model: Task quality model
        backend: Model backend
        ec_scores: Per-node EC scores
        confidence_scores: Per-node confidence scores
        budget_fractions: Budget levels as fractions of all-small cost
        num_runs: Number of runs per budget level
        base_seed: Random seed
        
    Returns:
        Dictionary mapping policy name to list of (cost, quality) points
    """
    from agentqo.executor import WorkflowExecutor
    from agentqo.workflows.dag import SMALL_FIDELITY, LARGE_FIDELITY
    
    executor = WorkflowExecutor(backend, task_model)
    rng = np.random.default_rng(base_seed)
    
    # Compute base cost (all small)
    base_cost = len(workflow.nodes) * SMALL_FIDELITY.cost
    
    policies: List[AllocationPolicy] = [
        ECPolicy(),
        ConfidencePolicy(),
        UniformPolicy(),
        AllSmallPolicy(),
    ]
    if oracle_ec_scores is not None:
        policies.insert(1, OracleECPolicy())
    
    curves: Dict[str, List[Tuple[float, float]]] = {p.name: [] for p in policies}
    
    for budget_frac in budget_fractions:
        budget = base_cost * budget_frac
        
        # Get allocations for each policy
        allocations = {}
        for policy in policies:
            if policy.name in ["AgentQO", "EC"]:
                scores = ec_scores
            elif policy.name == "Oracle-EC":
                scores = oracle_ec_scores or {}
            elif policy.name == "Confidence":
                scores = confidence_scores
            else:
                scores = {}
            
            allocations[policy.name] = policy.allocate(
                workflow=workflow,
                budget=budget,
                node_scores=scores,
            )
        
        # Run experiments for each policy
        for policy_name, allocation in allocations.items():
            if curves[policy_name] and curves[policy_name][-1][0] == allocation.budget_used:
                continue
            qualities = []
            for run_idx in range(num_runs):
                task_seed = int(rng.integers(0, 2**31))
                task = task_model.generate_task(workflow, np.random.default_rng(task_seed))
                
                record = executor.run_workflow(
                    workflow=workflow,
                    task=task,
                    fidelity_plan=allocation.fidelity_plan,
                    seed=task_seed,
                )
                
                qualities.append(record.final_quality)
            
            avg_quality = np.mean(qualities)
            curves[policy_name].append((allocation.budget_used, avg_quality))
    
    return curves


def analyze_h3_results(
    curves: Dict[str, List[Tuple[float, float]]],
) -> Dict[str, Any]:
    """Analyze H3 results: Does EC-based allocation beat baselines?
    
    H3: Spending GPU resources by predicted EC gives more task quality
    per unit of GPU cost than spending uniformly or by confidence.
    
    Success criteria: AgentQO curve is above Confidence and Uniform
    at equal cost levels.
    """
    agentqo_curve = curves.get("AgentQO", [])
    confidence_curve = curves.get("Confidence", [])
    uniform_curve = curves.get("Uniform", [])
    
    if not agentqo_curve or not confidence_curve or not uniform_curve:
        return {"h3_holds": False, "reason": "Missing curve data"}
    
    # Interpolate to compare at same cost levels
    def interpolate_quality(curve: List[Tuple[float, float]], cost: float) -> float:
        """Linear interpolation of quality at given cost."""
        costs = [c for c, q in curve]
        qualities = [q for c, q in curve]
        
        if cost <= costs[0]:
            return qualities[0]
        if cost >= costs[-1]:
            return qualities[-1]
        
        for i in range(len(costs) - 1):
            if costs[i] <= cost <= costs[i + 1]:
                t = (cost - costs[i]) / (costs[i + 1] - costs[i])
                return qualities[i] + t * (qualities[i + 1] - qualities[i])
        
        return qualities[-1]
    
    # Compare at AgentQO cost levels
    comparisons = []
    for cost, agentqo_quality in agentqo_curve:
        confidence_quality = interpolate_quality(confidence_curve, cost)
        uniform_quality = interpolate_quality(uniform_curve, cost)
        
        comparisons.append({
            "cost": cost,
            "agentqo_quality": agentqo_quality,
            "confidence_quality": confidence_quality,
            "uniform_quality": uniform_quality,
            "beats_confidence": agentqo_quality > confidence_quality,
            "beats_uniform": agentqo_quality > uniform_quality,
        })
    
    # H3 holds if AgentQO beats both at most cost levels
    beats_confidence_count = sum(c["beats_confidence"] for c in comparisons)
    beats_uniform_count = sum(c["beats_uniform"] for c in comparisons)
    
    h3_holds = (
        beats_confidence_count >= len(comparisons) * 0.6 and
        beats_uniform_count >= len(comparisons) * 0.6
    )
    
    # Compute area under curve for overall comparison
    def compute_auc(curve: List[Tuple[float, float]]) -> float:
        """Compute area under quality-cost curve."""
        if len(curve) < 2:
            return 0.0
        auc = 0.0
        for i in range(len(curve) - 1):
            c1, q1 = curve[i]
            c2, q2 = curve[i + 1]
            auc += (c2 - c1) * (q1 + q2) / 2
        return auc
    
    auc_agentqo = compute_auc(agentqo_curve)
    auc_confidence = compute_auc(confidence_curve)
    auc_uniform = compute_auc(uniform_curve)
    
    return {
        "h3_holds": h3_holds,
        "beats_confidence_fraction": beats_confidence_count / len(comparisons),
        "beats_uniform_fraction": beats_uniform_count / len(comparisons),
        "auc_agentqo": auc_agentqo,
        "auc_confidence": auc_confidence,
        "auc_uniform": auc_uniform,
        "auc_improvement_vs_confidence": (auc_agentqo - auc_confidence) / auc_confidence if auc_confidence > 0 else 0,
        "auc_improvement_vs_uniform": (auc_agentqo - auc_uniform) / auc_uniform if auc_uniform > 0 else 0,
        "point_comparisons": comparisons,
        "curves": curves,
    }
