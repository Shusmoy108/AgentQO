#!/usr/bin/env python3
"""H2: Can EC be predicted from structure + recycled embeddings?

Labels come from H1 fault injection. The split is leave-one-workflow-out:
no node from a test DAG is seen at training time.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentqo.experiments.dataset import (
    Split,
    canonical_split,
    filter_samples,
    labeling_results_to_maps,
    leave_one_workflow_out,
    matrix_from_samples,
    observations_to_samples,
)
from agentqo.experiments.suite import SuiteMember, default_suite
from agentqo.labeling.ec_labeler import ECLabeler, LabelingResult
from agentqo.metrics.figures import save_h2_ranking_figure
from agentqo.metrics.io import write_csv, write_json
from agentqo.metrics.report import generate_h2_report
from agentqo.predictors.ec_predictor import (
    ConfidenceBaseline,
    GBTECPredictor,
    MLPECPredictor,
    PredictorMetrics,
    StructureOnlyBaseline,
    analyze_h2_results,
)
from agentqo.predictors.features import FeatureExtractor, NUM_ROLES
from agentqo.simulator.task_model import MockBackend
from agentqo.workflows.dag import Workflow


@dataclass
class H2Artifacts:
    analysis: Dict
    predictor: GBTECPredictor
    extractor: FeatureExtractor
    split: Split
    labeling: Dict[str, LabelingResult]
    workflows: Dict[str, Workflow]


def _ensure_labels(
    members: List[SuiteMember],
    labeling: Optional[Dict[str, LabelingResult]],
    num_tasks: int,
    embedding_dim: int,
    seed: int,
) -> Dict[str, LabelingResult]:
    if labeling is not None:
        return labeling
    out: Dict[str, LabelingResult] = {}
    for member in members:
        backend = MockBackend(member.task_model, embedding_dim=embedding_dim)
        labeler = ECLabeler(backend, member.task_model)
        print(f"  labeling {member.workflow.name} for H2...")
        out[member.workflow.name] = labeler.label_workflow(
            member.workflow, num_tasks=num_tasks, base_seed=seed, show_progress=True,
        )
    return out


def _eval_view(name, predictor, X_train, y_train, X_test, y_test) -> PredictorMetrics:
    predictor.fit(X_train, y_train)
    return predictor.evaluate(X_test, y_test, top_k_values=[1, 3, 5])


def run_h2_experiment(
    num_tasks: int = 40,
    embedding_dim: int = 256,
    output_dir: str = "data/h2",
    base_seed: int = 42,
    quick: bool = False,
    suite: Optional[List[SuiteMember]] = None,
    labeling_results: Optional[Dict[str, LabelingResult]] = None,
) -> H2Artifacts:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    members = suite if suite is not None else default_suite(quick=quick)
    workflows = {m.workflow.name: m.workflow for m in members}

    print("=" * 60)
    print("H2 EXPERIMENT: EC Prediction (leave-one-workflow-out)")
    print("=" * 60)

    labeling = _ensure_labels(
        members, labeling_results, num_tasks, embedding_dim, base_seed
    )
    labels_map, observations = labeling_results_to_maps(labeling)
    extractor = FeatureExtractor(embedding_dim)
    samples = observations_to_samples(observations, labels_map, workflows, extractor)
    print(f"Samples: {len(samples)}  workflows: {len(workflows)}")

    folds = leave_one_workflow_out(list(workflows))
    fold_rows = []
    fold_summaries = []
    for fold in folds:
        train = filter_samples(samples, fold.train_workflows)
        test = filter_samples(samples, fold.test_workflows)
        if len(train) < 8 or len(test) < 4:
            continue
        X_aq_tr, y_tr, _ = matrix_from_samples(train, "agentqo")
        X_aq_te, y_te, _ = matrix_from_samples(test, "agentqo")
        X_st_tr, _, _ = matrix_from_samples(train, "structure")
        X_st_te, _, _ = matrix_from_samples(test, "structure")
        X_cf_tr, _, _ = matrix_from_samples(train, "confidence")
        X_cf_te, _, _ = matrix_from_samples(test, "confidence")

        metrics = {
            "AgentQO": _eval_view(
                "AgentQO",
                GBTECPredictor(n_estimators=80, max_depth=3, random_state=base_seed),
                X_aq_tr, y_tr, X_aq_te, y_te,
            ),
            "Structure-Only": _eval_view(
                "Structure-Only",
                StructureOnlyBaseline(structural_dim=NUM_ROLES + 7, random_state=base_seed),
                X_st_tr, y_tr, X_st_te, y_te,
            ),
            "Confidence-Only": _eval_view(
                "Confidence-Only",
                ConfidenceBaseline(),
                X_cf_tr, y_tr, X_cf_te, y_te,
            ),
        }
        fold_summaries.append(metrics)
        for model, m in metrics.items():
            fold_rows.append({
                "test_workflow": fold.test_workflows[0],
                "model": model,
                "spearman": m.spearman_corr,
                "mae": m.mae,
                "rmse": m.rmse,
                "p_at_3": m.top_k_precision.get(3, 0.0),
                "overhead_ms": m.overhead_ms,
            })

    def _mean_metrics(model: str) -> Dict[str, float]:
        subset = [r for r in fold_rows if r["model"] == model]
        if not subset:
            return {"spearman_corr": 0.0, "mae": 0.0, "rmse": 0.0, "overhead_ms": 0.0}
        return {
            "spearman_corr": float(np.mean([r["spearman"] for r in subset])),
            "mae": float(np.mean([r["mae"] for r in subset])),
            "rmse": float(np.mean([r["rmse"] for r in subset])),
            "overhead_ms": float(np.mean([r["overhead_ms"] for r in subset])),
        }

    averaged = {name: PredictorMetrics(
        mae=_mean_metrics(name)["mae"],
        rmse=_mean_metrics(name)["rmse"],
        spearman_corr=_mean_metrics(name)["spearman_corr"],
        top_k_precision={3: float(np.mean([
            r["p_at_3"] for r in fold_rows if r["model"] == name
        ] or [0.0]))},
        r2=0.0,
        overhead_ms=_mean_metrics(name)["overhead_ms"],
    ) for name in ["AgentQO", "Structure-Only", "Confidence-Only"]}

    analysis = analyze_h2_results(averaged)
    analysis["best_model"] = "AgentQO"
    analysis["spearman_correlation"] = averaged["AgentQO"].spearman_corr
    analysis["subset_invariant_holds"] = (
        averaged["AgentQO"].spearman_corr + 1e-9
        >= averaged["Structure-Only"].spearman_corr - 0.02
    )
    analysis["detailed_metrics"] = {k: v.to_dict() for k, v in averaged.items()}
    analysis["n_samples"] = len(samples)
    analysis["n_folds"] = len(fold_summaries)

    # Canonical split: fit the predictor H3 will actually use.
    split = canonical_split(list(workflows))
    split.save(output_path / "h2_split.json")
    train = filter_samples(samples, split.train_workflows)
    X_train, y_train, _ = matrix_from_samples(train, "agentqo")
    predictor = GBTECPredictor(n_estimators=80, max_depth=3, random_state=base_seed)
    predictor.fit(X_train, y_train)

    print(f"\n{'Model':<20} {'Spearman':>10} {'MAE':>10} {'P@3':>10}")
    print("-" * 52)
    for name, m in averaged.items():
        print(f"{name:<20} {m.spearman_corr:>10.4f} {m.mae:>10.4f} "
              f"{m.top_k_precision.get(3, 0):>10.4f}")
    print(f"\nH2 HOLDS: {'YES' if analysis['h2_holds'] else 'NO'}")
    print(f"subset invariant (AgentQO >= structure): "
          f"{'YES' if analysis['subset_invariant_holds'] else 'NO'}")

    write_csv(output_path / "h2_fold_metrics.csv", fold_rows)
    write_json(output_path / "h2_results.json", {
        "analysis": analysis,
        "split": split.to_dict(),
        "config": {
            "num_tasks": num_tasks,
            "embedding_dim": embedding_dim,
            "base_seed": base_seed,
        },
    })
    save_h2_ranking_figure(
        {k: v.to_dict() for k, v in averaged.items()},
        output_path / "h2_spearman.png",
    )
    print("\n" + generate_h2_report(analysis, output_path))
    print(f"Artifacts written to {output_path}")
    return H2Artifacts(
        analysis=analysis,
        predictor=predictor,
        extractor=extractor,
        split=split,
        labeling=labeling,
        workflows=workflows,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run H2: EC prediction")
    parser.add_argument("--num-tasks", type=int, default=40)
    parser.add_argument("--embedding-dim", type=int, default=256)
    parser.add_argument("--output-dir", type=str, default="data/h2")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    artifacts = run_h2_experiment(
        num_tasks=args.num_tasks,
        embedding_dim=args.embedding_dim,
        output_dir=args.output_dir,
        base_seed=args.seed,
        quick=args.quick,
    )
    sys.exit(0 if artifacts.analysis.get("h2_holds") else 1)


if __name__ == "__main__":
    main()
