"""Canonical workflow suite for H1–H3.

Each workflow has a unique name so train/test splits cannot silently
collide (the previous library reused ``math_reasoning`` for every size).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from agentqo.simulator.task_model import (
    MathReasoningTaskModel,
    MultiHopQATaskModel,
    SelfConsistencyTaskModel,
    TaskModel,
)
from agentqo.workflows.dag import Workflow
from agentqo.workflows.library import (
    create_complex_workflow,
    create_math_reasoning_workflow,
    create_multihop_qa_workflow,
    create_self_consistency_workflow,
)


@dataclass(frozen=True)
class SuiteMember:
    workflow: Workflow
    task_model: TaskModel
    display_name: str


def default_suite(quick: bool = False) -> List[SuiteMember]:
    """Workflows covering fan-out, verification, redundancy, and formatting."""
    if quick:
        specs: Sequence[Tuple[str, Workflow, TaskModel]] = (
            ("Math 3-step", create_math_reasoning_workflow(3), MathReasoningTaskModel()),
            ("QA 3-researcher", create_multihop_qa_workflow(3), MultiHopQATaskModel()),
            ("Self-consistency k=3", create_self_consistency_workflow(3), SelfConsistencyTaskModel()),
            ("Complex + formatter", create_complex_workflow(2, 2), MultiHopQATaskModel()),
        )
    else:
        specs = (
            ("Math 3-step", create_math_reasoning_workflow(3), MathReasoningTaskModel()),
            ("Math 5-step", create_math_reasoning_workflow(5), MathReasoningTaskModel()),
            ("QA 3-researcher", create_multihop_qa_workflow(3), MultiHopQATaskModel()),
            ("QA 5-researcher", create_multihop_qa_workflow(5), MultiHopQATaskModel()),
            ("Self-consistency k=3", create_self_consistency_workflow(3), SelfConsistencyTaskModel()),
            ("Self-consistency k=5", create_self_consistency_workflow(5), SelfConsistencyTaskModel()),
            ("Complex + formatter", create_complex_workflow(2, 2), MultiHopQATaskModel()),
        )
    members = [
        SuiteMember(workflow=wf, task_model=tm, display_name=disp)
        for disp, wf, tm in specs
    ]
    names = [m.workflow.name for m in members]
    if len(names) != len(set(names)):
        raise RuntimeError(f"suite workflow names are not unique: {names}")
    return members
