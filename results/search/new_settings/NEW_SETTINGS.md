## New settings (landed after the registered run; not part of the S1-S4 verdicts)

Same 14 methods, 5 budgets, 30 seeds and metrics as the registered run. 2 objectives only (no latency truth).

### code_c15_7 (32 plans)

Mean HV ratio over 30 seeds; B = 4/4/4/4/6 (1/2/5/10/20%; equal B values repeat one
experiment, so a W or L there counts more than once).

| method | 1% | 2% | 5% | 10% | 20% |
|---|---|---|---|---|---|
| nsga2_pairwise_m3 | 0.946 | 0.946 | 0.946 | 0.946 | 0.965 |
| nsga2_pairwise_m5 | 0.946 | 0.946 | 0.946 | 0.946 | 0.965 |
| nsga2_indep_add | 0.903 | 0.903 | 0.903 | 0.903 | 0.962 |
| nsga2_indep_mult | 0.903 | 0.903 | 0.903 | 0.903 | 0.962 |
| nsga2_logit_add | 0.903 | 0.903 | 0.903 | 0.903 | 0.962 |
| mopso_pairwise_m3 | 0.946 | 0.946 | 0.946 | 0.946 | 0.965 |
| gde3_pairwise_m3 | 0.946 | 0.946 | 0.946 | 0.946 | 0.965 |
| nsga2_active_m3 | 0.974 | 0.974 | 0.974 | 0.974 | 0.974 |
| abacus | 0.903 | 0.903 | 0.903 | 0.903 | 0.962 |
| random | 0.754 | 0.754 | 0.754 | 0.754 | 0.815 |
| greedy_uv | 0.978 | 0.978 | 0.978 | 0.978 | 0.979 |

S2 comparisons (nsga2_pairwise_m3 minus comparator, paired per budget, tau = 0.0134):

| comparator | W | T | L | per budget |
|---|---|---|---|---|
| (a) nsga2_indep_add | 4 | 1 | 0 | W(+0.042) W(+0.042) W(+0.042) W(+0.042) T(+0.003) |
| (b) abacus | 4 | 1 | 0 | W(+0.042) W(+0.042) W(+0.042) W(+0.042) T(+0.003) |
| (c) random | 5 | 0 | 0 | W(+0.192) W(+0.192) W(+0.192) W(+0.192) W(+0.150) |
| (d) greedy_uv | 0 | 0 | 5 | L(-0.032) L(-0.032) L(-0.032) L(-0.032) L(-0.014) |

S3 quantities: independence MAE 0.0314, gap (pairwise m3 minus indep) +0.0345.

### math500_q15_7 (64 plans)

Mean HV ratio over 30 seeds; B = 4/4/4/6/13 (1/2/5/10/20%; equal B values repeat one
experiment, so a W or L there counts more than once).

| method | 1% | 2% | 5% | 10% | 20% |
|---|---|---|---|---|---|
| nsga2_pairwise_m3 | 0.900 | 0.900 | 0.900 | 0.960 | 0.997 |
| nsga2_pairwise_m5 | 0.900 | 0.900 | 0.900 | 0.960 | 0.989 |
| nsga2_indep_add | 0.898 | 0.898 | 0.898 | 0.990 | 0.997 |
| nsga2_indep_mult | 0.924 | 0.924 | 0.924 | 0.976 | 0.997 |
| nsga2_logit_add | 0.898 | 0.898 | 0.898 | 0.990 | 0.997 |
| mopso_pairwise_m3 | 0.900 | 0.900 | 0.900 | 0.960 | 0.997 |
| gde3_pairwise_m3 | 0.900 | 0.900 | 0.900 | 0.960 | 0.997 |
| nsga2_active_m3 | 0.900 | 0.900 | 0.900 | 0.934 | 0.968 |
| abacus | 0.898 | 0.898 | 0.898 | 0.990 | 0.997 |
| random | 0.674 | 0.674 | 0.674 | 0.709 | 0.850 |
| greedy_uv | 0.945 | 0.945 | 0.945 | 0.953 | 0.953 |
| rule_structural | 0.728 | 0.728 | 0.728 | 0.801 | 0.801 |
| rule_output | 0.875 | 0.875 | 0.875 | 0.945 | 0.945 |
| rule_confident_uv | 0.884 | 0.884 | 0.884 | 0.953 | 0.953 |

S2 comparisons (nsga2_pairwise_m3 minus comparator, paired per budget, tau = 0.0134):

| comparator | W | T | L | per budget |
|---|---|---|---|---|
| (a) nsga2_indep_add | 0 | 4 | 1 | T(+0.001) T(+0.001) T(+0.001) L(-0.031) T(+0.000) |
| (b) abacus | 0 | 4 | 1 | T(+0.001) T(+0.001) T(+0.001) L(-0.031) T(+0.000) |
| (c) random | 5 | 0 | 0 | W(+0.226) W(+0.226) W(+0.226) W(+0.250) W(+0.147) |
| (d) greedy_uv | 1 | 1 | 3 | L(-0.045) L(-0.045) L(-0.045) T(+0.007) W(+0.044) |
| (e) rule_structural | 5 | 0 | 0 | W(+0.171) W(+0.171) W(+0.171) W(+0.159) W(+0.197) |
| (e) rule_output | 5 | 0 | 0 | W(+0.024) W(+0.024) W(+0.024) W(+0.015) W(+0.053) |
| (e) rule_confident_uv | 4 | 1 | 0 | W(+0.016) W(+0.016) W(+0.016) T(+0.007) W(+0.044) |

S3 quantities: independence MAE 0.0773, gap (pairwise m3 minus indep) -0.0053.

### math_q7_32 (64 plans)

Mean HV ratio over 30 seeds; B = 4/4/4/6/13 (1/2/5/10/20%; equal B values repeat one
experiment, so a W or L there counts more than once).

| method | 1% | 2% | 5% | 10% | 20% |
|---|---|---|---|---|---|
| nsga2_pairwise_m3 | 0.985 | 0.985 | 0.985 | 0.990 | 0.995 |
| nsga2_pairwise_m5 | 0.985 | 0.985 | 0.985 | 0.990 | 0.995 |
| nsga2_indep_add | 0.985 | 0.985 | 0.985 | 0.995 | 0.999 |
| nsga2_indep_mult | 0.985 | 0.985 | 0.985 | 0.995 | 0.999 |
| nsga2_logit_add | 0.985 | 0.985 | 0.985 | 0.995 | 0.999 |
| mopso_pairwise_m3 | 0.985 | 0.985 | 0.985 | 0.990 | 0.995 |
| gde3_pairwise_m3 | 0.985 | 0.985 | 0.985 | 0.990 | 0.995 |
| nsga2_active_m3 | 0.963 | 0.963 | 0.963 | 0.974 | 0.990 |
| abacus | 0.985 | 0.985 | 0.985 | 0.995 | 0.999 |
| random | 0.683 | 0.683 | 0.683 | 0.723 | 0.874 |
| greedy_uv | 0.986 | 0.986 | 0.986 | 0.988 | 0.988 |
| rule_structural | 0.925 | 0.925 | 0.925 | 0.925 | 0.929 |
| rule_output | 0.982 | 0.982 | 0.982 | 0.995 | 0.999 |
| rule_confident_uv | 0.965 | 0.965 | 0.965 | 0.987 | 0.987 |

S2 comparisons (nsga2_pairwise_m3 minus comparator, paired per budget, tau = 0.0134):

| comparator | W | T | L | per budget |
|---|---|---|---|---|
| (a) nsga2_indep_add | 0 | 5 | 0 | T(+0.000) T(+0.000) T(+0.000) T(-0.006) T(-0.003) |
| (b) abacus | 0 | 5 | 0 | T(+0.000) T(+0.000) T(+0.000) T(-0.006) T(-0.003) |
| (c) random | 5 | 0 | 0 | W(+0.301) W(+0.301) W(+0.301) W(+0.266) W(+0.122) |
| (d) greedy_uv | 0 | 5 | 0 | T(-0.001) T(-0.001) T(-0.001) T(+0.001) T(+0.007) |
| (e) rule_structural | 5 | 0 | 0 | W(+0.060) W(+0.060) W(+0.060) W(+0.065) W(+0.066) |
| (e) rule_output | 0 | 5 | 0 | T(+0.002) T(+0.002) T(+0.002) T(-0.005) T(-0.004) |
| (e) rule_confident_uv | 3 | 2 | 0 | W(+0.020) W(+0.020) W(+0.020) T(+0.003) T(+0.009) |

S3 quantities: independence MAE 0.0162, gap (pairwise m3 minus indep) -0.0018.

S3 rho recomputed with the new settings (14 settings, supplementary): -0.095 (p = 0.748).

