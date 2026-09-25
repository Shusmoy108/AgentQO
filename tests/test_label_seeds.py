"""Different workflows must not share task instances (LOWO leakage guard)."""

from agentqo.experiments.suite import default_suite
from agentqo.labeling.ec_labeler import ECLabeler
from agentqo.simulator.task_model import MockBackend


def test_workflows_labeled_with_same_base_seed_get_distinct_tasks():
    task_ids = []
    for member in default_suite(quick=True)[:2]:
        backend = MockBackend(member.task_model, embedding_dim=64)
        result = ECLabeler(backend, member.task_model).label_workflow(
            member.workflow, num_tasks=4, base_seed=42, show_progress=False,
        )
        task_ids.append({o.task_id.split("_", 1)[1] for o in result.observations})
    assert not task_ids[0] & task_ids[1]
