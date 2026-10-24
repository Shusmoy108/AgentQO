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

H4 options (any of --small-share, --prefix-tokens, --repeat-id switches on the
extended file tag; without them the output files and table are as before):
  --small-share F    fraction of small-model requests, shuffled from the seed
                     (default: the original strict small/large alternation)
  --ignore-eos       on by default; every request must return exactly
                     --max-tokens completion tokens, or the run fails
  --prefix-tokens N  every prompt starts with the same ~N-token block
                     (real count measured with the server's /tokenize)
  --repeat-id R      tag for repeated runs
  --prefix-metrics   read vLLM's prefix-cache counters before/after each level
Every run also writes placement_{tag}_requests.csv (one row per request).
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

PREFIX_SENTENCE = (
    "Team handbook, section {i}: every agent reads the problem twice, writes each "
    "intermediate quantity with its unit, checks the arithmetic once more, and keeps "
    "the final answer as a plain number without extra words. "
)


def make_prompt(rng: random.Random, shared: bool, prefix: str = "") -> str:
    a, b, c = rng.randint(12, 999), rng.randint(3, 99), rng.randint(5, 500)
    q = (f"A shop sells {a} items per day for {b} days, then returns {c} items. "
         f"How many items were sold in total? Explain briefly.")
    if prefix:
        return prefix + "\n" + q
    return (SHARED_PREFIX + q) if shared else q


def post_json(url: str, body: dict, timeout: float = 900) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def count_tokens(url: str, model: str, text: str) -> int:
    return int(post_json(url.rstrip("/") + "/tokenize", {"model": model, "prompt": text})["count"])


def build_prefix(url: str, model: str, n_tokens: int) -> tuple[str, int]:
    """Fixed text of about n_tokens tokens (first sentence count >= n_tokens)."""
    text, i = "", 0
    while True:
        text += PREFIX_SENTENCE.format(i=i)
        i += 1
        n = count_tokens(url, model, text)
        if n >= n_tokens:
            return text, n


def call(url: str, model: str, prompt: str, max_tokens: int,
         ignore_eos: bool = False) -> tuple[float, float, int, int]:
    body = {"model": model, "prompt": prompt, "max_tokens": max_tokens, "temperature": 0}
    if ignore_eos:
        body["ignore_eos"] = True
    t0 = time.perf_counter()
    out = post_json(url.rstrip("/") + "/v1/completions", body)
    t1 = time.perf_counter()
    usage = out.get("usage", {})
    return t0, t1, int(usage.get("completion_tokens", 0)), int(usage.get("prompt_tokens", 0))


def prefix_counters(url: str) -> dict:
    """Sum of vLLM's prefix-cache query/hit counters (tokens) at this server."""
    with urllib.request.urlopen(url.rstrip("/") + "/metrics", timeout=30) as r:
        text = r.read().decode()
    out = {"queries": 0.0, "hits": 0.0}
    for line in text.splitlines():
        for key, name in (("queries", "vllm:prefix_cache_queries_total"), ("hits", "vllm:prefix_cache_hits_total")):
            if line.startswith(name):
                out[key] += float(line.rsplit(" ", 1)[1])
    return out


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    k = max(0, min(len(xs) - 1, int(round(q * (len(xs) - 1)))))
    return xs[k]


def make_jobs(n: int, small_share, seed: int, conc: int):
    """Which model each request goes to, in submission order."""
    if small_share is None:  # original behaviour: strict alternation
        return ["small" if i % 2 == 0 else "large" for i in range(n)]
    n_small = int(round(n * small_share))
    order = ["small"] * n_small + ["large"] * (n - n_small)
    random.Random(seed * 1000 + conc).shuffle(order)
    return order


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
    ap.add_argument("--small-share", type=float, default=None,
                    help="fraction of small-model requests (default: strict alternation, i.e. 0.5)")
    ap.add_argument("--ignore-eos", action=argparse.BooleanOptionalAction, default=True,
                    help="generate exactly --max-tokens tokens per request (default on)")
    ap.add_argument("--prefix-tokens", type=int, default=0, help="shared prompt prefix of ~N tokens (0 = off)")
    ap.add_argument("--repeat-id", type=int, default=None)
    ap.add_argument("--pause", type=float, default=10.0, help="seconds between levels")
    ap.add_argument("--prefix-metrics", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    concs = [int(c) for c in args.concurrency.split(",")]
    extended = args.small_share is not None or args.prefix_tokens > 0 or args.repeat_id is not None
    tag = f"{args.config}{'_prefix' if args.shared_prefix else ''}"
    share = 0.5 if args.small_share is None else args.small_share
    if extended:
        tag += (f"_s{share:g}_t{args.max_tokens}_p{args.prefix_tokens}_r{args.repeat_id}"
                f"_c{'-'.join(map(str, concs))}")
    prefix, prefix_n = "", 0
    if args.prefix_tokens > 0:
        prefix, prefix_n = build_prefix(args.small_url, SMALL_MODEL, args.prefix_tokens)
    rows, req_rows, cache_rows = [], [], []
    print(f"config={tag}  small={args.small_url}  large={args.large_url}")
    if extended:
        print(f"small_share={share:g} max_tokens={args.max_tokens} ignore_eos={args.ignore_eos} "
              f"prefix_tokens={prefix_n} (requested {args.prefix_tokens}) repeat_id={args.repeat_id} seed={args.seed}")
    print(f"{'conc':>5} {'model':>6} {'n':>4} {'p50 s':>8} {'p95 s':>8} {'mean s':>8} {'tok/s':>8}")

    # warm-up so the first level is not dominated by start-up effects
    call(args.small_url, SMALL_MODEL, "Hello", 4)
    call(args.large_url, LARGE_MODEL, "Hello", 4)

    for li, conc in enumerate(concs):
        if li and args.pause > 0:
            time.sleep(args.pause)
        rng = random.Random(args.seed + conc)
        jobs = [(which, make_prompt(rng, args.shared_prefix, prefix))
                for which in make_jobs(args.requests, args.small_share, args.seed, conc)]
        before = ({w: prefix_counters(u) for w, u in (("small", args.small_url), ("large", args.large_url))}
                  if args.prefix_metrics else None)
        t0 = time.perf_counter()
        results = []
        with cf.ThreadPoolExecutor(max_workers=conc) as pool:
            futs = {}
            for which, prompt in jobs:
                url = args.small_url if which == "small" else args.large_url
                model = SMALL_MODEL if which == "small" else LARGE_MODEL
                futs[pool.submit(call, url, model, prompt, args.max_tokens, args.ignore_eos)] = which
            for f in cf.as_completed(futs):
                s, e, toks, ptoks = f.result()
                results.append((futs[f], e - s, toks, s - t0, e - t0, ptoks))
        wall = time.perf_counter() - t0
        if args.ignore_eos:
            short = [r for r in results if r[2] != args.max_tokens]
            if short:
                raise SystemExit(f"FAIL: --ignore-eos is on but {len(short)} request(s) at concurrency {conc} "
                                 f"returned completion_tokens != {args.max_tokens}: "
                                 f"{sorted({r[2] for r in short})}")
        if before is not None:
            for w, u in (("small", args.small_url), ("large", args.large_url)):
                a = prefix_counters(u)
                dq, dh = a["queries"] - before[w]["queries"], a["hits"] - before[w]["hits"]
                cache_rows.append({"concurrency": conc, "model": w, "query_tokens": dq, "hit_tokens": dh,
                                   "hit_rate": dh / dq if dq else float("nan")})
        for which, lat, toks, s, e, ptoks in results:
            req_rows.append({"config": args.config, "concurrency": conc, "small_share": share,
                             "max_tokens": args.max_tokens, "prefix_tokens": prefix_n,
                             "repeat_id": args.repeat_id, "seed": args.seed, "model": which,
                             "start_s": s, "end_s": e, "latency_s": lat,
                             "prompt_tokens": ptoks, "completion_tokens": toks, "level_wall_s": wall})
        for which in ("small", "large"):
            lats = [r[1] for r in results if r[0] == which]
            toks = sum(r[2] for r in results if r[0] == which)
            if not lats:
                continue
            row = {"config": tag, "concurrency": conc, "model": which, "n": len(lats),
                   "p50_s": pct(lats, 0.5), "p95_s": pct(lats, 0.95),
                   "mean_s": statistics.mean(lats), "tokens_per_s": toks / wall,
                   "wall_s": wall}
            rows.append(row)
            print(f"{conc:>5} {which:>6} {len(lats):>4} {row['p50_s']:>8.2f} "
                  f"{row['p95_s']:>8.2f} {row['mean_s']:>8.2f} {row['tokens_per_s']:>8.1f}", flush=True)
        if before is not None:
            for c in cache_rows[-2:]:
                print(f"      prefix cache {c['model']}: hit rate {c['hit_rate']:.3f} "
                      f"({c['hit_tokens']:.0f}/{c['query_tokens']:.0f} tokens)", flush=True)

    path = os.path.join(args.out, f"placement_{tag}.csv")
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    req_path = os.path.join(args.out, f"placement_{tag}_requests.csv")
    with open(req_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(req_rows[0]))
        w.writeheader()
        w.writerows(req_rows)
    if cache_rows:
        with open(os.path.join(args.out, f"placement_{tag}_prefix_cache.json"), "w") as fh:
            json.dump({"prefix_tokens": prefix_n, "levels": cache_rows}, fh, indent=1)
    print(f"\nwrote {path}")
    if extended:
        print(f"wrote {req_path}")


if __name__ == "__main__":
    main()
