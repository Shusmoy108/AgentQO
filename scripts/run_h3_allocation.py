#!/usr/bin/env python3
"""H3: Does spending by *predicted* EC beat confidence and uniform?

AgentQO scores come from the H2 predictor, never from hidden importance
and never from oracle labels (oracle is reported only as an upper bound).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentqo.experiments.scoring import mean_confidence, predict_node_scores
from agentqo.experiments.suite import SuiteMember, default_suite
from agentqo.labeling.ec_labeler import LabelingResult, compute_bootstrap_ci
from agentqo.metrics.figures import save_h3_quality_cost_figure
from agentqo.metrics.io import append_results_entry, write_csv, write_json
from agentqo.metrics.report import generate_h3_report
from agentqo.policies.allocation import (
    analyze_h3_results,
    bootstrap_auc,
    compute_quality_cost_curve,
    h3_bottleneck,
)
from agentqo.predictors.ec_predictor import GBTECPredictor
from agentqo.predictors.features import FeatureExtractor
from agentqo.simulator.task_model import MockBackend
from scripts.run_h2_predictor import H2Artifacts, run_h2_experiment


def run_h3_experiment(
    num_runs_per_budget: int = 30,
    embedding_dim: int = 256,
    output_dir: str = "data/h3",
    base_seed: int = 42,
    quick: bool = False,
    suite: Optional[List[SuiteMember]] = None,
    h2_artifacts: Optional[H2Artifacts] = None,
    num_label_tasks: int = 30,
    include_oracle: bool = True,
    record_results: bool = False,
    backend_factory=None,
) -> Dict:
    """``backend_factory(task_model)`` builds the backend; default MockBackend."""
    if backend_factory is None:
        backend_factory = lambda tm: MockBackend(tm, embedding_dim=embedding_dim)  # noqa: E731
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    members = suite if suite is not None else default_suite(quick=quick)

    print("=" * 60)
    print("H3 EXPERIMENT: Value-Aware Allocation (predicted EC)")
    print("=" * 60)

    if h2_artifacts is None:
        print("Training EC predictor (H2) for allocation scores...")
        h2_artifacts = run_h2_experiment(
            num_tasks=num_label_tasks,
            embedding_dim=embedding_dim,
            output_dir=str(output_path / "h2_for_h3"),
            base_seed=base_seed,
            quick=quick,
            suite=members,
        )

    predictor: GBTECPredictor = h2_artifacts.predictor
    extractor: FeatureExtractor = h2_artifacts.extractor
    labeling: Dict[str, LabelingResult] = h2_artifacts.labeling
    test_names = set(h2_artifacts.split.test_workflows)
    # Evaluate allocation on held-out workflows; if a fold is tiny, use all.
    eval_members = [m for m in members if m.workflow.name in test_names] or members

    all_analyses = {}
    csv_rows = []
    last_curves = None

    for member in eval_members:
        workflow, task_model = member.workflow, member.task_model
        print(f"\n--- {member.display_name} ---")
        backend = backend_factory(task_model)

        predicted = predict_node_scores(
            workflow, task_model, backend, predictor, extractor,
            n_probes=8, view="agentqo", seed=base_seed + 7,
        )
        confidence = mean_confidence(
            workflow, task_model, backend, n_probes=8, seed=base_seed + 11,
        )
        oracle = {
            nid: lab.ec_score
            for nid, lab in labeling[workflow.name].labels.items()
        } if include_oracle and workflow.name in labeling else None

        print("  predicted EC:", {k: round(v, 4) for k, v in predicted.items()})
        raw: Dict = {}
        curves = compute_quality_cost_curve(
            workflow=workflow,
            task_model=task_model,
            backend=backend,
            ec_scores=predicted,
            confidence_scores=confidence,
            oracle_ec_scores=oracle,
            budget_fractions=[0.5, 0.8, 1.0, 1.3, 1.6, 2.0, 2.5, 3.0],
            num_runs=num_runs_per_budget,
            base_seed=base_seed,
            raw_out=raw,
        )
        last_curves = curves
        analysis = analyze_h3_results(curves)
        boot = bootstrap_auc(raw, seed=base_seed)
        analysis["bootstrap"] = boot
        analysis["bottleneck"] = h3_bottleneck(boot)
        all_analyses[workflow.name] = analysis
        print(f"  H3 holds: {'YES' if analysis['h3_holds'] else 'NO'}")
        print(f"  beats confidence {analysis['beats_confidence_fraction']*100:.0f}%  "
              f"uniform {analysis['beats_uniform_fraction']*100:.0f}%")
        for name, d in boot["auc"].items():
            print(f"  AUC {name:<11} {d['auc']:.3f}  [{d['ci'][0]:.3f}, {d['ci'][1]:.3f}]")
        for name, d in boot["diff"].items():
            print(f"  {name:<24} {d['diff']:+.3f}  [{d['ci'][0]:+.3f}, {d['ci'][1]:+.3f}]")
        print(f"  bottleneck: {analysis['bottleneck']}")
        save_h3_quality_cost_figure(
            curves, output_path / f"h3_quality_cost_{workflow.name}.png",
            raw=raw, title=f"H3: {member.display_name}",
        )
        for policy, points in raw.items():
            for cost, qualities in points:
                lo, hi = compute_bootstrap_ci(qualities, rng=np.random.default_rng(base_seed))
                csv_rows.append({
                    "workflow": workflow.name,
                    "policy": policy,
                    "cost": cost,
                    "quality": float(qualities.mean()),
                    "ci_low": lo,
                    "ci_high": hi,
                    "n": len(qualities),
                })

    write_csv(output_path / "h3_quality_cost.csv", csv_rows)
    if last_curves:
        save_h3_quality_cost_figure(last_curves, output_path / "h3_quality_cost.png")

    overall = {
        "h3_holds_all": all(a["h3_holds"] for a in all_analyses.values()),
        "h3_holds_any": any(a["h3_holds"] for a in all_analyses.values()),
        "analyses": {
            k: {kk: vv for kk, vv in v.items() if kk not in {"curves", "point_comparisons"}}
            for k, v in all_analyses.items()
        },
    }
    write_json(output_path / "h3_results.json", overall)
    if record_results and all_analyses:
        lines = []
        for wf, a in all_analyses.items():
            d = a["bootstrap"]["diff"]
            parts = [f"{k} {v['diff']:+.3f} [{v['ci'][0]:+.3f}, {v['ci'][1]:+.3f}]"
                     for k, v in d.items()]
            lines.append(f"{wf}: " + "; ".join(parts) + f"; bottleneck = {a['bottleneck']}")
        append_results_entry(
            "S-H3",
            {"num_runs": num_runs_per_budget, "quick": quick, "seed": base_seed,
             "oracle": include_oracle, "label_tasks": num_label_tasks},
            "H3 holds on " + str(sum(a["h3_holds"] for a in all_analyses.values()))
            + f"/{len(all_analyses)} held-out workflows. AUC diffs (95% paired bootstrap CI): "
            + " | ".join(lines),
            str(output_path / "h3_quality_cost_<workflow>.png"),
            "Bottleneck per workflow as listed. 'predictor' means oracle EC wins but "
            "predicted EC does not, so improve H2 before touching the allocator; "
            "'allocator' means even oracle EC loses, so check fidelity gap and budget granularity.",
        )
    if all_analyses:
        print("\n" + generate_h3_report(next(iter(all_analyses.values())), output_path))
    print(f"Artifacts written to {output_path}")
    return overall


def main() -> None:
    parser = argparse.ArgumentParser(description="Run H3: value-aware allocation")
    parser.add_argument("--num-runs", type=int, default=30)
    parser.add_argument("--embedding-dim", type=int, default=256)
    parser.add_argument("--output-dir", type=str, default="data/h3")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--oracle", action=argparse.BooleanOptionalAction, default=True,
                        help="report oracle-EC allocation as an upper bound")
    parser.add_argument("--label-tasks", type=int, default=30)
    args = parser.parse_args()
    results = run_h3_experiment(
        num_runs_per_budget=args.num_runs,
        embedding_dim=args.embedding_dim,
        output_dir=args.output_dir,
        base_seed=args.seed,
        quick=args.quick,
        num_label_tasks=args.label_tasks,
        include_oracle=args.oracle,
        record_results=True,
    )
    sys.exit(0 if results["h3_holds_any"] else 1)


if __name__ == "__main__":
    main()
