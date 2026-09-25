"""WP1: predictors, policies, and the runtime never read simulator internals.

``node_importance`` / ``node_difficulties`` may be read only by the simulator
itself (which defines the quality channel) and by DB persistence. A
class-level property shadows the instance fields and raises on any other
caller.
"""

import sys

import numpy as np
import pytest

from agentqo.simulator.task_model import TaskInstance

ALLOWED = ("agentqo.simulator.", "agentqo.database")


def _guard(field):
    def get(self):
        caller = sys._getframe(1).f_globals.get("__name__", "")
        if not caller.startswith(ALLOWED):
            raise AssertionError(f"{caller} read TaskInstance.{field}")
        return self.__dict__[field]

    def set_(self, value):
        self.__dict__[field] = value

    return property(get, set_)


@pytest.fixture
def guarded(monkeypatch):
    for field in ("node_importance", "node_difficulties"):
        monkeypatch.setattr(TaskInstance, field, _guard(field), raising=False)


def test_guard_catches_outside_reader(guarded):
    task = TaskInstance("t", "x", 0.5, {"a": 0.1}, {"a": 0.2}, 0)
    with pytest.raises(AssertionError):
        _ = task.node_importance


def test_predictor_fit_h3_and_runtime_do_not_leak(guarded, tmp_path):
    from scripts.run_agentqo import run_agentqo_experiment
    from scripts.run_h3_allocation import run_h3_experiment
    from agentqo.experiments.suite import default_suite

    suite = default_suite(quick=True)
    # H1 labeling + H2 predictor fit + H3 allocation with predicted EC.
    run_h3_experiment(num_runs_per_budget=2, embedding_dim=64, output_dir=str(tmp_path / "h3"),
                      quick=True, suite=suite, num_label_tasks=3)
    # Runtime episode fed by the predictor.
    run_agentqo_experiment(n_jobs=2, output_dir=str(tmp_path / "rt"), ec_source="predicted",
                           n_label_tasks=3, loads=("high",))
