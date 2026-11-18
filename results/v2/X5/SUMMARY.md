# Phase X5

Generated 2026-11-18 01:59 UTC, backend `vllm`.

Code run: `c1bb8338fa64acd82d82f1eb0c5a5ce6cb7b019b`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| math500_q15_7/labels | finished |
| math500_q15_7/plans | finished |

## math500_q15_7/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.61 | 0.041 | 0.025 | -0.04 | 0.085 | 0.02 | 0.003 | 200 | 200 | 200 |
| step_1 | 200 | 0.565 | 0.027 | 0.015 | -0.04 | 0.07 | 0.016 | 0.033 | 199 | 200 | 200 |
| step_2 | 200 | 0.385 | 0.026 | 0.01 | -0.035 | 0.055 | 0.007 | -0.003 | 192 | 200 | 200 |
| step_3 | 200 | 0.335 | 0.045 | 0.015 | -0.035 | 0.065 | 0.02 | 0.016 | 167 | 200 | 200 |
| aggregator | 200 | 0.51 | 0.294 | 0.135 | 0.065 | 0.205 | 0.085 | 0.102 | 184 | 200 | 200 |
| verifier | 200 | 0.5 | 0.53 | 0.265 | 0.205 | 0.33 | 0.346 | 0.341 | 195 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.039 |
| planner | llm_subtle_wrong | 96 | 0.01 |
| planner | resample_disagree | 200 | 0.005 |
| step_1 | swap_other_task | 200 | 0.003 |
| step_1 | llm_subtle_wrong | 162 | 0.056 |
| step_1 | resample_disagree | 199 | 0.055 |
| step_2 | swap_other_task | 200 | 0.032 |
| step_2 | llm_subtle_wrong | 176 | -0.003 |
| step_2 | resample_disagree | 192 | -0.005 |
| step_3 | swap_other_task | 200 | 0.059 |
| step_3 | resample_disagree | 167 | 0.042 |
| aggregator | swap_other_task | 199 | 0.17 |
| aggregator | resample_disagree | 184 | 0.201 |
| verifier | swap_other_task | 200 | 0.64 |
| verifier | resample_disagree | 195 | 0.623 |
| step_3 | llm_subtle_wrong | 191 | 0.042 |
| verifier | llm_subtle_wrong | 3 | 0 |
| aggregator | llm_subtle_wrong | 4 | 0 |

## math500_q15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+step_1+aggregator+verifier | aggregator,planner,step_1,verifier | 0.693 | 18 | 4 | 15.714 | large | large | small | small | large | large | 0.283 | 0.223 | 0.343 | 1.181 | 0.667 |
| step_1+step_3+verifier | step_1,step_3,verifier | 0.687 | 15 | 3 | 13.428 | small | large | small | large | small | large | 0.277 | 0.22 | 0.337 | 1.153 | 0.5 |
| step_1+aggregator+verifier | aggregator,step_1,verifier | 0.68 | 15 | 3 | 15.466 | small | large | small | small | large | large | 0.27 | 0.21 | 0.33 | 1.125 | 0.5 |
| aggregator+verifier | aggregator,verifier | 0.673 | 12 | 2 | 15.573 | small | small | small | small | large | large | 0.263 | 0.207 | 0.32 | 1.097 | 0.333 |
| step_2+aggregator+verifier | aggregator,step_2,verifier | 0.673 | 15 | 3 | 16.051 | small | small | large | small | large | large | 0.263 | 0.207 | 0.323 | 1.097 | 0.5 |
| planner+aggregator+verifier | aggregator,planner,verifier | 0.67 | 15 | 3 | 16.248 | large | small | small | small | large | large | 0.26 | 0.2 | 0.32 | 1.083 | 0.5 |
| step_1+step_3+aggregator+verifier | aggregator,step_1,step_3,verifier | 0.67 | 18 | 4 | 15.422 | small | large | small | large | large | large | 0.26 | 0.2 | 0.32 | 1.083 | 0.667 |
| step_2+step_3+aggregator+verifier | aggregator,step_2,step_3,verifier | 0.67 | 18 | 4 | 16.313 | small | small | large | large | large | large | 0.26 | 0.203 | 0.32 | 1.083 | 0.667 |

8 of 64 rows shown.
