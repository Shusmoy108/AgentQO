# Phase X11

Generated 2026-11-18 15:10 UTC, backend `vllm`.

Code run: `18b3d7a0414a1079fb68ba0f14526e2d0e0417ba`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| code_c15_7/plans | finished |
| math500_q15_7/plans | finished |

## code_c15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_coder | tier_tester | tier_fixer | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_large | all | 0.705 | 20 | 5 | 7.751 | large | large | large | large | large | 0.29 | 0.22 | 0.36 | 1 | 1 |
| planner+coder+tester+verifier | coder,planner,tester,verifier | 0.695 | 17 | 4 | 7.389 | large | large | large | small | large | 0.28 | 0.205 | 0.355 | 0.966 | 0.8 |
| planner+coder+verifier | coder,planner,verifier | 0.685 | 14 | 3 | 6.753 | large | large | small | small | large | 0.27 | 0.195 | 0.345 | 0.931 | 0.6 |
| planner+coder+fixer+verifier | coder,fixer,planner,verifier | 0.68 | 17 | 4 | 7.084 | large | large | small | large | large | 0.265 | 0.19 | 0.34 | 0.914 | 0.8 |
| planner+tester+fixer+verifier | fixer,planner,tester,verifier | 0.675 | 17 | 4 | 7.135 | large | small | large | large | large | 0.26 | 0.19 | 0.33 | 0.897 | 0.8 |
| planner+tester+verifier | planner,tester,verifier | 0.67 | 14 | 3 | 6.732 | large | small | large | small | large | 0.255 | 0.185 | 0.325 | 0.879 | 0.6 |
| planner+verifier | planner,verifier | 0.665 | 11 | 2 | 6.169 | large | small | small | small | large | 0.25 | 0.18 | 0.32 | 0.862 | 0.4 |
| planner+coder+tester+fixer | coder,fixer,planner,tester | 0.665 | 17 | 4 | 7.119 | large | large | large | large | small | 0.25 | 0.175 | 0.325 | 0.862 | 0.8 |

8 of 32 rows shown.

## math500_q15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_large | all | 0.74 | 24 | 6 | 8.471 | large | large | large | large | large | large | 0.365 | 0.3 | 0.43 | 1 | 1 |
| planner+step_3+verifier | planner,step_3,verifier | 0.695 | 15 | 3 | 13.33 | large | small | small | large | small | large | 0.32 | 0.25 | 0.39 | 0.877 | 0.5 |
| planner+aggregator+verifier | aggregator,planner,verifier | 0.695 | 15 | 3 | 14.174 | large | small | small | small | large | large | 0.32 | 0.25 | 0.39 | 0.877 | 0.5 |
| planner+step_1+step_2+aggregator+verifier | aggregator,planner,step_1,step_2,verifier | 0.69 | 21 | 5 | 10.306 | large | large | large | small | large | large | 0.315 | 0.25 | 0.38 | 0.863 | 0.833 |
| step_1+step_3+aggregator+verifier | aggregator,step_1,step_3,verifier | 0.685 | 18 | 4 | 12.219 | small | large | small | large | large | large | 0.31 | 0.24 | 0.38 | 0.849 | 0.667 |
| step_2+step_3+aggregator+verifier | aggregator,step_2,step_3,verifier | 0.685 | 18 | 4 | 11.283 | small | small | large | large | large | large | 0.31 | 0.245 | 0.375 | 0.849 | 0.667 |
| planner+step_2+step_3+aggregator+verifier | aggregator,planner,step_2,step_3,verifier | 0.685 | 21 | 5 | 13.732 | large | small | large | large | large | large | 0.31 | 0.245 | 0.38 | 0.849 | 0.833 |
| step_1+aggregator+verifier | aggregator,step_1,verifier | 0.68 | 15 | 3 | 12.434 | small | large | small | small | large | large | 0.305 | 0.235 | 0.375 | 0.836 | 0.5 |

8 of 64 rows shown.
