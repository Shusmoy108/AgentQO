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
    def __init__(self, n: int, pools, rng, scale: float = 1.0):
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
                        self.pairs[((i, ti), (j, tj))] = scale * rng.choice(pools["pair"])
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


# ------------------------------------------------------------------ EXPLORATORY, not registered
SCALES = (0.0, 0.5, 1.0, 2.0, 4.0)
BUDGETS = (50, 100, 200)


def _pick_new(F, G, k, seen):
    """Up to k genomes from candidates G (surrogate order) not already in `seen`."""
    out = []
    for i in pick(F, min(len(G), k + len(seen))):
        key = tuple(G[i])
        if key not in seen:
            seen.add(key); out.append(G[i])
        if len(out) >= k:
            break
    return out


def run_active_syn(sy, budget, seed, rounds=HP["active_rounds"], lam=1.0):
    """NSGA-II with pairwise m 3, re-fitting a ridge model of pair residuals on all verified plans per round."""
    f0, ver = surrogate(sy, "pairwise")
    seen = {tuple(g) for g in ver}
    chosen = list(ver)
    opts = [(i, t) for i in range(sy.n) for t in (1, 2)]
    P = [(a, b) for a, b in combinations(opts, 2) if a[0] != b[0]]
    I = np.array([[a[0], a[1], b[0], b[1]] for a, b in P])
    feat = lambda G: ((G[:, I[:, 0]] == I[:, 1]) & (G[:, I[:, 2]] == I[:, 3])).astype(float)
    w = None
    rng = np.random.default_rng(seed)

    def f(G):
        F = f0(G)
        if w is not None:
            F[:, 1] = -np.clip(-F[:, 1] + feat(np.asarray(G)) @ w, 0, 1)
        return F
    for k in range(rounds):
        left = budget - len(chosen)
        if left <= 0:
            break
        G, F = nsga2(np.full(sy.n, 3), f, rng, HP["generations"])
        chosen += _pick_new(F, G, int(np.ceil(left / (rounds - k))), seen)
        Gv = np.array(chosen)
        X = feat(Gv)
        y = sy.acc(Gv) - (-f0(Gv)[:, 1])
        w = X.T @ np.linalg.solve(X @ X.T + lam * np.eye(len(X)), y)   # ridge, dual form
    return np.array(chosen)


def greedy_syn(sy, budget):
    g = np.zeros(sy.n, dtype=int)
    out = [g.copy()]
    while len(out) < budget:
        moves = [(i, g[i] + 1) for i in range(sy.n) if g[i] < 2]
        if not moves:
            break
        i, t = max(moves, key=lambda m: (sy.label_gain[m] - sy.label_gain[m[0], g[m[0]]])
                   / max(sy.dcost[m] - sy.dcost[m[0], g[m[0]]], 1e-12))
        g[i] = t
        out.append(g.copy())
    return np.array(out)


def inst_rng(n: int, seed: int):
    """Instance stream. Seeds < 1000 keep the exploratory formula; seeds >= 1000 (S6 confirmatory) use a
    separate SeedSequence so no confirmatory instance shares a stream with an exploratory one."""
    return np.random.default_rng(10_000 + 100 * n + seed if seed < 1000 else [n, seed, 2026])


def abacus_layers(sy: Synthetic, need: int, max_layers: int = 60):
    """Next-best fill: exact non-dominated layers 1..L of the independence estimate, L the smallest with
    >= need plans. Exact because with additive estimates a dominated prefix stays dominated under any common
    completion, so a plan in layer <= L only extends prefixes in prefix-layers <= L."""
    def peel(F, L):
        rank = np.full(len(F), L)
        left = np.arange(len(F))
        for r in range(L):
            if not len(left):
                break
            m = pareto_mask(F[left]); rank[left[m]] = r; left = left[~m]
        return rank
    for L in range(1, max_layers + 1):
        G, F = np.zeros((1, 0), dtype=int), np.array([[1.0, -sy.base]])
        for i in range(sy.n):
            t = np.tile(np.arange(3), len(G))
            G = np.c_[np.repeat(G, 3, 0), t]
            F = np.repeat(F, 3, 0) + np.c_[sy.dcost[i, t], -sy.label_gain[i, t]]
            keep = peel(F, L) < L
            G, F = G[keep], F[keep]
        if len(G) >= need or L == max_layers:
            return G, F, L


def strict_hv(sy, G):
    """EXPLORATORY: reference accuracy = the all_small plan's true accuracy."""
    G = np.asarray(G)
    base = sy.acc(np.zeros((1, sy.n), dtype=int))[0]
    return hv2(np.maximum(sy.acc(G) - base, 0), sy.cost(G), sy.cmax)


def sweep_one(args):
    """One synthetic instance (n, seed) at every interaction scale and budget."""
    import time
    n, seed, pools, scales, budgets = args
    rows = []
    for scale in scales:
        sy = Synthetic(n, pools, inst_rng(n, seed), scale)
        card = np.full(n, 3)
        t0 = time.time(); GA, FA = abacus_dp(sy); t_dp = time.time() - t0
        sur = {k: surrogate(sy, k) for k in ("pairwise", "independence")}
        arch = {k: nsga2(card, f, np.random.default_rng(seed), HP["generations"]) for k, (f, _) in sur.items()}
        found, layers = {}, {}
        for b in budgets:
            for k, (f, ver) in sur.items():
                seen = {tuple(g) for g in ver}
                found[(f"nsga2_{k}", b)] = np.array(list(ver) + _pick_new(arch[k][1], arch[k][0], b - len(ver), seen))
            take = pick(FA, b)
            rest = b - len(take)
            found[("abacus", b)] = np.r_[GA[take], np.random.default_rng(seed).integers(0, 3, (rest, n))] if rest > 0 else GA[take]
            t0 = time.time(); GL, FL, L = abacus_layers(sy, b); layers[b] = (L, time.time() - t0)
            found[("abacus_nextbest", b)] = GL[pick(FL, b)]
            found[("greedy_uv", b)] = greedy_syn(sy, b)
            found[("random", b)] = np.random.default_rng(seed + 1).integers(0, 3, (b, n))
            found[("nsga2_active", b)] = run_active_syn(sy, b, seed)
        OG, OF = nsga2(card, lambda X: np.c_[sy.cost(X), -sy.acc(X)], np.random.default_rng(seed),
                       ORACLE["generations"], pop=ORACLE["pop"])
        ref = np.r_[OG[pareto_mask(OF)], *found.values()]
        ref_hv, ref_strict = hv(sy, ref), strict_hv(sy, ref)
        indep_err = float(np.abs(sy._pairsum(OG, sy.pairs)).mean())  # mean |interaction| over oracle archive plans
        for (m, b), G_ in found.items():
            rows.append({"n_agents": n, "interaction_scale": scale, "seed": seed, "method": m, "budget": b,
                         "verified": len(np.unique(G_, axis=0)), "hv_ratio": hv(sy, G_) / ref_hv,
                         "strict_hv_ratio": strict_hv(sy, G_) / ref_strict if ref_strict > 0 else float("nan"),
                         "abacus_front_size": len(GA), "abacus_dp_s": t_dp, "abacus_options_per_agent": 3,
                         "abacus_layers_used": layers[b][0], "abacus_layers_s": layers[b][1],
                         "n_interacting_pairs": len(sy.pairs) // 4, "mean_abs_interaction": indep_err,
                         "simulated": True})
    print(f"sweep n={n} seed={seed} done", flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interaction-sweep", action="store_true", help="EXPLORATORY / S6 sweep")
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--seed-start", type=int, default=0)
    ap.add_argument("--sizes", default=",".join(map(str, SIZES)))
    ap.add_argument("--scales", default=",".join(map(str, SCALES)))
    ap.add_argument("--budgets", default=",".join(map(str, BUDGETS)))
    ap.add_argument("--workers", type=int, default=9)
    ap.add_argument("--out", default=str(ROOT / "results" / "search" / "scalability_SIMULATED.csv"))
    a = ap.parse_args()
    pools = measured_pools()
    if a.interaction_sweep:
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        sizes = [int(x) for x in a.sizes.split(",")]
        scales = [float(x) for x in a.scales.split(",")]
        budgets = [int(x) for x in a.budgets.split(",")]
        jobs = [(n, s, pools, scales, budgets) for n in sizes for s in range(a.seed_start, a.seed_start + a.seeds)]
        with Pool(a.workers) as p:
            rows = [r for rs in p.map(sweep_one, jobs) for r in rs]
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
        print(f"wrote {len(rows)} rows to {out}")
        return
    with Pool(a.workers) as p:
        rows = [r for rs in p.map(one, [(n, s, pools) for n in SIZES for s in range(a.seeds)]) for r in rs]
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {a.out}")


if __name__ == "__main__":
    main()
