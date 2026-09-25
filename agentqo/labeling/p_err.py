"""Node error probability for real models (plan WP4, reference agreement).

p_err(v) = fraction of K samples of v (small model, temperature 0.7, fixed
seeds, on baseline inputs) whose extracted key differs from the reference
key. Planners have no key, so each planner sample is judged by the final
answer after running its descendants (K capped at 3 for cost).
"""

from __future__ import annotations

from typing import Callable, List, Optional

SAMPLE_INDEX_BASE = 100


def p_err_from_keys(sample_keys: List[Optional[str]], reference_key: Optional[str]) -> float:
    """Share of samples whose key differs from the reference (missing key = error)."""
    if not sample_keys:
        return 0.0
    return sum(1 for k in sample_keys if k is None or k != reference_key) / len(sample_keys)


def estimate_p_err(
    keyed: bool,
    k: int,
    sample_key: Callable[[int], Optional[str]],
    sample_final_key: Callable[[int], Optional[str]],
    reference_key: Optional[str],
    reference_final_key: Optional[str],
    planner_cap: int = 3,
) -> float:
    """``sample_key(i)`` / ``sample_final_key(i)`` run sample ``SAMPLE_INDEX_BASE + i``."""
    if keyed:
        return p_err_from_keys([sample_key(SAMPLE_INDEX_BASE + i) for i in range(k)], reference_key)
    n = min(k, planner_cap)
    return p_err_from_keys([sample_final_key(SAMPLE_INDEX_BASE + i) for i in range(n)], reference_final_key)
