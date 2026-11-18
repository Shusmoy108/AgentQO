# Phase X9

Generated 2026-11-18 16:02 UTC, backend `vllm`.

Code run: `18b3d7a0414a1079fb68ba0f14526e2d0e0417ba`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| math_tiers/plans | finished |

## math_tiers/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner=large+step_2=large+step_3=xl+aggregator=large+verifier=xl | aggregator,planner,step_2,step_3,verifier | 0.9 | 29 | 3 | 12.994 | large | small | large | xl | large | xl | 0.395 | 0.32 | 0.47 | 1.162 | 1.278 |
| planner=large+step_1=large+step_2=large+aggregator=xl+verifier=xl | aggregator,planner,step_1,step_2,verifier | 0.9 | 29 | 3 | 10.674 | large | large | large | small | xl | xl | 0.395 | 0.325 | 0.465 | 1.162 | 1.278 |
| planner=large+step_1=xl+step_3=large+aggregator=large+verifier=xl | aggregator,planner,step_1,step_3,verifier | 0.9 | 29 | 3 | 12.561 | large | xl | small | large | large | xl | 0.395 | 0.325 | 0.465 | 1.162 | 1.278 |
| planner=large+step_2=xl+step_3=large+aggregator=xl+verifier=xl | aggregator,planner,step_2,step_3,verifier | 0.9 | 33 | 2 | 13.378 | large | small | xl | large | xl | xl | 0.395 | 0.325 | 0.465 | 1.162 | 1.5 |
| planner=xl+step_2=xl+step_3=large+aggregator=large+verifier=xl | aggregator,planner,step_2,step_3,verifier | 0.9 | 33 | 2 | 14.08 | xl | small | xl | large | large | xl | 0.395 | 0.325 | 0.47 | 1.162 | 1.5 |
| planner=xl+step_1=xl+step_2=large+aggregator=xl+verifier=xl | aggregator,planner,step_1,step_2,verifier | 0.9 | 37 | 1 | 15.106 | xl | xl | large | small | xl | xl | 0.395 | 0.32 | 0.47 | 1.162 | 1.722 |
| planner=large+step_3=xl+aggregator=large+verifier=xl | aggregator,planner,step_3,verifier | 0.895 | 26 | 2 | 13.155 | large | small | small | xl | large | xl | 0.39 | 0.315 | 0.465 | 1.147 | 1.111 |
| planner=large+step_1=xl+step_3=xl+aggregator=large+verifier=xl | aggregator,planner,step_1,step_3,verifier | 0.895 | 33 | 2 | 14.759 | large | xl | small | xl | large | xl | 0.39 | 0.32 | 0.46 | 1.147 | 1.5 |

8 of 729 rows shown.
