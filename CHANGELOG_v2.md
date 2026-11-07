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
