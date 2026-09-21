"""H4 simulator: both signs of interaction, predictor beats naive baselines."""

import numpy as np

from agentqo.predictors.agenticonq import (
    AdditiveBaseline,
    AgentIconqPredictor,
    SingleCallBaseline,
    analyze_h4_results,
)
from agentqo.simulator.interaction_model import (
    CallSpec,
    generate_interaction_dataset,
    simulate_batch,
)


def test_contention_is_positive_without_shared_prefix():
    calls = [
        CallSpec("a", "llm-7b", gpu_id=0, prompt_tokens=128, decode_tokens=64, prefix_id="p1"),
        CallSpec("b", "llm-7b", gpu_id=0, prompt_tokens=128, decode_tokens=64, prefix_id="p2"),
    ]
    out = {o.call_id: o for o in simulate_batch(calls)}
    assert out["a"].imposed_on_others > 0
    assert out["a"].own_latency > out["a"].isolated_latency


def test_shared_prefix_can_reduce_imposed_latency():
    contend = simulate_batch([
        CallSpec("a", "llm-7b", 0, 256, 32, prefix_id="x"),
        CallSpec("b", "llm-7b", 0, 256, 32, prefix_id="y"),
    ])
    reuse = simulate_batch([
        CallSpec("a", "llm-7b", 0, 256, 32, prefix_id="same"),
        CallSpec("b", "llm-7b", 0, 256, 32, prefix_id="same"),
    ])
    assert reuse[0].imposed_on_others < contend[0].imposed_on_others
    assert reuse[0].shared_prefix is True


def test_cross_gpu_pairs_do_not_interact():
    calls = [
        CallSpec("a", "llm-7b", gpu_id=0, prompt_tokens=64, decode_tokens=16, prefix_id="p"),
        CallSpec("b", "llm-70b", gpu_id=1, prompt_tokens=64, decode_tokens=16, prefix_id="p"),
    ]
    out = simulate_batch(calls)
    assert out[0].n_colocated == 0
    assert out[1].n_colocated == 0
    assert out[0].imposed_on_others == 0


def test_agenticonq_beats_single_call_on_sim_data():
    X, Y, _ = generate_interaction_dataset(n_batches=180, seed=0)
    cut = int(0.7 * len(X))
    models = {
        "AgentIconq": AgentIconqPredictor(random_state=0),
        "Single-call": SingleCallBaseline(),
        "Naive-additive": AdditiveBaseline(),
    }
    results = {}
    for name, model in models.items():
        model.fit(X[:cut], Y[:cut])
        results[name] = model.evaluate(X[cut:], Y[cut:])
    analysis = analyze_h4_results(results)
    assert results["AgentIconq"].own_mae < results["Single-call"].own_mae
    assert analysis["captures_both_signs"] or results["AgentIconq"].sign_accuracy > 0.55
