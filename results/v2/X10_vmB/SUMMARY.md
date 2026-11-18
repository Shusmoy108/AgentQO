# Phase X10

Generated 2026-11-18 17:19 UTC, backend `vllm`.

Code run: `18b3d7a0414a1079fb68ba0f14526e2d0e0417ba`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| math_granite/plans | finished |
| math_phi/plans | finished |

## math_granite/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+step_1+aggregator+verifier | aggregator,planner,step_1,verifier | 0.738 | 18 | 4 | 8.975 | large | large | small | small | large | large | 0.255 | 0.195 | 0.312 | 1.03 | 0.667 |
| planner+step_3+aggregator+verifier | aggregator,planner,step_3,verifier | 0.735 | 18 | 4 | 9.205 | large | small | small | large | large | large | 0.253 | 0.193 | 0.312 | 1.02 | 0.667 |
| planner+step_1+step_2+aggregator+verifier | aggregator,planner,step_1,step_2,verifier | 0.735 | 21 | 5 | 9.433 | large | large | large | small | large | large | 0.253 | 0.193 | 0.31 | 1.02 | 0.833 |
| all_large | all | 0.73 | 24 | 6 | 9.72 | large | large | large | large | large | large | 0.247 | 0.188 | 0.307 | 1 | 1 |
| planner+step_3+verifier | planner,step_3,verifier | 0.725 | 15 | 3 | 8.842 | large | small | small | large | small | large | 0.242 | 0.185 | 0.297 | 0.98 | 0.5 |
| planner+step_1+step_3+aggregator+verifier | aggregator,planner,step_1,step_3,verifier | 0.725 | 21 | 5 | 9.359 | large | large | small | large | large | large | 0.242 | 0.185 | 0.3 | 0.98 | 0.833 |
| planner+step_2+step_3+verifier | planner,step_2,step_3,verifier | 0.723 | 18 | 4 | 9.302 | large | small | large | large | small | large | 0.24 | 0.182 | 0.297 | 0.97 | 0.667 |
| planner+step_1+step_2+step_3+verifier | planner,step_1,step_2,step_3,verifier | 0.72 | 21 | 5 | 9.408 | large | large | large | large | small | large | 0.237 | 0.175 | 0.297 | 0.96 | 0.833 |

8 of 64 rows shown.

## math_phi/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| step_1+step_3+aggregator+verifier | aggregator,step_1,step_3,verifier | 0.965 | 18 | 4 | 19.398 | small | large | small | large | large | large | 0.172 | 0.135 | 0.212 | 1.113 | 0.667 |
| planner+step_1+step_2+verifier | planner,step_1,step_2,verifier | 0.96 | 18 | 4 | 17.166 | large | large | large | small | small | large | 0.168 | 0.13 | 0.207 | 1.081 | 0.667 |
| step_2+verifier | step_2,verifier | 0.958 | 12 | 2 | 14.156 | small | small | large | small | small | large | 0.165 | 0.125 | 0.205 | 1.065 | 0.333 |
| planner+step_3+verifier | planner,step_3,verifier | 0.958 | 15 | 3 | 15.5 | large | small | small | large | small | large | 0.165 | 0.125 | 0.205 | 1.065 | 0.5 |
| planner+step_2+step_3+verifier | planner,step_2,step_3,verifier | 0.958 | 18 | 4 | 16.708 | large | small | large | large | small | large | 0.165 | 0.125 | 0.205 | 1.065 | 0.667 |
| step_1+step_2+step_3+aggregator+verifier | aggregator,step_1,step_2,step_3,verifier | 0.958 | 21 | 5 | 20.043 | small | large | large | large | large | large | 0.165 | 0.128 | 0.205 | 1.065 | 0.833 |
| step_1+verifier | step_1,verifier | 0.955 | 12 | 2 | 15.499 | small | large | small | small | small | large | 0.163 | 0.122 | 0.203 | 1.048 | 0.333 |
| step_1+step_2+verifier | step_1,step_2,verifier | 0.955 | 15 | 3 | 16.15 | small | large | large | small | small | large | 0.163 | 0.122 | 0.203 | 1.048 | 0.5 |

8 of 64 rows shown.
