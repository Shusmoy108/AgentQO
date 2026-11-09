# Phase P1

Generated 2026-11-09 11:59 UTC, backend `ollama`.

Code run: `161e50eff6b9182a2e7acde8125dfaad6bb0d9f3`, `182c9fff5a4fda2efdac0174040d07483428433a`, `e9fdd85b46dc1194203b064ed3bb1de131740027` **(dirty working tree)**; packaged at `182c9fff5a4fda2efdac0174040d07483428433a` (dirty).

**Resumed at more than one commit; see `provenance.jsonl`.**

**Test run on `ollama`: not a reported result.**

| step | status |
|---|---|
| hotpot_q15_7/labels | finished |
| hotpot_q15_7/labels_disagree | finished |
| math_q15_7/labels | finished |
| math_q15_7/labels_disagree | finished |

## hotpot_q15_7/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.455 | 0 | 0 | -0.05 | 0.045 | 0.009 | -0.007 | 200 | 200 | 200 |
| hop_1 | 200 | 0.905 | 0.017 | 0.01 | -0.045 | 0.06 | 0.014 | 0.045 | 200 | 200 | 200 |
| hop_2 | 200 | 0.82 | -0.006 | -0.01 | -0.045 | 0.025 | -0.004 | 0.011 | 195 | 200 | 200 |
| aggregator | 200 | 0.595 | 0.244 | 0.135 | 0.08 | 0.19 | 0.095 | 0.139 | 184 | 200 | 200 |
| verifier | 200 | 0.395 | 0.228 | 0.09 | 0.04 | 0.145 | 0.183 | 0.139 | 178 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.015 |
| planner | llm_subtle_wrong | 137 | 0.029 |
| planner | resample_disagree | 200 | -0.015 |
| hop_1 | swap_other_task | 200 | 0.015 |
| hop_1 | resample_disagree | 200 | 0.05 |
| hop_2 | swap_other_task | 200 | -0.005 |
| hop_2 | resample_disagree | 195 | 0.013 |
| aggregator | swap_other_task | 200 | 0.157 |
| verifier | swap_other_task | 199 | 0.407 |
| verifier | resample_disagree | 178 | 0.309 |
| aggregator | resample_disagree | 184 | 0.228 |
| hop_1 | llm_subtle_wrong | 1 | 0 |
| verifier | llm_subtle_wrong | 1 | 0 |

## hotpot_q15_7/labels_disagree

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.455 | 0 | 0 | -0.05 | 0.045 | 0.009 | -0.007 | 200 | 200 | 200 |
| hop_1 | 200 | 0.905 | 0.017 | 0.015 | -0.035 | 0.065 | 0.018 | 0.05 | 200 | 182 | 200 |
| hop_2 | 200 | 0.82 | -0.006 | -0.005 | -0.035 | 0.025 | 0 | 0.015 | 195 | 164 | 200 |
| aggregator | 200 | 0.595 | 0.244 | 0.145 | 0.095 | 0.2 | 0.101 | 0.146 | 184 | 119 | 200 |
| verifier | 200 | 0.395 | 0.228 | 0.09 | 0.04 | 0.145 | 0.183 | 0.139 | 178 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.015 |
| planner | llm_subtle_wrong | 137 | 0.029 |
| planner | resample_disagree | 200 | -0.015 |
| hop_1 | swap_other_task | 200 | 0.02 |
| hop_1 | resample_disagree | 200 | 0.055 |
| hop_2 | swap_other_task | 200 | 0 |
| hop_2 | resample_disagree | 195 | 0.018 |
| aggregator | swap_other_task | 200 | 0.167 |
| verifier | swap_other_task | 199 | 0.407 |
| verifier | resample_disagree | 178 | 0.309 |
| aggregator | resample_disagree | 184 | 0.239 |
| hop_1 | llm_subtle_wrong | 1 | 0 |
| verifier | llm_subtle_wrong | 1 | 0 |

## math_q15_7/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.6 | 0.033 | 0.02 | -0.055 | 0.095 | 0.04 | 0.017 | 200 | 200 | 200 |
| step_1 | 200 | 0.52 | 0.096 | 0.035 | -0.04 | 0.11 | 0.05 | 0.05 | 194 | 200 | 200 |
| step_2 | 200 | 0.62 | 0.089 | 0.055 | -0.015 | 0.125 | 0.059 | 0.059 | 191 | 200 | 200 |
| step_3 | 200 | 0.515 | 0.146 | 0.065 | 0 | 0.13 | 0.087 | 0.044 | 163 | 200 | 200 |
| aggregator | 200 | 0.425 | 0.318 | 0.165 | 0.09 | 0.235 | 0.038 | 0.15 | 120 | 200 | 200 |
| verifier | 200 | 0.625 | 0.64 | 0.4 | 0.315 | 0.48 | 0.521 | 0.496 | 198 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.043 |
| planner | llm_subtle_wrong | 117 | 0.085 |
| planner | resample_disagree | 200 | 0.025 |
| step_1 | numeric_perturb | 195 | 0.059 |
| step_1 | swap_other_task | 195 | 0.115 |
| step_1 | resample_disagree | 194 | 0.088 |
| step_2 | numeric_perturb | 197 | 0.107 |
| step_2 | swap_other_task | 195 | 0.079 |
| step_2 | resample_disagree | 191 | 0.094 |
| step_3 | numeric_perturb | 198 | 0.184 |
| step_3 | swap_other_task | 198 | 0.154 |
| step_3 | resample_disagree | 163 | 0.086 |
| aggregator | numeric_perturb | 195 | 0.046 |
| aggregator | swap_other_task | 200 | 0.125 |
| verifier | swap_other_task | 199 | 0.804 |
| verifier | resample_disagree | 198 | 0.765 |
| aggregator | resample_disagree | 120 | 0.342 |

## math_q15_7/labels_disagree

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.6 | 0.033 | 0.02 | -0.055 | 0.095 | 0.04 | 0.017 | 200 | 200 | 200 |
| step_1 | 200 | 0.52 | 0.096 | 0.05 | -0.01 | 0.11 | 0.06 | 0.059 | 194 | 104 | 200 |
| step_2 | 200 | 0.62 | 0.089 | 0.055 | -0.01 | 0.115 | 0.06 | 0.059 | 191 | 124 | 200 |
| step_3 | 200 | 0.515 | 0.146 | 0.075 | 0.015 | 0.135 | 0.093 | 0.047 | 163 | 103 | 200 |
| aggregator | 200 | 0.425 | 0.318 | 0.135 | 0.07 | 0.195 | 0.025 | 0.147 | 120 | 85 | 200 |
| verifier | 200 | 0.625 | 0.64 | 0.4 | 0.315 | 0.48 | 0.521 | 0.496 | 198 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.043 |
| planner | llm_subtle_wrong | 117 | 0.085 |
| planner | resample_disagree | 200 | 0.025 |
| step_1 | numeric_perturb | 195 | 0.079 |
| step_1 | swap_other_task | 195 | 0.131 |
| step_1 | resample_disagree | 194 | 0.103 |
| step_2 | numeric_perturb | 197 | 0.107 |
| step_2 | swap_other_task | 195 | 0.085 |
| step_2 | resample_disagree | 191 | 0.094 |
| step_3 | numeric_perturb | 198 | 0.194 |
| step_3 | swap_other_task | 198 | 0.164 |
| step_3 | resample_disagree | 163 | 0.092 |
| aggregator | numeric_perturb | 195 | 0.015 |
| aggregator | swap_other_task | 200 | 0.095 |
| verifier | swap_other_task | 199 | 0.804 |
| verifier | resample_disagree | 198 | 0.765 |
| aggregator | resample_disagree | 120 | 0.333 |
