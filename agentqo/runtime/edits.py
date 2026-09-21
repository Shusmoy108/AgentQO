"""Constrained runtime edit space from AgentQO proposal §V.A.

The first version does not rewrite graphs arbitrarily. Edits are local:
width, loop stop/extend, verifier on/off, model fidelity, branch cancel, no-op.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from agentqo.workflows.dag import Fidelity, NodeRole, Workflow


@dataclass(frozen=True)
class Edit:
    """One local plan edit. ``noop`` keeps the current logical plan."""

    kind: str
    node_id: Optional[str] = None
    fidelity: Optional[Fidelity] = None
    k: Optional[int] = None
    enable: Optional[bool] = None

    def describe(self) -> str:
        if self.kind == "noop":
            return "noop"
        if self.kind == "set_fidelity":
            name = self.fidelity.name if self.fidelity else "?"
            return f"set_fidelity({self.node_id}->{name})"
        if self.kind == "set_verifier":
            return f"set_verifier({self.enable})"
        if self.kind == "set_width":
            return f"set_width({self.k})"
        if self.kind == "cancel":
            return f"cancel({self.node_id})"
        if self.kind == "skip_optional":
            return f"skip({self.node_id})"
        if self.kind == "admit_optional":
            return f"admit({self.node_id})"
        return self.kind


def noop() -> Edit:
    return Edit(kind="noop")


def candidate_edits(
    workflow: Workflow,
    skipped: Set[str],
    cancelled: Set[str],
    completed: Set[str],
    active: Set[str],
    fidelities: Dict[str, Fidelity],
) -> List[Edit]:
    """Enumerate the proposal's constrained edit set for the current state."""
    edits = [noop()]
    frozen = completed | active | skipped | cancelled

    for node_id, node in workflow.nodes.items():
        if node_id in frozen:
            continue
        current = fidelities.get(node_id, node.fidelities[0])
        for fid in node.fidelities:
            if fid.name != current.name:
                edits.append(Edit(kind="set_fidelity", node_id=node_id, fidelity=fid))
        if node.optional:
            edits.append(Edit(kind="skip_optional", node_id=node_id))

    for node_id in skipped:
        node = workflow.nodes.get(node_id)
        if node is not None and node.optional:
            edits.append(Edit(kind="admit_optional", node_id=node_id))

    verifiers = [
        nid for nid, n in workflow.nodes.items()
        if n.role == NodeRole.VERIFIER and nid not in completed and nid not in active
    ]
    for vid in verifiers:
        currently_skipped = vid in skipped
        edits.append(Edit(kind="set_verifier", node_id=vid, enable=currently_skipped))

    groups = workflow.get_speculative_groups()
    for node_ids in groups.values():
        optional = [
            nid for nid in node_ids
            if workflow.nodes[nid].optional and nid not in completed and nid not in active
        ]
        required = [nid for nid in node_ids if not workflow.nodes[nid].optional]
        live = [
            nid for nid in node_ids
            if nid not in skipped and nid not in cancelled
        ]
        if optional:
            k_min = len(required) or 1
            k_max = len(node_ids)
            for k in range(k_min, k_max + 1):
                if k != len(live):
                    edits.append(Edit(kind="set_width", k=k))

    for nid in list(active):
        node = workflow.nodes[nid]
        if node.speculative or node.optional:
            edits.append(Edit(kind="cancel", node_id=nid))

    # Deduplicate while keeping order.
    seen = set()
    unique: List[Edit] = []
    for e in edits:
        key = (e.kind, e.node_id, e.fidelity.name if e.fidelity else None, e.k, e.enable)
        if key in seen:
            continue
        seen.add(key)
        unique.append(e)
    return unique


def apply_edit(
    edit: Edit,
    skipped: Set[str],
    cancelled: Set[str],
    fidelities: Dict[str, Fidelity],
    workflow: Workflow,
) -> None:
    """Mutate runtime plan sets in place."""
    if edit.kind == "noop":
        return
    if edit.kind == "set_fidelity" and edit.node_id and edit.fidelity:
        fidelities[edit.node_id] = edit.fidelity
        return
    if edit.kind == "skip_optional" and edit.node_id:
        skipped.add(edit.node_id)
        return
    if edit.kind == "admit_optional" and edit.node_id:
        skipped.discard(edit.node_id)
        cancelled.discard(edit.node_id)
        return
    if edit.kind == "cancel" and edit.node_id:
        cancelled.add(edit.node_id)
        skipped.add(edit.node_id)
        return
    if edit.kind == "set_verifier" and edit.node_id:
        if edit.enable:
            skipped.discard(edit.node_id)
        else:
            skipped.add(edit.node_id)
        return
    if edit.kind == "set_width" and edit.k is not None:
        groups = workflow.get_speculative_groups()
        for node_ids in groups.values():
            ordered = sorted(node_ids)
            for i, nid in enumerate(ordered):
                if i < edit.k:
                    skipped.discard(nid)
                    cancelled.discard(nid)
                elif workflow.nodes[nid].optional:
                    skipped.add(nid)
        return
