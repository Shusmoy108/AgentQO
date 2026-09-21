#!/usr/bin/env python3
"""H1: Does downstream importance vary across nodes?

Labels are measured by fault injection. Hidden simulator importance is
never used as a stand-in for EC.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentqo.database import AgentQODatabase
from agentqo.experiments.suite import SuiteMember, default_suite
from agentqo.labeling.ec_labeler import (
    ECLabeler,
    LabelingResult,
    analyze_h1_results,
)
from agentqo.metrics.figures import save_h1_histogram
from agentqo.metrics.io import write_csv, write_json
from agentqo.metrics.report import generate_h1_report
from agentqo.simulator.task_model import MockBackend


def run_h1_experiment(
    num_tasks: int = 80,
    embedding_dim: int = 256,
    output_dir: str = "data/h1",
    base_seed: int = 42,
    use_db: bool = True,
    quick: bool = False,
    suite: Optional[List[SuiteMember]] = None,
) -> Dict[str, LabelingResult]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    db = AgentQODatabase(output_path / "agentqo.db") if use_db else None
    members = suite if suite is not None else default_suite(quick=quick)

    print("=" * 60)
    print("H1 EXPERIMENT: Epistemic Criticality Labeling")
    print("=" * 60)
    print(f"Tasks per workflow: {num_tasks}")
    print(f"Workflows: {len(members)}")
    print()

    results: Dict[str, LabelingResult] = {}
    analyses = {}
    csv_rows = []

    for member in members:
        workflow, task_model = member.workflow, member.task_model
        print(f"\n--- {member.display_name} ({workflow.name}) ---")
        backend = MockBackend(task_model, embedding_dim=embedding_dim)
        labeler = ECLabeler(backend, task_model, db)
        labeled = labeler.label_workflow(
            workflow=workflow,
            num_tasks=num_tasks,
            base_seed=base_seed,
            show_progress=True,
        )
        analysis = analyze_h1_results(labeled.labels, workflow)
        results[workflow.name] = labeled
        analyses[workflow.name] = analysis

        print(f"  H1 holds: {'YES' if analysis['h1_holds'] else 'NO'}")
        print(f"  range={analysis['statistics']['range']:.4f}  "
              f"cv={analysis['statistics']['cv']:.4f}")
        print(f"  high: {analysis['high_criticality_nodes']}")
        print(f"  low:  {analysis['low_criticality_nodes']}")
        smoke = analysis.get("smoke_test", {})
        print(f"  smoke test: {'PASS' if smoke.get('passed') else 'FAIL'} "
              f"{smoke.get('notes', '')}")

        save_h1_histogram(
            labeled.labels,
            output_path / f"h1_{workflow.name}.png",
            title=f"H1: {member.display_name}",
        )
        for nid, lab in labeled.labels.items():
            row = lab.to_dict()
            row["workflow_display"] = member.display_name
            csv_rows.append(row)

    write_csv(output_path / "h1_ec_labels.csv", csv_rows)
    overall = {
        "h1_holds_all": all(a["h1_holds"] for a in analyses.values()),
        "h1_holds_any": any(a["h1_holds"] for a in analyses.values()),
        "analyses": {
            k: {kk: vv for kk, vv in v.items() if kk != "node_ranking"}
            for k, v in analyses.items()
        },
        "config": {
            "num_tasks": num_tasks,
            "embedding_dim": embedding_dim,
            "base_seed": base_seed,
            "workflows": [m.workflow.name for m in members],
        },
    }
    write_json(output_path / "h1_results.json", overall)

    first = next(iter(analyses.values()))
    print("\n" + generate_h1_report(first, output_path))
    print(f"Artifacts written to {output_path}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run H1: EC labeling")
    parser.add_argument("--num-tasks", type=int, default=80)
    parser.add_argument("--embedding-dim", type=int, default=256)
    parser.add_argument("--output-dir", type=str, default="data/h1")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-db", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    results = run_h1_experiment(
        num_tasks=args.num_tasks,
        embedding_dim=args.embedding_dim,
        output_dir=args.output_dir,
        base_seed=args.seed,
        use_db=not args.no_db,
        quick=args.quick,
    )
    holds = any(
        analyze_h1_results(r.labels, m.workflow)["h1_holds"]
        for r, m in zip(
            results.values(),
            default_suite(quick=args.quick),
        )
    )
    # Recompute from saved analyses is simpler:
    import json
    payload = json.loads(Path(args.output_dir, "h1_results.json").read_text())
    if payload["h1_holds_any"]:
        print("\nH1 supported — proceed to H2")
        sys.exit(0)
    print("\nH1 not supported — stop the EC direction")
    sys.exit(1)


if __name__ == "__main__":
    main()
