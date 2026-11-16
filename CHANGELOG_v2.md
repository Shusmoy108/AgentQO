# CHANGELOG v2

Every v2 change and design decision, newest last. Branch `v2-dev`, cut from `h2-real`
(commit 0775671), because `h4_fit.py` and the Session 1 H2/H4 code are not on `main`.

## 2026-11-06

**Branch.** `v2-dev` from `h2-real`. Why: v2 reuses `h4_fit.simulate`, `run_real_h3.py`
and the Session 1 labeler, which live only there.

**Output directories (`agentqo/metrics/io.py`: `resolve_output_dir`, `mark_done`).** Every
v2 script writes `run_config.v2.json`. Same config in an existing directory = resume; a
different config = new directory with a numeric suffix (`_2`, `_3`, ...); `DONE` marks a
finished run, which a re-run skips. Why: the brief forbids overwriting results and asks for
resumable scripts; comparing configs stops a rerun with new flags from mixing into old files.

**Cache and trace format unchanged.** The SQLite `GenerationCache` schema and key
(model, messages, temperature, top_p, max_tokens, seed) are untouched; new fields go into
new CSV/JSON files or into trace `metadata`. Why: backward compatibility rule. Session 1
caches replay with zero new calls.

**M1 cost model (`agentqo/metrics/cost_model.py`, `scripts/v2/cost_report.py`,
`configs/v2_prices.yaml`).** Per-call API USD from token counts and the price table; GPU
seconds from measured latency; shared placement divides GPU seconds by the vLLM memory
fraction used in Session 1 (0.25 small, 0.55 large); GPU USD at 1/2/4 USD/h. Old cost units
(small 1, large 4) kept as a column. Why: prices must be editable without code changes, and
cost units keep v2 tables comparable with Session 1.

**M2 all-subsets plans (`scripts/run_real_h3.py --plans all_subsets`).** All 2^n
upgrade subsets; one problem's plans run in sequence on one worker, so shared prefixes are
generated once and the cache never races (problems never share prompts). Outputs
`h3_plans.csv` (paired bootstrap CIs vs all_small, 5000 resamples, seed 0),
`h3_per_problem.csv`, `h3_calls.csv` (per-call tokens and latency). Default `--plans`
keeps the Session 1 behaviour.

**M3 realistic labels (`ec_labeler.py`, `labels_v2.py`, `run_real_pipeline.py`).**
`--realistic` records q_base, per-strategy consequence, consequence from real disagreeing
samples (`ec_real`), and per-call counts. `--disagree-only` reruns an agent's descendants
only when a small-model resample disagrees with the base output, and otherwise counts the
consequence as 0. `labels_v2.csv` has exactly the columns in the brief; per-problem and
per-strategy tables are separate files. Why: H1a/H1c need real-error consequence and
rerun counts side by side with the synthetic numbers.

**M4 rules (`agentqo/policies/v2_rules.py`, `scripts/v2/rules_report.py`).** Rules
(ec_synthetic, ec_real, uv, confident_uv, ...) pick top-k agents for budgets 1..n;
estimators (additive, multiplicative, pairwise_corrected with m = 3 measured pairs) predict
plan accuracy. `rules_report.py` was added (not in the brief) to write `rule_plans.csv`,
`estimator_errors.csv` and `h1c.json`, which H1/H2 need.

**M5 Pareto (`scripts/v2/pareto.py`).** Plans x placements (separate, shared, shared_mps)
on accuracy, cost, p95 latency. Shared-placement latency uses the AgentIconq interference
model 1 + beta * u * omega through `h4_fit.simulate` (identity iso); betas in
`configs/v2_interference.yaml` are copied from the `h4_complete.zip` fit (shared 2.392/0.991,
shared_mps 2.072/0.332). Joint search vs two-step baseline, hypervolume in
`pareto_summary.json`; H3a in `constrained_best.csv`, H4a in `budget_best.csv`, H3c in
`latency_check.csv` when P5 data exist.

**M6 placement (`scripts/v2/run_placement.py`).** Runs plans with K problems in flight
against the servers already running in the named placement; bypasses the cache and fails
on any cache hit; optional nvidia-smi logging per VM. Why: placement is a server-side
setup, so the script times what is there rather than starting servers.

**M7 routing (`scripts/v2/routing_offline.py`).** Offline disagreement-triggered
routing from the per-problem label data: upgrade an agent only on problems where its K
small samples disagree. Single-agent only; pair routing is skipped (no hypothesis needs it).

**M8 HotpotQA (`agentqo/tasks/hotpotqa.py`, prompts, answers, library).** Distractor
dev set from the official URL, falling back to the Hugging Face rows API (the official host
did not resolve on 2026-11-06). Rows sorted by id, split seed 0: label 200, eval 300.
Workflow `hotpot_chain`: planner -> hop_1 -> hop_2 -> aggregator -> verifier (cautious).
Score = exact match after normalisation; F1 reported next to it. Fake backend answers
HotpotQA prompts so tests run offline.

**M9 models (`configs/v2_models.yaml`, `scripts/v2/model_env.py`).** One table of HF
ids, max tokens (math 256, Granite 512, HotpotQA 384) and Ollama tags.

**M10 driver (`scripts/v2/run_phase.sh`, `package_phase.sh`, `summarize_phase.py`).**
The brief's RESULTS FORMAT section was missing and the phases were not defined, so I
defined P1-P6 + final (listed at the top of `run_phase.sh`) and the SUMMARY.md layout
(status table, then each CSV as a table, JSON as a block, "Test run" banner off vLLM).
`package_phase.sh` writes SUMMARY.md, summary.json, MANIFEST.txt, a zip without SQLite
(final zip includes it) and commits CSV/JSON/MD to `v2-lease1` through a worktree, then
pushes (no force). `V2_PUSH=0` turns git off for test runs.

**Extra: `scripts/v2/adaptive_check.py`.** Simulates H5a (add 25 problems at a time,
stop when the leader's paired CI clears the runner-up) on `h3_per_problem.csv`.

**Data split for 400 problems.** GSM8K `eval_ext` = the Session 1 eval split extended
with unused test problems to 400, so P2 math has the 400-problem pool H5a needs.

**Verifier.** v2 phases set `AGENTQO_VERIFIER=cautious` (the Session 1 verifier that
helps). Known behaviour, unchanged: its "Final answer: N" output does not match
`_KEY_SPAN`, so `numeric_perturb` never fires on the verifier and the labeler falls back to
the other strategies.

## 2026-11-07

**Fixes from Ollama dry runs.** Fake-server `_ANSWER` regex matched the template
placeholder by backtracking (HotpotQA scored 0 on fake); now `\s*([^<\s][^<\n]*)`.
Power-logger test replaced fixed sleeps with polling (race). Planner `consequence_real`
test accepts None (the fake's good plans equal the reference).

**Dry-run findings that bear on the pre-registration (no hypothesis text changed).**
- H1c: the planner has a disagreeing resample on 10 of 10 math problems and alone is 1/5
  of all reruns, so "at most 1/5 of the full reruns" is close to unreachable on the math
  chain (measured: disagree-only used 32 of 50 reruns, 0.64, on 10 problems).
- H3b: two-step points are a subset of the joint search space, so joint hypervolume >=
  two-step always; only "strictly higher" is informative.
- HotpotQA prompts reach 3281 tokens (p99 2408); start vLLM with `--max-model-len 8192`
  for HotpotQA (Session 1 used 4096). Ollama (4096 context) did not truncate: max prompt 2729.
- Results are small enough to commit to `v2-lease1` as plain files (~7 MB per
  200-problem workflow of substitution JSON).

**Timing.** `PLAN_v2_times.md` from 10- and 20-problem Ollama runs of every module.

**Pre-registration.** `prereg/v2_lease1.md` committed with the hypotheses as given and a
table of how each is measured; later changes go in `prereg/v2_amendments.md`.

## 2026-11-07 (pre-lease fixes; amendments in `prereg/v2_amendments.md`)

**FIX 1, HotpotQA aggregator and verifier (bug fix, A5).** Cause: the aggregator
prompt put the question ~1,500 tokens above the answer slot (before 10 paragraphs), and
its last instruction was "for a yes/no question answer yes or no". The 7B model answered
"Yes" as if confirming the findings (e.g. hops found "The Frost Report", aggregator wrote
"Final answer: Yes"). The extractor was not at fault: it read "Final answer: Yes"
correctly. Fix (`agentqo/tasks/prompts.py`): both prompts restate the question just
before the instruction, ask for the shortest span (name, title, place, date, number,
short phrase), and allow yes/no only for a question asking whether something is true. The
verifier now writes KEEP or CHANGE, may change only when a paragraph contradicts the
answer, and must give a short span. A first variant that listed yes/no question openers
(Is, Are, Was, ...) still gave 32% yes/no aggregator answers on non-yes/no questions and was
dropped. Before/after numbers are below under "Acceptance".

**FIX 1, frozen HotpotQA split.** `data/splits/hotpot_v2.json` holds the label (200)
and eval (400) ids, written once by `python3 -m agentqo.tasks.hotpotqa` from the seeded
split; the loader reads ids from it and fails if the file or any row is missing.
`.gitignore` now ignores `data/*` except `data/splits/`. Label ids and the first 300 eval
ids are the same as before.

**FIX 2, disagree-only definition.** A Q+ rerun is skipped only when the small and the
large output keys at the agent are equal (Q+ = baseline correctness); agents without a
comparable key (the planner, or an output with no extractable key) are never skipped.
Before, the planner was skipped when its text matched exactly. Real-error consequence
was already undefined (None) when no disagreeing resample exists, but `ec_real` reported
0 for an agent with none at all; it is now blank, and `labels_v2.csv` gains
`ec_real_n_used`. Rules rank a blank `ec_real` last.

**FIX 3, provenance.** `run_phase.sh` calls `summarize_phase.py provenance` at the start
of every (re)start of a phase: one line in `provenance.jsonl` with the full HEAD commit and
a dirty flag (tracked changes anywhere, or untracked files under agentqo/, scripts/,
configs/, data/splits/, tests/). With `V2_BACKEND=vllm` (a lease phase) a dirty tree
refuses to run. SUMMARY.md and summary.json report the commits run, the dirty flag, and
the commit at packaging time; a phase resumed at more than one commit is flagged.

**FIX 4, sample sizes (A8).** GSM8K pools now follow the Session 1 F4/F5 order exactly
(checked against the Session 1 LABEL 500 and EVAL2 300 id lists): `--split label` for
GSM8K = 100 dev + Session 1 extra[0:400], first n; `eval_ext` = EVAL 200 + Session 1
EVAL2 (extra[500:800]). Before, `eval_ext` drew its extra 200 with a different seed and
overlapped the Session 1 LABEL problems; the first 200 eval problems are unchanged. Phases:
P1/P3/P4 math labels 200 (`label`), HotpotQA eval 400.

**FIX 5, GPU cost from throughput (A7).** `cost_model.py`: the per-call column is renamed
`gpu_usd_latency` (and `gpu_usd_latency_<rate>`, `gpu_usd_latency_shared_<rate>`). New:
`measured_throughput_costs` (P5: GPUs reserved x wall / problems; separate 2, shared 1),
`tokens_per_second` (per placement and model, from P5 calls), `estimated_throughput_costs`
(`gpu_usd_throughput_<placement>`, labelled estimated), `rank_agreement` (Kendall tau-b).
`cost_report.py --placement` writes `placement_costs.csv` and the A3 taus. `pareto.py`
uses `gpu_usd_throughput` by default (falls back to `gpu_usd_latency` with a warning
when no P5 data exist; placements without P5 data are left out, not priced NaN), and H4a
uses the separate-placement throughput cost. Simplification, marked in the code: output
tokens only (prefill ignored), max rate over runs.

**A2 output.** `pareto.py` writes `limit_gaps.csv` (joint minus two-step accuracy on a
decile grid of cost and p95 limits) and `a2_*` keys in `pareto_summary.json`.

**A1 output.** `h1c.json` adds per-agent UV change, max change, the confident_uv
budget-1/2 picks in both modes, and whether the rerun share is at most 0.5.

**A4 output.** `routing_offline.py --labels --workflow` marks the one primary row
(`samples_disagree` for the confident_uv budget-1 agent) and writes `routing_summary.json`.
Known gap: the planner has 3 samples (Session 1 cost cap), not 5.

**FIX 1 acceptance (Ollama, Qwen 1.5B/7B, 40 HotpotQA label problems, cautious verifier).**

| | EM | F1 | yes/no on the 39 non-yes/no questions (final / aggregator) | verifier changed the answer |
|---|---|---|---|---|
| all_large before | 0.250 | 0.352 | 51% / 54% | 7.5% |
| all_large after | **0.475** | **0.635** | **0% / 0%** | 17.5% |
| all_small after | 0.225 | 0.411 | 0% / 0% | 17.5% |

Thresholds (EM >= 0.25 or F1 >= 0.40; under 10% yes/no) are met. The one yes/no question
(gold "no") is now answered "no" by all_large (before: "yes"). The verifier's net effect is
-2.5 EM points on all_large (aggregator EM 0.500, final 0.475) and +7.5 on all_small. The
probe script is a scratch file, not part of the repo; the numbers come from the same
executor, prompts and cache as the phases.

**Dry runs after the fixes (Ollama, 20 problems, P1/P2/P6 for math and HotpotQA, V2_PUSH=0).**
All phases exit 0 with no unfinished steps; provenance records clean commits (`74dc70e` for
P1/P2, `a6d9f17` for P6). HotpotQA eval all_large accuracy 0.40 (0.15 before FIX 1),
all_small 0.10. FIX 2 check on math: 47 Q+ reruns skipped; on 6 of them the full rerun
gave a different correctness despite equal keys, so UV differs by up to 0.10 (aggregator)
between modes. Equal keys do not mean equal downstream text on real models, so Q+ =
baseline is exact only on the fake backend. Top-2 agents and confident_uv budget-1/2 picks
agree in both settings. Rerun share 0.59 (math) and 0.825 (HotpotQA). Throughput GPU cost
ran from the M6 separate-placement output only, so shared placements are left out of the
dry-run Pareto (A3 tau separate: math 0.53, HotpotQA 0.56).

## 2026-11-07 (A3 prompt: A10, E3, E4, A11, lease tag)

**A10.** New hypothesis H1c-b in `prereg/v2_amendments.md` (top-2 agents and confident_uv
budget-1/2 picks unchanged by key-based skipping); A1 left as registered.

**E3 (exploratory).** `ec_labeler.py` records `outputs_identical` (small and large text equal
after collapsing whitespace) on realistic records; `labels_v2.skip_variants` computes, from
the full-mode per-problem labels, the rerun share and per-agent UV error of the key rule and
of the exact rule; `rules_report.py` writes them to `h1c.json` (`e3_skip_variants`). The
offline key rule reproduces the --disagree-only rerun counts (tested on the fake backend,
and 59/100 on the math dry run). The exact rule is exact by construction: identical text
gives identical downstream prompts, and the fake-backend test checks UV error 0.

**E4 (exploratory).** `v2_rules.logit_additive`, in `estimator_errors.csv` next to the others.

**A11.** `cost_model.fit_token_rates`: per (model, placement), NNLS of per-call latency on
prompt and completion tokens gives the prefill/decode shape; one scale per (model, placement)
makes each P5 run's calls add up to the GPU time the model held. `estimated_throughput_costs`
now uses a_m x prompt + b_m x completion per tier and the model name from the calls, and
sets `gpu_cost_basis_<placement>` to `estimated_rates` or `fallback_latency` (latency price,
memory fraction when shared). The output-tokens-only `tokens_per_second` is removed.
`cost_report.py` writes `token_rates.csv`, cost-basis counts and `a3_basis_*`; `pareto.py`
no longer switches silently: every candidate has `cost_basis`, `budget_best.csv` has
`gpu_cost_basis`, the summary has `cost_basis_counts` and `any_fallback`. Placements without
rates are now priced by the flagged fallback instead of left out.

**P5 calibration sets.** `V2_P5_CAL=qwen_hotpot|qwen3_14_math|granite_math` runs all_small and
all_large, K = 16, 64 problems, 3 repeats, under the running placement, into
`P5/cal_<set>_<placement>`. P6 feeds every P5 run to the rate fit (rates are keyed by model).
Qwen 3B/14B was not in P5 before; it is now a calibration set.

**hypotheses.md.** `scripts/v2/hypotheses_report.py` (run at the end of P6) writes
`P6/hypotheses/hypotheses.md` and `.json`: the values behind each hypothesis and amendment
per setting, and a cost-basis table (estimated vs fallback per placement; measured only in
`placement_costs.csv`). SUMMARY.md of P6 embeds it.

**Lease tag.** `summarize_phase.py provenance --lease` (used for vllm phases) refuses to run
unless HEAD is the `v2-lease1-start` commit, or `V2_DEVIATION` names an id present in
`prereg/v2_amendments.md`; provenance records the tag commit and the deviation.

**Dry run (Ollama, 20 problems, commit 8f90567, clean; P1/P2 replayed from the cache).**

| | math Qwen 1.5B/7B | HotpotQA Qwen 1.5B/7B |
|---|---|---|
| E3 exact-skip: reruns used / full (share), max UV error | 88/100 (0.88), 0.000 | 77/80 (0.963), 0.000 |
| Key-skip (A1/A10): reruns used / full (share), max UV error | 59/100 (0.59), 0.100 | 66/80 (0.825), 0.050 |
| E4 logit_additive MAE held-out (all) | 0.099 (0.086) | 0.207 (0.160) |
| additive / multiplicative / pairwise MAE held-out | 0.132 / 0.177 / 0.095 | 0.113 / 0.348 / 0.102 |
| A10 top-2 and confident_uv picks unchanged | yes | yes |

A11 rates fitted on the Mac M6 run (Ollama, separate placement only, 120 calls per model;
GPU-seconds per token): qwen2.5:1.5b-instruct a = 0.00477, b = 0.01621; qwen2.5:7b-instruct
a = 0.00899, b = 0.03541. Shared and shared_mps had no Ollama run, so their costs are flagged
fallback_latency in the dry run.

## 2026-11-07 21:59:58 UTC: q4 setting (4-bit laptop run)

**A12 registered** in `prereg/v2_amendments.md` before any q4 data: a separate 4-bit Ollama
setting (Qwen2.5 1.5B/7B Q4_K_M), math and HotpotQA, label 200 + eval 200 each. Why: test
whether findings hold under quantization and add power before the lease; never pooled with vLLM.

Decisions (made without asking, per the q4 prompt):
- q4 runs on branch v2-q4 = tag v2-lease1-start + the A12 commit, no code change.
- Own cache `data/cache/v2_q4.sqlite`: no q4 result reuses dry-run calls made before A12.
- Sizes via `V2_N=200` in the existing driver (`run_phase.sh`): label 200, math eval = first 200
  of eval_ext, HotpotQA eval = first 200 of the frozen eval list.
- `package_phase.sh` pushes to v2-lease1 by design, so `run_q4_all.sh` calls it with
  `V2_PUSH=0` (summary, manifest, zip) and commits and pushes CSV/JSON/MD to v2-q4 itself.
- Q4-5 runs the P6 steps directly (cost from API prices and tokens, rules, routing, adaptive,
  Pareto on api_usd only) and then marks H3a, A2, H3c, A3, H4a "not testable on Mac" in
  hypotheses.md and drops its GPU cost-basis table (it would only show latency fallbacks).
- Ollama is run by the driver (`ollama serve` with OLLAMA_NUM_PARALLEL from the throughput
  test, OLLAMA_KEEP_ALIVE=-1) instead of the brew service, so the parallel setting can be set.
- Deadline 2026-11-15 23:00 UTC: the code cannot change, so the driver stops the running step
  with SIGTERM once the deadline passes; every finished call is in the cache, so a re-run
  resumes and redoes at most the problems in flight.
- Disk: 7.8 GB free at the start. The driver deletes only results/v2_dry*/ and results/v2_t20/
  when under 10 GB (about 15 MB); it continues with a logged warning, and fails a step only
  under 2 GB free, to protect the SQLite cache.
- Files over 20 MB are not pushed to git (they stay in the cache zip).

## 2026-11-12 06:52:05 UTC: A13 hotpot_chain_isolated, A14 Granite on HotpotQA (branch v2-dev)

**A13 and A14 registered** in `prereg/v2_amendments.md` before any data for them.

Code:
- `create_hotpot_chain_isolated_workflow` (key `hotpot_iso`): same DAG as hotpot_chain, name
  `hotpot_chain_isolated`. `prompts._hotpot_isolated_prompt`: the aggregator gets the hotpot_chain
  prompt with the paragraphs replaced by the question line. The verifier gets the question, the hop
  outputs and the proposed answer; its two references to paragraphs read "findings", because it
  has none. Planner and hop prompts are unchanged (tested byte-identical).
- `run_real_h3.py` accepts any `hotpot*` workflow with `--dataset hotpotqa`.
- `run_phase.sh`: P1/P2 add `hotpot_iso_q15_7` after the HotpotQA steps (VM-A); P4 adds
  `hotpot_granite` and `hotpot_iso_granite` after Granite math (VM-B), labels 200, all 32 plans on
  400, max_tokens 512. The default `V2_SETTINGS` is now "math hotpot hotpot_iso", and P4 honours it.
  P6 analyses the three new settings; `hypotheses_report.py` lists them (one column per task and family).
- `configs/v2_models.yaml`: Ollama tags `granite3.1-dense:2b` / `:8b` for Mac dry runs.
- Granite-only short-span line (decision made with the user after the dry run): `AGENTQO_HOTPOT_SPAN=1`, exported
  in P4 around the Granite HotpotQA steps, adds "The final answer is the span alone, not a
  sentence." to the HotpotQA aggregator and verifier prompts. Qwen prompts are unchanged, so q4
  and the Qwen lease settings use the same prompts as before. Within-family comparisons (A13)
  use identical prompts; raw Qwen vs Granite accuracy includes this difference.
- Tests: isolated prompts (no paragraphs downstream, hop outputs present, upstream unchanged),
  registry, span line (only with the flag, only aggregator/verifier), driver P4 order, and the
  fake-backend HotpotQA driver test now runs hotpot and hotpot_iso. pytest: 184 passed.
- `PLAN_v2_times.md`: A13/A14 rows; total ~41 h (10x rule) / ~8.2 h (Session 1 rate).

**Dry run (Ollama, 10 HotpotQA eval problems, all_small / all_large, cache
`data/cache/v2_dry_a13.sqlite`, uncommitted tree on v2-dev).** The A13/A14 checks (EM > 0, short spans, no wrong yes/no) pass.

| setting | all_small EM / F1 | all_large EM / F1 | wrong yes/no | mean answer words |
|---|---|---|---|---|
| Qwen 1.5B/7B hotpot_chain_isolated | 0.20 / 0.31 | 0.50 / 0.71 | 0 | 3.6 / 2.9 |
| Granite 2B/8B hotpot_chain, no span line | 0.30 / 0.34 | 0.00 / 0.26 | 0 | 8.0 / 10.4 |
| Granite 2B/8B hotpot_chain_isolated, no span line | 0.20 / 0.28 | 0.10 / 0.35 | 0 | 8.3 / 10.3 |
| Granite 2B/8B hotpot_chain, span line | 0.40 / 0.47 | 0.30 / 0.53 | 0 | 4.9 / 5.5 |
| Granite 2B/8B hotpot_chain_isolated, span line | 0.30 / 0.33 | 0.30 / 0.56 | 0 | 2.6 / 4.9 |

Without the span line Granite answered in sentences ("Diplazium has more species than Mahonia.").
The first Granite dry run was stopped by Claude Code at 2/10 problems (Mac memory low) and
resumed from the cache. Docs outside the repo were not changed.

**Tag.** `v2-lease1-start` moved from 55c6590 to the commit carrying this entry. To avoid a force-push,
the old remote tag was deleted and the new one pushed.

## 2026-11-16 04:06:51 UTC: A13 restated, A14 revised, A15 Phi, P0 smoke test, fresh caches (branch v2-dev)

**Registered** in `prereg/v2_amendments.md` under one timestamp, before any lease data. No model
was run on the Mac (no Ollama, no vLLM); all checks below use the fake backend.

Choices made without asking (as instructed), each also stated in the amendment:
- A13 was already registered on 2026-11-12 with the same text, and its code was already built
  and tested. The text is restated with the new timestamp; the 2026-11-12 registration stands.
- A14 differs from the 2026-11-12 text by "max-model-len 8192" and the validation sentence, so it
  is appended as a superseding text.
- Phi: max_tokens 512 for math too (A15 gives none; follows Granite). The A14 short-span line is
  turned on for Phi HotpotQA, as for Granite, because the code cannot change after the tag. No Phi
  P5 calibration set, so Phi GPU cost uses the latency fallback.
- Phi runs as a new phase **P4b** (VM-B, after P4), not inside P4, because it needs different vLLM
  servers and `use_models` checks them.
- "Scores 0" = none of the 10 smoke answers (5 problems x all_small + all_large) is correct. A
  per-plan rule would skip a 1.5B/2B setting about 1 time in 4-6 by chance at EM 0.2-0.3.
- The smoke test uses the first 5 label problems, which the labels step runs anyway.

Hugging Face (API metadata only, nothing downloaded): microsoft/Phi-3.5-mini-instruct and
microsoft/phi-4 exist, gated=false, license mit.

Code:
- `configs/v2_models.yaml`: `phi_small`, `phi_large`, max_tokens `phi: 512`.
- `scripts/v2/run_phase.sh`: phase **P0** (`V2_P0=qwen|granite|phi`) smoke-tests the five new settings
  (Qwen isolated, Granite hotpot, Granite isolated, Phi math, Phi hotpot). `labels`/`plans` call
  `ready`, which smoke-tests a new setting P0 has not checked, and returns without running for a
  setting in `results/v2/P0/skips.tsv`. Phase **P4b**: Phi math, then Phi hotpot_chain. P6
  analyses `math_phi` and `hotpot_phi`; `final` copies P0 and P4b. The fake backend's smoke run
  is not judged (it cannot answer real problems).
- New `scripts/v2/smoke_check.py`: `check` (the P0 rule) and `skip` (by hand, e.g. time short).
  Both write `skips.tsv`, `FAILURES.md` and a `D-P0-<setting>` deviation in the amendments.
- `summarize_phase.git_state`: `prereg/v2_amendments.md` and `FAILURES.md` no longer make the
  tree dirty, so a P0 skip logged during the lease does not stop later lease phases.
- `run_real_h3.py`: each `h3_traces.json` entry also has `pred` (the extracted final answer).
- Session 1 caches no longer exist: the vLLM cache default is now `data/cache/v2_lease1.sqlite`
  (was `vllm.sqlite`, the Session 1 name); nothing looks for a Session 1 cache.
- `hypotheses_report.py`: columns `math_phi`, `hotpot_phi`.
- Tests: smoke rule (score 0, wrong yes/no, missing traces) and skip logging; P0 on the fake
  backend then a skip gating P1; P4b order; lease logs do not dirty the tree; the HotpotQA
  labels test now also runs hotpot_chain_isolated end to end on the fake backend.
- During development, two fake-backend runs (before the "not judged" rule) appended stray
  `D-P0-hotpot_iso_q15_7` lines to the amendments and created FAILURES.md; both were reverted
  before this entry and never committed.
- `PLAN_v2_times.md`: q4 call counts; total ~427,000 calls, ~67 h (10x rule) / ~11.3 h
  (Session 1 rate); VM-B ~46 h / ~6.0 h.

## 2026-11-16 04:27:11 UTC: A16 multi-tier, A17 10-agent workflow, 72 h lease plan and time-budget cut (branch v2-dev)

**Registered** A16, A17 and L2 (lease structure: 2026-11-16 12:00 to 2026-11-19 12:00 UTC, VM
order, cut order) in `prereg/v2_amendments.md`, before any lease data. No model was run on the
Mac; all checks use the fake backend.

Choices made without asking (as instructed), each also stated in the amendment:
- A16 1.5B->7B labels are the P1 `math_q15_7` labels (same problems and models); only 1.5B->14B
  labels are run.
- "MAE over the 729 plans" is read as in H2a: held-out plans, with all-plans MAE next to it;
  (a) needs both independence estimators >= 5 points; (b) needs pairwise below both.
- 14B API price 4.00/20.00 USD per million tokens (7B price x 14/7), cost units 8.
- A17 eval = first 200 of eval_ext, max_tokens 256, GSM8K, cautious verifier.
- First request said "A17 on VM-B after P4b, before Phi"; the follow-up moved it to VM-A after A16
  (phase P2c), which is what is built.
- Hours for the cut check are the conservative 10x-rule estimates, with a 4 h reserve; a cut also
  cuts the earlier settings in the cut order on that VM, so the order holds. E1 and the P5 K=1
  runs are outside `run_phase.sh` and are cut by hand.

Code:
- `XL_FIDELITY` (tier `xl`), `VLLM_XL_MODEL`; `VLLM_ENDPOINTS` may be keyed by served model id
  (checked before tier names), so the same servers serve 1.5B/7B, 1.5B/14B and 1.5B/7B/14B.
  `model_env.py` takes an optional third model and checks its server.
- `run_real_h3.py --tiers` (default `$V2_TIERS` or small,large): `tier_plans` enumerates every
  tier per agent (small,large is exactly the old 64-plan list and order); plans run per problem in
  sequence, so shared prefixes are generated once. `h3_plans.csv` has `tier_<agent>` columns for
  all_subsets runs. `--plans all_xl` for the A16 smoke test. The dry run counts distinct prompts
  per problem from the DAG.
- `pairs_to_measure` drops pairs that are not plans (same agent twice); binary results unchanged.
- New `scripts/v2/tiers_report.py` (A16 a, b, c). `configs/v2_prices.yaml`: xl prices;
  `price_plans` treats a tier missing from the shared-memory split as a whole GPU.
- `run_phase.sh`: P2b (A16) and P2c (A17) on VM-A; P0 options `tiers` and `complex`; `budget`
  (time-budget cut and A17 200->100 reduction, default lease end on vllm, `V2_HOURS_<setting>`
  overrides); smoke runs marked once per setting (`SMOKED`), so a later step never re-runs a
  smoke test with different servers; P6 analyses `complex_q15_7` and runs `tiers_report.py`.
- `smoke_check.py`: `reduce` and `moved`; `--root` for FAILURES.md and the amendments (tests
  write to a temp dir, never the repo); `check` judges every plan in the traces.
- Tests: tier enumeration and order, xl routing by model id, A16 phase + P6 on fake, A17 1,024 plans
  + reduction + cut, cascade cut, moved settings, phase order; pairwise on tier options.
- `PLAN_v2_times.md`: sized to the 72 h lease. ~830,000 calls; ~109 h at the 10x rule (VM-A
  ~51 h, VM-B ~54 h, both within 72 h with ~14-16 h slack) or ~16 h at the Session 1 rate.

## Lease 2 operations log (Chameleon KVM@TACC, 2026-11-16 to 2026-11-19; code at tag v2-lease1-start = 252a12b)

Operational choices made during the lease (no code change; the tag is what runs):
- 2026-11-16 12:55Z The CC image on these VMs is Ubuntu 22.04 with Python 3.10; vLLM 0.32.0 needs >= 3.11.
  Python 3.12 installed with uv into /mnt/data/python, venv /mnt/data/venv. vLLM 0.32.0+cu129 and torch
  2.13.0+cu129 (the pinned versions) installed; torchcodec removed (CUDA 13 only).
- Everything large lives on /mnt/data (clone /mnt/data/AgentQO, HF_HOME=/mnt/data/hf, caches /mnt/data/cache).
  13:01Z The first model prefetch ran in a tmux session without HF_HOME and wrote 23 GB to ~/.cache on the
  root disk (root fell to 1-3 GB free); moved into /mnt/data/hf/hub and the prefetch restarted with the env.
- The VMs have no git credentials (no tokens on the VMs), so phases run with V2_PUSH=0 and package_phase.sh
  zips on the VM; the Mac pulls every 5 min and pushes each gated phase's CSV/JSON/MD to v2-lease1 from a
  Mac worktree (same summarize_phase.py copy filter). VM-B's P0 goes to results/v2/P0_vmB (both VMs run P0).
- Phases run from a per-VM queue (/mnt/data/queue_{A,B}.sh, outside the tree): server start/stop per phase,
  3 retries with 2/5/15 min backoff (dead servers restarted between tries), failures to results/v2/FAILURES.md.
- Server ports: small 8001, large 8002, xl (14B, A16) 8003; VLLM_ENDPOINTS keyed by model id.
  --max-model-len: 8192 for any server that serves HotpotQA in that phase (Qwen P0/P1/P2, Granite, Phi),
  4096 for math-only phases (P2b, P2c, P3). max-model-len only bounds context length; outputs are unchanged.
- P0 on VM-A runs qwen, tiers and complex under one 3-server config (1.5B 0.15 / 7B 0.30 / 14B 0.45),
  so the 14B server starts once for P0; P1/P2 then use 0.25 / 0.55.
- Time budget: V2_LEASE_END=2026-11-19T06:00Z (the GPU cutoff), V2_RESERVE_HOURS=6 (P5, P5 cal, E1).
- No sqlite3 CLI on the image; cache backups use Python's sqlite3 Connection.backup (same online backup API).
- Model prefetch covers P5 too: VM-A also gets Qwen 3B and Granite 2B/8B (small side of separate placement,
  both sides of shared), VM-B also gets Qwen 7B (large side of separate placement).
- 13:10Z VM-A reaches VM-B's vLLM ports over the private network (10.56.2.39), so separate placement works.
  No VM-A -> VM-B SSH key was installed, so run_placement.py's VM-B power logger (which SSHes) is not used:
  P5 runs with V2_VMS="gpu_a=local", and VM-B's power during P5 comes from its continuous 1 s nvidia-smi log
  (logs/v2/power_vmB.csv), cut to each P5 run's time window. Both VMs log power for the whole lease.
- 13:30Z NEXT block received and applied: (1) network check VM-A -> VM-B vLLM ports OK, in STATUS.md;
  (2) clocks recorded in P0/env.txt (chrony, offset < 1 us, no change needed); (3) h4 refit with
  placement_test.py logged as lease-time deviation D-L2-h4grid in prereg/v2_amendments.md, to run after
  P5's main blocks on shared and shared_mps per V2_P5_CAL model pair (+ separate cells as the L_iso
  baseline h4_fit needs); (4) Python 3.12 build and the root-disk incident in P0/env.txt; (5) at GATE P4b,
  a "spare time" line in STATUS.md; nothing unregistered starts on spare time.
- 13:40Z NEXT block 2: confirms VM-A -> VM-B HTTP (VM-B servers bind 0.0.0.0). Note: no earlier check in this
  lease failed (13:10Z :8002 Granite 8B OK; 13:30Z :8001 Qwen 3B and :8002 Qwen 14B OK; only :8003, unused
  on VM-B, had no answer). P5 separate calls VM-B at http://10.56.2.39:<port>, and the same curl check from
  VM-A runs right before the first separate run (result to STATUS.md and here). Items 2-5 of NEXT block 1
  stand (clock, D-L2-h4grid, env.txt done; spare-time line at GATE P4b pending).
- 13:55Z NEXT block 3 (disk projection): du of /mnt/data and the clone's results/, logs/, data/cache/ on both VMs;
  growth sampled 13:43-13:53Z (VM-A P2 7.4 KB/call, VM-B P3 14.4 KB/call; prefetch done, so only run data grows).
  Projected /mnt/data free: VM-A 93 -> ~91 (P2b) -> ~88 (P2c) -> ~84 GB (P5 + final zip); VM-B 69 -> ~69 (P3)
  -> ~66 (P4) -> ~63 GB (P4b), at a conservative 15 / 29 KB per call. Nothing projected below 25 GB, so no trace
  packing or cache deletion was done. Details in STATUS.md. Re-check at each GATE.
- 15:45Z P2b push to GitHub was rejected: results/v2/P2b/math_tiers/plans/h3_calls.csv is 120 MB (> 100 MB limit).
  Fix (Mac tooling only, no code at the tag): that file is committed as h3_calls.csv.gz (15 MB, gzip -9); the
  uncompressed file stays in the P2b zip and the Mac mirror. tools/mac_sync.sh now gzips any file > 95 MB in the
  git copy before commit, so P2c/P4b cannot hit the limit. Sync loop restarted with the 6 h backup schedule kept.
- 17:15Z GATE P4b: VM-B queue done 17:04Z (VM-A 16:35Z). Spare-time line written to STATUS.md: ~60.8 h to the
  06:00Z cutoff, ~6.5-7 h of registered work left (P5, P5 cal, h4 refit, E1, P6, final) -> ~54 h spare per VM.
  Nothing unregistered started.
- 18:20Z NEXT block 4: L2-X registered and pushed (6f612c7b) before any X data. P5 started now (P1-P4 done):
  Mac orchestrator tools/p5_orch.sh drives VM blocks (/mnt/data/p5.sh, lease tooling outside the tree):
  separate -> shared (VM-B runs the shared cal sets on its own GPU meanwhile) -> shared_mps -> qwen_hotpot
  shared cal -> separate cal sets (VM-B serves each large model). K=16 via run_phase.sh P5; K=1/32 (E2)
  via run_placement.py into P5/<placement>_k1|_k32. granite_hotpot and phi_math cal sets run with
  run_placement.py (run_phase's V2_P5_CAL lists only the three registered sets). VM-B power in separate
  runs comes from its background log (no VM-A -> VM-B ssh key; none added). Phi-3.5-mini downloaded to
  VM-A for the phi_math separate cal. mac_sync: block gates P5-<block> push the P5 folder (VM-B: P5_vmB).
  X items: X4 and parts of X1/X2 need code changes, so they are not run; exact changes in STATUS.md.
- 2026-11-16T20:12:40Z X3 STARTED/RESUMED on VM-B (resumes from the lease cache)
- 20:12Z NEXT block 5: X3 (L2-X) started on VM-B's idle GPU, before P6 (V2_DEVIATION=L2-X; code at the tag):
  Qwen2.5-7B :8001 0.25, Granite-3.1-8B :8002 0.27, Phi-4 :8003 0.40 on one H100, by model id; smoke 5 problems
  (all_small/all_large/all_xl), labels 200 (Qwen7B->Granite8B, Qwen7B->Phi-4), 729 plans x 200, into results/v2/X3/.
  P5 priority: VM-B's lq.sh srv_start now kills X3 (session + run_real_* processes) and stops its servers before
  any other block starts servers on VM-B, so no P5/H4 latency run shares VM-B's GPU with X3. A watcher on VM-B
  (x3watch) resumes X3 from the cache after 3 idle minutes (no servers, no blocks, GPU < 1 GB). Start, pause and
  resume times are copied from VM-B's x3_events.log into STATUS.md and here.
- 2026-11-16T21:09:24Z X3 PAUSED on VM-B before B-serve-Q7_8002_8192 starts its servers (X3 servers stopped, GPU freed)
- 23:05Z NEXT block 6: STATUS NOW lines pushed (02f9b2ab). X code changes approved and made on branch
  v2-lease2-x (eeb54603, from the tag; separate clone /mnt/data/AgentQO-x on both VMs; tag clone untouched):
  per-request start/end, A16 tier plans in run_placement, GSM8K eval_x2 (719) and HotpotQA extra (600),
  AGENTQO_SEED_SALT. 6 new tests; full suite 195 passed, 8 skipped. Recorded in prereg/v2_amendments.md
  as D-L2-X-code. X3 milestone gates (smoke, labels) pushed; their "FAILED/partial" text is a gate-file
  format slip, corrected in STATUS.md.
