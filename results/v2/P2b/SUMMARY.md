# Phase P2b

Generated 2026-11-16 15:36 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| math_tiers/labels | finished |
| math_tiers/labels_disagree | finished |
| math_tiers/plans | finished |

## math_tiers/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.445 | 0.202 | 0.09 | 0.025 | 0.16 | 0.058 | 0.051 | 200 | 200 | 200 |
| step_1 | 200 | 0.41 | 0.061 | 0.045 | -0.02 | 0.11 | 0.012 | 0.025 | 190 | 200 | 200 |
| step_2 | 200 | 0.465 | 0.086 | 0.05 | -0.01 | 0.11 | 0.04 | 0.032 | 181 | 200 | 200 |
| step_3 | 200 | 0.395 | 0.152 | 0.075 | 0.01 | 0.14 | 0.053 | 0.049 | 161 | 200 | 200 |
| aggregator | 200 | 0.3 | 0.2 | 0.075 | 0.005 | 0.14 | 0.012 | 0.053 | 99 | 200 | 200 |
| verifier | 200 | 0.475 | 0.768 | 0.365 | 0.295 | 0.44 | 0.457 | 0.439 | 190 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.142 |
| planner | resample_disagree | 200 | 0.105 |
| step_1 | numeric_perturb | 192 | 0.036 |
| step_1 | swap_other_task | 198 | 0.013 |
| step_1 | resample_disagree | 190 | 0.058 |
| step_2 | numeric_perturb | 200 | 0.098 |
| step_2 | swap_other_task | 196 | 0.054 |
| step_2 | resample_disagree | 181 | 0.061 |
| step_3 | numeric_perturb | 196 | 0.107 |
| step_3 | swap_other_task | 197 | 0.16 |
| step_3 | resample_disagree | 161 | 0.124 |
| aggregator | numeric_perturb | 197 | 0.005 |
| aggregator | swap_other_task | 199 | 0.08 |
| verifier | swap_other_task | 199 | 0.869 |
| verifier | resample_disagree | 190 | 0.837 |
| aggregator | resample_disagree | 99 | 0.182 |
| planner | llm_subtle_wrong | 88 | 0.068 |
| step_1 | llm_subtle_wrong | 5 | 0.2 |
| verifier | llm_subtle_wrong | 3 | 1 |
| verifier | numeric_perturb | 1 | 1 |
| aggregator | llm_subtle_wrong | 1 | 0 |

## math_tiers/labels_disagree

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.445 | 0.202 | 0.09 | 0.025 | 0.16 | 0.058 | 0.051 | 200 | 200 | 200 |
| step_1 | 200 | 0.41 | 0.061 | 0.025 | -0.025 | 0.075 | 0.003 | 0.014 | 190 | 85 | 200 |
| step_2 | 200 | 0.465 | 0.086 | 0.04 | -0.01 | 0.095 | 0.035 | 0.026 | 181 | 93 | 200 |
| step_3 | 200 | 0.395 | 0.152 | 0.06 | 0.01 | 0.11 | 0.047 | 0.039 | 161 | 79 | 200 |
| aggregator | 200 | 0.3 | 0.2 | 0.06 | 0.005 | 0.115 | 0.008 | 0.047 | 99 | 60 | 200 |
| verifier | 200 | 0.475 | 0.768 | 0.365 | 0.295 | 0.44 | 0.457 | 0.439 | 190 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.142 |
| planner | resample_disagree | 200 | 0.105 |
| step_1 | numeric_perturb | 192 | 0.016 |
| step_1 | swap_other_task | 198 | -0.008 |
| step_1 | resample_disagree | 190 | 0.032 |
| step_2 | numeric_perturb | 200 | 0.087 |
| step_2 | swap_other_task | 196 | 0.043 |
| step_2 | resample_disagree | 181 | 0.05 |
| step_3 | numeric_perturb | 196 | 0.092 |
| step_3 | swap_other_task | 197 | 0.145 |
| step_3 | resample_disagree | 161 | 0.099 |
| aggregator | numeric_perturb | 197 | -0.01 |
| aggregator | swap_other_task | 199 | 0.065 |
| verifier | swap_other_task | 199 | 0.869 |
| verifier | resample_disagree | 190 | 0.837 |
| aggregator | resample_disagree | 99 | 0.162 |
| planner | llm_subtle_wrong | 88 | 0.068 |
| step_1 | llm_subtle_wrong | 5 | 0.2 |
| verifier | llm_subtle_wrong | 3 | 1 |
| verifier | numeric_perturb | 1 | 1 |
| aggregator | llm_subtle_wrong | 1 | 0 |

## math_tiers/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner=large+step_3=xl+verifier=xl | planner,step_3,verifier | 0.905 | 23 | 1 | 12.853 | large | small | small | xl | small | xl | 0.435 | 0.36 | 0.51 | 1.261 | 0.944 |
| planner=large+step_1=xl+step_2=large+aggregator=large+verifier=xl | aggregator,planner,step_1,step_2,verifier | 0.905 | 29 | 3 | 12.456 | large | xl | large | small | large | xl | 0.435 | 0.36 | 0.51 | 1.261 | 1.278 |
| planner=large+step_2=large+step_3=xl+aggregator=xl+verifier=xl | aggregator,planner,step_2,step_3,verifier | 0.905 | 33 | 2 | 13.479 | large | small | large | xl | xl | xl | 0.435 | 0.365 | 0.505 | 1.261 | 1.5 |
| step_1=large+step_2=xl+aggregator=large+verifier=xl | aggregator,step_1,step_2,verifier | 0.9 | 26 | 2 | 11.017 | small | large | xl | small | large | xl | 0.43 | 0.355 | 0.5 | 1.246 | 1.111 |
| step_2=xl+step_3=xl+aggregator=large+verifier=xl | aggregator,step_2,step_3,verifier | 0.9 | 30 | 1 | 14.517 | small | small | xl | xl | large | xl | 0.43 | 0.355 | 0.5 | 1.246 | 1.333 |
| planner=large+step_1=xl+step_3=large+aggregator=large+verifier=xl | aggregator,planner,step_1,step_3,verifier | 0.9 | 29 | 3 | 12.385 | large | xl | small | large | large | xl | 0.43 | 0.35 | 0.51 | 1.246 | 1.278 |
| planner=large+step_2=xl+step_3=xl+aggregator=xl+verifier=xl | aggregator,planner,step_2,step_3,verifier | 0.9 | 37 | 1 | 15.31 | large | small | xl | xl | xl | xl | 0.43 | 0.36 | 0.505 | 1.246 | 1.722 |
| planner=xl+step_1=xl+step_2=xl+aggregator=large+verifier=xl | aggregator,planner,step_1,step_2,verifier | 0.9 | 37 | 1 | 16.549 | xl | xl | xl | small | large | xl | 0.43 | 0.355 | 0.505 | 1.246 | 1.722 |

8 of 729 rows shown.
