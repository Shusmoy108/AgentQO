"""latsim: server model, closed loop, interference, beta borrowing, metrics."""

import math

import pytest

from agentqo.latsim.evaluate import metrics, n_upgraded
from agentqo.latsim.fit import betas_for, nearest_pair
from agentqo.latsim.sim import pct, replay, simulate

P = {"s": {"o": 0.01, "c": 1e-5, "a": 0.003, "b": 0.0005, "e": 1e-4},
     "l": {"o": 0.02, "c": 2e-5, "a": 0.008, "b": 0.001, "e": 2e-4}}


def iso(m, p, c):
    q = P[m]
    return q["o"] + q["c"] * p + c * (q["a"] + q["b"] + q["e"] * (p + c / 2) / 1000)


def test_isolated_call_matches_closed_form():
    assert replay([(0.0, "s", 200, 50)], P)[0] == pytest.approx(iso("s", 200, 50))
    assert replay([(0.0, "l", 0, 10)], P)[0] == pytest.approx(iso("l", 0, 10))


def test_batching_slows_each_call():
    one = replay([(0.0, "s", 0, 100)], P)[0]
    two = replay([(0.0, "s", 0, 100), (0.0, "s", 0, 100)], P)
    step1, step2 = P["s"]["a"] + P["s"]["b"] + P["s"]["e"] * 0.05, P["s"]["a"] + 2 * P["s"]["b"] + P["s"]["e"] * 0.1
    assert two[0] == pytest.approx(P["s"]["o"] + 100 * step2)
    assert two[0] > one == pytest.approx(P["s"]["o"] + 100 * step1)


def test_prefill_stalls_decode():
    alone = replay([(0.0, "s", 0, 100)], P)[0]
    with_prefill = replay([(0.0, "s", 0, 100), (0.1, "s", 5000, 1)], P)[0]
    assert with_prefill > alone + 0.9 * P["s"]["c"] * 5000


def test_k1_problem_latency_is_sum_of_isolated_calls():
    probs = [[("s", 100, 20), ("l", 50, 30)], [("l", 10, 5)]]
    lat = simulate(probs, P, k=1)
    assert lat[0] == pytest.approx(iso("s", 100, 20) + iso("l", 50, 30))
    assert lat[1] == pytest.approx(iso("l", 10, 5))


def test_interference_only_when_other_server_busy():
    probs = [[("s", 100, 10 + 15 * i), ("l", 100, 40)] for i in range(8)]  # varied, so problems desync
    betas = {("l", "s"): 2.0, ("s", "l"): 1.0}
    # K=1: calls never overlap, so a shared GPU costs nothing
    assert simulate(probs, P, 1, betas) == pytest.approx(simulate(probs, P, 1))
    sep, sh = simulate(probs, P, 4), simulate(probs, P, 4, betas)
    assert sum(sh) > sum(sep)


def test_closed_loop_k_and_call_latency():
    probs = [[("s", 0, 10)] * 3 for _ in range(6)]
    calls = []
    lat = simulate(probs, P, 3, call_latency=calls)
    assert [len(c) for c in calls] == [3] * 6
    assert all(math.isclose(sum(c), x) for c, x in zip(calls, lat))
    assert pct(lat, 0.95) == max(lat)


def test_beta_borrowing():
    q = "Qwen/Qwen2.5-"
    assert nearest_pair(f"{q}1.5B-Instruct", f"{q}7B-Instruct") == "q15_7"
    assert nearest_pair("microsoft/Phi-3.5-mini-instruct", "microsoft/phi-4") == "q3_14"
    params = {"betas": {p: {"shared": {"large_to_small": 2.0, "small_to_large": 1.0}} for p in ("q15_7", "q3_14", "g2_8")}}
    b = betas_for([f"{q}1.5B-Instruct", f"{q}7B-Instruct", f"{q}14B-Instruct"], "shared", params)
    assert len(b) == 6 and b[(f"{q}14B-Instruct", f"{q}7B-Instruct")] == 2.0
    assert betas_for([f"{q}1.5B-Instruct"], "separate", params) == {}


def test_metrics_and_plan_types():
    rows = [{"x_p50": 1.0, "x_p95": 2.0, "meas_p50": 1.0, "meas_p95": 2.1},
            {"x_p50": 1.0, "x_p95": 3.0, "meas_p50": 1.0, "meas_p95": 2.0},
            {"x_p50": 2.0, "x_p95": 4.0, "meas_p50": 2.0, "meas_p95": 4.0}]
    m = metrics(rows, "x")
    assert m["x_w10"] == pytest.approx(2 / 3) and m["x_w20"] == pytest.approx(2 / 3)
    assert n_upgraded("planner+verifier") == 2 and n_upgraded("only_step_1") == 1 and n_upgraded("all_large") == -1


def test_cold_runs_first_use_of_each_model(tmp_path):
    import json
    from agentqo.latsim.fit import cold_runs
    (tmp_path / "run_config.v2.json").write_text(json.dumps({"plans": "all_small,only_planner,all_large"}))
    calls = {("all_small", "0", "t"): [("s",)], ("only_planner", "0", "t"): [("l",), ("s",)],
             ("all_large", "0", "t"): [("l",)], ("all_small", "1", "t"): [("s",)]}
    assert cold_runs(str(tmp_path), calls) == {("all_small", "0"), ("only_planner", "0")}


def test_h3cfair_fixed_point_matches_h4_fit_for_two_models():
    from agentqo.latsim.h3cfair import fixed_point
    from scripts.h4_fit import simulate as h4_simulate
    nodes = [("s", 0.3), ("l", 0.9), ("s", 0.2), ("l", 0.5)]
    beta = {"small": 2.4, "large": 1.0}
    prof = {"mean": {f"n{i}": {"fidelity": "small" if m == "s" else "large", "completion_tokens": x}
                     for i, (m, x) in enumerate(nodes)}}
    st = h4_simulate(prof, lambda m, tok, conc: tok, 16, lambda m, uo, ov, conc: 1.0 + beta[m] * uo * ov)
    want = {m: 1.0 + beta[m] * st["busy"]["large" if m == "small" else "small"] * st["overlap"] for m in beta}
    got = fixed_point(nodes, {("l", "s"): 2.4, ("s", "l"): 1.0}, 16)
    assert got["s"] == pytest.approx(want["small"]) and got["l"] == pytest.approx(want["large"])


def test_h3cfair_k_interpolation():
    from agentqo.latsim.h3cfair import at_k
    by = {1: 1.0, 16: 2.0, 32: 4.0}
    assert at_k(by, 16) == 2.0 and at_k(by, 4) == pytest.approx(1.5) and at_k(by, 64) == 4.0
    assert at_k({16: 3.0}, 4) == 3.0
