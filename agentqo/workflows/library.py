"""
Library of example workflows for AgentQO experiments.

Workflow patterns used by the runtime optimizer and the H1–H4 suite:
1. Math reasoning (GSM8K-style): planner -> researchers -> aggregator -> verifier
2. Multi-hop QA (HotpotQA-style): planner -> researchers -> aggregator -> verifier
3. Self-consistency: prompt -> k required + optional extra samplers -> aggregator
4. Refinement: draft -> critic -> optional refine rounds -> aggregator

These cover the patterns AgentQO cares about:
- Fan-out from planners to researchers
- Verification as optional downstream quality check
- Redundancy through speculative sampling
- Loop stop/extend as a constrained runtime edit
"""

from typing import List, Optional

from agentqo.workflows.dag import (
    Fidelity,
    NodeRole,
    Workflow,
    WorkflowBuilder,
    DEFAULT_FIDELITIES,
    SMALL_FIDELITY,
    LARGE_FIDELITY,
)


def create_math_reasoning_workflow(
    num_steps: int = 3,
    include_verifier: bool = True,
    fidelities: Optional[List[Fidelity]] = None,
) -> Workflow:
    """Create a math reasoning workflow (GSM8K-style).
    
    Structure:
        planner -> step_1 -> step_2 -> ... -> step_n -> aggregator -> [verifier]
    
    This models step-by-step mathematical problem solving where:
    - Planner decomposes the problem into steps
    - Each step node performs one computation
    - Aggregator combines step results into final answer
    - Optional verifier checks the answer
    
    Args:
        num_steps: Number of computation steps (default: 3)
        include_verifier: Whether to include optional verifier (default: True)
        fidelities: Fidelity options for nodes (default: small/large)
    
    Returns:
        Workflow representing the math reasoning DAG
    """
    fidelities = fidelities or list(DEFAULT_FIDELITIES)
    suffix = f"s{num_steps}" + ("_ver" if include_verifier else "")
    builder = WorkflowBuilder(
        name=f"math_reasoning_{suffix}",
        description=f"GSM8K-style {num_steps}-step math reasoning workflow",
    )
    
    # Planner node - decomposes problem
    builder.add_planner(
        "planner",
        description="Decompose math problem into computational steps",
        fidelities=fidelities,
    )
    
    # Step nodes - each performs one computation
    prev_node = "planner"
    for i in range(1, num_steps + 1):
        step_id = f"step_{i}"
        builder.add_researcher(
            step_id,
            inputs=[prev_node],
            description=f"Execute computation step {i}",
            fidelities=fidelities,
        )
        prev_node = step_id
    
    # Aggregator - combines step results
    builder.add_aggregator(
        "aggregator",
        inputs=[prev_node],
        description="Combine step results into final answer",
        fidelities=fidelities,
    )
    
    # Optional verifier
    if include_verifier:
        builder.add_verifier(
            "verifier",
            inputs=["aggregator"],
            optional=True,
            description="Verify final answer correctness",
            fidelities=fidelities,
        )
    
    return builder.build()


def create_multihop_qa_workflow(
    num_researchers: int = 3,
    include_verifier: bool = True,
    fidelities: Optional[List[Fidelity]] = None,
) -> Workflow:
    """Create a multi-hop QA workflow (HotpotQA-style).
    
    Structure:
        planner -> [researcher_1, researcher_2, ..., researcher_n] -> aggregator -> [verifier]
    
    This models multi-hop question answering where:
    - Planner identifies what information is needed
    - Multiple researchers gather different pieces of evidence (fan-out)
    - Aggregator synthesizes evidence into final answer
    - Optional verifier validates the answer
    
    Args:
        num_researchers: Number of parallel researcher nodes (default: 3)
        include_verifier: Whether to include optional verifier (default: True)
        fidelities: Fidelity options for nodes (default: small/large)
    
    Returns:
        Workflow representing the multi-hop QA DAG
    """
    fidelities = fidelities or list(DEFAULT_FIDELITIES)
    suffix = f"r{num_researchers}" + ("_ver" if include_verifier else "")
    builder = WorkflowBuilder(
        name=f"multihop_qa_{suffix}",
        description=f"HotpotQA-style {num_researchers}-researcher multi-hop QA workflow",
    )
    
    # Planner node - identifies information needs
    builder.add_planner(
        "planner",
        description="Identify required information for multi-hop reasoning",
        fidelities=fidelities,
    )
    
    # Researcher nodes - gather evidence in parallel (fan-out)
    researcher_ids = []
    for i in range(1, num_researchers + 1):
        researcher_id = f"researcher_{i}"
        builder.add_researcher(
            researcher_id,
            inputs=["planner"],
            description=f"Gather evidence piece {i}",
            fidelities=fidelities,
        )
        researcher_ids.append(researcher_id)
    
    # Aggregator - synthesizes all evidence
    builder.add_aggregator(
        "aggregator",
        inputs=researcher_ids,
        description="Synthesize evidence into final answer",
        fidelities=fidelities,
    )
    
    # Optional verifier
    if include_verifier:
        builder.add_verifier(
            "verifier",
            inputs=["aggregator"],
            optional=True,
            description="Validate synthesized answer",
            fidelities=fidelities,
        )
    
    return builder.build()


def create_self_consistency_workflow(
    k: int = 3,
    k_max: Optional[int] = None,
    fidelities: Optional[List[Fidelity]] = None,
) -> Workflow:
    """Self-consistency with optional extra branches for runtime width edits.

    Samplers 1..k are required. Samplers k+1..k_max are optional speculative
    branches AgentQO can admit or cancel (proposal §V.A).
    """
    k_max = k_max or k
    if k_max < k:
        raise ValueError("k_max must be >= k")
    fidelities = fidelities or list(DEFAULT_FIDELITIES)
    builder = WorkflowBuilder(
        name=f"self_consistency_k{k}_max{k_max}" if k_max != k else f"self_consistency_k{k}",
        description=f"Self-consistency with k={k} required, k_max={k_max}",
    )
    builder.add_planner(
        "prompt_encoder",
        description="Encode prompt for multiple sampling paths",
        fidelities=fidelities,
    )
    speculative_group_id = "consistency_group"
    sampler_ids = []
    for i in range(1, k_max + 1):
        sampler_id = f"sampler_{i}"
        builder.add_sampler(
            sampler_id,
            inputs=["prompt_encoder"],
            speculative_group_id=speculative_group_id,
            optional=i > k,
            description=f"Generate candidate answer {i}",
            fidelities=fidelities,
        )
        sampler_ids.append(sampler_id)
    builder.add_aggregator(
        "aggregator",
        inputs=sampler_ids,
        description="Select best answer via majority voting",
        fidelities=fidelities,
    )
    return builder.build()


def create_complex_workflow(
    num_researchers: int = 2,
    num_steps_per_researcher: int = 2,
    include_verifier: bool = True,
    fidelities: Optional[List[Fidelity]] = None,
) -> Workflow:
    """Create a complex workflow combining multiple patterns.
    
    Structure:
        planner -> [researcher_1 -> step_1_1 -> step_1_2, 
                    researcher_2 -> step_2_1 -> step_2_2,
                    ...] -> aggregator -> [verifier] -> formatter
    
    This combines:
    - Fan-out from planner to researchers
    - Sequential processing within each branch
    - Aggregation of all results
    - Optional verification
    - Final formatting
    
    Useful for testing more complex DAG structures.
    """
    fidelities = fidelities or list(DEFAULT_FIDELITIES)
    suffix = f"r{num_researchers}_s{num_steps_per_researcher}"
    suffix += "_ver" if include_verifier else ""
    builder = WorkflowBuilder(
        name=f"complex_{suffix}",
        description="Complex workflow with fan-out, sequential processing, and a formatter",
    )
    
    # Planner
    builder.add_planner(
        "planner",
        description="Decompose complex task",
        fidelities=fidelities,
    )
    
    # Research branches with sequential steps
    final_step_ids = []
    for r in range(1, num_researchers + 1):
        researcher_id = f"researcher_{r}"
        builder.add_researcher(
            researcher_id,
            inputs=["planner"],
            description=f"Research branch {r}",
            fidelities=fidelities,
        )
        
        prev_node = researcher_id
        for s in range(1, num_steps_per_researcher + 1):
            step_id = f"step_{r}_{s}"
            builder.add_researcher(
                step_id,
                inputs=[prev_node],
                description=f"Process step {s} for branch {r}",
                fidelities=fidelities,
            )
            prev_node = step_id
        
        final_step_ids.append(prev_node)
    
    # Aggregator
    builder.add_aggregator(
        "aggregator",
        inputs=final_step_ids,
        description="Aggregate all branch results",
        fidelities=fidelities,
    )
    
    # Optional verifier
    prev_node = "aggregator"
    if include_verifier:
        builder.add_verifier(
            "verifier",
            inputs=["aggregator"],
            optional=True,
            description="Verify aggregated result",
            fidelities=fidelities,
        )
        prev_node = "verifier"
    
    # Formatter
    builder.add_formatter(
        "formatter",
        inputs=[prev_node],
        description="Format final output",
        fidelities=fidelities,
    )
    
    return builder.build()


def create_refinement_workflow(
    max_rounds: int = 2,
    fidelities: Optional[List[Fidelity]] = None,
) -> Workflow:
    """Iterative refinement loop with stop/extend edit points.

    Structure:
        draft -> critic -> aggregator
                    |         ^
                    +-> refine_1 (optional) --+
                    +-> refine_2 (optional) --+

    AgentQO can skip later refine rounds (stop) or admit them (extend).
    """
    fidelities = fidelities or list(DEFAULT_FIDELITIES)
    builder = WorkflowBuilder(
        name=f"refinement_r{max_rounds}",
        description=f"Refinement loop with up to {max_rounds} extra rounds",
    )
    builder.add_planner("draft", description="Initial answer", fidelities=fidelities)
    builder.add_researcher(
        "critic",
        inputs=["draft"],
        description="Critique the draft",
        fidelities=fidelities,
    )
    refine_ids = []
    for i in range(1, max_rounds + 1):
        rid = f"refine_{i}"
        builder.add_researcher(
            rid,
            inputs=["critic"],
            optional=True,
            description=f"Refinement round {i}",
            fidelities=fidelities,
        )
        refine_ids.append(rid)
    builder.add_aggregator(
        "aggregator",
        inputs=["critic"] + refine_ids,
        description="Emit refined answer",
        fidelities=fidelities,
    )
    return builder.build()
