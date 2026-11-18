# Phase X10r

Generated 2026-11-18 19:04 UTC, backend `vllm`.

Code run: `18b3d7a0414a1079fb68ba0f14526e2d0e0417ba`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| math_granite/plans | finished |
| math_phi/plans | finished |

## math_granite/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+step_2+step_3+verifier | planner,step_2,step_3,verifier | 0.74 | 18 | 4 | 9.307 | large | small | large | large | small | large | 0.268 | 0.212 | 0.323 | 1.081 | 0.667 |
| planner+step_3+verifier | planner,step_3,verifier | 0.73 | 15 | 3 | 8.827 | large | small | small | large | small | large | 0.258 | 0.205 | 0.312 | 1.04 | 0.5 |
| planner+step_1+step_2+aggregator+verifier | aggregator,planner,step_1,step_2,verifier | 0.728 | 21 | 5 | 9.22 | large | large | large | small | large | large | 0.255 | 0.2 | 0.312 | 1.03 | 0.833 |
| planner+step_1+verifier | planner,step_1,verifier | 0.725 | 15 | 3 | 8.492 | large | large | small | small | small | large | 0.253 | 0.195 | 0.31 | 1.02 | 0.5 |
| planner+step_1+step_2+step_3+verifier | planner,step_1,step_2,step_3,verifier | 0.723 | 21 | 5 | 9.339 | large | large | large | large | small | large | 0.25 | 0.195 | 0.31 | 1.01 | 0.833 |
| planner+step_1+step_3+aggregator+verifier | aggregator,planner,step_1,step_3,verifier | 0.723 | 21 | 5 | 9.397 | large | large | small | large | large | large | 0.25 | 0.195 | 0.31 | 1.01 | 0.833 |
| planner+step_1+aggregator+verifier | aggregator,planner,step_1,verifier | 0.72 | 18 | 4 | 8.819 | large | large | small | small | large | large | 0.247 | 0.193 | 0.305 | 1 | 0.667 |
| all_large | all | 0.72 | 24 | 6 | 9.601 | large | large | large | large | large | large | 0.247 | 0.19 | 0.307 | 1 | 1 |

8 of 64 rows shown.

## math_phi/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+step_1+step_3+verifier | planner,step_1,step_3,verifier | 0.958 | 18 | 4 | 18.064 | large | large | small | large | small | large | 0.242 | 0.198 | 0.287 | 1.043 | 0.667 |
| planner+step_3+verifier | planner,step_3,verifier | 0.955 | 15 | 3 | 15.883 | large | small | small | large | small | large | 0.24 | 0.195 | 0.285 | 1.032 | 0.5 |
| planner+step_3+aggregator+verifier | aggregator,planner,step_3,verifier | 0.955 | 18 | 4 | 17.171 | large | small | small | large | large | large | 0.24 | 0.198 | 0.285 | 1.032 | 0.667 |
| step_1+step_2+step_3+verifier | step_1,step_2,step_3,verifier | 0.955 | 18 | 4 | 17.868 | small | large | large | large | small | large | 0.24 | 0.197 | 0.285 | 1.032 | 0.667 |
| planner+step_1+step_2+step_3+verifier | planner,step_1,step_2,step_3,verifier | 0.955 | 21 | 5 | 18.641 | large | large | large | large | small | large | 0.24 | 0.195 | 0.285 | 1.032 | 0.833 |
| planner+step_1+step_2+aggregator+verifier | aggregator,planner,step_1,step_2,verifier | 0.955 | 21 | 5 | 18.594 | large | large | large | small | large | large | 0.24 | 0.198 | 0.285 | 1.032 | 0.833 |
| planner+step_2+step_3+aggregator+verifier | aggregator,planner,step_2,step_3,verifier | 0.955 | 21 | 5 | 18.439 | large | small | large | large | large | large | 0.24 | 0.198 | 0.285 | 1.032 | 0.833 |
| step_1+step_2+step_3+aggregator+verifier | aggregator,step_1,step_2,step_3,verifier | 0.955 | 21 | 5 | 20.489 | small | large | large | large | large | large | 0.24 | 0.198 | 0.285 | 1.032 | 0.833 |

8 of 64 rows shown.
