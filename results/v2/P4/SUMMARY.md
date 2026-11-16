# Phase P4

Generated 2026-11-16 15:04 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| hotpot_granite/labels | finished |
| hotpot_granite/labels_disagree | finished |
| hotpot_granite/plans | finished |
| hotpot_iso_granite/labels | finished |
| hotpot_iso_granite/labels_disagree | finished |
| hotpot_iso_granite/plans | finished |
| math_granite/labels | finished |
| math_granite/labels_disagree | finished |
| math_granite/plans | finished |

## hotpot_granite/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.4 | 0.087 | 0.035 | -0.02 | 0.09 | 0.017 | 0.002 | 200 | 200 | 200 |
| hop_1 | 200 | 0.935 | 0.005 | 0.005 | -0.02 | 0.03 | 0.01 | 0.005 | 199 | 200 | 200 |
| hop_2 | 200 | 0.9 | 0.006 | 0.005 | -0.015 | 0.03 | 0 | -0.014 | 200 | 200 | 200 |
| aggregator | 200 | 0.35 | 0.3 | 0.105 | 0.06 | 0.155 | 0.067 | 0.1 | 144 | 200 | 200 |
| verifier | 200 | 0.14 | -0.036 | -0.005 | -0.03 | 0.02 | 0.059 | 0.024 | 107 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.055 |
| planner | llm_subtle_wrong | 200 | 0.03 |
| planner | resample_disagree | 200 | 0.005 |
| hop_1 | swap_other_task | 200 | 0.01 |
| hop_1 | resample_disagree | 199 | 0.005 |
| hop_2 | swap_other_task | 200 | 0 |
| hop_2 | resample_disagree | 200 | -0.015 |
| aggregator | swap_other_task | 200 | 0.172 |
| aggregator | resample_disagree | 144 | 0.257 |
| verifier | swap_other_task | 200 | 0.405 |
| verifier | resample_disagree | 107 | 0.164 |
| aggregator | llm_subtle_wrong | 1 | 0 |
| verifier | llm_subtle_wrong | 1 | 0 |

## hotpot_granite/labels_disagree

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.4 | 0.087 | 0.035 | -0.02 | 0.09 | 0.017 | 0.002 | 200 | 200 | 200 |
| hop_1 | 200 | 0.935 | 0.005 | 0.005 | -0.02 | 0.03 | 0.01 | 0.005 | 199 | 187 | 200 |
| hop_2 | 200 | 0.9 | 0.006 | 0.005 | -0.015 | 0.03 | 0 | -0.014 | 200 | 180 | 200 |
| aggregator | 200 | 0.35 | 0.3 | 0.105 | 0.06 | 0.155 | 0.067 | 0.1 | 144 | 71 | 200 |
| verifier | 200 | 0.14 | -0.036 | -0.005 | -0.03 | 0.02 | 0.059 | 0.024 | 107 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.055 |
| planner | llm_subtle_wrong | 200 | 0.03 |
| planner | resample_disagree | 200 | 0.005 |
| hop_1 | swap_other_task | 200 | 0.01 |
| hop_1 | resample_disagree | 199 | 0.005 |
| hop_2 | swap_other_task | 200 | 0 |
| hop_2 | resample_disagree | 200 | -0.015 |
| aggregator | swap_other_task | 200 | 0.172 |
| aggregator | resample_disagree | 144 | 0.257 |
| verifier | swap_other_task | 200 | 0.405 |
| verifier | resample_disagree | 107 | 0.164 |
| aggregator | llm_subtle_wrong | 1 | 0 |
| verifier | llm_subtle_wrong | 1 | 0 |

## hotpot_granite/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | f1 | tier_planner | tier_hop_1 | tier_hop_2 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hop_2+aggregator+verifier | aggregator,hop_2,verifier | 0.52 | 14 | 3 | 7.604 | 0.695 | small | small | large | large | large | 0.085 | 0.043 | 0.128 | 1.03 | 0.6 |
| all_large | all | 0.517 | 20 | 5 | 9.904 | 0.695 | large | large | large | large | large | 0.083 | 0.035 | 0.13 | 1 | 1 |
| hop_1+hop_2+aggregator+verifier | aggregator,hop_1,hop_2,verifier | 0.515 | 17 | 4 | 7.913 | 0.686 | small | large | large | large | large | 0.08 | 0.035 | 0.122 | 0.97 | 0.8 |
| planner+hop_1+aggregator+verifier | aggregator,hop_1,planner,verifier | 0.512 | 17 | 4 | 9.478 | 0.698 | large | large | small | large | large | 0.077 | 0.03 | 0.125 | 0.939 | 0.8 |
| planner+hop_2+aggregator+verifier | aggregator,hop_2,planner,verifier | 0.505 | 17 | 4 | 9.556 | 0.681 | large | small | large | large | large | 0.07 | 0.022 | 0.12 | 0.848 | 0.8 |
| planner+hop_1+hop_2+aggregator | aggregator,hop_1,hop_2,planner | 0.502 | 17 | 4 | 10.01 | 0.667 | large | large | large | large | small | 0.068 | 0.022 | 0.113 | 0.818 | 0.8 |
| planner+aggregator+verifier | aggregator,planner,verifier | 0.5 | 14 | 3 | 9.174 | 0.688 | large | small | small | large | large | 0.065 | 0.018 | 0.113 | 0.788 | 0.6 |
| hop_2+aggregator | aggregator,hop_2 | 0.497 | 11 | 2 | 7.656 | 0.658 | small | small | large | large | small | 0.062 | 0.02 | 0.105 | 0.758 | 0.4 |

8 of 32 rows shown.

## hotpot_iso_granite/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.445 | 0.056 | 0.025 | -0.035 | 0.085 | 0.084 | 0.016 | 200 | 200 | 200 |
| hop_1 | 200 | 0.935 | 0.005 | 0.005 | -0.04 | 0.05 | 0.032 | 0.012 | 199 | 200 | 200 |
| hop_2 | 200 | 0.9 | 0.011 | 0.01 | -0.025 | 0.045 | 0.075 | 0.016 | 200 | 200 | 200 |
| aggregator | 200 | 0.335 | 0.254 | 0.085 | 0.04 | 0.135 | 0.056 | 0.098 | 138 | 200 | 200 |
| verifier | 200 | 0.095 | 0.053 | 0.005 | -0.015 | 0.03 | 0.049 | 0.03 | 110 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.295 |
| planner | llm_subtle_wrong | 200 | 0.065 |
| planner | resample_disagree | 200 | 0.035 |
| hop_1 | swap_other_task | 200 | 0.033 |
| hop_1 | resample_disagree | 199 | 0.013 |
| hop_2 | swap_other_task | 200 | 0.08 |
| hop_2 | resample_disagree | 200 | 0.018 |
| aggregator | swap_other_task | 200 | 0.157 |
| aggregator | resample_disagree | 138 | 0.272 |
| verifier | swap_other_task | 200 | 0.42 |
| verifier | resample_disagree | 110 | 0.259 |
| aggregator | llm_subtle_wrong | 1 | 0 |

## hotpot_iso_granite/labels_disagree

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.445 | 0.056 | 0.025 | -0.035 | 0.085 | 0.084 | 0.016 | 200 | 200 | 200 |
| hop_1 | 200 | 0.935 | 0.005 | 0.005 | -0.04 | 0.05 | 0.032 | 0.012 | 199 | 187 | 200 |
| hop_2 | 200 | 0.9 | 0.011 | 0.01 | -0.025 | 0.045 | 0.075 | 0.016 | 200 | 180 | 200 |
| aggregator | 200 | 0.335 | 0.254 | 0.085 | 0.04 | 0.135 | 0.056 | 0.098 | 138 | 68 | 200 |
| verifier | 200 | 0.095 | 0.053 | 0.005 | -0.015 | 0.03 | 0.049 | 0.03 | 110 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.295 |
| planner | llm_subtle_wrong | 200 | 0.065 |
| planner | resample_disagree | 200 | 0.035 |
| hop_1 | swap_other_task | 200 | 0.033 |
| hop_1 | resample_disagree | 199 | 0.013 |
| hop_2 | swap_other_task | 200 | 0.08 |
| hop_2 | resample_disagree | 200 | 0.018 |
| aggregator | swap_other_task | 200 | 0.157 |
| aggregator | resample_disagree | 138 | 0.272 |
| verifier | swap_other_task | 200 | 0.42 |
| verifier | resample_disagree | 110 | 0.259 |
| aggregator | llm_subtle_wrong | 1 | 0 |

## hotpot_iso_granite/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | f1 | tier_planner | tier_hop_1 | tier_hop_2 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_large | all | 0.542 | 20 | 5 | 7.397 | 0.714 | large | large | large | large | large | 0.133 | 0.083 | 0.182 | 1 | 1 |
| planner+hop_1+aggregator+verifier | aggregator,hop_1,planner,verifier | 0.52 | 17 | 4 | 6.925 | 0.696 | large | large | small | large | large | 0.11 | 0.06 | 0.16 | 0.83 | 0.8 |
| planner+hop_1+hop_2+aggregator | aggregator,hop_1,hop_2,planner | 0.515 | 17 | 4 | 8.408 | 0.679 | large | large | large | large | small | 0.105 | 0.058 | 0.152 | 0.792 | 0.8 |
| hop_2+aggregator+verifier | aggregator,hop_2,verifier | 0.505 | 14 | 3 | 5.084 | 0.662 | small | small | large | large | large | 0.095 | 0.052 | 0.138 | 0.717 | 0.6 |
| hop_1+hop_2+aggregator+verifier | aggregator,hop_1,hop_2,verifier | 0.502 | 17 | 4 | 5.399 | 0.658 | small | large | large | large | large | 0.092 | 0.048 | 0.138 | 0.698 | 0.8 |
| planner+hop_1+aggregator | aggregator,hop_1,planner | 0.5 | 14 | 3 | 7.981 | 0.672 | large | large | small | large | small | 0.09 | 0.04 | 0.14 | 0.679 | 0.6 |
| planner+aggregator+verifier | aggregator,planner,verifier | 0.497 | 14 | 3 | 6.563 | 0.666 | large | small | small | large | large | 0.087 | 0.037 | 0.138 | 0.66 | 0.6 |
| planner+hop_2+aggregator+verifier | aggregator,hop_2,planner,verifier | 0.497 | 17 | 4 | 7.07 | 0.674 | large | small | large | large | large | 0.087 | 0.035 | 0.138 | 0.66 | 0.8 |

8 of 32 rows shown.

## math_granite/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.49 | 0.122 | 0.06 | -0.02 | 0.135 | 0.07 | 0.024 | 200 | 200 | 200 |
| step_1 | 200 | 0.085 | 0.235 | -0.02 | -0.075 | 0.03 | -0.003 | 0.001 | 98 | 200 | 200 |
| step_2 | 200 | 0.32 | 0.078 | -0.005 | -0.065 | 0.055 | 0 | 0.003 | 145 | 200 | 200 |
| step_3 | 200 | 0.105 | -0.095 | 0 | -0.055 | 0.055 | 0.02 | 0 | 79 | 200 | 200 |
| aggregator | 200 | 0.235 | 0.277 | 0.035 | -0.03 | 0.1 | 0.067 | 0.064 | 114 | 200 | 200 |
| verifier | 200 | 0.37 | 0.432 | 0.16 | 0.085 | 0.23 | 0.291 | 0.242 | 165 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.138 |
| planner | llm_subtle_wrong | 200 | 0.13 |
| planner | resample_disagree | 200 | 0.045 |
| step_1 | numeric_perturb | 191 | 0.01 |
| step_1 | swap_other_task | 198 | -0.048 |
| step_1 | resample_disagree | 98 | 0.01 |
| step_2 | numeric_perturb | 196 | 0.01 |
| step_2 | swap_other_task | 192 | -0.01 |
| step_3 | numeric_perturb | 198 | 0.182 |
| step_3 | swap_other_task | 198 | 0.093 |
| aggregator | numeric_perturb | 200 | 0.305 |
| aggregator | swap_other_task | 198 | 0.23 |
| aggregator | resample_disagree | 114 | 0.254 |
| verifier | swap_other_task | 200 | 0.69 |
| verifier | resample_disagree | 165 | 0.567 |
| step_2 | resample_disagree | 145 | 0.008 |
| step_3 | resample_disagree | 79 | 0 |
| step_1 | llm_subtle_wrong | 5 | -0.2 |
| verifier | llm_subtle_wrong | 4 | 0.25 |

## math_granite/labels_disagree

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.49 | 0.122 | 0.06 | -0.02 | 0.135 | 0.07 | 0.024 | 200 | 200 | 200 |
| step_1 | 200 | 0.085 | 0.235 | 0.02 | -0.005 | 0.05 | 0.003 | 0.007 | 98 | 19 | 200 |
| step_2 | 200 | 0.32 | 0.078 | 0.025 | -0.015 | 0.065 | 0.01 | 0.019 | 145 | 64 | 200 |
| step_3 | 200 | 0.105 | -0.095 | -0.01 | -0.035 | 0.01 | 0.019 | -0.004 | 79 | 21 | 200 |
| aggregator | 200 | 0.235 | 0.277 | 0.065 | 0.015 | 0.115 | 0.074 | 0.057 | 114 | 47 | 200 |
| verifier | 200 | 0.37 | 0.432 | 0.16 | 0.085 | 0.23 | 0.291 | 0.242 | 165 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.138 |
| planner | llm_subtle_wrong | 200 | 0.13 |
| planner | resample_disagree | 200 | 0.045 |
| step_1 | numeric_perturb | 191 | 0.052 |
| step_1 | swap_other_task | 198 | -0.008 |
| step_1 | resample_disagree | 98 | 0.051 |
| step_2 | numeric_perturb | 196 | 0.041 |
| step_2 | swap_other_task | 192 | 0.016 |
| step_3 | numeric_perturb | 198 | 0.172 |
| step_3 | swap_other_task | 198 | 0.083 |
| aggregator | numeric_perturb | 200 | 0.335 |
| aggregator | swap_other_task | 198 | 0.26 |
| aggregator | resample_disagree | 114 | 0.228 |
| verifier | swap_other_task | 200 | 0.69 |
| verifier | resample_disagree | 165 | 0.567 |
| step_2 | resample_disagree | 145 | 0.056 |
| step_3 | resample_disagree | 79 | -0.025 |
| step_1 | llm_subtle_wrong | 5 | -0.2 |
| verifier | llm_subtle_wrong | 4 | 0.25 |

## math_granite/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+step_2+step_3+aggregator+verifier | aggregator,planner,step_2,step_3,verifier | 0.75 | 21 | 5 | 9.615 | large | small | large | large | large | large | 0.278 | 0.22 | 0.338 | 1.028 | 0.833 |
| all_large | all | 0.743 | 24 | 6 | 9.643 | large | large | large | large | large | large | 0.27 | 0.21 | 0.33 | 1 | 1 |
| planner+step_1+aggregator+verifier | aggregator,planner,step_1,verifier | 0.738 | 18 | 4 | 8.9 | large | large | small | small | large | large | 0.265 | 0.205 | 0.325 | 0.981 | 0.667 |
| planner+step_2+aggregator+verifier | aggregator,planner,step_2,verifier | 0.733 | 18 | 4 | 9.229 | large | small | large | small | large | large | 0.26 | 0.202 | 0.32 | 0.963 | 0.667 |
| planner+step_1+step_3+aggregator+verifier | aggregator,planner,step_1,step_3,verifier | 0.73 | 21 | 5 | 9.348 | large | large | small | large | large | large | 0.258 | 0.2 | 0.315 | 0.954 | 0.833 |
| planner+step_1+step_2+step_3+verifier | planner,step_1,step_2,step_3,verifier | 0.728 | 21 | 5 | 9.382 | large | large | large | large | small | large | 0.255 | 0.198 | 0.312 | 0.944 | 0.833 |
| planner+step_3+aggregator+verifier | aggregator,planner,step_3,verifier | 0.723 | 18 | 4 | 9.105 | large | small | small | large | large | large | 0.25 | 0.193 | 0.307 | 0.926 | 0.667 |
| planner+step_1+verifier | planner,step_1,verifier | 0.718 | 15 | 3 | 8.5 | large | large | small | small | small | large | 0.245 | 0.188 | 0.305 | 0.907 | 0.5 |

8 of 64 rows shown.
