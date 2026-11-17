## X1, frozen predictions (predictions.csv)

Pooled:

| placement | k | all | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau | h3c within 10% | h3c within 20% | h3c MAPE p95 | h3c Kendall tau | mean_sum within 10% | mean_sum within 20% | mean_sum MAPE p95 | mean_sum Kendall tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| separate | 16 |  | 320 | 0.759 | 0.912 | 0.075 | 0.929 | 0.138 | 0.188 | 1.050 | 0.820 | 0.000 | 0.009 | 0.584 | 0.779 |
| shared | 16 |  | 618 | 0.681 | 0.932 | 0.081 | 0.907 | 0.026 | 0.063 | 1.287 | 0.745 | 0.081 | 0.215 | 0.325 | 0.736 |
|  |  | all | 938 | 0.708 | 0.925 | 0.079 | 0.927 | 0.069 | 0.112 | 1.195 | 0.788 | 0.053 | 0.145 | 0.413 | 0.575 |

By setting:

| setting | placement | k | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau | h3c within 10% | h3c within 20% | h3c MAPE p95 | h3c Kendall tau | mean_sum within 10% | mean_sum within 20% | mean_sum MAPE p95 | mean_sum Kendall tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| complex_q15_7 | shared | 16 | 184 | 0.804 | 0.962 | 0.064 | 0.844 | 0.000 | 0.005 | 1.125 | 0.692 | 0.054 | 0.179 | 0.304 | 0.624 |
| hotpot_iso_q15_7 | separate | 16 | 32 | 0.312 | 0.656 | 0.147 | 0.677 | 0.000 | 0.000 | 1.875 | 0.710 | 0.000 | 0.000 | 1.140 | 0.673 |
| hotpot_iso_q15_7 | shared | 16 | 32 | 0.188 | 0.750 | 0.158 | 0.677 | 0.000 | 0.000 | 2.409 | 0.593 | 0.375 | 0.625 | 0.202 | 0.270 |
| hotpot_q15_7 | separate | 16 | 32 | 0.281 | 0.594 | 0.181 | 0.641 | 0.000 | 0.000 | 1.962 | 0.649 | 0.000 | 0.000 | 1.103 | 0.593 |
| hotpot_q15_7 | shared | 16 | 32 | 0.062 | 0.375 | 0.217 | 0.734 | 0.000 | 0.000 | 2.529 | 0.669 | 0.375 | 0.594 | 0.216 | 0.319 |
| math_granite | separate | 16 | 64 | 0.781 | 0.984 | 0.063 | 0.720 | 0.000 | 0.000 | 0.978 | 0.726 | 0.000 | 0.047 | 0.400 | 0.745 |
| math_granite | shared | 16 | 64 | 0.797 | 1.000 | 0.059 | 0.638 | 0.000 | 0.000 | 1.334 | 0.296 | 0.031 | 0.062 | 0.316 | 0.411 |
| math_phi | separate | 16 | 64 | 0.875 | 0.984 | 0.052 | 0.805 | 0.000 | 0.000 | 1.179 | 0.794 | 0.000 | 0.000 | 0.505 | 0.770 |
| math_phi | shared | 16 | 64 | 0.734 | 1.000 | 0.074 | 0.676 | 0.000 | 0.000 | 1.467 | 0.594 | 0.031 | 0.188 | 0.280 | 0.549 |
| math_q15_7 | separate | 16 | 64 | 0.891 | 0.984 | 0.054 | 0.845 | 0.688 | 0.938 | 0.079 | 0.763 | 0.000 | 0.000 | 0.389 | 0.788 |
| math_q15_7 | shared | 16 | 64 | 0.828 | 0.984 | 0.055 | 0.795 | 0.203 | 0.484 | 0.201 | 0.699 | 0.000 | 0.000 | 0.688 | 0.570 |
| math_q3_14 | separate | 16 | 64 | 0.953 | 0.984 | 0.042 | 0.905 | 0.000 | 0.000 | 1.098 | 0.872 | 0.000 | 0.000 | 0.502 | 0.878 |
| math_q3_14 | shared | 16 | 64 | 0.844 | 1.000 | 0.050 | 0.783 | 0.000 | 0.000 | 1.426 | 0.468 | 0.047 | 0.250 | 0.246 | 0.614 |
| math_tiers | shared | 16 | 114 | 0.526 | 0.947 | 0.094 | 0.781 | - | - | - | - | 0.079 | 0.254 | 0.297 | 0.488 |

By plan type (latsim only):

| placement | k | plan_type | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau |
|---|---|---|---|---|---|---|---|
| separate | 16 | 3+_large | 194 | 0.768 | 0.907 | 0.075 | 0.929 |
| separate | 16 | all_large | 6 | 0.667 | 0.667 | 0.099 | 1.000 |
| separate | 16 | all_small | 6 | 1.000 | 1.000 | 0.048 | 1.000 |
| separate | 16 | one_large | 34 | 0.765 | 0.912 | 0.083 | 0.897 |
| separate | 16 | two_large | 80 | 0.725 | 0.938 | 0.072 | 0.910 |
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
| separate | 16 |  | 320 | 0.844 | 0.981 | 0.055 | 0.931 | 0.138 | 0.188 | 1.050 | 0.820 | 0.000 | 0.009 | 0.584 | 0.779 |
| shared | 16 |  | 618 | 0.751 | 0.977 | 0.068 | 0.907 | 0.026 | 0.063 | 1.287 | 0.745 | 0.081 | 0.215 | 0.325 | 0.736 |
|  |  | all | 938 | 0.783 | 0.979 | 0.063 | 0.930 | 0.069 | 0.112 | 1.195 | 0.788 | 0.053 | 0.145 | 0.413 | 0.575 |

By setting:

| setting | placement | k | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau | h3c within 10% | h3c within 20% | h3c MAPE p95 | h3c Kendall tau | mean_sum within 10% | mean_sum within 20% | mean_sum MAPE p95 | mean_sum Kendall tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| complex_q15_7 | shared | 16 | 184 | 0.810 | 0.978 | 0.061 | 0.841 | 0.000 | 0.005 | 1.125 | 0.692 | 0.054 | 0.179 | 0.304 | 0.624 |
| hotpot_iso_q15_7 | separate | 16 | 32 | 0.812 | 1.000 | 0.055 | 0.694 | 0.000 | 0.000 | 1.875 | 0.710 | 0.000 | 0.000 | 1.140 | 0.673 |
| hotpot_iso_q15_7 | shared | 16 | 32 | 0.812 | 1.000 | 0.069 | 0.637 | 0.000 | 0.000 | 2.409 | 0.593 | 0.375 | 0.625 | 0.202 | 0.270 |
| hotpot_q15_7 | separate | 16 | 32 | 0.750 | 0.938 | 0.067 | 0.685 | 0.000 | 0.000 | 1.962 | 0.649 | 0.000 | 0.000 | 1.103 | 0.593 |
| hotpot_q15_7 | shared | 16 | 32 | 0.688 | 0.906 | 0.092 | 0.706 | 0.000 | 0.000 | 2.529 | 0.669 | 0.375 | 0.594 | 0.216 | 0.319 |
| math_granite | separate | 16 | 64 | 0.797 | 0.984 | 0.063 | 0.721 | 0.000 | 0.000 | 0.978 | 0.726 | 0.000 | 0.047 | 0.400 | 0.745 |
| math_granite | shared | 16 | 64 | 0.797 | 1.000 | 0.060 | 0.642 | 0.000 | 0.000 | 1.334 | 0.296 | 0.031 | 0.062 | 0.316 | 0.411 |
| math_phi | separate | 16 | 64 | 0.844 | 0.984 | 0.053 | 0.807 | 0.000 | 0.000 | 1.179 | 0.794 | 0.000 | 0.000 | 0.505 | 0.770 |
| math_phi | shared | 16 | 64 | 0.734 | 1.000 | 0.072 | 0.676 | 0.000 | 0.000 | 1.467 | 0.594 | 0.031 | 0.188 | 0.280 | 0.549 |
| math_q15_7 | separate | 16 | 64 | 0.859 | 0.984 | 0.056 | 0.848 | 0.688 | 0.938 | 0.079 | 0.763 | 0.000 | 0.000 | 0.389 | 0.788 |
| math_q15_7 | shared | 16 | 64 | 0.828 | 0.984 | 0.054 | 0.793 | 0.203 | 0.484 | 0.201 | 0.699 | 0.000 | 0.000 | 0.688 | 0.570 |
| math_q3_14 | separate | 16 | 64 | 0.938 | 0.984 | 0.042 | 0.906 | 0.000 | 0.000 | 1.098 | 0.872 | 0.000 | 0.000 | 0.502 | 0.878 |
| math_q3_14 | shared | 16 | 64 | 0.844 | 1.000 | 0.049 | 0.781 | 0.000 | 0.000 | 1.426 | 0.468 | 0.047 | 0.250 | 0.246 | 0.614 |
| math_tiers | shared | 16 | 114 | 0.544 | 0.947 | 0.092 | 0.784 | - | - | - | - | 0.079 | 0.254 | 0.297 | 0.488 |

By plan type (latsim only):

| placement | k | plan_type | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau |
|---|---|---|---|---|---|---|---|
| separate | 16 | 3+_large | 194 | 0.881 | 0.995 | 0.049 | 0.930 |
| separate | 16 | all_large | 6 | 1.000 | 1.000 | 0.026 | 1.000 |
| separate | 16 | all_small | 6 | 0.833 | 1.000 | 0.071 | 1.000 |
| separate | 16 | one_large | 34 | 0.618 | 0.912 | 0.089 | 0.900 |
| separate | 16 | two_large | 80 | 0.838 | 0.975 | 0.055 | 0.909 |
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
| X1/math_granite/separate/placement_summary.csv | separate | 16 | 64 | 64 | 2 |
| X1/math_phi/separate/placement_summary.csv | separate | 16 | 64 | 64 | 2 |
| X1/math_q15_7/separate/placement_summary.csv | separate | 16 | 64 | 64 | 2 |
| X1/math_q15_7/shared/placement_summary.csv | shared | 16 | 64 | 64 | 2 |
| X1/math_q3_14/separate/placement_summary.csv | separate | 16 | 64 | 64 | 2 |
| X1/math_tiers/shared/placement_summary.csv | shared | 16 | 114 | 114 | 2 |
| X1_vmB/math_granite/shared/placement_summary.csv | shared | 16 | 64 | 64 | 2 |
| X1_vmB/math_phi/shared/placement_summary.csv | shared | 16 | 64 | 64 | 2 |
| X1_vmB/math_q3_14/shared/placement_summary.csv | shared | 16 | 64 | 64 | 2 |

## X1b, frozen predictions (predictions.csv)

Pooled:

| placement | k | all | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau | h3c within 10% | h3c within 20% | h3c MAPE p95 | h3c Kendall tau | mean_sum within 10% | mean_sum within 20% | mean_sum MAPE p95 | mean_sum Kendall tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| separate | 32 |  | 59 | 0.610 | 0.847 | 0.117 | 0.918 | 0.119 | 0.254 | 0.823 | 0.771 | 0.017 | 0.034 | 0.468 | 0.743 |
| separate | 4 |  | 59 | 0.661 | 0.949 | 0.075 | 0.916 | 0.153 | 0.237 | 1.119 | 0.774 | 0.000 | 0.000 | 0.651 | 0.742 |
| separate | 8 |  | 59 | 0.661 | 0.915 | 0.085 | 0.921 | 0.136 | 0.254 | 1.048 | 0.770 | 0.000 | 0.034 | 0.605 | 0.739 |
|  |  | all | 177 | 0.644 | 0.904 | 0.092 | 0.914 | 0.136 | 0.249 | 0.997 | 0.753 | 0.006 | 0.023 | 0.574 | 0.721 |

By setting:

| setting | placement | k | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau | h3c within 10% | h3c within 20% | h3c MAPE p95 | h3c Kendall tau | mean_sum within 10% | mean_sum within 20% | mean_sum MAPE p95 | mean_sum Kendall tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hotpot_q15_7 | separate | 32 | 11 | 0.000 | 0.182 | 0.334 | 0.782 | 0.000 | 0.000 | 1.529 | 0.745 | 0.000 | 0.000 | 0.780 | 0.745 |
| hotpot_q15_7 | separate | 4 | 11 | 0.727 | 0.818 | 0.091 | 0.818 | 0.000 | 0.000 | 2.315 | 0.818 | 0.000 | 0.000 | 1.336 | 0.818 |
| hotpot_q15_7 | separate | 8 | 11 | 0.636 | 0.727 | 0.109 | 0.673 | 0.000 | 0.000 | 2.231 | 0.818 | 0.000 | 0.000 | 1.275 | 0.818 |
| math_granite | separate | 32 | 16 | 0.812 | 1.000 | 0.067 | 0.850 | 0.000 | 0.000 | 0.882 | 0.683 | 0.062 | 0.125 | 0.338 | 0.650 |
| math_granite | separate | 4 | 16 | 0.562 | 1.000 | 0.075 | 0.783 | 0.000 | 0.000 | 1.149 | 0.783 | 0.000 | 0.000 | 0.529 | 0.783 |
| math_granite | separate | 8 | 16 | 0.625 | 0.938 | 0.083 | 0.817 | 0.000 | 0.000 | 1.027 | 0.650 | 0.000 | 0.125 | 0.442 | 0.650 |
| math_phi | separate | 32 | 16 | 0.625 | 1.000 | 0.067 | 0.867 | 0.000 | 0.000 | 1.005 | 0.900 | 0.000 | 0.000 | 0.390 | 0.817 |
| math_phi | separate | 4 | 16 | 0.688 | 1.000 | 0.066 | 0.917 | 0.000 | 0.000 | 1.276 | 0.933 | 0.000 | 0.000 | 0.579 | 0.850 |
| math_phi | separate | 8 | 16 | 0.812 | 1.000 | 0.073 | 0.900 | 0.000 | 0.000 | 1.204 | 0.917 | 0.000 | 0.000 | 0.529 | 0.833 |
| math_q15_7 | separate | 32 | 16 | 0.812 | 1.000 | 0.066 | 0.833 | 0.438 | 0.938 | 0.097 | 0.700 | 0.000 | 0.000 | 0.460 | 0.867 |
| math_q15_7 | separate | 4 | 16 | 0.688 | 0.938 | 0.072 | 0.733 | 0.562 | 0.875 | 0.109 | 0.800 | 0.000 | 0.000 | 0.373 | 0.867 |
| math_q15_7 | separate | 8 | 16 | 0.562 | 0.938 | 0.081 | 0.750 | 0.500 | 0.938 | 0.099 | 0.817 | 0.000 | 0.000 | 0.382 | 0.917 |

By plan type (latsim only):

| placement | k | plan_type | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau |
|---|---|---|---|---|---|---|---|
| separate | 32 | 3+_large | 21 | 0.714 | 0.857 | 0.116 | 0.952 |
| separate | 32 | all_large | 4 | 0.750 | 0.750 | 0.195 | 1.000 |
| separate | 32 | all_small | 4 | 0.500 | 0.750 | 0.133 | 1.000 |
| separate | 32 | one_large | 23 | 0.522 | 0.870 | 0.108 | 0.913 |
| separate | 32 | two_large | 7 | 0.571 | 0.857 | 0.094 | 1.000 |
| separate | 4 | 3+_large | 21 | 0.571 | 0.905 | 0.083 | 0.924 |
| separate | 4 | all_large | 4 | 1.000 | 1.000 | 0.043 | 1.000 |
| separate | 4 | all_small | 4 | 0.750 | 1.000 | 0.032 | 1.000 |
| separate | 4 | one_large | 23 | 0.652 | 0.957 | 0.081 | 0.929 |
| separate | 4 | two_large | 7 | 0.714 | 1.000 | 0.071 | 1.000 |
| separate | 8 | 3+_large | 21 | 0.714 | 0.857 | 0.086 | 0.943 |
| separate | 8 | all_large | 4 | 0.750 | 0.750 | 0.075 | 1.000 |
| separate | 8 | all_small | 4 | 0.500 | 1.000 | 0.108 | 1.000 |
| separate | 8 | one_large | 23 | 0.609 | 0.957 | 0.085 | 0.937 |
| separate | 8 | two_large | 7 | 0.714 | 1.000 | 0.073 | 1.000 |

## X1b, rev1 predictions (rev1/predictions.csv)

Pooled:

| placement | k | all | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau | h3c within 10% | h3c within 20% | h3c MAPE p95 | h3c Kendall tau | mean_sum within 10% | mean_sum within 20% | mean_sum MAPE p95 | mean_sum Kendall tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| separate | 32 |  | 59 | 0.712 | 0.966 | 0.077 | 0.933 | 0.119 | 0.254 | 0.823 | 0.771 | 0.017 | 0.034 | 0.468 | 0.743 |
| separate | 4 |  | 59 | 0.661 | 0.983 | 0.075 | 0.917 | 0.153 | 0.237 | 1.119 | 0.774 | 0.000 | 0.000 | 0.651 | 0.742 |
| separate | 8 |  | 59 | 0.644 | 0.966 | 0.079 | 0.925 | 0.136 | 0.254 | 1.048 | 0.770 | 0.000 | 0.034 | 0.605 | 0.739 |
|  |  | all | 177 | 0.672 | 0.972 | 0.077 | 0.923 | 0.136 | 0.249 | 0.997 | 0.753 | 0.006 | 0.023 | 0.574 | 0.721 |

By setting:

| setting | placement | k | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau | h3c within 10% | h3c within 20% | h3c MAPE p95 | h3c Kendall tau | mean_sum within 10% | mean_sum within 20% | mean_sum MAPE p95 | mean_sum Kendall tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hotpot_q15_7 | separate | 32 | 11 | 0.545 | 0.818 | 0.106 | 0.673 | 0.000 | 0.000 | 1.529 | 0.745 | 0.000 | 0.000 | 0.780 | 0.745 |
| hotpot_q15_7 | separate | 4 | 11 | 0.636 | 1.000 | 0.096 | 0.855 | 0.000 | 0.000 | 2.315 | 0.818 | 0.000 | 0.000 | 1.336 | 0.818 |
| hotpot_q15_7 | separate | 8 | 11 | 0.545 | 1.000 | 0.077 | 0.745 | 0.000 | 0.000 | 2.231 | 0.818 | 0.000 | 0.000 | 1.275 | 0.818 |
| math_granite | separate | 32 | 16 | 0.812 | 1.000 | 0.067 | 0.850 | 0.000 | 0.000 | 0.882 | 0.683 | 0.062 | 0.125 | 0.338 | 0.650 |
| math_granite | separate | 4 | 16 | 0.625 | 1.000 | 0.074 | 0.783 | 0.000 | 0.000 | 1.149 | 0.783 | 0.000 | 0.000 | 0.529 | 0.783 |
| math_granite | separate | 8 | 16 | 0.625 | 0.938 | 0.081 | 0.817 | 0.000 | 0.000 | 1.027 | 0.650 | 0.000 | 0.125 | 0.442 | 0.650 |
| math_phi | separate | 32 | 16 | 0.625 | 1.000 | 0.068 | 0.867 | 0.000 | 0.000 | 1.005 | 0.900 | 0.000 | 0.000 | 0.390 | 0.817 |
| math_phi | separate | 4 | 16 | 0.688 | 1.000 | 0.066 | 0.917 | 0.000 | 0.000 | 1.276 | 0.933 | 0.000 | 0.000 | 0.579 | 0.850 |
| math_phi | separate | 8 | 16 | 0.812 | 1.000 | 0.075 | 0.900 | 0.000 | 0.000 | 1.204 | 0.917 | 0.000 | 0.000 | 0.529 | 0.833 |
| math_q15_7 | separate | 32 | 16 | 0.812 | 1.000 | 0.075 | 0.817 | 0.438 | 0.938 | 0.097 | 0.700 | 0.000 | 0.000 | 0.460 | 0.867 |
| math_q15_7 | separate | 4 | 16 | 0.688 | 0.938 | 0.072 | 0.733 | 0.562 | 0.875 | 0.109 | 0.800 | 0.000 | 0.000 | 0.373 | 0.867 |
| math_q15_7 | separate | 8 | 16 | 0.562 | 0.938 | 0.082 | 0.733 | 0.500 | 0.938 | 0.099 | 0.817 | 0.000 | 0.000 | 0.382 | 0.917 |

By plan type (latsim only):

| placement | k | plan_type | n | latsim within 10% | latsim within 20% | latsim MAPE p95 | latsim Kendall tau |
|---|---|---|---|---|---|---|---|
| separate | 32 | 3+_large | 21 | 0.810 | 1.000 | 0.070 | 0.952 |
| separate | 32 | all_large | 4 | 1.000 | 1.000 | 0.067 | 1.000 |
| separate | 32 | all_small | 4 | 0.500 | 0.750 | 0.100 | 1.000 |
| separate | 32 | one_large | 23 | 0.609 | 0.957 | 0.084 | 0.905 |
| separate | 32 | two_large | 7 | 0.714 | 1.000 | 0.065 | 1.000 |
| separate | 4 | 3+_large | 21 | 0.571 | 1.000 | 0.080 | 0.924 |
| separate | 4 | all_large | 4 | 0.750 | 1.000 | 0.056 | 1.000 |
| separate | 4 | all_small | 4 | 0.750 | 1.000 | 0.038 | 1.000 |
| separate | 4 | one_large | 23 | 0.696 | 0.957 | 0.082 | 0.929 |
| separate | 4 | two_large | 7 | 0.714 | 1.000 | 0.075 | 1.000 |
| separate | 8 | 3+_large | 21 | 0.667 | 0.952 | 0.079 | 0.933 |
| separate | 8 | all_large | 4 | 1.000 | 1.000 | 0.037 | 1.000 |
| separate | 8 | all_small | 4 | 0.500 | 1.000 | 0.095 | 1.000 |
| separate | 8 | one_large | 23 | 0.609 | 0.957 | 0.083 | 0.937 |
| separate | 8 | two_large | 7 | 0.571 | 1.000 | 0.080 | 1.000 |

### X1b coverage

| summary | placement | K | plans measured | plans listed | min repeats |
|---|---|---|---|---|---|
| X1b/hotpot_q15_7/separate_k32/placement_summary.csv | separate | 32 | 11 | 11 | 2 |
| X1b/hotpot_q15_7/separate_k4/placement_summary.csv | separate | 4 | 11 | 11 | 2 |
| X1b/hotpot_q15_7/separate_k8/placement_summary.csv | separate | 8 | 11 | 11 | 2 |
| X1b/math_granite/separate_k32/placement_summary.csv | separate | 32 | 16 | 16 | 2 |
| X1b/math_granite/separate_k4/placement_summary.csv | separate | 4 | 16 | 16 | 2 |
| X1b/math_granite/separate_k8/placement_summary.csv | separate | 8 | 16 | 16 | 2 |
| X1b/math_phi/separate_k32/placement_summary.csv | separate | 32 | 16 | 16 | 2 |
| X1b/math_phi/separate_k4/placement_summary.csv | separate | 4 | 16 | 16 | 2 |
| X1b/math_phi/separate_k8/placement_summary.csv | separate | 8 | 16 | 16 | 2 |
| X1b/math_q15_7/separate_k1/placement_summary.csv | separate | 1 | 4 | 16 | 1 |
| X1b/math_q15_7/separate_k32/placement_summary.csv | separate | 32 | 16 | 16 | 2 |
| X1b/math_q15_7/separate_k4/placement_summary.csv | separate | 4 | 16 | 16 | 2 |
| X1b/math_q15_7/separate_k8/placement_summary.csv | separate | 8 | 16 | 16 | 2 |
