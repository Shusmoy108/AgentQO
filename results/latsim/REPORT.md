# latsim: whole-plan latency predictor, results

Branch `v2-latsim` (cut from origin/v2-lease1 a0abe77c). Pre-registration and every freeze: `docs/latsim_prereg.md`.

Data status at 2026-11-18 00:30 UTC:
- **X1 complete**: all 14 blocks, every listed plan, 2 repeats each (938 points; coverage in `X1_coverage.csv`).
  The lease logged "TIME LEFT after X1" at 15:54Z.
- **X1b complete** (last block, math_phi shared, landed 23:18Z): all 9 blocks, every listed plan, 2 repeats each,
  402 points at K = 4/8/32, plus math_q15_7 K=1 (4 plans x separate/shared, 32 problems, 1 repeat). VM-B's
  21:09Z server-swap incident runs sit in `X1b_vmB/math_phi/superseded_server_swap_2109Z/` and are left out.
  Results below.
- **X1c complete** (lease head ee868ef7, ~00:06Z): Phi grid + fit and the A16 three-model runs. rev2 was fitted on
  it, tagged `latsim-rev2-20261118T000620Z` and pushed before any rev2 prediction or score; results below.
- **X6 latency: not present, and its 32B model cannot be predicted** (no 32B fit data).

Generated tables: `report_tables.md`, `compare/{X1,X1b}_by_setting.csv`, `compare/{X1,X1b}_bootstrap.csv`,
`matched/X1b_k1_*`. Per-plan CSVs: `{X1,X1b}_per_plan.csv` (frozen), `rev1/{X1,X1b}_per_plan.csv`.

## Provenance

| version | tag | commit | what | fit data |
|---|---|---|---|---|
| latsim frozen | `latsim-frozen-20261117T133315Z` | 04c5bbde | simulator + parameters + full prediction grid, before any X1 file was opened | P5 + P5/h4grid |
| latsim rev1 | `latsim-rev1-20261117T134155Z` | 2009dcd1 | the fit leaves out cold-prefix-cache P5 runs, so it predicts warm steady state. Made after scoring the frozen version on X1, prompted by its failure analysis; uses no X1 value | P5 + P5/h4grid |
| latsim rev2 | `latsim-rev2-20261118T000620Z` | b3d0bdd6 | rev1 with measured instead of borrowed interference factors: the Phi-3.5-mini/Phi-4 pair (X1c Phi grid, h4_fit p50) and the four Qwen 14B pairs on a three-model GPU (fitted on the X1c A16 runs); every other parameter as rev1 | rev1's + X1c only |
| H3c-fair, mean_sum-fair | `h3cfair-frozen-20261117T140740Z` | 30f7cf66 | registered formulas with latsim's fit data as input, plus the comparison/bootstrap code, frozen before any of their scores | P5 + P5/h4grid |

Strict held-out claims (PI decision): latsim frozen on X1; latsim rev1 on X1b (rev1 was made after X1 was opened, so
its X1 numbers are shown but are not held out). rev2 (Phi and three-model interference factors measured instead of
borrowed, fitted on X1c only) is a labelled revision, not a held-out claim on X1 or X1b (both were open).
X1b K=1 (32 problems) is scored only against re-runs of the tagged frozen / rev1 code on those same 32 problems.

The registered H3c (column `h3c`; P6 value 0.492 on P5) is kept exactly as registered. H3c-fair is an added,
separately labelled baseline.

## Method (short)

- **latsim** (`agentqo/latsim/sim.py`) is a discrete-event (fluid) simulation with one vLLM server per model:
  - prefill costs c s/token and stalls the server's decoding calls;
  - decoding produces one token per step of a + b·n + e·KV/1000 s;
  - each call adds o s of client overhead.
  - Problems replay their h3_calls calls in executor order, with K problems in a closed loop.
  - While another model's server on the same GPU is busy, rates are divided by 1 + Σβ, using the h4grid betas.
  - Parameters are fitted jointly per model family on P5 separate runs (closed loop) and h4grid logs (open loop).
- **H3c-fair** (`agentqo/latsim/h3cfair.py`) keeps the registered H3c formula: longest path of base call latency × a
  fixed-point placement factor. Given the registered H3c's own inputs, it reproduces the registered values to 2e-15.
  - Base latencies come from P5 separate runs of the same workflow at the matching K (interpolated in log₂K).
  - The factor uses latsim's betas.
  - Calls with no measured cell use the model's per-call rate at K applied to h3_calls tokens (latsim's borrowing
    rule): complex_q15_7, hotpot_iso_* and hotpot_phi.
- **mean_sum-fair** sums the mean base latency over the plan's nodes, with no factor.

## X1 (held out for the frozen version, K = 16): complete, 938 points

Pooled:

| predictor | n | within 10% | within 20% | MAPE p95 | Kendall τ |
|---|---|---|---|---|---|
| latsim frozen (held out) | 938 | **0.708** | 0.925 | 0.079 | 0.927 |
| latsim rev1 (not held out on X1) | 938 | **0.783** | 0.979 | 0.063 | 0.930 |
| H3c (registered) | 824* | 0.069 | 0.112 | 1.195 | 0.788 |
| H3c-fair | 938 | 0.450 | 0.751 | 0.138 | 0.872 |
| mean_sum-fair | 938 | 0.013 | 0.034 | 0.560 | 0.583 |
| sum of mean call latencies (as first registered, P2-P4 base) | 938 | 0.053 | 0.145 | 0.413 | 0.575 |

\* H3c has no prediction for math_tiers (3 tiers); H3c-fair handles n models.

Pre-stated criterion (frozen latsim's within-10% share above the registered H3c's on the same plans): **met**,
0.708 vs 0.069.

Paired bootstrap of the within-10% share, latsim minus H3c-fair (5,000 resamples of plans, seed 0, stratified when
pooled):
- frozen: **+0.258** [0.222, 0.293]
- rev1: **+0.333** [0.295, 0.369]

### Per setting × placement (K = 16)

Within 10% / within 20% / MAPE p95 / Kendall τ within the setting:

| setting | placement | n | latsim frozen | latsim rev1 | H3c (registered) | H3c-fair | mean_sum-fair |
|---|---|---|---|---|---|---|---|
| complex_q15_7 | shared | 184 | 0.80 / 0.96 / 0.064 / 0.84 | 0.81 / 0.98 / 0.061 / 0.84 | 0.00 / 0.01 / 1.125 / 0.69 | 0.53 / 0.86 / 0.103 / 0.71 | 0.00 / 0.00 / 0.699 / 0.62 |
| hotpot_iso_q15_7 | separate | 32 | 0.31 / 0.66 / 0.147 / 0.68 | 0.81 / 1.00 / 0.055 / 0.69 | 0.00 / 0.00 / 1.875 / 0.71 | 0.12 / 0.53 / 0.207 / 0.71 | 0.38 / 0.81 / 0.139 / 0.73 |
| hotpot_iso_q15_7 | shared | 32 | 0.19 / 0.75 / 0.158 / 0.68 | 0.81 / 1.00 / 0.069 / 0.64 | 0.00 / 0.00 / 2.409 / 0.59 | 0.00 / 0.06 / 0.357 / 0.54 | 0.00 / 0.03 / 0.539 / 0.35 |
| hotpot_q15_7 | separate | 32 | 0.28 / 0.59 / 0.181 / 0.64 | 0.75 / 0.94 / 0.067 / 0.69 | 0.00 / 0.00 / 1.962 / 0.65 | 0.53 / 0.94 / 0.094 / 0.55 | 0.00 / 0.12 / 0.299 / 0.48 |
| hotpot_q15_7 | shared | 32 | 0.06 / 0.38 / 0.217 / 0.73 | 0.69 / 0.91 / 0.092 / 0.71 | 0.00 / 0.00 / 2.529 / 0.67 | 0.09 / 0.44 / 0.246 / 0.42 | 0.00 / 0.00 / 0.614 / 0.20 |
| math_granite | separate | 64 | 0.78 / 0.98 / 0.063 / 0.72 | 0.80 / 0.98 / 0.063 / 0.72 | 0.00 / 0.00 / 0.978 / 0.73 | 0.48 / 0.89 / 0.106 / 0.57 | 0.00 / 0.00 / 0.388 / 0.65 |
| math_granite | shared | 64 | 0.80 / 1.00 / 0.059 / 0.64 | 0.80 / 1.00 / 0.060 / 0.64 | 0.00 / 0.00 / 1.334 / 0.30 | 0.42 / 0.72 / 0.154 / 0.26 | 0.00 / 0.00 / 0.686 / 0.35 |
| math_phi | separate | 64 | 0.88 / 0.98 / 0.052 / 0.80 | 0.84 / 0.98 / 0.053 / 0.81 | 0.00 / 0.00 / 1.179 / 0.79 | 0.81 / 0.98 / 0.066 / 0.76 | 0.00 / 0.02 / 0.344 / 0.72 |
| math_phi | shared | 64 | 0.73 / 1.00 / 0.074 / 0.68 | 0.73 / 1.00 / 0.072 / 0.68 | 0.00 / 0.00 / 1.467 / 0.59 | 0.44 / 0.81 / 0.133 / 0.55 | 0.00 / 0.00 / 0.666 / 0.45 |
| math_q15_7 | separate | 64 | 0.89 / 0.98 / 0.054 / 0.85 | 0.86 / 0.98 / 0.056 / 0.85 | 0.69 / 0.94 / 0.079 / 0.76 | 0.69 / 0.94 / 0.079 / 0.76 | 0.00 / 0.00 / 0.394 / 0.79 |
| math_q15_7 | shared | 64 | 0.83 / 0.98 / 0.055 / 0.79 | 0.83 / 0.98 / 0.054 / 0.79 | 0.20 / 0.48 / 0.201 / 0.70 | 0.27 / 0.69 / 0.151 / 0.70 | 0.00 / 0.00 / 0.690 / 0.56 |
| math_q3_14 | separate | 64 | 0.95 / 0.98 / 0.042 / 0.90 | 0.94 / 0.98 / 0.042 / 0.91 | 0.00 / 0.00 / 1.098 / 0.87 | 0.75 / 0.94 / 0.068 / 0.83 | 0.00 / 0.00 / 0.304 / 0.87 |
| math_q3_14 | shared | 64 | 0.84 / 1.00 / 0.050 / 0.78 | 0.84 / 1.00 / 0.049 / 0.78 | 0.00 / 0.00 / 1.426 / 0.47 | 0.44 / 0.69 / 0.139 / 0.49 | 0.00 / 0.00 / 0.625 / 0.58 |
| math_tiers | shared | 114 | 0.53 / 0.95 / 0.094 / 0.78 | 0.54 / 0.95 / 0.092 / 0.78 | - | 0.22 / 0.49 / 0.212 / 0.65 | 0.00 / 0.00 / 0.730 / 0.50 |

On math_q15_7 separate, H3c-fair and the registered H3c are identical, because the registered H3c already used P5
separate K=16 calls there.

Paired bootstrap, within-10% share, latsim minus H3c-fair (difference [95% CI]; bold = H3c-fair significantly better):

| setting | placement | frozen − H3c-fair | rev1 − H3c-fair |
|---|---|---|---|
| complex_q15_7 | shared | +0.272 [0.185, 0.353] | +0.277 [0.196, 0.359] |
| hotpot_iso_q15_7 | separate | +0.188 [0.031, 0.344] | +0.688 [0.469, 0.875] |
| hotpot_iso_q15_7 | shared | +0.188 [0.062, 0.344] | +0.812 [0.656, 0.938] |
| hotpot_q15_7 | separate | **-0.250 [-0.469, -0.031]** | +0.219 [-0.031, 0.469] |
| hotpot_q15_7 | shared | -0.031 [-0.156, 0.094] | +0.594 [0.406, 0.750] |
| math_granite | separate | +0.297 [0.172, 0.438] | +0.312 [0.188, 0.438] |
| math_granite | shared | +0.375 [0.234, 0.516] | +0.375 [0.234, 0.516] |
| math_phi | separate | +0.062 [-0.031, 0.156] | +0.031 [-0.078, 0.141] |
| math_phi | shared | +0.297 [0.141, 0.453] | +0.297 [0.141, 0.453] |
| math_q15_7 | separate | +0.203 [0.062, 0.344] | +0.172 [0.031, 0.312] |
| math_q15_7 | shared | +0.562 [0.421, 0.703] | +0.562 [0.406, 0.703] |
| math_q3_14 | separate | +0.203 [0.094, 0.328] | +0.188 [0.062, 0.312] |
| math_q3_14 | shared | +0.406 [0.266, 0.547] | +0.406 [0.266, 0.547] |
| math_tiers | shared | +0.307 [0.193, 0.421] | +0.325 [0.211, 0.439] |
| all, stratified |  | +0.258 [0.222, 0.293] | +0.333 [0.295, 0.369] |

Summary over the 14 groups:
- **Frozen** is significantly ahead of H3c-fair in 11, not different in 2 (hotpot_q15_7 shared, math_phi separate),
  and significantly behind in 1 (hotpot_q15_7 separate).
- **Rev1** is significantly ahead in 12 and not different in 2 (hotpot_q15_7 separate, math_phi separate).

### What the fair baseline shows

- **Most of the registered H3c's X1 failure was its inputs.** With latsim's data, H3c goes from 0.07 to 0.45 within
  10%. The rest of the gap is the formula: a mean-field placement factor, and no queueing or prefill effects across
  problems.
- **H3c-fair's main weakness is shared placement.** It does better on separate math (0.48–0.81, close to latsim on
  math_phi separate) and on hotpot_q15_7 separate (0.53). Shared settings fall to 0.00–0.53, and its within-setting τ drops to 0.26–0.71.
- **The one place a baseline beats a latsim version** is hotpot_q15_7 separate, where H3c-fair beats frozen latsim
  (−0.25, CI excludes 0). That is the prefix-cache error that rev1 fixed. H3c-fair's measured base absorbs it, because
  the median over P5's three repeats picks a warm repeat.
- **mean_sum-fair** has no queueing or tail term. It predicts roughly the mean, so its median p95 error is −30% to −74%
  in every group but one. The exception is hotpot_iso_q15_7 separate (−12%, within 10% 0.38), whose base uses
  borrowed rates.

## X1b (held out for rev1; new loads K = 4, 8, 32 and K = 1): complete, 402 + 8 points

rev1 was made after X1 was opened and before any X1b data existed, so X1b is its held-out test (PI decision). Frozen is
shown too. Baselines as on X1 (H3c-fair inputs interpolated in log2 K between P5's K = 1/16/32 where they exist).

| predictor | within 10% | within 20% | MAPE p95 | Kendall τ (pooled) |
|---|---|---|---|---|
| **latsim rev1** (held out) | **0.669** | **0.928** | **0.083** | **0.918** |
| latsim frozen | 0.649 | 0.883 | 0.097 | 0.908 |
| H3c-fair | 0.453 | 0.741 | 0.142 | 0.871 |
| H3c (registered) | 0.149 | 0.286 | 0.993 | 0.711 |
| mean_sum-fair | 0.012 | 0.035 | 0.505 | 0.685 |

Paired bootstrap, latsim − H3c-fair within-10% share, stratified over the 27 setting × placement × K groups (5,000
resamples, seed 0): **rev1 +0.216 [0.157, 0.276]**, frozen +0.197 [0.139, 0.254].

Per group, CI excluding 0 (bold in the table): rev1 is ahead in 5 of 27 and behind in none; frozen ahead in 5, behind in
1 (hotpot_q15_7 separate K=32, the prefix-cache error). With 11–16 plans per group most single-group CIs span 0.

By placement and load (rev1, within 10% / MAPE p95; `rev1/X1b_pooled.csv`): separate K = 4 / 8 / 32: 0.66 / 0.64 /
0.71, MAPE 0.08 at each; shared: 0.68 / 0.73 / 0.61, MAPE 0.08 / 0.07 / 0.11; shared_mps (math_q15_7 only): 0.69 /
0.75 / 0.50, MAPE 0.07 / 0.07 / 0.11. Shared and MPS at K=32 are the weakest cells, for the reason under failure 6.

**K = 1** (32 problems; scored only against re-runs of the frozen and rev1 tags on exactly those problems,
`matched/`): both versions 8/8 plans within 10%, MAPE p95 0.022, τ 0.93. No baseline is scored at K=1 (their
predictions are over 64 problems).

**Within-group ranking** is where latsim is weakest. Median within-group τ: latsim 0.78 (both versions), registered H3c
0.75, H3c-fair 0.67, mean_sum-fair 0.60. rev1's τ is higher than H3c-fair's in 20 of 27 groups (5 lower), higher than
mean_sum-fair's in 23 (4 lower: math_q15_7 separate at every K, where mean_sum-fair reaches 0.88–0.90, and
math_q15_7 shared_mps K=32), but only level with the registered H3c (higher in 12, lower in 13). The registered
H3c's level is far off (median p95 error ~+100%) but its order within a group is about as good.

### Per setting × placement × K

| setting | placement | K | n | within 10%: frozen / rev1 / H3c-fair / H3c | MAPE p95: rev1 / H3c-fair | τ: rev1 / H3c-fair | rev1 − H3c-fair, within 10% [95% CI] |
|---|---|---|---|---|---|---|---|
| hotpot_q15_7 | separate | 4 | 11 | 0.73 / 0.64 / 0.36 / 0.00 | 0.10 / 0.22 | 0.85 / 0.75 | +0.27 [-0.18, +0.73] |
| hotpot_q15_7 | separate | 8 | 11 | 0.64 / 0.55 / 0.45 / 0.00 | 0.08 / 0.18 | 0.75 / 0.67 | +0.09 [-0.36, +0.55] |
| hotpot_q15_7 | separate | 32 | 11 | 0.00 / 0.55 / 0.36 / 0.00 | 0.11 / 0.11 | 0.67 / 0.75 | +0.18 [-0.18, +0.55] |
| hotpot_q15_7 | shared | 4 | 11 | 0.82 / 0.73 / 0.27 / 0.00 | 0.06 / 0.26 | 0.78 / 0.67 | +0.45 [+0.00, +0.91] |
| hotpot_q15_7 | shared | 8 | 11 | 0.36 / 0.64 / 0.18 / 0.00 | 0.08 / 0.29 | 0.78 / 0.71 | +0.45 [+0.00, +0.82] |
| hotpot_q15_7 | shared | 32 | 11 | 0.00 / 0.27 / 0.09 / 0.00 | 0.26 / 0.25 | 0.64 / 0.53 | +0.18 [+0.00, +0.45] |
| math_granite | separate | 4 | 16 | 0.56 / 0.62 / 0.44 / 0.00 | 0.07 / 0.12 | 0.78 / 0.60 | +0.19 [-0.12, +0.50] |
| math_granite | separate | 8 | 16 | 0.62 / 0.62 / 0.50 / 0.00 | 0.08 / 0.14 | 0.82 / 0.53 | +0.12 [-0.25, +0.44] |
| math_granite | separate | 32 | 16 | 0.81 / 0.81 / 0.38 / 0.00 | 0.07 / 0.14 | 0.85 / 0.57 | **+0.44 [+0.12, +0.75]** |
| math_granite | shared | 4 | 16 | 0.62 / 0.56 / 0.56 / 0.00 | 0.09 / 0.16 | 0.65 / 0.62 | +0.00 [-0.31, +0.31] |
| math_granite | shared | 8 | 16 | 0.88 / 0.88 / 0.38 / 0.00 | 0.04 / 0.17 | 0.82 / 0.58 | **+0.50 [+0.25, +0.75]** |
| math_granite | shared | 32 | 16 | 0.75 / 0.75 / 0.38 / 0.00 | 0.06 / 0.14 | 0.78 / 0.45 | +0.38 [+0.00, +0.69] |
| math_phi | separate | 4 | 16 | 0.69 / 0.69 / 0.62 / 0.00 | 0.07 / 0.09 | 0.92 / 0.87 | +0.06 [-0.31, +0.44] |
| math_phi | separate | 8 | 16 | 0.81 / 0.81 / 0.56 / 0.00 | 0.08 / 0.09 | 0.90 / 0.85 | +0.25 [+0.00, +0.50] |
| math_phi | separate | 32 | 16 | 0.62 / 0.62 / 0.56 / 0.00 | 0.07 / 0.09 | 0.87 / 0.83 | +0.06 [-0.19, +0.31] |
| math_phi | shared | 4 | 16 | 0.62 / 0.62 / 0.44 / 0.00 | 0.10 / 0.18 | 0.70 / 0.52 | +0.19 [+0.00, +0.38] |
| math_phi | shared | 8 | 16 | 0.62 / 0.62 / 0.19 / 0.00 | 0.10 / 0.19 | 0.68 / 0.52 | **+0.44 [+0.19, +0.69]** |
| math_phi | shared | 32 | 16 | 0.62 / 0.62 / 0.56 / 0.00 | 0.09 / 0.12 | 0.57 / 0.58 | +0.06 [-0.19, +0.31] |
| math_q15_7 | separate | 4 | 16 | 0.69 / 0.69 / 0.62 / 0.56 | 0.07 / 0.09 | 0.73 / 0.80 | +0.06 [-0.25, +0.38] |
| math_q15_7 | separate | 8 | 16 | 0.56 / 0.56 / 0.69 / 0.50 | 0.08 / 0.09 | 0.73 / 0.78 | -0.12 [-0.44, +0.19] |
| math_q15_7 | separate | 32 | 16 | 0.81 / 0.81 / 0.69 / 0.44 | 0.08 / 0.07 | 0.82 / 0.65 | +0.12 [-0.12, +0.38] |
| math_q15_7 | shared | 4 | 16 | 0.81 / 0.81 / 0.50 / 0.38 | 0.06 / 0.12 | 0.80 / 0.80 | +0.31 [+0.00, +0.56] |
| math_q15_7 | shared | 8 | 16 | 0.75 / 0.75 / 0.50 / 0.25 | 0.07 / 0.12 | 0.78 / 0.78 | +0.25 [-0.06, +0.56] |
| math_q15_7 | shared | 32 | 16 | 0.69 / 0.69 / 0.25 / 0.38 | 0.08 / 0.16 | 0.73 / 0.85 | **+0.44 [+0.12, +0.75]** |
| math_q15_7 | shared_mps | 4 | 16 | 0.69 / 0.69 / 0.69 / 0.69 | 0.07 / 0.09 | 0.77 / 0.75 | +0.00 [-0.31, +0.38] |
| math_q15_7 | shared_mps | 8 | 16 | 0.75 / 0.75 / 0.44 / 0.38 | 0.07 / 0.10 | 0.78 / 0.75 | **+0.31 [+0.06, +0.56]** |
| math_q15_7 | shared_mps | 32 | 16 | 0.56 / 0.50 / 0.25 / 0.19 | 0.11 / 0.21 | 0.58 / 0.53 | +0.25 [-0.06, +0.56] |

## rev2: with measured instead of borrowed interference factors (labelled revision, not held out)

Fitted on X1c only, tagged `latsim-rev2-20261118T000620Z` (b3d0bdd6) before any rev2 prediction or score. rev2's
predictions differ from rev1's only where a borrowed factor was replaced (checked): math_tiers shared (2,656 grid rows),
math_phi and hotpot_phi shared / shared_mps (248 + 248 + 120 + 120); every other row is identical to rev1's.

| | interference factor | borrowed (rev1) | measured (rev2) |
|---|---|---|---|
| Phi, shared | Phi-4 → Phi-3.5-mini / reverse | 2.148 / 1.052 (Qwen 3B/14B grid) | 1.896 / 1.164 (X1c Phi grid) |
| Phi, MPS | Phi-4 → Phi-3.5-mini / reverse | Qwen 3B/14B MPS | 1.572 / 0.567 |
| three models, shared | 14B → 1.5B / 1.5B → 14B | 2.225 / 0.908 (Qwen 1.5B/7B grid) | 2.594 / 0.861 (X1c A16 fit) |
| three models, shared | 14B → 7B / 7B → 14B | 2.148 / 1.052 (Qwen 3B/14B grid) | 1.764 / 1.122 (X1c A16 fit) |

Pooled (within 10% / within 20% / MAPE p50 / MAPE p95 / τ):

| test | frozen | rev1 | rev2 |
|---|---|---|---|
| X1 (938) | 0.708 / 0.925 / 0.063 / 0.079 / 0.927 | 0.783 / 0.979 / 0.049 / 0.063 / 0.930 | 0.793 / 0.981 / 0.046 / 0.062 / 0.931 |
| X1b (402) | 0.649 / 0.883 / 0.079 / 0.097 / 0.908 | 0.669 / 0.928 / 0.062 / 0.083 / 0.918 | 0.679 / 0.933 / 0.059 / 0.082 / 0.918 |

rev2 − H3c-fair, within 10% (stratified bootstrap, its own seed-0 stream so the frozen / rev1 draws are unchanged):
X1 +0.343 [0.307, 0.380], significantly ahead in 12 of 14 groups, behind in none; X1b +0.226 [0.167, 0.286], ahead in
6 of 27, behind in none.

Where it changed (median error, rev1 → rev2):
- **math_tiers shared, plans with the 14B** (X1, 102 plans): within 10% 0.50 → 0.65, p95 +9.6% → +6.9%, p50 +6.8% →
  +5.7%. All math_tiers shared: 0.54 → 0.68 (vs H3c-fair 0.22; rev2 − H3c-fair +0.46 [0.35, 0.56]). Still high, so
  the borrowed factors were only part of failure 3.
- **math_phi shared**: X1b within 10% 0.63 → 0.71 (p50 +10.5% → +7.8%, p95 +4.4% → +3.3%), but X1 0.73 → 0.66 (p50
  +10.5% → +9.3%, p95 +5.4% → +6.3%). The measured Phi factors shrink the p50 error by only 1–3 points, so the +8–9%
  Phi shared p50 error is mostly not an interference-factor error (failure 4 needs another explanation).
- Pooled the change is small (+0.01 within 10% on X1 and X1b): the replaced factors touch 2 of X1's 14 groups and 3 of
  X1b's 27.

## In-sample (P5, fit data)

- Share of P5 (plan, placement, K) points with p95 within 10% / 20%, mean over repeats: latsim frozen 0.831 / 0.964.
- Registered H3c on P5, per repeat: 0.492.

## Where latsim fails

1. **Frozen latsim on HotpotQA plans with 2+ agents on the 7B** (p95 +13% to +27%) is a prefix-cache effect.
   - In P5's Qwen HotpotQA calibration, repeat 0 of a model's first plan is 2.1× slower at p95 than repeats 1–2, with
     identical tokens.
   - The frozen fit put that cold cost into every call, but X1 runs most plans warm.
   - Rev1 raises HotpotQA within-10% from 0.06–0.31 to 0.69–0.81. The effect is ~7% on Granite HotpotQA and nil on
     math.
   - X1b confirms it out of sample at new loads: hotpot_q15_7 separate median p95 error frozen +15% (K=32: within 10%
     0.00, MAPE 0.33), rev1 +3% (K=32: 0.55, MAPE 0.11).
2. **Cold first plans** in a block (all_small, then the only_* plans) meet a cold server, and rev1 predicts warm.
   - Separate one_large: within 10% 0.62, bias −4%.
   - Separate all_small: 0.83, bias −7%.
   - A per-block cache-state model would cover this; not built.
3. **math_tiers plans with a 14B agent**: within 10% 0.50, bias +10% (14B-free tier plans: 0.91).
   - Three models share one GPU, and the betas involving the 14B are borrowed: 7B/14B from the Qwen 3B/14B grid,
     1.5B/14B from the Qwen 1.5B/7B grid (a log-size tie; an earlier version of this report and the prereg said
     3B/14B for both, see the prereg erratum).
   - Summing two betas when both other servers are busy likely overstates the slowdown. X1c's A16 three-model runs
     now exist; rev2 fits the four 14B factors on them (fitted vs borrowed: 14B→1.5B 2.59 vs 2.23, 1.5B→14B 0.86 vs
     0.91, 14B→7B 1.76 vs 2.15, 7B→14B 1.12 vs 1.05; per-call log RMSE on A16 0.137 → 0.111). rev2 raises
     within 10% on these plans to 0.65 (bias +7%); see the rev2 section.
4. **math_phi shared**: p50 +11%, p95 +5%. In separate placement Phi is on target (p50 +1%, p95 −1%), so the error
   was attributed to the borrowed Phi betas. X1b repeats it at every load
   (rev1 median p50 error +12% / +12% / +8%, p95 +4% / +8% / +3% at K = 4 / 8 / 32; within 10% 0.63 each), while
   math_phi separate stays on target (within 20% 1.00 at every K). rev2's measured Phi factors cut the p50 error by
   only 1–3 points (X1 +9%, X1b +8%), so the borrowed betas were not the main cause; not yet explained.
5. **Ranking within a setting** is weaker than the pooled τ: 0.64–0.91 per setting, against 0.93 pooled, which mostly
   reflects differences between settings. Still, it is above every baseline's within-setting τ in 11 of 14 groups
   (frozen) and 12 of 14 (rev1).
   - hotpot_iso_q15_7 separate is an exception for both versions: the baselines reach 0.71–0.73, against latsim's
     0.68–0.69.
   - math_granite separate is an exception for both: the registered H3c reaches 0.73, against latsim's 0.72.
   - hotpot_q15_7 separate is an exception for frozen only.

6. **Shared and MPS placement at K = 32 run high** (X1b only; X1 is K=16). hotpot_q15_7 shared: median p95 error
   frozen +47%, rev1 +25% (within 10% 0.00 / 0.27). math_q15_7 shared_mps: +8%. math_q15_7 and math_granite plain
   shared at K=32 are on target (−1% and +1%), so it is not shared placement as such. For rev1 on HotpotQA, ~8 points
   come from the base (separate K=32 +8%) and the rest from interference: predicted shared/separate p95 ratio 2.05
   against measured 1.83 at K=32, while at K=4 / 8 they match (1.75 vs 1.90, 1.99 vs 1.98). Likely cause, not checked:
   the h4grid betas are constant slowdowns applied whenever the other server is busy, measured at lower occupancy, so
   near saturation latsim adds more slowdown than the GPU shows. H3c-fair also fails there (within 10% 0.09).

## Reproduce

```
python3 -m agentqo.latsim.fit --out results/latsim/rev1/params.json            # P5 + h4grid only (~10 min, CPU)
python3 -m agentqo.latsim.predict --params results/latsim/rev1/params.json \
    --out results/latsim/rev1/predictions.csv --p5-out results/latsim/rev1/p5_insample.csv
python3 -m agentqo.latsim.rev2 --out results/latsim/rev2/params.json          # rev1 + X1c factors (~15 s)
python3 -m agentqo.latsim.predict --params results/latsim/rev2/params.json \
    --out results/latsim/rev2/predictions.csv --p5-out results/latsim/rev2/p5_insample.csv
python3 -m agentqo.latsim.h3cfair                                               # H3c-fair / mean_sum-fair grid
python3 -m agentqo.latsim.report                                                # registered metrics, every version
python3 -m agentqo.latsim.compare --name X1 \
    --measured 'results/v2/X1/*/*/placement_summary.csv,results/v2/X1_vm*/*/*/placement_summary.csv'
python3 -m agentqo.latsim.compare --name X1b --measured 'results/v2/X1b*/*/*/placement_summary.csv' --exclude-k 1
python3 -m agentqo.latsim.matched --tag latsim-frozen-20261117T133315Z --params results/latsim/params.json \
    --label frozen_matched_k1 --runs 'results/v2/X1b/math_q15_7/*_k1/run_*.csv'      # same for rev1 at its tag
python3 -m agentqo.latsim.evaluate --name X1b_k1_rev1_matched --out results/latsim/matched \
    --measured 'results/v2/X1b/*/*_k1/placement_summary.csv' --predictions results/latsim/matched/rev1_matched_k1.csv
```
