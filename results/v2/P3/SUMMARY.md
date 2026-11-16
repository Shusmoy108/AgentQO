# Phase P3

Generated 2026-11-16 13:58 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| math_q3_14/labels | finished |
| math_q3_14/labels_disagree | finished |
| math_q3_14/plans | finished |

## math_q3_14/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.235 | 0.021 | 0.005 | -0.045 | 0.055 | -0.001 | -0.002 | 200 | 200 | 200 |
| step_1 | 200 | 0.405 | 0.037 | 0.035 | -0.005 | 0.075 | 0.008 | 0.02 | 147 | 200 | 200 |
| step_2 | 200 | 0.49 | 0.051 | 0.04 | 0 | 0.08 | 0.009 | 0.009 | 138 | 200 | 200 |
| step_3 | 200 | 0.42 | 0 | 0.015 | -0.025 | 0.055 | -0.007 | 0 | 103 | 200 | 200 |
| aggregator | 200 | 0.21 | 0.048 | 0.02 | -0.035 | 0.075 | 0.006 | 0.014 | 73 | 200 | 200 |
| verifier | 200 | 0.3 | 0.8 | 0.24 | 0.18 | 0.3 | 0.287 | 0.274 | 132 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | -0.01 |
| planner | llm_subtle_wrong | 200 | 0 |
| planner | resample_disagree | 200 | -0.01 |
| step_1 | numeric_perturb | 198 | 0.018 |
| step_1 | swap_other_task | 196 | 0.015 |
| step_2 | numeric_perturb | 197 | 0.02 |
| step_2 | swap_other_task | 197 | 0.015 |
| step_3 | numeric_perturb | 199 | -0.015 |
| step_3 | swap_other_task | 198 | -0.018 |
| aggregator | numeric_perturb | 200 | 0.037 |
| aggregator | swap_other_task | 200 | 0.025 |
| verifier | swap_other_task | 197 | 0.949 |
| step_1 | resample_disagree | 147 | 0.048 |
| step_2 | resample_disagree | 138 | 0.018 |
| step_3 | resample_disagree | 103 | 0 |
| aggregator | resample_disagree | 73 | 0.068 |
| verifier | resample_disagree | 132 | 0.886 |
| verifier | llm_subtle_wrong | 6 | 0.667 |
| verifier | numeric_perturb | 2 | -0.25 |
| step_1 | llm_subtle_wrong | 1 | 1 |

## math_q3_14/labels_disagree

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.235 | 0.021 | 0.005 | -0.045 | 0.055 | -0.001 | -0.002 | 200 | 200 | 200 |
| step_1 | 200 | 0.405 | 0.037 | 0.015 | -0.015 | 0.05 | -5.22e-04 | 0.011 | 147 | 81 | 200 |
| step_2 | 200 | 0.49 | 0.051 | 0.025 | -0.01 | 0.06 | 0.001 | 0.002 | 138 | 98 | 200 |
| step_3 | 200 | 0.42 | 0 | 0 | -0.03 | 0.03 | -0.013 | -0.012 | 103 | 84 | 200 |
| aggregator | 200 | 0.21 | 0.048 | 0.01 | -0.015 | 0.04 | 0.004 | 0.006 | 73 | 42 | 200 |
| verifier | 200 | 0.3 | 0.8 | 0.24 | 0.18 | 0.3 | 0.287 | 0.274 | 132 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | -0.01 |
| planner | llm_subtle_wrong | 200 | 0 |
| planner | resample_disagree | 200 | -0.01 |
| step_1 | numeric_perturb | 198 | -0.003 |
| step_1 | swap_other_task | 196 | -0.005 |
| step_2 | numeric_perturb | 197 | 0.005 |
| step_2 | swap_other_task | 197 | 0 |
| step_3 | numeric_perturb | 199 | -0.03 |
| step_3 | swap_other_task | 198 | -0.033 |
| aggregator | numeric_perturb | 200 | 0.028 |
| aggregator | swap_other_task | 200 | 0.015 |
| verifier | swap_other_task | 197 | 0.949 |
| step_1 | resample_disagree | 147 | 0.027 |
| step_2 | resample_disagree | 138 | 0.004 |
| step_3 | resample_disagree | 103 | -0.029 |
| aggregator | resample_disagree | 73 | 0.027 |
| verifier | resample_disagree | 132 | 0.886 |
| verifier | llm_subtle_wrong | 6 | 0.667 |
| verifier | numeric_perturb | 2 | -0.25 |
| step_1 | llm_subtle_wrong | 1 | 1 |

## math_q3_14/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| step_1+step_2+step_3+aggregator+verifier | aggregator,step_1,step_2,step_3,verifier | 0.892 | 21 | 5 | 12.642 | small | large | large | large | large | large | 0.217 | 0.172 | 0.263 | 1.048 | 0.833 |
| step_1+aggregator+verifier | aggregator,step_1,verifier | 0.89 | 15 | 3 | 9.768 | small | large | small | small | large | large | 0.215 | 0.17 | 0.263 | 1.036 | 0.5 |
| step_3+aggregator+verifier | aggregator,step_3,verifier | 0.89 | 15 | 3 | 9.493 | small | small | small | large | large | large | 0.215 | 0.17 | 0.263 | 1.036 | 0.5 |
| step_1+step_3+aggregator+verifier | aggregator,step_1,step_3,verifier | 0.89 | 18 | 4 | 11.474 | small | large | small | large | large | large | 0.215 | 0.17 | 0.263 | 1.036 | 0.667 |
| step_1+step_2+aggregator+verifier | aggregator,step_1,step_2,verifier | 0.887 | 18 | 4 | 11.212 | small | large | large | small | large | large | 0.212 | 0.168 | 0.258 | 1.024 | 0.667 |
| planner+step_1+step_2+aggregator+verifier | aggregator,planner,step_1,step_2,verifier | 0.887 | 21 | 5 | 12.584 | large | large | large | small | large | large | 0.212 | 0.168 | 0.258 | 1.024 | 0.833 |
| step_1+step_2+verifier | step_1,step_2,verifier | 0.882 | 15 | 3 | 10.896 | small | large | large | small | small | large | 0.207 | 0.163 | 0.253 | 1 | 0.5 |
| step_1+step_3+verifier | step_1,step_3,verifier | 0.882 | 15 | 3 | 11.097 | small | large | small | large | small | large | 0.207 | 0.165 | 0.253 | 1 | 0.5 |

8 of 64 rows shown.
