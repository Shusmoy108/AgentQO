"""WP0.2: the runtime's predicted EC never comes from a predictor that saw the workflow."""

import csv

import pytest

from scripts.run_agentqo import label_suite, run_agentqo_experiment, runtime_workflows, train_runtime_predictor
from agentqo.predictors.features import FeatureExtractor


def test_predictor_never_trains_on_runtime_workflow():
    labeling, workflows = label_suite(n_tasks=3, seed=0, quick=True)
    runtime_names = {wf.name for wf in runtime_workflows()}
    # The math runtime workflow is also in the suite: it must be held out.
    assert runtime_names & set(workflows)
    for name in runtime_names:
        _, trained_on = train_runtime_predictor(labeling, workflows, name, FeatureExtractor(64), 0)
        assert name not in trained_on
        assert trained_on


def test_runtime_csv_has_ec_source(tmp_path):
    run_agentqo_experiment(n_jobs=2, output_dir=str(tmp_path), ec_source="predicted",
                           n_seeds=2, loads=("high",), n_label_tasks=3)
    with open(tmp_path / "agentqo_runtime.csv") as fh:
        rows = list(csv.DictReader(fh))
    assert rows and all(r["ec_source"] == "predicted" for r in rows)
    assert {r["seed"] for r in rows} == {"42", "1042"}
