# Phase X2

Generated 2026-11-18 00:45 UTC, backend `vllm`.

Code run: `c1bb8338fa64acd82d82f1eb0c5a5ce6cb7b019b`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| hotpot_iso_q15_7/plans | finished |
| hotpot_q15_7/plans | finished |
| math_q15_7/plans | finished |

## hotpot_iso_q15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | f1 | tier_planner | tier_hop_1 | tier_hop_2 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_large | all | 0.522 | 20 | 5 | 3.458 | 0.676 | large | large | large | large | large | 0.232 | 0.187 | 0.275 | 1 | 1 |
| hop_1+hop_2+aggregator+verifier | aggregator,hop_1,hop_2,verifier | 0.518 | 17 | 4 | 2.843 | 0.649 | small | large | large | large | large | 0.228 | 0.187 | 0.272 | 0.986 | 0.8 |
| planner+hop_2+aggregator+verifier | aggregator,hop_2,planner,verifier | 0.493 | 17 | 4 | 2.901 | 0.636 | large | small | large | large | large | 0.203 | 0.162 | 0.245 | 0.878 | 0.8 |
| hop_2+aggregator+verifier | aggregator,hop_2,verifier | 0.478 | 14 | 3 | 2.31 | 0.596 | small | small | large | large | large | 0.188 | 0.153 | 0.223 | 0.813 | 0.6 |
| planner+hop_1+hop_2+verifier | hop_1,hop_2,planner,verifier | 0.455 | 17 | 4 | 3.317 | 0.613 | large | large | large | small | large | 0.165 | 0.12 | 0.208 | 0.712 | 0.8 |
| planner+hop_1+aggregator+verifier | aggregator,hop_1,planner,verifier | 0.45 | 17 | 4 | 3.227 | 0.593 | large | large | small | large | large | 0.16 | 0.117 | 0.205 | 0.691 | 0.8 |
| hop_1+aggregator+verifier | aggregator,hop_1,verifier | 0.445 | 14 | 3 | 2.595 | 0.589 | small | large | small | large | large | 0.155 | 0.113 | 0.198 | 0.669 | 0.6 |
| hop_1+hop_2+verifier | hop_1,hop_2,verifier | 0.433 | 14 | 3 | 2.701 | 0.588 | small | large | large | small | large | 0.143 | 0.102 | 0.187 | 0.619 | 0.6 |

8 of 32 rows shown.

## hotpot_q15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | f1 | tier_planner | tier_hop_1 | tier_hop_2 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hop_1+hop_2+aggregator+verifier | aggregator,hop_1,hop_2,verifier | 0.532 | 17 | 4 | 3.475 | 0.674 | small | large | large | large | large | 0.192 | 0.15 | 0.233 | 1.15 | 0.8 |
| hop_1+aggregator+verifier | aggregator,hop_1,verifier | 0.52 | 14 | 3 | 3.26 | 0.665 | small | large | small | large | large | 0.18 | 0.14 | 0.222 | 1.08 | 0.6 |
| planner+hop_1+aggregator+verifier | aggregator,hop_1,planner,verifier | 0.517 | 17 | 4 | 3.803 | 0.652 | large | large | small | large | large | 0.177 | 0.135 | 0.218 | 1.06 | 0.8 |
| hop_2+aggregator+verifier | aggregator,hop_2,verifier | 0.512 | 14 | 3 | 2.914 | 0.648 | small | small | large | large | large | 0.172 | 0.132 | 0.21 | 1.03 | 0.6 |
| planner+aggregator+verifier | aggregator,planner,verifier | 0.507 | 14 | 3 | 3.215 | 0.649 | large | small | small | large | large | 0.167 | 0.127 | 0.207 | 1 | 0.6 |
| planner+hop_2+aggregator+verifier | aggregator,hop_2,planner,verifier | 0.507 | 17 | 4 | 3.521 | 0.646 | large | small | large | large | large | 0.167 | 0.127 | 0.208 | 1 | 0.8 |
| all_large | all | 0.507 | 20 | 5 | 4.047 | 0.651 | large | large | large | large | large | 0.167 | 0.125 | 0.21 | 1 | 1 |
| aggregator+verifier | aggregator,verifier | 0.495 | 11 | 2 | 2.651 | 0.63 | small | small | small | large | large | 0.155 | 0.117 | 0.193 | 0.93 | 0.4 |

8 of 32 rows shown.

## math_q15_7/plans

### h3_plans.csv

| plan | upgraded | accuracy | cost_units | large_calls | latency_s | tier_planner | tier_step_1 | tier_step_2 | tier_step_3 | tier_aggregator | tier_verifier | gain_vs_small | gain_ci_low | gain_ci_high | share_of_full_gain | share_of_full_extra_cost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| step_1+aggregator+verifier | aggregator,step_1,verifier | 0.843 | 15 | 3 | 5.209 | small | large | small | small | large | large | 0.339 | 0.3 | 0.377 | 1.056 | 0.5 |
| step_1+step_2+step_3+aggregator+verifier | aggregator,step_1,step_2,step_3,verifier | 0.84 | 21 | 5 | 4.989 | small | large | large | large | large | large | 0.337 | 0.298 | 0.376 | 1.048 | 0.833 |
| step_2+aggregator+verifier | aggregator,step_2,verifier | 0.836 | 15 | 3 | 5.514 | small | small | large | small | large | large | 0.332 | 0.293 | 0.37 | 1.035 | 0.5 |
| step_1+step_2+aggregator+verifier | aggregator,step_1,step_2,verifier | 0.836 | 18 | 4 | 4.999 | small | large | large | small | large | large | 0.332 | 0.293 | 0.37 | 1.035 | 0.667 |
| planner+step_3+aggregator+verifier | aggregator,planner,step_3,verifier | 0.834 | 18 | 4 | 5.797 | large | small | small | large | large | large | 0.331 | 0.292 | 0.371 | 1.03 | 0.667 |
| step_1+step_3+aggregator+verifier | aggregator,step_1,step_3,verifier | 0.834 | 18 | 4 | 5.188 | small | large | small | large | large | large | 0.331 | 0.291 | 0.37 | 1.03 | 0.667 |
| step_3+aggregator+verifier | aggregator,step_3,verifier | 0.833 | 15 | 3 | 5.675 | small | small | small | large | large | large | 0.33 | 0.291 | 0.369 | 1.026 | 0.5 |
| planner+aggregator+verifier | aggregator,planner,verifier | 0.83 | 15 | 3 | 5.837 | large | small | small | small | large | large | 0.327 | 0.287 | 0.366 | 1.017 | 0.5 |

8 of 64 rows shown.
