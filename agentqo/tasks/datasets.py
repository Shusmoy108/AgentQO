"""Benchmark loaders. GSM8K test set, fixed seeded working set and dev/eval split."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from agentqo.tasks.answers import gsm8k_gold

GSM8K_URL = (
    "https://raw.githubusercontent.com/openai/grade-school-math/master/"
    "grade_school_math/data/{split}.jsonl"
)
TASK_DIR = Path("data/tasks")


def _gsm8k_rows(split: str, cache_dir: Path) -> List[Dict[str, str]]:
    path = cache_dir / f"gsm8k_{split}.jsonl"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(GSM8K_URL.format(split=split), timeout=60) as resp:
            path.write_bytes(resp.read())
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load_gsm8k(
    split: str = "test",
    n: Optional[int] = 300,
    seed: int = 0,
    cache_dir: Path = TASK_DIR,
) -> List[Dict[str, str]]:
    """Seeded working set of GSM8K problems: [{qid, question, gold}].

    ``qid`` is the row index in the official jsonl. The chosen ids are saved
    to ``gsm8k_ids.json`` so the working set is auditable and fixed.
    """
    rows = _gsm8k_rows(split, cache_dir)
    idx = np.arange(len(rows))
    if n is not None and n < len(rows):
        idx = np.sort(np.random.default_rng(seed).choice(len(rows), size=n, replace=False))
    problems = [
        {"qid": f"gsm8k-{split}-{i}", "question": rows[i]["question"], "gold": gsm8k_gold(rows[i]["answer"])}
        for i in idx
    ]
    ids_path = cache_dir / "gsm8k_ids.json"
    ids_path.write_text(json.dumps({"split": split, "seed": seed, "qids": [p["qid"] for p in problems]}, indent=1))
    return problems


def session1_extra(cache_dir: Path = TASK_DIR) -> List[Dict[str, str]]:
    """GSM8K test rows outside the 300 working set, in the Session 1 F4/F5 order (numpy
    seed 1). Session 1 used [0:400] for LABEL (after the 100 dev), [400:500] for VALID and
    [500:800] for EVAL2; 1,019 rows in all."""
    working = load_gsm8k(n=300, seed=0, cache_dir=cache_dir)
    used = {p["qid"] for p in working}
    rows = _gsm8k_rows("test", cache_dir)
    rest = [i for i in range(len(rows)) if f"gsm8k-test-{i}" not in used]
    return [{"qid": f"gsm8k-test-{rest[j]}", "question": rows[rest[j]]["question"],
             "gold": gsm8k_gold(rows[rest[j]]["answer"])} for j in np.random.default_rng(1).permutation(len(rest))]


def _dev_eval(cache_dir: Path) -> Dict[str, List[Dict[str, str]]]:
    return dev_eval_split(load_gsm8k(n=300, seed=0, cache_dir=cache_dir), n_dev=100, seed=0, cache_dir=cache_dir)


def extended_label(n: int, cache_dir: Path = TASK_DIR) -> List[Dict[str, str]]:
    """v2 label set: the Session 1 LABEL 500 order (100 dev, then extra[0:400]), first n.
    n = 200 is the 100 Session 1 dev problems + 100 new ones; never in extended_eval."""
    if n > 500:
        raise ValueError("the Session 1 LABEL set has 500 problems")
    return (_dev_eval(cache_dir)["dev"] + session1_extra(cache_dir)[:400])[:n]


def extended_eval(n: int, cache_dir: Path = TASK_DIR) -> List[Dict[str, str]]:
    """v2 eval set: the 200 Session 1 EVAL problems, then Session 1 EVAL2 (extra[500:800]).

    The first 200 are unchanged, so old plans stay comparable and the cache is reused.
    Disjoint from extended_label and from Session 1 VALID by construction."""
    if n > 500:
        raise ValueError("EVAL + EVAL2 has 500 problems")
    return (_dev_eval(cache_dir)["eval"] + session1_extra(cache_dir)[500:800])[:n]


def dev_eval_split(
    problems: List[Dict[str, str]],
    n_dev: int = 100,
    seed: int = 0,
    cache_dir: Path = TASK_DIR,
) -> Dict[str, List[Dict[str, str]]]:
    """Section 13.3: freeze a dev / eval split once and reuse it.

    If ``split.json`` exists it is authoritative, so the split never moves.
    """
    path = cache_dir / "split.json"
    by_id = {p["qid"]: p for p in problems}
    if path.exists():
        saved = json.loads(path.read_text())
        return {k: [by_id[q] for q in saved[k] if q in by_id] for k in ("dev", "eval")}
    order = np.random.default_rng(seed).permutation(len(problems))
    dev = [problems[i] for i in order[:n_dev]]
    ev = [problems[i] for i in order[n_dev:]]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"dev": [p["qid"] for p in dev], "eval": [p["qid"] for p in ev]}, indent=1))
    return {"dev": dev, "eval": ev}
