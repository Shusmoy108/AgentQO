#!/usr/bin/env python3
"""Real-model pipeline: tasks -> substitute labeling (H1) -> H2 -> H3.

Same script on the laptop and on Chameleon; only ``--backend`` and the
endpoint config change.

    python scripts/run_real_pipeline.py --backend fake --n-tasks 10
    VLLM_ENDPOINTS='{"small":"http://localhost:8001","large":"http://localhost:8002"}' \\
        python scripts/run_real_pipeline.py --backend vllm --n-tasks 200 --stage h1 --probe hf

Artifacts under ``--output-dir``: per-workflow H1 labels, traces,
substitution chains, role summary, absorption table, figures, then H2 and
H3 outputs, and a run config. Every run appends one entry to RESULTS.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentqo.backends.cache import GenerationCache
from agentqo.backends.composite import CompositeBackend
from agentqo.backends.probe import HFHiddenStateProbe, PlaceholderProbe
from agentqo.backends.vllm_http import VLLMHTTPBackend, VLLMHTTPConfig
from agentqo.experiments.suite import SuiteMember
from agentqo.labeling.ec_labeler import ECLabeler, LabelingResult, analyze_h1_results
from agentqo.metrics.figures import save_h1_histogram
from agentqo.metrics.io import append_results_entry, write_csv, write_json
from agentqo.tasks.datasets import dev_eval_split, load_gsm8k
from agentqo.tasks.prompts import build_prompt, code_output
from agentqo.tasks.real_task_model import RealTaskModel
from agentqo.workflows.library import (
    create_complex_workflow,
    create_math_reasoning_workflow,
    create_self_consistency_workflow,
)

WORKFLOWS = {
    "math": ("Math 3-step + verifier", lambda: create_math_reasoning_workflow(3, include_verifier=True)),
    "sc": ("Self-consistency k=3", lambda: create_self_consistency_workflow(3)),
    "complex": ("Complex + formatter", lambda: create_complex_workflow(2, 2)),
}


def build_backend(args, problems):
    config = VLLMHTTPConfig.from_env()
    config.temperature = 0.0          # every non-sampler node is greedy
    config.sampler_temperature = 0.7  # samplers vary through fixed seeds
    config.max_tokens = args.max_tokens
    config.allow_missing_logprobs = args.allow_missing_logprobs
    request_fn = None
    if args.backend == "fake":
        from agentqo.backends.fake_server import FakeServer

        # Per-node error rates; about 50% / 20% final-answer error for small / large.
        request_fn = FakeServer(problems, {config.small_model: 0.10, config.large_model: 0.03})
    text = VLLMHTTPBackend(config, request_fn=request_fn, prompt_fn=build_prompt,
                           code_fn=code_output, cache=GenerationCache(args.cache))
    return CompositeBackend(text, make_probe(args))


def make_probe(args):
    if args.probe == "hf":
        return HFHiddenStateProbe(args.probe_model, layer=args.probe_layer, pool=args.probe_pool)
    return PlaceholderProbe(64)


def load_problems(args) -> List[Dict[str, str]]:
    working = load_gsm8k(n=300, seed=0)
    split = dev_eval_split(working, n_dev=100, seed=0)
    pool = working if args.split == "all" else split[args.split]
    return pool[: args.n_tasks]


def _role_summary(res: LabelingResult, workflow) -> List[dict]:
    by_role: Dict[str, List[dict]] = {}
    for r in res.records:
        by_role.setdefault(r["role"], []).append(r)
    rows = []
    for role, recs in by_role.items():
        corr = [c for r in recs for c in r["corruptions"]]
        rows.append({
            "workflow": workflow.name,
            "role": role,
            "n": len(recs),
            "consequence": float(np.mean([r["consequence"] for r in recs])),
            "p_err": float(np.mean([r["p_err"] for r in recs])),
            "ec": float(np.mean([r["consequence"] * r["p_err"] for r in recs])),
            "absorbed_share": float(np.mean([not c["final_differs"] for c in corr])) if corr else 0.0,
        })
    return rows


def _absorption(res: LabelingResult, workflow) -> List[dict]:
    """Per corruption: did the final answer survive, and which node repaired it."""
    rows = []
    for r in res.records:
        for i, c in enumerate(r["corruptions"]):
            absorber = ""
            if not c["final_differs"]:
                for d in workflow.topological_order:
                    if d in c["descendants"] and c["descendants"][d] == r["descendants_plus"].get(d):
                        absorber = d
                        break
            rows.append({
                "workflow": workflow.name, "task_id": r["task_id"], "node_id": r["node_id"],
                "role": r["role"], "corruption": i, "strategy": c["strategy"],
                "key_differs": c["key_differs"], "final_differs": c["final_differs"],
                "absorbed": not c["final_differs"], "absorbed_by": absorber,
            })
    return rows


def write_h1_artifacts(out: Path, member: SuiteMember, res: LabelingResult) -> dict:
    wf = member.workflow
    wdir = out / "h1" / wf.name
    for t in res.traces:
        write_json(wdir / "traces" / f"{t['task_id']}.json", t)
    for r in res.records:
        write_json(wdir / "substitutions" / f"{r['task_id']}_{r['node_id']}.json", r)
    analysis = analyze_h1_results(res.labels, wf)
    write_csv(wdir / "h1_labels.csv", [
        {"node_id": nid, "role": wf.nodes[nid].role.value, **lab.to_dict()}
        for nid, lab in res.labels.items()
    ])
    write_csv(wdir / "role_summary.csv", _role_summary(res, wf))
    write_csv(wdir / "absorption.csv", _absorption(res, wf))
    save_h1_histogram(res.labels, wdir / "h1_consequence.png", title=f"H1: {member.display_name}")
    keyed = [c["key_differs"] for r in res.records for c in r["corruptions"] if c["key_differs"] is not None]
    finals = [c["final_differs"] for r in res.records for c in r["corruptions"] if c["key_differs"] is None]
    summary = {
        "h1_holds": analysis["h1_holds"],
        "range": analysis["statistics"].get("range"),
        "cv": analysis["statistics"].get("cv"),
        "smoke_test": analysis.get("smoke_test"),
        "key_change_rate": float(np.mean(keyed)) if keyed else None,
        "planner_final_change_rate": float(np.mean(finals)) if finals else None,
        "invariant_violations": sum(len(r["invariant_violations"]) for r in res.records),
        "baseline_accuracy": float(np.mean([t["final_quality"] for t in res.traces])),
        "by_node": {nid: {"consequence": lab.consequence_mean,
                          "ci": [lab.consequence_ci_low, lab.consequence_ci_high],
                          "p_err": lab.local_error_prob, "ec": lab.ec_score}
                    for nid, lab in res.labels.items()},
    }
    write_json(wdir / "h1_summary.json", summary)
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--backend", choices=["fake", "vllm"], default="fake")
    ap.add_argument("--n-tasks", type=int, default=10)
    ap.add_argument("--split", choices=["dev", "eval", "all"], default="dev")
    ap.add_argument("--workflows", default="math,sc,complex")
    ap.add_argument("--stage", choices=["all", "smoke", "h1", "h2", "h3"], default="all",
                    help="h2/h3 relabel from the cache first (no new calls if cached)")
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--cache", default="data/cache/generations.sqlite")
    ap.add_argument("--probe", choices=["placeholder", "hf"], default="placeholder")
    ap.add_argument("--probe-model", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--probe-layer", type=int, default=None)
    ap.add_argument("--probe-pool", choices=["mean", "last"], default="mean")
    ap.add_argument("--allow-placeholder", action="store_true",
                    help="let H2 run on placeholder embeddings (debugging only)")
    ap.add_argument("--allow-missing-logprobs", action="store_true")
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--corruptions", type=int, default=3)
    ap.add_argument("--k", type=int, default=5, help="p_err samples per node")
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--h3-runs", type=int, default=None, help="tasks per H3 budget (default n-tasks)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    out = Path(args.output_dir or f"data/real/{args.backend}")
    problems = load_problems(args)
    backend = build_backend(args, problems)
    write_json(out / "run_config.json", {**vars(args), "backend_info": backend.get_info(),
                                         "qids": [p["qid"] for p in problems]})
    members = []
    for key in args.workflows.split(","):
        display, make = WORKFLOWS[key.strip()]
        members.append(SuiteMember(workflow=make(), task_model=RealTaskModel(problems), display_name=display))

    if args.stage == "smoke":
        run_smoke(backend, members[0], problems)
        return

    # H1: substitute labeling (always; h2/h3 stages replay it from the cache).
    labeling: Dict[str, LabelingResult] = {}
    h1: Dict[str, dict] = {}
    for m in members:
        m.task_model.reset()
        labeler = ECLabeler(backend, m.task_model, mode="substitute", n_corruptions=args.corruptions,
                            k_samples=args.k, max_workers=args.workers)
        res = labeler.label_workflow(m.workflow, num_tasks=len(problems), base_seed=args.seed)
        labeling[m.workflow.name] = res
        h1[m.workflow.name] = write_h1_artifacts(out, m, res)
        s = h1[m.workflow.name]
        print(f"\nH1 {m.display_name}: holds={s['h1_holds']} range={s['range']:.3f} cv={s['cv']:.3f} "
              f"baseline_acc={s['baseline_accuracy']:.2f} key_change={s['key_change_rate']}")
        for nid, d in s["by_node"].items():
            print(f"  {nid:<13} consequence={d['consequence']:+.3f} "
                  f"[{d['ci'][0]:+.3f},{d['ci'][1]:+.3f}] p_err={d['p_err']:.2f} ec={d['ec']:+.3f}")
    print(f"\nHTTP calls: {backend.n_http_calls}  cache hits: {backend.cache.hits}  "
          f"misses: {backend.cache.misses}")

    h2 = h3 = None
    if args.stage in ("all", "h2", "h3"):
        if backend.probe.kind == "placeholder" and not args.allow_placeholder:
            print("\nH2/H3 skipped: embeddings are placeholders (hash of text). "
                  "Use --probe hf, or --allow-placeholder for a debugging run.")
        else:
            from scripts.run_h2_predictor import run_h2_experiment
            from scripts.run_h3_allocation import run_h3_experiment

            artifacts = run_h2_experiment(embedding_dim=backend.embedding_dim, output_dir=str(out / "h2"),
                                          base_seed=args.seed, suite=members, labeling_results=labeling)
            h2 = artifacts.analysis
            if args.stage in ("all", "h3"):
                for m in members:
                    m.task_model.reset()
                h3 = run_h3_experiment(
                    num_runs_per_budget=args.h3_runs or len(problems), embedding_dim=backend.embedding_dim,
                    output_dir=str(out / "h3"), base_seed=args.seed, suite=members,
                    h2_artifacts=artifacts, backend_factory=lambda tm: backend,
                )

    write_json(out / "pipeline_summary.json", {"h1": h1, "h2": h2, "h3": h3})
    append_results_entry(
        {"fake": "DRY", "vllm": "R-H1"}[args.backend],
        {"backend": args.backend, "n_tasks": len(problems), "split": args.split,
         "workflows": args.workflows, "probe": args.probe, "C": args.corruptions, "K": args.k},
        "; ".join(f"{wf}: H1 {'PASS' if s['h1_holds'] else 'FAIL'} range {s['range']:.3f} cv {s['cv']:.3f} "
                  f"key-change {s['key_change_rate']}" for wf, s in h1.items())
        + (f"; H2 holds {h2.get('h2_holds')}" if h2 else "; H2 not run")
        + (f"; H3 holds on any {h3.get('h3_holds_any')}" if h3 else "; H3 not run"),
        str(out / "h1" / "<workflow>" / "h1_consequence.png"),
        "Fake server: tests the pipeline only, never a result." if args.backend == "fake" else "",
    )
    print(f"\nArtifacts in {out}")


def run_smoke(backend, member, problems) -> None:
    """M1: text back, logprobs present, rerun served from cache."""
    wf = member.workflow
    from agentqo.workflows.dag import LARGE_FIDELITY, SMALL_FIDELITY

    node = wf.nodes[wf.topological_order[0]]  # root: needs no upstream inputs
    for fid in (SMALL_FIDELITY, LARGE_FIDELITY):
        for p in problems[:5]:
            task = member.task_model.generate_task(wf, None)
            ctx = {"task": task, "workflow": wf, "results": {}}
            r1 = backend.execute_node(node, {}, fid, ctx)
            r2 = backend.execute_node(node, {}, fid, ctx)
            print(f"{fid.name:<6} {task.task_id:<16} conf_src={r1.metadata['confidence_source']:<8} "
                  f"cache_hit_on_rerun={r2.metadata['cache_hit']} "
                  f"text={r1.output['text'][:60]!r}")
        member.task_model.reset()


if __name__ == "__main__":
    main()
