# Phase X8

Generated 2026-11-18 07:34 UTC, backend `vllm`.

Code run: `c1bb8338fa64acd82d82f1eb0c5a5ce6cb7b019b`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| complex_q15_7/plans | finished |

## complex_q15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_researcher_1 | tier_researcher_2 | tier_step_1_1 | tier_step_1_2 | tier_step_2_1 | tier_step_2_2 | tier_aggregator | tier_verifier | tier_formatter | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| step_1_1+step_2_1+step_2_2+aggregator+verifier | aggregator,step_1_1,step_2_1,step_2_2,verifier | 0.885 | 25 | 5 | 8.645 | small | small | small | large | small | large | large | large | large | small | 0.375 | 0.305 | 0.445 | 1.364 | 0.5 |
| planner+researcher_1+verifier | planner,researcher_1,verifier | 0.88 | 19 | 3 | 7.888 | large | large | small | small | small | small | small | small | large | small | 0.37 | 0.3 | 0.44 | 1.345 | 0.3 |
| planner+aggregator+verifier | aggregator,planner,verifier | 0.88 | 19 | 3 | 9.925 | large | small | small | small | small | small | small | large | large | small | 0.37 | 0.3 | 0.44 | 1.345 | 0.3 |
| researcher_1+step_1_1+step_2_1+verifier | researcher_1,step_1_1,step_2_1,verifier | 0.875 | 22 | 4 | 6.937 | small | large | small | large | small | large | small | small | large | small | 0.365 | 0.295 | 0.435 | 1.327 | 0.4 |
| planner+researcher_2+step_2_2+aggregator+verifier | aggregator,planner,researcher_2,step_2_2,verifier | 0.875 | 25 | 5 | 8.135 | large | small | large | small | small | small | large | large | large | small | 0.365 | 0.29 | 0.44 | 1.327 | 0.5 |
| researcher_1+step_1_1+step_1_2+step_2_1+verifier | researcher_1,step_1_1,step_1_2,step_2_1,verifier | 0.875 | 25 | 5 | 7.023 | small | large | small | large | large | large | small | small | large | small | 0.365 | 0.295 | 0.435 | 1.327 | 0.5 |
| researcher_2+step_1_1+step_2_1+verifier | researcher_2,step_1_1,step_2_1,verifier | 0.87 | 22 | 4 | 6.85 | small | small | large | large | small | large | small | small | large | small | 0.36 | 0.29 | 0.43 | 1.309 | 0.4 |
| planner+researcher_1+researcher_2+step_1_1+step_1_2+verifier | planner,researcher_1,researcher_2,step_1_1,step_1_2,verifier | 0.87 | 28 | 6 | 6.059 | large | large | large | large | large | small | small | small | large | small | 0.36 | 0.285 | 0.43 | 1.309 | 0.6 |

8 of 1024 rows shown.
