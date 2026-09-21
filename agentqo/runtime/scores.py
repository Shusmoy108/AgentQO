"""Proposal scoring functions: C_phys, EC, U(e), V_KV, I_b(t)."""

from __future__ import annotations

from typing import Dict, Iterable, Mapping, Optional, Set

from agentqo.workflows.dag import NodeRole, Workflow


def expected_quality(
    workflow: Workflow,
    ec: Mapping[str, float],
    skipped: Set[str],
    fidelities: Mapping[str, object],
) -> float:
    """Cheap Q̂(W): expected quality contribution of the current plan.

    Executed nodes contribute EC × yield(fidelity). Skipped optional work
    adds nothing. Skipped required work and skipped verifiers subtract.
    This is the runtime estimator in eq. (6), not the quality channel.
    """
    quality = 0.0
    for node_id, node in workflow.nodes.items():
        ec_v = float(ec.get(node_id, 0.0))
        if node_id in skipped:
            if node.role == NodeRole.VERIFIER:
                quality -= 0.40 * sum(ec.get(inp, 0.0) for inp in node.inputs)
            elif not node.optional:
                quality -= ec_v
            continue
        fid = fidelities.get(node_id)
        name = getattr(fid, "name", "small")
        yield_rate = 0.82 if name != "small" else 0.55
        quality += yield_rate * ec_v
    return float(max(0.0, min(1.0, quality)))


def marginal_edit_value(
    workflow: Workflow,
    ec: Mapping[str, float],
    skipped_before: Set[str],
    skipped_after: Set[str],
    fid_before: Mapping[str, object],
    fid_after: Mapping[str, object],
) -> float:
    """Proposal eq. (5): U(e) = Q̂(W⊕e) − Q̂(W)."""
    return expected_quality(workflow, ec, skipped_after, fid_after) - expected_quality(
        workflow, ec, skipped_before, fid_before
    )


def kv_value(
    reuse_prob: float,
    recompute_cost: float,
    ec_owner: float,
    kappa: float = 1.0,
) -> float:
    """Proposal eq. (7): V_KV(b) = P(reuse) · C_recompute · (1 + κ EC_v)."""
    return float(reuse_prob * recompute_cost * (1.0 + kappa * ec_owner))


def branch_index(
    expected_delta_q: float,
    expected_remain_cost: float,
) -> float:
    """Proposal eq. (8): I_b(t) = E[ΔQ|h] / E[C_remain|h]."""
    return float(expected_delta_q / max(expected_remain_cost, 1e-6))


def speculative_delta_q(
    n_done_correct: int,
    n_running: int,
    saturation: float = 0.45,
    p_correct: float = 0.55,
) -> float:
    """Diminishing value of one more unfinished speculative branch."""
    q_now = 1.0 - (1.0 - saturation) ** n_done_correct
    q_plus = 1.0 - (1.0 - saturation) ** (n_done_correct + p_correct)
    return max(0.0, q_plus - q_now) * max(n_running, 1)


def risk_term(
    workflow: Workflow,
    ec: Mapping[str, float],
    fidelities: Mapping[str, object],
    active: Iterable[str],
    contended: bool,
) -> float:
    """R̂: unprotected high-EC work currently in a contended GPU."""
    if not contended:
        return 0.0
    risk = 0.0
    for node_id in active:
        fid = fidelities.get(node_id)
        name = getattr(fid, "name", "small")
        if name == "small":
            risk += float(ec.get(node_id, 0.0))
    return risk
