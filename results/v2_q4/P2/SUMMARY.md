# Phase P2

Generated 2026-11-09 19:56 UTC, backend `ollama`.

Code run: `8bedf6e27e70a8f554d7e478792fd1ad0169ff3f`, `f280f973158a9a388ab40cc32c06789e883cb0c6`; packaged at `8bedf6e27e70a8f554d7e478792fd1ad0169ff3f` (dirty).

**Resumed at more than one commit; see `provenance.jsonl`.**

**Test run on `ollama`: not a reported result.**

| step | status |
|---|---|
| hotpot_q15_7/plans | finished |
| math_q15_7/plans | finished |

## hotpot_q15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | f1 | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hop_1+aggregator+verifier | aggregator,hop_1,verifier | 0.56 | 14 | 3 | 41.87 | 0.687 | 0.285 | 0.205 | 0.36 | 1.018 | 0.6 |
| all_large | all | 0.555 | 20 | 5 | 54.078 | 0.681 | 0.28 | 0.2 | 0.355 | 1 | 1 |
| hop_1+hop_2+aggregator+verifier | aggregator,hop_1,hop_2,verifier | 0.55 | 17 | 4 | 45.76 | 0.679 | 0.275 | 0.2 | 0.35 | 0.982 | 0.8 |
| planner+hop_1+hop_2+aggregator | aggregator,hop_1,hop_2,planner | 0.535 | 17 | 4 | 47.537 | 0.668 | 0.26 | 0.18 | 0.335 | 0.929 | 0.8 |
| planner+hop_1+aggregator+verifier | aggregator,hop_1,planner,verifier | 0.535 | 17 | 4 | 49.62 | 0.67 | 0.26 | 0.185 | 0.335 | 0.929 | 0.8 |
| planner+hop_1+hop_2+verifier | hop_1,hop_2,planner,verifier | 0.53 | 17 | 4 | 52.596 | 0.667 | 0.255 | 0.18 | 0.33 | 0.911 | 0.8 |
| planner+aggregator+verifier | aggregator,planner,verifier | 0.525 | 14 | 3 | 40.215 | 0.657 | 0.25 | 0.175 | 0.325 | 0.893 | 0.6 |
| planner+hop_2+aggregator+verifier | aggregator,hop_2,planner,verifier | 0.525 | 17 | 4 | 41.049 | 0.666 | 0.25 | 0.175 | 0.33 | 0.893 | 0.8 |

8 of 32 rows shown.

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
