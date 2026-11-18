# Phase X2

Generated 2026-11-18 02:07 UTC, backend `vllm`.

Code run: `c1bb8338fa64acd82d82f1eb0c5a5ce6cb7b019b`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| math_granite/plans | finished |
| math_phi/plans | finished |

## math_granite/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+step_3+aggregator+verifier | aggregator,planner,step_3,verifier | 0.758 | 18 | 4 | 8.902 | large | small | small | large | large | large | 0.235 | 0.193 | 0.275 | 1.03 | 0.667 |
| planner+step_2+step_3+aggregator+verifier | aggregator,planner,step_2,step_3,verifier | 0.757 | 21 | 5 | 9.353 | large | small | large | large | large | large | 0.234 | 0.192 | 0.275 | 1.024 | 0.833 |
| all_large | all | 0.751 | 24 | 6 | 9.451 | large | large | large | large | large | large | 0.228 | 0.189 | 0.27 | 1 | 1 |
| planner+step_1+step_2+aggregator+verifier | aggregator,planner,step_1,step_2,verifier | 0.748 | 21 | 5 | 8.998 | large | large | large | small | large | large | 0.225 | 0.185 | 0.267 | 0.988 | 0.833 |
| planner+step_1+step_2+step_3+verifier | planner,step_1,step_2,step_3,verifier | 0.74 | 21 | 5 | 9.117 | large | large | large | large | small | large | 0.217 | 0.177 | 0.259 | 0.951 | 0.833 |
| planner+step_1+step_3+verifier | planner,step_1,step_3,verifier | 0.736 | 18 | 4 | 8.707 | large | large | small | large | small | large | 0.213 | 0.175 | 0.252 | 0.933 | 0.667 |
| planner+step_1+step_3+aggregator+verifier | aggregator,planner,step_1,step_3,verifier | 0.734 | 21 | 5 | 9.025 | large | large | small | large | large | large | 0.211 | 0.168 | 0.252 | 0.927 | 0.833 |
| planner+step_1+aggregator+verifier | aggregator,planner,step_1,verifier | 0.733 | 18 | 4 | 8.651 | large | large | small | small | large | large | 0.21 | 0.167 | 0.25 | 0.921 | 0.667 |

8 of 64 rows shown.

## math_phi/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| only_verifier | verifier | 0.942 | 9 | 1 | 12.031 | small | small | small | small | small | large | 0.124 | 0.096 | 0.152 | 1.099 | 0.167 |
| planner+step_2+step_3+verifier | planner,step_2,step_3,verifier | 0.939 | 18 | 4 | 16.533 | large | small | large | large | small | large | 0.121 | 0.092 | 0.15 | 1.074 | 0.667 |
| planner+verifier | planner,verifier | 0.937 | 12 | 2 | 13.132 | large | small | small | small | small | large | 0.12 | 0.092 | 0.147 | 1.062 | 0.333 |
| planner+step_3+verifier | planner,step_3,verifier | 0.937 | 15 | 3 | 15.172 | large | small | small | large | small | large | 0.12 | 0.092 | 0.149 | 1.062 | 0.5 |
| planner+step_2+aggregator+verifier | aggregator,planner,step_2,verifier | 0.937 | 18 | 4 | 16.269 | large | small | large | small | large | large | 0.12 | 0.09 | 0.147 | 1.062 | 0.667 |
| planner+step_1+step_2+step_3+verifier | planner,step_1,step_2,step_3,verifier | 0.937 | 21 | 5 | 18.38 | large | large | large | large | small | large | 0.12 | 0.092 | 0.147 | 1.062 | 0.833 |
| planner+step_2+step_3+aggregator+verifier | aggregator,planner,step_2,step_3,verifier | 0.937 | 21 | 5 | 17.796 | large | small | large | large | large | large | 0.12 | 0.09 | 0.147 | 1.062 | 0.833 |
| planner+step_2+verifier | planner,step_2,verifier | 0.936 | 15 | 3 | 14.853 | large | small | large | small | small | large | 0.118 | 0.089 | 0.147 | 1.049 | 0.5 |

8 of 64 rows shown.
