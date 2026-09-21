"""
Tests for workflow DAG abstractions.

Tests:
1. Graph helpers return correct values
2. Topological ordering is valid
3. Descendants and ancestors computed correctly
4. Cycle detection works
5. Speculative group handling
"""

import pytest
from agentqo.workflows.dag import (
    Fidelity,
    NodeSpec,
    NodeRole,
    Workflow,
    WorkflowBuilder,
    SMALL_FIDELITY,
    LARGE_FIDELITY,
)
from agentqo.workflows.library import (
    create_math_reasoning_workflow,
    create_multihop_qa_workflow,
    create_self_consistency_workflow,
)


class TestFidelity:
    """Tests for Fidelity dataclass."""
    
    def test_valid_fidelity(self):
        """Test creating valid fidelity."""
        f = Fidelity(name="test", cost=1.0, base_error_rate=0.1)
        assert f.name == "test"
        assert f.cost == 1.0
        assert f.base_error_rate == 0.1
    
    def test_invalid_cost(self):
        """Test that negative cost raises error."""
        with pytest.raises(ValueError, match="cost must be positive"):
            Fidelity(name="test", cost=-1.0, base_error_rate=0.1)
    
    def test_invalid_error_rate(self):
        """Test that error rate outside [0,1] raises error."""
        with pytest.raises(ValueError, match="base_error_rate must be in"):
            Fidelity(name="test", cost=1.0, base_error_rate=1.5)
        
        with pytest.raises(ValueError, match="base_error_rate must be in"):
            Fidelity(name="test", cost=1.0, base_error_rate=-0.1)

    def test_invalid_num_gpus(self):
        with pytest.raises(ValueError, match="num_gpus"):
            Fidelity(name="test", cost=1.0, base_error_rate=0.1, num_gpus=0)

    def test_model_id_defaults_to_name(self):
        f = Fidelity(name="draft", cost=1.0, base_error_rate=0.2)
        assert f.model_id == "draft"


class TestNodeSpec:
    """Tests for NodeSpec dataclass."""
    
    def test_valid_node(self):
        """Test creating valid node."""
        node = NodeSpec(
            node_id="test",
            role=NodeRole.PLANNER,
            inputs=[],
        )
        assert node.node_id == "test"
        assert node.role == NodeRole.PLANNER
        assert len(node.fidelities) == 2  # Default fidelities
    
    def test_speculative_without_group_id(self):
        """Test that speculative node without group_id raises error."""
        with pytest.raises(ValueError, match="speculative_group_id"):
            NodeSpec(
                node_id="test",
                role=NodeRole.SAMPLER,
                speculative=True,
                speculative_group_id=None,
            )


class TestWorkflow:
    """Tests for Workflow class."""
    
    def test_simple_workflow(self):
        """Test creating a simple linear workflow."""
        workflow = (
            WorkflowBuilder("test")
            .add_planner("a")
            .add_researcher("b", inputs=["a"])
            .add_aggregator("c", inputs=["b"])
            .build()
        )
        
        assert len(workflow.nodes) == 3
        assert "a" in workflow.nodes
        assert "b" in workflow.nodes
        assert "c" in workflow.nodes
    
    def test_topological_order(self):
        """Test that topological order is correct."""
        workflow = (
            WorkflowBuilder("test")
            .add_planner("a")
            .add_researcher("b", inputs=["a"])
            .add_researcher("c", inputs=["a"])
            .add_aggregator("d", inputs=["b", "c"])
            .build()
        )
        
        topo = workflow.topological_order
        
        # a must come before b, c
        # b, c must come before d
        assert topo.index("a") < topo.index("b")
        assert topo.index("a") < topo.index("c")
        assert topo.index("b") < topo.index("d")
        assert topo.index("c") < topo.index("d")
    
    def test_descendants(self):
        """Test descendant computation."""
        workflow = (
            WorkflowBuilder("test")
            .add_planner("a")
            .add_researcher("b", inputs=["a"])
            .add_researcher("c", inputs=["a"])
            .add_aggregator("d", inputs=["b", "c"])
            .build()
        )
        
        # a's descendants are b, c, d
        assert workflow.get_descendants("a") == frozenset({"b", "c", "d"})
        
        # b's descendants are d
        assert workflow.get_descendants("b") == frozenset({"d"})
        
        # d has no descendants
        assert workflow.get_descendants("d") == frozenset()
    
    def test_ancestors(self):
        """Test ancestor computation."""
        workflow = (
            WorkflowBuilder("test")
            .add_planner("a")
            .add_researcher("b", inputs=["a"])
            .add_researcher("c", inputs=["a"])
            .add_aggregator("d", inputs=["b", "c"])
            .build()
        )
        
        # a has no ancestors
        assert workflow.get_ancestors("a") == frozenset()
        
        # b's ancestor is a
        assert workflow.get_ancestors("b") == frozenset({"a"})
        
        # d's ancestors are a, b, c
        assert workflow.get_ancestors("d") == frozenset({"a", "b", "c"})
    
    def test_depth(self):
        """Test depth computation."""
        workflow = (
            WorkflowBuilder("test")
            .add_planner("a")
            .add_researcher("b", inputs=["a"])
            .add_researcher("c", inputs=["b"])
            .add_aggregator("d", inputs=["c"])
            .build()
        )
        
        assert workflow.get_depth("a") == 0
        assert workflow.get_depth("b") == 1
        assert workflow.get_depth("c") == 2
        assert workflow.get_depth("d") == 3
    
    def test_fan_out(self):
        """Test fan-out computation."""
        workflow = (
            WorkflowBuilder("test")
            .add_planner("a")
            .add_researcher("b", inputs=["a"])
            .add_researcher("c", inputs=["a"])
            .add_researcher("d", inputs=["a"])
            .add_aggregator("e", inputs=["b", "c", "d"])
            .build()
        )
        
        assert workflow.get_fan_out("a") == 3  # a -> b, c, d
        assert workflow.get_fan_out("b") == 1  # b -> e
        assert workflow.get_fan_out("e") == 0  # e is leaf
    
    def test_downstream_reach(self):
        """Test downstream reach computation."""
        workflow = (
            WorkflowBuilder("test")
            .add_planner("a")
            .add_researcher("b", inputs=["a"])
            .add_researcher("c", inputs=["a"])
            .add_aggregator("d", inputs=["b", "c"])
            .build()
        )
        
        assert workflow.get_downstream_reach("a") == 3  # b, c, d
        assert workflow.get_downstream_reach("b") == 1  # d
        assert workflow.get_downstream_reach("d") == 0  # none
    
    def test_has_downstream_verifier(self):
        """Test downstream verifier detection."""
        workflow = (
            WorkflowBuilder("test")
            .add_planner("a")
            .add_researcher("b", inputs=["a"])
            .add_aggregator("c", inputs=["b"])
            .add_verifier("v", inputs=["c"])
            .build()
        )
        
        assert workflow.has_downstream_verifier("a") is True
        assert workflow.has_downstream_verifier("b") is True
        assert workflow.has_downstream_verifier("c") is True
        assert workflow.has_downstream_verifier("v") is False
    
    def test_speculative_groups(self):
        """Test speculative group identification."""
        workflow = create_self_consistency_workflow(k=3)
        
        groups = workflow.get_speculative_groups()
        
        assert len(groups) == 1
        group_id = list(groups.keys())[0]
        assert len(groups[group_id]) == 3
    
    def test_cycle_detection(self):
        """Test that cycles are detected."""
        builder = WorkflowBuilder("test")
        builder._nodes["a"] = NodeSpec(
            node_id="a", role=NodeRole.PLANNER, inputs=["c"]
        )
        builder._nodes["b"] = NodeSpec(
            node_id="b", role=NodeRole.RESEARCHER, inputs=["a"]
        )
        builder._nodes["c"] = NodeSpec(
            node_id="c", role=NodeRole.AGGREGATOR, inputs=["b"]
        )
        
        with pytest.raises(ValueError, match="cycle"):
            builder.build()
    
    def test_missing_input_reference(self):
        """Test that missing input references are detected."""
        builder = WorkflowBuilder("test")
        builder._nodes["a"] = NodeSpec(
            node_id="a", role=NodeRole.PLANNER, inputs=["nonexistent"]
        )
        
        with pytest.raises(ValueError, match="does not exist"):
            builder.build()


class TestWorkflowLibrary:
    """Tests for workflow library functions."""
    
    def test_math_reasoning_workflow(self):
        """Test math reasoning workflow creation."""
        workflow = create_math_reasoning_workflow(num_steps=3, include_verifier=True)
        
        # Should have: planner, step_1, step_2, step_3, aggregator, verifier
        assert len(workflow.nodes) == 6
        assert "planner" in workflow.nodes
        assert "step_1" in workflow.nodes
        assert "aggregator" in workflow.nodes
        assert "verifier" in workflow.nodes
        
        # Verify it's a valid DAG
        topo = workflow.topological_order
        assert len(topo) == 6
    
    def test_multihop_qa_workflow(self):
        """Test multi-hop QA workflow creation."""
        workflow = create_multihop_qa_workflow(num_researchers=3, include_verifier=True)
        
        # Should have: planner, 3 researchers, aggregator, verifier
        assert len(workflow.nodes) == 6
        
        # Researchers should all depend on planner
        for i in range(1, 4):
            researcher = workflow.nodes[f"researcher_{i}"]
            assert "planner" in researcher.inputs
        
        # Aggregator should depend on all researchers
        agg = workflow.nodes["aggregator"]
        assert len(agg.inputs) == 3
    
    def test_self_consistency_workflow(self):
        """Test self-consistency workflow creation."""
        workflow = create_self_consistency_workflow(k=5)
        
        # Should have: prompt_encoder, 5 samplers, aggregator
        assert len(workflow.nodes) == 7
        
        # All samplers should be speculative
        groups = workflow.get_speculative_groups()
        assert len(groups) == 1
        group_nodes = list(groups.values())[0]
        assert len(group_nodes) == 5


class TestSubgraph:
    """Tests for subgraph extraction."""
    
    def test_subgraph_extraction(self):
        """Test extracting a subgraph."""
        workflow = (
            WorkflowBuilder("test")
            .add_planner("a")
            .add_researcher("b", inputs=["a"])
            .add_researcher("c", inputs=["a"])
            .add_aggregator("d", inputs=["b", "c"])
            .build()
        )
        
        subgraph = workflow.subgraph({"a", "b"})
        
        assert len(subgraph.nodes) == 2
        assert "a" in subgraph.nodes
        assert "b" in subgraph.nodes
        assert "c" not in subgraph.nodes
        
        # b's input should still be a
        assert subgraph.nodes["b"].inputs == ["a"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
