#!/usr/bin/env python3
"""H4 P4 driver: run the real math workflow with K problems in flight and time it.

Uses the existing pieces unchanged: load_problems / build_backend / WORKFLOWS
from run_real_pipeline.py, make_plans (ec_top2) from run_real_h3.py, and
WorkflowExecutor. Endpoints come from VLLM_ENDPOINTS as usual.

Timing runs bypass the generation cache (every call goes to a server):

    AGENTQO_VERIFIER=passthrough python3 -u scripts/h4_workflow_load.py \
        --placement S --k 16 --repeat-id 0 --out data/h4/p4

--token-profile instead replays the same 64 problems FROM the cache (no
timing is reported) to record per-node completion tokens for the P4
simulation in h4_fit.py.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import json
import os
import statistics
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentqo.executor import WorkflowExecutor  # noqa: E402
from agentqo.tasks.real_task_model import RealTaskModel  # noqa: E402
from agentqo.workflows.dag import LARGE_FIDELITY  # noqa: E402
from scripts.run_real_h3 import make_plans  # noqa: E402
from scripts.run_real_pipeline import WORKFLOWS, build_backend, load_problems  # noqa: E402

C9_H1 = "data/vllm/h1_math_passthrough_n100/h1/math_reasoning_s3_ver/h1_summary.json"
C9_TRACES = "data/vllm/h3_eval_n200/h3_traces.json"
GPUS = {"S": 2, "C": 1, "CM": 1}


def pct(xs, q):
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round(q * (len(xs) - 1)))))
    return xs[k]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--placement", required=True, choices=list(GPUS))
    ap.add_argument("--k", type=int, default=16, help="problems in flight")
    ap.add_argument("--n-tasks", type=int, default=64)
    ap.add_argument("--repeat-id", type=int, default=0)
    ap.add_argument("--out", default="data/h4/p4")
    ap.add_argument("--h1-summary", default=C9_H1)
    ap.add_argument("--token-profile", default="", help="write per-node tokens from the CACHE to this JSON")
    ap.add_argument("--cache", default="data/cache/vllm.sqlite", help="only read with --token-profile")
    # what build_backend / load_problems expect (C9 settings)
    ap.add_argument("--backend", default="vllm")
    ap.add_argument("--split", default="eval")
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--allow-missing-logprobs", action="store_true")
    ap.add_argument("--probe", default="placeholder")
    ap.add_argument("--probe-model", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--probe-layer", type=int, default=None)
    ap.add_argument("--probe-pool", default="mean")
    args = ap.parse_args()
    if os.environ.get("AGENTQO_VERIFIER") != "passthrough":
        raise SystemExit("set AGENTQO_VERIFIER=passthrough (C9 setup)")

    problems = load_problems(args)
    backend = build_backend(args, problems)
    if not args.token_profile:
        backend.text_backend.cache = None  # every call is a real model call
    workflow = WORKFLOWS["math"][1]()
    task_model = RealTaskModel(problems)
    executor = WorkflowExecutor(backend, task_model)
    ec = {n: float(d["ec"]) for n, d in json.loads(Path(args.h1_summary).read_text())["by_node"].items()}
    plan = make_plans(workflow, ec)["ec_top2"]
    tasks = [task_model.generate_task(workflow, None) for _ in range(len(problems))]
    print(f"placement={args.placement} K={args.k} n={len(tasks)} repeat={args.repeat_id} "
          f"ec_top2 upgrades={sorted(plan.assignments)} cache={'ON (token profile only)' if args.token_profile else 'bypassed'} "
          f"endpoints={backend.text_backend.config.endpoints}", flush=True)

    t0 = time.perf_counter()

    def run(task):
        s = time.perf_counter()
        rec = executor.run_workflow(workflow, task, fidelity_plan=plan, seed=0)
        e = time.perf_counter()
        nodes = {}
        for nid, r in rec.node_results.items():
            if r.metadata.get("code_node"):
                continue
            nodes[nid] = {"fidelity": plan.get_fidelity(workflow.nodes[nid]).name,
                          "latency_s": float(r.metadata.get("latency_s") or 0.0),
                          "prompt_tokens": int(r.metadata.get("prompt_tokens") or 0),
                          "completion_tokens": int(r.metadata.get("completion_tokens") or 0),
                          "cache_hit": bool(r.metadata.get("cache_hit"))}
        return task, s - t0, e - t0, float(rec.final_quality), nodes

    with cf.ThreadPoolExecutor(max_workers=args.k) as pool:
        done = list(pool.map(run, tasks))
    wall = time.perf_counter() - t0

    if args.token_profile:
        prof = {"plan": sorted(plan.assignments), "per_problem": {t.task_id: nodes for t, _, _, _, nodes in done}}
        Path(args.token_profile).parent.mkdir(parents=True, exist_ok=True)
        json.dump(prof, open(args.token_profile, "w"), indent=1)
        hits = sum(n["cache_hit"] for *_, nodes in done for n in nodes.values())
        total = sum(len(nodes) for *_, nodes in done)
        print(f"token profile from cache: {hits}/{total} node calls were cache hits; wrote {args.token_profile}")
        return

    if any(n["cache_hit"] for *_, nodes in done for n in nodes.values()):
        raise SystemExit("FAIL: a cache hit occurred in a timing run")
    c9 = {t["task_id"]: t["correct"] for t in json.load(open(C9_TRACES))["ec_top2"]}
    rows = []
    for task, s, e, q, nodes in done:
        rows.append({"placement": args.placement, "k": args.k, "repeat_id": args.repeat_id, "task_id": task.task_id,
                     "start_s": s, "end_s": e, "latency_s": e - s,
                     "n_small": sum(n["fidelity"] != LARGE_FIDELITY.name for n in nodes.values()),
                     "n_large": sum(n["fidelity"] == LARGE_FIDELITY.name for n in nodes.values()),
                     "correct": q, "c9_correct": c9.get(task.task_id),
                     "completion_tokens": json.dumps({k: v["completion_tokens"] for k, v in nodes.items()}),
                     "node_latency_s": json.dumps({k: round(v["latency_s"], 4) for k, v in nodes.items()})})
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"p4_{args.placement}_k{args.k}_r{args.repeat_id}.csv"
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    lat = [r["latency_s"] for r in rows]
    match = np.mean([r["correct"] == r["c9_correct"] for r in rows])
    per_gpu_hour = len(rows) / (wall / 3600) / GPUS[args.placement]
    print(f"p50 e2e {pct(lat, 0.5):.2f} s  p95 e2e {pct(lat, 0.95):.2f} s  mean {statistics.mean(lat):.2f} s  "
          f"wall {wall:.1f} s  problems/GPU-hour {per_gpu_hour:.0f}  accuracy {np.mean([r['correct'] for r in rows]):.3f}  "
          f"match with C9 per-problem correctness {match:.3f}")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
