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
_FINAL = re.compile(r"final answer\s*:\s*(.+)", re.IGNORECASE)
_HOT_HASH = re.compile(r"####\s*(.+)")
_FINDING = re.compile(r"FINDING\s*:\s*(.+)", re.IGNORECASE)


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


def gsm8k_answer_span(text: str) -> Optional[tuple]:
    """L2-X12: (start, end) character span of the answer extract_gsm8k_number returns, else None."""
    if not text:
        return None
    for pattern in (_HASH, _BOXED, _ANY):
        found = list(pattern.finditer(text))
        if found:
            m = found[-1]
            a, b = m.span(1) if m.groups() else m.span(0)
            while a < b and text[a].isspace(): a += 1      # the number pattern may include surrounding blanks
            while b > a and text[b - 1].isspace(): b -= 1
            return a, b
    return None


def extract_hotpot_answer(text: str) -> Optional[str]:
    """Normalized short answer: last "Final answer:", else "####", else "FINDING:", else last line."""
    if not text or not text.strip():
        return None
    for pattern in (_FINAL, _HOT_HASH, _FINDING):
        found = pattern.findall(text)
        if found:
            return normalize_answer(found[-1]) or None
    return normalize_answer(text.strip().splitlines()[-1]) or None


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


# L2-X5: MATH-500. The answer is the content of the last \boxed{...} (braces balanced); no boxed
# answer means unscorable. Equality is normalized string match or numeric equality.
def extract_boxed(text: str) -> Optional[str]:
    """Normalized content of the last ``\\boxed{...}`` (or ``\\fbox{...}``), else None."""
    if not text:
        return None
    start = max(text.rfind("\\boxed{"), text.rfind("\\fbox{"))
    if start < 0:
        return None
    i = text.index("{", start) + 1
    depth, j = 1, i
    while j < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        j += 1
    if depth:
        return None
    return normalize_math(text[i:j - 1]) or None


def _strip_text_cmd(s: str) -> str:
    return re.sub(r"\\(?:text|textbf|mathrm|mbox)\{([^{}]*)\}", r"\1", s)


def normalize_math(s: str) -> str:
    """Canonical string for a MATH answer: no spaces/sizing/$/units of degrees or percent, dfrac -> frac,
    a single leading 'x =' dropped, trailing period dropped."""
    s = _strip_text_cmd(s.strip())
    for a, b in (("\\left", ""), ("\\right", ""), ("\\!", ""), ("\\,", ""), ("\\;", ""), ("\\:", ""),
                 ("\\dfrac", "\\frac"), ("\\tfrac", "\\frac"), ("^{\\circ}", ""), ("^\\circ", ""),
                 ("\\%", ""), ("%", ""), ("$", ""), ("\\displaystyle", "")):
        s = s.replace(a, b)
    s = re.sub(r"\s+", "", s).rstrip(".")
    s = re.sub(r"^[a-zA-Z]=(?=.)", "", s)
    s = re.sub(r"\\frac(\d)(\d)", r"\\frac{\1}{\2}", s)
    return s


def _math_number(s: str) -> Optional[float]:
    """Numeric value of a normalized answer: 12, -3.5, 1,000, a/b, \\frac{a}{b}, -\\frac{a}{b}; else None."""
    s = s.replace(",", "")
    m = re.fullmatch(r"(-?)\\frac\{(-?\d+(?:\.\d+)?)\}\{(-?\d+(?:\.\d+)?)\}", s)
    if m:
        den = float(m.group(3))
        return None if den == 0 else (-1 if m.group(1) else 1) * float(m.group(2)) / den
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)/(-?\d+(?:\.\d+)?)", s)
    if m:
        den = float(m.group(2))
        return None if den == 0 else float(m.group(1)) / den
    try:
        return float(s)
    except ValueError:
        return None


def math_equal(pred: Optional[str], gold: str) -> bool:
    """Normalized string match, else numeric equality (relative tolerance 1e-6)."""
    if pred is None:
        return False
    p, g = normalize_math(pred), normalize_math(gold)
    if p == g:
        return True
    a, b = _math_number(p), _math_number(g)
    return a is not None and b is not None and abs(a - b) <= 1e-6 * max(1.0, abs(b))


def f1(pred: str, gold: str) -> float:
    p, g = normalize_answer(pred).split(), normalize_answer(gold).split()
    common = sum((Counter(p) & Counter(g)).values())
    if common == 0:
        return 0.0
    precision, recall = common / len(p), common / len(g)
    return 2 * precision * recall / (precision + recall)
