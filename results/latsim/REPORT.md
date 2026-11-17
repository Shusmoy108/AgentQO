# latsim: whole-plan latency predictor, results

Branch `v2-latsim` (cut from origin/v2-lease1 a0abe77c). Pre-registration: `docs/latsim_prereg.md`.
Status at 2026-11-17 ~13:45 UTC: **X1 not complete** (math_q3_14 separate running; math_granite and math_phi separate
not yet run). **X1b: no data yet.** **X6 latency: not present, and not predictable** (no 32B fit data).
Full generated tables: `report_tables.md`; per-plan CSVs: `X1_per_plan.csv` (frozen) and `rev1/X1_per_plan.csv`.

## Provenance

| version | tag | commit | what changed | fit data |
|---|---|---|---|---|
| frozen | `latsim-frozen-20261117T133315Z` | 04c5bbde | - | P5 + P5/h4grid |
| rev1 | `latsim-rev1-20261117T134155Z` | 2009dcd1 | P5 runs where a model first meets the block's problems (cold vLLM prefix cache) are left out of the fit, so the model predicts warm steady-state latency | P5 + P5/h4grid |

The frozen code, parameters and the full prediction grid (every plan x separate/shared/shared_mps x K 1/4/8/16/32,
with both baselines) were committed, tagged and pushed before any X1 latency file was opened. Rev1 was made after the
frozen X1 scoring and is motivated by its failure analysis (below); it uses no X1 value. Both results are reported.

## Method (short)

Discrete-event (fluid) simulation, `agentqo/latsim/sim.py`. One vLLM server per model: prefill c s/token that stalls the
server's decoding calls; decode one token per step of a + b n + e KV/1000 s (n decoding calls, KV their context);
o s client overhead. Each problem replays its h3_calls calls in executor order (topological; every call waits for its
parents); K problems in a closed loop as run_placement. Interference: while another model's server on the same GPU is
busy, rates are divided by 1 + sum of the directed betas from P5/h4grid/<pair>/fit (MPS betas for shared_mps; none for
separate). Per-model parameters are fitted jointly per family on P5 separate runs (closed loop, warm-started by an
open-loop fit) and h4grid separate request logs (open loop). Phi borrows the Qwen 3B/14B betas; math_tiers' pairs with
the 14B borrow q3_14.

## In-sample (P5, fit data)

Share of P5 (plan, placement, K) points with p95 within 10% / 20%, mean over repeats: frozen 0.831 / 0.964.
H3c on P5 per repeat (P6's H3c value, reproduced exactly): 0.492.

## X1 (held out, K = 16), 746 (setting, plan, placement) points so far

Pooled, p95 within 10% / 20%, MAPE p50 / p95, Kendall tau of the plan p95 ranking:

| predictor | n | within 10% | within 20% | MAPE p50 | MAPE p95 | tau |
|---|---|---|---|---|---|---|
| latsim frozen | 746 | **0.666** | 0.910 | 0.072 | 0.085 | 0.927 |
| latsim rev1 | 746 | **0.763** | 0.977 | 0.053 | 0.066 | 0.930 |
| H3c (P6 predictor) | 632* | 0.090 | 0.146 | 1.361 | 1.228 | 0.774 |
| sum of mean call latencies | 746 | 0.067 | 0.178 | 0.452 | 0.399 | 0.722 |

\* H3c has no prediction for math_tiers (3 tiers). Pre-stated criterion (latsim frozen within-10% share above H3c's on
the same plans): **met** (0.666 vs 0.090; on math_q15_7 alone, where H3c's base is P5's own separate calls:
separate 0.891 vs 0.688, shared 0.828 vs 0.203).

By setting (latsim; frozen -> rev1, within 10% / MAPE p95 / tau):

| setting | placement | n | frozen w10 | rev1 w10 | rev1 w20 | rev1 MAPE p95 | rev1 bias p95 | rev1 tau |
|---|---|---|---|---|---|---|---|---|
| complex_q15_7 | shared | 184 | 0.804 | 0.810 | 0.978 | 0.061 | +0.018 | 0.841 |
| hotpot_iso_q15_7 | separate | 32 | 0.312 | 0.812 | 1.000 | 0.055 | -0.003 | 0.694 |
| hotpot_iso_q15_7 | shared | 32 | 0.188 | 0.812 | 1.000 | 0.069 | +0.055 | 0.637 |
| hotpot_q15_7 | separate | 32 | 0.281 | 0.750 | 0.938 | 0.067 | -0.004 | 0.685 |
| hotpot_q15_7 | shared | 32 | 0.062 | 0.688 | 0.906 | 0.092 | +0.071 | 0.706 |
| math_granite | shared | 64 | 0.797 | 0.797 | 1.000 | 0.060 | +0.024 | 0.642 |
| math_phi | shared | 64 | 0.734 | 0.734 | 1.000 | 0.072 | +0.054 | 0.676 |
| math_q15_7 | separate | 64 | 0.891 | 0.859 | 0.984 | 0.056 | -0.036 | 0.848 |
| math_q15_7 | shared | 64 | 0.828 | 0.828 | 0.984 | 0.054 | +0.022 | 0.793 |
| math_q3_14 | shared | 64 | 0.844 | 0.844 | 1.000 | 0.049 | +0.032 | 0.781 |
| math_tiers | shared | 114 | 0.526 | 0.544 | 0.947 | 0.092 | +0.085 | 0.784 |

## Where it fails

1. **Frozen: HotpotQA, plans with 2+ agents on the 7B** (p95 +13% to +27%). Cause: vLLM prefix cache. In P5's Qwen
   HotpotQA calibration, repeat 0 of each model's first plan is 2.1x slower at p95 than repeats 1-2 (identical tokens):
   the ~1,550-token contexts are prefilled once, then cached. The frozen fit put that cold cost into every call; X1
   runs 32 plans per block, so almost every plan runs warm. Rev1 (warm-only fit) fixes most of it (HotpotQA within 10%
   0.06-0.31 -> 0.69-0.81). The effect is ~7% for Granite HotpotQA and nil for math.
2. **Cold first plans** (both versions): the first plans of a block (all_small, then the only_* plans) meet a cold
   server; rev1 underpredicts them (separate one_large: within 10% 0.38, bias -10%; all_small -9%). A cache-state
   model per block (which problems each server has already seen) would cover this; not built.
3. **math_tiers plans with a 14B agent** (has_xl: within 10% 0.50, bias +10%; 14B-free tier plans 0.91). Three models
   share one GPU and the 1.5B/7B <-> 14B betas are borrowed from the Qwen 3B/14B grid; the sum of two betas when both
   other servers are busy likely overstates the slowdown. No 3-model grid exists to fit this.
4. **math_phi p50** +11% (p95 +5%): Phi's betas are borrowed (no Phi grid); its separate-placement X1 runs are not in yet.
5. **Ranking within a setting** is weaker than the pooled tau suggests (per-setting tau 0.64-0.85; pooled 0.93 mostly
   reflects between-setting differences). Plans within a HotpotQA setting differ by less than the run-to-run noise.

## Baselines

H3c is accurate only where its latency base was measured under the same conditions (math_q15_7: P5 separate calls).
Elsewhere it reads h3_calls latency_s, which were measured during P2-P4 at V2_WORKERS = 32 with very different server
load, so it overpredicts by 1.3x-2.8x (MAPE p95 1.2). The sum of mean call latencies ignores queueing and the p95 tail
(bias -29%).

## Reproduce

```
python3 -m agentqo.latsim.fit --out results/latsim/rev1/params.json          # P5 + h4grid only (~10 min, CPU)
python3 -m agentqo.latsim.predict --params results/latsim/rev1/params.json \
    --out results/latsim/rev1/predictions.csv --p5-out results/latsim/rev1/p5_insample.csv
python3 -m agentqo.latsim.report                                              # scores every version on X1 / X1b
```
