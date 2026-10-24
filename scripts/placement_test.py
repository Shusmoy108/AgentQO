#!/usr/bin/env python3
"""Placement test: how much do agent calls slow each other down, depending on
where the models run?

Sends a mix of small-model and large-model requests at several concurrency
levels and records per-request latency. Run it twice:
  split      small model on GPU A, large model on GPU B (two VMs)
  colocated  both models on the same GPU
and compare. Uses only the Python standard library.

    python3 scripts/placement_test.py --config split \
        --small-url http://localhost:8001 --large-url http://10.x.x.x:8002
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import json
import os
import random
import statistics
import time
import urllib.request

SMALL_MODEL = os.environ.get("VLLM_SMALL_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
LARGE_MODEL = os.environ.get("VLLM_LARGE_MODEL", "Qwen/Qwen2.5-7B-Instruct")

SHARED_PREFIX = (
    "You are one agent in a team solving grade-school math problems. Read the "
    "problem carefully, reason step by step, and end with the final number. "
) * 8


def make_prompt(rng: random.Random, shared: bool) -> str:
    a, b, c = rng.randint(12, 999), rng.randint(3, 99), rng.randint(5, 500)
    q = (f"A shop sells {a} items per day for {b} days, then returns {c} items. "
         f"How many items were sold in total? Explain briefly.")
    return (SHARED_PREFIX + q) if shared else q


def call(url: str, model: str, prompt: str, max_tokens: int) -> tuple[float, int]:
    body = json.dumps({"model": model, "prompt": prompt, "max_tokens": max_tokens,
                       "temperature": 0}).encode()
    req = urllib.request.Request(url.rstrip("/") + "/v1/completions", data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=900) as r:
        out = json.loads(r.read())
    return time.perf_counter() - t0, int(out.get("usage", {}).get("completion_tokens", 0))


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    k = max(0, min(len(xs) - 1, int(round(q * (len(xs) - 1)))))
    return xs[k]


def main() -> None:
    ap = argparse.ArgumentParser(description="Placement / contention test")
    ap.add_argument("--config", required=True, help="label, e.g. split or colocated")
    ap.add_argument("--small-url", required=True)
    ap.add_argument("--large-url", required=True)
    ap.add_argument("--concurrency", default="1,4,16,32")
    ap.add_argument("--requests", type=int, default=64, help="requests per level")
    ap.add_argument("--max-tokens", type=int, default=128)
    ap.add_argument("--shared-prefix", action="store_true")
    ap.add_argument("--out", default="data/placement")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    tag = f"{args.config}{'_prefix' if args.shared_prefix else ''}"
    rows = []
    print(f"config={tag}  small={args.small_url}  large={args.large_url}")
    print(f"{'conc':>5} {'model':>6} {'n':>4} {'p50 s':>8} {'p95 s':>8} {'mean s':>8} {'tok/s':>8}")

    # warm-up so the first level is not dominated by start-up effects
    call(args.small_url, SMALL_MODEL, "Hello", 4)
    call(args.large_url, LARGE_MODEL, "Hello", 4)

    for conc in [int(c) for c in args.concurrency.split(",")]:
        rng = random.Random(args.seed + conc)
        jobs = []
        for i in range(args.requests):
            which = "small" if i % 2 == 0 else "large"
            jobs.append((which, make_prompt(rng, args.shared_prefix)))
        t0 = time.perf_counter()
        results = []
        with cf.ThreadPoolExecutor(max_workers=conc) as pool:
            futs = {}
            for which, prompt in jobs:
                url = args.small_url if which == "small" else args.large_url
                model = SMALL_MODEL if which == "small" else LARGE_MODEL
                futs[pool.submit(call, url, model, prompt, args.max_tokens)] = which
            for f in cf.as_completed(futs):
                lat, toks = f.result()
                results.append((futs[f], lat, toks))
        wall = time.perf_counter() - t0
        for which in ("small", "large"):
            lats = [r[1] for r in results if r[0] == which]
            toks = sum(r[2] for r in results if r[0] == which)
            row = {"config": tag, "concurrency": conc, "model": which, "n": len(lats),
                   "p50_s": pct(lats, 0.5), "p95_s": pct(lats, 0.95),
                   "mean_s": statistics.mean(lats), "tokens_per_s": toks / wall,
                   "wall_s": wall}
            rows.append(row)
            print(f"{conc:>5} {which:>6} {len(lats):>4} {row['p50_s']:>8.2f} "
                  f"{row['p95_s']:>8.2f} {row['mean_s']:>8.2f} {row['tokens_per_s']:>8.1f}")

    path = os.path.join(args.out, f"placement_{tag}.csv")
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
