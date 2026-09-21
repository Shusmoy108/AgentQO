"""
Feature extraction for EC prediction.

Two feature views:
1. Structural features: role, depth, fan-out, downstream reach, etc.
2. Embedding features: recycled embedding from node execution
3. Confidence: single scalar from node execution

The AgentQO predictor uses structure + embedding.
Baselines use structure only or confidence only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from agentqo.backends.base import NodeResult
from agentqo.workflows.dag import NodeRole, NodeSpec, Workflow


# Role encoding (one-hot)
ROLE_ENCODING = {
    NodeRole.PLANNER: 0,
    NodeRole.RESEARCHER: 1,
    NodeRole.AGGREGATOR: 2,
    NodeRole.VERIFIER: 3,
    NodeRole.SAMPLER: 4,
    NodeRole.FORMATTER: 5,
}
NUM_ROLES = len(ROLE_ENCODING)


@dataclass
class NodeFeatures:
    """Features for a single node.
    
    Attributes:
        node_id: Node identifier
        
        # Structural features (fixed for workflow)
        role_onehot: One-hot encoding of node role
        depth: Depth in DAG (normalized)
        fan_out: Number of direct dependents (normalized)
        downstream_reach: Total descendants (normalized)
        has_downstream_verifier: 1 if any descendant is verifier
        is_optional: 1 if node is optional
        is_speculative: 1 if node is speculative
        num_inputs: Number of input dependencies (normalized)
        
        # Embedding features (from execution)
        embedding: Recycled embedding vector
        
        # Confidence feature
        confidence: Model confidence in output
    """
    node_id: str
    
    # Structural (always available)
    role_onehot: np.ndarray
    depth: float
    fan_out: float
    downstream_reach: float
    has_downstream_verifier: float
    is_optional: float
    is_speculative: float
    num_inputs: float
    
    # Embedding (requires execution)
    embedding: Optional[np.ndarray] = None
    
    # Confidence (requires execution)
    confidence: Optional[float] = None
    
    @property
    def structural_features(self) -> np.ndarray:
        """Get structural features as a flat array."""
        return np.concatenate([
            self.role_onehot,
            np.array([
                self.depth,
                self.fan_out,
                self.downstream_reach,
                self.has_downstream_verifier,
                self.is_optional,
                self.is_speculative,
                self.num_inputs,
            ])
        ])
    
    @property
    def structural_dim(self) -> int:
        """Dimension of structural features."""
        return NUM_ROLES + 7
    
    def as_vector(self, view: str = "agentqo") -> np.ndarray:
        """Flat feature vector for a named view.

        Views (from the plan):
            structure   – DAG features only
            confidence  – scalar confidence
            embedding   – recycled embedding only
            agentqo     – structure + embedding (the proposed predictor)
            all         – structure + embedding + confidence (sanity / ablation)
        """
        if view == "structure":
            return self.structural_features
        if view == "confidence":
            conf = 0.0 if self.confidence is None else self.confidence
            return np.array([conf], dtype=np.float32)
        if view == "embedding":
            if self.embedding is None:
                raise ValueError("embedding view requested but embedding is None")
            return self.embedding.astype(np.float32, copy=False)
        if view == "agentqo":
            if self.embedding is None:
                raise ValueError("agentqo view requires an embedding")
            return np.concatenate([
                self.structural_features,
                self.embedding.astype(np.float32),
            ])
        if view == "all":
            parts = [self.structural_features]
            if self.embedding is not None:
                parts.append(self.embedding.astype(np.float32))
            conf = 0.0 if self.confidence is None else self.confidence
            parts.append(np.array([conf], dtype=np.float32))
            return np.concatenate(parts)
        raise ValueError(f"unknown feature view: {view}")

    def get_full_features(self, include_embedding: bool = True) -> np.ndarray:
        """Back-compat wrapper. Prefer :meth:`as_vector`."""
        if include_embedding:
            return self.as_vector("all")
        return self.as_vector("structure")


class FeatureExtractor:
    """Extracts features for EC prediction.
    
    Can extract:
    - Structure-only features (from workflow DAG)
    - Structure + embedding features (from workflow + execution results)
    - Structure + confidence features (from workflow + execution results)
    - Full features (all of the above)
    """
    
    def __init__(self, embedding_dim: int = 256) -> None:
        """Initialize feature extractor.
        
        Args:
            embedding_dim: Expected dimension of embeddings
        """
        self.embedding_dim = embedding_dim
    
    def extract_structural_features(
        self,
        workflow: Workflow,
        node_id: str,
    ) -> NodeFeatures:
        """Extract only structural features for a node.
        
        These features are fixed for a given workflow structure
        and don't require execution.
        """
        node = workflow.nodes[node_id]
        max_depth = max(workflow.get_depth(nid) for nid in workflow.nodes)
        num_nodes = len(workflow.nodes)
        
        # Role one-hot
        role_onehot = np.zeros(NUM_ROLES, dtype=np.float32)
        role_idx = ROLE_ENCODING.get(node.role, 0)
        role_onehot[role_idx] = 1.0
        
        # Normalized structural features
        depth = workflow.get_depth(node_id) / max(max_depth, 1)
        fan_out = workflow.get_fan_out(node_id) / max(num_nodes - 1, 1)
        downstream_reach = workflow.get_downstream_reach(node_id) / max(num_nodes - 1, 1)
        
        return NodeFeatures(
            node_id=node_id,
            role_onehot=role_onehot,
            depth=depth,
            fan_out=fan_out,
            downstream_reach=downstream_reach,
            has_downstream_verifier=1.0 if workflow.has_downstream_verifier(node_id) else 0.0,
            is_optional=1.0 if node.optional else 0.0,
            is_speculative=1.0 if node.speculative else 0.0,
            num_inputs=len(node.inputs) / max(num_nodes - 1, 1),
        )
    
    def extract_features_with_results(
        self,
        workflow: Workflow,
        node_id: str,
        node_result: NodeResult,
    ) -> NodeFeatures:
        """Extract features including embedding and confidence.
        
        Requires execution results for the node.
        """
        features = self.extract_structural_features(workflow, node_id)
        
        # Add embedding
        features.embedding = node_result.embedding
        
        # Add confidence
        features.confidence = node_result.confidence
        
        return features
    
    def extract_all_structural_features(
        self,
        workflow: Workflow,
    ) -> Dict[str, NodeFeatures]:
        """Extract structural features for all nodes in a workflow."""
        return {
            node_id: self.extract_structural_features(workflow, node_id)
            for node_id in workflow.nodes
        }
    
    def extract_all_features_with_results(
        self,
        workflow: Workflow,
        node_results: Dict[str, NodeResult],
    ) -> Dict[str, NodeFeatures]:
        """Extract full features for all nodes with results."""
        features = {}
        for node_id in workflow.nodes:
            if node_id in node_results:
                features[node_id] = self.extract_features_with_results(
                    workflow, node_id, node_results[node_id]
                )
            else:
                # Node was skipped, use structural features only
                features[node_id] = self.extract_structural_features(workflow, node_id)
        
        return features
    
    def average_features_over_runs(
        self,
        feature_lists: List[Dict[str, NodeFeatures]],
    ) -> Dict[str, NodeFeatures]:
        """Average features over multiple runs (for denoising).
        
        Similar to how TRAIL averages over prompt tokens.
        
        Args:
            feature_lists: List of per-node features from different runs
            
        Returns:
            Averaged features
        """
        if not feature_lists:
            return {}
        
        # Get all node IDs
        all_node_ids = set()
        for features in feature_lists:
            all_node_ids.update(features.keys())
        
        averaged = {}
        for node_id in all_node_ids:
            # Collect features for this node across runs
            node_features = [
                f[node_id] for f in feature_lists
                if node_id in f
            ]
            
            if not node_features:
                continue
            
            # Use first as template for structural features (they're the same)
            template = node_features[0]
            
            # Average embeddings
            embeddings = [f.embedding for f in node_features if f.embedding is not None]
            avg_embedding = np.mean(embeddings, axis=0) if embeddings else None
            
            # Average confidence
            confidences = [f.confidence for f in node_features if f.confidence is not None]
            avg_confidence = np.mean(confidences) if confidences else None
            
            averaged[node_id] = NodeFeatures(
                node_id=node_id,
                role_onehot=template.role_onehot,
                depth=template.depth,
                fan_out=template.fan_out,
                downstream_reach=template.downstream_reach,
                has_downstream_verifier=template.has_downstream_verifier,
                is_optional=template.is_optional,
                is_speculative=template.is_speculative,
                num_inputs=template.num_inputs,
                embedding=avg_embedding,
                confidence=avg_confidence,
            )
        
        return averaged


def prepare_training_data(
    features_by_workflow: Dict[str, Dict[str, NodeFeatures]],
    labels_by_workflow: Dict[str, Dict[str, float]],
    include_embedding: bool = True,
    view: Optional[str] = None,
) -> Tuple[np.ndarray, np.ndarray, List[Tuple[str, str]]]:
    """Prepare training data from features and *measured* EC labels.

    ``labels_by_workflow`` must be fault-injection scores, not hidden
    simulator importance.
    """
    chosen_view = view or ("agentqo" if include_embedding else "structure")
    X_list = []
    y_list = []
    ids: List[Tuple[str, str]] = []

    for workflow_name, node_features in features_by_workflow.items():
        if workflow_name not in labels_by_workflow:
            continue
        workflow_labels = labels_by_workflow[workflow_name]
        for node_id, features in node_features.items():
            if node_id not in workflow_labels:
                continue
            X_list.append(features.as_vector(chosen_view))
            y_list.append(workflow_labels[node_id])
            ids.append((workflow_name, node_id))

    if not X_list:
        return np.empty((0, 0)), np.empty((0,)), []
    return np.asarray(X_list), np.asarray(y_list, dtype=np.float64), ids
