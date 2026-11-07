"""M4 rules and estimators."""

from itertools import combinations

import pytest

from agentqo.policies.v2_rules import (
    all_rules,
    confident_uv_order,
    independence_additive,
    independence_multiplicative,
    output_order,
    pairs_to_measure,
    pairwise_corrected,
    structural_order,
)
from agentqo.workflows.library import create_math_reasoning_workflow
from scripts.v2.rules_report import estimator_tables, h1c, parse_upgraded, plan_label, rule_rows

WF = create_math_reasoning_workflow(3)
AGENTS = list(WF.topological_order)
UV = {"planner": .05, "step_1": .01, "step_2": .00, "step_3": -.01, "aggregator": .10, "verifier": .20}
LOW = {"planner": -.01, "step_1": -.02, "step_2": -.03, "step_3": -.03, "aggregator": .02, "verifier": .10}
LABELS = {a: {"uv": UV[a], "uv_ci_low": LOW[a], "ec_synthetic": i, "ec_real": -i} for i, a in enumerate(AGENTS)}


def exact(gains, pair_bonus=None):
    """Additive truth with optional pair interactions."""
    out = {}
    for r in range(len(AGENTS) + 1):
        for p in combinations(AGENTS, r):
            plan = frozenset(p)
            x = .4 + sum(gains[v] for v in plan)
            for pair, b in (pair_bonus or {}).items():
                if pair <= plan:
                    x += b
            out[plan] = x
    return out


def test_every_rule_gives_a_plan_per_budget():
    rules = all_rules(LABELS, WF)
    assert set(rules) == {"all_small", "all_large", "structural_topk", "output_topk", "ec_topk",
                          "ec_real_topk", "uv_topk", "confident_uv"}
    for name, by_k in rules.items():
        assert sorted(by_k) == list(range(1, 7))
    for name in set(rules) - {"all_small", "all_large"}:
        for k in range(1, 7):
            assert len(rules[name][k]) == k
    assert rules["all_small"][3] == frozenset() and rules["all_large"][1] == frozenset(AGENTS)


def test_orders_match_earlier_definitions():
    assert structural_order(WF) == AGENTS  # a chain: reach falls along it
    assert output_order(WF) == AGENTS[::-1]
    assert all_rules(LABELS, WF)["uv_topk"][2] == {"verifier", "aggregator"}
    assert all_rules(LABELS, WF)["ec_topk"][1] == {"verifier"}
    assert all_rules(LABELS, WF)["ec_real_topk"][1] == {"planner"}


def test_confident_uv_uses_ci_then_structure():
    assert confident_uv_order(LABELS, WF) == ["verifier", "aggregator", "planner", "step_1", "step_2", "step_3"]


def test_estimators_exact_on_additive_truth():
    truth = exact({a: .02 for a in AGENTS})
    add = independence_additive(truth)
    for plan, acc in truth.items():
        assert add(plan) == pytest.approx(acc)
    assert independence_multiplicative(truth)(frozenset({"planner"})) == pytest.approx(.42)
    assert independence_multiplicative(truth)(frozenset({"planner", "verifier"})) == pytest.approx(.4 * 1.05 ** 2)


def test_pairwise_recovers_a_measured_interaction():
    gains = {"planner": .10, "step_1": .0, "step_2": .0, "step_3": .0, "aggregator": .12, "verifier": .14}
    pair = frozenset({"aggregator", "verifier"})
    truth = exact(gains, {pair: -.08})
    assert pair in pairs_to_measure(truth, AGENTS, 3)
    pw = pairwise_corrected(truth, AGENTS, 3)
    add = independence_additive(truth)
    assert pw(frozenset(AGENTS)) == pytest.approx(truth[frozenset(AGENTS)])
    assert add(pair) == pytest.approx(truth[pair] + .08)


def test_pairwise_m_limits_which_pairs_count():
    gains = {"planner": .10, "step_1": .0, "step_2": .0, "step_3": .0, "aggregator": .12, "verifier": .14}
    truth = exact(gains, {frozenset({"planner", "step_1"}): .05})
    assert frozenset({"planner", "step_1"}) not in pairs_to_measure(truth, AGENTS, 3)
    assert len(pairs_to_measure(truth, AGENTS, 2)) == 1


def test_clipping_and_zero_baseline():
    truth = exact({a: .3 for a in AGENTS})
    assert independence_additive(truth)(frozenset(AGENTS)) == 1.0
    zero = {frozenset(): 0.0, frozenset({"planner"}): .2}
    assert independence_multiplicative(zero)(frozenset({"planner"})) == pytest.approx(.2)


def test_estimator_table_splits_held_out_from_inputs():
    gains = {"planner": .10, "step_1": .0, "step_2": .0, "step_3": .0, "aggregator": .12, "verifier": .14}
    truth = exact(gains, {frozenset({"aggregator", "verifier"}): -.08})
    rows, detail, thresholds = estimator_tables(truth, AGENTS, 3)
    by = {r["estimator"]: r for r in rows}
    assert by["pairwise_corrected"]["n_held_out"] == 64 - 1 - 6 - 3
    assert by["pairwise_corrected"]["mae_held_out"] < by["independence_additive"]["mae_held_out"]
    assert len(detail) == 4 * 64 and set(thresholds) == {"p25", "p50", "p75"}
    assert 0 <= by["independence_additive"]["feasibility_wrong_p50"] <= 1


def test_rule_rows_report_regret_within_budget():
    truth = exact({"planner": .1, "step_1": .0, "step_2": .0, "step_3": .0, "aggregator": .2, "verifier": .3})
    rows = rule_rows(all_rules(LABELS, WF), truth, AGENTS)
    r = next(x for x in rows if x["rule"] == "structural_topk" and x["budget"] == 1)
    assert r["upgraded"] == "planner"
    assert r["best_accuracy_at_budget"] == pytest.approx(.7) and r["regret"] == pytest.approx(.2) and not r["is_best"]
    assert next(x for x in rows if x["rule"] == "ec_topk" and x["budget"] == 1)["is_best"]


def test_h1c_share_and_top2():
    full = [{"agent": a, "uv": UV[a], "reruns_used": 10, "reruns_full": 10} for a in AGENTS]
    fast = [{"agent": a, "uv": UV[a], "reruns_used": 2, "reruns_full": 10} for a in AGENTS]
    res = h1c(full, fast)
    assert res["share"] == .2 and res["top2_same"]


def test_plan_labels_round_trip():
    for text in ("none", "all", "aggregator,planner"):
        assert plan_label(parse_upgraded(text, AGENTS), AGENTS) == text


def test_logit_additive_estimator_e4():
    import math
    from agentqo.policies.v2_rules import logit_additive
    a, b = frozenset({"a"}), frozenset({"b"})
    measured = {frozenset(): 0.5, a: 0.75, b: 0.5}
    est = logit_additive(measured)
    assert est(frozenset()) == pytest.approx(0.5) and est(a) == pytest.approx(0.75)
    assert est(a | b) == pytest.approx(0.75)  # b adds nothing in log-odds
    two = logit_additive({frozenset(): 0.5, a: 0.75, b: 0.75})(a | b)
    assert two == pytest.approx(1 / (1 + math.exp(-2 * math.log(3))))  # log-odds add
    assert 0 < logit_additive({frozenset(): 0.0, a: 1.0})(a) < 1  # clipped, finite
