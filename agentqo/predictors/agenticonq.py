"""
Two-sided interaction cost model (AgentIconq) — H4.

A call's cost has two sides:
  1. own latency under the current co-located set
  2. extra latency imposed on every already-running co-located call

Shared prefixes make co-location *cheaper* (negative interaction).
That is the sign TRAIL/IconqSched-style predictors must capture.

This module is a physics-style GPU simulator plus a lightweight
regressor. Swap the simulator for vLLM traces later; the predictor
and metrics stay the same.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor


def q_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Geometric mean-style max(pred/true, true/pred). 1.0 is perfect."""
    yt = np.asarray(y_true, dtype=np.float64)
    yp = np.asarray(y_pred, dtype=np.float64)
    yt = np.clip(yt, 1e-9, None)
    yp = np.clip(yp, 1e-9, None)
    ratio = np.maximum(yp / yt, yt / yp)
    return float(np.mean(ratio))


def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def metrics_from_predictions(Y: np.ndarray, pred: np.ndarray) -> AgentIconqMetrics:
    own_t, own_p = Y[:, 0], pred[:, 0]
    imp_t, imp_p = Y[:, 1], pred[:, 1]
    sign_true = np.sign(imp_t)
    sign_pred = np.sign(imp_p)
    signs_ok = float(np.mean(sign_true == sign_pred))
    return AgentIconqMetrics(
        own_mae=mean_absolute_error(own_t, own_p),
        own_qerr=q_error(own_t, own_p),
        imposed_mae=mean_absolute_error(imp_t, imp_p),
        imposed_qerr=q_error(np.abs(imp_t) + 1e-6, np.abs(imp_p) + 1e-6),
        sign_accuracy=signs_ok,
    )


@dataclass
class AgentIconqMetrics:
    own_mae: float
    own_qerr: float
    imposed_mae: float
    imposed_qerr: float
    sign_accuracy: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "own_mae": self.own_mae,
            "own_qerr": self.own_qerr,
            "imposed_mae": self.imposed_mae,
            "imposed_qerr": self.imposed_qerr,
            "sign_accuracy": self.sign_accuracy,
        }


class AgentIconqPredictor:
    """Two-headed GBT: [own_latency, imposed_delay]."""

    def __init__(self, random_state: int = 42) -> None:
        self.model = MultiOutputRegressor(
            GradientBoostingRegressor(
                n_estimators=80,
                max_depth=3,
                random_state=random_state,
            )
        )
        self._fitted = False

    @property
    def name(self) -> str:
        return "AgentIconq"

    def fit(self, X: np.ndarray, Y: np.ndarray) -> None:
        self.model.fit(X, Y)
        self._fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise ValueError("Model must be fitted before prediction")
        return self.model.predict(X)

    def evaluate(self, X: np.ndarray, Y: np.ndarray) -> AgentIconqMetrics:
        return metrics_from_predictions(Y, self.predict(X))


class SingleCallBaseline:
    """Ignores the batch: predicts isolated latency, imposed delay = 0."""

    def __init__(self) -> None:
        self._own_mean = 0.0
        self._fitted = False

    @property
    def name(self) -> str:
        return "Single-call"

    def fit(self, X: np.ndarray, Y: np.ndarray) -> None:
        # Feature 0 is designed to be isolated latency in the simulator.
        self._own_mean = float(np.mean(Y[:, 0]))
        self._fitted = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        isolated = X[:, 0] if X.ndim == 2 else np.full(len(X), self._own_mean)
        out = np.zeros((len(isolated), 2))
        out[:, 0] = isolated
        return out

    def evaluate(self, X: np.ndarray, Y: np.ndarray) -> AgentIconqMetrics:
        return metrics_from_predictions(Y, self.predict(X))


class AdditiveBaseline:
    """Naive: own = isolated * (1 + n_colocated), imposed = isolated * 0.1 * n."""

    @property
    def name(self) -> str:
        return "Naive-additive"

    def fit(self, X: np.ndarray, Y: np.ndarray) -> None:
        return

    def predict(self, X: np.ndarray) -> np.ndarray:
        isolated = X[:, 0]
        n_col = X[:, 1]
        own = isolated * (1.0 + 0.15 * n_col)
        imposed = isolated * 0.10 * n_col
        return np.stack([own, imposed], axis=1)

    def evaluate(self, X: np.ndarray, Y: np.ndarray) -> AgentIconqMetrics:
        return metrics_from_predictions(Y, self.predict(X))


def analyze_h4_results(
    results: Dict[str, AgentIconqMetrics],
) -> Dict[str, Any]:
    ours = results.get("AgentIconq")
    if ours is None:
        return {"h4_holds": False, "reason": "AgentIconq missing"}
    single = results.get("Single-call")
    additive = results.get("Naive-additive")
    beats_single = single is None or ours.own_qerr < single.own_qerr
    beats_add = additive is None or ours.own_qerr < additive.own_qerr
    captures_sign = ours.sign_accuracy > 0.7
    return {
        "h4_holds": bool(beats_single and beats_add and captures_sign),
        "beats_single_call": beats_single,
        "beats_additive": beats_add,
        "captures_both_signs": captures_sign,
        "metrics": {k: v.to_dict() for k, v in results.items()},
    }
