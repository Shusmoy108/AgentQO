# Phase P2c

Generated 2026-11-16 16:35 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| complex_q15_7/labels | finished |
| complex_q15_7/labels_disagree | finished |
| complex_q15_7/plans | finished |

## complex_q15_7/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.54 | -0.074 | -0.04 | -0.115 | 0.035 | 0.031 | 0.038 | 200 | 200 | 200 |
| researcher_1 | 200 | 0.79 | 0.013 | 0.02 | -0.035 | 0.08 | 0.018 | 0.012 | 198 | 200 | 200 |
| researcher_2 | 200 | 0.815 | -0.086 | -0.085 | -0.155 | -0.015 | -0.038 | -0.054 | 196 | 200 | 200 |
| step_1_1 | 200 | 0.58 | 0.009 | 0.01 | -0.03 | 0.05 | 0.002 | -0.013 | 191 | 200 | 200 |
| step_1_2 | 200 | 0.445 | 0 | -0.01 | -0.06 | 0.04 | 0.01 | 0.008 | 176 | 200 | 200 |
| step_2_1 | 200 | 0.52 | -0.019 | -0.01 | -0.065 | 0.04 | 0.016 | 0.012 | 186 | 200 | 200 |
| step_2_2 | 200 | 0.305 | -0.049 | -0.01 | -0.06 | 0.04 | 0.03 | 0.036 | 166 | 200 | 200 |
| aggregator | 200 | 0.3 | 0.117 | 0.035 | -0.03 | 0.105 | 0.02 | 0.037 | 124 | 200 | 200 |
| verifier | 200 | 0.465 | 0.505 | 0.24 | 0.165 | 0.32 | 0.406 | 0.331 | 190 | 200 | 200 |
| formatter | 200 | 0.17 | -0.441 | -0.075 | -0.12 | -0.035 | 0.09 | -0.032 | 50 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.036 |
| planner | llm_subtle_wrong | 105 | 0.095 |
| planner | resample_disagree | 200 | 0.07 |
| researcher_1 | numeric_perturb | 200 | 0.05 |
| researcher_1 | swap_other_task | 199 | -0.005 |
| researcher_1 | resample_disagree | 198 | 0.015 |
| researcher_2 | numeric_perturb | 199 | -0.033 |
| researcher_2 | swap_other_task | 197 | -0.061 |
| researcher_2 | resample_disagree | 196 | -0.066 |
| step_1_1 | numeric_perturb | 199 | 0.015 |
| step_1_1 | swap_other_task | 194 | -0.008 |
| step_1_1 | resample_disagree | 191 | -0.021 |
| step_1_2 | numeric_perturb | 199 | 0.025 |
| step_1_2 | swap_other_task | 196 | 0.018 |
| step_1_2 | resample_disagree | 176 | 0.017 |
| step_2_1 | numeric_perturb | 200 | 0.037 |
| step_2_1 | swap_other_task | 194 | 0.021 |
| step_2_1 | resample_disagree | 186 | 0.022 |
| step_2_2 | numeric_perturb | 199 | 0.113 |
| step_2_2 | swap_other_task | 196 | 0.046 |
| step_2_2 | resample_disagree | 166 | 0.096 |
| aggregator | numeric_perturb | 198 | 0.061 |
| aggregator | swap_other_task | 198 | 0.056 |
| verifier | swap_other_task | 196 | 0.811 |
| verifier | resample_disagree | 190 | 0.663 |
| formatter | numeric_perturb | 200 | 0.5 |
| formatter | swap_other_task | 200 | 0.502 |
| aggregator | resample_disagree | 124 | 0.109 |
| formatter | resample_disagree | 50 | -0.18 |
| verifier | llm_subtle_wrong | 2 | 1 |
| verifier | numeric_perturb | 1 | 1 |

## complex_q15_7/labels_disagree

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.54 | -0.074 | -0.04 | -0.115 | 0.035 | 0.031 | 0.038 | 200 | 200 | 200 |
| researcher_1 | 200 | 0.79 | 0.013 | 0.01 | -0.04 | 0.06 | 0.01 | 0.004 | 198 | 158 | 200 |
| researcher_2 | 200 | 0.815 | -0.086 | -0.07 | -0.135 | -0.005 | -0.026 | -0.041 | 196 | 163 | 200 |
| step_1_1 | 200 | 0.58 | 0.009 | 0.005 | -0.03 | 0.035 | 8.17e-04 | -0.017 | 191 | 116 | 200 |
| step_1_2 | 200 | 0.445 | 0 | 0 | -0.04 | 0.04 | 0.013 | 0.013 | 176 | 89 | 200 |
| step_2_1 | 200 | 0.52 | -0.019 | -0.01 | -0.055 | 0.035 | 0.016 | 0.012 | 186 | 104 | 200 |
| step_2_2 | 200 | 0.305 | -0.049 | -0.015 | -0.055 | 0.02 | 0.028 | 0.032 | 166 | 61 | 200 |
| aggregator | 200 | 0.3 | 0.117 | 0.035 | -0.02 | 0.09 | 0.02 | 0.042 | 124 | 60 | 200 |
| verifier | 200 | 0.465 | 0.505 | 0.235 | 0.16 | 0.315 | 0.404 | 0.328 | 190 | 93 | 200 |
| formatter | 200 | 0.17 | -0.441 | -0.075 | -0.12 | -0.035 | 0.09 | -0.032 | 50 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.036 |
| planner | llm_subtle_wrong | 105 | 0.095 |
| planner | resample_disagree | 200 | 0.07 |
| researcher_1 | numeric_perturb | 200 | 0.04 |
| researcher_1 | swap_other_task | 199 | -0.015 |
| researcher_1 | resample_disagree | 198 | 0.005 |
| researcher_2 | numeric_perturb | 199 | -0.018 |
| researcher_2 | swap_other_task | 197 | -0.046 |
| researcher_2 | resample_disagree | 196 | -0.051 |
| step_1_1 | numeric_perturb | 199 | 0.015 |
| step_1_1 | swap_other_task | 194 | -0.013 |
| step_1_1 | resample_disagree | 191 | -0.026 |
| step_1_2 | numeric_perturb | 199 | 0.035 |
| step_1_2 | swap_other_task | 196 | 0.023 |
| step_1_2 | resample_disagree | 176 | 0.028 |
| step_2_1 | numeric_perturb | 200 | 0.037 |
| step_2_1 | swap_other_task | 194 | 0.021 |
| step_2_1 | resample_disagree | 186 | 0.022 |
| step_2_2 | numeric_perturb | 199 | 0.108 |
| step_2_2 | swap_other_task | 196 | 0.041 |
| step_2_2 | resample_disagree | 166 | 0.084 |
| aggregator | numeric_perturb | 198 | 0.061 |
| aggregator | swap_other_task | 198 | 0.056 |
| verifier | swap_other_task | 196 | 0.806 |
| verifier | resample_disagree | 190 | 0.658 |
| formatter | numeric_perturb | 200 | 0.5 |
| formatter | swap_other_task | 200 | 0.502 |
| aggregator | resample_disagree | 124 | 0.125 |
| formatter | resample_disagree | 50 | -0.18 |
| verifier | llm_subtle_wrong | 2 | 1 |
| verifier | numeric_perturb | 1 | 1 |

## complex_q15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_researcher_1 | tier_researcher_2 | tier_step_1_1 | tier_step_1_2 | tier_step_2_1 | tier_step_2_2 | tier_aggregator | tier_verifier | tier_formatter | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+researcher_1+step_1_1+step_2_1+verifier | planner,researcher_1,step_1_1,step_2_1,verifier | 0.88 | 25 | 5 | 7.496 | large | large | small | large | small | large | small | small | large | small | 0.38 | 0.31 | 0.45 | 1.288 | 0.5 |
| planner+step_1_1+verifier | planner,step_1_1,verifier | 0.875 | 19 | 3 | 9.14 | large | small | small | large | small | small | small | small | large | small | 0.375 | 0.305 | 0.445 | 1.271 | 0.3 |
| planner+step_1_2+step_2_1+verifier | planner,step_1_2,step_2_1,verifier | 0.875 | 22 | 4 | 9.031 | large | small | small | small | large | large | small | small | large | small | 0.375 | 0.3 | 0.45 | 1.271 | 0.4 |
| planner+researcher_2+step_1_1+step_2_2+aggregator+verifier | aggregator,planner,researcher_2,step_1_1,step_2_2,verifier | 0.875 | 28 | 6 | 7.943 | large | small | large | large | small | small | large | large | large | small | 0.375 | 0.305 | 0.45 | 1.271 | 0.6 |
| planner+researcher_1+step_2_1+verifier | planner,researcher_1,step_2_1,verifier | 0.87 | 22 | 4 | 7.464 | large | large | small | small | small | large | small | small | large | small | 0.37 | 0.3 | 0.44 | 1.254 | 0.4 |
| researcher_2+step_2_1+step_2_2+aggregator+verifier | aggregator,researcher_2,step_2_1,step_2_2,verifier | 0.87 | 25 | 5 | 8.209 | small | small | large | small | small | large | large | large | large | small | 0.37 | 0.3 | 0.445 | 1.254 | 0.5 |
| planner+step_1_1+step_1_2+step_2_1+aggregator+verifier | aggregator,planner,step_1_1,step_1_2,step_2_1,verifier | 0.87 | 28 | 6 | 8.809 | large | small | small | large | large | large | small | large | large | small | 0.37 | 0.295 | 0.445 | 1.254 | 0.6 |
| planner+researcher_1+step_1_1+step_1_2+step_2_1+verifier | planner,researcher_1,step_1_1,step_1_2,step_2_1,verifier | 0.865 | 28 | 6 | 7.448 | large | large | small | large | large | large | small | small | large | small | 0.365 | 0.295 | 0.435 | 1.237 | 0.6 |

8 of 1024 rows shown.
