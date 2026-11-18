# Phase X3

Generated 2026-11-18 04:13 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| labels_q7_G8 | finished |
| labels_q7_G8_2 | finished |
| labels_q7_P4 | finished |
| labels_q7_P4_2 | finished |
| plans | UNFINISHED |
| plans_2 | finished |

## labels_q7_G8

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.105 | -0.048 | -0.005 | -0.04 | 0.03 | 0.002 | 6.00e-04 | 200 | 200 | 200 |
| step_1 | 200 | 0.245 | 0.02 | -0.03 | -0.075 | 0.015 | -9.52e-04 | -0.01 | 72 | 200 | 200 |
| step_2 | 200 | 0.305 | -0.016 | -0.015 | -0.055 | 0.02 | -0.002 | 0 | 77 | 200 | 200 |
| step_3 | 200 | 0.275 | -0.018 | 0 | -0.04 | 0.04 | 0.003 | 0.002 | 75 | 200 | 200 |
| aggregator | 200 | 0.345 | -0.072 | -0.04 | -0.09 | 0.015 | -0.004 | -0.006 | 109 | 200 | 200 |
| verifier | 200 | 0.245 | -0.551 | -0.135 | -0.195 | -0.075 | 0.182 | -0.004 | 84 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.022 |
| planner | llm_subtle_wrong | 200 | 0.01 |
| planner | resample_disagree | 200 | 0.005 |
| step_1 | numeric_perturb | 194 | 0 |
| step_1 | swap_other_task | 196 | -0.008 |
| step_1 | resample_disagree | 72 | -0.042 |
| step_2 | numeric_perturb | 198 | -0.015 |
| step_2 | swap_other_task | 199 | 0.004 |
| step_2 | resample_disagree | 77 | 0 |
| step_3 | numeric_perturb | 196 | 0.005 |
| step_3 | swap_other_task | 197 | 0.015 |
| step_3 | resample_disagree | 75 | 0.007 |
| aggregator | numeric_perturb | 200 | 0.015 |
| aggregator | swap_other_task | 200 | -0.04 |
| aggregator | resample_disagree | 109 | -0.018 |
| verifier | swap_other_task | 199 | 0.754 |
| verifier | resample_disagree | 84 | -0.018 |
| verifier | llm_subtle_wrong | 4 | 0.75 |
| step_1 | llm_subtle_wrong | 4 | 0 |

## labels_q7_G8_2

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.105 | -0.048 | -0.005 | -0.04 | 0.03 | 0.002 | 6.00e-04 | 200 | 200 | 200 |
| step_1 | 200 | 0.245 | 0.02 | -0.03 | -0.075 | 0.015 | -9.52e-04 | -0.01 | 72 | 200 | 200 |
| step_2 | 200 | 0.305 | -0.016 | -0.015 | -0.055 | 0.02 | -0.002 | 0 | 77 | 200 | 200 |
| step_3 | 200 | 0.275 | -0.018 | 0 | -0.04 | 0.04 | 0.003 | 0.002 | 75 | 200 | 200 |
| aggregator | 200 | 0.345 | -0.072 | -0.04 | -0.09 | 0.015 | -0.004 | -0.006 | 109 | 200 | 200 |
| verifier | 200 | 0.245 | -0.551 | -0.135 | -0.195 | -0.075 | 0.182 | -0.004 | 84 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.022 |
| planner | llm_subtle_wrong | 200 | 0.01 |
| planner | resample_disagree | 200 | 0.005 |
| step_1 | numeric_perturb | 194 | 0 |
| step_1 | swap_other_task | 196 | -0.008 |
| step_1 | resample_disagree | 72 | -0.042 |
| step_2 | numeric_perturb | 198 | -0.015 |
| step_2 | swap_other_task | 199 | 0.004 |
| step_2 | resample_disagree | 77 | 0 |
| step_3 | numeric_perturb | 196 | 0.005 |
| step_3 | swap_other_task | 197 | 0.015 |
| step_3 | resample_disagree | 75 | 0.007 |
| aggregator | numeric_perturb | 200 | 0.015 |
| aggregator | swap_other_task | 200 | -0.04 |
| aggregator | resample_disagree | 109 | -0.018 |
| verifier | swap_other_task | 199 | 0.754 |
| verifier | resample_disagree | 84 | -0.018 |
| verifier | llm_subtle_wrong | 4 | 0.75 |
| step_1 | llm_subtle_wrong | 4 | 0 |

## labels_q7_P4

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.085 | -0.118 | -0.01 | -0.045 | 0.02 | 4.20e-04 | 0 | 200 | 200 | 200 |
| step_1 | 200 | 0.155 | -0.065 | -0.045 | -0.085 | -0.005 | -0.005 | 0 | 59 | 200 | 200 |
| step_2 | 200 | 0.225 | -0.022 | -0.02 | -0.055 | 0.015 | -0.003 | -0.014 | 60 | 200 | 200 |
| step_3 | 200 | 0.29 | -0.017 | 0.005 | -0.035 | 0.045 | 0.005 | 0.011 | 78 | 200 | 200 |
| aggregator | 200 | 0.315 | 0.111 | 0.065 | 0.025 | 0.11 | 0.013 | 0.062 | 110 | 200 | 200 |
| verifier | 200 | 0.11 | 0.455 | 0.05 | 0.01 | 0.095 | 0.114 | 0.09 | 67 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.018 |
| planner | llm_subtle_wrong | 199 | -0.01 |
| planner | resample_disagree | 200 | 0 |
| step_1 | numeric_perturb | 192 | -0.031 |
| step_1 | swap_other_task | 198 | -0.03 |
| step_1 | resample_disagree | 59 | 0 |
| step_2 | numeric_perturb | 193 | -0.021 |
| step_2 | swap_other_task | 200 | -0.005 |
| step_2 | resample_disagree | 60 | -0.067 |
| step_3 | numeric_perturb | 198 | 0.008 |
| step_3 | swap_other_task | 198 | 0.025 |
| step_3 | resample_disagree | 78 | 0.038 |
| aggregator | numeric_perturb | 200 | 0.015 |
| aggregator | swap_other_task | 200 | 0.07 |
| aggregator | resample_disagree | 110 | 0.209 |
| verifier | swap_other_task | 199 | 0.94 |
| verifier | resample_disagree | 67 | 0.739 |
| verifier | llm_subtle_wrong | 4 | 0.75 |
| step_1 | llm_subtle_wrong | 2 | 0 |

## labels_q7_P4_2

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.085 | -0.118 | -0.01 | -0.045 | 0.02 | 4.20e-04 | 0 | 200 | 200 | 200 |
| step_1 | 200 | 0.155 | -0.065 | -0.045 | -0.085 | -0.005 | -0.005 | 0 | 59 | 200 | 200 |
| step_2 | 200 | 0.225 | -0.022 | -0.02 | -0.055 | 0.015 | -0.003 | -0.014 | 60 | 200 | 200 |
| step_3 | 200 | 0.29 | -0.017 | 0.005 | -0.035 | 0.045 | 0.005 | 0.011 | 78 | 200 | 200 |
| aggregator | 200 | 0.315 | 0.111 | 0.065 | 0.025 | 0.11 | 0.013 | 0.062 | 110 | 200 | 200 |
| verifier | 200 | 0.11 | 0.455 | 0.05 | 0.01 | 0.095 | 0.114 | 0.09 | 67 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.018 |
| planner | llm_subtle_wrong | 199 | -0.01 |
| planner | resample_disagree | 200 | 0 |
| step_1 | numeric_perturb | 192 | -0.031 |
| step_1 | swap_other_task | 198 | -0.03 |
| step_1 | resample_disagree | 59 | 0 |
| step_2 | numeric_perturb | 193 | -0.021 |
| step_2 | swap_other_task | 200 | -0.005 |
| step_2 | resample_disagree | 60 | -0.067 |
| step_3 | numeric_perturb | 198 | 0.008 |
| step_3 | swap_other_task | 198 | 0.025 |
| step_3 | resample_disagree | 78 | 0.038 |
| aggregator | numeric_perturb | 200 | 0.015 |
| aggregator | swap_other_task | 200 | 0.07 |
| aggregator | resample_disagree | 110 | 0.209 |
| verifier | swap_other_task | 199 | 0.94 |
| verifier | resample_disagree | 67 | 0.739 |
| verifier | llm_subtle_wrong | 4 | 0.75 |
| step_1 | llm_subtle_wrong | 2 | 0 |

## plans_2

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner=large+step_1=large+step_2=large+verifier=xl | planner,step_1,step_2,verifier | 0.97 | 22 | 3 | 16.483 | large | large | large | small | small | xl | 0.1 | 0.055 | 0.15 | -0.87 | 0.889 |
| planner=xl+step_3=xl+aggregator=large+verifier=xl | aggregator,planner,step_3,verifier | 0.96 | 30 | 1 | 17.667 | xl | small | small | xl | large | xl | 0.09 | 0.04 | 0.14 | -0.783 | 1.333 |
| step_3=xl+aggregator=large+verifier=xl | aggregator,step_3,verifier | 0.955 | 23 | 1 | 16.838 | small | small | small | xl | large | xl | 0.085 | 0.035 | 0.135 | -0.739 | 0.944 |
| step_1=xl+step_3=xl+aggregator=large+verifier=xl | aggregator,step_1,step_3,verifier | 0.955 | 30 | 1 | 20.441 | small | xl | small | xl | large | xl | 0.085 | 0.04 | 0.135 | -0.739 | 1.333 |
| planner=large+step_2=large+step_3=xl+aggregator=xl+verifier=xl | aggregator,planner,step_2,step_3,verifier | 0.955 | 33 | 2 | 21.936 | large | small | large | xl | xl | xl | 0.085 | 0.035 | 0.135 | -0.739 | 1.5 |
| planner=xl+step_1=xl+step_3=xl+aggregator=large+verifier=xl | aggregator,planner,step_1,step_3,verifier | 0.955 | 37 | 1 | 20.114 | xl | xl | small | xl | large | xl | 0.085 | 0.035 | 0.135 | -0.739 | 1.722 |
| planner=large+step_1=large+step_2=large+step_3=large+aggregator=large+verifier=xl | aggregator,planner,step_1,step_2,step_3,verifier | 0.955 | 28 | 5 | 15.582 | large | large | large | large | large | xl | 0.085 | 0.035 | 0.135 | -0.739 | 1.222 |
| planner=xl+step_1=xl+step_2=large+step_3=xl+aggregator=large+verifier=xl | aggregator,planner,step_1,step_2,step_3,verifier | 0.955 | 40 | 2 | 21.619 | xl | xl | large | xl | large | xl | 0.085 | 0.035 | 0.135 | -0.739 | 1.889 |

8 of 729 rows shown.
