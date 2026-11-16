# Phase P4b

Generated 2026-11-16 17:04 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| hotpot_phi/labels | finished |
| hotpot_phi/labels_disagree | finished |
| hotpot_phi/plans | finished |
| math_phi/labels | finished |
| math_phi/labels_disagree | finished |
| math_phi/plans | finished |

## hotpot_phi/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.28 | -0.054 | -0.015 | -0.065 | 0.03 | 0.003 | 0.006 | 200 | 200 | 200 |
| hop_1 | 200 | 0.895 | -0.017 | -0.005 | -0.045 | 0.035 | -0.005 | 0.009 | 196 | 200 | 200 |
| hop_2 | 200 | 0.845 | 0.006 | 0 | -0.05 | 0.05 | 0.028 | 0.014 | 192 | 200 | 200 |
| aggregator | 200 | 0.35 | 0.157 | 0.04 | -0.005 | 0.09 | 0.052 | 0.061 | 94 | 200 | 200 |
| verifier | 200 | 0.275 | 0.055 | 0.015 | -0.035 | 0.065 | 0.127 | 0.051 | 96 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.048 |
| planner | llm_subtle_wrong | 200 | -0.03 |
| planner | resample_disagree | 200 | 0.02 |
| hop_1 | swap_other_task | 200 | -0.006 |
| hop_1 | resample_disagree | 196 | 0.01 |
| hop_2 | swap_other_task | 200 | 0.033 |
| hop_2 | resample_disagree | 192 | 0.016 |
| aggregator | swap_other_task | 200 | 0.152 |
| aggregator | resample_disagree | 94 | 0.176 |
| verifier | swap_other_task | 200 | 0.48 |
| verifier | resample_disagree | 96 | 0.193 |
| aggregator | llm_subtle_wrong | 4 | 0 |

## hotpot_phi/labels_disagree

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.28 | -0.054 | -0.015 | -0.065 | 0.03 | 0.003 | 0.006 | 200 | 200 | 200 |
| hop_1 | 200 | 0.895 | -0.017 | -0.015 | -0.05 | 0.02 | -0.015 | 0.005 | 196 | 179 | 200 |
| hop_2 | 200 | 0.845 | 0.006 | 0.005 | -0.04 | 0.05 | 0.032 | 0.018 | 192 | 169 | 200 |
| aggregator | 200 | 0.35 | 0.157 | 0.055 | 0.02 | 0.095 | 0.057 | 0.061 | 94 | 70 | 200 |
| verifier | 200 | 0.275 | 0.055 | 0.015 | -0.035 | 0.065 | 0.127 | 0.051 | 96 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.048 |
| planner | llm_subtle_wrong | 200 | -0.03 |
| planner | resample_disagree | 200 | 0.02 |
| hop_1 | swap_other_task | 200 | -0.016 |
| hop_1 | resample_disagree | 196 | 0.005 |
| hop_2 | swap_other_task | 200 | 0.037 |
| hop_2 | resample_disagree | 192 | 0.021 |
| aggregator | swap_other_task | 200 | 0.167 |
| aggregator | resample_disagree | 94 | 0.176 |
| verifier | swap_other_task | 200 | 0.48 |
| verifier | resample_disagree | 96 | 0.193 |
| aggregator | llm_subtle_wrong | 4 | 0 |

## hotpot_phi/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | f1 | tier_planner | tier_hop_1 | tier_hop_2 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+verifier | planner,verifier | 0.54 | 11 | 2 | 11.561 | 0.723 | large | small | small | small | large | 0.113 | 0.068 | 0.158 | 1.552 | 0.4 |
| planner+aggregator+verifier | aggregator,planner,verifier | 0.537 | 14 | 3 | 11.801 | 0.745 | large | small | small | large | large | 0.11 | 0.062 | 0.158 | 1.517 | 0.6 |
| planner+hop_2+aggregator | aggregator,hop_2,planner | 0.522 | 14 | 3 | 16.679 | 0.698 | large | small | large | large | small | 0.095 | 0.05 | 0.138 | 1.31 | 0.6 |
| planner+hop_1+hop_2+aggregator | aggregator,hop_1,hop_2,planner | 0.517 | 17 | 4 | 21.003 | 0.696 | large | large | large | large | small | 0.09 | 0.043 | 0.138 | 1.241 | 0.8 |
| planner+hop_2+verifier | hop_2,planner,verifier | 0.515 | 14 | 3 | 15.284 | 0.71 | large | small | large | small | large | 0.087 | 0.043 | 0.133 | 1.207 | 0.6 |
| planner+hop_1+aggregator+verifier | aggregator,hop_1,planner,verifier | 0.515 | 17 | 4 | 16.186 | 0.725 | large | large | small | large | large | 0.087 | 0.035 | 0.14 | 1.207 | 0.8 |
| planner+aggregator | aggregator,planner | 0.512 | 11 | 2 | 13.014 | 0.686 | large | small | small | large | small | 0.085 | 0.04 | 0.13 | 1.172 | 0.4 |
| hop_1+verifier | hop_1,verifier | 0.512 | 11 | 2 | 14.11 | 0.71 | small | large | small | small | large | 0.085 | 0.043 | 0.128 | 1.172 | 0.4 |

8 of 32 rows shown.

## math_phi/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.17 | 0.265 | 0.045 | 0.005 | 0.09 | 0.007 | 0.009 | 200 | 200 | 200 |
| step_1 | 200 | 0.365 | 0 | 0.01 | -0.03 | 0.05 | 0.004 | 0.017 | 106 | 200 | 200 |
| step_2 | 200 | 0.465 | 0.032 | 0.03 | -0.01 | 0.07 | 0.006 | 0.009 | 120 | 200 | 200 |
| step_3 | 200 | 0.26 | 0.058 | 0.015 | -0.03 | 0.06 | 0.014 | 0.005 | 77 | 200 | 200 |
| aggregator | 200 | 0.28 | 0.357 | 0.16 | 0.1 | 0.22 | 0.04 | 0.13 | 74 | 200 | 200 |
| verifier | 200 | 0.205 | 0.878 | 0.18 | 0.125 | 0.24 | 0.187 | 0.171 | 97 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.028 |
| planner | llm_subtle_wrong | 200 | 0.045 |
| planner | resample_disagree | 200 | 0.045 |
| step_1 | numeric_perturb | 189 | 0.008 |
| step_1 | swap_other_task | 199 | 0.013 |
| step_1 | resample_disagree | 106 | 0.047 |
| step_2 | numeric_perturb | 197 | 0.005 |
| step_2 | swap_other_task | 199 | 0.02 |
| step_2 | resample_disagree | 120 | 0.021 |
| step_3 | numeric_perturb | 198 | 0.068 |
| step_3 | swap_other_task | 198 | 0.035 |
| aggregator | numeric_perturb | 200 | 0.058 |
| aggregator | swap_other_task | 200 | 0.217 |
| verifier | swap_other_task | 199 | 0.928 |
| verifier | resample_disagree | 97 | 0.835 |
| aggregator | resample_disagree | 74 | 0.446 |
| step_3 | resample_disagree | 77 | 0.019 |
| verifier | llm_subtle_wrong | 5 | 0.8 |
| step_1 | llm_subtle_wrong | 3 | 0 |
| verifier | numeric_perturb | 3 | 0 |

## math_phi/labels_disagree

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.17 | 0.265 | 0.045 | 0.005 | 0.09 | 0.007 | 0.009 | 200 | 200 | 200 |
| step_1 | 200 | 0.365 | 0 | 0 | -0.02 | 0.02 | 0 | 0.02 | 106 | 75 | 200 |
| step_2 | 200 | 0.465 | 0.032 | 0.015 | -0.015 | 0.05 | -0.001 | 0.006 | 120 | 93 | 200 |
| step_3 | 200 | 0.26 | 0.058 | 0.015 | -0.005 | 0.04 | 0.014 | 0.009 | 77 | 52 | 200 |
| aggregator | 200 | 0.28 | 0.357 | 0.1 | 0.06 | 0.145 | 0.023 | 0.107 | 74 | 56 | 200 |
| verifier | 200 | 0.205 | 0.878 | 0.18 | 0.125 | 0.24 | 0.187 | 0.171 | 97 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.028 |
| planner | llm_subtle_wrong | 200 | 0.045 |
| planner | resample_disagree | 200 | 0.045 |
| step_1 | numeric_perturb | 189 | -0.003 |
| step_1 | swap_other_task | 199 | 0.003 |
| step_1 | resample_disagree | 106 | 0.057 |
| step_2 | numeric_perturb | 197 | -0.01 |
| step_2 | swap_other_task | 199 | 0.005 |
| step_2 | resample_disagree | 120 | 0.013 |
| step_3 | numeric_perturb | 198 | 0.068 |
| step_3 | swap_other_task | 198 | 0.035 |
| aggregator | numeric_perturb | 200 | -0.003 |
| aggregator | swap_other_task | 200 | 0.158 |
| verifier | swap_other_task | 199 | 0.928 |
| verifier | resample_disagree | 97 | 0.835 |
| aggregator | resample_disagree | 74 | 0.365 |
| step_3 | resample_disagree | 77 | 0.032 |
| verifier | llm_subtle_wrong | 5 | 0.8 |
| step_1 | llm_subtle_wrong | 3 | 0 |
| verifier | numeric_perturb | 3 | 0 |

## math_phi/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+step_1+step_2+step_3+verifier | planner,step_1,step_2,step_3,verifier | 0.96 | 21 | 5 | 18.643 | large | large | large | large | small | large | 0.215 | 0.172 | 0.258 | 1.049 | 0.833 |
| step_2+step_3+verifier | step_2,step_3,verifier | 0.958 | 15 | 3 | 16.129 | small | small | large | large | small | large | 0.212 | 0.172 | 0.258 | 1.037 | 0.5 |
| planner+step_1+step_2+verifier | planner,step_1,step_2,verifier | 0.958 | 18 | 4 | 16.92 | large | large | large | small | small | large | 0.212 | 0.17 | 0.258 | 1.037 | 0.667 |
| planner+step_1+step_3+verifier | planner,step_1,step_3,verifier | 0.958 | 18 | 4 | 18.091 | large | large | small | large | small | large | 0.212 | 0.172 | 0.255 | 1.037 | 0.667 |
| planner+step_2+step_3+aggregator+verifier | aggregator,planner,step_2,step_3,verifier | 0.958 | 21 | 5 | 18.523 | large | small | large | large | large | large | 0.212 | 0.175 | 0.255 | 1.037 | 0.833 |
| step_3+verifier | step_3,verifier | 0.955 | 12 | 2 | 14.82 | small | small | small | large | small | large | 0.21 | 0.168 | 0.255 | 1.024 | 0.333 |
| planner+step_2+verifier | planner,step_2,verifier | 0.955 | 15 | 3 | 15.302 | large | small | large | small | small | large | 0.21 | 0.17 | 0.253 | 1.024 | 0.5 |
| planner+step_3+verifier | planner,step_3,verifier | 0.955 | 15 | 3 | 15.955 | large | small | small | large | small | large | 0.21 | 0.168 | 0.253 | 1.024 | 0.5 |

8 of 64 rows shown.
