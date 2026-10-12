"""Event-driven joint search over (edit e, physical plan P). Proposal §V.E."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from agentqo.runtime.cluster import Cluster
from agentqo.runtime.edits import Edit, apply_edit, candidate_edits, noop
from agentqo.runtime.scores import expected_quality, risk_term
from agentqo.simulator.interaction_model import CallSpec
from agentqo.workflows.dag import Fidelity, Workflow, SMALL_FIDELITY


@dataclass
class Decision:
    edit: Edit
    gpu_id: Optional[int]
    score: float
    q_hat: float
    latency_hat: float
    cost_hat: float
    risk_hat: float
    rationale: str = ""


@dataclass
class OptimizerConfig:
    lambda_l: float = 0.15
    lambda_c: float = 0.10
    lambda_r: float = 0.35
    lambda_move: float = 0.2
    lambda_reuse: float = 0.4
    # AgentIconq latencies are ~20–40 abstract ms per call. Divide so
    # λ_L L̂ and Q̂ live on the same scale in eq. (6).
    latency_scale: float = 25.0
    # Plan-level cost of remaining work, per unit of fidelity cost. The
    # placement terms above only price the next call, so an edit to a
    # future node (skip, downgrade) looked free. This term prices it.
    lambda_plan: float = 0.01
    # A non-noop edit must beat the best noop plan by this margin.
    # Stops add/cancel flip-flops on near-ties (hysteresis).
    edit_margin: float = 0.005
    # Reject edits whose Q̂ falls more than this below the starting plan's
    # Q̂ (the WP15 "within 2 points" rule, applied to the estimator).
    quality_floor_drop: float = 0.02


def edit_lock_key(edit: Edit) -> str:
    """What an edit touches. Once touched, it is not edited again."""
    if edit.kind == "set_width":
        return "__width__"
    return edit.node_id or edit.kind


class JointOptimizer:
    """max_{e,P} Q̂ − λ_L L̂ − λ_C Ĉ − λ_R R̂  (proposal eq. 6)."""

    def __init__(self, cluster: Cluster, config: Optional[OptimizerConfig] = None) -> None:
        self.cluster = cluster
        self.config = config or OptimizerConfig()

    def decide(
        self,
        workflow: Workflow,
        skipped: Set[str],
        cancelled: Set[str],
        completed: Set[str],
        active: Set[str],
        fidelities: Dict[str, Fidelity],
        ec: Dict[str, float],
        ready_nodes: List[str],
        prefix_id: str,
        locked: Optional[Set[str]] = None,
        q_floor: Optional[float] = None,
    ) -> Decision:
        locked = locked or set()
        edits = [
            e for e in candidate_edits(
                workflow, skipped, cancelled, completed, active, fidelities
            )
            if edit_lock_key(e) not in locked
        ]
        gpus = list(range(len(self.cluster.gpus)))
        best: Optional[Decision] = None
        best_noop: Optional[Decision] = None

        for edit in edits:
            skipped_e = set(skipped)
            cancelled_e = set(cancelled)
            fid_e = dict(fidelities)
            apply_edit(edit, skipped_e, cancelled_e, fid_e, workflow)
            q_hat = expected_quality(workflow, ec, skipped_e, fid_e)
            if edit.kind != "noop" and q_floor is not None and q_hat < q_floor:
                continue
            plan_cost = sum(
                getattr(fid_e.get(n), "cost", 1.0)
                for n in workflow.nodes
                if n not in skipped_e and n not in completed
            )

            # Placement is priced on the pre-edit ready set, so every edit
            # sees the same latency/cost terms. Otherwise skipping whatever
            # is ready now (e.g. the verifier) wins by zeroing those terms.
            # Edits are priced only by Q̂, lambda_plan and risk.
            live_ready = [
                n for n in ready_nodes
                if n not in skipped and n not in cancelled
            ]
            placements: List[Optional[int]] = [None] if not live_ready else list(gpus)

            for gpu_id in placements:
                latency = 0.0
                cost = 0.0
                move = 0.0
                reuse = 0.0
                if gpu_id is not None and live_ready:
                    node_id = max(live_ready, key=lambda n: ec.get(n, 0.0))
                    # Price placement with the pre-edit fidelity. Fidelity
                    # changes are priced once, through lambda_plan, so the
                    # node that happens to be ready now (often the planner)
                    # is not penalized for an upgrade that a not-yet-ready
                    # node would get for free.
                    fid = fidelities.get(node_id, SMALL_FIDELITY)
                    spec = CallSpec(
                        call_id="candidate",
                        model_id=fid.model_id,
                        gpu_id=gpu_id,
                        prompt_tokens=128,
                        decode_tokens=64,
                        prefix_id=prefix_id,
                    )
                    kv_here = list(self.cluster.gpus[gpu_id].kv.values())
                    if any(r.workflow_id == prefix_id for r in kv_here):
                        reuse = max(
                            r.recompute_cost for r in kv_here
                            if r.workflow_id == prefix_id
                        )
                    elif any(
                        r.workflow_id == prefix_id
                        for g in self.cluster.gpus
                        for r in g.kv.values()
                    ):
                        move = 8.0
                    own, _ext, c_phys = self.cluster.physical_cost(
                        spec,
                        lambda_move=self.config.lambda_move,
                        lambda_reuse=self.config.lambda_reuse,
                        move_cost=move,
                        reuse_bonus=reuse,
                    )
                    latency = own / self.config.latency_scale
                    cost = c_phys / self.config.latency_scale
                contended = gpu_id is not None and len(self.cluster.gpus[gpu_id].running) > 0
                r_hat = risk_term(workflow, ec, fid_e, active, contended)
                score = (
                    q_hat
                    - self.config.lambda_l * latency
                    - self.config.lambda_c * cost
                    - self.config.lambda_r * r_hat
                    - self.config.lambda_plan * plan_cost
                )
                decision = Decision(
                    edit=edit,
                    gpu_id=gpu_id,
                    score=score,
                    q_hat=q_hat,
                    latency_hat=latency,
                    cost_hat=cost,
                    risk_hat=r_hat,
                    rationale=edit.describe(),
                )
                if edit.kind == "noop":
                    if best_noop is None or decision.score > best_noop.score:
                        best_noop = decision
                if best is None or decision.score > best.score:
                    best = decision

        if (
            best is not None and best_noop is not None
            and best.edit.kind != "noop"
            and best.score < best_noop.score + self.config.edit_margin
        ):
            best = best_noop
        return best or Decision(
            edit=noop(), gpu_id=self.cluster.least_loaded_gpu(),
            score=0.0, q_hat=0.0, latency_hat=0.0, cost_hat=0.0, risk_hat=0.0,
        )
