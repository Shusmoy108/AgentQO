#!/usr/bin/env python3
"""M6: run plans against the live servers under one placement and time them.

Timing bypasses the generation cache. Placement is what the servers already
are; this script only labels it. Endpoints come from VLLM_ENDPOINTS.

    python3 scripts/v2/run_placement.py --placement shared --plans all_small,only_verifier \
        --vm gpu_a=local --vm gpu_b=cc@10.0.0.2 --output-dir results/v2/P5/shared
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import subprocess
import sys
import time
from pathlib import Path
from typing import List

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agentqo.executor import FidelityPlan, WorkflowExecutor  # noqa: E402
from agentqo.metrics.io import args_config, mark_done, read_csv, resolve_output_dir, write_csv, write_json  # noqa: E402
from agentqo.policies.v2_rules import parse_plan_name  # noqa: E402
from agentqo.tasks.real_task_model import RealTaskModel  # noqa: E402
from agentqo.workflows.dag import LARGE_FIDELITY, SMALL_FIDELITY  # noqa: E402
from scripts.h4_fit import pct  # noqa: E402
from scripts.run_real_pipeline import WORKFLOWS, build_backend, load_problems  # noqa: E402

SMI = ["nvidia-smi", "--query-gpu=timestamp,power.draw,utilization.gpu,memory.used", "--format=csv", "-l", "1"]


class PowerLoggers:
    """One background nvidia-smi per VM (name=local or name=ssh_target), writing power_<name>.csv."""

    def __init__(self, vms: List[str], out: Path, smi: List[str] = SMI) -> None:
        self.procs, self.problems = {}, []
        for vm in vms:
            name, _, target = vm.partition("=")
            cmd = smi if target in ("", "local") else ["ssh", "-o", "BatchMode=yes", target, *smi]
            fh = (out / f"power_{name}.csv").open("a")
            try:
                self.procs[name] = (subprocess.Popen(cmd, stdout=fh, stderr=subprocess.PIPE, text=True), fh)
            except OSError as exc:
                fh.close()
                self._problem(f"{name}: cannot start {cmd[0]}: {exc}")

    def _problem(self, msg: str) -> None:
        self.problems.append(msg)
        print(f"WARNING: power log {msg}", flush=True)

    def check(self) -> None:
        """A logger that already exited means power data are missing; say so while it can be fixed."""
        for name, (proc, _) in self.procs.items():
            if proc.poll() is not None and not any(p.startswith(name + ":") for p in self.problems):
                self._problem(f"{name}: exited early with code {proc.returncode}: {proc.stderr.read()[:200]}")

    def stop(self) -> None:
        self.check()
        for proc, fh in self.procs.values():
            proc.terminate()
            proc.wait(timeout=10)
            fh.close()


def run_one(workflow, problems, executor, task_model, plan, k: int):
    task_model.reset()
    tasks = [task_model.generate_task(workflow, None) for _ in problems]
    t0 = time.perf_counter()

    def run(task):
        start = time.perf_counter()
        rec = executor.run_workflow(workflow, task, fidelity_plan=plan, seed=0)
        return task, start - t0, time.perf_counter() - t0, rec

    with cf.ThreadPoolExecutor(max_workers=k) as pool:
        done = list(pool.map(run, tasks))
    return done, time.perf_counter() - t0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--placement", required=True, choices=["separate", "shared", "shared_mps"])
    ap.add_argument("--plans", required=True, help="comma list of plan names, as in h3_plans.csv")
    ap.add_argument("--workflow", default="math", choices=list(WORKFLOWS))
    ap.add_argument("--dataset", default="gsm8k", choices=["gsm8k", "hotpotqa"])
    ap.add_argument("--split", default="eval")
    ap.add_argument("--n-tasks", type=int, default=64)
    ap.add_argument("--k", type=int, default=16, help="problems in flight")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--vm", action="append", default=[], metavar="NAME=TARGET",
                    help="log nvidia-smi on this VM; TARGET is local or an ssh target (repeatable)")
    ap.add_argument("--output-dir", default="results/v2/placement")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backend", default="vllm", choices=["fake", "ollama", "vllm"])
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--allow-missing-logprobs", action="store_true")
    ap.add_argument("--cache", default=":memory:", help="never used for timing; build_backend needs a value")
    ap.add_argument("--probe", default="placeholder")
    ap.add_argument("--probe-model", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--probe-layer", type=int, default=None)
    ap.add_argument("--probe-pool", default="mean")
    args = ap.parse_args()

    workflow = WORKFLOWS[args.workflow][1]()
    topo = list(workflow.topological_order)
    plans = {name: parse_plan_name(name, topo) for name in args.plans.split(",")}
    out, finished = resolve_output_dir(args.output_dir, args_config(args), create=not args.dry_run)
    runs = [(n, r) for n in plans for r in range(args.repeats)]
    if args.dry_run:
        print(f"would run {len(runs)} timing runs ({len(plans)} plans x {args.repeats} repeats) under {args.placement}, "
              f"K={args.k}, n={args.n_tasks}, into {out}; power logs: {args.vm or 'none'}")
        return
    if finished:
        print(f"already finished: {out}")
        return

    problems = load_problems(args)
    backend = build_backend(args, problems)
    backend.text_backend.cache = None  # every call is a real model call
    task_model = RealTaskModel(problems, dataset=args.dataset)
    executor = WorkflowExecutor(backend, task_model)
    power = PowerLoggers(args.vm, out)
    try:
        for name, repeat in runs:
            path = out / f"run_{name}_r{repeat}.csv"
            if path.exists():
                print(f"skip {path.name}: already written", flush=True)
                continue
            plan = FidelityPlan(assignments={n: LARGE_FIDELITY for n in plans[name]}, default_fidelity=SMALL_FIDELITY)
            done, wall = run_one(workflow, problems, executor, task_model, plan, args.k)
            rows, calls = [], []
            for task, s, e, rec in done:
                nodes = {n: r for n, r in rec.node_results.items() if not r.metadata.get("code_node")}
                if any(r.metadata.get("cache_hit") for r in nodes.values()):
                    raise SystemExit("FAIL: a cache hit occurred in a timing run")
                rows.append({"plan": name, "placement": args.placement, "k": args.k, "repeat": repeat,
                             "task_id": task.task_id, "start_s": s, "end_s": e, "latency_s": e - s,
                             "correct": float(rec.final_quality), "wall_s": wall})
                calls += [{"plan": name, "task_id": task.task_id, "node_id": n, "model": r.metadata.get("model"),
                           "fidelity": r.fidelity_used, "prompt_tokens": r.metadata.get("prompt_tokens", 0),
                           "completion_tokens": r.metadata.get("completion_tokens", 0),
                           "latency_s": r.metadata.get("latency_s", 0.0), "repeat": repeat}
                          for n, r in nodes.items()]
            # Calls first: the run file is the resume marker, so it must land last.
            write_csv(out / f"calls_{name}_r{repeat}.csv", calls)
            write_csv(path, rows)
            lat = [r["latency_s"] for r in rows]
            print(f"{name} r{repeat}: p50 {pct(lat, .5):.2f}s p95 {pct(lat, .95):.2f}s wall {wall:.1f}s", flush=True)
            power.check()
    finally:
        power.stop()

    summary, all_calls = [], []
    for name, repeat in runs:
        rows = read_csv(out / f"run_{name}_r{repeat}.csv")
        all_calls += read_csv(out / f"calls_{name}_r{repeat}.csv")
        lat = [float(r["latency_s"]) for r in rows]
        wall = float(rows[0]["wall_s"])
        summary.append({"plan": name, "placement": args.placement, "k": args.k, "repeat": repeat, "n": len(rows),
                        "p50_s": pct(lat, .5), "p95_s": pct(lat, .95), "p99_s": pct(lat, .99),
                        "throughput_per_s": len(rows) / wall if wall else float("nan"),
                        "accuracy": float(np.mean([float(r["correct"]) for r in rows]))})
    write_csv(out / "placement_summary.csv", summary)
    write_csv(out / "placement_calls.csv", all_calls)
    write_json(out / "placement_status.json", {"power_problems": power.problems, "vms": args.vm})
    mark_done(out)
    print(f"wrote {out}/placement_summary.csv")


if __name__ == "__main__":
    main()
