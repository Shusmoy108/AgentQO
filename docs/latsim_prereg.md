# latsim pre-registration: whole-plan latency predictor

Frozen: tag `latsim-frozen-20261117T133315Z`, commit `04c5bbde1fd283ca424b0d383bdee91c4a73779d` (branch v2-latsim, cut from origin/v2-lease1 a0abe77c).
Written and pushed before any X1, X1b or X6 latency file was opened.

## What is frozen

- Code: `agentqo/latsim/` (sim.py, fit.py, predict.py, baselines.py, evaluate.py), tests `tests/test_latsim.py`.
- Fitted parameters: `results/latsim/params.json` (per-model o, c, a, b, e; betas per pair and placement; beta quantile).
- Predictions: `results/latsim/predictions.csv`: every plan of every setting (h3_calls of P2, P2b, P2c, P3, P4, P4b),
  placements separate / shared / shared_mps, K = 1, 4, 8, 16, 32, for latsim and both baselines (h3c, mean_sum).
  Evaluation is a join of this file with measured summaries; nothing is recomputed after the freeze.
- In-sample check on the fit data: `results/latsim/p5_insample.csv`.

## Fit data (only)

results/v2/P5 (separate / shared / shared_mps at K = 1 / 16 / 32, calibration sets) and results/v2/P5/h4grid
(separate-placement request logs; betas from each pair's fit/fit_results.json and fit/mps_fit.json). Shared and MPS
P5 runs are used only to choose the beta quantile (p50 vs p95 fits), not to fit any parameter. Token counts per call come
from each setting's h3_calls (P2 / P2b / P2c / P3 / P4 / P4b), which are inputs, not latency targets.

## Model

See the docstrings of `agentqo/latsim/sim.py` and `fit.py`. In short: one fluid vLLM server per model (prefill c s/token
that stalls decoding; decode step a + b n + e KV/1000; client overhead o), problems replay their calls in executor order,
K problems in a closed loop, interference while another model's server on the same GPU is busy: rate / (1 + sum beta).
Pairs without a grid borrow betas from the grid pair closest in log model size (Phi-3.5-mini / Phi-4 -> q3_14;
math_tiers 1.5B/7B/14B: 1.5B-7B -> q15_7, pairs with 14B -> q3_14). No 32B parameters exist, so X6 32B is not predicted.

## Held-out tests (never fitted on)

1. X1: results/v2/X1*/<setting>/<placement>/placement_summary.csv (K = 16; separate + shared; complex_q15_7 and
   math_tiers shared only).
2. X1b: same layout under results/v2/X1b* (K = 1, 4, 8, 32), when it lands.
3. X6 latency (7B / 32B, separate): reported as not predictable (no 32B fit data); 7B-only plans are predicted only if
   predictions exist for that setting (they do not: X6 settings are not in the frozen file).

Measured value per (setting, plan, placement, K) = mean over repeats of p50_s and p95_s.

## Metrics (per setting x placement x K, per plan type, and pooled)

Share of plans with |pred p95 / meas p95 - 1| <= 10% and <= 20%; MAPE of p50 and p95; Kendall tau between predicted and
measured p95 over plans; median signed p95 error (bias). Same for the baselines h3c (P6's H3c predictor, reproduced
exactly: 63/63 P6 latency_check rows, 0.492 within 10%) and mean_sum (sum of mean call latencies).

Success criterion stated in advance: latsim's pooled X1 share of plans within 10% on p95 is higher than h3c's on the same
plans (the H3c reference value is 0.49).

## Revisions

Any change after the freeze gets a new tag `latsim-rev<N>-<UTC>` and is reported next to the frozen result, never instead
of it.

### rev1 (tag `latsim-rev1-20261117T134155Z`, commit 2009dcd1, 2026-11-17 13:41 UTC, after the frozen X1 scoring)

Fit leaves out P5 runs where a model first meets the block's problems (cold vLLM prefix cache; `fit.cold_runs`), so
parameters describe warm servers. Motivation: frozen X1 failure analysis (HotpotQA overpredicted on 2+-large plans) and
P5's own cal_qwen_hotpot repeat-0 runs (p95 2.1x repeats 1-2). Fit data unchanged (P5 + h4grid); no X1 value used.
Frozen predictions are kept and reported next to rev1's in results/latsim/REPORT.md.

## Added baselines H3c-fair and mean_sum-fair (registered before any of their scores on X1 / X1b)

Frozen: tag `__H3CTAG__`, commit `__H3CCOMMIT__`. Code `agentqo/latsim/h3cfair.py` (predictions) and
`agentqo/latsim/compare.py` (analysis); predictions `results/latsim/h3cfair/predictions.csv` (every plan x
separate / shared / shared_mps x K 1/4/8/16/32). The registered H3c result (P6 value 0.492; column `h3c`) is kept
exactly as is; H3c-fair is an added, separately labelled baseline.

Motivation: the registered H3c reads its base call latencies from P2-P4 h3_calls (measured under other load) for every
setting but math_q15_7, so part of its X1 error is input data, not formula. H3c-fair gives it latsim's data.

Definition. The registered H3c formula, unchanged (scripts/v2/pareto.py LatencyModel): per problem the longest path
through the workflow DAG of base call latency x the factor of the call's model; p50 / p95 over the 64 problems. Factor
= 1 + sum_o beta[o -> m] u_o overlap from the h4_fit.simulate fixed point at K, generalised from two models to n
(identical for two). mean_sum-fair: sum over the plan's nodes of the mean base latency of (node, model); no factor.
Check: given the registered inputs (P5 separate K=16 base, configs/v2_interference.yaml betas), H3c-fair reproduces the
registered H3c on math_q15_7 to 2e-15 (192 of 192 values).

Data (fit data only; nothing from P2-P4 latency):
- Base latency of (workflow, problem, node, model): median of the measured calls in P5 separate-placement runs
  (P5/separate, separate_k1, separate_k32, cal_*_separate) of the same workflow at the matching K. K with no runs:
  linear in log2 K between the nearest measured Ks, clamped (Qwen 1.5B/7B math has K = 1/16/32; every calibration set
  is K = 16 only, so their value is used at every K). math_tiers' 14B cells come from cal_qwen3_14_math_separate.
- Placement enters through the factor only, as in the registered H3c, with latsim's betas (frozen params.json: h4grid,
  quantile p50). P5 shared calibration runs are not a base: they run all_small / all_large only, so the other model is
  idle and they contain no interference.
- Borrowing rule (latsim's: per-model parameters from P5, tokens from the setting's h3_calls; betas from the grid pair
  closest in log size, Phi -> q3_14, math_tiers pairs with the 14B -> q3_14): a call with no measured cell gets
  r0 + r1 prompt_tokens + r2 completion_tokens, least squares over all of that model's P5 separate calls at that K (any
  workflow), applied to its h3_calls tokens. This covers complex_q15_7, hotpot_iso_q15_7, hotpot_iso_granite and
  hotpot_phi (borrowed share 1.0); every other setting has measured cells only (0.0).

Analysis (compare.py), per setting x placement x K and pooled, for latsim_frozen, latsim_rev1, h3c (registered),
h3cfair, mean_sum_fair: n, share of plans with p95 within 10% and 20%, MAPE p95, Kendall tau of predicted vs measured
p95 within the group. Paired bootstrap of the within-10% share, latsim (frozen and rev1) minus h3cfair: 5,000 resamples
of the group's plans with replacement, numpy default_rng(0), one generator in group order; 95% CI = 2.5 / 97.5
percentiles; pooled CI resamples plans within each group (stratified). Measured = mean over repeats.
