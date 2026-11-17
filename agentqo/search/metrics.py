"""Per-run metrics on verified plans only."""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
from scipy.stats import spearmanr

from agentqo.search.ground_truth import PLACEMENTS, Setting, hv2, hv3, pareto_mask, true_hv

BUDGET_FRACS = (0.01, 0.02, 0.05, 0.10, 0.20)


def budget_for(size: int, frac: float) -> int:
    return max(4, int(round(frac * size)))


def igd(s: Setting, rows: List[int]) -> float:
    """Mean distance from each true-front plan to the nearest verified front plan, in
    (cost / max cost, accuracy) space."""
    cmax = s.cost.max()
    T = np.c_[s.cost, s.acc][pareto_mask(np.c_[s.cost, -s.acc])] / [cmax, 1]
    if not rows:
        return float("nan")
    Vp = np.c_[s.cost[rows], s.acc[rows]] / [cmax, 1]
    Vp = Vp[pareto_mask(np.c_[Vp[:, 0], -Vp[:, 1]])]
    return float(np.sqrt(((T[:, None, :] - Vp[None]) ** 2).sum(-1)).min(1).mean())


def regret(s: Setting, rows: List[int], q: float) -> float:
    """Best true accuracy at cost <= the q-quantile plan cost, minus the best verified one."""
    lim = np.quantile(s.cost, q)
    best = s.acc[s.cost <= lim].max()
    got = [s.acc[r] for r in rows if s.cost[r] <= lim]
    return float(best - (max(got) if got else 0.0))


def metrics_2d(s: Setting, rows: List[int], sur=None) -> Dict[str, float]:
    rows = sorted(set(rows))
    out = {"hv_ratio": hv2(s.acc[rows], s.cost[rows], s.cost.max()) / true_hv(s),
           "igd": igd(s, rows), "n_verified": len(rows),
           **{f"regret_p{int(q*100)}": regret(s, rows, q) for q in (0.25, 0.5, 0.75)},
           "surrogate_rho": float("nan")}
    if sur is not None:
        out["surrogate_rho"] = float(spearmanr(sur.acc(s.genomes), s.acc)[0])
    return out


def all_3d(s: Setting):
    """Every (plan, placement): accuracy, cost, true latency, rows."""
    acc = np.r_[s.acc, s.acc]
    cost = np.r_[s.cost, s.cost]
    lat = np.r_[s.latency[PLACEMENTS[0]], s.latency[PLACEMENTS[1]]]
    return acc, cost, lat


def true_hv3(s: Setting) -> float:
    acc, cost, lat = all_3d(s)
    return hv3(acc, cost, lat, cost.max(), lat.max())


def metrics_3d(s: Setting, items, hv_true: Optional[float] = None) -> Dict[str, float]:
    acc, cost, lat = all_3d(s)
    idx = sorted({r + s.size * p for r, p in items})
    hv_true = hv_true or true_hv3(s)
    return {"hv3_ratio": hv3(acc[idx], cost[idx], lat[idx], cost.max(), lat.max()) / hv_true,
            "n_verified": len(idx)}
