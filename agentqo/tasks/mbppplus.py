"""L2-X7: MBPP+ (evalplus/mbppplus, test split, 378 problems) for the code workflow.

Data: data/tasks/mbppplus.jsonl, converted once from the pinned Hugging Face parquet (commit and sha256
in results/v2/X7/README.md). Split: seed-0 permutation of the rows sorted by task_id; label = first 200,
eval = the rest (178, capped at 300). The gold value is "mbppplus:<task_id>"; the MBPP+ test program is
looked up here, so traces stay small. Score: the final code passes ALL MBPP+ tests, run in the sandbox.
"""

from __future__ import annotations

import ast
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from agentqo.tasks.datasets import TASK_DIR

N_LABEL, N_EVAL_MAX, SPLIT_SEED = 200, 300, 0
_CODE = re.compile(r"```(?:python|py|Python)?[ \t]*\n(.*?)```", re.S)


@lru_cache(maxsize=4)
def _rows(cache_dir: str = str(TASK_DIR)) -> Dict[str, Dict]:
    path = Path(cache_dir) / "mbppplus.jsonl"
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    return {str(r["task_id"]): r for r in rows}


def _as_list(v) -> List[str]:
    """A dataset list field, stored as a list or as its Python literal string."""
    return list(v) if not isinstance(v, str) else list(ast.literal_eval(v))


def _tests(row: Dict) -> List[str]:
    return _as_list(row["test_list"])


def load_mbppplus(split: str = "label", cache_dir: Path = TASK_DIR) -> List[Dict[str, str]]:
    """[{qid, question, gold}] for split label (200), eval (the rest, at most 300) or all."""
    rows = sorted(_rows(str(cache_dir)).values(), key=lambda r: int(r["task_id"]))
    order = np.random.default_rng(SPLIT_SEED).permutation(len(rows))
    parts = {"label": [rows[i] for i in order[:N_LABEL]], "eval": [rows[i] for i in order[N_LABEL:N_LABEL + N_EVAL_MAX]]}
    if split not in ("label", "eval", "all"):
        raise ValueError(f"MBPP+ splits are label, eval, all; got {split}")
    chosen = parts["label"] + parts["eval"] if split == "all" else parts[split]
    return [{"qid": f"mbppplus-{r['task_id']}", "question": problem_text(r), "gold": f"mbppplus:{r['task_id']}"}
            for r in chosen]


def problem_text(row: Dict) -> str:
    """The MBPP prompt plus its first visible test, which fixes the function name and signature."""
    return f"{row['prompt'].strip()}\nYour code should pass this test:\n{_tests(row)[0]}"


def example_tests(qid: str, cache_dir: Path = TASK_DIR) -> List[str]:
    """The visible MBPP asserts (test_list) for a problem; the hidden MBPP+ tests are never shown."""
    return _tests(_rows(str(cache_dir))[qid.removeprefix("mbppplus-")])


def test_program(gold: str, cache_dir: Path = TASK_DIR) -> str:
    row = _rows(str(cache_dir))[gold.removeprefix("mbppplus:")]
    imports = _as_list(row.get("test_imports") or [])
    return "\n".join(imports) + "\n" + row["test"]


def extract_code(text: Optional[str]) -> Optional[str]:
    """The last fenced code block (```python ... ```); None if there is none."""
    if not text:
        return None
    blocks = _CODE.findall(text)
    return blocks[-1].strip() or None if blocks else None


def passes(code: Optional[str], gold: str, timeout_s: float = 10.0, cache_dir: Path = TASK_DIR) -> bool:
    """True if ``code`` passes every MBPP+ test, run in the sandbox (never in this process)."""
    if not code:
        return False
    from agentqo.tasks.sandbox import run_python
    return run_python(code + "\n\n" + test_program(gold, cache_dir), timeout_s=timeout_s).ok


def assert_report(code: Optional[str], asserts: List[str], timeout_s: float = 10.0) -> str:
    """Run each assert against ``code`` in the sandbox; one PASS/FAIL line per assert (for the fixer/verifier)."""
    if not code:
        return "no code to test"
    if not asserts:
        return "no tests"
    from agentqo.tasks.sandbox import run_python
    harness = (code + "\n\n_tests = " + repr(asserts) + "\n"
               "for _t in _tests:\n"
               "    try:\n"
               "        exec(_t, globals())\n"
               "        print('PASS', _t)\n"
               "    except Exception as _e:\n"
               "        print('FAIL', _t, '->', type(_e).__name__, str(_e)[:200])\n")
    r = run_python(harness, timeout_s=timeout_s)
    if r.timed_out:
        return f"TIMEOUT after {timeout_s:.0f} s (infinite loop or too slow)\n{r.stdout[-1500:]}"
    if r.returncode != 0 and not r.stdout:
        return "ERROR running the code:\n" + r.stderr.strip()[-1500:]
    return r.stdout.strip()[-3000:] or "no output"


def tester_asserts(text: Optional[str], limit: int = 8) -> List[str]:
    """The assert lines the tester wrote (from its last code block, else its text)."""
    src = extract_code(text) or (text or "")
    return [ln.strip() for ln in src.splitlines() if ln.strip().startswith("assert ")][:limit]
