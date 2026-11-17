# Phase X4

Generated 2026-11-17 03:42 UTC, backend `vllm`.

Code run: `c1bb8338fa64acd82d82f1eb0c5a5ce6cb7b019b`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| math_q15_7/plans | finished |

## math_q15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+step_1+step_2+step_3+verifier | planner,step_1,step_2,step_3,verifier | 0.828 | 21 | 5 | 5.18 | large | large | large | large | small | large | 0.345 | 0.292 | 0.398 | 1.07 | 0.833 |
| step_2+verifier | step_2,verifier | 0.825 | 12 | 2 | 5.332 | small | small | large | small | small | large | 0.343 | 0.292 | 0.393 | 1.062 | 0.333 |
| planner+step_2+step_3+verifier | planner,step_2,step_3,verifier | 0.823 | 18 | 4 | 5.408 | large | small | large | large | small | large | 0.34 | 0.287 | 0.393 | 1.054 | 0.667 |
| step_1+step_3+aggregator+verifier | aggregator,step_1,step_3,verifier | 0.82 | 18 | 4 | 5.375 | small | large | small | large | large | large | 0.338 | 0.285 | 0.39 | 1.047 | 0.667 |
| planner+step_2+step_3+aggregator+verifier | aggregator,planner,step_2,step_3,verifier | 0.818 | 21 | 5 | 5.866 | large | small | large | large | large | large | 0.335 | 0.282 | 0.39 | 1.039 | 0.833 |
| step_1+aggregator+verifier | aggregator,step_1,verifier | 0.812 | 15 | 3 | 5.345 | small | large | small | small | large | large | 0.33 | 0.278 | 0.383 | 1.023 | 0.5 |
| step_2+aggregator+verifier | aggregator,step_2,verifier | 0.812 | 15 | 3 | 5.82 | small | small | large | small | large | large | 0.33 | 0.28 | 0.383 | 1.023 | 0.5 |
| planner+step_1+step_3+aggregator+verifier | aggregator,planner,step_1,step_3,verifier | 0.812 | 21 | 5 | 5.58 | large | large | small | large | large | large | 0.33 | 0.278 | 0.383 | 1.023 | 0.833 |

8 of 64 rows shown.
