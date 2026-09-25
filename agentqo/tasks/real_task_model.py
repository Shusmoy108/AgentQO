"""TaskModel for real benchmark problems.

Quality is read from the answer node's *text* only. Correctness flags and
simulator internals (``node_importance``, ``node_difficulties``) are never
used: they are empty here.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

import numpy as np

from agentqo.backends.base import NodeResult
from agentqo.backends.vllm_http import _output_as_text
from agentqo.simulator.task_model import TaskInstance, TaskModel
from agentqo.tasks.answers import extract_gsm8k_number, f1

if TYPE_CHECKING:
    from agentqo.workflows.dag import Fidelity, NodeSpec, Workflow


def answer_node(workflow: "Workflow", node_results: Dict[str, NodeResult]) -> Optional[str]:
    """First executed node in ``workflow.answer_nodes``; else the last executed node."""
    for nid in workflow.answer_nodes:
        if nid in node_results:
            return nid
    executed = [nid for nid in workflow.topological_order if nid in node_results]
    return executed[-1] if executed else None


class RealTaskModel(TaskModel):
    """Serves problems from a fixed working set, in order (wraps around).

    ``generate_task`` ignores ``rng``: the working set, not a random draw,
    defines which problems are used. Call ``reset()`` to start over.
    """

    def __init__(self, problems: List[Dict[str, str]], dataset: str = "gsm8k") -> None:
        if not problems:
            raise ValueError("RealTaskModel needs at least one problem")
        if dataset not in ("gsm8k", "hotpotqa"):
            raise ValueError(f"unknown dataset {dataset}")
        self.problems = problems
        self.dataset = dataset
        self._cursor = 0

    def reset(self) -> None:
        self._cursor = 0

    def generate_task(self, workflow: "Workflow", rng: np.random.Generator) -> TaskInstance:
        p = self.problems[self._cursor % len(self.problems)]
        self._cursor += 1
        return TaskInstance(
            task_id=p["qid"],
            task_type=self.dataset,
            difficulty=0.0,
            node_difficulties={},
            node_importance={},
            ground_truth=p["gold"],
            metadata={"problem": p["question"], "dataset": self.dataset, "qid": p["qid"]},
        )

    def extract(self, text: str) -> Optional[str]:
        if self.dataset == "gsm8k":
            return extract_gsm8k_number(text)
        return text.strip() or None

    def score_text(self, text: str, gold: Any) -> float:
        pred = self.extract(text)
        if pred is None:
            return 0.0
        if self.dataset == "gsm8k":
            return float(pred == str(gold))
        return f1(pred, str(gold))

    def compute_quality(
        self,
        task: TaskInstance,
        node_results: Dict[str, NodeResult],
        workflow: "Workflow",
    ) -> float:
        nid = answer_node(workflow, node_results)
        if nid is None:
            return 0.0
        return self.score_text(_output_as_text(node_results[nid].output), task.ground_truth)

    def compute_node_error_prob(
        self,
        node: "NodeSpec",
        fidelity: "Fidelity",
        task: TaskInstance,
        input_results: Dict[str, NodeResult],
    ) -> float:
        raise NotImplementedError("only the simulator defines node error probabilities")
