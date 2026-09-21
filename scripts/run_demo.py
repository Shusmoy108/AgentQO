#!/usr/bin/env python3
"""Run H1 → H2 → H3 (and H4 simulator) with a single seed and shared labels."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentqo.experiments.suite import default_suite
from agentqo.metrics.io import write_json
from agentqo.metrics.report import generate_full_report
from scripts.run_h1_labeling import run_h1_experiment
from scripts.run_h2_predictor import run_h2_experiment
from scripts.run_h3_allocation import run_h3_experiment
from scripts.run_h4_agenticonq import run_h4_experiment


def run_full_demo(
    num_tasks: int = 40,
    num_runs: int = 20,
    embedding_dim: int = 256,
    output_dir: str = "data/demo",
    base_seed: int = 42,
    quick_mode: bool = False,
) -> dict:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    if quick_mode:
        num_tasks = min(num_tasks, 16)
        num_runs = min(num_runs, 8)

    suite = default_suite(quick=True if quick_mode else False)

    print("=" * 70)
    print("AgentQO PROTOTYPE  (H1 → H2 → H3, H4 simulator)")
    print("=" * 70)

    labeling = run_h1_experiment(
        num_tasks=num_tasks,
        embedding_dim=embedding_dim,
        output_dir=str(output_path / "h1"),
        base_seed=base_seed,
        use_db=True,
        suite=suite,
    )
    h2 = run_h2_experiment(
        num_tasks=num_tasks,
        embedding_dim=embedding_dim,
        output_dir=str(output_path / "h2"),
        base_seed=base_seed,
        suite=suite,
        labeling_results=labeling,
    )
    h3 = run_h3_experiment(
        num_runs_per_budget=num_runs,
        embedding_dim=embedding_dim,
        output_dir=str(output_path / "h3"),
        base_seed=base_seed,
        suite=suite,
        h2_artifacts=h2,
    )
    h4 = run_h4_experiment(
        n_batches=200 if quick_mode else 500,
        output_dir=str(output_path / "h4"),
        seed=base_seed,
    )

    h1_any = any(
        # smoke + range already baked into files; recompute cheaply from labels
        True for _ in labeling
    )
    # Use written H1 json for the official gate.
    import json
    h1_payload = json.loads((output_path / "h1" / "h1_results.json").read_text())
    h1_holds = h1_payload["h1_holds_any"]
    h2_holds = bool(h2.analysis.get("h2_holds"))
    h3_holds = bool(h3.get("h3_holds_any"))
    h4_holds = bool(h4.get("h4_holds"))

    print()
    print(f"{'Hypothesis':<44} {'Result'}")
    print("-" * 60)
    print(f"{'H1  EC varies across nodes':<44} {'PASS' if h1_holds else 'FAIL'}")
    print(f"{'H2  EC predicted on unseen workflows':<44} {'PASS' if h2_holds else 'FAIL'}")
    print(f"{'H3  predicted-EC allocation wins':<44} {'PASS' if h3_holds else 'FAIL'}")
    print(f"{'H4  two-sided cost (simulator)':<44} {'PASS' if h4_holds else 'FAIL'}")

    first_h1 = next(iter(h1_payload["analyses"].values()))
    generate_full_report(first_h1, h2.analysis, next(iter(h3["analyses"].values()), {"h3_holds": h3_holds}), output_path)

    combined = {
        "h1_holds": h1_holds,
        "h2_holds": h2_holds,
        "h3_holds": h3_holds,
        "h4_holds": h4_holds,
        "all_pass": h1_holds and h2_holds and h3_holds,
        "config": {
            "num_tasks": num_tasks,
            "num_runs": num_runs,
            "embedding_dim": embedding_dim,
            "base_seed": base_seed,
            "quick_mode": quick_mode,
        },
    }
    write_json(output_path / "demo_results.json", combined)
    print(f"\nArtifacts: {output_path}")
    return combined


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AgentQO H1–H4 demo")
    parser.add_argument("--num-tasks", type=int, default=40)
    parser.add_argument("--num-runs", type=int, default=20)
    parser.add_argument("--embedding-dim", type=int, default=256)
    parser.add_argument("--output-dir", type=str, default="data/demo")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    results = run_full_demo(
        num_tasks=args.num_tasks,
        num_runs=args.num_runs,
        embedding_dim=args.embedding_dim,
        output_dir=args.output_dir,
        base_seed=args.seed,
        quick_mode=args.quick,
    )
    sys.exit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
