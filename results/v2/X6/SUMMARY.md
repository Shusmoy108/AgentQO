# Phase X6

Generated 2026-11-18 07:08 UTC, backend `vllm`.

Code run: `c1bb8338fa64acd82d82f1eb0c5a5ce6cb7b019b`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| hotpot_q7_32/labels | finished |
| hotpot_q7_32/plans | finished |
| latency/separate | finished |
| math500_q7_32/labels | finished |
| math500_q7_32/plans | finished |
| math_q7_32/labels | finished |
| math_q7_32/plans | finished |

## hotpot_q7_32/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.21 | 0.119 | 0.025 | -0.015 | 0.065 | 0.006 | 0.002 | 200 | 200 | 200 |
| hop_1 | 200 | 0.88 | 0.034 | 0.035 | -0.005 | 0.075 | 0.035 | 0.028 | 186 | 200 | 200 |
| hop_2 | 200 | 0.66 | -0.023 | -0.01 | -0.05 | 0.03 | -0.008 | 0.002 | 168 | 200 | 200 |
| aggregator | 200 | 0.17 | 0 | -0.005 | -0.05 | 0.04 | 0.011 | 0.024 | 57 | 200 | 200 |
| verifier | 200 | 0.315 | 0.19 | 0.06 | 0.005 | 0.115 | 0.186 | 0.088 | 85 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.045 |
| planner | llm_subtle_wrong | 199 | 0.005 |
| planner | resample_disagree | 200 | 0.01 |
| hop_1 | swap_other_task | 200 | 0.04 |
| hop_1 | resample_disagree | 186 | 0.032 |
| hop_2 | swap_other_task | 200 | -0.012 |
| hop_2 | resample_disagree | 168 | 0.003 |
| aggregator | swap_other_task | 200 | 0.062 |
| verifier | swap_other_task | 200 | 0.585 |
| verifier | resample_disagree | 85 | 0.276 |
| aggregator | resample_disagree | 57 | 0.14 |
| aggregator | llm_subtle_wrong | 2 | 0.5 |
| verifier | llm_subtle_wrong | 2 | 0.5 |

## hotpot_q7_32/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | f1 | tier_planner | tier_hop_1 | tier_hop_2 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+aggregator | aggregator,planner | 0.54 | 11 | 2 | 9.181 | 0.703 | large | small | small | large | small | 0.05 | 0.013 | 0.092 | 4 | 0.4 |
| hop_2+aggregator | aggregator,hop_2 | 0.537 | 11 | 2 | 9.004 | 0.697 | small | small | large | large | small | 0.048 | 0.013 | 0.085 | 3.8 | 0.4 |
| hop_2+verifier | hop_2,verifier | 0.537 | 11 | 2 | 12.145 | 0.7 | small | small | large | small | large | 0.048 | 0.003 | 0.092 | 3.8 | 0.4 |
| planner+hop_2 | hop_2,planner | 0.532 | 11 | 2 | 12.439 | 0.699 | large | small | large | small | small | 0.043 | 0.007 | 0.08 | 3.4 | 0.4 |
| aggregator+verifier | aggregator,verifier | 0.532 | 11 | 2 | 9.395 | 0.693 | small | small | small | large | large | 0.043 | 0 | 0.087 | 3.4 | 0.4 |
| planner+hop_1+aggregator | aggregator,hop_1,planner | 0.532 | 14 | 3 | 14.374 | 0.695 | large | large | small | large | small | 0.043 | 0.003 | 0.085 | 3.4 | 0.6 |
| planner+hop_1+hop_2+aggregator | aggregator,hop_1,hop_2,planner | 0.532 | 17 | 4 | 19.144 | 0.697 | large | large | large | large | small | 0.043 | 0.003 | 0.085 | 3.4 | 0.8 |
| only_aggregator | aggregator | 0.53 | 8 | 1 | 4.987 | 0.696 | small | small | small | large | small | 0.04 | 0.007 | 0.072 | 3.2 | 0.2 |

8 of 32 rows shown.

## latency/separate

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 16 | 0 | 64 | 2.601 | 5.174 | 5.443 | 4.355 | 0.859 |
| all_small | separate | 16 | 1 | 64 | 2.728 | 4.973 | 5.339 | 4.189 | 0.844 |
| only_planner | separate | 16 | 0 | 64 | 4.911 | 7.663 | 8.146 | 2.553 | 0.844 |
| only_planner | separate | 16 | 1 | 64 | 4.887 | 7.871 | 8.164 | 2.467 | 0.844 |
| only_aggregator | separate | 16 | 0 | 64 | 3.462 | 7.556 | 7.691 | 3.335 | 0.844 |
| only_aggregator | separate | 16 | 1 | 64 | 3.399 | 7.677 | 8.983 | 2.807 | 0.844 |
| only_verifier | separate | 16 | 0 | 64 | 4.29 | 10.262 | 11.467 | 2.461 | 0.859 |
| only_verifier | separate | 16 | 1 | 64 | 4.502 | 10.043 | 10.257 | 2.47 | 0.844 |
| planner+verifier | separate | 16 | 0 | 64 | 7.392 | 12.494 | 13.529 | 1.698 | 0.844 |
| planner+verifier | separate | 16 | 1 | 64 | 7.253 | 12.992 | 13.502 | 1.663 | 0.844 |
| aggregator+verifier | separate | 16 | 0 | 64 | 6.777 | 10.932 | 11.151 | 1.895 | 0.875 |
| aggregator+verifier | separate | 16 | 1 | 64 | 6.692 | 11.137 | 13.134 | 1.805 | 0.891 |
| all_large | separate | 16 | 0 | 64 | 13.78 | 21.149 | 22.736 | 0.973 | 0.891 |
| all_large | separate | 16 | 1 | 64 | 13.9 | 20.706 | 21.526 | 0.972 | 0.875 |

## math500_q7_32/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.27 | -0.241 | -0.065 | -0.12 | -0.015 | 7.29e-04 | -0.006 | 200 | 200 | 200 |
| step_1 | 200 | 0.205 | -0.317 | -0.065 | -0.11 | -0.02 | -0.002 | -0.002 | 199 | 200 | 200 |
| step_2 | 200 | 0.19 | -0.105 | -0.02 | -0.065 | 0.025 | 0.004 | 0.002 | 198 | 200 | 200 |
| step_3 | 200 | 0.185 | -0.135 | -0.025 | -0.07 | 0.02 | 0.012 | -0.006 | 197 | 200 | 200 |
| aggregator | 200 | 0.09 | -0.056 | -0.05 | -0.1 | -0.005 | 0.005 | 0.011 | 49 | 200 | 200 |
| verifier | 200 | 0.175 | -0.114 | -0.02 | -0.065 | 0.025 | 0.154 | 0.07 | 83 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | -0.025 |
| planner | llm_subtle_wrong | 200 | 0.03 |
| planner | resample_disagree | 200 | -0.02 |
| step_1 | swap_other_task | 200 | -0.022 |
| step_1 | llm_subtle_wrong | 198 | 0.01 |
| step_1 | resample_disagree | 199 | -0.01 |
| step_2 | swap_other_task | 200 | 0.021 |
| step_2 | llm_subtle_wrong | 199 | 0.015 |
| step_2 | resample_disagree | 198 | 0.01 |
| step_3 | swap_other_task | 200 | 0.025 |
| step_3 | llm_subtle_wrong | 199 | 0.09 |
| step_3 | resample_disagree | 197 | -0.028 |
| aggregator | swap_other_task | 200 | 0.042 |
| verifier | swap_other_task | 200 | 0.72 |
| verifier | resample_disagree | 83 | 0.325 |
| aggregator | resample_disagree | 49 | 0.092 |
| aggregator | llm_subtle_wrong | 9 | 0 |
| verifier | llm_subtle_wrong | 6 | 0.667 |
| aggregator | numeric_perturb | 1 | 0 |

## math500_q7_32/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+step_1+step_2+step_3+verifier | planner,step_1,step_2,step_3,verifier | 0.777 | 21 | 5 | 36.214 | large | large | large | large | small | large | 0.127 | 0.077 | 0.177 | 1.056 | 0.833 |
| all_large | all | 0.77 | 24 | 6 | 37.448 | large | large | large | large | large | large | 0.12 | 0.07 | 0.17 | 1 | 1 |
| planner+step_1+step_2+aggregator+verifier | aggregator,planner,step_1,step_2,verifier | 0.767 | 21 | 5 | 33.997 | large | large | large | small | large | large | 0.117 | 0.07 | 0.167 | 0.972 | 0.833 |
| step_1+step_2+aggregator+verifier | aggregator,step_1,step_2,verifier | 0.76 | 18 | 4 | 29.876 | small | large | large | small | large | large | 0.11 | 0.067 | 0.153 | 0.917 | 0.667 |
| step_1+step_2+step_3+verifier | step_1,step_2,step_3,verifier | 0.753 | 18 | 4 | 32.871 | small | large | large | large | small | large | 0.103 | 0.06 | 0.147 | 0.861 | 0.667 |
| planner+step_1+step_2+verifier | planner,step_1,step_2,verifier | 0.75 | 18 | 4 | 31.692 | large | large | large | small | small | large | 0.1 | 0.053 | 0.147 | 0.833 | 0.667 |
| planner+step_3+verifier | planner,step_3,verifier | 0.747 | 15 | 3 | 23.586 | large | small | small | large | small | large | 0.097 | 0.05 | 0.143 | 0.806 | 0.5 |
| step_1+step_3+verifier | step_1,step_3,verifier | 0.747 | 15 | 3 | 26.411 | small | large | small | large | small | large | 0.097 | 0.053 | 0.14 | 0.806 | 0.5 |

8 of 64 rows shown.

## math_q7_32/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.16 | -0.125 | -0.02 | -0.07 | 0.03 | 0.001 | 0.004 | 200 | 200 | 200 |
| step_1 | 200 | 0.18 | -0.083 | -0.04 | -0.08 | 0 | 0.003 | 0.003 | 60 | 200 | 200 |
| step_2 | 200 | 0.22 | -0.045 | -0.03 | -0.07 | 0.01 | 8.10e-04 | 0.004 | 60 | 200 | 200 |
| step_3 | 200 | 0.275 | -0.127 | -0.045 | -0.09 | -0.005 | -0.004 | -0.031 | 71 | 200 | 200 |
| aggregator | 200 | 0.225 | -0.067 | -0.03 | -0.085 | 0.025 | 0.005 | 0.008 | 90 | 200 | 200 |
| verifier | 200 | 0.135 | 0.593 | 0.08 | 0.035 | 0.125 | 0.155 | 0.123 | 75 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.006 |
| planner | llm_subtle_wrong | 199 | 0.01 |
| planner | resample_disagree | 200 | 0.025 |
| step_1 | numeric_perturb | 196 | 0.02 |
| step_1 | swap_other_task | 198 | 0.01 |
| step_1 | resample_disagree | 60 | 0.017 |
| step_2 | numeric_perturb | 200 | 0 |
| step_2 | swap_other_task | 200 | 0.007 |
| step_2 | resample_disagree | 60 | 0.017 |
| step_3 | numeric_perturb | 200 | -0.005 |
| step_3 | swap_other_task | 198 | -0.025 |
| step_3 | resample_disagree | 71 | -0.113 |
| aggregator | numeric_perturb | 200 | 0.01 |
| aggregator | swap_other_task | 200 | 0.033 |
| aggregator | resample_disagree | 90 | 0.033 |
| verifier | swap_other_task | 200 | 0.93 |
| verifier | resample_disagree | 75 | 0.74 |
| verifier | llm_subtle_wrong | 5 | 1 |
| step_1 | llm_subtle_wrong | 4 | 0 |

## math_q7_32/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| step_3+aggregator+verifier | aggregator,step_3,verifier | 0.94 | 15 | 3 | 10.086 | small | small | small | large | large | large | 0.12 | 0.085 | 0.158 | 1.091 | 0.5 |
| step_3+verifier | step_3,verifier | 0.938 | 12 | 2 | 9.391 | small | small | small | large | small | large | 0.117 | 0.083 | 0.155 | 1.068 | 0.333 |
| planner+step_1+step_2+step_3+verifier | planner,step_1,step_2,step_3,verifier | 0.935 | 21 | 5 | 13.842 | large | large | large | large | small | large | 0.115 | 0.08 | 0.15 | 1.045 | 0.833 |
| aggregator+verifier | aggregator,verifier | 0.932 | 12 | 2 | 8.343 | small | small | small | small | large | large | 0.113 | 0.075 | 0.15 | 1.023 | 0.333 |
| step_1+step_2+step_3+verifier | step_1,step_2,step_3,verifier | 0.932 | 18 | 4 | 12.206 | small | large | large | large | small | large | 0.113 | 0.077 | 0.15 | 1.023 | 0.667 |
| step_2+step_3+aggregator+verifier | aggregator,step_2,step_3,verifier | 0.932 | 18 | 4 | 11.406 | small | small | large | large | large | large | 0.113 | 0.075 | 0.147 | 1.023 | 0.667 |
| planner+aggregator+verifier | aggregator,planner,verifier | 0.93 | 15 | 3 | 10.326 | large | small | small | small | large | large | 0.11 | 0.072 | 0.147 | 1 | 0.5 |
| step_1+step_3+verifier | step_1,step_3,verifier | 0.93 | 15 | 3 | 11.095 | small | large | small | large | small | large | 0.11 | 0.075 | 0.145 | 1 | 0.5 |

8 of 64 rows shown.
