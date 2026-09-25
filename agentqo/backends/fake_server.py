"""Scripted OpenAI-compatible server for dry runs (test double, never results).

Plug into ``VLLMHTTPBackend(request_fn=FakeServer(...))``. It recognizes the
role from the prompt template, knows each problem's gold answer, and makes
errors that propagate through *text*:

- a node's output is wrong if it errs itself (rate per model) or if the
  upstream text it received is wrong (a flawed plan, a plan written for a
  different problem, or a RESULT / #### number that is not the gold answer);
- a verifier repairs a wrong input with probability ``repair[model]``;
- a formatter copies whatever answer it was given.

Randomness depends on (model, messages) at temperature 0 and also on the
seed above 0, like a real server with fixed seeds.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import zlib
from typing import Any, Dict, List, Mapping, Optional

import numpy as np

from agentqo.tasks.answers import extract_gsm8k_number

_KEY = re.compile(r"(?:RESULT:|####)\s*(-?[\d,]+(?:\.\d+)?)")
PLAN_OK, PLAN_BAD = "[plan-ok", "[plan-bad]"
_TAG = re.compile(r"\[plan-ok:(\w+)\]")


class FakeServer:
    def __init__(
        self,
        problems: List[Dict[str, str]],
        error_rates: Mapping[str, float],
        repair: Optional[Mapping[str, float]] = None,
        sleep_s: float = 0.0,
        logprobs: bool = True,
    ) -> None:
        self.gold = {p["question"]: p["gold"] for p in problems}
        self.error_rates = dict(error_rates)
        self.repair = dict(repair or {m: 0.5 for m in error_rates})
        self.sleep_s = sleep_s
        self.logprobs = logprobs
        self.n_requests = 0

    def __call__(self, url: str, payload: Dict[str, Any], headers: Mapping[str, str], timeout_s: float) -> Dict[str, Any]:
        self.n_requests += 1
        if self.sleep_s:
            time.sleep(self.sleep_s)
        model = payload["model"]
        prompt = payload["messages"][-1]["content"]
        temp = float(payload.get("temperature", 0.0))
        material = json.dumps([model, payload["messages"], payload.get("seed") if temp > 0 else 0])
        rng = np.random.default_rng(int(hashlib.sha256(material.encode()).hexdigest()[:15], 16))
        # Higher temperature -> more errors, as with real sampling.
        err = min(0.95, self.error_rates.get(model, 0.3) * (1.0 + 0.5 * temp))
        text, ok = self._respond(prompt, model, err, rng)
        lp = -0.05 if ok else -0.7
        return {
            "choices": [{
                "message": {"role": "assistant", "content": text},
                "logprobs": {"content": [{"token": t, "logprob": lp + 0.05 * rng.standard_normal()}
                                         for t in text.split()[:16]]} if self.logprobs else None,
            }],
            "usage": {"prompt_tokens": len(prompt) // 4, "completion_tokens": max(1, len(text) // 4)},
            "model": model,
        }

    def _respond(self, prompt: str, model: str, err: float, rng: np.random.Generator):
        if prompt.startswith("Rewrite the following"):
            return self._subtle_wrong(prompt, rng), False
        question = next((q for q in self.gold if q in prompt), None)
        if question is None:
            return "I cannot find the problem.", False
        gold = self.gold[question]
        # Plans carry a per-problem tag, so a plan swapped in from another
        # task is recognized as wrong, as a real model would be misled by it.
        tag_ok = f"{zlib.crc32(question.encode()) & 0xFFFF:x}"
        upstream = _upstream(prompt)
        upstream_ok = (
            PLAN_BAD not in prompt
            and all(t == tag_ok for t in _TAG.findall(upstream))
            and all(k.replace(",", "") == gold for k in _KEY.findall(upstream))
        )
        own_error = rng.random() < err

        if prompt.startswith(("You are planning", "Restate this")):
            ok = not own_error
            tag = f"{PLAN_OK}:{tag_ok}]" if ok else PLAN_BAD
            head = "PLAN:" if prompt.startswith("You are") else "GIVEN:"
            return f"{head}\n1. Find the quantities. {tag}\n2. Combine them.", ok
        if "Restate only the final answer" in prompt:
            given = extract_gsm8k_number(_upstream(prompt)) or gold
            return f"The answer is {given}.\n#### {given}", given == gold
        if "Check the solution" in prompt:
            if upstream_ok:
                ok = not (own_error and rng.random() < 0.3)
            else:
                ok = rng.random() < self.repair.get(model, 0.5)
            verdict = "correct" if upstream_ok and ok else "incorrect"
            return f"VERDICT: {verdict}\n#### {gold if ok else _wrong(gold, rng)}", ok

        ok = upstream_ok and not own_error
        value = gold if ok else _wrong(gold, rng)
        if "RESULT: <number>" in prompt:
            return f"Computing this step gives {value}.\nRESULT: {value}", ok
        return f"Working through the problem, the total is {value}.\n#### {value}", ok

    @staticmethod
    def _subtle_wrong(prompt: str, rng: np.random.Generator) -> str:
        original = prompt.split("Output:\n", 1)[-1]
        out = _TAG.sub(PLAN_BAD, original)
        keys = _KEY.findall(out)
        if keys:
            k = keys[-1]
            out = out[::-1].replace(k[::-1], _wrong(k.replace(",", ""), rng)[::-1], 1)[::-1]
        return out if out != original else original + f" {PLAN_BAD}"


def _upstream(prompt: str) -> str:
    """Everything after the problem statement: what the node was given."""
    for marker in ("Plan:", "Results so far:", "Step results:", "Proposed solution:",
                   "Solution:", "Notes:", "Your work so far"):
        i = prompt.find(marker)
        if i >= 0:
            return prompt[i:]
    return ""


def _wrong(gold: str, rng: np.random.Generator) -> str:
    try:
        g = int(float(gold))
    except ValueError:
        return gold + "0"
    return str(g + int(rng.choice([-10, -2, -1, 1, 2, 10])))
