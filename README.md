# AgentQO Prototype

Reliability-aware **joint logical and physical** optimization of LLM-agent
workflows. Epistemic criticality (EC) is the value signal: spend GPU on nodes
whose errors actually move end-to-end quality, and account for the delay those
calls impose on everyone else sharing the GPU.

This repository has two layers:

1. **Measurement (H1–H4).** Can we label EC, predict it on unseen DAGs, and
   show that predicted-EC spend and two-sided GPU cost are real effects?
2. **Runtime (proposal §V).** An event-driven serving optimizer that co-selects
   a logical edit *e* and a physical plan *P* at each event:

   `max_{e,P} Q̂ − λ_L L̂ − λ_C Ĉ − λ_R R̂`

   Edits are constrained (width, loop, verifier, fidelity, cancel, no-op).
   Placement uses AgentIconq (`C_phys` = own latency + externality). KV
   residency follows `V_KV`; speculative branches stop when `I_b(t)` is low.

TRAIL (ICLR 2025) is a reference for *how* to evaluate a cheap recycled-embedding
predictor. It is not the optimizer. The GPU/vLLM hook is still a stub.

## Scientific protocol (read this)

- EC labels come from **fault injection**, never from the simulator's hidden
  importance vector.
- H2 splits are **leave-one-workflow-out**. A test DAG is unseen at training.
- H3 allocates by the **H2 predictor**, not by oracle EC. Oracle-EC is reported
  only as an upper bound.
- The mock embedding carries hidden importance + difficulty. Confidence tracks
  *local* correctness. That gap is the point of AgentQO.
- Every experiment writes a CSV and a PNG under `data/`.

H1–H3 are necessary but not sufficient. The proposal's claim is the **runtime
optimizer**, compared against FCFS-Fixed and FixedPlan-EC.

## Quick start

```bash
python -m pip install -e ".[all]"
pytest tests/ -q
python scripts/run_demo.py --quick
python scripts/run_agentqo.py --n-jobs 8 --n-gpus 2
```

Measurement suite (CPU, no GPU):

```bash
python scripts/run_h1_labeling.py --num-tasks 80
python scripts/run_h2_predictor.py --num-tasks 40
python scripts/run_h3_allocation.py --num-runs 30
python scripts/run_h4_agenticonq.py --n-batches 500
```

## Layout

```
agentqo/
  workflows/          DAG + library (math, multi-hop QA, self-consistency, refinement)
  backends/           ModelBackend protocol; vLLM stub for the GPU phase
  simulator/          Quality channel, MockBackend, multi-GPU interaction model
  executor.py         Run with overrides + descendant-only recompute
  labeling/           Fault-injection EC labels + per-task observations
  predictors/         EC GBT/MLP, feature views, AgentIconq
  policies/           Value-per-cost allocation (H3)
  runtime/            Joint logical/physical serving optimizer (proposal §V)
  experiments/        Suite, leakage-free splits, runtime scoring
  metrics/            Ranking, quality–cost, figures, CSV
scripts/              One script per hypothesis + run_agentqo.py
tests/                DAG, executor, quality-channel, AgentIconq, runtime
data/                 gitignored artifacts
```

## Multi-LLM / multi-GPU

`Fidelity` is a serving choice: `model_id`, `num_gpus`, `gpu_type`, plus cost
and error rate. Small = 7B-class on 1 GPU; large = 70B-class on 2 GPUs.
AgentIconq models contention on the same GPU and prefix reuse (negative
interaction). Cross-GPU pairs do not interact. Replace the interaction
simulator with vLLM traces in the GPU phase; labeling, predictors, and
policies do not change.

## Author

Shusmoy Chowdhury
