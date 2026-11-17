"""Discrete-event (fluid) simulator of vLLM servers, one per model, with K problems in flight.

Server model, per model m (parameters o, c, a, b; fitted in latsim.fit):
  * A call arrives with prompt_tokens P and completion_tokens C. It is first prefilled:
    c seconds per prompt token; the calls in prefill share the server equally and, as in
    vLLM (prefill batched ahead of decode), the server's decoding calls make no progress
    while any call is in prefill.
  * Then it decodes C tokens; with n calls decoding, each gets one token per step of
    a + b * n + e * KV / 1000 seconds (continuous batching), KV = sum over the decoding
    calls of their context, P + C / 2 tokens each (attention reads the KV cache).
  * The caller sees the result o seconds after the server finishes (HTTP, tokenization),
    so an isolated call takes o + c * P + C * (a + b + e * (P + C / 2) / 1000).
  * Interference (two or more servers on one GPU): every rate of server m is divided by
    1 + sum_o beta[o -> m] * busy_o, busy_o = 1 while server o has any call. Separate
    placement: betas = {}.
Problems run their calls one after another (WorkflowExecutor runs nodes in topological
order, so every call also waits for its parents); K problems run in a closed loop, as
run_placement's ThreadPoolExecutor(K).
"""

from __future__ import annotations

import heapq
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

Call = Tuple[str, float, float]  # (model, prompt_tokens, completion_tokens)


def _engine(arrivals: List[tuple], params: Mapping[str, Mapping[str, float]],
            betas: Mapping[Tuple[str, str], float], on_done: Callable[[int, float], None]) -> None:
    """arrivals: heap of (time, seq, call_id, model, P, C); on_done(call_id, t_seen) may push more."""
    pre: Dict[str, Dict[int, float]] = {}  # model -> call -> remaining prompt tokens
    dec: Dict[str, Dict[int, float]] = {}  # model -> call -> remaining decode tokens
    todo: Dict[int, float] = {}  # call -> completion tokens, until its prefill ends
    kv: Dict[int, float] = {}  # call -> context tokens while decoding
    kv_sum: Dict[str, float] = {}
    t, eps = 0.0, 1e-9
    while arrivals or any(pre.values()) or any(dec.values()):
        while arrivals and arrivals[0][0] <= t + eps:
            _, _, cid, m, p, c = heapq.heappop(arrivals)
            pre.setdefault(m, {})[cid] = max(p, 0.0)
            dec.setdefault(m, {})
            todo[cid] = max(c, 0.0)
            kv[cid] = max(p, 0.0) + max(c, 0.0) / 2
        busy = {m for m in pre if pre[m] or dec[m]}
        if not busy:
            t = arrivals[0][0]
            continue
        # per-call rates (tokens/s) of the current phase
        rates: Dict[Tuple[str, int, bool], float] = {}
        for m in busy:
            q = params[m]
            slow = 1.0 + sum(b for (o, mm), b in betas.items() if mm == m and o in busy)
            if pre[m]:
                r = 1.0 / (q["c"] * slow * len(pre[m])) if q["c"] > 0 else float("inf")
                for cid in pre[m]:
                    rates[(m, cid, True)] = r
            else:
                r = 1.0 / ((q["a"] + q["b"] * len(dec[m]) + q.get("e", 0.0) * kv_sum[m] / 1000) * slow)
                for cid in dec[m]:
                    rates[(m, cid, False)] = r
        dt = min((pre[m][cid] if is_pre else dec[m][cid]) / r for (m, cid, is_pre), r in rates.items())
        if arrivals:
            dt = min(dt, arrivals[0][0] - t)
        dt = max(dt, 0.0)
        t += dt
        for (m, cid, is_pre), r in rates.items():
            box = pre[m] if is_pre else dec[m]
            box[cid] = box[cid] - r * dt if r != float("inf") else 0.0
            if box[cid] <= eps:
                del box[cid]
                if is_pre:
                    c_left = todo.pop(cid)
                    if c_left > eps:
                        dec[m][cid] = c_left
                        kv_sum[m] = kv_sum.get(m, 0.0) + kv[cid]
                        continue
                else:
                    kv_sum[m] -= kv[cid]
                del kv[cid]
                on_done(cid, t + params[m]["o"])



def simulate(problems: Sequence[Sequence[Call]], params: Mapping[str, Mapping[str, float]], k: int,
             betas: Optional[Mapping[Tuple[str, str], float]] = None,
             call_latency: Optional[List[List[float]]] = None) -> List[float]:
    """Per-problem latency (seconds), in input order, with k problems in flight.
    call_latency, if given, is filled with each problem's per-call latencies."""
    n = len(problems)
    latency, start, step = [0.0] * n, [0.0] * n, [0] * n
    issued = [0.0] * n
    if call_latency is not None:
        call_latency[:] = [[] for _ in range(n)]
    arrivals: List[tuple] = []
    seq = [0]
    nxt = [0]

    def issue(i: int, t: float) -> None:
        while not problems[i]:  # a problem without calls ends at once
            latency[i] = 0.0
            if nxt[0] >= n:
                return
            i, nxt[0] = nxt[0], nxt[0] + 1
            start[i] = t
        m, p, c = problems[i][step[i]][:3]
        issued[i] = t
        seq[0] += 1
        heapq.heappush(arrivals, (t, seq[0], i, m, p, c))

    def on_done(i: int, t: float) -> None:
        if call_latency is not None:
            call_latency[i].append(t - issued[i])
        step[i] += 1
        if step[i] < len(problems[i]):
            issue(i, t)
            return
        latency[i] = t - start[i]
        if nxt[0] < n:
            j = nxt[0]
            nxt[0] += 1
            start[j] = t
            issue(j, t)

    for _ in range(min(k, n)):
        j = nxt[0]
        nxt[0] += 1
        issue(j, 0.0)
    _engine(arrivals, params, betas or {}, on_done)
    return latency


def replay(calls: Sequence[Tuple[float, str, float, float]], params: Mapping[str, Mapping[str, float]],
           betas: Optional[Mapping[Tuple[str, str], float]] = None) -> List[float]:
    """Open loop: calls = [(issue_time, model, P, C)]; returns each call's latency."""
    arrivals = [(t, i, i, m, p, c) for i, (t, m, p, c) in enumerate(calls)]
    heapq.heapify(arrivals)
    out = [0.0] * len(calls)

    def on_done(i: int, t: float) -> None:
        out[i] = t - calls[i][0]

    _engine(arrivals, params, betas or {}, on_done)
    return out


def pct(xs: Sequence[float], q: float) -> float:
    """Nearest-rank percentile, as scripts/h4_fit.pct (and run_placement's summaries)."""
    xs = sorted(xs)
    i = max(0, min(len(xs) - 1, int(round(q * (len(xs) - 1)))))
    return xs[i]
