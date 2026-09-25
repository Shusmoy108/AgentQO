"""WP1: answer extraction on real output styles, and RealTaskModel quality."""

import numpy as np
import pytest

from agentqo.backends.base import NodeResult
from agentqo.tasks.answers import extract_gsm8k_number, f1, gsm8k_gold, normalize_answer
from agentqo.tasks.real_task_model import RealTaskModel
from agentqo.workflows.library import create_math_reasoning_workflow

STYLES = [
    ("Natalia sold 48 + 24 = 72 clips.\n#### 72", "72"),
    ("#### 1,234", "1234"),
    ("The answer is $18.", "18"),
    ("So she makes $18.00 every day.\n#### $18.00", "18"),
    ("Total: 5 * 3 = 15. Then 15 - 2 = 13.", "13"),
    ("#### -7", "-7"),
    ("The temperature drops to -7 degrees.", "-7"),
    ("#### 3.5", "3.5"),
    ("RESULT: 42", "42"),
    ("VERDICT: correct\n#### 110", "110"),
    ("VERDICT: incorrect. The right total is 96.\n#### 96", "96"),
    ("Final answer: \\boxed{25}", "25"),
    ("Step 1: 10 apples. Step 2: 4 eaten.\nFinal answer: \\boxed{6}.", "6"),
    ("#### 5\nWait, recheck.\n#### 8", "8"),
    ("It costs $1,000,000 in total.", "1000000"),
    ("#### 12.", "12"),
    ("She has 0.25 of the pie left.", "0.25"),
    ("**Answer:** 64", "64"),
    ("PLAN:\n1. Add 3 and 4\n2. Multiply by 2", "2"),
]


@pytest.mark.parametrize("text,expected", STYLES)
def test_extract_styles(text, expected):
    assert extract_gsm8k_number(text) == expected


def test_extract_none():
    assert extract_gsm8k_number("I don't know.") is None
    assert extract_gsm8k_number("") is None


def test_gsm8k_gold_field():
    assert gsm8k_gold("48/2 = <<48/2=24>>24 clips\n#### 1,072") == "1072"


def test_f1_and_normalize():
    assert normalize_answer("The Eiffel Tower!") == "eiffel tower"
    assert f1("Eiffel Tower", "the eiffel tower") == 1.0
    assert f1("Paris", "London") == 0.0


def _quality_of(text, gold, workflow, model):
    task = model.generate_task(workflow, np.random.default_rng(0))
    task.ground_truth = gold
    result = NodeResult("aggregator", {"text": text}, False, 0.5, np.zeros(4), 0.0, "small")
    return model.compute_quality(task, {"aggregator": result}, workflow)


def test_compute_quality_on_50_gold_strings():
    wf = create_math_reasoning_workflow(3, include_verifier=False)
    golds = [str(g) for g in np.random.default_rng(0).integers(-50, 100_000, size=50)]
    model = RealTaskModel([{"qid": "q", "question": "?", "gold": "0"}])
    assert all(_quality_of(f"work...\n#### {int(g):,}", g, wf, model) == 1.0 for g in golds)
    assert all(_quality_of(f"#### {int(g) + 1}", g, wf, model) == 0.0 for g in golds)


def test_compute_quality_on_real_gsm8k_answers():
    datasets = pytest.importorskip("agentqo.tasks.datasets")
    try:
        problems = datasets._gsm8k_rows("test", datasets.TASK_DIR)[:50]
    except OSError:
        pytest.skip("GSM8K not cached and offline")
    wf = create_math_reasoning_workflow(3, include_verifier=False)
    model = RealTaskModel([{"qid": "q", "question": "?", "gold": "0"}])
    assert all(_quality_of(r["answer"], gsm8k_gold(r["answer"]), wf, model) == 1.0 for r in problems)


def test_answer_node_priority():
    wf = create_math_reasoning_workflow(3, include_verifier=True)
    model = RealTaskModel([{"qid": "q", "question": "?", "gold": "7"}])
    task = model.generate_task(wf, np.random.default_rng(0))
    agg = NodeResult("aggregator", {"text": "#### 7"}, False, 0.5, np.zeros(4), 0.0, "small")
    ver = NodeResult("verifier", {"text": "VERDICT: incorrect\n#### 8"}, True, 0.5, np.zeros(4), 0.0, "small")
    assert model.compute_quality(task, {"aggregator": agg}, wf) == 1.0
    # Verifier outranks aggregator, and correctness flags are ignored.
    assert model.compute_quality(task, {"aggregator": agg, "verifier": ver}, wf) == 0.0
