"""Offline plan search: true front, hypervolume, each method on a toy 2^4 space, budget accounting."""

from itertools import product

import numpy as np
import pytest

from agentqo.search.ground_truth import V2, Setting, hv2, hv3, pareto_mask, true_front, true_hv
from agentqo.search.methods import (METHODS_2D, BudgetExceeded, Verifier, nd_ranks, run_abacus, run_greedy_uv,
                                    run_random, run_surrogate_search)
from agentqo.search.metrics import budget_for, metrics_2d
from agentqo.search.surrogates import LabelTerms, make_surrogate

GAIN = np.array([0.20, 0.10, 0.05, 0.02])
DCOST = np.array([4.0, 1.0, 2.0, 0.5])
INTER = {(0, 1): -0.15}  # a strong negative interaction between the two top agents


def toy(interaction=True):
    G = np.array(list(product([0, 1], repeat=4)), dtype=np.int8)
    acc = 0.4 + G @ GAIN
    if interaction:
        for (i, j), d in INTER.items():
            acc = acc + d * (G[:, i] & G[:, j])
    cost = 1.0 + G @ DCOST
    names = ["+".join(a for a, g in zip("abcd", r) if g) or "all_small" for r in G]
    s = Setting("toy", list("abcd"), ["small", "large"], names, G, acc, cost,
                np.zeros((16, 1)), ["p0"], {})
    terms = LabelTerms(0.4, 1.0, np.c_[np.zeros(4), GAIN], np.c_[np.zeros(4), DCOST], np.c_[np.zeros(4), GAIN])
    return s, terms


def brute_front(s):
    return sorted(i for i in range(s.size) if not any(
        s.acc[j] >= s.acc[i] and s.cost[j] <= s.cost[i] and (s.acc[j] > s.acc[i] or s.cost[j] < s.cost[i])
        for j in range(s.size)))


def test_true_front_matches_brute_force():
    for inter in (False, True):
        s, _ = toy(inter)
        assert sorted(true_front(s)) == brute_front(s)


def test_hypervolume_by_hand():
    assert hv2(np.array([0.6, 0.8]), np.array([0.5, 1.0]), 1.0) == pytest.approx(0.3)
    assert hv2(np.array([0.6, 0.5]), np.array([0.5, 0.7]), 1.0) == pytest.approx(0.3)  # dominated point ignored
    assert hv2(np.array([0.6, 0.8]), np.array([0.2, 0.6]), 1.0) == pytest.approx(0.4 * 0.6 + 0.4 * 0.8)
    assert hv3([0.6], [0.5], [0.5], 1.0, 1.0) == pytest.approx(0.5 * 0.5 * 0.6)
    # two points, one faster but less accurate: slices add up
    assert hv3([0.6, 0.8], [0.5, 0.5], [0.2, 0.6], 1.0, 1.0) == pytest.approx(0.5 * (0.4 * 0.6 + 0.4 * 0.8))


def test_nd_ranks_first_front():
    s, _ = toy()
    F = np.c_[s.cost, -s.acc]
    assert sorted(np.flatnonzero(nd_ranks(F) == 0)) == brute_front(s)
    assert (pareto_mask(F) == (nd_ranks(F) == 0)).all()


@pytest.mark.parametrize("method", ["nsga2_indep_add", "nsga2_logit_add", "mopso_pairwise_m3",
                                    "gde3_pairwise_m3", "nsga2_pairwise_m3", "abacus"])
def test_exact_surrogate_finds_known_front_at_front_size_budget(method):
    s, terms = toy(interaction=False)
    k = len(brute_front(s))
    budget = k + (1 if "pairwise" in method else 0) + (k // 2 if "pairwise" in method else 0)
    V = METHODS_2D[method](s, budget, np.random.default_rng(0), terms=terms)
    assert metrics_2d(s, V.rows)["hv_ratio"] == pytest.approx(1.0)
    assert len(V.rows) <= budget


def test_pairwise_surrogate_recovers_interaction_and_charges_budget():
    s, terms = toy(interaction=True)
    sur = make_surrogate("pairwise_corrected_m3", s, 8, terms)
    assert len(sur.verified) == 1 + 3  # all_small + 3 pairs (cap floor(8/2)-1 = 3)
    assert np.abs(sur.acc(s.genomes) - s.acc).max() == pytest.approx(0.0, abs=1e-12)
    ind = make_surrogate("independence_additive", s, 8, terms)
    assert ind.verified == [] and np.abs(ind.acc(s.genomes) - s.acc).max() == pytest.approx(0.15)
    V = run_surrogate_search(s, 8, np.random.default_rng(0), "pairwise_corrected_m3", terms=terms)
    assert set(sur.verified) <= set(V.rows) and len(V.rows) <= 8


def test_full_budget_methods_reach_true_hv():
    s, terms = toy()
    for fn in (lambda: run_random(s, 16, np.random.default_rng(1)), lambda: run_abacus(s, 16, terms=terms)):
        assert metrics_2d(s, fn().rows)["hv_ratio"] == pytest.approx(1.0)


def test_greedy_path_and_budget():
    s, terms = toy()
    V = run_greedy_uv(s, 16, terms=terms)
    assert V.rows[0] == s.row([0, 0, 0, 0]) and len(V.rows) == 5  # n + 1 plans on the path
    assert len(run_greedy_uv(s, 3, terms=terms).rows) == 3


def test_verifier_budget_accounting():
    V = Verifier(2)
    V(0); V(0); V(1)
    assert V.rows == [0, 1] and V.left == 0
    with pytest.raises(BudgetExceeded):
        V(2)
    assert budget_for(32, 0.01) == 4 and budget_for(729, 0.10) == 73


@pytest.mark.skipif(not (V2 / "P2" / "math_q15_7").exists(), reason="lease results not present")
def test_every_method_respects_budget_on_real_setting():
    from agentqo.search.ground_truth import load_setting
    from agentqo.search.surrogates import label_terms
    s = load_setting("math_q15_7", with_latency=False)
    assert true_hv(s) == pytest.approx(0.6796, abs=1e-4)  # results/v2/P6/search_ground_truth.md
    terms = label_terms(s)
    for b in (4, 6, 13):
        for name, fn in METHODS_2D.items():
            V = fn(s, b, np.random.default_rng(0), terms=terms)
            assert len(set(V.rows)) == len(V.rows) <= b, name
