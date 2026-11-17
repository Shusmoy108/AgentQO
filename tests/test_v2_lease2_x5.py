"""L2-X5 (MATH-500) code on branch v2-lease2-x: boxed extraction, scoring, prompts, loader."""

from __future__ import annotations

import json
from types import SimpleNamespace

from agentqo.tasks.answers import extract_boxed, math_equal, normalize_math
from agentqo.tasks.math500 import load_math500
from agentqo.tasks.prompts import build_prompt, math500_prompt
from agentqo.tasks.real_task_model import RealTaskModel
from scripts.run_real_pipeline import WORKFLOWS


def test_extract_boxed():
    assert extract_boxed(r"so \boxed{3} and finally \boxed{\frac{1}{2}}.") == r"\frac{1}{2}"
    assert extract_boxed(r"\boxed{\left( 3, \frac{\pi}{2} \right)}") == r"(3,\frac{\pi}{2})"
    assert extract_boxed("#### 42") is None          # no boxed answer -> unscorable
    assert extract_boxed(r"\boxed{\frac{1}{2}") is None  # unbalanced braces


def test_math_equal():
    assert math_equal(r"\dfrac{1}{2}", r"\frac12")
    assert math_equal("0.5", r"\frac{1}{2}")
    assert math_equal(r"-\frac{3}{4}", "-0.75")
    assert math_equal("x = 3", "3")
    assert math_equal(r"10\%", "10") and math_equal(r"90^\circ", "90")
    assert math_equal("1,000", "1000")
    assert math_equal(r"\text{Evelyn}", "Evelyn")
    assert math_equal(r"(3,\frac{\pi}{2})", r"\left( 3, \frac{\pi}{2} \right)")
    assert not math_equal("2", "3") and not math_equal(None, "3") and not math_equal(r"\frac{1}{0}", "1")
    assert normalize_math(r"  4\sqrt{2}. ") == r"4\sqrt{2}"


def test_task_model_math500():
    tm = RealTaskModel([{"qid": "math500-a", "question": "q", "gold": r"\frac{1}{2}"}], dataset="math500")
    assert tm.extract(r"Final: \boxed{\dfrac12}") == r"\frac{1}{2}"
    assert tm.score_text(r"\boxed{0.5}", r"\frac{1}{2}") == 1.0
    assert tm.score_text("#### 0.5", r"\frac{1}{2}") == 0.0  # GSM8K format is not scored for MATH-500


def test_math500_prompts():
    wf = WORKFLOWS["math"][1]()
    task = SimpleNamespace(metadata={"dataset": "math500", "problem": "Find x."}, task_id="t")
    ctx = {"workflow": wf, "results": {}, "task": task, "problem": "Find x."}
    agg = build_prompt(wf.nodes["aggregator"], {}, ctx)
    assert r"\boxed{<answer>}" in agg and "#### <number>" not in agg
    step = build_prompt(wf.nodes["step_1"], {}, ctx)
    assert "RESULT: <expression>" in step and "<number>" not in step
    gsm = build_prompt(wf.nodes["aggregator"], {}, {**ctx, "task": SimpleNamespace(metadata={"dataset": "gsm8k"})})
    assert "#### <number>" in gsm and r"\boxed" not in gsm          # GSM8K prompts unchanged
    assert "Final answer: <number>" not in math500_prompt("End with: Final answer: <number>")


def test_load_math500_split(tmp_path):
    rows = [{"problem": f"p{i}", "answer": rf"\dfrac{{{i}}}{{2}}", "unique_id": f"test/algebra/{i}.json",
             "subject": "Algebra", "level": 1} for i in range(500)]
    (tmp_path / "math500_test.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    lab, ev = load_math500("label", tmp_path), load_math500("eval", tmp_path)
    assert len(lab) == 200 and len(ev) == 300
    assert not {p["qid"] for p in lab} & {p["qid"] for p in ev}
    assert lab == load_math500("label", tmp_path)                       # fixed split
    assert lab[0]["gold"].startswith(r"\frac{") and lab[0]["qid"].startswith("math500-test_algebra_")
    saved = json.loads((tmp_path / "math500_split.json").read_text())
    assert len(saved["label"]) == 200 and len(saved["eval"]) == 300
