"""
Multi-GPU / multi-LLM interaction simulator for AgentIconq.

Not a substitute for vLLM traces. It exists so H4's *predictor* and
metrics can be tested before GPU access, and so the sign of prefix
reuse is in the data generator by construction.

Latency units are abstract milliseconds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np


MODEL_PREFILL_US = {
    "llm-7b": 0.012,
    "llm-70b": 0.045,
    "small": 0.012,
    "large": 0.045,
}
MODEL_DECODE_US = {
    "llm-7b": 0.35,
    "llm-70b": 1.20,
    "small": 0.35,
    "large": 1.20,
}


@dataclass(frozen=True)
class CallSpec:
    """One in-flight LLM call."""

    call_id: str
    model_id: str
    gpu_id: int
    prompt_tokens: int
    decode_tokens: int
    prefix_id: Optional[str] = None


@dataclass
class CallOutcome:
    call_id: str
    isolated_latency: float
    own_latency: float
    imposed_on_others: float
    n_colocated: int
    shared_prefix: bool
    gpu_id: int
    model_id: str


def isolated_latency(call: CallSpec) -> float:
    prefill = MODEL_PREFILL_US.get(call.model_id, 0.02) * call.prompt_tokens
    decode = MODEL_DECODE_US.get(call.model_id, 0.5) * call.decode_tokens
    return prefill + decode


def simulate_batch(calls: Sequence[CallSpec]) -> List[CallOutcome]:
    """Compute two-sided costs for a co-located batch.

    Interaction is *only* among calls that share a GPU. Shared prefix_id
    on the same GPU reduces prefill (negative imposed delay). Distinct
    prefixes contend for SM/memory (positive imposed delay). Cross-GPU
    pairs do not interact.
    """
    by_gpu: Dict[int, List[CallSpec]] = {}
    for call in calls:
        by_gpu.setdefault(call.gpu_id, []).append(call)

    outcomes: Dict[str, CallOutcome] = {}
    for gpu_id, group in by_gpu.items():
        isolated = {c.call_id: isolated_latency(c) for c in group}
        n = len(group)
        for call in group:
            others = [o for o in group if o.call_id != call.call_id]
            n_col = len(others)
            share = [
                o for o in others
                if call.prefix_id and o.prefix_id == call.prefix_id
            ]
            contend = [o for o in others if o not in share]

            # Contention grows with decode tokens of neighbors.
            contention = 0.0
            for o in contend:
                contention += 0.12 * isolated[o.call_id] / max(n, 1)

            # Prefix reuse: we avoid repeating a shared prefill.
            reuse = 0.0
            if share:
                prefill = MODEL_PREFILL_US.get(call.model_id, 0.02) * call.prompt_tokens
                reuse = 0.55 * prefill * (1.0 - 1.0 / (1 + len(share)))

            own = isolated[call.call_id] + contention - reuse
            # Extra latency this call imposes on the rest of the GPU batch.
            imposed = contention - (reuse * 0.5 if share else 0.0)
            outcomes[call.call_id] = CallOutcome(
                call_id=call.call_id,
                isolated_latency=isolated[call.call_id],
                own_latency=max(own, 0.05 * isolated[call.call_id]),
                imposed_on_others=imposed,
                n_colocated=n_col,
                shared_prefix=bool(share),
                gpu_id=gpu_id,
                model_id=call.model_id,
            )
    return [outcomes[c.call_id] for c in calls]


def outcome_features(outcome: CallOutcome, call: CallSpec) -> np.ndarray:
    """Feature vector aligned with AgentIconq baselines.

    Layout:
        0 isolated latency (single-call baseline uses this)
        1 n_colocated
        2 prompt_tokens
        3 decode_tokens
        4 shared_prefix
        5 is_70b
        6 gpu_id
    """
    return np.array([
        outcome.isolated_latency,
        float(outcome.n_colocated),
        float(call.prompt_tokens),
        float(call.decode_tokens),
        1.0 if outcome.shared_prefix else 0.0,
        1.0 if "70" in call.model_id or call.model_id == "large" else 0.0,
        float(call.gpu_id),
    ], dtype=np.float32)


def generate_interaction_dataset(
    n_batches: int = 400,
    max_batch: int = 6,
    n_gpus: int = 2,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray, List[CallOutcome]]:
    """Synthetic H4 dataset with both contention and prefix-reuse batches."""
    rng = np.random.default_rng(seed)
    models = ["llm-7b", "llm-70b"]
    X_rows: List[np.ndarray] = []
    Y_rows: List[np.ndarray] = []
    all_outcomes: List[CallOutcome] = []

    for b in range(n_batches):
        k = int(rng.integers(1, max_batch + 1))
        reuse_batch = bool(rng.random() < 0.35)
        shared_prefix = f"pfx_{b}" if reuse_batch else None
        calls: List[CallSpec] = []
        for i in range(k):
            gpu = 0 if reuse_batch else int(rng.integers(0, n_gpus))
            prefix = shared_prefix if reuse_batch else (
                f"pfx_{b}_{i}" if rng.random() > 0.2 else shared_prefix
            )
            calls.append(
                CallSpec(
                    call_id=f"b{b}_c{i}",
                    model_id=str(rng.choice(models)),
                    gpu_id=gpu,
                    prompt_tokens=int(rng.integers(32, 1024)),
                    decode_tokens=int(rng.integers(8, 256)),
                    prefix_id=prefix,
                )
            )
        outcomes = simulate_batch(calls)
        for call, out in zip(calls, outcomes):
            X_rows.append(outcome_features(out, call))
            Y_rows.append(np.array([out.own_latency, out.imposed_on_others]))
            all_outcomes.append(out)

    return np.stack(X_rows), np.stack(Y_rows), all_outcomes
