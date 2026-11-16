# Phase P2

Generated 2026-11-16 13:48 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| hotpot_iso_q15_7/plans | finished |
| hotpot_q15_7/plans | finished |
| math_q15_7/plans | finished |

## hotpot_iso_q15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | f1 | tier_planner | tier_hop_1 | tier_hop_2 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_large | all | 0.527 | 20 | 5 | 3.429 | 0.696 | large | large | large | large | large | 0.235 | 0.18 | 0.29 | 1 | 1 |
| hop_1+hop_2+aggregator+verifier | aggregator,hop_1,hop_2,verifier | 0.485 | 17 | 4 | 2.808 | 0.648 | small | large | large | large | large | 0.193 | 0.14 | 0.245 | 0.819 | 0.8 |
| planner+hop_2+aggregator+verifier | aggregator,hop_2,planner,verifier | 0.48 | 17 | 4 | 2.977 | 0.651 | large | small | large | large | large | 0.188 | 0.138 | 0.237 | 0.798 | 0.8 |
| planner+hop_1+hop_2+verifier | hop_1,hop_2,planner,verifier | 0.453 | 17 | 4 | 3.298 | 0.639 | large | large | large | small | large | 0.16 | 0.107 | 0.215 | 0.681 | 0.8 |
| planner+hop_1+aggregator+verifier | aggregator,hop_1,planner,verifier | 0.448 | 17 | 4 | 3.249 | 0.601 | large | large | small | large | large | 0.155 | 0.102 | 0.207 | 0.66 | 0.8 |
| hop_2+aggregator+verifier | aggregator,hop_2,verifier | 0.445 | 14 | 3 | 2.31 | 0.594 | small | small | large | large | large | 0.152 | 0.107 | 0.198 | 0.649 | 0.6 |
| hop_1+aggregator+verifier | aggregator,hop_1,verifier | 0.44 | 14 | 3 | 2.591 | 0.601 | small | large | small | large | large | 0.147 | 0.098 | 0.198 | 0.628 | 0.6 |
| hop_1+hop_2+verifier | hop_1,hop_2,verifier | 0.438 | 14 | 3 | 2.677 | 0.609 | small | large | large | small | large | 0.145 | 0.095 | 0.195 | 0.617 | 0.6 |

8 of 32 rows shown.

## hotpot_q15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | f1 | tier_planner | tier_hop_1 | tier_hop_2 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+hop_1+aggregator+verifier | aggregator,hop_1,planner,verifier | 0.505 | 17 | 4 | 3.888 | 0.669 | large | large | small | large | large | 0.193 | 0.138 | 0.242 | 1.085 | 0.8 |
| aggregator+verifier | aggregator,verifier | 0.49 | 11 | 2 | 2.72 | 0.644 | small | small | small | large | large | 0.177 | 0.13 | 0.225 | 1 | 0.4 |
| all_large | all | 0.49 | 20 | 5 | 4.072 | 0.666 | large | large | large | large | large | 0.177 | 0.122 | 0.23 | 1 | 1 |
| hop_1+aggregator+verifier | aggregator,hop_1,verifier | 0.487 | 14 | 3 | 3.287 | 0.662 | small | large | small | large | large | 0.175 | 0.12 | 0.228 | 0.986 | 0.6 |
| planner+hop_2+aggregator+verifier | aggregator,hop_2,planner,verifier | 0.48 | 17 | 4 | 3.662 | 0.658 | large | small | large | large | large | 0.168 | 0.115 | 0.22 | 0.944 | 0.8 |
| hop_1+hop_2+aggregator+verifier | aggregator,hop_1,hop_2,verifier | 0.48 | 17 | 4 | 3.46 | 0.658 | small | large | large | large | large | 0.168 | 0.113 | 0.223 | 0.944 | 0.8 |
| hop_2+aggregator+verifier | aggregator,hop_2,verifier | 0.475 | 14 | 3 | 2.926 | 0.637 | small | small | large | large | large | 0.163 | 0.113 | 0.212 | 0.915 | 0.6 |
| planner+aggregator+verifier | aggregator,planner,verifier | 0.472 | 14 | 3 | 3.312 | 0.652 | large | small | small | large | large | 0.16 | 0.107 | 0.212 | 0.901 | 0.6 |

8 of 32 rows shown.

## math_q15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planner+step_1+step_3+aggregator+verifier | aggregator,planner,step_1,step_3,verifier | 0.83 | 21 | 5 | 5.678 | large | large | small | large | large | large | 0.34 | 0.287 | 0.393 | 1.03 | 0.833 |
| step_2+verifier | step_2,verifier | 0.823 | 12 | 2 | 5.34 | small | small | large | small | small | large | 0.333 | 0.28 | 0.385 | 1.008 | 0.333 |
| step_2+aggregator+verifier | aggregator,step_2,verifier | 0.823 | 15 | 3 | 5.73 | small | small | large | small | large | large | 0.333 | 0.282 | 0.385 | 1.008 | 0.5 |
| all_large | all | 0.82 | 24 | 6 | 5.599 | large | large | large | large | large | large | 0.33 | 0.278 | 0.383 | 1 | 1 |
| planner+step_2+step_3+aggregator+verifier | aggregator,planner,step_2,step_3,verifier | 0.815 | 21 | 5 | 5.963 | large | small | large | large | large | large | 0.325 | 0.273 | 0.38 | 0.985 | 0.833 |
| planner+step_1+aggregator+verifier | aggregator,planner,step_1,verifier | 0.81 | 18 | 4 | 5.653 | large | large | small | small | large | large | 0.32 | 0.265 | 0.375 | 0.97 | 0.667 |
| planner+step_3+aggregator+verifier | aggregator,planner,step_3,verifier | 0.807 | 18 | 4 | 6.06 | large | small | small | large | large | large | 0.318 | 0.263 | 0.372 | 0.962 | 0.667 |
| planner+step_1+step_2+step_3+verifier | planner,step_1,step_2,step_3,verifier | 0.807 | 21 | 5 | 5.215 | large | large | large | large | small | large | 0.318 | 0.265 | 0.37 | 0.962 | 0.833 |

8 of 64 rows shown.
