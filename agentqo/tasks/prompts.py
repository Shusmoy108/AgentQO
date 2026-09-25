"""Role prompts for real GSM8K runs (plan WP2, Appendix D).

``build_prompt`` returns the user prompt for an LLM node. ``code_output``
returns finished text for nodes computed in code (the self-consistency
majority vote), or None for LLM nodes. Both read upstream text from
``task_context["results"]`` (every result so far in this run), so a
substituted ancestor output reaches every descendant.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from agentqo.backends.vllm_http import _output_as_text
from agentqo.tasks.answers import extract_gsm8k_number
from agentqo.workflows.dag import NodeRole

if TYPE_CHECKING:
    from agentqo.backends.base import NodeResult
    from agentqo.workflows.dag import NodeSpec, Workflow

PLANNER = """You are planning how to solve a math word problem. Do not solve it.
Problem: {problem}
Write a numbered plan of at most {n_steps} computation steps.
Start your answer with "PLAN:"."""

ENCODER = """Restate this math word problem in your own words and list every quantity it gives. Do not solve it.
Problem: {problem}
Start your answer with "GIVEN:"."""

STEP = """Problem: {problem}
Plan:
{plan}
Results so far:
{prior}
Carry out step {i} only. Show the calculation briefly.
End with "RESULT: <number>"."""

BRANCH = """Problem: {problem}
Plan:
{plan}
Your work so far on this branch:
{prior}
You handle part {branch} of the plan. Do the next calculation for your part only.
End with "RESULT: <number>"."""

AGGREGATOR = """Problem: {problem}
Step results:
{steps}
State the final answer. End with "#### <number>"."""

VERIFIER = """Problem: {problem}
Proposed solution:
{proposed}
Check the solution. If it is wrong, correct it.
Write "VERDICT: correct" or "VERDICT: incorrect", then end with "#### <number>"."""

SAMPLER = """Solve this math word problem step by step.
Problem: {problem}
End with "#### <number>"."""

SAMPLER_WITH_CONTEXT = """Solve this math word problem step by step.
Problem: {problem}
Notes:
{notes}
End with "#### <number>"."""

FORMATTER = """Problem: {problem}
Solution:
{proposed}
Restate only the final answer. End with "#### <number>"."""


def _text(results: Dict[str, "NodeResult"], nid: str) -> str:
    return _output_as_text(results[nid].output) if nid in results else "(not available)"


def _problem(task_context: Dict[str, Any]) -> str:
    task = task_context.get("task")
    meta = getattr(task, "metadata", None) or {}
    return str(task_context.get("problem") or meta.get("problem") or "")


def _planner_id(workflow: "Workflow") -> Optional[str]:
    return next((n for n, s in workflow.nodes.items() if s.role == NodeRole.PLANNER), None)


def _chain(workflow: "Workflow", nid: str) -> List[str]:
    """Researcher ancestors of ``nid`` (its own branch), in topological order."""
    anc = workflow.get_ancestors(nid)
    return [n for n in workflow.topological_order
            if n in anc and workflow.nodes[n].role == NodeRole.RESEARCHER]


def _results_block(results, ids: List[str]) -> str:
    return "\n".join(f"{n}: {_text(results, n)}" for n in ids) or "(none yet)"


def build_prompt(node: "NodeSpec", inputs: Dict[str, "NodeResult"], task_context: Dict[str, Any]) -> str:
    workflow: "Workflow" = task_context["workflow"]
    results = {**task_context.get("results", {}), **inputs}
    problem = _problem(task_context)
    role = node.role
    plan_id = _planner_id(workflow)
    plan = _text(results, plan_id) if plan_id else "(no plan)"

    if role == NodeRole.PLANNER:
        if workflow.get_speculative_groups():
            return ENCODER.format(problem=problem)
        n_steps = sum(1 for s in workflow.nodes.values() if s.role == NodeRole.RESEARCHER)
        return PLANNER.format(problem=problem, n_steps=max(2, min(n_steps, 6)))
    if role == NodeRole.RESEARCHER:
        prior = _results_block(results, _chain(workflow, node.node_id))
        if node.node_id.startswith("step_") and node.node_id.count("_") == 1:
            return STEP.format(problem=problem, plan=plan, prior=prior, i=node.node_id.split("_")[1])
        branch = node.node_id.split("_")[1]
        return BRANCH.format(problem=problem, plan=plan, prior=prior, branch=branch)
    if role == NodeRole.AGGREGATOR:
        return AGGREGATOR.format(problem=problem, steps=_results_block(results, list(node.inputs)))
    if role == NodeRole.VERIFIER:
        return VERIFIER.format(problem=problem, proposed=_results_block(results, list(node.inputs)))
    if role == NodeRole.SAMPLER:
        notes = _results_block(results, list(node.inputs))
        return SAMPLER_WITH_CONTEXT.format(problem=problem, notes=notes) if node.inputs else SAMPLER.format(problem=problem)
    if role == NodeRole.FORMATTER:
        return FORMATTER.format(problem=problem, proposed=_results_block(results, list(node.inputs)))
    raise ValueError(f"no template for role {role}")


def code_output(node: "NodeSpec", inputs: Dict[str, "NodeResult"], task_context: Dict[str, Any]) -> Optional[str]:
    """Self-consistency aggregator = majority vote in code, not an LLM call."""
    workflow: "Workflow" = task_context["workflow"]
    if node.role != NodeRole.AGGREGATOR or not workflow.get_speculative_groups():
        return None
    votes = [extract_gsm8k_number(_output_as_text(r.output)) for r in inputs.values()]
    counts = Counter(v for v in votes if v is not None)
    if not counts:
        return "VOTE: no extractable answers"
    winner, n = counts.most_common(1)[0]  # ties go to the first answer seen
    return f"VOTE: {dict(counts)} ({n}/{len(votes)})\n#### {winner}"
