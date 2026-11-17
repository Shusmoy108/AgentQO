# Phase E1

Generated 2026-11-17 03:14 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| awq/original | finished |
| awq/passthrough | finished |
| fp16/original | finished |
| fp16/passthrough | finished |

## awq/original

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 100 | 0.41 | 0.073 | 0.03 | -0.05 | 0.12 | 0.071 | 0.055 | 100 | 100 | 100 |
| step_1 | 100 | 0.59 | 0.017 | 0 | -0.07 | 0.07 | 0.03 | 0.03 | 98 | 100 | 100 |
| step_2 | 100 | 0.56 | -0.018 | -0.01 | -0.06 | 0.04 | 0.022 | 0.007 | 94 | 100 | 100 |
| step_3 | 100 | 0.49 | 0 | 0.01 | -0.05 | 0.07 | 0.053 | 0.013 | 83 | 100 | 100 |
| aggregator | 100 | 0.41 | 0.049 | 0 | -0.07 | 0.07 | 0.03 | 0.051 | 68 | 100 | 100 |
| verifier | 100 | 0.93 | 0.118 | 0.11 | 0.01 | 0.21 | 0.164 | 0.101 | 99 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 100 | 0.07 |
| planner | llm_subtle_wrong | 82 | 0.085 |
| planner | resample_disagree | 100 | 0.06 |
| step_1 | numeric_perturb | 99 | 0.03 |
| step_1 | swap_other_task | 99 | 0.071 |
| step_1 | resample_disagree | 98 | 0.051 |
| step_2 | numeric_perturb | 98 | 0.071 |
| step_2 | swap_other_task | 100 | 0 |
| step_2 | resample_disagree | 94 | 0.011 |
| step_3 | numeric_perturb | 99 | 0.091 |
| step_3 | swap_other_task | 98 | 0.102 |
| step_3 | resample_disagree | 83 | 0.024 |
| aggregator | numeric_perturb | 97 | 0.052 |
| aggregator | swap_other_task | 99 | 0.086 |
| verifier | numeric_perturb | 97 | 0.191 |
| verifier | resample_disagree | 99 | 0.111 |
| verifier | swap_other_task | 65 | 0.169 |
| aggregator | resample_disagree | 68 | 0.118 |
| verifier | llm_subtle_wrong | 2 | 0 |

## awq/passthrough

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 100 | 0.72 | 0.194 | 0.14 | 0.03 | 0.25 | 0.152 | 0.145 | 100 | 100 | 100 |
| step_1 | 100 | 0.59 | 0.068 | -0.01 | -0.13 | 0.11 | 0.08 | 0.066 | 98 | 100 | 100 |
| step_2 | 100 | 0.56 | 0.107 | 0.05 | -0.03 | 0.13 | 0.104 | 0.101 | 94 | 100 | 100 |
| step_3 | 100 | 0.49 | 0.224 | 0.13 | 0.05 | 0.21 | 0.172 | 0.158 | 83 | 100 | 100 |
| aggregator | 100 | 0.41 | 0.512 | 0.21 | 0.13 | 0.3 | 0.226 | 0.183 | 68 | 100 | 100 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 100 | 0.232 |
| planner | llm_subtle_wrong | 82 | 0.183 |
| planner | resample_disagree | 100 | 0.2 |
| step_1 | numeric_perturb | 99 | 0.101 |
| step_1 | swap_other_task | 99 | 0.172 |
| step_1 | resample_disagree | 98 | 0.112 |
| step_2 | numeric_perturb | 98 | 0.173 |
| step_2 | swap_other_task | 100 | 0.155 |
| step_2 | resample_disagree | 94 | 0.16 |
| step_3 | numeric_perturb | 99 | 0.303 |
| step_3 | swap_other_task | 98 | 0.323 |
| step_3 | resample_disagree | 83 | 0.289 |
| aggregator | numeric_perturb | 97 | 0.526 |
| aggregator | swap_other_task | 99 | 0.51 |
| aggregator | resample_disagree | 68 | 0.419 |

## fp16/original

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 100 | 0.52 | -0.058 | -0.03 | -0.1 | 0.03 | -0.053 | -0.041 | 100 | 100 | 100 |
| step_1 | 100 | 0.45 | -0.022 | 0 | -0.06 | 0.06 | -0.004 | 0 | 94 | 100 | 100 |
| step_2 | 100 | 0.42 | 0.024 | 0.02 | -0.03 | 0.08 | 0.007 | -0.011 | 89 | 100 | 100 |
| step_3 | 100 | 0.28 | 0.071 | 0.02 | -0.03 | 0.07 | -0.003 | -0.004 | 77 | 100 | 100 |
| aggregator | 100 | 0.3 | 0.5 | 0.19 | 0.09 | 0.29 | 0.052 | 0.091 | 52 | 100 | 100 |
| verifier | 100 | 0.88 | 0.261 | 0.23 | 0.12 | 0.34 | 0.275 | 0.219 | 100 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 100 | -0.093 |
| planner | llm_subtle_wrong | 48 | -0.042 |
| planner | resample_disagree | 100 | -0.06 |
| step_1 | numeric_perturb | 99 | 0.025 |
| step_1 | swap_other_task | 98 | -0.041 |
| step_1 | resample_disagree | 94 | 0 |
| step_2 | numeric_perturb | 100 | 0.03 |
| step_2 | swap_other_task | 97 | 0 |
| step_2 | resample_disagree | 89 | -0.022 |
| step_3 | numeric_perturb | 97 | 0.031 |
| step_3 | swap_other_task | 98 | -0.053 |
| step_3 | resample_disagree | 77 | -0.013 |
| aggregator | numeric_perturb | 98 | 0.071 |
| aggregator | swap_other_task | 99 | 0.258 |
| verifier | numeric_perturb | 97 | 0.33 |
| verifier | swap_other_task | 96 | 0.333 |
| verifier | resample_disagree | 100 | 0.265 |
| aggregator | resample_disagree | 52 | 0.288 |
| step_3 | llm_subtle_wrong | 1 | 0 |

## fp16/passthrough

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 100 | 0.52 | 0.154 | 0.08 | -0.02 | 0.18 | 0.137 | 0.056 | 100 | 100 | 100 |
| step_1 | 100 | 0.45 | 0.067 | -0.08 | -0.18 | 0.02 | 0.024 | 0.008 | 94 | 100 | 100 |
| step_2 | 100 | 0.42 | -0.071 | -0.04 | -0.12 | 0.04 | 0.037 | 0 | 89 | 100 | 100 |
| step_3 | 100 | 0.28 | 0.214 | 0.05 | -0.03 | 0.13 | 0.111 | 0.05 | 77 | 100 | 100 |
| aggregator | 100 | 0.3 | 0.567 | 0.17 | 0.09 | 0.25 | 0.196 | 0.169 | 52 | 100 | 100 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 100 | 0.263 |
| planner | llm_subtle_wrong | 48 | 0.125 |
| planner | resample_disagree | 100 | 0.09 |
| step_1 | numeric_perturb | 99 | 0.177 |
| step_1 | swap_other_task | 98 | -0.077 |
| step_1 | resample_disagree | 94 | 0.016 |
| step_2 | numeric_perturb | 100 | 0.12 |
| step_2 | swap_other_task | 97 | 0.031 |
| step_2 | resample_disagree | 89 | 0 |
| step_3 | numeric_perturb | 97 | 0.443 |
| step_3 | swap_other_task | 98 | 0.308 |
| step_3 | resample_disagree | 77 | 0.169 |
| aggregator | numeric_perturb | 98 | 0.633 |
| aggregator | swap_other_task | 99 | 0.616 |
| aggregator | resample_disagree | 52 | 0.538 |
| step_3 | llm_subtle_wrong | 1 | 1 |
