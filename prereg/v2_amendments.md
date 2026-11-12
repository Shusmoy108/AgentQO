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
