# Phase X11

Generated 2026-11-18 14:52 UTC, backend `vllm`.

Code run: `18b3d7a0414a1079fb68ba0f14526e2d0e0417ba`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| math500_q15_7/plans | finished |

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
