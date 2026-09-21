"""Metrics and reporting utilities."""

from agentqo.metrics.ranking import (
    compute_ranking_metrics,
    spearman_correlation,
    top_k_precision,
    kendall_tau,
)
from agentqo.metrics.quality_cost import (
    compute_quality_per_cost,
    compute_pareto_frontier,
)
from agentqo.metrics.report import (
    generate_h1_report,
    generate_h2_report,
    generate_h3_report,
    generate_full_report,
)

__all__ = [
    "compute_ranking_metrics",
    "spearman_correlation",
    "top_k_precision",
    "kendall_tau",
    "compute_quality_per_cost",
    "compute_pareto_frontier",
    "generate_h1_report",
    "generate_h2_report",
    "generate_h3_report",
    "generate_full_report",
]
