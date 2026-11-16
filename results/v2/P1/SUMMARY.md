# Phase P1

Generated 2026-11-16 13:24 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| hotpot_iso_q15_7/labels | finished |
| hotpot_iso_q15_7/labels_disagree | finished |
| hotpot_q15_7/labels | finished |
| hotpot_q15_7/labels_disagree | finished |
| math_q15_7/labels | finished |
| math_q15_7/labels_disagree | finished |

## hotpot_iso_q15_7/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.61 | -0.025 | -0.015 | -0.075 | 0.05 | 0.043 | 0.028 | 200 | 200 | 200 |
| hop_1 | 200 | 0.87 | 0.063 | 0.05 | -0.01 | 0.115 | 0.144 | 0.102 | 198 | 200 | 200 |
| hop_2 | 200 | 0.77 | 0.078 | 0.06 | 0.015 | 0.105 | 0.054 | 0.054 | 197 | 200 | 200 |
| aggregator | 200 | 0.495 | 0.091 | 0.03 | -0.025 | 0.085 | 0.066 | 0.067 | 179 | 200 | 200 |
| verifier | 200 | 0.305 | 0.016 | 0.005 | -0.035 | 0.05 | 0.1 | 0.061 | 181 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.121 |
| planner | llm_subtle_wrong | 120 | -0.017 |
| planner | resample_disagree | 200 | 0.045 |
| hop_1 | swap_other_task | 200 | 0.168 |
| hop_1 | resample_disagree | 198 | 0.119 |
| hop_2 | swap_other_task | 200 | 0.068 |
| hop_2 | resample_disagree | 197 | 0.069 |
| aggregator | swap_other_task | 200 | 0.12 |
| aggregator | resample_disagree | 179 | 0.12 |
| verifier | swap_other_task | 198 | 0.283 |
| verifier | resample_disagree | 181 | 0.169 |
| aggregator | llm_subtle_wrong | 2 | 0 |
| verifier | llm_subtle_wrong | 1 | -1 |

## hotpot_iso_q15_7/labels_disagree

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.61 | -0.025 | -0.015 | -0.075 | 0.05 | 0.043 | 0.028 | 200 | 200 | 200 |
| hop_1 | 200 | 0.87 | 0.063 | 0.055 | -0.005 | 0.12 | 0.148 | 0.106 | 198 | 174 | 200 |
| hop_2 | 200 | 0.77 | 0.078 | 0.06 | 0.015 | 0.105 | 0.054 | 0.054 | 197 | 154 | 200 |
| aggregator | 200 | 0.495 | 0.091 | 0.045 | 0 | 0.09 | 0.074 | 0.076 | 179 | 99 | 200 |
| verifier | 200 | 0.305 | 0.016 | 0.005 | -0.035 | 0.05 | 0.1 | 0.061 | 181 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.121 |
| planner | llm_subtle_wrong | 120 | -0.017 |
| planner | resample_disagree | 200 | 0.045 |
| hop_1 | swap_other_task | 200 | 0.172 |
| hop_1 | resample_disagree | 198 | 0.124 |
| hop_2 | swap_other_task | 200 | 0.068 |
| hop_2 | resample_disagree | 197 | 0.069 |
| aggregator | swap_other_task | 200 | 0.135 |
| aggregator | resample_disagree | 179 | 0.137 |
| verifier | swap_other_task | 198 | 0.283 |
| verifier | resample_disagree | 181 | 0.169 |
| aggregator | llm_subtle_wrong | 2 | 0 |
| verifier | llm_subtle_wrong | 1 | -1 |

## hotpot_q15_7/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.405 | 0.049 | 0.02 | -0.035 | 0.075 | 0.015 | 0.012 | 200 | 200 | 200 |
| hop_1 | 200 | 0.87 | 0.023 | 0.02 | -0.025 | 0.065 | 0.021 | 0.063 | 198 | 200 | 200 |
| hop_2 | 200 | 0.77 | 0.006 | 0 | -0.035 | 0.035 | 0.002 | 0.006 | 197 | 200 | 200 |
| aggregator | 200 | 0.52 | 0.173 | 0.09 | 0.035 | 0.145 | 0.077 | 0.093 | 187 | 200 | 200 |
| verifier | 200 | 0.405 | 0.16 | 0.065 | 0.005 | 0.125 | 0.176 | 0.13 | 171 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.042 |
| planner | llm_subtle_wrong | 120 | 0.033 |
| planner | resample_disagree | 200 | 0.03 |
| hop_1 | swap_other_task | 200 | 0.025 |
| hop_1 | resample_disagree | 198 | 0.073 |
| hop_2 | swap_other_task | 200 | 0.003 |
| hop_2 | resample_disagree | 197 | 0.008 |
| aggregator | swap_other_task | 200 | 0.136 |
| aggregator | resample_disagree | 187 | 0.163 |
| verifier | swap_other_task | 200 | 0.412 |
| verifier | resample_disagree | 171 | 0.304 |
| aggregator | llm_subtle_wrong | 1 | 0 |

## hotpot_q15_7/labels_disagree

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.405 | 0.049 | 0.02 | -0.035 | 0.075 | 0.015 | 0.012 | 200 | 200 | 200 |
| hop_1 | 200 | 0.87 | 0.023 | 0.02 | -0.025 | 0.065 | 0.021 | 0.063 | 198 | 174 | 200 |
| hop_2 | 200 | 0.77 | 0.006 | 0.005 | -0.03 | 0.04 | 0.006 | 0.01 | 197 | 154 | 200 |
| aggregator | 200 | 0.52 | 0.173 | 0.09 | 0.04 | 0.14 | 0.077 | 0.09 | 187 | 104 | 200 |
| verifier | 200 | 0.405 | 0.16 | 0.065 | 0.005 | 0.125 | 0.176 | 0.13 | 171 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.042 |
| planner | llm_subtle_wrong | 120 | 0.033 |
| planner | resample_disagree | 200 | 0.03 |
| hop_1 | swap_other_task | 200 | 0.025 |
| hop_1 | resample_disagree | 198 | 0.073 |
| hop_2 | swap_other_task | 200 | 0.007 |
| hop_2 | resample_disagree | 197 | 0.013 |
| aggregator | swap_other_task | 200 | 0.136 |
| aggregator | resample_disagree | 187 | 0.158 |
| verifier | swap_other_task | 200 | 0.412 |
| verifier | resample_disagree | 171 | 0.304 |
| aggregator | llm_subtle_wrong | 1 | 0 |

## math_q15_7/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.495 | 0.182 | 0.09 | 0.015 | 0.16 | 0.071 | 0.052 | 200 | 200 | 200 |
| step_1 | 200 | 0.455 | -0.066 | -0.045 | -0.115 | 0.025 | -0.005 | -0.034 | 189 | 200 | 200 |
| step_2 | 200 | 0.43 | -0.035 | 0.005 | -0.05 | 0.065 | 0.02 | 0.011 | 181 | 200 | 200 |
| step_3 | 200 | 0.305 | 0.082 | 0.015 | -0.045 | 0.07 | 0.039 | 0.01 | 156 | 200 | 200 |
| aggregator | 200 | 0.345 | 0.304 | 0.115 | 0.05 | 0.18 | 0.031 | 0.084 | 107 | 200 | 200 |
| verifier | 200 | 0.485 | 0.66 | 0.32 | 0.245 | 0.395 | 0.426 | 0.413 | 190 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.136 |
| planner | llm_subtle_wrong | 91 | 0.165 |
| planner | resample_disagree | 200 | 0.105 |
| step_1 | numeric_perturb | 197 | 0.058 |
| step_1 | swap_other_task | 196 | -0.079 |
| step_1 | resample_disagree | 189 | -0.071 |
| step_2 | numeric_perturb | 199 | 0.078 |
| step_2 | swap_other_task | 195 | 0.003 |
| step_2 | resample_disagree | 181 | 0.022 |
| step_3 | numeric_perturb | 196 | 0.151 |
| step_3 | swap_other_task | 198 | 0.104 |
| step_3 | resample_disagree | 156 | 0.032 |
| aggregator | numeric_perturb | 195 | 0.056 |
| aggregator | swap_other_task | 199 | 0.123 |
| verifier | swap_other_task | 199 | 0.824 |
| verifier | resample_disagree | 190 | 0.792 |
| aggregator | resample_disagree | 107 | 0.248 |
| step_3 | llm_subtle_wrong | 2 | 0 |
| verifier | llm_subtle_wrong | 3 | 0.333 |
| step_2 | llm_subtle_wrong | 1 | 0 |
| verifier | numeric_perturb | 1 | 1 |

## math_q15_7/labels_disagree

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.495 | 0.182 | 0.09 | 0.015 | 0.16 | 0.071 | 0.052 | 200 | 200 | 200 |
| step_1 | 200 | 0.455 | -0.066 | -0.03 | -0.08 | 0.025 | 0.002 | -0.027 | 189 | 91 | 200 |
| step_2 | 200 | 0.43 | -0.035 | -0.015 | -0.06 | 0.03 | 0.01 | 0 | 181 | 86 | 200 |
| step_3 | 200 | 0.305 | 0.082 | 0.025 | -0.025 | 0.075 | 0.042 | 0.014 | 156 | 61 | 200 |
| aggregator | 200 | 0.345 | 0.304 | 0.105 | 0.05 | 0.16 | 0.027 | 0.084 | 107 | 69 | 200 |
| verifier | 200 | 0.485 | 0.66 | 0.32 | 0.245 | 0.395 | 0.426 | 0.413 | 190 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.136 |
| planner | llm_subtle_wrong | 91 | 0.165 |
| planner | resample_disagree | 200 | 0.105 |
| step_1 | numeric_perturb | 197 | 0.074 |
| step_1 | swap_other_task | 196 | -0.064 |
| step_1 | resample_disagree | 189 | -0.056 |
| step_2 | numeric_perturb | 199 | 0.058 |
| step_2 | swap_other_task | 195 | -0.018 |
| step_2 | resample_disagree | 181 | 0 |
| step_3 | numeric_perturb | 196 | 0.161 |
| step_3 | swap_other_task | 198 | 0.114 |
| step_3 | resample_disagree | 156 | 0.045 |
| aggregator | numeric_perturb | 195 | 0.046 |
| aggregator | swap_other_task | 199 | 0.113 |
| verifier | swap_other_task | 199 | 0.824 |
| verifier | resample_disagree | 190 | 0.792 |
| aggregator | resample_disagree | 107 | 0.248 |
| step_3 | llm_subtle_wrong | 2 | 0 |
| verifier | llm_subtle_wrong | 3 | 0.333 |
| step_2 | llm_subtle_wrong | 1 | 0 |
| verifier | numeric_perturb | 1 | 1 |
