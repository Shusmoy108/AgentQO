## New settings (landed after the registered run; not part of the S1-S4 verdicts)

Same 14 methods, 5 budgets, 30 seeds and metrics as the registered run. 2 objectives only (no latency truth).

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

S3 rho recomputed with the new settings (12 settings, supplementary): 0.035 (p = 0.914).

