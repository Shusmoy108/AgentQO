"""SIMULATED scalability study (labeled as such): synthetic 10/15/20/30-agent, 3-tier workflows whose
gains, label errors and pair interactions are sampled from the measured distributions of the 11 lease
settings. NSGA-II (pairwise_corrected m 3 and independence) vs Abacus-style vs random at 200 verified
plans, against a long oracle NSGA-II run on the true function.

    python3 -m agentqo.search.scalability [--seeds 30] [--workers 9]
"""

from __future__ import annotations

import argparse
import csv
import os
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402

from agentqo.search.ground_truth import ROOT, SETTINGS, hv2, load_setting, pareto_mask  # noqa: E402
from agentqo.search.methods import HP, nsga2, pick  # noqa: E402
from agentqo.search.surrogates import label_terms  # noqa: E402

SIZES = (10, 15, 20, 30)
BUDGET = 200
ORACLE = {"pop": 200, "generations": 300}
REF_N = 6            # agents in the measured math workflows; gains scale by REF_N / n
REF_PAIRS = 15       # interacting agent pairs expected in a synthetic workflow (C(6, 2))


def measured_pools():
    """Pools from the exhaustive lease settings (eval accuracy unless noted)."""
    pools = {k: [] for k in ("base", "gL", "dXL", "rcost", "noise", "pair")}
    for name in SETTINGS:
        s = load_setting(name, with_latency=False)
        t = label_terms(s)
        z = np.zeros(s.n, dtype=int)
        b, bc = s.acc[s.row(z)], s.cost[s.row(z)]
        pools["base"].append(b)
        single = {}
        for i in range(s.n):
            for tt in range(1, len(s.tiers)):
                g = z.copy(); g[i] = tt
                single[(i, tt)] = s.acc[s.row(g)] - b
                pools["noise"].append(t.gain[i, tt] - single[(i, tt)])
                if tt == 1:
                    pools["gL"].append(single[(i, tt)])
                    pools["rcost"].append((s.cost[s.row(g)] - bc) / bc)
                else:
                    pools["dXL"].append(single[(i, 2)] - single[(i, 1)])
        for (i, ti), (j, tj) in combinations(single, 2):
            if i != j:
                g = z.copy(); g[i], g[j] = ti, tj
                pools["pair"].append(s.acc[s.row(g)] - b - single[(i, ti)] - single[(j, tj)])
    return {k: np.array(v) for k, v in pools.items()}


class Synthetic:
    def __init__(self, n: int, pools, rng):
        self.n, sc = n, REF_N / n
        self.base = rng.choice(pools["base"])
        gL = rng.choice(pools["gL"], n) * sc
        gX = gL + rng.choice(pools["dXL"], n) * sc
        self.gain = np.c_[np.zeros(n), gL, gX]
        rc = np.abs(rng.choice(pools["rcost"], n))
        self.dcost = np.c_[np.zeros(n), rc, 2 * rc]          # xl API price = 2 x large (v2_prices.yaml)
        self.label_gain = self.gain + np.c_[np.zeros(n), rng.choice(pools["noise"], (n, 2)) * sc]
        p = min(1.0, REF_PAIRS / (n * (n - 1) / 2))
        self.pairs = {}
        for i, j in combinations(range(n), 2):
            if rng.random() < p:
                for ti in (1, 2):
                    for tj in (1, 2):
                        self.pairs[((i, ti), (j, tj))] = rng.choice(pools["pair"])
        self.cmax = 1 + self.dcost[:, 2].sum()

    def _pairsum(self, G, table):
        out = np.zeros(len(G))
        for ((i, ti), (j, tj)), d in table.items():
            out += d * ((G[:, i] == ti) & (G[:, j] == tj))
        return out

    def acc(self, G):
        G = np.asarray(G)
        return np.clip(self.base + self.gain[np.arange(self.n), G].sum(1) + self._pairsum(G, self.pairs), 0, 1)

    def cost(self, G):
        return 1 + self.dcost[np.arange(self.n), np.asarray(G)].sum(1)


def surrogate(sy: Synthetic, kind: str):
    """Returns (objective fn, plans the surrogate verified). Cost is known (additive token prices)."""
    idx = np.arange(sy.n)
    verified, delta = [], {}
    base = sy.base
    if kind == "pairwise":
        z = np.zeros(sy.n, dtype=int)
        verified.append(z)
        opts = sorted(((i, t) for i in range(sy.n) for t in (1, 2)), key=lambda o: -sy.label_gain[o])[:3]
        for (i, ti), (j, tj) in combinations(opts, 2):
            if i != j:
                g = z.copy(); g[i], g[j] = ti, tj
                verified.append(g)
                delta[((i, ti), (j, tj))] = sy.acc(g[None])[0] - base - sy.label_gain[i, ti] - sy.label_gain[j, tj]

    def f(G):
        G = np.asarray(G)
        a = base + sy.label_gain[idx, G].sum(1) + sy._pairsum(G, delta)
        return np.c_[sy.cost(G), -np.clip(a, 0, 1)]
    return f, verified


def abacus_dp(sy: Synthetic):
    """Exact Pareto front of the independence estimate by per-agent Pareto merging (additive objectives)."""
    pts = [(1.0, sy.base, ())]
    for i in range(sy.n):
        cand = [(c + sy.dcost[i, t], a + sy.label_gain[i, t], g + (t,)) for c, a, g in pts for t in range(3)]
        F = np.array([[c, -a] for c, a, _ in cand])
        keep = pareto_mask(F)
        pts = [p for p, k in zip(cand, keep) if k]
    G = np.array([g for _, _, g in pts])
    return G, np.c_[[c for c, _, _ in pts], [-min(1, max(0, a)) for _, a, _ in pts]]


def hv(sy, G):
    G = np.asarray(G)
    return hv2(sy.acc(G), sy.cost(G), sy.cmax)


def one(args):
    n, seed, pools = args
    rng = np.random.default_rng(10_000 + 100 * n + seed)
    sy = Synthetic(n, pools, rng)
    card = np.full(n, 3)
    found = {}
    for kind in ("pairwise", "independence"):
        f, ver = surrogate(sy, kind)
        G, F = nsga2(card, f, np.random.default_rng(seed), HP["generations"])
        chosen = list(ver) + [G[i] for i in pick(F, BUDGET - len(ver))]
        found[f"nsga2_{kind}"] = np.array(chosen)
    G, F = abacus_dp(sy)
    front_size = len(G)
    take = pick(F, BUDGET)
    extra = BUDGET - len(take)  # DP front smaller than B: fill at random (logged)
    found["abacus"] = np.r_[G[take], rng.integers(0, 3, (extra, n))] if extra > 0 else G[take]
    found["random"] = rng.integers(0, 3, (BUDGET, n))
    truef = lambda X: np.c_[sy.cost(X), -sy.acc(X)]
    OG, OF = nsga2(card, truef, np.random.default_rng(seed), ORACLE["generations"], pop=ORACLE["pop"])
    ref = np.r_[OG[pareto_mask(OF)], *found.values()]
    ref_hv = hv(sy, ref)
    rows = [{"n_agents": n, "seed": seed, "method": m, "budget": BUDGET, "verified": len(np.unique(G_, axis=0)),
             "hv_ratio": hv(sy, G_) / ref_hv, "oracle_hv_ratio": hv(sy, OG[pareto_mask(OF)]) / ref_hv,
             "abacus_front_size": front_size if m == "abacus" else "",
             "n_interacting_pairs": len(sy.pairs) // 4, "simulated": True} for m, G_ in found.items()]
    print(f"n={n} seed={seed} done", flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--workers", type=int, default=9)
    ap.add_argument("--out", default=str(ROOT / "results" / "search" / "scalability_SIMULATED.csv"))
    a = ap.parse_args()
    pools = measured_pools()
    with Pool(a.workers) as p:
        rows = [r for rs in p.map(one, [(n, s, pools) for n in SIZES for s in range(a.seeds)]) for r in rs]
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {a.out}")


if __name__ == "__main__":
    main()
