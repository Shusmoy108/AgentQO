"""M8: HotpotQA distractor setting (10 given paragraphs, no retrieval).

Rows come from the official dev file, or from the Hugging Face rows API when
that host is down. Both are stored in one schema and sorted by id, so the
seeded label/eval split does not depend on the source.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List

import numpy as np

from agentqo.tasks.datasets import TASK_DIR

OFFICIAL_URL = "http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json"
HF_ROWS_URL = ("https://datasets-server.huggingface.co/rows?dataset=hotpotqa/hotpot_qa"
               "&config=distractor&split=validation&offset={offset}&length=100")
N_DEV = 7405
N_LABEL, N_EVAL = 200, 300
SPLIT_SEED = 0


def _official_rows() -> List[Dict]:
    with urllib.request.urlopen(OFFICIAL_URL, timeout=120) as r:
        rows = json.loads(r.read())
    return [{"id": x["_id"], "question": x["question"], "answer": x["answer"], "context": x["context"]}
            for x in rows]


def _hf_page(offset: int) -> Dict:
    for attempt in range(8):
        try:
            with urllib.request.urlopen(HF_ROWS_URL.format(offset=offset), timeout=60) as r:
                return json.loads(r.read())
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Hugging Face rows API kept failing at offset {offset}")


def _hf_rows() -> List[Dict]:
    rows = []
    for offset in range(0, N_DEV, 100):
        for item in _hf_page(offset)["rows"]:
            x = item["row"]
            ctx = list(zip(x["context"]["title"], x["context"]["sentences"]))
            rows.append({"id": x["id"], "question": x["question"], "answer": x["answer"], "context": ctx})
        time.sleep(0.2)
    return rows


def _load_rows(cache_dir: Path) -> List[Dict]:
    path = cache_dir / "hotpot_dev_distractor.jsonl"
    if not path.exists():
        try:
            rows = _official_rows()
        except (OSError, ValueError) as exc:
            print(f"official HotpotQA host failed ({exc}); using the Hugging Face rows API")
            rows = _hf_rows()
        if len(rows) != N_DEV:
            raise RuntimeError(f"expected {N_DEV} HotpotQA dev rows, got {len(rows)}")
        rows.sort(key=lambda r: r["id"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return [json.loads(line) for line in path.read_text().splitlines()]


def format_problem(row: Dict) -> str:
    paragraphs = "\n".join(f"[{title}] {''.join(sents)}" for title, sents in row["context"])
    return f"Question: {row['question']}\nParagraphs:\n{paragraphs}"


def split_rows(rows: List[Dict], seed: int = SPLIT_SEED) -> Dict[str, List[Dict]]:
    """Fixed seeded disjoint splits over rows sorted by id: label 200, eval 300."""
    order = np.random.default_rng(seed).permutation(len(rows))
    return {"label": [rows[i] for i in order[:N_LABEL]],
            "eval": [rows[i] for i in order[N_LABEL:N_LABEL + N_EVAL]]}


def load_hotpotqa(split: str = "label", cache_dir: Path = TASK_DIR) -> List[Dict[str, str]]:
    """[{qid, question, gold}]; ``question`` holds the question and its paragraphs."""
    parts = split_rows(_load_rows(cache_dir))
    rows = parts["label"] + parts["eval"] if split == "all" else parts[split]
    return [{"qid": f"hotpot-{r['id']}", "question": format_problem(r), "gold": r["answer"]} for r in rows]
