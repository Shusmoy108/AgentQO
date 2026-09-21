"""
Tests for executor with overrides and partial recompute.

Tests:
1. Basic workflow execution
2. Correctness override works
3. Partial recompute only affects descendants
4. Invariant: unchanged nodes have identical results
"""

import pytest
import numpy as np

from agentqo.workflows.dag import Workflow, WorkflowBuilder, NodeRole
from agentqo.workflows.library import create_math_reasoning_workflow
from agentqo.simulator.task_model import MockBackend, MathReasoningTaskModel
from agentqo.executor import (
    WorkflowExecutor,
    ExecutionOverrides,
    FidelityPlan,
    verify_partial_recompute_invariant,
)


@pytest.fixture
def simple_workflow():
    """Create a simple test workflow."""
    return (
        WorkflowBuilder("test_workflow")
        .add_planner("a")
        .add_researcher("b", inputs=["a"])
        .add_researcher("c", inputs=["a"])
        .add_aggregator("d", inputs=["b", "c"])
        .build()
    )


@pytest.fixture
def task_model():
    """Create a task model for testing."""
    return MathReasoningTaskModel(
        base_difficulty=0.3,
        difficulty_variance=0.1,
    )


@pytest.fixture
def backend(task_model):
    """Create a mock backend."""
    return MockBackend(
        task_model=task_model,
        embedding_dim=64,  # Small for testing
        confidence_noise=0.1,
    )


@pytest.fixture
def executor(backend, task_model):
    """Create an executor."""
    return WorkflowExecutor(backend, task_model)


class TestBasicExecution:
    """Tests for basic workflow execution."""
    
    def test_execute_workflow(self, executor, simple_workflow, task_model):
        """Test basic workflow execution."""
        rng = np.random.default_rng(42)
        task = task_model.generate_task(simple_workflow, rng)
        
        record = executor.run_workflow(
            workflow=simple_workflow,
            task=task,
            seed=42,
        )
        
        # All nodes should be executed
        assert len(record.node_results) == 4
        assert "a" in record.node_results
        assert "b" in record.node_results
        assert "c" in record.node_results
        assert "d" in record.node_results
        
        # Quality should be computed
        assert 0 <= record.final_quality <= 1
        
        # Cost should be positive
        assert record.total_cost > 0
    
    def test_reproducibility(self, executor, simple_workflow, task_model):
        """Test that same seed gives same results."""
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)
        
        task1 = task_model.generate_task(simple_workflow, rng1)
        task2 = task_model.generate_task(simple_workflow, rng2)
        
        record1 = executor.run_workflow(simple_workflow, task1, seed=42)
        record2 = executor.run_workflow(simple_workflow, task2, seed=42)
        
        # Results should be identical
        assert record1.final_quality == record2.final_quality
        assert record1.total_cost == record2.total_cost
        
        for node_id in simple_workflow.nodes:
            assert record1.node_results[node_id].correctness == record2.node_results[node_id].correctness


class TestCorrectnessOverride:
    """Tests for correctness override (fault injection)."""
    
    def test_force_correct(self, executor, simple_workflow, task_model):
        """Test forcing a node to be correct."""
        rng = np.random.default_rng(42)
        task = task_model.generate_task(simple_workflow, rng)
        
        overrides = ExecutionOverrides(
            forced_correctness={"a": True}
        )
        
        record = executor.run_workflow(
            workflow=simple_workflow,
            task=task,
            overrides=overrides,
            seed=42,
        )
        
        # Node a should be correct
        assert record.node_results["a"].correctness is True
        assert record.node_results["a"].metadata.get("correctness_forced") is True
    
    def test_force_incorrect(self, executor, simple_workflow, task_model):
        """Test forcing a node to be incorrect."""
        rng = np.random.default_rng(42)
        task = task_model.generate_task(simple_workflow, rng)
        
        overrides = ExecutionOverrides(
            forced_correctness={"a": False}
        )
        
        record = executor.run_workflow(
            workflow=simple_workflow,
            task=task,
            overrides=overrides,
            seed=42,
        )
        
        # Node a should be incorrect
        assert record.node_results["a"].correctness is False


    def test_force_output_override(self, executor, simple_workflow, task_model):
        rng = np.random.default_rng(42)
        task = task_model.generate_task(simple_workflow, rng)
        overrides = ExecutionOverrides(force_outputs={"a": {"forced": True}})
        record = executor.run_workflow(
            simple_workflow, task, overrides=overrides, seed=42
        )
        assert record.node_results["a"].output == {"forced": True}
        assert record.node_results["a"].metadata.get("output_forced") is True


class TestPartialRecompute:
    """Tests for partial recompute (descendant-only)."""
    
    def test_partial_recompute_descendants_only(
        self, executor, simple_workflow, task_model
    ):
        """Test that partial recompute only affects descendants."""
        rng = np.random.default_rng(42)
        task = task_model.generate_task(simple_workflow, rng)
        
        # Run baseline
        baseline = executor.run_workflow(
            workflow=simple_workflow,
            task=task,
            seed=42,
        )
        
        # Force node b to be incorrect
        overrides = ExecutionOverrides(
            forced_correctness={"b": False}
        )
        
        # Partial recompute
        partial = executor.run_with_partial_recompute(
            workflow=simple_workflow,
            task=task,
            baseline_results=baseline.node_results,
            changed_nodes={"b"},
            overrides=overrides,
            seed=43,  # Different seed for recompute
        )
        
        # Verify invariant: a and c should be unchanged
        # (only b and d should be affected, where d is descendant of b)
        is_valid, violations = verify_partial_recompute_invariant(
            baseline, partial, {"b"}, simple_workflow
        )
        
        assert is_valid, f"Invariant violations: {violations}"
    
    def test_override_at_v_leaves_ancestors_unchanged(
        self, executor, simple_workflow, task_model
    ):
        """Test that forcing v leaves all non-descendants identical."""
        rng = np.random.default_rng(42)
        task = task_model.generate_task(simple_workflow, rng)
        
        # Run baseline
        baseline = executor.run_workflow(
            workflow=simple_workflow,
            task=task,
            seed=42,
        )
        
        # Force node c (changes only c and d, not a or b)
        overrides = ExecutionOverrides(
            forced_correctness={"c": True}
        )
        
        partial = executor.run_with_partial_recompute(
            workflow=simple_workflow,
            task=task,
            baseline_results=baseline.node_results,
            changed_nodes={"c"},
            overrides=overrides,
            seed=43,
        )
        
        # a and b should be byte-identical to baseline
        # (they are not descendants of c)
        is_valid, violations = verify_partial_recompute_invariant(
            baseline, partial, {"c"}, simple_workflow
        )
        
        assert is_valid, f"Invariant violations: {violations}"
        
        # Node a should be byte-identical (same object) after partial recompute
        assert baseline.node_results["a"] is partial.node_results["a"]
        assert baseline.node_results["b"].correctness == partial.node_results["b"].correctness


class TestMathReasoningWorkflow:
    """Tests using the math reasoning workflow template."""
    
    def test_math_workflow_execution(self, task_model, backend):
        """Test executing the math reasoning workflow."""
        workflow = create_math_reasoning_workflow(num_steps=3)
        executor = WorkflowExecutor(backend, task_model)
        
        rng = np.random.default_rng(42)
        task = task_model.generate_task(workflow, rng)
        
        record = executor.run_workflow(workflow, task, seed=42)
        
        # All nodes should be executed
        assert len(record.node_results) == 6  # planner + 3 steps + aggregator + verifier
        assert 0 <= record.final_quality <= 1
    
    def test_consequence_of_planner_error(self, task_model, backend):
        """Test that planner error has high downstream consequence."""
        workflow = create_math_reasoning_workflow(num_steps=3)
        executor = WorkflowExecutor(backend, task_model)
        
        rng = np.random.default_rng(42)
        task = task_model.generate_task(workflow, rng)
        
        # Force planner correct
        correct_override = ExecutionOverrides(forced_correctness={"planner": True})
        record_correct = executor.run_workflow(
            workflow, task, overrides=correct_override, seed=42
        )
        
        # Force planner incorrect
        incorrect_override = ExecutionOverrides(forced_correctness={"planner": False})
        record_incorrect = executor.run_workflow(
            workflow, task, overrides=incorrect_override, seed=42
        )
        
        # Planner error should cause quality drop (high consequence)
        quality_gap = record_correct.final_quality - record_incorrect.final_quality
        assert quality_gap >= 0, "Correct planner should give at least as good quality"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
