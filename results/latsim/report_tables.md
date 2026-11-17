## X1, frozen predictions (predictions.csv)

Pooled:

| placement | k | all | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau | h3c within 10% | h3c within 20% | h3c MAPE p95 | h3c Kendall tau | mean_sum within 10% | mean_sum within 20% | mean_sum MAPE p95 | mean_sum Kendall tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| separate | 16 |  | 128 | 0.594 | 0.805 | 0.109 | 0.875 | 0.344 | 0.469 | 0.999 | 0.332 | 0.000 | 0.000 | 0.755 | 0.095 |
| shared | 16 |  | 618 | 0.681 | 0.932 | 0.081 | 0.907 | 0.026 | 0.063 | 1.287 | 0.745 | 0.081 | 0.215 | 0.325 | 0.736 |
|  |  | all | 746 | 0.666 | 0.910 | 0.085 | 0.927 | 0.090 | 0.146 | 1.228 | 0.774 | 0.067 | 0.178 | 0.399 | 0.722 |

By setting:

| setting | placement | k | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau | h3c within 10% | h3c within 20% | h3c MAPE p95 | h3c Kendall tau | mean_sum within 10% | mean_sum within 20% | mean_sum MAPE p95 | mean_sum Kendall tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| complex_q15_7 | shared | 16 | 184 | 0.804 | 0.962 | 0.064 | 0.844 | 0.000 | 0.005 | 1.125 | 0.692 | 0.054 | 0.179 | 0.304 | 0.624 |
| hotpot_iso_q15_7 | separate | 16 | 32 | 0.312 | 0.656 | 0.147 | 0.677 | 0.000 | 0.000 | 1.875 | 0.710 | 0.000 | 0.000 | 1.140 | 0.673 |
| hotpot_iso_q15_7 | shared | 16 | 32 | 0.188 | 0.750 | 0.158 | 0.677 | 0.000 | 0.000 | 2.409 | 0.593 | 0.375 | 0.625 | 0.202 | 0.270 |
| hotpot_q15_7 | separate | 16 | 32 | 0.281 | 0.594 | 0.181 | 0.641 | 0.000 | 0.000 | 1.962 | 0.649 | 0.000 | 0.000 | 1.103 | 0.593 |
| hotpot_q15_7 | shared | 16 | 32 | 0.062 | 0.375 | 0.217 | 0.734 | 0.000 | 0.000 | 2.529 | 0.669 | 0.375 | 0.594 | 0.216 | 0.319 |
| math_granite | shared | 16 | 64 | 0.797 | 1.000 | 0.059 | 0.638 | 0.000 | 0.000 | 1.334 | 0.296 | 0.031 | 0.062 | 0.316 | 0.411 |
| math_phi | shared | 16 | 64 | 0.734 | 1.000 | 0.074 | 0.676 | 0.000 | 0.000 | 1.467 | 0.594 | 0.031 | 0.188 | 0.280 | 0.549 |
| math_q15_7 | separate | 16 | 64 | 0.891 | 0.984 | 0.054 | 0.845 | 0.688 | 0.938 | 0.079 | 0.763 | 0.000 | 0.000 | 0.389 | 0.788 |
| math_q15_7 | shared | 16 | 64 | 0.828 | 0.984 | 0.055 | 0.795 | 0.203 | 0.484 | 0.201 | 0.699 | 0.000 | 0.000 | 0.688 | 0.570 |
| math_q3_14 | shared | 16 | 64 | 0.844 | 1.000 | 0.050 | 0.783 | 0.000 | 0.000 | 1.426 | 0.468 | 0.047 | 0.250 | 0.246 | 0.614 |
| math_tiers | shared | 16 | 114 | 0.526 | 0.947 | 0.094 | 0.781 | - | - | - | - | 0.079 | 0.254 | 0.297 | 0.488 |

By plan type (latsim only):

| placement | k | plan_type | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau |
|---|---|---|---|---|---|---|---|
| separate | 16 | 3+_large | 71 | 0.563 | 0.746 | 0.118 | 0.896 |
| separate | 16 | all_large | 3 | 0.333 | 0.333 | 0.170 | 1.000 |
| separate | 16 | all_small | 3 | 1.000 | 1.000 | 0.044 | 1.000 |
| separate | 16 | one_large | 16 | 0.688 | 0.875 | 0.098 | 0.817 |
| separate | 16 | two_large | 35 | 0.600 | 0.914 | 0.096 | 0.866 |
| shared | 16 | 3+_large | 352 | 0.750 | 0.943 | 0.073 | 0.890 |
| shared | 16 | all_large | 6 | 0.667 | 0.833 | 0.097 | 1.000 |
| shared | 16 | all_small | 8 | 1.000 | 1.000 | 0.042 | 0.909 |
| shared | 16 | one_large | 41 | 0.610 | 0.902 | 0.090 | 0.898 |
| shared | 16 | tiers:has_xl | 102 | 0.480 | 0.941 | 0.099 | 0.732 |
| shared | 16 | tiers:large_only | 11 | 0.909 | 1.000 | 0.052 | 0.745 |
| shared | 16 | two_large | 98 | 0.622 | 0.888 | 0.091 | 0.908 |

## X1, rev1 predictions (rev1/predictions.csv)

Pooled:

| placement | k | all | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau | h3c within 10% | h3c within 20% | h3c MAPE p95 | h3c Kendall tau | mean_sum within 10% | mean_sum within 20% | mean_sum MAPE p95 | mean_sum Kendall tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| separate | 16 |  | 128 | 0.820 | 0.977 | 0.059 | 0.890 | 0.344 | 0.469 | 0.999 | 0.332 | 0.000 | 0.000 | 0.755 | 0.095 |
| shared | 16 |  | 618 | 0.751 | 0.977 | 0.068 | 0.907 | 0.026 | 0.063 | 1.287 | 0.745 | 0.081 | 0.215 | 0.325 | 0.736 |
|  |  | all | 746 | 0.763 | 0.977 | 0.066 | 0.930 | 0.090 | 0.146 | 1.228 | 0.774 | 0.067 | 0.178 | 0.399 | 0.722 |

By setting:

| setting | placement | k | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau | h3c within 10% | h3c within 20% | h3c MAPE p95 | h3c Kendall tau | mean_sum within 10% | mean_sum within 20% | mean_sum MAPE p95 | mean_sum Kendall tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| complex_q15_7 | shared | 16 | 184 | 0.810 | 0.978 | 0.061 | 0.841 | 0.000 | 0.005 | 1.125 | 0.692 | 0.054 | 0.179 | 0.304 | 0.624 |
| hotpot_iso_q15_7 | separate | 16 | 32 | 0.812 | 1.000 | 0.055 | 0.694 | 0.000 | 0.000 | 1.875 | 0.710 | 0.000 | 0.000 | 1.140 | 0.673 |
| hotpot_iso_q15_7 | shared | 16 | 32 | 0.812 | 1.000 | 0.069 | 0.637 | 0.000 | 0.000 | 2.409 | 0.593 | 0.375 | 0.625 | 0.202 | 0.270 |
| hotpot_q15_7 | separate | 16 | 32 | 0.750 | 0.938 | 0.067 | 0.685 | 0.000 | 0.000 | 1.962 | 0.649 | 0.000 | 0.000 | 1.103 | 0.593 |
| hotpot_q15_7 | shared | 16 | 32 | 0.688 | 0.906 | 0.092 | 0.706 | 0.000 | 0.000 | 2.529 | 0.669 | 0.375 | 0.594 | 0.216 | 0.319 |
| math_granite | shared | 16 | 64 | 0.797 | 1.000 | 0.060 | 0.642 | 0.000 | 0.000 | 1.334 | 0.296 | 0.031 | 0.062 | 0.316 | 0.411 |
| math_phi | shared | 16 | 64 | 0.734 | 1.000 | 0.072 | 0.676 | 0.000 | 0.000 | 1.467 | 0.594 | 0.031 | 0.188 | 0.280 | 0.549 |
| math_q15_7 | separate | 16 | 64 | 0.859 | 0.984 | 0.056 | 0.848 | 0.688 | 0.938 | 0.079 | 0.763 | 0.000 | 0.000 | 0.389 | 0.788 |
| math_q15_7 | shared | 16 | 64 | 0.828 | 0.984 | 0.054 | 0.793 | 0.203 | 0.484 | 0.201 | 0.699 | 0.000 | 0.000 | 0.688 | 0.570 |
| math_q3_14 | shared | 16 | 64 | 0.844 | 1.000 | 0.049 | 0.781 | 0.000 | 0.000 | 1.426 | 0.468 | 0.047 | 0.250 | 0.246 | 0.614 |
| math_tiers | shared | 16 | 114 | 0.544 | 0.947 | 0.092 | 0.784 | - | - | - | - | 0.079 | 0.254 | 0.297 | 0.488 |

By plan type (latsim only):

| placement | k | plan_type | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau |
|---|---|---|---|---|---|---|---|
| separate | 16 | 3+_large | 71 | 0.901 | 0.986 | 0.048 | 0.903 |
| separate | 16 | all_large | 3 | 1.000 | 1.000 | 0.024 | 1.000 |
| separate | 16 | all_small | 3 | 0.667 | 1.000 | 0.090 | 1.000 |
| separate | 16 | one_large | 16 | 0.375 | 0.875 | 0.112 | 0.833 |
| separate | 16 | two_large | 35 | 0.857 | 1.000 | 0.055 | 0.866 |
| shared | 16 | 3+_large | 352 | 0.827 | 0.989 | 0.059 | 0.891 |
| shared | 16 | all_large | 6 | 1.000 | 1.000 | 0.033 | 1.000 |
| shared | 16 | all_small | 8 | 0.750 | 1.000 | 0.049 | 0.909 |
| shared | 16 | one_large | 41 | 0.659 | 0.951 | 0.074 | 0.898 |
| shared | 16 | tiers:has_xl | 102 | 0.500 | 0.941 | 0.097 | 0.736 |
| shared | 16 | tiers:large_only | 11 | 0.909 | 1.000 | 0.050 | 0.745 |
| shared | 16 | two_large | 98 | 0.745 | 0.980 | 0.072 | 0.904 |

### X1 coverage

| summary | placement | K | plans measured | plans listed | min repeats |
|---|---|---|---|---|---|
| X1/complex_q15_7/shared/placement_summary.csv | shared | 16 | 184 | 184 | 2 |
| X1/hotpot_iso_q15_7/separate/placement_summary.csv | separate | 16 | 32 | 32 | 2 |
| X1/hotpot_iso_q15_7/shared/placement_summary.csv | shared | 16 | 32 | 32 | 2 |
| X1/hotpot_q15_7/separate/placement_summary.csv | separate | 16 | 32 | 32 | 2 |
| X1/hotpot_q15_7/shared/placement_summary.csv | shared | 16 | 32 | 32 | 2 |
| X1/math_q15_7/separate/placement_summary.csv | separate | 16 | 64 | 64 | 2 |
| X1/math_q15_7/shared/placement_summary.csv | shared | 16 | 64 | 64 | 2 |
| X1/math_tiers/shared/placement_summary.csv | shared | 16 | 114 | 114 | 2 |
| X1_vmB/math_granite/shared/placement_summary.csv | shared | 16 | 64 | 64 | 2 |
| X1_vmB/math_phi/shared/placement_summary.csv | shared | 16 | 64 | 64 | 2 |
| X1_vmB/math_q3_14/shared/placement_summary.csv | shared | 16 | 64 | 64 | 2 |

## X1b

No measured files yet (results/v2/X1b*/*/*/placement_summary.csv).
