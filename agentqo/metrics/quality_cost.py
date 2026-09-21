"""
Quality-cost metrics for allocation evaluation.

Measures how well allocation policies trade off quality and cost.
"""

from typing import Dict, List, Tuple

import numpy as np


def compute_quality_per_cost(
    quality: float,
    cost: float,
) -> float:
    """Compute quality per unit cost.
    
    Args:
        quality: Task quality score
        cost: Total cost incurred
        
    Returns:
        Quality per cost ratio
    """
    if cost <= 0:
        return 0.0
    return quality / cost


def compute_pareto_frontier(
    points: List[Tuple[float, float]],
) -> List[Tuple[float, float]]:
    """Compute Pareto frontier for (cost, quality) points.
    
    Points on the frontier are not dominated by any other point
    (no point has both lower cost AND higher quality).
    
    Args:
        points: List of (cost, quality) tuples
        
    Returns:
        List of points on the Pareto frontier
    """
    if not points:
        return []
    
    # Sort by cost ascending
    sorted_points = sorted(points, key=lambda p: p[0])
    
    frontier = []
    max_quality = float("-inf")
    
    for cost, quality in sorted_points:
        if quality > max_quality:
            frontier.append((cost, quality))
            max_quality = quality
    
    return frontier


def compute_area_under_curve(
    curve: List[Tuple[float, float]],
) -> float:
    """Compute area under a quality-cost curve.
    
    Uses trapezoidal integration.
    
    Args:
        curve: List of (cost, quality) points sorted by cost
        
    Returns:
        Area under the curve
    """
    if len(curve) < 2:
        return 0.0
    
    auc = 0.0
    for i in range(len(curve) - 1):
        c1, q1 = curve[i]
        c2, q2 = curve[i + 1]
        # Trapezoidal rule
        auc += (c2 - c1) * (q1 + q2) / 2
    
    return auc


def compute_area_between_curves(
    curve_a: List[Tuple[float, float]],
    curve_b: List[Tuple[float, float]],
) -> float:
    """Compute area between two quality-cost curves.
    
    Positive if curve_a is generally above curve_b.
    
    Args:
        curve_a: First curve (cost, quality) points
        curve_b: Second curve (cost, quality) points
        
    Returns:
        Signed area between curves
    """
    # Get all unique cost values
    costs = sorted(set(c for c, _ in curve_a) | set(c for c, _ in curve_b))
    
    if len(costs) < 2:
        return 0.0
    
    # Linear interpolation helper
    def interpolate(curve: List[Tuple[float, float]], cost: float) -> float:
        if not curve:
            return 0.0
        
        costs_c = [c for c, _ in curve]
        qualities = [q for _, q in curve]
        
        if cost <= costs_c[0]:
            return qualities[0]
        if cost >= costs_c[-1]:
            return qualities[-1]
        
        for i in range(len(costs_c) - 1):
            if costs_c[i] <= cost <= costs_c[i + 1]:
                t = (cost - costs_c[i]) / (costs_c[i + 1] - costs_c[i])
                return qualities[i] + t * (qualities[i + 1] - qualities[i])
        
        return qualities[-1]
    
    area = 0.0
    for i in range(len(costs) - 1):
        c1 = costs[i]
        c2 = costs[i + 1]
        
        qa1 = interpolate(curve_a, c1)
        qa2 = interpolate(curve_a, c2)
        qb1 = interpolate(curve_b, c1)
        qb2 = interpolate(curve_b, c2)
        
        # Difference at endpoints
        diff1 = qa1 - qb1
        diff2 = qa2 - qb2
        
        # Trapezoidal area of difference
        area += (c2 - c1) * (diff1 + diff2) / 2
    
    return area


def compare_allocation_curves(
    curves: Dict[str, List[Tuple[float, float]]],
    reference_policy: str = "AgentQO",
) -> Dict[str, Dict[str, float]]:
    """Compare quality-cost curves across policies.
    
    Args:
        curves: Dictionary mapping policy name to (cost, quality) points
        reference_policy: Policy to use as reference for comparisons
        
    Returns:
        Dictionary with comparison metrics
    """
    results = {}
    
    if reference_policy not in curves:
        return results
    
    ref_curve = curves[reference_policy]
    ref_auc = compute_area_under_curve(ref_curve)
    
    for policy_name, curve in curves.items():
        policy_auc = compute_area_under_curve(curve)
        area_diff = compute_area_between_curves(ref_curve, curve)
        
        results[policy_name] = {
            "auc": policy_auc,
            "auc_vs_reference": policy_auc - ref_auc,
            "area_diff_from_reference": area_diff,
            "pareto_frontier": compute_pareto_frontier(curve),
        }
    
    return results
