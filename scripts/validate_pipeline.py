#!/usr/bin/env python3
"""Validation checks V1-V9 (plan Section 13.2) plus the M3 extraction rate.

    python scripts/validate_pipeline.py --backend ollama --n-tasks 20   # gate M2 (+ M4)
    python scripts/validate_pipeline.py --backend ollama --n-tasks 50   # gate M3

Uses the same tasks, seed, and generation cache as run_real_pipeline.py, so
after a pipeline run on the same split the labeling here is served from the
cache. V1, V2, V4-V7 and M3 print PASS/FAIL and set the exit code. V3 and V9
need a person: they write files to read. V8 is informational below 200 tasks.
V10 needs the WP9 calibration run and is not checked here.
"""

from __future__ import annotations

import argparse
import random
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentqo.backends.base import NodeResult
from agentqo.experiments.suite import SuiteMember
from agentqo.labeling.ec_labeler import ECLabeler
from agentqo.metrics.io import write_csv, write_json
from agentqo.tasks.real_task_model import RealTaskModel, answer_node
from scripts.run_real_pipeline import WORKFLOWS, build_backend, load_problems

STRICT = re.compile(r"####\s*-?\$?\s*\d|\\boxed\{")


def label_all(backend, members, args):
    out = {}
    for m in members:
        m.task_model.reset()
        labeler = ECLabeler(backend, m.task_model, mode="substitute", n_corruptions=args.corruptions,
                            k_samples=args.k, max_workers=args.workers)
        out[m.workflow.name] = labeler.label_workflow(m.workflow, num_tasks=args.n_tasks, base_seed=args.seed)
    return out


def forced_quality(member, trace, text):
    """Quality after replacing the answer node's output in a traced run with ``text``."""
    wf, tm = member.workflow, member.task_model
    results = {nid: NodeResult(nid, n["output"], False, 0.0, np.zeros(1), 0.0, n["fidelity"])
               for nid, n in trace["nodes"].items()}
    a = answer_node(wf, results)
    results[a] = NodeResult(a, text, False, 0.0, np.zeros(1), 0.0, "")
    task = tm.generate_task(wf, None)
    task.ground_truth = trace["gold"]
    return tm.compute_quality(task, results, wf)


def gold_plus_one(gold: str) -> str:
    g = float(gold) + 1
    return str(int(g)) if g.is_integer() else repr(g)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--backend", choices=["fake", "ollama", "vllm"], default="fake")
    ap.add_argument("--n-tasks", type=int, default=20)
    ap.add_argument("--split", choices=["dev", "eval", "all"], default="dev")
    ap.add_argument("--workflows", default="math,sc,complex")
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--cache", default="data/cache/generations.sqlite")
    ap.add_argument("--allow-missing-logprobs", action="store_true")
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--corruptions", type=int, default=3)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    args.probe = "placeholder"  # generations and labels do not depend on the probe

    out = Path(args.output_dir or f"data/validate/{args.backend}")
    problems = load_problems(args)
    backend = build_backend(args, problems)
    members = [SuiteMember(workflow=WORKFLOWS[k.strip()][1](), task_model=RealTaskModel(problems),
                           display_name=WORKFLOWS[k.strip()][0]) for k in args.workflows.split(",")]
    by_name = {m.workflow.name: m for m in members}

    labeling = label_all(backend, members, args)
    checks = {}  # name -> (passed or None for manual/info, detail)

    # V1 / V2: the scorer reads the answer node and nothing else.
    v1 = [forced_quality(by_name[w], t, f"#### {t['gold']}") for w, r in labeling.items() for t in r.traces]
    v2 = [forced_quality(by_name[w], t, f"#### {gold_plus_one(t['gold'])}")
          for w, r in labeling.items() for t in r.traces]
    checks["V1 gold injection"] = (all(q == 1.0 for q in v1), f"{sum(q == 1.0 for q in v1)}/{len(v1)} score 1.0")
    checks["V2 wrong injection"] = (all(q == 0.0 for q in v2), f"{sum(q == 0.0 for q in v2)}/{len(v2)} score 0.0")

    # M3 and V3: answer-node outputs, strict format rate, and a sample to hand-check.
    answers = []
    for w, r in labeling.items():
        wf = by_name[w].workflow
        for t in r.traces:
            a = answer_node(wf, t["nodes"])
            answers.append({"workflow": w, "task_id": t["task_id"], "node": a, "gold": t["gold"],
                            "key": t["nodes"][a]["key"], "strict": bool(STRICT.search(t["nodes"][a]["output"])),
                            "output_tail": t["nodes"][a]["output"][-300:]})
    rate = float(np.mean([a["strict"] for a in answers]))
    checks["M3 extraction"] = (rate >= 0.95, f"{rate:.1%} of {len(answers)} answer outputs have #### or \\boxed")
    audit = random.Random(args.seed).sample(answers, min(50, len(answers)))
    write_csv(out / "v3_extraction_audit.csv", [{**a, "correct": ""} for a in audit])
    checks["V3 extraction audit"] = (None, f"fill 'correct' in {out / 'v3_extraction_audit.csv'} (need >=98%)")

    # V4: corruptions must change the key; V5: descendant-only recompute.
    keyed = [c["key_differs"] for r in labeling.values() for rec in r.records
             for c in rec["corruptions"] if c["key_differs"] is not None]
    kc = float(np.mean(keyed)) if keyed else 0.0
    checks["V4 corruption effectiveness"] = (kc >= 0.9, f"{kc:.1%} of {len(keyed)} keyed corruptions change the key")
    viol = sum(len(rec["invariant_violations"]) for r in labeling.values() for rec in r.records)
    checks["V5 isolation invariant"] = (viol == 0, f"{viol} violations")

    # V6: relabel from the cache.
    calls_before = backend.n_http_calls
    again = label_all(backend, members, args)
    same = all(
        {n: l.to_dict() for n, l in labeling[w].labels.items()} == {n: l.to_dict() for n, l in again[w].labels.items()}
        for w in labeling)
    new_calls = backend.n_http_calls - calls_before
    checks["V6 determinism"] = (same and new_calls == 0, f"labels identical={same}, new HTTP calls={new_calls}")

    # V7: leakage guard.
    rc = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_no_leakage.py"],
                        cwd=Path(__file__).resolve().parent.parent, capture_output=True, text=True)
    checks["V7 leakage"] = (rc.returncode == 0, rc.stdout.strip().splitlines()[-1] if rc.stdout.strip() else rc.stderr[-200:])

    # V8: per-node consequence on two halves of the tasks.
    halves = [[], []]
    for w, r in labeling.items():
        ids = [t["task_id"] for t in r.traces]
        first = set(ids[: len(ids) // 2])
        for nid in r.labels:
            for h, keep in enumerate((lambda t: t in first, lambda t: t not in first)):
                vals = [rec["consequence"] for rec in r.records if rec["node_id"] == nid and keep(rec["task_id"])]
                halves[h].append(np.mean(vals) if vals else 0.0)
    rho = float(spearmanr(*halves).statistic) if len(halves[0]) > 2 else float("nan")
    v8_ok = rho >= 0.6
    checks["V8 label stability"] = (v8_ok if args.n_tasks >= 200 else None,
                                    f"Spearman {rho:.2f} over {len(halves[0])} nodes (target >=0.6; gated at 200 tasks)")

    # V9: ten substitution chains to read end to end.
    recs = [rec for r in labeling.values() for rec in r.records]
    spot = random.Random(args.seed).sample(recs, min(10, len(recs)))
    write_json(out / "v9_spot_check.json", spot)
    checks["V9 human spot check"] = (None, f"read {out / 'v9_spot_check.json'}")

    print()
    for name, (ok, detail) in checks.items():
        tag = {True: "PASS", False: "FAIL", None: "READ" if name[:2] in ("V3", "V9") else "INFO"}[ok]
        print(f"{tag:<5} {name:<30} {detail}")
    write_json(out / "validation.json", {
        "backend": args.backend, "n_tasks": args.n_tasks, "split": args.split, "workflows": args.workflows,
        "backend_info": backend.get_info(),
        "checks": {n: {"passed": ok, "detail": d} for n, (ok, d) in checks.items()},
    })
    print(f"\nWrote {out}")
    sys.exit(1 if any(ok is False for ok, _ in checks.values()) else 0)


if __name__ == "__main__":
    main()
