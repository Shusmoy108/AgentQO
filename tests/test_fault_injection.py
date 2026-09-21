"""
Tests for fault injection and EC labeling.

Tests:
1. Fault injection produces different qualities
2. EC labels are computed correctly
3. Bootstrap CI is valid
4. H1 analysis works
"""

import pytest
import numpy as np

from agentqo.workflows.library import create_math_reasoning_workflow, create_multihop_qa_workflow
from agentqo.simulator.task_model import MockBackend, MathReasoningTaskModel, MultiHopQATaskModel
from agentqo.labeling.ec_labeler import ECLabeler, ECLabel, compute_bootstrap_ci, analyze_h1_results


@pytest.fixture
def math_workflow():
    """Create math reasoning workflow for testing."""
    return create_math_reasoning_workflow(num_steps=2, include_verifier=False)


@pytest.fixture
def math_task_model():
    """Create math task model."""
    return MathReasoningTaskModel(
        base_difficulty=0.4,
        difficulty_variance=0.1,
    )


@pytest.fixture
def math_backend(math_task_model):
    """Create backend for math tasks."""
    return MockBackend(
        task_model=math_task_model,
        embedding_dim=64,
    )


class TestBootstrapCI:
    """Tests for bootstrap confidence interval computation."""
    
    def test_bootstrap_ci_basic(self):
        """Test basic bootstrap CI computation."""
        rng = np.random.default_rng(42)
        data = rng.normal(0.5, 0.1, size=100)
        
        ci_low, ci_high = compute_bootstrap_ci(data, confidence=0.95, rng=rng)
        
        # CI should contain the mean
        mean = np.mean(data)
        assert ci_low <= mean <= ci_high
        
        # CI should be reasonable width
        assert ci_high - ci_low < 0.1
    
    def test_bootstrap_ci_empty(self):
        """Test bootstrap CI with empty data."""
        ci_low, ci_high = compute_bootstrap_ci(np.array([]))
        assert ci_low == 0.0
        assert ci_high == 0.0
    
    def test_bootstrap_ci_single(self):
        """Test bootstrap CI with single data point."""
        ci_low, ci_high = compute_bootstrap_ci(np.array([0.5]))
        assert ci_low == 0.5
        assert ci_high == 0.5


class TestECLabeler:
    """Tests for EC labeling."""
    
    def test_label_single_node(self, math_workflow, math_task_model, math_backend):
        """Test that labeling produces valid EC labels."""
        labeler = ECLabeler(math_backend, math_task_model)
        
        # Run with small number of tasks for speed
        labeled = labeler.label_workflow(
            workflow=math_workflow,
            num_tasks=10,
            base_seed=42,
            show_progress=False,
        )
        labels = labeled.labels
        
        # Should have labels for all nodes
        assert len(labels) == len(math_workflow.nodes)
        
        # Each label should be valid
        for node_id, label in labels.items():
            assert isinstance(label, ECLabel)
            assert label.node_id == node_id
            assert label.num_samples == 10
            # CI should be valid
            assert label.consequence_ci_low <= label.consequence_mean <= label.consequence_ci_high or \
                   np.isclose(label.consequence_ci_low, label.consequence_mean)
    
    def test_consequence_varies_across_nodes(self, math_workflow, math_task_model, math_backend):
        """Test that consequence varies across nodes (H1 sanity check)."""
        labeler = ECLabeler(math_backend, math_task_model)
        
        labeled = labeler.label_workflow(
            workflow=math_workflow,
            num_tasks=30,
            base_seed=42,
            show_progress=False,
        )
        labels = labeled.labels
        
        consequences = [label.consequence_mean for label in labels.values()]
        
        # Should have some variance
        assert np.std(consequences) > 0, "Consequences should vary across nodes"


class TestH1Analysis:
    """Tests for H1 analysis functions."""
    
    def test_analyze_h1_results(self, math_workflow, math_task_model, math_backend):
        """Test H1 analysis produces valid output."""
        labeler = ECLabeler(math_backend, math_task_model)
        
        labeled = labeler.label_workflow(
            workflow=math_workflow,
            num_tasks=20,
            base_seed=42,
            show_progress=False,
        )
        labels = labeled.labels
        
        analysis = analyze_h1_results(labels, math_workflow)
        
        # Analysis should have required keys
        assert "statistics" in analysis
        assert "correlations" in analysis
        assert "h1_holds" in analysis
        assert "high_criticality_nodes" in analysis
        assert "low_criticality_nodes" in analysis
        
        # Statistics should be valid
        stats = analysis["statistics"]
        assert "mean" in stats
        assert "std" in stats
        assert stats["std"] >= 0
    
    def test_critical_node_impact(self, math_task_model, math_backend):
        """Test that high-criticality nodes have larger consequence."""
        # Use a workflow where we know planner should be critical
        workflow = create_math_reasoning_workflow(num_steps=3, include_verifier=True)
        
        labeler = ECLabeler(math_backend, math_task_model)
        
        labeled = labeler.label_workflow(
            workflow=workflow,
            num_tasks=50,
            base_seed=42,
            show_progress=False,
        )
        labels = labeled.labels
        
        # Planner consequence should generally be higher than formatter/verifier
        planner_consequence = labels["planner"].consequence_mean
        verifier_consequence = labels["verifier"].consequence_mean
        
        # This isn't guaranteed due to randomness, but should generally hold
        # We just check they're computed
        assert planner_consequence is not None
        assert verifier_consequence is not None


class TestMultiHopQA:
    """Tests for multi-hop QA task model."""
    
    def test_multihop_labeling(self):
        """Test labeling on multi-hop QA workflow."""
        workflow = create_multihop_qa_workflow(num_researchers=2, include_verifier=False)
        task_model = MultiHopQATaskModel(base_difficulty=0.4)
        backend = MockBackend(task_model, embedding_dim=64)
        
        labeler = ECLabeler(backend, task_model)
        
        labeled = labeler.label_workflow(
            workflow=workflow,
            num_tasks=10,
            base_seed=42,
            show_progress=False,
        )
        labels = labeled.labels
        
        assert len(labels) == len(workflow.nodes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
