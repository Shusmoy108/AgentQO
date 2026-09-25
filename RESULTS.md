# AgentQO Results

## Environment
- Commit:
- Chameleon site / node type / GPU / driver / CUDA:
- vLLM version:
- Models (small / large / probe):
- SU used this phase (see ledger):

## Gate summary
| Gate | Result | Key number (95% CI) | n |
|---|---|---|---|
| CAL | | | |
| H1 | | | |
| H2 | | | |
| H3 | | | |
| H4 | | | |
| RT | | | |

## SU ledger (hard cap 1,000)
| Date | Hardware | Hours | SU | Cumulative | What ran |
|---|---|---|---|---|---|

## Per-experiment entries

### S-H3 2026-09-24
- Config: num_runs=30, quick=False, seed=42, oracle=True, label_tasks=30
- Result: H3 holds on 1/1 held-out workflows. AUC diffs (95% paired bootstrap CI): complex_r2_s2_ver: AgentQO - Confidence +1.554 [+0.844, +2.226]; AgentQO - Uniform +1.461 [+0.570, +2.356]; Oracle-EC - Confidence +1.914 [+1.061, +2.869]; Oracle-EC - Uniform +1.821 [+0.741, +2.933]; Oracle-EC - AgentQO +0.360 [-0.210, +0.941]; bottleneck = none: predicted EC beats confidence and uniform (CI excludes 0)
- Figure: data/h3/h3_quality_cost_<workflow>.png
- Interpretation: Bottleneck per workflow as listed. 'predictor' means oracle EC wins but predicted EC does not, so improve H2 before touching the allocator; 'allocator' means even oracle EC loses, so check fidelity gap and budget granularity.
- Changes made since last run and why: 

### S-RT 2026-09-24
- Config: ec_source=predicted, seeds=5, loads=low,med,high, n_jobs=8, n_gpus=2
- Result: AgentQO Q/GPU-hour above FCFS (paired CI excludes 0) in 6/12 cells; quality below FCFS (CI excludes 0) in 9/12 cells. Table: data/agentqo_predicted/agentqo_runtime_summary.csv
- Figure: data/agentqo_predicted/agentqo_pareto.png
- Interpretation: Simulated clock and GPU cost; efficiency wins that come with a quality loss are not wins under the WP15 criterion (accuracy within 2 points of FCFS).
- Changes made since last run and why: 

### S-RT 2026-09-24
- Config: ec_source=structure, seeds=5, loads=low,med,high, n_jobs=8, n_gpus=2
- Result: AgentQO Q/GPU-hour above FCFS (paired CI excludes 0) in 6/12 cells; quality below FCFS (CI excludes 0) in 9/12 cells. Table: data/agentqo_structure/agentqo_runtime_summary.csv
- Figure: data/agentqo_structure/agentqo_pareto.png
- Interpretation: Simulated clock and GPU cost; efficiency wins that come with a quality loss are not wins under the WP15 criterion (accuracy within 2 points of FCFS).
- Changes made since last run and why: 

### S-RT 2026-09-24
- Config: ec_source=oracle, seeds=5, loads=low,med,high, n_jobs=8, n_gpus=2
- Result: AgentQO Q/GPU-hour above FCFS (paired CI excludes 0) in 6/12 cells; quality below FCFS (CI excludes 0) in 9/12 cells. Table: data/agentqo_oracle/agentqo_runtime_summary.csv
- Figure: data/agentqo_oracle/agentqo_pareto.png
- Interpretation: Simulated clock and GPU cost; efficiency wins that come with a quality loss are not wins under the WP15 criterion (accuracy within 2 points of FCFS).
- Changes made since last run and why: 

### S-H2 2026-09-24
- Config: embedding_signal=hidden, num_tasks=40, quick=False, seed=42
- Result: mean LOWO Spearman: AgentQO 0.354, Structure-Only 0.384, Confidence-Only -0.002, Structure+Noise 0.329; H2 holds: False; beats Structure+Noise control: True
- Figure: data/h2/h2_spearman.png
- Interpretation: Mock embeddings carry hidden importance by construction; compare with S-CIRC.
- Changes made since last run and why: 

### S-CIRC 2026-09-24
- Config: embedding_signal=none, num_tasks=40, quick=False, seed=42
- Result: mean LOWO Spearman: AgentQO 0.334, Structure-Only 0.384, Confidence-Only -0.002, Structure+Noise 0.330; H2 holds: False; beats Structure+Noise control: True
- Figure: data/h2_noise/h2_spearman.png
- Interpretation: With noise embeddings, AgentQO should fall to about structure-only. If it does, the sim H2 gain comes from the embedding signal and real hidden states must carry it.
- Changes made since last run and why: 

### S-RT note 2026-09-24
- Config: the three S-RT runs above differ only in `--ec-source`.
- Result: AgentQO's per-cell quality, completion, and edit counts are almost identical across structure, predicted, and oracle EC. FixedPlan-EC does change with the source.
- Interpretation: the joint optimizer's edits do not depend on the EC ranking, so better EC cannot help AgentQO until its edit scores respond to EC (Section 9, "Runtime: fast but lower accuracy"). On self-consistency, AgentQO makes about 250 edits per episode and loses quality. That looks like add/cancel thrashing to fix before WP15. The runtime's speculative stopping also reads `NodeResult.correctness` (ground truth), which a real runtime cannot see; fix in WP13.
- Changes made since last run and why: none (not tuned).

### S-CIRC note 2026-09-24
- Config: S-H2 vs S-CIRC above, after the labeling seed fix.
- Result: noise embeddings give AgentQO 0.334, the same as the Structure+Noise control at 0.330, so the circularity check behaves as designed. Hidden-signal embeddings add about 0.02 (0.354), and AgentQO is below Structure-Only (0.384). **Sim H2 FAILS.**
- Interpretation: the earlier sim H2 PASS (0.49 vs 0.30) was inflated by leakage. Every workflow was labeled with the same base seed, so task *i* (difficulty, RNG stream, and therefore node embeddings) was identical across workflows, and the embedding acted as a task ID shared across LOWO folds. Structure-only is the real bar. The mock embedding's hidden signal is too weak to beat it, and whether real hidden states can is the open question for WP11.
- Changes made since last run and why: `ECLabeler.label_workflow` now mixes the workflow name into the task seed (guarded by `tests/test_label_seeds.py`), and H2 reports a Structure+Noise control. The pass thresholds did not change.

### DRY 2026-09-25
- Config: backend=fake, n_tasks=10, split=dev, workflows=math,sc,complex, probe=placeholder, C=3, K=5
- Result: math_reasoning_s3_ver: H1 FAIL range 0.600 cv 0.462 key-change 1.0; self_consistency_k3: H1 PASS range 0.833 cv 0.759 key-change 1.0; complex_r2_s2_ver: H1 FAIL range 0.767 cv 0.629 key-change 1.0; H2 not run; H3 not run
- Figure: data/real/fake/h1/<workflow>/h1_consequence.png
- Interpretation: Fake server: tests the pipeline only, never a result.
- Changes made since last run and why: 

### DRY 2026-09-25
- Config: backend=fake, n_tasks=10, split=dev, workflows=math,sc,complex, probe=hf, C=3, K=5
- Result: math_reasoning_s3_ver: H1 FAIL range 0.600 cv 0.462 key-change 1.0; self_consistency_k3: H1 PASS range 0.833 cv 0.759 key-change 1.0; complex_r2_s2_ver: H1 FAIL range 0.767 cv 0.629 key-change 1.0; H2 holds False; H3 holds on any False
- Figure: data/real/fake_hfprobe/h1/<workflow>/h1_consequence.png
- Interpretation: Fake server: tests the pipeline only, never a result.
- Changes made since last run and why: 
