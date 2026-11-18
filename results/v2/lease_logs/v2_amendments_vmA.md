# AgentQO v2, Lease 1: amendments to the pre-registration

Committed: 2026-11-07 16:10:08 UTC (the commit carrying this line is the amendment's registration).
Pre-registration: `prereg/v2_lease1.md`, commit `9f297bdda489180b3922e00080be8f3786a02b68`
(2026-11-07 09:57:34 UTC), unchanged.
Lease starts: Nov 16, 12:00 UTC. Every amendment below is made before any lease data exist.

## Amendments (text as given)

A1  H1c replaced: "Skipping Q+ reruns where the small and large output keys agree changes no
    agent's UV by more than 0.02 and no top-2 agent or budget-1/2 pick of confident_uv. On Qwen
    1.5B/7B math it uses at most 50% of the full Q+ reruns." Reason: the original 1/5 target
    was set without accounting for the planner, which can never be skipped; 50% is based on
    Session 1, where 32% of (agent, problem) pairs disagreed on Qwen math.
A2  H3b replaced: "Joint search has strictly higher hypervolume than the two-step baseline in at
    least 2 of the settings with placement data, and for at least one (cost limit, p95 latency
    limit) pair the two-step choice is at least 2 points less accurate than the joint choice."
    Reason: the original wording cannot fail (the two-step plans are a subset).
A3  H4b replaced: "Ranking the 64 math plans by measured GPU-time cost differs from ranking
    them by the 1-vs-4 cost units (Kendall tau below 0.9) in at least one setting." Reason: the
    original wording is fixed by the price table (20x) and is not an empirical test.
A4  H6 narrowed: one pre-specified rule: route agent v to the large model when the K = 5 small
    samples are not unanimous; tested only for the agent chosen by confident_uv at budget 1 in
    each setting. All other rules and thresholds are reported as exploratory.
A5  HotpotQA fixes (FIX 1) and the disagree-only definition (FIX 2) are bug fixes made before
    any lease data; the HotpotQA dry-run numbers are void.
A6  Exploratory, not pre-registered: E1 quantization ablation, E2 extra placement concurrency
    levels (see the lease prompt).
A7  GPU cost definition fixed: GPU cost is gpu_usd_throughput = GPUs reserved for the placement
    (separate 2, shared and shared_mps 1) x wall-clock seconds of the run / problems completed
    x gpu_hour_usd / 3600, measured in P5 placement runs. For quality phases it is estimated
    from each plan's token counts and the tokens/s measured in P5 for each model and placement,
    and labelled "estimated". The per-call latency price is kept as gpu_usd_latency for
    comparison only. gpu_usd_throughput is the cost in the Pareto search (H3a, A2), in H4a and
    in A3. Reason: per-call latency x GPU price overcounts GPU time when 32 requests share the
    GPU in a batch; this is a definition fix made before any lease data.
A8  Sample sizes (FIX 4): Qwen 1.5B/7B math labels 200 (the 100 Session 1 dev problems + 100
    new, disjoint from eval); Qwen 3B/14B math labels 200; Granite labels 200 (a subset of the
    Session 1 LABEL 500). HotpotQA: label 200, eval 400 (the frozen split allows 400). Reason:
    Session 1 showed 100 labels are too noisy when agents are close (Granite).
A9  Provenance (FIX 3): every phase records the full commit of the code run and a dirty flag;
    a lease phase does not start from a dirty working tree. Procedure only; no hypothesis changes.

## How each amendment is measured (the code's reading of the text above)

| Id | Reading | Output |
|---|---|---|
| A1 | "Full Q+ reruns" = (agent, problem) pairs where the agent has descendants. A Q+ rerun is skipped only when the small and large output keys at the agent are equal; agents without a comparable key (planner) are never skipped. UV change = abs(UV full - UV disagree-only) per agent. Top-2 = the two highest-UV agents. confident_uv picks at budgets 1 and 2 from each labels file. | `h1c.json` (`a1_*`) |
| A2 | "Settings with placement data" = settings whose plan costs use P5 throughput (Qwen 1.5B/7B math and HotpotQA). Limits: every pair of deciles 10..100 of the candidates' cost and p95 latency; pairs where the two-step baseline has no feasible point are left out. Choice = highest accuracy within both limits. | `pareto_summary.json` (`a2_*`), `limit_gaps.csv` |
| A3 | Kendall tau-b over the 64 plans between gpu_usd_throughput (estimated, per placement) and cost units; holds if below 0.9 for at least one placement in at least one setting. gpu_usd_latency is reported next to it. | `cost_summary.json` (`a3_kendall_tau_*`) |
| A4 | "Not unanimous" = the stored small samples' keys are not all equal (rule `samples_disagree`). Matching as in H6: accuracy >= fixed plan - 0.01 and lower API cost. The planner's samples are final answers after its descendants and the labeler draws 3 of them (Session 1 cap), not 5; if confident_uv picks the planner, K = 3 for that test. | `routing_summary.json` (`a4_*`), `routing.csv` (`primary`) |
| A5 | HotpotQA dry-run outputs from before FIX 1 are not used anywhere. | - |
| A7 | separate: 2 GPUs held for the busier model's output tokens / its P5 tokens/s; shared and shared_mps: 1 GPU for both models' time. Tokens/s per (placement, model) = highest over P5 runs of output tokens / run wall time. HotpotQA reuses the math P5 rates of the same models. Settings with no P5 run for their models (Qwen 3B/14B, Granite) fall back to gpu_usd_latency, and their outputs say so. | `plan_costs.csv`, `placement_costs.csv`, `cost_summary.json` |
| A8 | GSM8K label 200 = the Session 1 LABEL order (100 dev, then the Session 1 F4 extra problems); eval 400 = Session 1 EVAL 200 + the first 200 of Session 1 EVAL2. HotpotQA ids are in `data/splits/hotpot_v2.json`. | `agentqo/tasks/datasets.py`, `data/splits/hotpot_v2.json` |

## Amendments added 2026-11-07 18:14:08 UTC

Committed with this section (the commit carrying this timestamp registers it). A1-A9
above are unchanged; A1 stays registered as written.

A10 New hypothesis (A1 is not edited): "H1c-b: skipping Q+ reruns where the small and large
    output keys agree changes no top-2 agent and no confident_uv budget-1/2 pick, in every
    setting." Added on 2026-11-07, after the Ollama dry run showed that A1's UV-equality
    condition fails because equal keys do not imply equal downstream text: 6 of 47 skipped
    reruns changed correctness (20 Qwen 1.5B/7B math problems, max UV change 0.10).
E3  Exploratory: an exact skip variant that skips only when the small and large outputs are
    identical after whitespace normalisation; its rerun share and UV error are reported next
    to the key-based rule.
E4  Exploratory: a logit-additive plan estimator (sum of single-agent changes in log-odds,
    with accuracy clipped to [0.01, 0.99]) next to additive, multiplicative and pairwise.
    The multiplicative proxy is unstable when baseline accuracy is low: in the HotpotQA dry
    run (all_small accuracy 0.10) its MAE was 0.28 over all plans (0.35 held out).
A11 Definition refinement of A7, before lease data: GPU time per call = a_m x prompt_tokens +
    b_m x completion_tokens, with a_m, b_m fitted per model and placement from P5 per-call
    data (prefill and decode rates), instead of output tokens only. P5 adds calibration runs
    so every model and task has measured rates: Granite 2B/8B math, HotpotQA Qwen 1.5B/7B and
    Qwen 3B/14B math, each all_small and all_large, separate and shared, K = 16, 64 problems.
    No cost in Pareto or A3 may fall back to per-call latency without a "fallback" flag in the
    output; P6 hypotheses.md says which costs are measured and which are fallback.
L1  Lease commit: the final pre-lease v2-dev commit is tagged v2-lease1-start and all lease
    phases run at that commit. Any code change during the lease is a new commit, logged here
    as a lease-time deviation (id, UTC time, reason, affected phases), and the affected
    phases are rerun. The driver refuses a vllm phase off the tag unless V2_DEVIATION names
    a deviation id that appears in this file.

### How these are measured

| Id | Reading | Output |
|---|---|---|
| A10 | Top-2 = the two highest-UV agents; confident_uv picks at budgets 1 and 2; full labels against --disagree-only labels, in each of the four settings. | `h1c.json` (`top2_same`, `a1_confident_uv_same`) |
| E3 | Computed offline from the full-mode labels: Q+ taken as the baseline wherever the small and large outputs at the agent are identical after collapsing whitespace (planner included). UV error = abs(UV with skips - full UV) per agent. The key rule is computed the same way, next to it. | `h1c.json` (`e3_skip_variants`) |
| E4 | Same held-out plans and MAE as H2a. | `estimator_errors.csv` (`logit_additive`) |
| A11 | Shape: non-negative least squares of per-call latency on prompt and completion tokens, per (model, placement). Scale: the calls of each P5 run add up to the GPU time the model held (separate: the run's wall time; shared: the wall time split by alpha/beta-weighted work), one scale per (model, placement). Plan time per tier = a_m x prompt + b_m x completion; separate = 2 GPUs x the busier tier; shared = 1 GPU x both. Rates are pooled over tasks per model. Calibration runs use 3 repeats, like the main sweep. A placement or model without rates (e.g. shared_mps outside the Qwen 1.5B/7B math sweep) gets the latency price with basis `fallback_latency`. | `token_rates.csv`, `plan_costs.csv` (`gpu_cost_basis_*`), `cost_summary.json` (`a3_basis_*`), `hypotheses.md` |

Correction to the request behind A11: Qwen 3B/14B was not in P5 (only Qwen 1.5B/7B math
was), so it is added as a calibration set like the other two.

## Amendment added 2026-11-07 21:59:58 UTC

Committed with this section (the commit carrying this timestamp registers it), before any
q4 data exist. A1-A11 and L1 above are unchanged.

A12 "Additional setting q4: Qwen2.5 1.5B/7B 4-bit via Ollama, math chain and HotpotQA chain,
    200 label + 200 eval problems each (math eval = first 200 of eval_ext; HotpotQA eval = first 200
    of the frozen eval list in data/splits/hotpot_v2.json). Same hypotheses and analyses as the
    vLLM settings, except placement (H3) and throughput GPU cost, which cannot be tested on the Mac.
    Reason: test whether findings hold under quantization and add statistical power before the
    lease. Reported as a separate 4-bit setting, never pooled with vLLM data."

### How A12 is measured

| Id | Reading | Output |
|---|---|---|
| A12 | Runs on branch v2-q4 = tag v2-lease1-start + this amendment, no code change, driven by `scripts/v2/run_q4_all.sh`. Models: Ollama `qwen2.5:1.5b-instruct` and `qwen2.5:7b-instruct` (Q4_K_M). Own SQLite cache `data/cache/v2_q4.sqlite` (no calls reused from the dry runs). Not testable on the Mac and marked so in `hypotheses.md`: H3a, A2, H3c (placement), A3 and H4a (need GPU throughput cost). Costs are API prices and token counts only. | `results/v2_q4/`, branch v2-q4 |

## Amendment added 2026-11-12 06:52:05 UTC

Committed with this section (the commit carrying this timestamp registers it), before any
hotpot_chain_isolated or Granite HotpotQA data exist. A1-A12 and L1 above are unchanged.

A13 "New workflow hotpot_chain_isolated: same as hotpot_chain, except the aggregator and verifier see
    only the question and the hop outputs (no paragraphs). Prediction: hop_1 and/or hop_2 have upgrade
    value with 95% CI above 0, and the structural rule's regret at budgets 1-2 is smaller than in
    hotpot_chain. Reason: in hotpot_chain the aggregator re-reads all paragraphs and can repair hop
    errors (laptop q4: hop upgrade values about 0)."

A14 "Second model family on every task: Granite 3.1 2B/8B on hotpot_chain and hotpot_chain_isolated
    (labels 200, all 32 plans on 400 eval problems, max_tokens 512), in addition to math. All
    hypotheses apply per family and are reported per family, never pooled."

### How A13 and A14 are measured

| Id | Reading | Output |
|---|---|---|
| A13 | Workflow key `hotpot_iso` (`create_hotpot_chain_isolated_workflow`). Same DAG, planner and hop prompts as hotpot_chain. Aggregator: the hotpot_chain prompt with the paragraphs removed (question + findings). Verifier: question + hop outputs + proposed answer; its two references to paragraphs read "findings", since it has none. Qwen 1.5B/7B setting `hotpot_iso_q15_7`: labels in P1 and plans in P2, each after the HotpotQA step (VM-A), same sizes and max_tokens 384 as hotpot_q15_7. Upgrade value = UV per agent in `labels_v2.csv` with its 95% CI; structural-rule regret at budgets 1-2 from `rule_plans.csv`, compared with hotpot_q15_7 in the same family. | `P1/hotpot_iso_q15_7/`, `P2/hotpot_iso_q15_7/`, `P6/hotpot_iso_q15_7/` |
| A14 | P4 (VM-B), after Granite math: `hotpot_granite` and `hotpot_iso_granite`, labels 200 (full and --disagree-only) and all 32 plans on the 400 frozen HotpotQA eval problems, max_tokens 512. P6 analyses each separately; `hypotheses.md` has one column per (task, family). Granite only: the aggregator and verifier prompts of both HotpotQA workflows get one extra line before the answer slot, "The final answer is the span alone, not a sentence." (`AGENTQO_HOTPOT_SPAN=1`, set in P4), because in the dry run Granite wrote the final answer as a sentence (all_large EM 0.00 on hotpot_chain). Comparisons within a family use identical prompts; raw accuracy across families includes this prompt difference and is not a registered test. No new P5 calibration set: A11 pools token rates over tasks per model, so Granite HotpotQA GPU costs use the Granite rates from the `granite_math` calibration set. | `P4/hotpot_granite/`, `P4/hotpot_iso_granite/`, `P6/hypotheses/hypotheses.md` |

## Amendments added 2026-11-16 04:06:51 UTC

Committed with this section (the commit carrying this timestamp registers it), before any lease
data exist (no vLLM data for any v2 setting, no Phi data of any kind). A1-A12, L1 and the
2026-11-12 section are unchanged except where A14 below supersedes the 2026-11-12 A14 text.

A13 (restated; text identical to the 2026-11-12 registration, which stands; given again with this
    timestamp as requested)
    "New workflow hotpot_chain_isolated: same as hotpot_chain, except the aggregator and verifier
    see only the question and the hop outputs (no paragraphs). Prediction: hop_1 and/or hop_2 have
    upgrade value with 95% CI above 0, and the structural rule's regret at budgets 1-2 is smaller
    than in hotpot_chain. Reason: in hotpot_chain the aggregator re-reads all paragraphs and can
    repair hop errors (laptop q4: hop upgrade values about 0)."

A14 (supersedes the 2026-11-12 A14 text; adds max-model-len 8192 and the validation sentence)
    "Second model family on every task: Granite 3.1 2B/8B on hotpot_chain and hotpot_chain_isolated
    (labels 200, all 32 plans x 400 eval problems, max_tokens 512, max-model-len 8192), in addition
    to math. All hypotheses apply per family and are reported per family, never pooled.
    Validation of new code: the 5-problem vLLM smoke test in lease P0, not a Mac run."

A15 "Third model family: microsoft/Phi-3.5-mini-instruct (small) and microsoft/phi-4 (large), MIT
    license, no gating. Math (labels 200, all 64 plans x 400) and hotpot_chain (labels 200, all 32
    plans x 400; max_tokens 512, max-model-len 8192). Same hypotheses, reported per family, never
    pooled. Runs last on VM-B; skipped with a logged reason if time runs short or the P0 smoke test
    fails. Validation: 5-problem vLLM smoke test in lease P0."
    Hugging Face check (2026-11-16 04:06:51 UTC, API metadata only, nothing downloaded): both ids exist;
    microsoft/Phi-3.5-mini-instruct gated=false, license mit; microsoft/phi-4 gated=false, license
    mit. Phi is not skipped.

### How A13-A15 and the P0 smoke test are measured

| Id | Reading | Output |
|---|---|---|
| A13 | As read on 2026-11-12 (workflow key `hotpot_iso`, setting `hotpot_iso_q15_7` in P1/P2 on VM-A), now gated by the P0 smoke test. | `P1/hotpot_iso_q15_7/`, `P2/hotpot_iso_q15_7/`, `P6/hotpot_iso_q15_7/` |
| A14 | As read on 2026-11-12 (P4 on VM-B after Granite math: `hotpot_granite`, then `hotpot_iso_granite`; short-span line `AGENTQO_HOTPOT_SPAN=1`), plus: vLLM servers started with `--max-model-len 8192`; both settings gated by the P0 smoke test. The 2026-11-12 Ollama dry run on the Mac stays in CHANGELOG_v2.md as background; it is not the validation. | `P0/`, `P4/hotpot_granite/`, `P4/hotpot_iso_granite/` |
| A15 | Config keys `phi_small` / `phi_large` in `configs/v2_models.yaml`. Phase P4b (VM-B, after P4): `math_phi` (labels 200 full and --disagree-only, all 64 plans on eval_ext 400), then `hotpot_phi` (labels 200, all 32 plans on the 400 frozen HotpotQA eval problems). max_tokens 512 for both tasks (A15 gives 512 for HotpotQA and no math value; 512 follows Granite math). `--max-model-len 8192`. HotpotQA uses the A14 short-span line (`AGENTQO_HOTPOT_SPAN=1`), as Granite does: the code freezes at the tag, so a Phi failure to give short spans could not be fixed during the lease. Within-family comparisons use identical prompts; raw accuracy across families includes this difference and is not a registered test. No P5 calibration set for Phi, so its GPU costs carry `gpu_cost_basis = fallback_latency`. `hypotheses.md` has one column each for `math_phi` and `hotpot_phi`. Skipped by hand if time runs short: `scripts/v2/smoke_check.py skip <setting> "<reason>"`, which logs it as below. | `P0/`, `P4b/math_phi/`, `P4b/hotpot_phi/`, `P6/math_phi/`, `P6/hotpot_phi/` |
| P0 | Settings new since Session 1: `hotpot_iso_q15_7`, `hotpot_granite`, `hotpot_iso_granite`, `math_phi`, `hotpot_phi`. Each is run on the first 5 problems of its label split with plans all_small and all_large, same max_tokens and prompts as its main run (`V2_P0=qwen\|granite\|phi` picks the servers running). It fails if it scores 0 (none of the 10 answers correct, all_small and all_large together) or if any answer normalizes to yes/no where the gold does not. A failed setting is skipped for the rest of the lease: a line in `results/v2/P0/skips.tsv`, in `FAILURES.md`, and a lease-time deviation `D-P0-<setting>` appended to this file. A new setting that P0 did not check is smoke-tested right before its first labels/plans step, so none runs unchecked. These two log files are excluded from the dirty-tree check, so appending to them does not stop later lease phases. | `results/v2/P0/<setting>/smoke/`, `results/v2/P0/skips.tsv`, `FAILURES.md` |
| caches | Session 1 caches no longer exist. The vLLM cache default is the new file `data/cache/v2_lease1.sqlite`; no code looks for a Session 1 cache, and every call is generated fresh. | - |

## Amendments added 2026-11-16 04:27:11 UTC

Committed with this section (the commit carrying this timestamp registers it), before any lease
data exist. A1-A15, L1 and the sections above are unchanged.

A16 "Multi-tier allocation: each math-chain agent uses Qwen2.5 1.5B, 7B or 14B (3^6 = 729 plans).
    All 729 plans on 200 eval problems; labels 200 measure each agent's gain for 1.5B->7B and
    1.5B->14B. Predictions: (a) independence estimates have mean absolute error >= 5 points over
    the 729 plans; (b) the pairwise-corrected estimate has lower error; (c) at most 10% of plans
    are on the accuracy-API-cost Pareto front. Purpose: ground truth for evaluating surrogate-assisted
    multi-objective search on a space larger than the binary case."

A17 "10-agent branching workflow (complex_r2_s2_ver, cautious verifier), Qwen 1.5B/7B, all
    2^10 = 1,024 plans on 200 eval problems, labels 200. Same predictions (a) and (b) as A16.
    Purpose: interactions and search ground truth in a non-chain workflow."

L2 (lease structure, given with A16/A17): Lease 1 runs 2026-11-16 12:00 UTC to 2026-11-19 12:00 UTC
    (72 h); only the tag freezes at 12:00 UTC on 2026-11-16. VM-A: P1, P2, P2b (A16), P2c (A17, after
    stopping the 14B server and restoring the 1.5B/7B memory split). VM-B: P3, P4 (Granite math and
    HotpotQA), P4b (Phi). Whichever VM finishes first takes the next unstarted setting from the other
    VM. If time runs short, settings are cut in this order: Phi hotpot, Phi math, A17 200->100 eval
    problems (same labels; the reduction is logged), A17, A16, E1, P5 K=1 runs, Granite isolated.

### How A16, A17 and L2 are measured

| Id | Reading | Output |
|---|---|---|
| A16 | Setting `math_tiers`, phase P2b (VM-A, after P2). Tiers small/large/xl = Qwen2.5 1.5B/7B/14B (`run_real_h3.py --plans all_subsets --tiers small,large,xl`, set by `V2_TIERS`); every plan writes the tier of each agent (`tier_<agent>`) in `h3_plans.csv`. Eval = first 200 of eval_ext, max_tokens 256. Labels: 1.5B->14B = labels 200 (full and --disagree-only) run with small 1.5B and large 14B; 1.5B->7B = the P1 `math_q15_7` labels (same 200 problems, same models), not run again. Estimators: a plan is the set of options "agent=tier" for its non-small agents; independence_additive, independence_multiplicative and pairwise_corrected (m = 3 top single options; a pair naming one agent twice is not a plan and is dropped) are the H2a/H2c code unchanged. "Mean absolute error over the 729 plans" = MAE over held-out plans as in H2a (not all_small, not a single option, not a measured pair); MAE over all plans next to it. (a) holds if both independence estimators have held-out MAE >= 0.05; (b) if pairwise_corrected's held-out MAE is below both. Also reported, not a test: independence from the labels (all_small accuracy + each agent's label UV for its tier). (c) Pareto front = plans not dominated in (accuracy higher, API USD per problem lower); holds if at most 10% of the 729 plans are on it. API price of 14B: 4.00 / 20.00 USD per million input/output tokens (the 7B price x 14/7); cost units 8. No GPU cost or placement for A16. | `P2b/math_tiers/`, `P6/math_tiers/tiers/tiers_summary.json`, `tier_estimator_errors.csv`, `tier_pareto.csv` |
| A17 | Setting `complex_q15_7`, phase P2c (VM-A, after P2b), workflow key `complex` (complex_r2_s2_ver), GSM8K, AGENTQO_VERIFIER=cautious, max_tokens 256. Labels 200 (full and --disagree-only) on the label split; 1,024 plans on the first 200 of eval_ext. (a), (b) read as in A16, from `estimator_errors.csv` of the standard P6 analysis (binary plans, m = 3). | `P2c/complex_q15_7/`, `P6/complex_q15_7/rules/estimator_errors.csv` |
| P0 | `math_tiers` (plans all_small, all_large, all_xl) and `complex_q15_7` join the P0 smoke test (V2_P0=tiers, complex), same rule as A13-A15. | `P0/math_tiers/`, `P0/complex_q15_7/` |
| L2 | Before a cuttable setting starts on a VM, `run_phase.sh` compares its 10x-rule hours from PLAN_v2_times.md (Phi hotpot 11, Phi math 16.5, A17 23 at 200 / 12.5 at 100, A16 19, Granite isolated 5.5) with the hours left to 2026-11-19 12:00 UTC minus a 4 h reserve (P5, P5 cal, P6, final). On each VM the later cuttable settings come earlier in the cut order, so a setting needs only its own hours; a setting cut for time also cuts the not-yet-started settings before it in the order on its VM. A17 drops to the first 100 eval problems if 200 does not fit and 100 does. Each cut or reduction is written to `results/v2/P0/skips.tsv` or `reduced.tsv`, FAILURES.md and this file (`D-P0-<setting>`, `D-P0-complex_q15_7-n100`). E1 and the P5 K=1 runs are not run by `run_phase.sh` and are cut by hand at their place in the order. A setting moved to the other VM is recorded with `smoke_check.py moved` (skips file only; not a deviation). The check sees one VM's clock, not the other VM's queue; across VMs the operator keeps the order. | `results/v2/P0/`, FAILURES.md |

## Lease-time deviation D-L2-h4grid (2026-11-16 13:30:14 UTC)

lease-time deviation. Time: 2026-11-16 13:30:14 UTC. Id: D-L2-h4grid. Affected phase: P5 (adds data only).
Reason: P5's run_placement.py output has per-problem start/end times and per-call latency, but not the
per-request start/end timing that scripts/h4_fit.py needs to refit the directed interference model
(AgentIconq betas). The refit therefore uses the Session 1 grid tool scripts/placement_test.py, unchanged
at the tag v2-lease1-start (no code change, so V2_DEVIATION is not needed to run it).
What runs: after P5's main placement blocks, for each model pair in V2_P5_CAL (Qwen 1.5B/7B for the main
sweep, plus qwen_hotpot's pair = Qwen 1.5B/7B, qwen3_14_math = Qwen 3B/14B, granite_math = Granite 2B/8B),
placement_test.py per-request grids in separate placement (L_iso) and in shared and shared_mps
placements, then h4_fit.py fit (and fit-mps for shared_mps) per model pair, compared with Session 1
(shared 2.392 / 0.991, MPS 2.072 / 0.332). Separate-placement grid cells are run only as the L_iso
baseline h4_fit requires. This adds data; it does not replace any P5 measurement, does not change the
H3c hold-out split (P6/hypotheses/h3c_split.json), and its fits are not used by any registered verdict.

## L2-X: lease-time exploratory extensions, registered 2026-11-16 18:16:57 UTC, before any X data exists

Status: EXPLORATORY. No X result changes, replaces or enters any registered verdict (H1-H6, A1-A17,
H3c split). Each X item writes only to its own folder results/v2/X1..X4/, is included in
results_v2_UPLOAD.zip and FINAL/data_check.md, and is listed in P6/search_ground_truth.md.
Code: tag v2-lease1-start, unchanged. Only config/env change: V2_TIERS, VLLM_ENDPOINTS,
VLLM_{SMALL,LARGE,XL}_MODEL, plan lists, seeds, problem ranges, output dirs, cache path. An item (or
part) that needs a code change is not run; the exact change is written to STATUS.md.
Order: after P6, X1 -> X2 -> X3 -> X4, while time allows before the new-GPU-work cutoff
2026-11-19 06:00 UTC; time left is recomputed and logged in STATUS.md after each item. Work is split
across VM-A and VM-B so neither idles; X1 "separate" uses both. Common settings: AGENTQO_VERIFIER=
cautious; AGENTQO_HOTPOT_SPAN=1 for Granite/Phi HotpotQA only (as P4/P4b); max_tokens as the quality
phases (Qwen math/complex 256, Qwen HotpotQA 384, Granite/Phi 512); vLLM memory 0.25 small / 0.55 large.

X1 Latency ground truth for every plan, no cache hits (scripts/v2/run_placement.py, as P5).
   Settings and plans: math_q15_7 (64), hotpot_q15_7 (32), hotpot_iso_q15_7 (32), math_q3_14 (64),
   math_granite (64), math_phi (64): all plans, placements separate (small on VM-A, large on VM-B
   at 10.56.2.39) and shared (both on one GPU), K=16, the first 64 problems of P5's split (GSM8K
   eval; HotpotQA eval), 2 repeats (3 if time allows). complex_q15_7 (A17): shared only, every plan
   on the true accuracy-cost Pareto front (P6/complex_q15_7/pareto) plus 100 other plans drawn at
   random with seed 0, K=16, 64 problems, 2 repeats.
   Measured: per plan and repeat p50/p95/p99 latency, throughput, accuracy (placement_summary.csv);
   per call prompt/completion tokens, latency and model (placement_calls.csv); per problem start/end
   time; nvidia-smi 1 s power logs (run_placement --vm on the driving VM; on the other VM the
   background log logs/v2/power_vm<V>.csv, clocks chrony-synced < 1 us).
   Not config-only, so not run: (i) per-request start/end timestamps (run_placement records
   per-problem start/end and per-call latency only); (ii) math_tiers (A16) plans, because
   run_placement builds binary small/large plans only. Exact changes go to STATUS.md.

X2 More eval problems (scripts/run_real_h3.py --plans all_subsets, lease cache).
   Config-only part: math_q15_7, math_granite and math_phi, all 64 plans on eval_ext 500 (the
   frozen eval_ext order; problems 1-400 are cache hits, 401-500 are new: 100 more problems).
   Measured: per-plan accuracy on problems 401-500 and on 1-500, Pareto front change.
   Not config-only, so not run: GSM8K test problems beyond eval_ext's 500 cap (~619 more), and 600
   more HotpotQA dev problems outside the frozen label/eval split.

X3 Cross-family model choice on math: tiers small/large/xl = Qwen2.5-7B / Granite-3.1-8B / Phi-4
   (VLLM_SMALL/LARGE/XL_MODEL, V2_TIERS=small,large,xl, VLLM_ENDPOINTS by model id), all three on one
   H100, max_tokens 512. First a 5-problem smoke test (label split) with plans all_small, all_large,
   all_xl; a family that scores 0 stops X3. Then labels 200 (label split, --realistic) for
   Qwen7B->Granite8B and Qwen7B->Phi-4, and all 3^6 = 729 plans on eval_ext 200.
   Measured: per-plan accuracy and API cost, per-agent label UV per pair, Pareto front vs single-
   family settings.

X4 Seed replicate of math_q15_7 and hotpot_q15_7: NOT config-only, so not run. Request seeds are
   fixed per (task, node, sample) in VLLMHTTPBackend._seed and run_real_h3.py passes seed=0, so a
   new cache with the same code would reproduce the same seeded requests. Exact change in STATUS.md.

### L2-X lease-time deviation: code change for X items (2026-11-16 23:02:12 UTC)

lease-time deviation: code change for X items. Id: D-L2-X-code. Approved by the PI's NEXT block
(2026-11-16 ~22:30 UTC). Branch v2-lease2-x, cut from tag v2-lease1-start, commit
eeb54603bbdfa1f760bbde86d6cd16a12388e034 (pushed, no force). Run from a separate clone
/mnt/data/AgentQO-x on each VM; the tag clone /mnt/data/AgentQO that runs every registered phase is
untouched. X1, X2 and X4 run on the GPU only after P6, from this commit, with V2_DEVIATION=D-L2-X-code,
writing to results/v2/X1, X2, X4 (X3 needs no code change and keeps running at the tag).
Changes (each with a unit test in tests/test_v2_lease2_x.py; full suite 195 passed, 8 skipped,
vs 189 passed, 8 skipped at the tag):
- X1(i): VLLMHTTPBackend records wall-clock request_start_s / request_end_s (epoch s) per request;
  run_placement.py writes them to placement_calls.csv.
- X1(ii): run_placement.py times A16 tier plans (V2_TIERS=small,large,xl) via run_real_h3.tier_plans;
  binary plans are built exactly as before.
- X2: GSM8K split eval_x2 = the 719 test problems in neither label 200 nor eval_ext 400
  (session1_extra order); HotpotQA split extra = the next 600 dev rows in the frozen split's seeded
  order outside label/eval. Checked on the real data: 719 and 600 problems, 0 overlap.
- X4: AGENTQO_SEED_SALT salts the per-request seed (unset = registered seeds); X4 also uses its own
  cache file, so nothing is reused.
X scope with this change: X1 adds per-request start/end timestamps and math_tiers (A16, shared:
Pareto-front plans + 100 random, seed 0); X2 = all plans of math_q15_7, math_granite, math_phi on
eval_x2 (719) and of hotpot_q15_7, hotpot_iso_q15_7 on HotpotQA extra (600), replacing the
eval_ext-500 partial X2; X4 = all plans of math_q15_7 (eval_ext 400) and hotpot_q15_7 (eval 400)
with AGENTQO_SEED_SALT=1 and cache data/cache/x4_seed1.sqlite. Order after P6: X1 -> X2 -> X3 (if not
finished) -> X4, split across both VMs.

git diff --stat v2-lease1-start eeb54603:
```
 agentqo/backends/vllm_http.py |   9 +++-
 agentqo/tasks/datasets.py     |   9 ++++
 agentqo/tasks/hotpotqa.py     |  22 +++++++--
 scripts/run_real_h3.py        |   2 +-
 scripts/run_real_pipeline.py  |  10 +++--
 scripts/v2/run_placement.py   |  39 ++++++++++++----
 tests/test_v2_lease2_x.py     | 101 ++++++++++++++++++++++++++++++++++++++++++
 7 files changed, 174 insertions(+), 18 deletions(-)
```

### L2-X update: X2 problem sets and the timing lock (2026-11-16 23:20:30 UTC, before any X2 data)

X2 now uses the GSM8K split eval_x2 (719 test problems in neither label 200 nor eval_ext 400) for
math_q15_7, math_granite and math_phi, and the HotpotQA split extra (600 dev rows outside the frozen
label/eval split) for hotpot_q15_7 and hotpot_iso_q15_7, all plans each, from v2-lease2-x eeb54603
(D-L2-X-code). This replaces the earlier X2 plan (all 64 plans on eval_ext 500, i.e. 100 new problems).
No X2 data exists on either VM at this time (checked: no results/v2/X2 directory on VM-A or VM-B).
Timing lock (PI NEXT block 7): every latency-measuring run (D-L2-h4grid, any remaining P5 step, all
of X1) creates /mnt/data/TIMING_LOCK on both VMs before its first server starts and removes it on each
VM only after that VM's last timing run; X3 and any other non-timing GPU job start or resume only when
no lock exists, and stop their servers before the lock is confirmed (tlock.sh acquire waits for that).
Check of the runs so far: X3's calls on VM-B span 20:15:07-21:09:21 UTC (none after its 21:09:24
pause); VM-B's timing servers came up at 21:10:19 (P5 separate cal) and 21:35:05 (h4grid), and VM-B's
P5 shared cal ended 19:27; during X3's window only VM-A's own GPU ran timing (P5 shared_mps). No overlap,
so no h4grid or P5 point is rerun.

## L2-X5/X6: lease-time exploratory extensions, registered 2026-11-17 01:49:29 UTC, before any X5 or X6 data exists

Status: EXPLORATORY, same rules as L2-X: no X5/X6 result changes or enters any registered verdict;
own folders results/v2/X5 and results/v2/X6; V2_DEVIATION set (D-L2-X-code); both are included in
results_v2_UPLOAD.zip, FINAL/data_check.md and P6/search_ground_truth.md. They start after X1, X2 and
X4 (X3 continues on VM-B), and no new X work starts after 2026-11-19 00:00 UTC; the time left is
recomputed and logged in STATUS.md after each item.

Reason. Task difficulty: GSM8K is close to the ceiling for the 7B (all_large 0.82 on math_q15_7), so
upgrade values and the Pareto front may look different when the small and large model both fail more
often; MATH-500 tests that. Model scale: every registered pair has its large model at <= 14B; a
7B/32B pair tests whether the findings hold when the small model is already strong and the large one
much larger, and adds a 32B point to the latency/cost picture.

Code. X5 needs a dataset loader and a scorer: branch v2-lease2-x commit
c1bb8338fa64acd82d82f1eb0c5a5ce6cb7b019b (on top of eeb54603, D-L2-X-code), pushed, run from
/mnt/data/AgentQO-x: agentqo/tasks/math500.py (HuggingFaceH4/MATH-500 test, 500 problems, fixed seed-0
split label 200 / eval 300, ids in data/tasks/math500_split.json); answers.extract_boxed (content of the
last balanced \boxed{}; none = unscorable), normalize_math and math_equal (normalized string match or
numeric equality, rel. tol. 1e-6); RealTaskModel dataset math500; the math chain role prompts with the
answer format \boxed{<answer>} instead of "#### <number>" (GSM8K prompts unchanged); --dataset math500.
5 unit tests (tests/test_v2_lease2_x5.py); full suite 200 passed, 8 skipped. Check on the data: the 500
reference solutions score 500/500 and all have a \boxed{} answer.
git diff --stat eeb54603 c1bb8338:
```
 agentqo/tasks/answers.py         | 65 ++++++++++++++++++++++++++++++++++++++++
 agentqo/tasks/math500.py         | 47 +++++++++++++++++++++++++++++
 agentqo/tasks/prompts.py         | 19 +++++++++++-
 agentqo/tasks/real_task_model.py |  8 +++--
 scripts/run_real_h3.py           |  2 +-
 scripts/run_real_pipeline.py     |  5 +++-
 scripts/v2/run_placement.py      |  2 +-
 tests/test_v2_lease2_x5.py       | 65 ++++++++++++++++++++++++++++++++++++++++
 8 files changed, 207 insertions(+), 6 deletions(-)
```

X5 harder math: math500_q15_7. MATH-500, the 6-agent math chain (math_reasoning_s3_ver),
AGENTQO_VERIFIER=cautious, Qwen2.5-1.5B/7B-Instruct (0.25 / 0.55 on one GPU, --max-model-len 8192),
max_tokens 1024, lease cache. Smoke test first: 5 label problems, all_small and all_large. Stop X5 (and
log why) if smoke all_small = 0 or more than 20% of the smoke outputs are unscorable (no \boxed{}).
Then labels on the 200 label problems (--realistic, --stage h1, K 5) and all 64 plans on the 300 eval
problems. Measured: per-agent labels (p_dis, UV, EC), per-plan accuracy, API cost and Pareto front,
and the unscorable rate (share of answers with no \boxed{}; per plan and overall, from h3_traces.json
pred = null). Results: results/v2/X5/math500_q15_7/{smoke,labels,plans}.

X6 larger scale: Qwen2.5-7B-Instruct (small) / Qwen2.5-32B-Instruct (large), full precision (bf16).
The two do not fit on one H100 80 GB with KV cache (weights ~15 GB + ~65 GB), so for the quality runs
the 32B is served alone on VM-A (--gpu-memory-utilization 0.90) and the 7B on VM-B (accuracy does not
depend on placement), mapped by model id in VLLM_ENDPOINTS; VM-A disk is freed first by deleting
models no longer needed there (its unused Phi-4 copy, the AWQ models after E1, Qwen 14B after X1's
math_tiers runs), logged in STATUS.md. Settings: math_q7_32 (GSM8K, max_tokens 256, labels 200 on the
label split, all 64 plans on eval_ext 400), hotpot_q7_32 (hotpot_chain, max_tokens 384, labels 200, all
32 plans on HotpotQA eval 400) and, if X5 passes its smoke test, math500_q7_32 (max_tokens 1024, labels
200, all 64 plans on the 300 eval problems). Same measures as the quality phases (labels, per-plan
accuracy/cost, Pareto front). Then a P5-style latency block for math_q7_32 under TIMING_LOCK: the 7 P5
plans, K=16, the first 64 GSM8K eval problems, 2 repeats, placement separate (32B on VM-A, 7B on
VM-B), with per-request start/end and power logs (run_placement.py at c1bb8338). The shared placement
cannot run: both models' weights alone exceed one 80 GB GPU in full precision, so it is recorded as
not run. Results: results/v2/X6/<setting>/..., latency in results/v2/X6/latency/separate.

### L2-X5/X6 corrections (2026-11-17 01:55:06 UTC, before any X5 or X6 data)

1. GPU memory. The H100s have 94 GB (nvidia-smi: 95,830 MiB), not 80 GB as written above. The X6
   shared 7B/32B latency block is dropped, for this reason: "shared 7B/32B infeasible with a usable KV
   cache on one 94 GB H100" (a placement feasibility constraint). Their weights (~15 + ~65 GB) would
   load but leave only ~5-8 GB of KV cache, so a shared block would measure memory pressure, not
   interference. X6 latency runs in the separate placement only (32B on VM-A, 7B on VM-B). Evidence,
   recorded before X6 starts (results/v2/X6/shared_feasibility/, summary in STATUS.md): one shared
   server start of both models on one GPU with --gpu-memory-utilization 0.50 (32B) / 0.45 (7B), and one
   with 0.75 / 0.20, with the KV-cache size, maximum concurrency / blocks or the error that vLLM reports.
   With 94 GB the 32B quality server runs at 0.90 (~85 GB, ~19 GB KV cache).
2. Disk for the 32B (~66 GB on VM-A). Only re-downloadable model weights past their last scheduled
   use are deleted: VM-A's unused Phi-4 copy (X1, X2 and X3 use VM-B's), the AWQ models (last use E1)
   and Qwen 14B on VM-A (last use X1 math_tiers), 66.1 GB, after X1 releases its timing lock. Blobs
   are deleted only if no remaining model links to them (/mnt/data/delmodel.py; the hub keeps blobs
   in one shared store). At least 25 GB stays free after the download (expected ~52 GB). Caches,
   results, logs and the venv are never deleted. Every deletion is logged in STATUS.md. If that is
   not enough when X6 is due, "ACTION NEEDED: attach another volume" is printed and X6 is skipped.

### L2-X5 safeguards (2026-11-17 01:57:47 UTC, before any X5 data)

Data version: HuggingFaceH4/MATH-500 test.jsonl at Hugging Face commit
6e4ed1a2a79af7d8630a6b768ec859cb5af4d3be ("main" on 2026-11-17 01:57:47 UTC), sha256
35dc41080a3680858b27fa7e0533d2d547825316fc5dafe5d316f4ccc5a06132 (500 rows); fetched at that commit,
byte-identical to main, and pinned at /mnt/data/AgentQO-x/data/tasks/math500_test.jsonl on both VMs, so
the loader never downloads it again. Recorded in results/v2/X5/README.md.
Prompt check: math500_prompt() rewrites the math prompts with str.replace. Before the smoke run, every
agent's prompt for the 5 smoke problems is built with the run's code and checked; after the labels,
every prompt actually sent (label traces) is checked. Rule: no prompt contains "#### <number>" or
"<number>"; every agent except the planner contains "\boxed" or "RESULT: <expression>" (the planner
only plans and is given no answer format, so it is checked for the first part only). A violation stops
X5 (smoke) or fails it before the plans. Static check run now: 30 prompts, 0 violations.
Scorer audit: after the labels, results/v2/X5/scorer_audit.csv lists 40 random label problems scored
wrong that have a prediction (seed 0; gold, pred, raw final text, a blank hand-check column) and
unscorable_by_agent.csv the unscorable rate per agent, for a manual false-negative check later. The
scorer is not changed during the lease.

## L2-X7: lease-time exploratory extension (coding), registered 2026-11-17 02:22:33 UTC, before any X7 data exists

Status: EXPLORATORY, same rules as L2-X: never changes a registered verdict; folder results/v2/X7;
V2_DEVIATION=D-L2-X-code; included in results_v2_UPLOAD.zip, FINAL/data_check.md and
P6/search_ground_truth.md. Runs only after X5 and X6, and only if at least 10 h remain before the
2026-11-19 00:00 UTC stop for new X work; otherwise skipped and logged. It never delays FINAL.
Reason: a third task type (code generation with executable checks, alongside math and multi-hop QA), to
see whether per-agent upgrade values, the rules and the Pareto structure carry over to an agent chain
whose intermediate outputs (code, tests, execution reports) are checked by running code.
Task: MBPP+ (evalplus/mbppplus, test split, 378 problems), Hugging Face commit
b2d74c91837c3f2a20c1299ae98133cbe7cfa077, file data/test-00000-of-00001-d5781c9c51e02795.parquet,
sha256 dc20030b3788fccf617444edcb34138ef13d7e4fafd17bfcb8c1279dbb12399b; converted once to
data/tasks/mbppplus.jsonl (rows sorted by task_id; sha256
94b7c1db0e68c88983fbe5a2fc878dda79875c6482283b350e6530b1f5ad6572), pinned on the VMs. Split: seed-0
permutation, label = first 200, eval = the other 178 (cap 300).
Workflow (5 agents, 2^5 = 32 plans): planner -> coder -> tester (writes 5 extra asserts) -> fixer (revises
the code given the sandbox results of the task's visible example test plus the tester's asserts) ->
verifier (picks coder's or fixer's code, also given both test reports). The hidden MBPP+ tests are used
only for scoring. Models: Qwen2.5-Coder-1.5B-Instruct (small) / Qwen2.5-Coder-7B-Instruct (large), one GPU
(0.25 / 0.55, --max-model-len 8192), max_tokens 512. Score: the verifier's final code (last fenced block)
passes ALL MBPP+ tests (exit code 0 in the sandbox).
Safe execution (mandatory): model code runs only in a subprocess (never exec/eval in the agent process),
as the non-root lease user, in a fresh temp dir, in new user/network/mount/pid namespaces (util-linux
unshare): no network; the temp dir is bound over /mnt (hiding /mnt/data: repo, caches, results, venv);
read-only empty tmpfs over /tmp, /var/tmp, /dev/shm, /home, /root, /run, /srv, /opt, /media; all
capabilities dropped and no_new_privs (the mounts cannot be undone); empty environment; ulimit -v 2 GB,
-u 64, 64 MB files, 64 open files; 10 s timeout that kills the process group; system /usr/bin/python3 -I
(python3-numpy from Ubuntu is installed on the X7 VMs because the MBPP+ test harness imports numpy).
Code: branch v2-lease2-x commit 88e9d762ee9a8b63c7b06bca05af5cb3840d6572 (on c1bb8338). Tests:
tests/test_v2_lease2_x7.py, 13 tests, 8 of them sandbox tests (network blocked; writes outside the temp
dir blocked and nothing lands on the host; repo, /mnt/data and a host canary file hidden; infinite loop
killed; memory and process limits; empty env and mounts cannot be undone; hidden-test scoring). Mac suite
205 passed, 16 skipped (the 8 sandbox tests need Linux); the sandbox tests and the full suite are run on
each X7 VM before any X7 data, and X7 stops if any sandbox test fails. GSM8K/HotpotQA prompts unchanged
(hash 1021bceca3949efc, same as the tag).
git diff --stat c1bb8338 88e9d762:
```
 agentqo/tasks/mbppplus.py        | 111 +++++++++++++++++++++++++++
 agentqo/tasks/prompts.py         |  73 ++++++++++++++++++
 agentqo/tasks/real_task_model.py |   8 +-
 agentqo/tasks/sandbox.py         |  77 +++++++++++++++++++
 agentqo/workflows/library.py     |  15 ++++
 scripts/run_real_h3.py           |   2 +-
 scripts/run_real_pipeline.py     |   7 +-
 scripts/v2/run_placement.py      |   2 +-
 tests/test_v2_lease2_x7.py       | 160 +++++++++++++++++++++++++++++++++++++++
 9 files changed, 451 insertions(+), 4 deletions(-)
```
Order: smoke on 5 label problems (all_small, all_large); stop X7 if all_small passes 0. Then labels on the
200 label problems (--realistic, --stage h1, K 5) on one VM and all 32 plans on the 178 eval problems on
the other, in parallel. Measured: per-agent labels (p_dis, UV, EC), per-plan pass rate and API cost, the
Pareto front, and the rate of answers with no code block and of sandbox timeouts.

### L2-X update: X4 redefined (2026-11-17 02:33:28 UTC, before any X4 data)

X4 redefined as a greedy-decoding run-to-run replicate: decoding is greedy (temperature 0), so the seed
salt has no effect; X4 reruns all plans of math_q15_7 and hotpot_q15_7 on the same 400 problems with a
fresh, separate cache, measuring serving nondeterminism (batching) on plan accuracy and Pareto-front
stability. Evidence: P5 all_small accuracy 0.516/0.516/0.562 across repeats on the same 64 problems.
Run: code v2-lease2-x c1bb8338 with AGENTQO_SEED_SALT=1 left set (no effect under greedy decoding; the
salted seeds also keep every cache key distinct), cache data/cache/x4_seed1.sqlite (new, separate),
math_q15_7 on eval_ext 400 (64 plans), hotpot_q15_7 on HotpotQA eval 400 (32 plans), Qwen 1.5B/7B, same
max_tokens and servers as P2. Reported against P2 (same plans and problems): per-plan accuracy change,
the share of (plan, problem) cells whose correctness flips, and whether the accuracy / API-cost Pareto
front changes (plans added or removed). No X4 data exists on either VM at this time.

### L2-X7 limitation (2026-11-17 02:33:28 UTC)

Sandbox timeouts during final scoring are not recorded separately: a timeout counts as a fail (the code
does not pass all MBPP+ tests). Timeouts that appear in the fixer's and verifier's test reports can be
counted from the label-trace prompts.

### L2-X7: sandbox interpreter package (2026-11-17)

python3-numpy installed from the Ubuntu 22.04 archive with apt (sudo), outside any TIMING_LOCK window, for
the sandbox interpreter /usr/bin/python3 (the MBPP+ test harness imports numpy):
- VM-A, 2026-11-17 03:07:42 UTC: python3-numpy 1:1.21.5-1ubuntu22.04.1 (numpy 1.21.5).
- VM-B: installed after its TIMING_LOCK is released; version appended below when done.
- VM-B, 2026-11-17 05:37:19 UTC: python3-numpy 1:1.21.5-1ubuntu22.04.1 (numpy 1.21.5), right after VM-B's TIMING_LOCK release.

### L2-X deviation D-L2-X1-complex-front (2026-11-17 07:05:34 UTC)

X1 complex_q15_7 (shared) took its front from P6/complex_q15_7/pareto_api/pareto_front.csv, which is the front over
accuracy, API cost and p95 latency (84 plans), not the 2-D accuracy / API-cost front registered in L2-X (12 plans,
P6/search_ground_truth.md). The timed list is therefore those 84 plans plus 100 others drawn with seed 0 from the
remaining 940 (X1/complex_q15_7/plan_selection.json); it contains all 12 plans of the registered 2-D front. Kept as is
(exploratory, a superset of the registered front); the 100 random plans differ from a draw over the 1,012 non-front
plans. Cost: about +0.9 h on VM-A's X1 shared block. math_tiers is as registered (14 front plans + 100).

### L2-X1b: load sweep for held-out latency validation, registered 2026-11-17 13:59:13 UTC, before any X1b data

Status: EXPLORATORY under L2-X (same rules: own folder results/v2/X1b, V2_DEVIATION=D-L2-X-code, code
v2-lease2-x c1bb8338 with per-request start/end timestamps, included in results_v2_UPLOAD.zip,
FINAL/data_check.md and P6/search_ground_truth.md as latency ground truth).
Reason: held-out validation of an offline whole-plan latency simulator, built in a separate session on branch
v2-latsim and fitted only on P5 + h4grid. X1b is never used for fitting; it measures loads and plans the
simulator has not seen.
What: settings math_q15_7, hotpot_q15_7, math_granite, math_phi. Plans: all_small, all_large, every
single-agent plan, plus random plans drawn with seed 1 from the rest: 8 for the math chain (6 agents, 16 plans)
and 4 for hotpot_chain (5 agents, 11 plans; the request said 12, but the chain has 5 agents). Loads K = 4, 8
and 32, the first 64 problems of P5's split, 2 repeats, no cache. Placements: separate (small on VM-A, large on
VM-B at 10.56.2.39) and shared (one GPU), plus shared_mps for math_q15_7 only. Also K=1 for math_q15_7 only:
all_small, all_large, only_verifier, aggregator+verifier, 32 problems, 1 repeat, separate and shared. Servers
and settings as X1 (small 0.25 / large 0.55, AGENTQO_VERIFIER=cautious, max_tokens 256 math / 384 HotpotQA /
512 Granite and Phi). Measured: per run p50/p95/p99, throughput, accuracy; per call tokens, latency and
request start/end; nvidia-smi 1 s power logs.
How and when: right after X1 and before X2, under TIMING_LOCK on both VMs held from X1 through X1b (X3 and X7
paused), reusing X1's servers where possible; a gate and push per setting and placement. If X1b would push
X7's start past 2026-11-18 14:00 UTC, only math_q15_7 and math_phi run and the cut is logged. The time left is
recomputed and logged after X1b.

### L2-X1c: interference grids the latency simulator still borrows, registered 2026-11-17 14:02:48 UTC, before any X1c data

X1c: h4-style interference grids for (a) Phi-3.5-mini/Phi-4 and (b) the three-model A16 setup (Qwen
1.5B/7B/14B on one GPU), because the latency simulator currently borrows these betas. Used to FIT latsim
rev2; X1/X1b stay held-out tests.
Rules as L2-X: EXPLORATORY, folder results/v2/X1c, code v2-lease2-x c1bb8338 run from the x clone,
V2_DEVIATION=D-L2-X-code, under TIMING_LOCK on both VMs (held from X1 through X1b and X1c, X3/X7 paused),
no cache, power logs kept, a gate and push per part. Runs after X1b and before X2; the time left is
recomputed after it; (b) is skipped if X7's start would move past 2026-11-18 14:00 UTC.
(a) Phi-3.5-mini (small) / Phi-4 (large): the D-L2-h4grid design with scripts/placement_test.py (unchanged at
the tag): grid in separate (Phi-3.5-mini on VM-A, Phi-4 on VM-B) and shared placement x small_share
0.25/0.5/0.75 x max_tokens 32/128/512 x concurrency 1,4,16 (64 requests) and 64 (128 requests), reduced to
1 repeat (repeat 0) to stay under 2 h; MPS step separate / shared_nomps / shared_mps x share 0.5 x 128
tokens x concurrency 1,4,16,32 x 3 repeats; then scripts/h4_fit.py fit and fit-mps (servers 0.25 / 0.55).
(b) A16 three-model setup, shared placement only (Qwen 1.5B 0.15 / 7B 0.30 / 14B 0.45 on VM-A's GPU, as P2b).
placement_test.py drives only two endpoints, so a synthetic three-model grid would need a code change; instead
the grid over which models are busy uses the A16 workflow with scripts/v2/run_placement.py (per-request
start/end timestamps), math chain, max_tokens 256, K=16, 64 problems, 2 repeats, tier plans chosen by the set
of busy models: small+large {aggregator=large+verifier=large, planner=large+step_2=large}; small+xl
{aggregator=xl+verifier=xl, planner=xl+step_2=xl}; large+xl {planner=large+step_1=large+step_2=large+
step_3=large+aggregator=xl+verifier=xl, planner=xl+step_1=large+step_2=large+step_3=large+aggregator=large+
verifier=large}; all three {step_2=large+verifier=xl, planner=xl+aggregator=large, step_1=large+step_3=xl+
verifier=large}.

### L2-X1c (b) plan rule (2026-11-17 14:15:30 UTC, before any X1c data)

X1c (b) uses only A16 plans that are NOT in results/v2/X1/math_tiers/plans.txt (the 114 plans X1 timed), so X1
math_tiers stays a clean held-out test for latsim rev2. A plan's busy set is the set of tiers its six agents use
(unlisted agents are small). A registered plan that X1 timed is replaced by an unused plan with the same busy set
(drawn with seed 2); if a busy set had no unused plan, the closest unused plan would be used and named. Check: 2 of
the 9 plans in the first X1c registration were in X1 (aggregator=xl+verifier=xl; step_1=large+step_3=xl+
verifier=large); every busy set has unused plans (small+large 51, small+xl 50, large+xl 53, all three 459), so both
were replaced by exact busy-set matches. Final X1c (b) plans (none in X1 math_tiers):
- small+large: aggregator=large+verifier=large; planner=large+step_2=large
- small+xl: planner=xl+step_1=xl+aggregator=xl (replaces aggregator=xl+verifier=xl); planner=xl+step_2=xl
- large+xl: planner=large+step_1=large+step_2=large+step_3=large+aggregator=xl+verifier=xl;
  planner=xl+step_1=large+step_2=large+step_3=large+aggregator=large+verifier=large
- all three: step_2=large+verifier=xl; planner=xl+aggregator=large; planner=large+step_1=xl (replaces
  step_1=large+step_3=xl+verifier=large)

### L2-X8: held-out problems for the largest search space, registered 2026-11-18 03:36:05 UTC, before any X8 data

Status: EXPLORATORY under L2-X (own folder results/v2/X8, V2_DEVIATION=D-L2-X-code, code v2-lease2-x c1bb8338
from the x clone, included in results_v2_UPLOAD.zip, FINAL/data_check.md and P6/search_ground_truth.md).
Reason: held-out problems for the largest search space. complex_q15_7 (A17, 1,024 plans) is the largest plan
space; X8 gives a second, disjoint set of problems on which every plan is measured, so search results can be
checked on problems the search never saw.
What: complex_q15_7 (complex_r2_s2_ver, Qwen2.5-1.5B/7B-Instruct, AGENTQO_VERIFIER=cautious, max_tokens 256,
servers 0.25 / 0.55 on one GPU), ALL 1,024 plans (run_real_h3.py --plans all_subsets) on 200 GSM8K problems from
eval_x2: the first 200 in its fixed order (none in label 200 or eval_ext 400). No new labels: X8 reuses P2c's
labels (results/v2/P2c/complex_q15_7/labels). Lease cache. Output results/v2/X8/complex_q15_7/plans. Accuracy only.
When: on VM-A's idle time, only after the search session's tag search-prereg-s5b-* exists on origin. X6 has
priority: if X3 finishes first, X8 waits; if X8 is running when X6 starts, it is paused and resumed from the
cache after X6 (including X6 latency) is complete. Never under a TIMING_LOCK. A gate and push when done.

### L2-X9 and L2-X10, registered 2026-11-18 13:55:13 UTC, before any X9 or X10 data

Status: EXPLORATORY under L2-X (own folders results/v2/X9 and results/v2/X10, V2_DEVIATION=D-L2-X-code, run from the
x clone at v2-lease2-x 18b3d7a0 (= aececaa1 + the eval_x2b split below, unit test added, Mac suite 206 passed / 16
skipped), included in results_v2_UPLOAD.zip, FINAL/data_check.md and P6/search_ground_truth.md; a gate and push each).
Both run on VM-B (the only VM that still has Qwen 14B, Granite and Phi weights); new GPU work may start until
2026-11-19 14:00 UTC, and both finish before then or are cut and logged.

L2-X9 (held-out problems for A16, the 3-tier space). Reason: a second, disjoint problem set on which every A16 plan is
measured, so tier-search results can be checked on problems the search never saw. What: math_tiers (A16: Qwen2.5-1.5B /
7B / 14B-Instruct as small / large / xl, math workflow, max_tokens 256, cautious verifier, servers 14B 0.45 / 7B 0.30 /
1.5B 0.15 on one GPU as in P2b), ALL 729 plans (run_real_h3.py --plans all_subsets, V2_TIERS=small,large,xl) on 200 GSM8K
problems: split eval_x2b = eval_x2[200:400] in its fixed order, i.e. the next 200 after X8's eval_x2[:200] (code change
18b3d7a0: scripts/run_real_pipeline.py load_problems + the --split choices of both scripts; test_eval_x2b_split checks
eval_x2b == eval_x2[200:400] and that it is disjoint from eval_x2[:200]). No new labels: P2b's labels are reused
(results/v2/P2b/math_tiers/labels). Lease cache. Qwen2.5-1.5B-Instruct is downloaded on VM-B (about 3 GB; nothing is
deleted; /mnt/data stays above 25 GB free). Started only after the search session's tag search-prereg-s5c-* exists on
origin (search-prereg-s5c-20261118T1353Z was there at registration). Output results/v2/X9/math_tiers/plans. Accuracy only.

L2-X10 (greedy run-to-run replicate for two more model families). Reason: X4 measured run-to-run variation under greedy
decoding for Qwen only; X10 measures it for Granite and Phi. What: math_granite (Granite-3.1-2B/8B) and math_phi
(Phi-3.5-mini/Phi-4), all 64 plans x the same 400 problems as P4 / P4b (split eval_ext, n 400), the same settings as
P4 / P4b (math workflow, max_tokens 512, cautious verifier, servers large 0.55 / small 0.25, max-model-len 4096, seed 42),
with a fresh separate cache (data/cache/x10_vmB.sqlite on VM-B, so no call is reused; AGENTQO_SEED_SALT=1 as in X4, which
has no effect under greedy decoding). Reported per setting, as in X4, against P4 / P4b: per-plan accuracy change, the
share of flipped (plan, problem) cells, plans with any flip, and Pareto-front changes (accuracy vs cost_units, both runs
costed with the reference run's cost per plan). Output results/v2/X10/<setting>/plans and x10_vs_ref_*.
Order on VM-B: X9, then X10 math_granite, then X10 math_phi; never under a TIMING_LOCK (none is planned).

### L2-X11: held-out replication on MATH-500 and MBPP+, registered 2026-11-18 14:16:52 UTC, before any X11 data

Status: EXPLORATORY under L2-X (own folder results/v2/X11, V2_DEVIATION=D-L2-X-code, run on VM-A only from the x clone at
v2-lease2-x 18b3d7a0, which contains the X5 and X7 code unchanged; no new code is needed: the "label" split of both loaders
already returns exactly the problems below). Included in results_v2_UPLOAD.zip, FINAL/data_check.md (required if finished)
and P6/search_ground_truth.md. A gate and push after each block. Accuracy only (no TIMING_LOCK; never started while VM-A
holds one). Nothing is deleted.
Purpose: held-out replication: do the plan ranking, the cheapest good plan, and best-vs-all-large hold on new problems?
Problem sets. MATH-500 has 500 problems and MBPP+ 378; X5 used 200 for labels + 300 for plan evaluation and X7 used 200 for
labels + 178 for plan evaluation, so no problem is untouched by X5/X7. The problems NOT in X5's / X7's plan evaluation are
exactly their 200 label problems; they were used only for the per-agent labels (H1 substitution runs), never for plan
evaluation. Therefore:
- X11a: math500_q15_7 (X5 setting: Qwen2.5-1.5B/7B-Instruct, math workflow, max_tokens 1024, max-model-len 8192, servers
  7B 0.60 / 1.5B 0.20, boxed-answer scorer of X5), ALL 64 plans on the MATH-500 split "label" (n = 200).
- X11b: code_c15_7 (X7 setting: Qwen2.5-Coder-1.5B/7B-Instruct, code workflow, max_tokens 512, max-model-len 8192, servers
  Coder 7B 0.45 / Coder 1.5B 0.15, X7 sandbox and MBPP+ base+plus tests), ALL 32 plans on the MBPP+ split "label" (n = 200,
  all MBPP+ problems not in X7's plan evaluation).
Greedy decoding, cautious verifier, lease cache (VM-A). Note: X5's label runs used VM-A's lease cache, so X11a calls whose
prompt is identical to an X5 label-run call (e.g. parts of all_small) are cache hits with the same greedy output; X7 ran on
VM-B, so X11b calls on VM-A are all fresh. The Coder 1.5B/7B weights are downloaded on VM-A (about 18 GB; /mnt/data stays
above 25 GB free). Before any model call, X11 writes split files (problem ids, the sha256 of the sorted id list) to
results/v2/X11/<setting>/split.json and asserts zero overlap with the X5 / X7 plan-evaluation ids (from their split and from
their h3_per_problem.csv); a non-empty overlap stops X11. VM-A runs the X7 sandbox tests and the full suite (V2_PUSH unset)
before X11b. Order: prep (no model calls) -> wait for the search session's tag search-prereg-s5d-* on origin -> X11a -> X11b.
No block starts after 2026-11-19 14:00Z; final_guard rules unchanged. A restart moves a partial run to superseded_* and logs
it. Reported: per plan accuracy, unscorable (X11a) / no-code (X11b) rates, and vs X5 / X7: Spearman rank correlation of plan
accuracy, the cheapest plan within 1 point of the best, and best plan vs all_large.

#### L2-X11 addendum: H5c (RQ5, confirmatory on X11), registered 2026-11-18 14:27:33 UTC, before any X11 model call (no X11 data exists:
results/v2/X11 is absent on VM-A; only x11prep, which makes no model calls, has run)

H5c. Data for the search: the existing X5 / X7 plan-evaluation per-problem data (results/v2/X5/math500_q15_7/plans,
64 plans x 300 MATH-500 eval problems; results/v2/X7/code_c15_7/plans, 32 plans x 178 MBPP+ eval problems). Two searches,
each run over 30 seeded problem orders (seeds 0-29; the seed permutes the eval problems):
(a) paired successive halving: round 1 scores every plan on the first n0 = 25 problems of the order; keep the top 1/3 of the
    plans by accuracy (ceil; ties broken by lower cost_units, then plan name), and triple the number of problems per round
    (25, 75, 225, ... capped at all eval problems; each round uses the first n_r problems of the same order, so comparisons
    are paired); stop when one plan is left or the problems are exhausted (then the best remaining plan by accuracy on all
    problems used, same tie-break).
(b) paired eps-racing: eps = 0.0134; every live plan is scored on the first 25 problems of the order, then 25 more per step;
    after each step the leader is the live plan with the highest accuracy on the problems seen; a plan is dropped when the
    upper end of the 95% normal CI (mean +/- 1.96 sd / sqrt(n)) of its per-problem paired difference to the leader is below
    -eps; stop when one plan is left or the problems are exhausted (then the leader).
Evaluations counted = plan x problem cells scored. Comparator: the eval-exhaustive pick = the plan with the best accuracy on
all eval problems (same tie-break); its cost = all plans x all eval problems. Scoring: each pick's accuracy on the X11
held-out problems (X11a: 200 MATH-500 problems; X11b: 200 MBPP+ problems), regret = best held-out accuracy over all plans
minus the pick's held-out accuracy. HELD if, in both settings, the mean held-out regret (over the 30 seeds) of (a) and of
(b) is within tau = 0.0134 of the exhaustive pick's held-out regret, and the mean number of evaluations of (a) and of (b)
is <= 40% of the exhaustive count. Otherwise NOT HELD (each condition reported separately). Offline analysis only (no
extra model calls), computed after X11 finishes; results in results/v2/X11/H5c/.

#### L2-X11 addendum: H1d (RQ1, confirmatory on X11), registered 2026-11-18 14:33:36 UTC, before any X11 model call (no X11 model output exists; results/v2/X11 holds only the two split.json files from x11prep)

Ranking source (PI decision at registration): the X5 / X7 per-agent labels were computed on the "label" split, i.e. on
exactly the 200 problems X11 scores on, and no labels exist on the eval problems; ranking by them would select and score on
the same problems. H1d therefore ranks agents from the X5 / X7 plan-evaluation per-problem data (math500_q15_7: 64 plans x
300 eval problems; code_c15_7: 32 plans x 178 eval problems), which is disjoint from the X11 problems.
- plain UV of agent a = accuracy(only_a) - accuracy(all_small) on the eval problems (point estimate); agents ranked by UV,
  ties in structural order (agentqo.policies.v2_rules.structural_order).
- confident_uv: agents whose 95% bootstrap CI lower bound (percentile; 2,000 paired resamples of eval problems, seed 0) of
  the per-problem difference correct(only_a) - correct(all_small) is > 0, ordered by UV; the rest in structural order.
- structural_topk: structural_order(workflow), as in the registered rules.
- ec_real_topk: dropped (it needs label-run resamples, which exist only on the X11 problems).
- eval-exhaustive: the plan with <= k upgrades with the best eval accuracy (ties: lower cost_units, then plan name).
Pick for a ranking at budget k: the plan that upgrades exactly its top-k agents (only_<a> for k = 1).
Scoring on X11 (X11a: 200 MATH-500, X11b: 200 MBPP+ held-out problems): regret_k = best X11 accuracy among all plans with
<= k upgrades minus the pick's X11 accuracy. HELD if, in both settings, the UV pick's regret is <= 0.02 at k = 1 and at
k = 2, AND at both k the UV regret exceeds the eval-exhaustive pick's regret by at most tau = 0.0134. Otherwise NOT HELD
(each condition reported). Note (PI): with plan-data UV the k = 1 UV pick (only_<top agent>) equals the eval-exhaustive
k = 1 pick by construction (both are the best single-upgrade plan on the eval problems, up to ties), so the "not worse than
eval-exhaustive by tau" condition is only informative at k = 2; the regret <= 0.02 condition applies at k = 1 and k = 2.
k = 3 is reported for all rankings (exploratory, no criterion). Offline analysis only (no extra
model calls), computed after X11 finishes; results in results/v2/X11/H1d/.

### L2-X12: all_small rerun with per-call logprobs, and H6b, registered 2026-11-18 14:38:00 UTC, before any X12 data

Status: EXPLORATORY under L2-X (own folder results/v2/X12, V2_DEVIATION=D-L2-X-code; included in results_v2_UPLOAD.zip,
FINAL/data_check.md and search ground truth notes). Optional: runs on VM-A only, after X11 completes, and only if it can start
before 2026-11-19 08:00Z; no block starts after 2026-11-19 14:00Z; VM-B is never touched. Accuracy-only (no TIMING_LOCK).
Nothing is deleted.
Code: v2-lease2-x 75da2c83 (= 18b3d7a0 + agentqo/backends/vllm_http.py _logprob_stats, agentqo/tasks/answers.py
gsm8k_answer_span, scripts/run_real_h3.py --logprob-columns; test_x12_logprob_stats; Mac suite 207 passed / 16 skipped).
The backend already requests logprobs on every call (logprobs=true, top_logprobs=1); X12 stores per call: mean_logprob (mean
token logprob of the completion), answer_text (the final numeric answer, same precedence as extract_gsm8k_number), and
answer_logprob / answer_first_logprob (mean / first logprob of the tokens overlapping that answer).
What: ONLY plan all_small (run_real_h3.py --plans all_small --logprob-columns), same models, prompts, max_tokens and cautious
verifier as the stored runs, greedy, with a fresh separate cache (data/cache/x12_vmA.sqlite on VM-A, so every call is new):
- math_q15_7 (Qwen2.5-1.5B-Instruct; max_tokens 256): eval_ext 400 (the P2 eval problems) and eval_x2 719 (the X2 problems);
- math_granite (granite-3.1-2b-instruct; max_tokens 512): eval_ext 400 (the P4 eval problems) and eval_x2 719 (X2).
Output results/v2/X12/<setting>/<eval|x2>/. Reported: the share of problems whose X12 final answer matches the stored
all_small answer (P2 / P4 / X2 traces), and X12 all_small accuracy vs the stored all_small accuracy.

H6b (RQ6, exploratory-confirmatory; next free label: H6 exists, H6b does not). A per-problem router that decides, after the
all_small run, whether to upgrade the verifier. Per setting:
- Outcomes (PI): small baseline = the X12 rerun's own all_small correctness (a rerun need not reproduce the stored answers;
  X4: ~6-10% of cells flip); upgraded outcome = the stored only_verifier correctness (P2 / P4 on eval, X2 on the held-out
  problems).
- Features (from the X12 all_small calls of the problem): answer agreement = share of the agents with a numeric answer whose
  answer equals the verifier's, aggregator answer == verifier answer (0/1), number of distinct answers; logprob features =
  verifier mean_logprob, verifier answer_logprob, aggregator answer_logprob, the minimum answer_logprob over agents, the mean
  of mean_logprob over agents (a missing value is replaced by the training mean).
- Model: L2-regularised logistic regression (C = 1, features standardised on the training set) predicting
  P(all_small wrong), trained on the eval problems (400).
- Decision: upgrade when P >= t. Cost per problem (API cost, registered tier prices small 0.10/0.50, large 2/10 USD per 1M
  input/output tokens): router = the X12 all_small cost + (if upgraded) the large verifier call of the stored only_verifier
  run (its tokens at large prices); fixed upgrade = the stored only_verifier plan's cost.
- Threshold t: on the eval problems, the candidate t (every distinct predicted P, plus 0 and 1.01) with the lowest mean router
  cost among those whose eval accuracy >= the fixed upgrade's eval accuracy - 0.01; if none qualifies, t = 0 (always upgrade).
- Test on the X2 problems (719): HELD if, in both settings, router accuracy >= fixed upgrade accuracy - 0.0134 AND router mean
  API cost <= 0.70 x the fixed upgrade's mean API cost. Otherwise NOT HELD (each condition reported). Offline analysis only
  (no model calls beyond the X12 reruns); results in results/v2/X12/H6b/.

#### L2-X11 addendum: H5c-b2 (RQ5 variant, confirmatory on X11), registered 2026-11-18 14:43:00 UTC AFTER X11 model calls started (14:34:01Z) but BEFORE any X11 output was read or analysed

Evidence at registration (checked on VM-A at 2026-11-18T14:42:44Z by file listing, row count and checksum only):
X11 per-problem rows existing on VM-A: 0 (no h3_per_problem.csv exists yet; X11a writes its outputs when the run ends).
Files in results/v2/X11 (4): code_c15_7/split.json (3,844 B), math500_q15_7/split.json (7,540 B),
math500_q15_7/plans/run_config.v2.json (471 B), provenance.jsonl (217 B). sha256 of results/v2/X11 as it stands (sha256 of
the sorted per-file sha256 list): c60c2a9e5a1b47bad76c6af8dbba6de76b64c892206d030377fad32deb320e76. No X11 analysis script has
run and no X11 output file has been opened. The Mac sync loop was paused at 14:42Z until this amendment is pushed; the Mac
mirror holds the same 4 files (no outputs).
H5c is unchanged and stays registered as is; H5c-b2 is a variant with only the racing rule changed ("good-enough" stopping).
(a) successive halving is not repeated.
(b2) paired eps-racing, eps = 0.0134, on the same X5 / X7 eval per-problem data, the same 30 seeded problem orders (seeds
0-29), 25 problems per step, the same tie-break as H5c (higher accuracy, then lower cost_units, then plan name). After each
step: leader = the live plan with the highest accuracy on the problems seen. For every other live plan p: d = correct(p) -
correct(leader) per problem, 95% normal CI mean +/- 1.96 sd / sqrt(n) (if sd = 0, use sd = 0.5). Drop p if its upper bound
< 0. STOP when every remaining non-leader plan has upper bound <= eps (no plan can beat the leader by more than eps), or when
one plan is left, or when the problems are exhausted; the pick is the leader.
Same scoring, comparator and criterion as H5c: each pick's accuracy on the X11 held-out problems; regret = best held-out
accuracy over all plans minus the pick's; comparator = the eval-exhaustive pick. HELD if, in both X11 settings, the mean
held-out regret of (b2) over the 30 seeds is within tau = 0.0134 of the exhaustive pick's regret, at <= 40% of the exhaustive
plan x problem evaluations. H5c and H5c-b2 are reported side by side; neither replaces the other. Offline analysis only;
results in results/v2/X11/H5c/ (both).
