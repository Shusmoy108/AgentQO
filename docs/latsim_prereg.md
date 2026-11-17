# latsim pre-registration: whole-plan latency predictor

Frozen: tag `__TAG__`, commit `__COMMIT__` (branch v2-latsim, cut from origin/v2-lease1 a0abe77c).
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
