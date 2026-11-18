# Phase X7

Generated 2026-11-18 04:54 UTC, backend `vllm`.

Code run: `aececaa1e00a6ad31b37dd84c70c5d6a061c4a74`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| code_c15_7/labels | finished |
| code_c15_7/plans | finished |

## code_c15_7/labels

### labels_v2.csv

| agent | n | p_dis | g_dis | uv | uv_ci_low | uv_ci_high | ec_synthetic | ec_real | ec_real_n_used | reruns_used | reruns_full |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planner | 200 | 0.91 | 0.17 | 0.155 | 0.08 | 0.23 | 0.22 | 0.234 | 200 | 200 | 200 |
| coder | 200 | 0.585 | 0.026 | 0.015 | -0.015 | 0.05 | 0.055 | 0.014 | 194 | 200 | 200 |
| tester | 200 | 0.99 | 0.02 | 0.02 | -0.02 | 0.065 | 0.155 | 0.03 | 200 | 200 | 200 |
| fixer | 200 | 0.54 | 0.278 | 0.15 | 0.1 | 0.2 | 0.064 | 0.166 | 200 | 200 | 200 |
| verifier | 200 | 0.2 | 0.375 | 0.075 | 0.04 | 0.115 | 0.136 | 0.095 | 193 | 0 | 0 |

### labels_v2_by_strategy.csv

| agent | strategy | n | consequence |
|---|---|---|---|
| planner | swap_other_task | 200 | 0.277 |
| planner | llm_subtle_wrong | 141 | 0.163 |
| planner | resample_disagree | 200 | 0.245 |
| coder | swap_other_task | 200 | 0.082 |
| coder | resample_disagree | 194 | 0.021 |
| tester | swap_other_task | 200 | 0.155 |
| tester | resample_disagree | 200 | 0.03 |
| fixer | swap_other_task | 200 | 0.098 |
| fixer | resample_disagree | 200 | 0.253 |
| verifier | swap_other_task | 195 | 0.487 |
| verifier | resample_disagree | 193 | 0.345 |
| verifier | llm_subtle_wrong | 7 | 0.714 |

## code_c15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_coder | tier_tester | tier_fixer | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+coder+fixer+verifier | coder,fixer,planner,verifier | 0.758 | 17 | 4 | 12.151 | large | large | small | large | large | 0.275 | 0.208 | 0.343 | 1 | 0.8 |
| all_large | all | 0.758 | 20 | 5 | 12.457 | large | large | large | large | large | 0.275 | 0.208 | 0.343 | 1 | 1 |
| planner+coder+fixer | coder,fixer,planner | 0.742 | 14 | 3 | 11.513 | large | large | small | large | small | 0.258 | 0.191 | 0.326 | 0.939 | 0.6 |
| planner+coder+verifier | coder,planner,verifier | 0.742 | 14 | 3 | 12.025 | large | large | small | small | large | 0.258 | 0.191 | 0.326 | 0.939 | 0.6 |
| planner+coder+tester+verifier | coder,planner,tester,verifier | 0.736 | 17 | 4 | 12.216 | large | large | large | small | large | 0.253 | 0.185 | 0.32 | 0.918 | 0.8 |
| planner+coder+tester+fixer | coder,fixer,planner,tester | 0.73 | 17 | 4 | 11.756 | large | large | large | large | small | 0.247 | 0.174 | 0.32 | 0.898 | 0.8 |
| planner+tester+fixer+verifier | fixer,planner,tester,verifier | 0.73 | 17 | 4 | 11.593 | large | small | large | large | large | 0.247 | 0.18 | 0.315 | 0.898 | 0.8 |
| planner+fixer+verifier | fixer,planner,verifier | 0.725 | 14 | 3 | 11.152 | large | small | small | large | large | 0.242 | 0.169 | 0.309 | 0.878 | 0.6 |

8 of 32 rows shown.
