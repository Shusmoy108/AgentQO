# Phase P2

Generated 2026-11-09 03:30 UTC, backend `ollama`.

Code run: `f280f973158a9a388ab40cc32c06789e883cb0c6`; packaged at `f280f973158a9a388ab40cc32c06789e883cb0c6` (dirty).

**Test run on `ollama`: not a reported result.**

| step | status |
|---|---|
| math_q15_7/plans | finished |

## math_q15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|
| step_1+verifier | step_1,verifier | 0.81 | 12 | 2 | 28.658 | 0.44 | 0.365 | 0.51 | 1.06 | 0.333 |
| step_2+step_3+verifier | step_2,step_3,verifier | 0.805 | 15 | 3 | 30.848 | 0.435 | 0.36 | 0.51 | 1.048 | 0.5 |
| step_1+aggregator+verifier | aggregator,step_1,verifier | 0.8 | 15 | 3 | 32.263 | 0.43 | 0.345 | 0.51 | 1.036 | 0.5 |
| planner+step_2+step_3+verifier | planner,step_2,step_3,verifier | 0.8 | 18 | 4 | 32.884 | 0.43 | 0.35 | 0.505 | 1.036 | 0.667 |
| step_1+step_2+step_3+verifier | step_1,step_2,step_3,verifier | 0.8 | 18 | 4 | 33.57 | 0.43 | 0.355 | 0.5 | 1.036 | 0.667 |
| step_2+verifier | step_2,verifier | 0.785 | 12 | 2 | 29.117 | 0.415 | 0.335 | 0.49 | 1 | 0.333 |
| planner+step_1+step_2+aggregator+verifier | aggregator,planner,step_1,step_2,verifier | 0.785 | 21 | 5 | 35.342 | 0.415 | 0.33 | 0.49 | 1 | 0.833 |
| all_large | all | 0.785 | 24 | 6 | 35.838 | 0.415 | 0.33 | 0.49 | 1 | 1 |

8 of 64 rows shown.
