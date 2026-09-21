"""Workflow DAG abstractions and library of example workflows."""

from agentqo.workflows.dag import (
    Fidelity,
    NodeSpec,
    NodeRole,
    Workflow,
    WorkflowBuilder,
)
from agentqo.workflows.library import (
    create_math_reasoning_workflow,
    create_multihop_qa_workflow,
    create_self_consistency_workflow,
    create_complex_workflow,
    create_refinement_workflow,
)

__all__ = [
    "Fidelity",
    "NodeSpec",
    "NodeRole",
    "Workflow",
    "WorkflowBuilder",
    "create_math_reasoning_workflow",
    "create_multihop_qa_workflow",
    "create_self_consistency_workflow",
    "create_complex_workflow",
    "create_refinement_workflow",
]
