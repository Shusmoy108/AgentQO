"""Search methods over plan genomes. Each method proposes with a surrogate only, then verifies up to
B plans by looking up their true values (Verifier); fronts are built from verified plans only.

Genome: one tier index per agent, plus (3-objective runs) a placement index as the last gene.
Hyperparameters are frozen in HP (docs/search_prereg.md).
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from agentqo.search.ground_truth import Setting, pareto_mask
from agentqo.search.surrogates import Surrogate, label_terms, make_surrogate

HP = {"pop": 40, "crossover": 0.9, "mutation": "1/n", "generations": 50,
      "mopso_w": 0.4, "mopso_c1": 0.3, "mopso_c2": 0.3, "gde3_F": 0.5, "gde3_CR": 0.9,
      "active_rounds": 4}


class BudgetExceeded(RuntimeError):
    pass


class Verifier:
    """Budget accounting: each distinct (row, placement) looked up costs 1; repeats are free."""

    def __init__(self, budget: int):
        self.budget, self.items = budget, []

    def __call__(self, row: int, placement: Optional[int] = None) -> None:
        key = (int(row), placement)
        if key in self.items:
            return
        if len(self.items) >= self.budget:
            raise BudgetExceeded(f"budget {self.budget} spent")
        self.items.append(key)

    @property
    def left(self) -> int:
        return self.budget - len(self.items)

    @property
    def rows(self) -> List[int]:
        return [r for r, _ in self.items]


# ------------------------------------------------------------------ multi-objective helpers
def nd_ranks(F: np.ndarray, need: Optional[int] = None) -> np.ndarray:
    """Non-dominated sorting rank (0 = first front). Stops peeling once `need` rows are ranked."""
    rank = np.full(len(F), np.iinfo(np.int32).max, dtype=np.int64)
    left = np.arange(len(F))
    r = 0
    while len(left) and (need is None or (rank < r).sum() < need):
        m = pareto_mask(F[left])
        rank[left[m]] = r
        left = left[~m]
        r += 1
    return rank


def crowding(F: np.ndarray) -> np.ndarray:
    n, d = F.shape
    cd = np.zeros(n)
    if n <= 2:
        return np.full(n, np.inf)
    for k in range(d):
        o = np.argsort(F[:, k], kind="stable")
        span = F[o[-1], k] - F[o[0], k] or 1.0
        cd[o[0]] = cd[o[-1]] = np.inf
        cd[o[1:-1]] += (F[o[2:], k] - F[o[:-2], k]) / span
    return cd


def survive(G: np.ndarray, F: np.ndarray, k: int) -> np.ndarray:
    """NSGA-II environmental selection: indices of k survivors by rank then crowding."""
    rank = nd_ranks(F, need=k)
    keep: List[int] = []
    for r in range(rank[rank < np.iinfo(np.int32).max].max() + 1):
        idx = np.flatnonzero(rank == r)
        if len(keep) + len(idx) <= k:
            keep += idx.tolist()
        else:
            cd = crowding(F[idx])
            keep += idx[np.argsort(-cd, kind="stable")][: k - len(keep)].tolist()
            break
    return np.array(keep)


def spread_pick(F: np.ndarray, k: int) -> np.ndarray:
    """k indices spread evenly along the first objective (extremes included)."""
    o = np.argsort(F[:, 0], kind="stable")
    if k >= len(o):
        return o
    pos = np.unique(np.round(np.linspace(0, len(o) - 1, k)).astype(int))
    rest = np.setdiff1d(np.arange(len(o)), pos)
    pos = np.r_[pos, rest[: k - len(pos)]].astype(int)
    return o[pos]


def pick(F: np.ndarray, k: int, exclude: Sequence[int] = ()) -> List[int]:
    """Up to k candidate indices: surrogate front first, spread along cost, then next fronts."""
    ok = np.setdiff1d(np.arange(len(F)), np.asarray(exclude, dtype=int))
    if k <= 0 or not len(ok):
        return []
    rank = nd_ranks(F[ok], need=k)
    out: List[int] = []
    for r in range(rank[rank < np.iinfo(np.int32).max].max() + 1):
        idx = ok[rank == r]
        take = idx[spread_pick(F[idx], k - len(out))]
        out += take.tolist()
        if len(out) >= k:
            break
    return out[:k]


def _unique(G: np.ndarray) -> np.ndarray:
    return np.unique(G, axis=0)


# ------------------------------------------------------------------ evolutionary searches
def nsga2(card: np.ndarray, f: Callable, rng, gens: int, pop: int = HP["pop"], init=None):
    """Integer NSGA-II: binary tournament, uniform crossover (p 0.9), per-gene mutation 1/n.
    Returns the archive of every distinct genome evaluated and its objectives."""
    n = len(card)
    P = rng.integers(0, card, size=(pop, n)) if init is None else init
    FP = f(P)
    arch = {tuple(g): fp for g, fp in zip(P, FP)}
    for _ in range(gens):
        rank = nd_ranks(FP)
        cd = crowding(FP)
        a, b = rng.integers(0, pop, (2, pop))
        better = (rank[a] < rank[b]) | ((rank[a] == rank[b]) & (cd[a] >= cd[b]))
        par = P[np.where(better, a, b)]
        kids = par.copy()
        for i in range(0, pop - 1, 2):
            if rng.random() < HP["crossover"]:
                m = rng.random(n) < 0.5
                kids[i, m], kids[i + 1, m] = par[i + 1, m], par[i, m]
        mut = rng.random(kids.shape) < 1.0 / n
        shift = rng.integers(1, np.maximum(card, 2), size=kids.shape)
        kids = np.where(mut & (card > 1), (kids + shift) % card, kids)
        FK = f(kids)
        for g, fk in zip(kids, FK):
            arch.setdefault(tuple(g), fk)
        A, FA = np.r_[P, kids], np.r_[FP, FK]
        A, ui = np.unique(A, axis=0, return_index=True)
        FA = FA[ui]
        if len(A) < pop:  # refill with random genomes (tiny spaces)
            extra = rng.integers(0, card, size=(pop - len(A), n))
            A, FA = np.r_[A, extra], np.r_[FA, f(extra)]
        keep = survive(A, FA, pop)
        P, FP = A[keep], FA[keep]
    G = np.array(list(arch))
    return G, np.array([arch[tuple(g)] for g in G])


def mopso(card: np.ndarray, f: Callable, rng, gens: int, pop: int = HP["pop"]):
    """Discrete MOPSO: each gene keeps its value (w), copies personal best (c1) or a leader drawn from
    the non-dominated archive (c2), else is redrawn; then per-gene mutation 1/n."""
    n = len(card)
    X = rng.integers(0, card, size=(pop, n))
    FX = f(X)
    pb, fpb = X.copy(), FX.copy()
    arch = {tuple(g): fx for g, fx in zip(X, FX)}
    w, c1 = HP["mopso_w"], HP["mopso_c1"]
    for _ in range(gens):
        AG = np.array(list(arch))
        AF = np.array([arch[tuple(g)] for g in AG])
        lead = AG[pareto_mask(AF)]
        L = lead[rng.integers(0, len(lead), pop)]
        u = rng.random((pop, n))
        X = np.where(u < w, X, np.where(u < w + c1, pb, L))  # remaining c2 = 1 - w - c1 -> leader
        mut = rng.random(X.shape) < 1.0 / n
        X = np.where(mut, rng.integers(0, card, size=X.shape), X)
        FX = f(X)
        for i, (g, fx) in enumerate(zip(X, FX)):
            arch.setdefault(tuple(g), fx)
            dom_new = (fx <= fpb[i]).all() and (fx < fpb[i]).any()
            dom_old = (fpb[i] <= fx).all() and (fpb[i] < fx).any()
            if dom_new or (not dom_old and rng.random() < 0.5):
                pb[i], fpb[i] = g, fx
    G = np.array(list(arch))
    return G, np.array([arch[tuple(g)] for g in G])


def gde3(card: np.ndarray, f: Callable, rng, gens: int, pop: int = HP["pop"]):
    """GDE3 on continuous genes in [0, card); rounding repair = floor and clip."""
    n = len(card)
    dec = lambda Z: np.minimum(np.floor(Z), card - 1).astype(np.int64)
    Z = rng.random((pop, n)) * card
    FZ = f(dec(Z))
    arch = {tuple(g): fz for g, fz in zip(dec(Z), FZ)}
    for _ in range(gens):
        newZ, newF = [], []
        for i in range(pop):
            a, b, c = rng.choice([j for j in range(pop) if j != i], 3, replace=False)
            v = np.clip(Z[a] + HP["gde3_F"] * (Z[b] - Z[c]), 0, card - 1e-9)
            m = rng.random(n) < HP["gde3_CR"]
            m[rng.integers(n)] = True
            u = np.where(m, v, Z[i])
            fu = f(dec(u[None]))[0]
            arch.setdefault(tuple(dec(u[None])[0]), fu)
            if (fu <= FZ[i]).all():
                newZ.append(u); newF.append(fu)
            elif (FZ[i] <= fu).all() and (FZ[i] < fu).any():
                newZ.append(Z[i]); newF.append(FZ[i])
            else:
                newZ += [Z[i], u]; newF += [FZ[i], fu]
        Z, FZ = np.array(newZ), np.array(newF)
        if len(Z) > pop:
            keep = survive(Z, FZ, pop)
            Z, FZ = Z[keep], FZ[keep]
    G = np.array(list(arch))
    return G, np.array([arch[tuple(g)] for g in G])


ENGINES = {"nsga2": nsga2, "mopso": mopso, "gde3": gde3}


# ------------------------------------------------------------------ objective builders
def objectives(sur: Surrogate, placement: bool) -> Callable:
    def f(G):
        G = np.asarray(G)
        cols = [sur.cost(G), -sur.acc(G)]
        if placement:
            cols.append(sur.latency(G))
        return np.c_[tuple(cols)]
    return f


def cards(s: Setting, placement: bool) -> np.ndarray:
    return np.array([len(s.tiers)] * s.n + ([2] if placement else []))


def _row(s: Setting, g) -> int:
    return s.row(np.asarray(g)[: s.n])


def verify_candidates(s, V: Verifier, G, F, placement: bool, k: Optional[int] = None) -> None:
    done = [i for i, g in enumerate(G) if (_row(s, g), int(g[-1]) if placement else None) in V.items]
    for i in pick(F, V.left if k is None else min(k, V.left), exclude=done):
        V(_row(s, G[i]), int(G[i][-1]) if placement else None)


def default_placement(sur: Surrogate, rows: Sequence[int]) -> List[int]:
    """Placement with the lowest predicted p95 for each plan (plan-first baseline)."""
    s = sur.s
    out = []
    for r in rows:
        G = np.array([np.r_[s.genomes[r], p] for p in (0, 1)])
        out.append(int(np.argmin(sur.latency(G))))
    return out


# ------------------------------------------------------------------ methods
def run_surrogate_search(s: Setting, budget: int, rng, kind: str, engine: str = "nsga2",
                         placement: bool = False, terms=None, gens: Optional[int] = None) -> Verifier:
    V = Verifier(budget)
    sur = make_surrogate(kind, s, budget, terms)
    for r in sur.verified[:budget]:
        V(r, 0 if placement else None)  # pair plans are timed at placement 0 (separate)
    G, F = ENGINES[engine](cards(s, placement), objectives(sur, placement), rng, gens or HP["generations"])
    verify_candidates(s, V, G, F, placement)
    V.surrogate = sur
    return V


def run_active(s: Setting, budget: int, rng, terms=None, gens: Optional[int] = None) -> Verifier:
    """Exploratory: NSGA-II with pairwise_corrected (m 3), verifying in rounds and re-fitting a
    ridge model of pair residuals on every verified plan between rounds."""
    V = Verifier(budget)
    sur = make_surrogate("pairwise_corrected_m3", s, budget, terms)
    for r in sur.verified[:budget]:
        V(r)
    gens = gens or HP["generations"]
    rounds = HP["active_rounds"]
    for k in range(rounds):
        if V.left <= 0:
            break
        G, F = nsga2(cards(s, False), objectives(sur, False), rng, gens)
        verify_candidates(s, V, G, F, False, k=int(np.ceil(V.left / (rounds - k))))
        sur.refit(V.rows)
    V.surrogate = sur
    return V


def run_plan_first(s: Setting, budget: int, rng, terms=None, gens: Optional[int] = None) -> Verifier:
    """S4 baseline: 2-objective search for plans, then each plan at its best predicted placement."""
    V2 = run_surrogate_search(s, budget, rng, "pairwise_corrected_m3", terms=terms, gens=gens)
    V = Verifier(budget)
    for r, p in zip(V2.rows, default_placement(V2.surrogate, V2.rows)):
        V(r, p)
    V.surrogate = V2.surrogate
    return V


def run_random(s: Setting, budget: int, rng, placement: bool = False, **_) -> Verifier:
    V = Verifier(budget)
    for r in rng.permutation(s.size)[:budget]:
        V(int(r), int(rng.integers(2)) if placement else None)
    return V


def run_greedy_uv(s: Setting, budget: int, rng=None, terms=None, **_) -> Verifier:
    """From all_small, repeatedly raise the one agent whose next tier has the best label UV per
    label cost; verify each plan on the path. Stops when every agent is at the top tier."""
    t = terms or label_terms(s)
    V = Verifier(budget)
    g = np.zeros(s.n, dtype=np.int64)
    V(s.row(g))
    while V.left > 0:
        moves = [(i, g[i] + 1) for i in range(s.n) if g[i] + 1 < len(s.tiers)]
        if not moves:
            break
        def score(m):
            i, tt = m
            dg = t.gain[i, tt] - t.gain[i, g[i]]
            dc = max(t.dcost[i, tt] - t.dcost[i, g[i]], 1e-12)
            return dg / dc
        i, tt = max(moves, key=score)
        g[i] = tt
        V(s.row(g))
    return V


def abacus_candidates(s: Setting, terms) -> Tuple[np.ndarray, np.ndarray]:
    """Independence (additive) estimates for every plan, exact enumeration (Abacus-style)."""
    sur = make_surrogate("independence_additive", s, 0, terms)
    return s.genomes, objectives(sur, False)(s.genomes)


def run_abacus(s: Setting, budget: int, rng=None, terms=None, **_) -> Verifier:
    V = Verifier(budget)
    G, F = abacus_candidates(s, terms or label_terms(s))
    verify_candidates(s, V, G, F, False)
    return V


def rule_plans(s: Setting, rule: str, terms) -> List[np.ndarray]:
    """Prefix plans k = 0..n of a fixed rule order; multi-tier settings: each prefix at every tier."""
    from agentqo.policies.v2_rules import rule_orders
    from scripts.run_real_pipeline import WORKFLOWS
    wf_key = ("hotpot_iso" if s.name.startswith("hotpot_iso") else s.name.split("_")[0])
    wf = WORKFLOWS[wf_key][1]()
    top = len(s.tiers) - 1  # labels for confident_uv: the top tier's label row
    labels = {a: {"uv": terms.gain[i, top], "uv_ci_low": terms.uv_ci_low[i, top],
                  "ec_synthetic": 0, "ec_real": 0} for i, a in enumerate(s.agents)}
    order = rule_orders(labels, wf)[rule]
    out = [np.zeros(s.n, dtype=np.int64)]
    for t in range(1, len(s.tiers)):
        for k in range(1, s.n + 1):
            g = np.zeros(s.n, dtype=np.int64)
            g[[s.agents.index(a) for a in order[:k]]] = t
            out.append(g)
    return out


def run_rule(s: Setting, budget: int, rng=None, terms=None, rule: str = "structural_topk", **_) -> Verifier:
    V = Verifier(budget)
    plans = rule_plans(s, rule, terms or label_terms(s))
    pos = np.unique(np.round(np.linspace(0, len(plans) - 1, min(budget, len(plans)))).astype(int))
    for i in pos:
        V(s.row(plans[i]))
    return V


RULES = {"rule_structural": "structural_topk", "rule_output": "output_topk", "rule_confident_uv": "confident_uv"}

METHODS_2D: Dict[str, Callable] = {
    "nsga2_pairwise_m3": lambda s, b, rng, **kw: run_surrogate_search(s, b, rng, "pairwise_corrected_m3", **kw),
    "nsga2_pairwise_m5": lambda s, b, rng, **kw: run_surrogate_search(s, b, rng, "pairwise_corrected_m5", **kw),
    "nsga2_indep_add": lambda s, b, rng, **kw: run_surrogate_search(s, b, rng, "independence_additive", **kw),
    "nsga2_indep_mult": lambda s, b, rng, **kw: run_surrogate_search(s, b, rng, "independence_multiplicative", **kw),
    "nsga2_logit_add": lambda s, b, rng, **kw: run_surrogate_search(s, b, rng, "logit_additive", **kw),
    "mopso_pairwise_m3": lambda s, b, rng, **kw: run_surrogate_search(s, b, rng, "pairwise_corrected_m3", "mopso", **kw),
    "gde3_pairwise_m3": lambda s, b, rng, **kw: run_surrogate_search(s, b, rng, "pairwise_corrected_m3", "gde3", **kw),
    "nsga2_active_m3": lambda s, b, rng, **kw: run_active(s, b, rng, **kw),
    "abacus": lambda s, b, rng, **kw: run_abacus(s, b, rng, terms=kw.get("terms")),
    "random": lambda s, b, rng, **kw: run_random(s, b, rng),
    "greedy_uv": lambda s, b, rng, **kw: run_greedy_uv(s, b, rng, terms=kw.get("terms")),
    **{name: (lambda r: lambda s, b, rng, **kw: run_rule(s, b, rng, terms=kw.get("terms"), rule=r))(r)
       for name, r in RULES.items()},
}

METHODS_3D: Dict[str, Callable] = {
    "joint_nsga2_pairwise_m3": lambda s, b, rng, **kw: run_surrogate_search(s, b, rng, "pairwise_corrected_m3", placement=True, **kw),
    "plan_first_nsga2_pairwise_m3": lambda s, b, rng, **kw: run_plan_first(s, b, rng, **kw),
    "random_3d": lambda s, b, rng, **kw: run_random(s, b, rng, placement=True),
}
