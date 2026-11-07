"""M2 (fake backend), M5, M6, M7 and the H5a simulation."""

import json
import stat
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pytest

from agentqo.metrics.cost_model import load_prices
from agentqo.metrics.io import read_csv
from agentqo.policies.v2_rules import parse_plan_name, plan_name
from agentqo.workflows.library import create_math_reasoning_workflow, create_multihop_qa_workflow
from scripts.run_real_h3 import all_subset_plans
from scripts.v2.adaptive_check import run as adaptive_run
from scripts.v2.pareto import LatencyModel, constrained_best, dominates, hypervolume, pareto_front, two_step
from scripts.v2.routing_offline import disagree_each_other, disagree_with_majority, evaluate, key_entropy
from scripts.v2.run_placement import PowerLoggers

ROOT = Path(__file__).resolve().parent.parent
WF = create_math_reasoning_workflow(3)
TOPO = list(WF.topological_order)
GSM8K = (ROOT / "data/tasks/gsm8k_test.jsonl").exists() and (ROOT / "data/tasks/split.json").exists()
needs_gsm8k = pytest.mark.skipif(not GSM8K, reason="GSM8K working set not downloaded")


def h3(tmp_path, *extra):
    cmd = [sys.executable, "scripts/run_real_h3.py", "--backend", "fake", "--split", "dev",
           "--plans", "all_subsets", "--cache", str(tmp_path / "c.sqlite"), *extra]
    return subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True).stdout


def test_all_subsets_is_every_assignment():
    plans = all_subset_plans(WF)
    assert len(plans) == 64 and {"all_small", "all_large", "only_verifier", "planner+verifier"} <= set(plans)
    for name in plans:
        assert plan_name(parse_plan_name(name, TOPO), TOPO) == name


def test_parse_plan_name_rejects_unknown_node():
    with pytest.raises(ValueError):
        parse_plan_name("planner+nope", TOPO)


@needs_gsm8k
def test_all_subsets_run_outputs_and_resume(tmp_path):
    out = tmp_path / "plans"
    args = ["--n-tasks", "4", "--output-dir", str(out)]
    assert "would run 64 plans" in h3(tmp_path, *args, "--dry-run")
    assert not out.exists()
    first = h3(tmp_path, *args, "--workers", "2")
    rows = read_csv(out / "h3_plans.csv")
    assert len(rows) == 64
    base = next(r for r in rows if r["plan"] == "all_small")
    assert float(base["gain_vs_small"]) == 0 and {"gain_ci_low", "gain_ci_high"} <= set(base)
    per = read_csv(out / "h3_per_problem.csv")
    assert len(per) == 64 * 4 and set(per[0]) == {"plan", "task_id", "correct"}
    calls = read_csv(out / "h3_calls.csv")
    assert len(calls) == 64 * 4 * 6
    assert {"plan", "model", "prompt_tokens", "completion_tokens", "latency_s"} <= set(calls[0])
    # Shared prefixes are generated once: far fewer requests than 64 * 6 per problem.
    assert sum(c["cache_hit"] == "False" for c in calls) <= (2 + 4 + 8 + 16 + 32 + 64) * 4
    trace = json.loads((out / "h3_traces.json").read_text())["all_small"][0]
    assert set(trace) == {"task_id", "gold", "correct", "keys"}  # format unchanged
    assert "already finished" in h3(tmp_path, *args)
    assert (out.parent / "plans_2").exists() is False
    h3(tmp_path, "--n-tasks", "3", "--output-dir", str(out))
    assert (out.parent / "plans_2" / "DONE").exists()  # another config never lands in the first directory
    assert first


def test_dominance_and_front():
    a = {"accuracy": .6, "cost": 1, "p95_latency": 1}
    b = {"accuracy": .5, "cost": 2, "p95_latency": 2}
    c = {"accuracy": .7, "cost": 3, "p95_latency": 1}
    assert dominates(a, b) and not dominates(a, c) and not dominates(a, a)
    assert pareto_front([a, b, c]) == [a, c]


def test_hypervolume_known_boxes():
    one = {"accuracy": .5, "cost": .5, "p95_latency": .5}
    assert hypervolume([one], 1, 1) == pytest.approx(.125)
    two = {"accuracy": .75, "cost": .75, "p95_latency": .5}
    # Union of boxes .5*.5*.5 and .75*.25*.5 minus their overlap .5*.25*.5.
    assert hypervolume([one, two], 1, 1) == pytest.approx(.125 + .09375 - .0625)
    assert hypervolume([one, two, {"accuracy": .4, "cost": .9, "p95_latency": .9}], 1, 1) >= hypervolume([one, two], 1, 1)
    assert hypervolume([], 1, 1) == 0


def test_hypervolume_order_free_and_adds_for_nondominated():
    rng = np.random.default_rng(0)
    pts = [{"accuracy": a, "cost": c, "p95_latency": l} for a, c, l in rng.random((12, 3))]
    v = hypervolume(pts, 1, 1)
    assert hypervolume(pts[::-1], 1, 1) == pytest.approx(v)
    assert hypervolume(pareto_front(pts), 1, 1) == pytest.approx(v)
    # Monte Carlo cross-check.
    u = rng.random((200000, 3))
    hit = np.zeros(len(u), bool)
    for p in pts:
        hit |= (u[:, 0] >= 1 - p["accuracy"]) & (u[:, 1] >= p["cost"]) & (u[:, 2] >= p["p95_latency"])
    assert hit.mean() == pytest.approx(v, abs=.005)


def calls_for(wf, lat):
    return [{"task_id": t, "node_id": n, "fidelity": tier, "latency_s": lat[tier]}
            for t in ("a", "b") for n in wf.nodes for tier in ("small", "large")]


def test_latency_is_longest_path_not_a_sum():
    wf = create_multihop_qa_workflow(3)  # planner -> 3 parallel researchers -> aggregator -> verifier
    m = LatencyModel(calls_for(wf, {"small": 1.0, "large": 3.0}), wf)
    assert m.p95(frozenset(), {"small": 1, "large": 1}) == pytest.approx(4.0)  # four nodes deep, six nodes wide
    assert m.p95(frozenset({"researcher_1"}), {"small": 1, "large": 1}) == pytest.approx(6.0)


def test_interference_is_directed_and_absent_when_unshared():
    m = LatencyModel(calls_for(WF, {"small": 1.0, "large": 1.0}), WF)
    betas = {"large_to_small": 2.4, "small_to_large": 1.0}
    assert m.factors(frozenset({"planner"}), None, 16) == {"small": 1.0, "large": 1.0}
    both = m.factors(frozenset({"planner", "step_1", "step_2"}), betas, 16)
    assert both["small"] > both["large"] > 1.0  # the large model hurts the small one more
    alone = m.factors(frozenset(), betas, 16)
    assert alone == {"small": pytest.approx(1.0), "large": pytest.approx(1.0)}


def pt(plan, placement, acc, cost, lat):
    return {"plan": plan_name(plan, TOPO), "plan_set": frozenset(plan), "placement": placement, "accuracy": acc,
            "cost": cost, "p95_latency": lat}


def test_two_step_commits_to_allocation_then_placement():
    pts = [pt([], "separate", .4, 1, 1), pt([], "shared", .4, .5, 2),
           pt(["planner"], "separate", .6, 2, 3), pt(["planner"], "shared", .6, 1, 4),
           pt(["verifier"], "separate", .5, 1, 1), pt(["verifier"], "shared", .5, .4, 1.1)]
    chosen = two_step(pts, 1)
    assert [(p["plan"], p["placement"]) for p in chosen] == [("all_small", "separate"), ("only_planner", "separate")]
    best = {r["placement"]: r["plan"] for r in constrained_best(pts, 2.5)}
    assert best["separate"] == "only_verifier" and best["shared"] == "only_verifier" and best["shared_mps"] == ""


def test_routing_rules():
    assert key_entropy(["1", "1"]) == 0 and key_entropy(["1", "2"]) == pytest.approx(1.0)
    assert key_entropy([None, "1"]) == pytest.approx(1.0)
    assert disagree_each_other(["1", "2"], "1") and not disagree_each_other(["1", "1"], "1")
    assert disagree_with_majority(["2", "2", "1"], "1") and not disagree_with_majority(["1", "1", "2"], "1")


def _route_row(keys, base_key, q_base, q_plus):
    tok = {f"{p}_{t}_{k}": 0.0 for p in ("base", "plus", "samples") for t in ("small", "large") for k in ("in", "out")}
    tok.update(base_small_out=1e6, plus_large_out=1e6, samples_small_out=2e5)
    return {"sample_keys": json.dumps(keys), "base_key": base_key, "baseline_correct": q_base, "q_plus": q_plus, **tok}


def test_routing_accuracy_and_cost_use_the_right_side():
    prices = load_prices()
    rows = [_route_row(["1", "2"], "1", 0, 1), _route_row(["1", "1"], "1", 1, 1)]
    res = evaluate(rows, disagree_each_other, prices)
    assert res["routed_share"] == .5 and res["accuracy"] == 1.0
    # routed: large 10.00 + samples 0.10; not routed: small 0.50 + samples 0.10
    assert res["cost"] == pytest.approx((10.0 + .1 + .5 + .1) / 2)


def test_adaptive_stops_early_when_one_plan_is_clearly_best():
    rows = []
    for t in range(400):
        rows += [{"plan": "good", "task_id": t, "correct": 1.0}, {"plan": "bad", "task_id": t, "correct": float(t % 4 == 0)}]
    res = adaptive_run(rows, 25, 20, 400, 0)
    assert res["best_plan"] == "good" and res["share_within_2_points"] == 1
    assert res["mean_problems_used"] <= 50 and res["share_at_most_half"] == 1


def test_adaptive_uses_everything_when_plans_tie():
    rows = []
    for t in range(100):
        rows += [{"plan": "a", "task_id": t, "correct": 1.0}, {"plan": "b", "task_id": t, "correct": 1.0}]
    assert adaptive_run(rows, 25, 5, 400, 0)["mean_problems_used"] == 100


def _wait_for(check, seconds=10.0):
    end = time.time() + seconds
    while time.time() < end and not check():
        time.sleep(.05)
    return check()


def test_power_logger_writes_and_reports_problems(tmp_path):
    stub = tmp_path / "smi"
    stub.write_text("#!/bin/sh\necho 'timestamp, power.draw [W], utilization.gpu [%], memory.used [MiB]'\nsleep 30\n")
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
    log = PowerLoggers(["gpu_a=local"], tmp_path, smi=[str(stub)])
    assert _wait_for(lambda: "power.draw" in (tmp_path / "power_gpu_a.csv").read_text())
    log.stop()
    assert not log.problems
    missing = PowerLoggers(["gpu_b=local"], tmp_path, smi=[str(tmp_path / "does-not-exist")])
    missing.stop()
    assert missing.problems and "gpu_b" in missing.problems[0]
    dead = PowerLoggers(["gpu_c=local"], tmp_path, smi=["false"])
    assert _wait_for(lambda: dead.procs["gpu_c"][0].poll() is not None)
    dead.stop()
    assert dead.problems and "exited early" in dead.problems[0]


@needs_gsm8k
def test_run_placement_outputs_and_resume(tmp_path):
    out = tmp_path / "p"
    cmd = [sys.executable, "scripts/v2/run_placement.py", "--backend", "fake", "--placement", "shared",
           "--plans", "all_small,only_verifier", "--n-tasks", "3", "--k", "2", "--repeats", "2",
           "--split", "eval", "--output-dir", str(out)]
    subprocess.run(cmd + ["--dry-run"], cwd=ROOT, check=True)
    assert not out.exists()
    subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True)
    rows = read_csv(out / "placement_summary.csv")
    assert len(rows) == 4 and {"p50_s", "p95_s", "p99_s", "throughput_per_s"} <= set(rows[0])
    assert (out / "placement_calls.csv").exists()
    # A killed run resumes: the finished files are not redone.
    (out / "DONE").unlink()
    (out / "run_only_verifier_r1.csv").unlink()
    res = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True).stdout
    assert res.count("skip ") == 3 and (out / "run_only_verifier_r1.csv").exists()
