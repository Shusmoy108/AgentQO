"""
Ranking metrics for EC prediction evaluation.

Following TRAIL's evaluation style:
- Spearman correlation for ranking quality
- Top-k precision for identifying critical nodes
- Kendall's tau for robust rank correlation
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy import stats


def spearman_correlation(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Tuple[float, float]:
    """Compute Spearman rank correlation.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        (correlation, p_value)
    """
    if len(np.unique(y_true)) < 2 or len(np.unique(y_pred)) < 2:
        return 0.0, 1.0
    
    corr, pvalue = stats.spearmanr(y_true, y_pred)
    
    if np.isnan(corr):
        return 0.0, 1.0
    
    return float(corr), float(pvalue)


def kendall_tau(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Tuple[float, float]:
    """Compute Kendall's tau rank correlation.
    
    More robust to ties than Spearman.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        (correlation, p_value)
    """
    if len(np.unique(y_true)) < 2 or len(np.unique(y_pred)) < 2:
        return 0.0, 1.0
    
    corr, pvalue = stats.kendalltau(y_true, y_pred)
    
    if np.isnan(corr):
        return 0.0, 1.0
    
    return float(corr), float(pvalue)


def top_k_precision(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    k: int,
) -> float:
    """Compute precision for identifying top-k items.
    
    Measures how well we identify the most critical nodes.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        k: Number of top items to consider
        
    Returns:
        Precision (fraction of predicted top-k that are true top-k)
    """
    if k > len(y_true):
        k = len(y_true)
    
    if k == 0:
        return 0.0
    
    true_top_k = set(np.argsort(y_true)[-k:])
    pred_top_k = set(np.argsort(y_pred)[-k:])
    
    return len(true_top_k & pred_top_k) / k


def top_k_recall(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    k: int,
) -> float:
    """Compute recall for identifying top-k items.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        k: Number of top items to consider
        
    Returns:
        Recall (same as precision when k is fixed)
    """
    # For fixed k, precision = recall
    return top_k_precision(y_true, y_pred, k)


def ndcg_at_k(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    k: int,
) -> float:
    """Compute Normalized Discounted Cumulative Gain at k.
    
    Measures ranking quality with position-dependent weighting.
    
    Args:
        y_true: True relevance scores
        y_pred: Predicted scores
        k: Number of positions to consider
        
    Returns:
        NDCG@k score in [0, 1]
    """
    if k > len(y_true):
        k = len(y_true)
    
    if k == 0:
        return 0.0
    
    # Get indices sorted by predicted score (descending)
    pred_order = np.argsort(y_pred)[::-1][:k]
    
    # Compute DCG
    dcg = 0.0
    for i, idx in enumerate(pred_order):
        rel = y_true[idx]
        dcg += (2 ** rel - 1) / np.log2(i + 2)
    
    # Compute ideal DCG
    ideal_order = np.argsort(y_true)[::-1][:k]
    idcg = 0.0
    for i, idx in enumerate(ideal_order):
        rel = y_true[idx]
        idcg += (2 ** rel - 1) / np.log2(i + 2)
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def compute_ranking_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    k_values: List[int] = [1, 3, 5],
) -> Dict[str, float]:
    """Compute comprehensive ranking metrics.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        k_values: Values of k for top-k metrics
        
    Returns:
        Dictionary of metric names to values
    """
    metrics = {}
    
    # Correlation metrics
    spearman, spearman_p = spearman_correlation(y_true, y_pred)
    metrics["spearman"] = spearman
    metrics["spearman_pvalue"] = spearman_p
    
    tau, tau_p = kendall_tau(y_true, y_pred)
    metrics["kendall_tau"] = tau
    metrics["kendall_tau_pvalue"] = tau_p
    
    # Top-k metrics
    for k in k_values:
        if k <= len(y_true):
            metrics[f"precision_at_{k}"] = top_k_precision(y_true, y_pred, k)
            metrics[f"ndcg_at_{k}"] = ndcg_at_k(y_true, y_pred, k)
    
    # Error metrics (treating as regression)
    metrics["mae"] = float(np.mean(np.abs(y_true - y_pred)))
    metrics["rmse"] = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    
    # R-squared
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    metrics["r2"] = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    return metrics
