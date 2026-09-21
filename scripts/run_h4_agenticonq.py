#!/usr/bin/env python3
"""H4: Two-sided interaction cost (AgentIconq) on a multi-GPU simulator.

This is the methodology check before real vLLM traces. Success: beat
single-call and naive-additive baselines, and recover both signs of
interaction (contention > 0, prefix reuse < 0).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentqo.metrics.figures import save_h4_interaction_figure
from agentqo.metrics.io import write_csv, write_json
from agentqo.predictors.agenticonq import (
    AdditiveBaseline,
    AgentIconqPredictor,
    SingleCallBaseline,
    analyze_h4_results,
)
from agentqo.simulator.interaction_model import generate_interaction_dataset


def run_h4_experiment(
    n_batches: int = 500,
    output_dir: str = "data/h4",
    seed: int = 42,
) -> dict:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("H4 EXPERIMENT: AgentIconq two-sided cost (simulator)")
    print("=" * 60)

    X, Y, outcomes = generate_interaction_dataset(
        n_batches=n_batches, n_gpus=2, seed=seed
    )
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(X))
    cut = int(0.7 * len(perm))
    train, test = perm[:cut], perm[cut:]
    X_tr, Y_tr = X[train], Y[train]
    X_te, Y_te = X[test], Y[test]

    models = [
        AgentIconqPredictor(random_state=seed),
        SingleCallBaseline(),
        AdditiveBaseline(),
    ]
    results = {}
    for model in models:
        model.fit(X_tr, Y_tr)
        results[model.name] = model.evaluate(X_te, Y_te)

    analysis = analyze_h4_results(results)
    print(f"\n{'Model':<18} {'Own MAE':>10} {'Own Q':>10} {'Imp MAE':>10} {'Sign':>8}")
    print("-" * 60)
    for name, m in results.items():
        print(f"{name:<18} {m.own_mae:>10.3f} {m.own_qerr:>10.3f} "
              f"{m.imposed_mae:>10.3f} {m.sign_accuracy:>8.3f}")
    print(f"\nH4 HOLDS: {'YES' if analysis['h4_holds'] else 'NO'}")

    contention = [o.imposed_on_others for o in outcomes if not o.shared_prefix]
    reuse = [o.imposed_on_others for o in outcomes if o.shared_prefix]
    save_h4_interaction_figure(contention, reuse, output_path / "h4_interaction.png")
    write_csv(output_path / "h4_metrics.csv", [
        {"model": name, **m.to_dict()} for name, m in results.items()
    ])
    write_json(output_path / "h4_results.json", analysis)
    print(f"Artifacts written to {output_path}")
    return analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Run H4: AgentIconq")
    parser.add_argument("--n-batches", type=int, default=500)
    parser.add_argument("--output-dir", type=str, default="data/h4")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    analysis = run_h4_experiment(
        n_batches=args.n_batches,
        output_dir=args.output_dir,
        seed=args.seed,
    )
    sys.exit(0 if analysis.get("h4_holds") else 1)


if __name__ == "__main__":
    main()
