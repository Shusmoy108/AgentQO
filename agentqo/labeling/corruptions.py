"""Corruptions for output-substitution fault injection (plan WP3).

A corruption is a wrong version of node v's output text. Descendants only
see text, so this is the only honest way to make v "wrong" with a real LLM.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from agentqo.backends.base import NodeResult
from agentqo.backends.vllm_http import _output_as_text
from agentqo.workflows.dag import NodeRole

SUBTLE_WRONG = """Rewrite the following output with exactly one subtle error that changes its conclusion. Keep the same format and length. Return only the rewritten output.
Output:
{text}"""

_KEY_SPAN = re.compile(r"(RESULT:|####)(\s*)(-?\$?[\d,]+(?:\.\d+)?)")


@dataclass
class Corruption:
    text: str
    strategy: str
    key: Optional[str]
    reference_key: Optional[str]

    @property
    def key_differs(self) -> Optional[bool]:
        """None when the node has no key (planner); judge by final answer instead."""
        if self.reference_key is None:
            return None
        return self.key != self.reference_key

    def to_dict(self) -> Dict[str, Any]:
        return {"strategy": self.strategy, "key": self.key, "reference_key": self.reference_key,
                "key_differs": self.key_differs, "text": self.text}


def _perturbations(key: str) -> List[str]:
    """Plausible arithmetic errors: off by one, a wrong operation, a digit swap."""
    try:
        v = float(key)
    except ValueError:
        return []
    out = []
    if v == int(v):
        k = int(v)
        out += [str(k + 1), str(k * 2), str(k - 1)]
        digits = str(abs(k))
        if len(digits) >= 2 and digits[-1] != digits[-2]:
            out.append(("-" if k < 0 else "") + digits[:-2] + digits[-1] + digits[-2])
    else:
        out += [repr(v + 1), repr(v * 2)]
    return [o for o in dict.fromkeys(out) if o != key]


def numeric_perturb(text: str, key: Optional[str], attempt: int) -> Optional[str]:
    if key is None:
        return None
    options = _perturbations(key)
    matches = list(_KEY_SPAN.finditer(text))
    if attempt >= len(options) or not matches:
        return None
    m = matches[-1]
    return text[: m.start(3)] + options[attempt] + text[m.end(3):]


class CorruptionMaker:
    """Builds C corruptions for one (task, node), rotating strategies.

    ``sample`` runs v on its baseline inputs with a given temperature and
    sample index (so each sample has its own fixed seed).
    ``donor_text`` returns v's baseline output from a different task.
    ``rewrite`` asks the small model for a subtle error (fallback).
    """

    def __init__(
        self,
        extract: Callable[[str], Optional[str]],
        sample: Callable[[float, int], NodeResult],
        donor_text: Callable[[int], Optional[str]],
        rewrite: Callable[[str, int], str],
        max_resamples: int = 8,
    ) -> None:
        self.extract = extract
        self.sample = sample
        self.donor_text = donor_text
        self.rewrite = rewrite
        self.max_resamples = max_resamples
        self._resample_next = 1

    def make(self, role: NodeRole, reference_text: str, n: int) -> List[Corruption]:
        ref_key = None if role == NodeRole.PLANNER else self.extract(reference_text)
        keyed = ref_key is not None
        strategies = (["numeric_perturb", "resample_disagree", "swap_other_task"] if keyed
                      else ["swap_other_task", "llm_subtle_wrong"])
        out: List[Corruption] = []
        used = {reference_text}
        for c in range(n):
            made = None
            for s in strategies[c % len(strategies):] + strategies[:c % len(strategies)]:
                text = self._try(s, reference_text, ref_key, c)
                if text is not None and text not in used:
                    made = Corruption(text, s, self.extract(text) if keyed else None, ref_key)
                    break
            if made is None:
                text = self.rewrite(reference_text, c)
                made = Corruption(text, "llm_subtle_wrong", self.extract(text) if keyed else None, ref_key)
            used.add(made.text)
            out.append(made)
        return out

    def _try(self, strategy: str, ref_text: str, ref_key: Optional[str], c: int) -> Optional[str]:
        if strategy == "numeric_perturb":
            return numeric_perturb(ref_text, ref_key, c)
        if strategy == "resample_disagree":
            while self._resample_next <= self.max_resamples:
                idx = self._resample_next
                self._resample_next += 1
                text = _output_as_text(self.sample(1.0, 1000 + idx).output)
                if self.extract(text) != ref_key:
                    return text
            return None
        if strategy == "swap_other_task":
            text = self.donor_text(c)
            if text is None or (ref_key is not None and self.extract(text) == ref_key):
                return None
            return text
        if strategy == "llm_subtle_wrong":
            return self.rewrite(ref_text, c)
        raise ValueError(strategy)


def rewrite_prompt(text: str) -> str:
    return SUBTLE_WRONG.format(text=text)

