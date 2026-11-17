"""L2-X5: MATH-500 (HuggingFaceH4/MATH-500, test split). Fixed seeded split of the 500 problems:
label = first 200 of a seed-0 permutation, eval = the other 300. The ids are written to
math500_split.json next to the data so the split is auditable."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Dict, List

import numpy as np

from agentqo.tasks.answers import normalize_math
from agentqo.tasks.datasets import TASK_DIR

URL = "https://huggingface.co/datasets/HuggingFaceH4/MATH-500/resolve/main/test.jsonl"
N_LABEL = 200
SPLIT_SEED = 0


def _rows(cache_dir: Path) -> List[Dict]:
    path = Path(cache_dir) / "math500_test.jsonl"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(URL, timeout=120) as r:
            path.write_bytes(r.read())
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    if len(rows) != 500:
        raise RuntimeError(f"expected 500 MATH-500 rows, got {len(rows)}")
    return sorted(rows, key=lambda r: r["unique_id"])


def load_math500(split: str = "label", cache_dir: Path = TASK_DIR) -> List[Dict[str, str]]:
    """[{qid, question, gold}] for split label (200), eval (300) or all (500)."""
    rows = _rows(cache_dir)
    order = np.random.default_rng(SPLIT_SEED).permutation(len(rows))
    parts = {"label": [rows[i] for i in order[:N_LABEL]], "eval": [rows[i] for i in order[N_LABEL:]]}
    split_path = Path(cache_dir) / "math500_split.json"
    if not split_path.exists():
        split_path.write_text(json.dumps({"seed": SPLIT_SEED, **{k: [r["unique_id"] for r in v] for k, v in parts.items()}},
                                         indent=1) + "\n")
    if split not in ("label", "eval", "all"):
        raise ValueError(f"MATH-500 splits are label, eval, all; got {split}")
    chosen = parts["label"] + parts["eval"] if split == "all" else parts[split]
    return [{"qid": "math500-" + r["unique_id"].replace("/", "_").removesuffix(".json"),
             "question": r["problem"], "gold": normalize_math(r["answer"])} for r in chosen]
