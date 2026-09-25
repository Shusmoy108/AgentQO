"""Answer extraction and scoring for real benchmark outputs."""

from __future__ import annotations

import re
import string
from collections import Counter
from typing import Optional

_NUM = r"-?\$?\s*-?\d[\d,]*(?:\.\d+)?"
_HASH = re.compile(r"####\s*(" + _NUM + ")")
_BOXED = re.compile(r"\\boxed\{\s*(" + _NUM + r")\s*\}")
_ANY = re.compile(_NUM)


def _canon(raw: str) -> Optional[str]:
    """'$1,234.50' -> '1234.5', '18.00' -> '18', '-3' -> '-3'."""
    s = raw.replace("$", "").replace(",", "").replace(" ", "").rstrip(".")
    neg = s.count("-") % 2 == 1
    s = s.replace("-", "")
    if not s:
        return None
    try:
        value = float(s)
    except ValueError:
        return None
    if neg:
        value = -value
    if value == int(value):
        return str(int(value))
    return repr(value)


def extract_gsm8k_number(text: str) -> Optional[str]:
    """Final numeric answer: last ``#### n``, else last ``\\boxed{n}``, else last number."""
    if not text:
        return None
    for pattern in (_HASH, _BOXED, _ANY):
        found = pattern.findall(text)
        if found:
            return _canon(found[-1])
    return None


def gsm8k_gold(answer_field: str) -> str:
    """Gold answer from the GSM8K ``answer`` field (number after ``####``)."""
    found = _HASH.findall(answer_field)
    if not found:
        raise ValueError(f"no #### in GSM8K answer: {answer_field[-80:]!r}")
    value = _canon(found[-1])
    assert value is not None
    return value


def normalize_answer(text: str) -> str:
    """SQuAD normalization: lowercase, drop punctuation, articles, extra spaces."""
    text = text.lower()
    text = "".join(ch for ch in text if ch not in set(string.punctuation))
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def f1(pred: str, gold: str) -> float:
    p, g = normalize_answer(pred).split(), normalize_answer(gold).split()
    common = sum((Counter(p) & Counter(g)).values())
    if common == 0:
        return 0.0
    precision, recall = common / len(p), common / len(g)
    return 2 * precision * recall / (precision + recall)
