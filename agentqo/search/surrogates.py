"""Plan surrogates for offline search. Accuracy and API cost of a genome (tier index per agent).

Single-agent terms come ONLY from label data (labels_v2.csv uv; labels_v2_per_problem.csv token
counts priced with configs/v2_prices.yaml). pairwise_corrected additionally uses measured plans
(all_small and the top-m pairs, looked up from the ground truth); each one is a verified plan
and is charged to the method's budget by the caller (Surrogate.verified).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List, Optional, Tuple

import numpy as np

from agentqo.metrics.cost_model import api_usd, load_prices
from agentqo.search.ground_truth import ROOT, V2, Setting, latsim_predictions, rd, PLACEMENTS

KINDS = ("independence_additive", "independence_multiplicative", "logit_additive",
         "pairwise_corrected_m3", "pairwise_corrected_m5")


@dataclass
class LabelTerms:
    base_acc: float          # all_small accuracy on the label problems
    base_cost: float         # all_small API USD per problem on the label problems
    gain: np.ndarray         # (n, T) accuracy gain of one agent at tier t (column 0 = 0)
    dcost: np.ndarray        # (n, T) API USD change of one agent at tier t (column 0 = 0)
    uv_ci_low: np.ndarray    # (n, T)


def label_terms(s: Setting) -> LabelTerms:
    prices = load_prices(ROOT / "configs" / "v2_prices.yaml")
    n, T = s.n, len(s.tiers)
    gain, dcost, low = np.zeros((n, T)), np.zeros((n, T)), np.zeros((n, T))
    base_acc = base_cost = None
    for t, tier in enumerate(s.tiers[1:], start=1):
        d = V2 / s.label_dirs[tier]
        d = d / "labels" if (d / "labels").exists() else d  # X3 label folders hold the csv files directly
        lab = {r["agent"]: r for r in rd(d / "labels_v2.csv")}
        pp = rd(d / "labels_v2_per_problem.csv")
        f = lambda r, k: float(r[k] or 0)
        base = {r["task_id"]: (f(r, "baseline_correct"),
                               api_usd(prices, "small", f(r, "base_small_in"), f(r, "base_small_out")))
                for r in pp}
        if base_acc is None:  # the base comes from the large-tier label run
            base_acc = float(np.mean([v[0] for v in base.values()]))
            base_cost = float(np.mean([v[1] for v in base.values()]))
        for i, a in enumerate(s.agents):
            gain[i, t] = float(lab[a]["uv"])
            low[i, t] = float(lab[a]["uv_ci_low"])
            rows = [r for r in pp if r["agent"] == a and r.get("skipped_plus") != "True"]
            plus = [api_usd(prices, "small", f(r, "plus_small_in"), f(r, "plus_small_out"))
                    + api_usd(prices, tier, f(r, "plus_large_in"), f(r, "plus_large_out")) for r in rows]
            dcost[i, t] = float(np.mean(plus)) - float(np.mean([base[r["task_id"]][1] for r in rows]))
    return LabelTerms(base_acc, base_cost, gain, dcost, low)


def _logit(p):
    p = np.clip(p, 0.01, 0.99)
    return np.log(p / (1 - p))


@dataclass
class Surrogate:
    kind: str
    s: Setting
    terms: LabelTerms
    verified: List[int] = field(default_factory=list)   # ground-truth rows consumed (budget)
    base: float = 0.0
    pair_delta: Dict[Tuple[Tuple[int, int], Tuple[int, int]], float] = field(default_factory=dict)
    resid_w: Optional[np.ndarray] = None                  # active-learning pair residual weights
    _pairs_all: Optional[List[Tuple[Tuple[int, int], Tuple[int, int]]]] = None

    def acc(self, G: np.ndarray) -> np.ndarray:
        G = np.asarray(G)[:, : self.s.n]
        idx = np.arange(self.s.n)
        g = self.terms.gain[idx, G]                       # (N, n)
        b = self.terms.base_acc
        if self.kind == "independence_additive":
            return np.clip(b + g.sum(1), 0, 1)
        if self.kind == "independence_multiplicative":
            return np.clip(b * np.prod((b + g) / b, axis=1), 0, 1) if b > 0 else np.clip(b + g.sum(1), 0, 1)
        if self.kind == "logit_additive":
            lb = _logit(b)
            return 1 / (1 + np.exp(-(lb + (_logit(b + g) - lb).sum(1))))
        out = self.base + g.sum(1)
        for ((i, ti), (j, tj)), d in self.pair_delta.items():
            out = out + d * ((G[:, i] == ti) & (G[:, j] == tj))
        if self.resid_w is not None:
            out = out + self._pair_features(G) @ self.resid_w
        return np.clip(out, 0, 1)

    def cost(self, G: np.ndarray) -> np.ndarray:
        G = np.asarray(G)[:, : self.s.n]
        return self.terms.base_cost + self.terms.dcost[np.arange(self.s.n), G].sum(1)

    def latency(self, G: np.ndarray) -> np.ndarray:
        """latsim frozen pred_p95 (K=16); last gene is the placement index."""
        pred = latsim_predictions()
        G = np.asarray(G)
        return np.array([pred[(self.s.name, self.s.names[self.s.row(g[: self.s.n])], PLACEMENTS[g[-1]])]
                         for g in G])

    # ---------------------------------------------------------- active learning (exploratory)
    def _pair_features(self, G):
        if self._pairs_all is None:
            opts = [(i, t) for i in range(self.s.n) for t in range(1, len(self.s.tiers))]
            self._pairs_all = [(a, b) for a, b in combinations(opts, 2) if a[0] != b[0]]
        return np.stack([(G[:, i] == ti) & (G[:, j] == tj) for (i, ti), (j, tj) in self._pairs_all], 1).astype(float)

    def refit(self, rows: List[int], lam: float = 1.0) -> None:
        """Ridge fit of pair residuals (truth - current surrogate) on all verified plans."""
        self.resid_w = None
        G = self.s.genomes[rows]
        X = self._pair_features(G)
        y = self.s.acc[rows] - self.acc(G)
        self.resid_w = np.linalg.solve(X.T @ X + lam * np.eye(X.shape[1]), X.T @ y)


def pair_plan_order(terms: LabelTerms, s: Setting, m: int) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """Pairs of the top-m single options by label gain (options naming one agent twice dropped)."""
    opts = [(i, t) for i in range(s.n) for t in range(1, len(s.tiers))]
    top = sorted(opts, key=lambda o: (-terms.gain[o], o))[:m]
    return [(a, b) for a, b in combinations(top, 2) if a[0] != b[0]]


def max_pairs(budget: int) -> int:
    """Pair plans a pairwise surrogate may buy: half the budget minus all_small (logged choice)."""
    return max(0, budget // 2 - 1)


def adaptive_pairs(budget: int) -> int:
    """EXPLORATORY variant (not registered): pair plans capped at 25% of the budget."""
    return int(0.25 * budget)


def make_surrogate(kind: str, s: Setting, budget: int, terms: Optional[LabelTerms] = None,
                   pair_cap=max_pairs) -> Surrogate:
    terms = terms or label_terms(s)
    sur = Surrogate(kind, s, terms)
    if kind.startswith("pairwise_corrected") or kind == "active":
        m = 5 if kind.endswith("m5") else 3
        zero = np.zeros(s.n, dtype=np.int8)
        r0 = s.row(zero)
        sur.verified.append(r0)
        sur.base = float(s.acc[r0])
        for (i, ti), (j, tj) in pair_plan_order(terms, s, m)[: pair_cap(budget)]:
            g = zero.copy()
            g[i], g[j] = ti, tj
            r = s.row(g)
            sur.verified.append(r)
            sur.pair_delta[((i, ti), (j, tj))] = float(s.acc[r]) - sur.base - terms.gain[i, ti] - terms.gain[j, tj]
    return sur
