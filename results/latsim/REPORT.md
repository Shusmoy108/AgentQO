# latsim: whole-plan latency predictor, results

Branch `v2-latsim` (cut from origin/v2-lease1 a0abe77c). Pre-registration and every freeze: `docs/latsim_prereg.md`.

Data status at 2026-11-17 20:15 UTC:
- **X1 complete**: all 14 blocks, every listed plan, 2 repeats each (938 points; coverage in `X1_coverage.csv`).
  The lease logged "TIME LEFT after X1" at 15:54Z.
- **X1b: in progress, 6 of 9 blocks in**: separate placement complete for all four settings, math_q15_7 shared and
  hotpot_q15_7 shared (258 points at K=4/8/32 x 2 repeats), plus math_q15_7 K=1 separate and shared (4 plans each,
  32 problems, 1 repeat). Still to come: math_q15_7 shared_mps, math_granite shared, math_phi shared.
  Interim, K=4/8/32 (rev1 is the held-out claim on X1b), within 10% / within 20% / MAPE p95 / tau:
  rev1 0.671 / 0.938 / 0.083 / 0.906; frozen 0.632 / 0.868 / 0.105 / 0.888; H3c-fair 0.465 / 0.767 / 0.138 / 0.861;
  registered H3c 0.155 / 0.302 / 1.025 / 0.599. latsim - H3c-fair within-10% (stratified bootstrap): rev1 +0.205
  [0.132, 0.283], frozen +0.167 [0.089, 0.236], both significant. Per group, CIs excluding 0: hotpot_q15_7 shared
  K=4 (frozen +0.55), math_q15_7 shared K=4 (frozen +0.31) and K=32 (+0.44 both), math_granite separate K=32 (+0.44
  both), and frozen on hotpot_q15_7 separate K=32 (-0.36).
  Failure modes so far: (1) HotpotQA, frozen: X1's prefix-cache overprediction recurs (separate median p95 error +15%,
  K=32 within 10% 0.00). (2) **New: HotpotQA shared at K=32, both versions overpredict** (median p95 error frozen
  +47%, rev1 +25%; within 10% 0.00 / 0.27). For rev1 it splits into the base (separate K=32 +8%) and interference:
  predicted shared/separate p95 ratio 2.05 vs measured 1.83 at K=32 (K=4: 1.75 vs 1.90, K=8: 1.99 vs 1.98). A likely
  cause (not yet checked): the h4grid betas are applied as constant slowdowns whenever the other server is busy, and
  were measured at lower occupancy, so near saturation latsim adds more interference than the GPU actually shows. H3c-fair is also wrong
  there (within 10% 0.09). math_granite separate: median p95 error -3% (both); math_q15_7 shared: -0.3% (frozen) /
  -1.2% (rev1), p50 +3%.
  K=1 (scored only against the matched 32-problem re-runs, `matched/`), frozen and rev1 alike: 8/8 plans within 10%,
  MAPE p95 0.022 (separate 0.030, shared 0.014), tau 0.93. MAPE p50 is 0.03 separate but 0.11 shared, mostly
  all_small shared (+24%): measured p50 0.88 s shared vs 1.11 s separate on the same 32 problems with no other model
  busy, i.e. run-to-run variation of a single repeat that the model, which predicts the same 1.10 s for both, cannot see.
  Tables: `report_tables.md`, `compare/X1b_*.csv`, `matched/X1b_k1_*`.
- **X1c** (Phi and three-model interference grids) is not in yet. It is the fit data for the planned rev2.
- **X6 latency: not present, and its 32B model cannot be predicted** (no 32B fit data).

Generated tables: `report_tables.md`, `compare/X1_by_setting.csv`, `compare/X1_bootstrap.csv`.
Per-plan CSVs: `X1_per_plan.csv` (frozen), `rev1/X1_per_plan.csv`.

## Provenance

| version | tag | commit | what | fit data |
|---|---|---|---|---|
| latsim frozen | `latsim-frozen-20261117T133315Z` | 04c5bbde | simulator + parameters + full prediction grid, before any X1 file was opened | P5 + P5/h4grid |
| latsim rev1 | `latsim-rev1-20261117T134155Z` | 2009dcd1 | the fit leaves out cold-prefix-cache P5 runs, so it predicts warm steady state. Made after scoring the frozen version on X1, prompted by its failure analysis; uses no X1 value | P5 + P5/h4grid |
| H3c-fair, mean_sum-fair | `h3cfair-frozen-20261117T140740Z` | 30f7cf66 | registered formulas with latsim's fit data as input, plus the comparison/bootstrap code, frozen before any of their scores | P5 + P5/h4grid |

Strict held-out claims (PI decision): latsim frozen on X1; latsim rev1 on X1b (rev1 was made after X1 was opened, so
its X1 numbers are shown but are not held out). Planned rev2 (after X1c: Phi and three-model interference factors
measured instead of borrowed, fitted on X1c only) will be shown as a labelled revision, not a held-out claim on X1.
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
2. **Cold first plans** in a block (all_small, then the only_* plans) meet a cold server, and rev1 predicts warm.
   - Separate one_large: within 10% 0.62, bias −4%.
   - Separate all_small: 0.83, bias −7%.
   - A per-block cache-state model would cover this; not built.
3. **math_tiers plans with a 14B agent**: within 10% 0.50, bias +10% (14B-free tier plans: 0.91).
   - Three models share one GPU, and the betas involving the 14B are borrowed from the Qwen 3B/14B grid.
   - Summing two betas when both other servers are busy likely overstates the slowdown. No 3-model grid exists to fit
     this.
4. **math_phi shared**: p50 +11%, p95 +5%. In separate placement Phi is on target (p50 +1%, p95 −1%), so the error
   sits in the borrowed Phi betas, which rev2 will replace with X1c's measured ones.
5. **Ranking within a setting** is weaker than the pooled τ: 0.64–0.91 per setting, against 0.93 pooled, which mostly
   reflects differences between settings. Still, it is above every baseline's within-setting τ in 11 of 14 groups
   (frozen) and 12 of 14 (rev1).
   - hotpot_iso_q15_7 separate is an exception for both versions: the baselines reach 0.71–0.73, against latsim's
     0.68–0.69.
   - math_granite separate is an exception for both: the registered H3c reaches 0.73, against latsim's 0.72.
   - hotpot_q15_7 separate is an exception for frozen only.

## Reproduce

```
python3 -m agentqo.latsim.fit --out results/latsim/rev1/params.json            # P5 + h4grid only (~10 min, CPU)
python3 -m agentqo.latsim.predict --params results/latsim/rev1/params.json \
    --out results/latsim/rev1/predictions.csv --p5-out results/latsim/rev1/p5_insample.csv
python3 -m agentqo.latsim.h3cfair                                               # H3c-fair / mean_sum-fair grid
python3 -m agentqo.latsim.report                                                # registered metrics, every version
python3 -m agentqo.latsim.compare --name X1 \
    --measured 'results/v2/X1/*/*/placement_summary.csv,results/v2/X1_vm*/*/*/placement_summary.csv'
```
