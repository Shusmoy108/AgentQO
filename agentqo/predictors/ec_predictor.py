"""
EC prediction models and baselines.

Models:
1. GBTECPredictor: Gradient boosted trees (XGBoost/sklearn)
2. MLPECPredictor: Neural network (PyTorch MLP, like TRAIL)

Baselines:
1. ConfidenceBaseline: Predicts EC from confidence only
2. StructureOnlyBaseline: Predicts EC from structural features only

Success for H2: AgentQO (structure + embedding) beats confidence-only
and is at least as good as structure-only.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


@dataclass
class PredictorMetrics:
    """Metrics for evaluating EC predictors.
    
    Attributes:
        mae: Mean absolute error
        rmse: Root mean squared error
        spearman_corr: Spearman rank correlation with true EC
        top_k_precision: Precision on identifying top-k critical nodes
        r2: R-squared score
        overhead_ms: Prediction overhead in milliseconds
    """
    mae: float
    rmse: float
    spearman_corr: float
    top_k_precision: Dict[int, float]  # k -> precision
    r2: float
    overhead_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mae": self.mae,
            "rmse": self.rmse,
            "spearman_corr": self.spearman_corr,
            "top_k_precision": self.top_k_precision,
            "r2": self.r2,
            "overhead_ms": self.overhead_ms,
        }


class ECPredictor(abc.ABC):
    """Abstract base class for EC predictors."""
    
    @abc.abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train the predictor.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: EC labels (n_samples,)
        """
        ...
    
    @abc.abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict EC scores.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            
        Returns:
            Predicted EC scores (n_samples,)
        """
        ...
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Model name for reporting."""
        ...
    
    def evaluate(
        self,
        X: np.ndarray,
        y_true: np.ndarray,
        top_k_values: List[int] = [1, 3, 5],
    ) -> PredictorMetrics:
        """Evaluate predictor on test data.
        
        Args:
            X: Feature matrix
            y_true: True EC labels
            top_k_values: K values for top-k precision
            
        Returns:
            PredictorMetrics with all evaluation metrics
        """
        import time
        from scipy import stats
        
        # Time prediction
        start = time.perf_counter()
        y_pred = self.predict(X)
        overhead_ms = (time.perf_counter() - start) * 1000
        
        # Basic metrics
        mae = np.mean(np.abs(y_true - y_pred))
        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
        
        # R-squared
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        
        # Spearman correlation
        if len(np.unique(y_true)) > 1 and len(np.unique(y_pred)) > 1:
            spearman_corr, _ = stats.spearmanr(y_true, y_pred)
        else:
            spearman_corr = 0.0
        
        # Top-k precision
        top_k_precision = {}
        for k in top_k_values:
            if k > len(y_true):
                top_k_precision[k] = 0.0
                continue
            
            true_top_k = set(np.argsort(y_true)[-k:])
            pred_top_k = set(np.argsort(y_pred)[-k:])
            precision = len(true_top_k & pred_top_k) / k
            top_k_precision[k] = precision
        
        return PredictorMetrics(
            mae=float(mae),
            rmse=float(rmse),
            spearman_corr=float(spearman_corr) if not np.isnan(spearman_corr) else 0.0,
            top_k_precision=top_k_precision,
            r2=float(r2),
            overhead_ms=overhead_ms,
        )


class GBTECPredictor(ECPredictor):
    """Gradient Boosted Trees predictor for EC.
    
    Uses sklearn's GradientBoostingRegressor.
    Robust, doesn't require feature scaling.
    """
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 5,
        learning_rate: float = 0.1,
        random_state: int = 42,
    ) -> None:
        self.model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state,
        )
        self._fitted = False
    
    @property
    def name(self) -> str:
        return "GBT"
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)
        self._fitted = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise ValueError("Model must be fitted before prediction")
        return self.model.predict(X)
    
    @property
    def feature_importances(self) -> np.ndarray:
        """Get feature importance scores."""
        if not self._fitted:
            raise ValueError("Model must be fitted first")
        return self.model.feature_importances_


class MLPECPredictor(ECPredictor):
    """MLP predictor for EC (similar to TRAIL's architecture).
    
    Uses PyTorch if available, falls back to sklearn MLPRegressor.
    """
    
    def __init__(
        self,
        hidden_dims: List[int] = [512, 256],
        learning_rate: float = 0.01,
        num_epochs: int = 30,
        batch_size: int = 32,
        random_state: int = 42,
    ) -> None:
        self.hidden_dims = hidden_dims
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.random_state = random_state
        
        self.scaler = StandardScaler()
        self._model = None
        self._fitted = False
        self._use_torch = self._check_torch()
    
    def _check_torch(self) -> bool:
        """Check if PyTorch is available."""
        try:
            import torch
            return True
        except ImportError:
            return False
    
    @property
    def name(self) -> str:
        return "MLP"
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        if self._use_torch:
            self._fit_torch(X_scaled, y)
        else:
            self._fit_sklearn(X_scaled, y)
        
        self._fitted = True
    
    def _fit_torch(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train using PyTorch."""
        import torch
        import torch.nn as nn
        import torch.optim as optim
        
        # Set seed
        torch.manual_seed(self.random_state)
        
        # Build model
        layers = []
        in_dim = X.shape[1]
        for hidden_dim in self.hidden_dims:
            layers.extend([
                nn.Linear(in_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1),
            ])
            in_dim = hidden_dim
        layers.append(nn.Linear(in_dim, 1))
        
        self._model = nn.Sequential(*layers)
        
        # Convert to tensors
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.FloatTensor(y).unsqueeze(1)
        
        # Training
        optimizer = optim.AdamW(self._model.parameters(), lr=self.learning_rate)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, self.num_epochs)
        criterion = nn.MSELoss()
        
        dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
        loader = torch.utils.data.DataLoader(
            dataset, batch_size=self.batch_size, shuffle=True
        )
        
        self._model.train()
        for epoch in range(self.num_epochs):
            for batch_X, batch_y in loader:
                optimizer.zero_grad()
                pred = self._model(batch_X)
                loss = criterion(pred, batch_y)
                loss.backward()
                optimizer.step()
            scheduler.step()
        
        self._model.eval()
    
    def _fit_sklearn(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fallback to sklearn MLPRegressor."""
        from sklearn.neural_network import MLPRegressor
        
        self._model = MLPRegressor(
            hidden_layer_sizes=tuple(self.hidden_dims),
            learning_rate_init=self.learning_rate,
            max_iter=self.num_epochs * (len(X) // self.batch_size + 1),
            batch_size=self.batch_size,
            random_state=self.random_state,
        )
        self._model.fit(X, y)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X_scaled = self.scaler.transform(X)
        
        if self._use_torch:
            import torch
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X_scaled)
                pred = self._model(X_tensor).squeeze().numpy()
            return pred
        else:
            return self._model.predict(X_scaled)


class ConfidenceBaseline(ECPredictor):
    """Baseline that predicts EC from confidence only.
    
    This baseline should be beaten by the full model.
    If confidence alone predicts EC well, there's less value in embeddings.
    """
    
    def __init__(self) -> None:
        self.model = Ridge(alpha=1.0)
        self._fitted = False
    
    @property
    def name(self) -> str:
        return "Confidence-Only"
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        conf = np.asarray(X, dtype=np.float64)
        if conf.ndim == 1:
            conf = conf.reshape(-1, 1)
        # Caller passes a confidence-only view. If a wider matrix is given,
        # use the last column (legacy layout).
        if conf.shape[1] > 1:
            conf = conf[:, -1:]
        self.model.fit(conf, y)
        self._fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise ValueError("Model must be fitted before prediction")
        conf = np.asarray(X, dtype=np.float64)
        if conf.ndim == 1:
            conf = conf.reshape(-1, 1)
        if conf.shape[1] > 1:
            conf = conf[:, -1:]
        return self.model.predict(conf)


class StructureOnlyBaseline(ECPredictor):
    """Baseline that predicts EC from structural features only.
    
    Uses the same model architecture as GBT but only structural features.
    This tests whether embeddings add value over structure alone.
    """
    
    def __init__(
        self,
        structural_dim: int = 13,  # NUM_ROLES + 7
        n_estimators: int = 100,
        random_state: int = 42,
    ) -> None:
        self.structural_dim = structural_dim
        self.model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            max_depth=5,
            random_state=random_state,
        )
        self._fitted = False
    
    @property
    def name(self) -> str:
        return "Structure-Only"
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        X_struct = X if X.shape[1] <= self.structural_dim else X[:, :self.structural_dim]
        self.model.fit(X_struct, y)
        self._fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise ValueError("Model must be fitted before prediction")
        X_struct = X if X.shape[1] <= self.structural_dim else X[:, :self.structural_dim]
        return self.model.predict(X_struct)


def compare_predictors(
    predictors: List[ECPredictor],
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    top_k_values: List[int] = [1, 3, 5],
) -> Dict[str, PredictorMetrics]:
    """Compare multiple predictors on the same data.
    
    Args:
        predictors: List of predictor instances
        X_train, y_train: Training data
        X_test, y_test: Test data
        top_k_values: K values for top-k precision
        
    Returns:
        Dictionary mapping predictor name to metrics
    """
    results = {}
    
    for predictor in predictors:
        predictor.fit(X_train, y_train)
        metrics = predictor.evaluate(X_test, y_test, top_k_values)
        results[predictor.name] = metrics
    
    return results


def analyze_h2_results(
    results: Dict[str, PredictorMetrics],
) -> Dict[str, Any]:
    """Analyze H2 results: Can EC be predicted better than baselines?
    
    H2: EC can be predicted cheaply, before a node finishes,
    better than confidence-only or structure-only baseline.
    
    Success criteria:
    - AgentQO beats Confidence-Only clearly (higher Spearman)
    - AgentQO is at least as good as Structure-Only
    """
    agentqo_names = ["AgentQO", "GBT", "MLP"]
    confidence_name = "Confidence-Only"
    structure_name = "Structure-Only"
    
    # Find best AgentQO model
    best_agentqo = None
    best_agentqo_score = -1
    for name in agentqo_names:
        if name in results:
            if results[name].spearman_corr > best_agentqo_score:
                best_agentqo = name
                best_agentqo_score = results[name].spearman_corr
    
    if best_agentqo is None:
        return {"h2_holds": False, "reason": "No AgentQO model found"}
    
    agentqo_metrics = results[best_agentqo]
    
    # Compare with confidence baseline
    beats_confidence = True
    confidence_margin = 0.0
    if confidence_name in results:
        confidence_metrics = results[confidence_name]
        confidence_margin = agentqo_metrics.spearman_corr - confidence_metrics.spearman_corr
        beats_confidence = confidence_margin > 0.05  # Clear margin
    
    # Compare with structure baseline
    at_least_structure = True
    structure_margin = 0.0
    if structure_name in results:
        structure_metrics = results[structure_name]
        structure_margin = agentqo_metrics.spearman_corr - structure_metrics.spearman_corr
        at_least_structure = structure_margin >= -0.02  # Allow small tolerance
    
    h2_holds = beats_confidence and at_least_structure
    
    return {
        "h2_holds": h2_holds,
        "best_model": best_agentqo,
        "spearman_correlation": agentqo_metrics.spearman_corr,
        "beats_confidence": beats_confidence,
        "confidence_margin": confidence_margin,
        "at_least_structure": at_least_structure,
        "structure_margin": structure_margin,
        "overhead_ms": agentqo_metrics.overhead_ms,
        "detailed_metrics": {name: m.to_dict() for name, m in results.items()},
    }
