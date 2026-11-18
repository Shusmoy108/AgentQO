# Phase X1b

Generated 2026-11-18 00:03 UTC, backend `vllm`.

Code run: `c1bb8338fa64acd82d82f1eb0c5a5ce6cb7b019b`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| hotpot_q15_7/separate_k32 | finished |
| hotpot_q15_7/separate_k4 | finished |
| hotpot_q15_7/separate_k8 | finished |
| hotpot_q15_7/shared_k32 | finished |
| hotpot_q15_7/shared_k4 | finished |
| hotpot_q15_7/shared_k8 | finished |
| math_granite/separate_k32 | finished |
| math_granite/separate_k4 | finished |
| math_granite/separate_k8 | finished |
| math_phi/separate_k32 | finished |
| math_phi/separate_k4 | finished |
| math_phi/separate_k8 | finished |
| math_q15_7/separate_k1 | finished |
| math_q15_7/separate_k32 | finished |
| math_q15_7/separate_k4 | finished |
| math_q15_7/separate_k8 | finished |
| math_q15_7/shared_k1 | finished |
| math_q15_7/shared_k32 | finished |
| math_q15_7/shared_k4 | finished |
| math_q15_7/shared_k8 | finished |
| math_q15_7/shared_mps_k32 | finished |
| math_q15_7/shared_mps_k4 | finished |
| math_q15_7/shared_mps_k8 | finished |

## hotpot_q15_7/separate_k32

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 32 | 0 | 64 | 0.895 | 1.411 | 1.545 | 28.201 | 0.266 |
| all_small | separate | 32 | 1 | 64 | 0.785 | 1.238 | 1.547 | 32.044 | 0.297 |
| all_large | separate | 32 | 0 | 64 | 1.352 | 1.998 | 2.315 | 17.894 | 0.547 |
| all_large | separate | 32 | 1 | 64 | 1.345 | 1.986 | 2.396 | 17.39 | 0.516 |
| only_planner | separate | 32 | 0 | 64 | 0.924 | 1.383 | 1.413 | 24.671 | 0.328 |
| only_planner | separate | 32 | 1 | 64 | 0.894 | 1.341 | 1.661 | 24.985 | 0.344 |
| only_hop_1 | separate | 32 | 0 | 64 | 0.875 | 1.277 | 1.345 | 27.268 | 0.359 |
| only_hop_1 | separate | 32 | 1 | 64 | 0.824 | 1.237 | 1.288 | 30.311 | 0.375 |
| only_hop_2 | separate | 32 | 0 | 64 | 0.833 | 1.206 | 1.326 | 29.311 | 0.312 |
| only_hop_2 | separate | 32 | 1 | 64 | 0.778 | 1.197 | 1.305 | 30.568 | 0.281 |
| only_aggregator | separate | 32 | 0 | 64 | 0.781 | 1.194 | 1.274 | 31.238 | 0.406 |
| only_aggregator | separate | 32 | 1 | 64 | 0.789 | 1.136 | 1.23 | 31.64 | 0.438 |
| only_verifier | separate | 32 | 0 | 64 | 0.884 | 1.459 | 1.816 | 26.61 | 0.516 |
| only_verifier | separate | 32 | 1 | 64 | 0.884 | 1.692 | 2.214 | 27.906 | 0.5 |
| hop_1+hop_2+aggregator | separate | 32 | 0 | 64 | 0.877 | 1.301 | 1.403 | 25.808 | 0.469 |
| hop_1+hop_2+aggregator | separate | 32 | 1 | 64 | 0.89 | 1.299 | 1.389 | 24.786 | 0.484 |
| planner+hop_1+hop_2+verifier | separate | 32 | 0 | 64 | 1.243 | 2.128 | 2.376 | 18.383 | 0.469 |
| planner+hop_1+hop_2+verifier | separate | 32 | 1 | 64 | 1.247 | 1.843 | 2.119 | 19.05 | 0.469 |
| planner+verifier | separate | 32 | 0 | 64 | 0.966 | 1.577 | 2.007 | 22.613 | 0.469 |
| planner+verifier | separate | 32 | 1 | 64 | 0.972 | 1.793 | 2.272 | 23.187 | 0.484 |
| hop_1+aggregator+verifier | separate | 32 | 0 | 64 | 1.006 | 1.815 | 1.979 | 23.909 | 0.531 |
| hop_1+aggregator+verifier | separate | 32 | 1 | 64 | 1.011 | 1.654 | 1.968 | 23.894 | 0.531 |

## hotpot_q15_7/separate_k4

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 4 | 0 | 64 | 0.574 | 0.889 | 1.073 | 6.727 | 0.281 |
| all_small | separate | 4 | 1 | 64 | 0.431 | 0.66 | 0.768 | 8.659 | 0.266 |
| all_large | separate | 4 | 0 | 64 | 1.464 | 2.166 | 2.502 | 2.601 | 0.547 |
| all_large | separate | 4 | 1 | 64 | 1.141 | 1.661 | 1.797 | 3.416 | 0.531 |
| only_planner | separate | 4 | 0 | 64 | 0.618 | 1.128 | 1.231 | 5.79 | 0.328 |
| only_planner | separate | 4 | 1 | 64 | 0.634 | 1.077 | 1.106 | 5.888 | 0.328 |
| only_hop_1 | separate | 4 | 0 | 64 | 0.584 | 0.935 | 1.077 | 6.456 | 0.359 |
| only_hop_1 | separate | 4 | 1 | 64 | 0.58 | 0.927 | 1.054 | 6.499 | 0.344 |
| only_hop_2 | separate | 4 | 0 | 64 | 0.526 | 0.808 | 0.84 | 7.405 | 0.297 |
| only_hop_2 | separate | 4 | 1 | 64 | 0.526 | 0.811 | 0.835 | 7.29 | 0.266 |
| only_aggregator | separate | 4 | 0 | 64 | 0.488 | 0.713 | 0.758 | 7.887 | 0.406 |
| only_aggregator | separate | 4 | 1 | 64 | 0.484 | 0.74 | 0.767 | 7.87 | 0.422 |
| only_verifier | separate | 4 | 0 | 64 | 0.595 | 1.296 | 1.463 | 6.084 | 0.484 |
| only_verifier | separate | 4 | 1 | 64 | 0.591 | 1.294 | 1.456 | 6.192 | 0.5 |
| hop_1+hop_2+aggregator | separate | 4 | 0 | 64 | 0.715 | 0.98 | 1.179 | 5.43 | 0.469 |
| hop_1+hop_2+aggregator | separate | 4 | 1 | 64 | 0.707 | 0.986 | 1.141 | 5.518 | 0.484 |
| planner+hop_1+hop_2+verifier | separate | 4 | 0 | 64 | 1.029 | 1.788 | 2.056 | 3.613 | 0.453 |
| planner+hop_1+hop_2+verifier | separate | 4 | 1 | 64 | 0.981 | 1.696 | 1.906 | 3.697 | 0.469 |
| planner+verifier | separate | 4 | 0 | 64 | 0.72 | 1.318 | 1.556 | 4.914 | 0.5 |
| planner+verifier | separate | 4 | 1 | 64 | 0.727 | 1.41 | 1.557 | 4.887 | 0.484 |
| hop_1+aggregator+verifier | separate | 4 | 0 | 64 | 0.794 | 1.329 | 1.557 | 4.809 | 0.562 |
| hop_1+aggregator+verifier | separate | 4 | 1 | 64 | 0.838 | 1.321 | 1.561 | 4.585 | 0.516 |

## hotpot_q15_7/separate_k8

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 8 | 0 | 64 | 0.516 | 0.758 | 0.821 | 14.568 | 0.297 |
| all_small | separate | 8 | 1 | 64 | 0.503 | 0.751 | 0.842 | 14.685 | 0.297 |
| all_large | separate | 8 | 0 | 64 | 1.12 | 1.617 | 1.988 | 6.466 | 0.516 |
| all_large | separate | 8 | 1 | 64 | 1.103 | 1.629 | 1.869 | 6.497 | 0.531 |
| only_planner | separate | 8 | 0 | 64 | 0.661 | 1.099 | 1.27 | 10.769 | 0.359 |
| only_planner | separate | 8 | 1 | 64 | 0.667 | 1.138 | 1.193 | 10.647 | 0.359 |
| only_hop_1 | separate | 8 | 0 | 64 | 0.619 | 0.98 | 1.071 | 11.315 | 0.359 |
| only_hop_1 | separate | 8 | 1 | 64 | 0.63 | 0.98 | 1.027 | 11.208 | 0.312 |
| only_hop_2 | separate | 8 | 0 | 64 | 0.574 | 0.856 | 0.928 | 12.932 | 0.312 |
| only_hop_2 | separate | 8 | 1 | 64 | 0.57 | 0.834 | 0.886 | 12.902 | 0.328 |
| only_aggregator | separate | 8 | 0 | 64 | 0.535 | 0.791 | 0.836 | 13.515 | 0.453 |
| only_aggregator | separate | 8 | 1 | 64 | 0.546 | 0.828 | 0.859 | 13.496 | 0.469 |
| only_verifier | separate | 8 | 0 | 64 | 0.64 | 1.384 | 1.462 | 11.341 | 0.453 |
| only_verifier | separate | 8 | 1 | 64 | 0.639 | 1.2 | 1.415 | 10.996 | 0.516 |
| hop_1+hop_2+aggregator | separate | 8 | 0 | 64 | 0.726 | 1.052 | 1.215 | 10.423 | 0.484 |
| hop_1+hop_2+aggregator | separate | 8 | 1 | 64 | 0.713 | 1.127 | 1.23 | 10.414 | 0.484 |
| planner+hop_1+hop_2+verifier | separate | 8 | 0 | 64 | 1.027 | 1.753 | 1.962 | 6.939 | 0.453 |
| planner+hop_1+hop_2+verifier | separate | 8 | 1 | 64 | 1.016 | 1.759 | 1.95 | 6.972 | 0.438 |
| planner+verifier | separate | 8 | 0 | 64 | 0.752 | 1.445 | 2.004 | 8.942 | 0.5 |
| planner+verifier | separate | 8 | 1 | 64 | 0.754 | 1.437 | 1.948 | 8.825 | 0.484 |
| hop_1+aggregator+verifier | separate | 8 | 0 | 64 | 0.868 | 1.424 | 1.604 | 8.629 | 0.5 |
| hop_1+aggregator+verifier | separate | 8 | 1 | 64 | 0.864 | 1.434 | 1.605 | 8.668 | 0.516 |

## hotpot_q15_7/shared_k32

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 32 | 0 | 64 | 0.852 | 1.316 | 1.481 | 28.848 | 0.281 |
| all_small | shared | 32 | 1 | 64 | 0.847 | 1.208 | 1.414 | 30.787 | 0.297 |
| all_large | shared | 32 | 0 | 64 | 1.329 | 2.027 | 2.35 | 17.775 | 0.547 |
| all_large | shared | 32 | 1 | 64 | 1.337 | 1.998 | 2.256 | 18.075 | 0.547 |
| only_planner | shared | 32 | 0 | 64 | 1.602 | 2.432 | 2.777 | 15.3 | 0.328 |
| only_planner | shared | 32 | 1 | 64 | 1.615 | 2.38 | 2.527 | 15.27 | 0.344 |
| only_hop_1 | shared | 32 | 0 | 64 | 1.483 | 2.177 | 2.285 | 17.545 | 0.344 |
| only_hop_1 | shared | 32 | 1 | 64 | 1.455 | 2.077 | 2.181 | 17.629 | 0.344 |
| only_hop_2 | shared | 32 | 0 | 64 | 1.472 | 2.174 | 2.433 | 17.564 | 0.266 |
| only_hop_2 | shared | 32 | 1 | 64 | 1.499 | 2.598 | 3.055 | 15.164 | 0.266 |
| only_aggregator | shared | 32 | 0 | 64 | 1.441 | 2.31 | 2.393 | 17.054 | 0.391 |
| only_aggregator | shared | 32 | 1 | 64 | 1.532 | 2.538 | 2.826 | 15.09 | 0.344 |
| only_verifier | shared | 32 | 0 | 64 | 1.569 | 2.897 | 3.011 | 15.92 | 0.484 |
| only_verifier | shared | 32 | 1 | 64 | 1.571 | 2.88 | 3.011 | 14.008 | 0.516 |
| hop_1+hop_2+aggregator | shared | 32 | 0 | 64 | 1.583 | 2.25 | 2.438 | 15.397 | 0.453 |
| hop_1+hop_2+aggregator | shared | 32 | 1 | 64 | 1.614 | 2.58 | 2.719 | 15.079 | 0.469 |
| planner+hop_1+hop_2+verifier | shared | 32 | 0 | 64 | 1.939 | 3.037 | 3.532 | 12.977 | 0.453 |
| planner+hop_1+hop_2+verifier | shared | 32 | 1 | 64 | 1.893 | 2.925 | 3.521 | 13.106 | 0.484 |
| planner+verifier | shared | 32 | 0 | 64 | 1.888 | 3.204 | 4.508 | 11.79 | 0.484 |
| planner+verifier | shared | 32 | 1 | 64 | 1.862 | 3.092 | 3.568 | 11.993 | 0.469 |
| hop_1+aggregator+verifier | shared | 32 | 0 | 64 | 1.898 | 3.323 | 3.8 | 13.173 | 0.547 |
| hop_1+aggregator+verifier | shared | 32 | 1 | 64 | 1.905 | 3.666 | 3.836 | 13.429 | 0.516 |

## hotpot_q15_7/shared_k4

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 4 | 0 | 64 | 0.546 | 0.825 | 0.858 | 7.013 | 0.281 |
| all_small | shared | 4 | 1 | 64 | 0.422 | 0.662 | 0.814 | 8.719 | 0.281 |
| all_large | shared | 4 | 0 | 64 | 1.453 | 2.128 | 2.498 | 2.588 | 0.547 |
| all_large | shared | 4 | 1 | 64 | 1.085 | 1.535 | 1.775 | 3.516 | 0.531 |
| only_planner | shared | 4 | 0 | 64 | 1.171 | 1.941 | 1.958 | 3.245 | 0.359 |
| only_planner | shared | 4 | 1 | 64 | 1.192 | 2.318 | 2.605 | 3.062 | 0.344 |
| only_hop_1 | shared | 4 | 0 | 64 | 1.148 | 1.719 | 2.104 | 3.328 | 0.359 |
| only_hop_1 | shared | 4 | 1 | 64 | 1.15 | 2.061 | 2.167 | 3.22 | 0.312 |
| only_hop_2 | shared | 4 | 0 | 64 | 0.969 | 1.655 | 1.793 | 3.856 | 0.281 |
| only_hop_2 | shared | 4 | 1 | 64 | 0.97 | 1.504 | 1.813 | 4.019 | 0.297 |
| only_aggregator | shared | 4 | 0 | 64 | 0.867 | 1.271 | 1.377 | 4.549 | 0.422 |
| only_aggregator | shared | 4 | 1 | 64 | 0.838 | 1.338 | 1.374 | 4.596 | 0.438 |
| only_verifier | shared | 4 | 0 | 64 | 1.149 | 2.456 | 2.688 | 3.117 | 0.5 |
| only_verifier | shared | 4 | 1 | 64 | 1.13 | 2.51 | 2.874 | 3.186 | 0.484 |
| hop_1+hop_2+aggregator | shared | 4 | 0 | 64 | 1.253 | 1.908 | 2.099 | 3.028 | 0.453 |
| hop_1+hop_2+aggregator | shared | 4 | 1 | 64 | 1.308 | 1.829 | 2.081 | 3.014 | 0.484 |
| planner+hop_1+hop_2+verifier | shared | 4 | 0 | 64 | 1.173 | 1.978 | 2.099 | 3.164 | 0.516 |
| planner+hop_1+hop_2+verifier | shared | 4 | 1 | 64 | 1.139 | 1.965 | 2.173 | 3.198 | 0.453 |
| planner+verifier | shared | 4 | 0 | 64 | 1.403 | 2.696 | 3.027 | 2.556 | 0.516 |
| planner+verifier | shared | 4 | 1 | 64 | 1.387 | 2.869 | 3.498 | 2.477 | 0.5 |
| hop_1+aggregator+verifier | shared | 4 | 0 | 64 | 1.56 | 2.438 | 2.735 | 2.537 | 0.531 |
| hop_1+aggregator+verifier | shared | 4 | 1 | 64 | 1.524 | 2.308 | 2.706 | 2.525 | 0.578 |

## hotpot_q15_7/shared_k8

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 8 | 0 | 64 | 0.509 | 0.89 | 0.902 | 14.122 | 0.297 |
| all_small | shared | 8 | 1 | 64 | 0.494 | 0.787 | 0.855 | 15.017 | 0.297 |
| all_large | shared | 8 | 0 | 64 | 1.124 | 1.664 | 1.843 | 6.543 | 0.531 |
| all_large | shared | 8 | 1 | 64 | 1.095 | 1.619 | 1.837 | 6.531 | 0.531 |
| only_planner | shared | 8 | 0 | 64 | 1.406 | 2.504 | 2.956 | 5.213 | 0.344 |
| only_planner | shared | 8 | 1 | 64 | 1.374 | 2.226 | 2.608 | 5.465 | 0.328 |
| only_hop_1 | shared | 8 | 0 | 64 | 1.366 | 2.119 | 2.291 | 5.523 | 0.328 |
| only_hop_1 | shared | 8 | 1 | 64 | 1.315 | 2.039 | 2.17 | 5.748 | 0.375 |
| only_hop_2 | shared | 8 | 0 | 64 | 1.254 | 2.017 | 2.134 | 6.007 | 0.297 |
| only_hop_2 | shared | 8 | 1 | 64 | 1.237 | 1.896 | 1.94 | 6.207 | 0.312 |
| only_aggregator | shared | 8 | 0 | 64 | 1.071 | 1.686 | 1.72 | 7.022 | 0.469 |
| only_aggregator | shared | 8 | 1 | 64 | 1.064 | 1.602 | 1.812 | 7.13 | 0.453 |
| only_verifier | shared | 8 | 0 | 64 | 1.273 | 2.41 | 3.42 | 5.568 | 0.5 |
| only_verifier | shared | 8 | 1 | 64 | 1.441 | 2.702 | 2.948 | 5.139 | 0.484 |
| hop_1+hop_2+aggregator | shared | 8 | 0 | 64 | 1.426 | 2.027 | 2.332 | 5.359 | 0.469 |
| hop_1+hop_2+aggregator | shared | 8 | 1 | 64 | 1.456 | 2.067 | 2.287 | 5.486 | 0.453 |
| planner+hop_1+hop_2+verifier | shared | 8 | 0 | 64 | 1.272 | 2.303 | 2.462 | 5.578 | 0.438 |
| planner+hop_1+hop_2+verifier | shared | 8 | 1 | 64 | 1.27 | 2.292 | 2.483 | 5.596 | 0.453 |
| planner+verifier | shared | 8 | 0 | 64 | 1.519 | 2.779 | 3.314 | 4.517 | 0.516 |
| planner+verifier | shared | 8 | 1 | 64 | 1.509 | 2.71 | 3.751 | 4.504 | 0.5 |
| hop_1+aggregator+verifier | shared | 8 | 0 | 64 | 1.642 | 2.948 | 3.188 | 4.435 | 0.531 |
| hop_1+aggregator+verifier | shared | 8 | 1 | 64 | 1.655 | 2.936 | 3.156 | 4.441 | 0.531 |

## math_granite/separate_k32

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 32 | 0 | 64 | 2.321 | 3.89 | 3.989 | 8.595 | 0.578 |
| all_small | separate | 32 | 1 | 64 | 2.234 | 3.764 | 3.94 | 9.629 | 0.594 |
| all_large | separate | 32 | 0 | 64 | 4.674 | 7.53 | 8.937 | 4.05 | 0.812 |
| all_large | separate | 32 | 1 | 64 | 4.715 | 7.988 | 8.31 | 4.093 | 0.812 |
| only_planner | separate | 32 | 0 | 64 | 2.745 | 4.633 | 5.635 | 5.849 | 0.656 |
| only_planner | separate | 32 | 1 | 64 | 2.875 | 4.882 | 5.461 | 6.212 | 0.625 |
| only_step_1 | separate | 32 | 0 | 64 | 2.454 | 4.159 | 4.944 | 7.558 | 0.547 |
| only_step_1 | separate | 32 | 1 | 64 | 2.493 | 4.614 | 4.983 | 7.826 | 0.578 |
| only_step_2 | separate | 32 | 0 | 64 | 2.503 | 4.246 | 5.238 | 7.626 | 0.547 |
| only_step_2 | separate | 32 | 1 | 64 | 2.342 | 4.809 | 4.907 | 7.415 | 0.578 |
| only_step_3 | separate | 32 | 0 | 64 | 2.498 | 4.176 | 4.536 | 8.689 | 0.562 |
| only_step_3 | separate | 32 | 1 | 64 | 2.414 | 4.107 | 4.801 | 7.862 | 0.547 |
| only_aggregator | separate | 32 | 0 | 64 | 2.52 | 4.795 | 4.962 | 7.236 | 0.562 |
| only_aggregator | separate | 32 | 1 | 64 | 2.612 | 4.736 | 5.165 | 7.856 | 0.562 |
| only_verifier | separate | 32 | 0 | 64 | 3.127 | 4.825 | 5.78 | 6.167 | 0.703 |
| only_verifier | separate | 32 | 1 | 64 | 3.142 | 4.642 | 5.472 | 6.382 | 0.688 |
| planner+step_1+step_2+aggregator+verifier | separate | 32 | 0 | 64 | 4.269 | 6.819 | 7.628 | 5.146 | 0.812 |
| planner+step_1+step_2+aggregator+verifier | separate | 32 | 1 | 64 | 4.225 | 7.744 | 9.938 | 4.473 | 0.812 |
| step_1+step_2+step_3 | separate | 32 | 0 | 64 | 2.548 | 4.724 | 5.23 | 6.735 | 0.562 |
| step_1+step_2+step_3 | separate | 32 | 1 | 64 | 2.492 | 4.803 | 5.314 | 5.184 | 0.547 |
| step_2+step_3+verifier | separate | 32 | 0 | 64 | 3.475 | 5.597 | 6.628 | 5.648 | 0.75 |
| step_2+step_3+verifier | separate | 32 | 1 | 64 | 3.478 | 5.24 | 5.571 | 6.703 | 0.719 |
| step_2+step_3 | separate | 32 | 0 | 64 | 2.791 | 4.456 | 5.443 | 6.832 | 0.547 |
| step_2+step_3 | separate | 32 | 1 | 64 | 2.52 | 4.233 | 4.589 | 7.084 | 0.547 |
| planner+step_1+aggregator | separate | 32 | 0 | 64 | 3.23 | 7.378 | 7.798 | 5.822 | 0.688 |
| planner+step_1+aggregator | separate | 32 | 1 | 64 | 3.37 | 6.178 | 7.611 | 6.317 | 0.734 |
| planner+step_1+step_3+verifier | separate | 32 | 0 | 64 | 4.072 | 7.038 | 7.958 | 5.008 | 0.75 |
| planner+step_1+step_3+verifier | separate | 32 | 1 | 64 | 4.021 | 6.963 | 8.009 | 4.759 | 0.812 |
| planner+step_1+step_2+aggregator | separate | 32 | 0 | 64 | 3.445 | 5.911 | 7.757 | 5.455 | 0.703 |
| planner+step_1+step_2+aggregator | separate | 32 | 1 | 64 | 3.464 | 6.534 | 7.557 | 5.542 | 0.641 |

30 of 32 rows shown.

## math_granite/separate_k4

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 4 | 0 | 64 | 1.818 | 3.581 | 3.841 | 1.931 | 0.516 |
| all_small | separate | 4 | 1 | 64 | 1.767 | 3.373 | 4.104 | 2.03 | 0.594 |
| all_large | separate | 4 | 0 | 64 | 4.304 | 6.531 | 8.16 | 0.883 | 0.766 |
| all_large | separate | 4 | 1 | 64 | 4.231 | 6.997 | 8.449 | 0.843 | 0.781 |
| only_planner | separate | 4 | 0 | 64 | 2.562 | 4.444 | 5.772 | 1.447 | 0.672 |
| only_planner | separate | 4 | 1 | 64 | 2.515 | 4.078 | 5.556 | 1.445 | 0.656 |
| only_step_1 | separate | 4 | 0 | 64 | 1.893 | 3.639 | 4.584 | 1.821 | 0.562 |
| only_step_1 | separate | 4 | 1 | 64 | 1.845 | 3.371 | 4.419 | 1.944 | 0.578 |
| only_step_2 | separate | 4 | 0 | 64 | 2.038 | 3.403 | 4.614 | 1.769 | 0.562 |
| only_step_2 | separate | 4 | 1 | 64 | 1.984 | 3.385 | 4.184 | 1.794 | 0.594 |
| only_step_3 | separate | 4 | 0 | 64 | 1.981 | 3.561 | 3.681 | 1.823 | 0.562 |
| only_step_3 | separate | 4 | 1 | 64 | 1.95 | 3.898 | 4.12 | 1.754 | 0.594 |
| only_aggregator | separate | 4 | 0 | 64 | 2.115 | 4.151 | 5.079 | 1.589 | 0.578 |
| only_aggregator | separate | 4 | 1 | 64 | 2.264 | 4.099 | 4.696 | 1.59 | 0.578 |
| only_verifier | separate | 4 | 0 | 64 | 2.701 | 4.705 | 5.169 | 1.396 | 0.719 |
| only_verifier | separate | 4 | 1 | 64 | 2.712 | 4.536 | 5.325 | 1.394 | 0.703 |
| planner+step_1+step_2+aggregator+verifier | separate | 4 | 0 | 64 | 3.971 | 6.374 | 8.132 | 0.916 | 0.766 |
| planner+step_1+step_2+aggregator+verifier | separate | 4 | 1 | 64 | 3.975 | 6.237 | 6.482 | 0.945 | 0.797 |
| step_1+step_2+step_3 | separate | 4 | 0 | 64 | 2.3 | 4.254 | 5.973 | 1.535 | 0.594 |
| step_1+step_2+step_3 | separate | 4 | 1 | 64 | 2.346 | 3.982 | 5.031 | 1.558 | 0.578 |
| step_2+step_3+verifier | separate | 4 | 0 | 64 | 3.263 | 5.116 | 6.479 | 1.169 | 0.688 |
| step_2+step_3+verifier | separate | 4 | 1 | 64 | 3.262 | 5.285 | 5.782 | 1.144 | 0.719 |
| step_2+step_3 | separate | 4 | 0 | 64 | 2.246 | 3.815 | 4.648 | 1.596 | 0.594 |
| step_2+step_3 | separate | 4 | 1 | 64 | 2.249 | 3.803 | 4.212 | 1.61 | 0.578 |
| planner+step_1+aggregator | separate | 4 | 0 | 64 | 3.001 | 5.589 | 6.303 | 1.169 | 0.641 |
| planner+step_1+aggregator | separate | 4 | 1 | 64 | 2.912 | 5.231 | 8.688 | 1.218 | 0.672 |
| planner+step_1+step_3+verifier | separate | 4 | 0 | 64 | 3.698 | 6.272 | 9.264 | 0.917 | 0.703 |
| planner+step_1+step_3+verifier | separate | 4 | 1 | 64 | 3.528 | 6.357 | 7.475 | 0.993 | 0.703 |
| planner+step_1+step_2+aggregator | separate | 4 | 0 | 64 | 3.179 | 5.751 | 6.545 | 1.096 | 0.641 |
| planner+step_1+step_2+aggregator | separate | 4 | 1 | 64 | 3.151 | 6.012 | 8.303 | 1.112 | 0.641 |

30 of 32 rows shown.

## math_granite/separate_k8

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 8 | 0 | 64 | 1.867 | 3.493 | 6.213 | 2.988 | 0.594 |
| all_small | separate | 8 | 1 | 64 | 1.875 | 3.405 | 3.86 | 3.647 | 0.625 |
| all_large | separate | 8 | 0 | 64 | 4.505 | 6.722 | 8.094 | 1.558 | 0.812 |
| all_large | separate | 8 | 1 | 64 | 4.058 | 7.973 | 8.585 | 1.526 | 0.734 |
| only_planner | separate | 8 | 0 | 64 | 2.631 | 4.029 | 4.61 | 2.655 | 0.594 |
| only_planner | separate | 8 | 1 | 64 | 2.519 | 4.041 | 4.395 | 2.831 | 0.562 |
| only_step_1 | separate | 8 | 0 | 64 | 1.992 | 3.915 | 4.871 | 3.233 | 0.562 |
| only_step_1 | separate | 8 | 1 | 64 | 1.996 | 3.346 | 4.727 | 3.248 | 0.562 |
| only_step_2 | separate | 8 | 0 | 64 | 2.09 | 4.291 | 4.954 | 3.061 | 0.594 |
| only_step_2 | separate | 8 | 1 | 64 | 2.071 | 4.11 | 5.498 | 3.012 | 0.562 |
| only_step_3 | separate | 8 | 0 | 64 | 2.078 | 3.824 | 4.194 | 3.332 | 0.547 |
| only_step_3 | separate | 8 | 1 | 64 | 2.133 | 3.877 | 4.78 | 3.3 | 0.609 |
| only_aggregator | separate | 8 | 0 | 64 | 2.191 | 5.962 | 6.178 | 2.746 | 0.547 |
| only_aggregator | separate | 8 | 1 | 64 | 2.241 | 4.75 | 6.977 | 2.605 | 0.641 |
| only_verifier | separate | 8 | 0 | 64 | 2.679 | 4.46 | 5.547 | 2.567 | 0.719 |
| only_verifier | separate | 8 | 1 | 64 | 2.746 | 3.981 | 4.421 | 2.704 | 0.766 |
| planner+step_1+step_2+aggregator+verifier | separate | 8 | 0 | 64 | 3.953 | 6.997 | 8.439 | 1.725 | 0.734 |
| planner+step_1+step_2+aggregator+verifier | separate | 8 | 1 | 64 | 3.989 | 7.057 | 9.537 | 1.729 | 0.828 |
| step_1+step_2+step_3 | separate | 8 | 0 | 64 | 2.387 | 3.935 | 4.091 | 2.438 | 0.594 |
| step_1+step_2+step_3 | separate | 8 | 1 | 64 | 2.407 | 4.036 | 4.187 | 2.758 | 0.547 |
| step_2+step_3+verifier | separate | 8 | 0 | 64 | 3.169 | 5.405 | 7.276 | 1.933 | 0.75 |
| step_2+step_3+verifier | separate | 8 | 1 | 64 | 3.171 | 5.601 | 6.414 | 2.167 | 0.734 |
| step_2+step_3 | separate | 8 | 0 | 64 | 2.253 | 4.094 | 5.325 | 2.904 | 0.594 |
| step_2+step_3 | separate | 8 | 1 | 64 | 2.296 | 4.105 | 4.58 | 2.867 | 0.594 |
| planner+step_1+aggregator | separate | 8 | 0 | 64 | 2.977 | 5.612 | 7.459 | 2.168 | 0.625 |
| planner+step_1+aggregator | separate | 8 | 1 | 64 | 2.954 | 7.104 | 7.285 | 2.138 | 0.641 |
| planner+step_1+step_3+verifier | separate | 8 | 0 | 64 | 3.768 | 7.132 | 7.797 | 1.75 | 0.75 |
| planner+step_1+step_3+verifier | separate | 8 | 1 | 64 | 3.732 | 7.352 | 9.49 | 1.618 | 0.672 |
| planner+step_1+step_2+aggregator | separate | 8 | 0 | 64 | 3.158 | 5.601 | 6.138 | 2.119 | 0.625 |
| planner+step_1+step_2+aggregator | separate | 8 | 1 | 64 | 3.25 | 5.948 | 6.795 | 2.161 | 0.688 |

30 of 32 rows shown.

## math_phi/separate_k32

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 32 | 0 | 64 | 4.361 | 6.374 | 6.668 | 5.219 | 0.812 |
| all_small | separate | 32 | 1 | 64 | 4.368 | 6.062 | 6.215 | 5.913 | 0.812 |
| all_large | separate | 32 | 0 | 64 | 9.911 | 15.26 | 15.901 | 2.083 | 0.953 |
| all_large | separate | 32 | 1 | 64 | 9.455 | 15.399 | 15.88 | 1.876 | 0.969 |
| only_planner | separate | 32 | 0 | 64 | 4.434 | 6.23 | 6.671 | 5.212 | 0.844 |
| only_planner | separate | 32 | 1 | 64 | 4.484 | 6.739 | 7.008 | 5.201 | 0.812 |
| only_step_1 | separate | 32 | 0 | 64 | 5.649 | 8.321 | 9.295 | 3.932 | 0.797 |
| only_step_1 | separate | 32 | 1 | 64 | 5.557 | 8.273 | 9.185 | 4.099 | 0.828 |
| only_step_2 | separate | 32 | 0 | 64 | 4.729 | 7.303 | 7.451 | 5.11 | 0.766 |
| only_step_2 | separate | 32 | 1 | 64 | 4.654 | 6.97 | 7.365 | 4.607 | 0.797 |
| only_step_3 | separate | 32 | 0 | 64 | 4.846 | 7.326 | 9.473 | 3.355 | 0.828 |
| only_step_3 | separate | 32 | 1 | 64 | 4.893 | 7.316 | 8.243 | 4.259 | 0.797 |
| only_aggregator | separate | 32 | 0 | 64 | 4.721 | 9.395 | 9.581 | 3.739 | 0.859 |
| only_aggregator | separate | 32 | 1 | 64 | 4.827 | 9.346 | 9.467 | 3.909 | 0.828 |
| only_verifier | separate | 32 | 0 | 64 | 5.985 | 8.322 | 9.722 | 4.033 | 0.938 |
| only_verifier | separate | 32 | 1 | 64 | 5.952 | 7.762 | 8.948 | 3.531 | 0.922 |
| planner+step_1+step_2+aggregator+verifier | separate | 32 | 0 | 64 | 8.711 | 14.992 | 17.032 | 2.054 | 0.938 |
| planner+step_1+step_2+aggregator+verifier | separate | 32 | 1 | 64 | 8.6 | 14.466 | 16.002 | 2.105 | 0.953 |
| step_1+step_2+step_3 | separate | 32 | 0 | 64 | 6.405 | 9.475 | 10.469 | 3.242 | 0.828 |
| step_1+step_2+step_3 | separate | 32 | 1 | 64 | 6.293 | 8.701 | 9.447 | 3.423 | 0.766 |
| step_2+step_3+verifier | separate | 32 | 0 | 64 | 7.337 | 11.741 | 12.186 | 2.949 | 0.922 |
| step_2+step_3+verifier | separate | 32 | 1 | 64 | 7.292 | 10.744 | 11.699 | 2.837 | 0.938 |
| step_2+step_3 | separate | 32 | 0 | 64 | 5.125 | 7.68 | 8.558 | 3.94 | 0.797 |
| step_2+step_3 | separate | 32 | 1 | 64 | 5.16 | 8.329 | 9.609 | 4.045 | 0.812 |
| planner+step_1+aggregator | separate | 32 | 0 | 64 | 6.641 | 11.353 | 11.695 | 2.957 | 0.875 |
| planner+step_1+aggregator | separate | 32 | 1 | 64 | 6.464 | 10.817 | 11.593 | 2.992 | 0.828 |
| planner+step_1+step_3+verifier | separate | 32 | 0 | 64 | 8.716 | 12.872 | 14.092 | 2.224 | 0.922 |
| planner+step_1+step_3+verifier | separate | 32 | 1 | 64 | 8.568 | 12.564 | 14.017 | 2.604 | 0.906 |
| planner+step_1+step_2+aggregator | separate | 32 | 0 | 64 | 6.711 | 11.997 | 12.731 | 2.854 | 0.828 |
| planner+step_1+step_2+aggregator | separate | 32 | 1 | 64 | 6.672 | 10.613 | 12.018 | 2.577 | 0.844 |

30 of 32 rows shown.

## math_phi/separate_k4

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 4 | 0 | 64 | 2.993 | 4.374 | 4.916 | 1.256 | 0.844 |
| all_small | separate | 4 | 1 | 64 | 2.975 | 4.369 | 4.634 | 1.264 | 0.844 |
| all_large | separate | 4 | 0 | 64 | 8.981 | 14.093 | 14.748 | 0.419 | 0.938 |
| all_large | separate | 4 | 1 | 64 | 8.955 | 14.103 | 14.757 | 0.421 | 0.984 |
| only_planner | separate | 4 | 0 | 64 | 3.769 | 5.542 | 5.859 | 1.052 | 0.781 |
| only_planner | separate | 4 | 1 | 64 | 3.754 | 5.343 | 5.526 | 1.057 | 0.844 |
| only_step_1 | separate | 4 | 0 | 64 | 4.427 | 6.5 | 7.571 | 0.88 | 0.828 |
| only_step_1 | separate | 4 | 1 | 64 | 4.308 | 6.757 | 7.664 | 0.887 | 0.828 |
| only_step_2 | separate | 4 | 0 | 64 | 3.746 | 6.32 | 6.597 | 0.976 | 0.812 |
| only_step_2 | separate | 4 | 1 | 64 | 3.663 | 5.717 | 5.829 | 0.985 | 0.781 |
| only_step_3 | separate | 4 | 0 | 64 | 3.911 | 6.478 | 6.744 | 0.934 | 0.797 |
| only_step_3 | separate | 4 | 1 | 64 | 3.857 | 5.758 | 6.811 | 0.954 | 0.812 |
| only_aggregator | separate | 4 | 0 | 64 | 3.701 | 8.369 | 8.973 | 0.902 | 0.875 |
| only_aggregator | separate | 4 | 1 | 64 | 3.886 | 8.376 | 8.554 | 0.883 | 0.859 |
| only_verifier | separate | 4 | 0 | 64 | 5.116 | 7.796 | 7.994 | 0.755 | 0.922 |
| only_verifier | separate | 4 | 1 | 64 | 5.171 | 7.748 | 8.477 | 0.738 | 0.922 |
| planner+step_1+step_2+aggregator+verifier | separate | 4 | 0 | 64 | 7.723 | 13.645 | 15.561 | 0.459 | 0.922 |
| planner+step_1+step_2+aggregator+verifier | separate | 4 | 1 | 64 | 7.757 | 13.674 | 16.746 | 0.458 | 0.938 |
| step_1+step_2+step_3 | separate | 4 | 0 | 64 | 5.669 | 9.128 | 9.408 | 0.667 | 0.828 |
| step_1+step_2+step_3 | separate | 4 | 1 | 64 | 5.698 | 8.323 | 9.009 | 0.666 | 0.828 |
| step_2+step_3+verifier | separate | 4 | 0 | 64 | 6.215 | 9.68 | 10.595 | 0.574 | 0.938 |
| step_2+step_3+verifier | separate | 4 | 1 | 64 | 6.126 | 10.169 | 11.281 | 0.574 | 0.906 |
| step_2+step_3 | separate | 4 | 0 | 64 | 4.329 | 6.874 | 7.384 | 0.819 | 0.781 |
| step_2+step_3 | separate | 4 | 1 | 64 | 4.541 | 6.828 | 7.165 | 0.825 | 0.75 |
| planner+step_1+aggregator | separate | 4 | 0 | 64 | 5.59 | 10.604 | 11.491 | 0.645 | 0.844 |
| planner+step_1+aggregator | separate | 4 | 1 | 64 | 5.566 | 10.591 | 10.859 | 0.65 | 0.875 |
| planner+step_1+step_3+verifier | separate | 4 | 0 | 64 | 8.019 | 11.803 | 13.093 | 0.481 | 0.922 |
| planner+step_1+step_3+verifier | separate | 4 | 1 | 64 | 8.035 | 11.799 | 12.818 | 0.484 | 0.922 |
| planner+step_1+step_2+aggregator | separate | 4 | 0 | 64 | 5.706 | 11.333 | 13.058 | 0.607 | 0.859 |
| planner+step_1+step_2+aggregator | separate | 4 | 1 | 64 | 5.76 | 10.815 | 12.479 | 0.615 | 0.812 |

30 of 32 rows shown.

## math_phi/separate_k8

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 8 | 0 | 64 | 3.221 | 5.391 | 5.933 | 2.191 | 0.828 |
| all_small | separate | 8 | 1 | 64 | 3.214 | 4.774 | 6.151 | 2.212 | 0.812 |
| all_large | separate | 8 | 0 | 64 | 8.903 | 14.392 | 15.041 | 0.775 | 0.938 |
| all_large | separate | 8 | 1 | 64 | 9.123 | 14.313 | 14.938 | 0.788 | 0.938 |
| only_planner | separate | 8 | 0 | 64 | 3.727 | 5.963 | 6.468 | 1.93 | 0.844 |
| only_planner | separate | 8 | 1 | 64 | 3.729 | 5.982 | 6.51 | 1.951 | 0.859 |
| only_step_1 | separate | 8 | 0 | 64 | 4.623 | 7.706 | 8.427 | 1.569 | 0.828 |
| only_step_1 | separate | 8 | 1 | 64 | 4.536 | 6.457 | 7.212 | 1.618 | 0.797 |
| only_step_2 | separate | 8 | 0 | 64 | 3.886 | 5.903 | 6.181 | 1.789 | 0.766 |
| only_step_2 | separate | 8 | 1 | 64 | 3.861 | 5.699 | 5.846 | 1.905 | 0.812 |
| only_step_3 | separate | 8 | 0 | 64 | 4.03 | 6.316 | 6.839 | 1.706 | 0.812 |
| only_step_3 | separate | 8 | 1 | 64 | 4.046 | 6.059 | 6.308 | 1.765 | 0.781 |
| only_aggregator | separate | 8 | 0 | 64 | 3.911 | 8.455 | 8.67 | 1.64 | 0.859 |
| only_aggregator | separate | 8 | 1 | 64 | 3.934 | 7.527 | 8.447 | 1.609 | 0.859 |
| only_verifier | separate | 8 | 0 | 64 | 5.176 | 7.836 | 8.266 | 1.4 | 0.938 |
| only_verifier | separate | 8 | 1 | 64 | 5.279 | 7.716 | 8.091 | 1.44 | 0.922 |
| planner+step_1+step_2+aggregator+verifier | separate | 8 | 0 | 64 | 7.961 | 13.863 | 15.713 | 0.824 | 0.922 |
| planner+step_1+step_2+aggregator+verifier | separate | 8 | 1 | 64 | 7.993 | 13.86 | 16.629 | 0.816 | 0.922 |
| step_1+step_2+step_3 | separate | 8 | 0 | 64 | 5.839 | 8.374 | 9.569 | 1.236 | 0.766 |
| step_1+step_2+step_3 | separate | 8 | 1 | 64 | 5.797 | 8.507 | 9.567 | 1.265 | 0.844 |
| step_2+step_3+verifier | separate | 8 | 0 | 64 | 6.331 | 10.262 | 10.672 | 1.084 | 0.953 |
| step_2+step_3+verifier | separate | 8 | 1 | 64 | 6.307 | 9.927 | 11.075 | 1.095 | 0.953 |
| step_2+step_3 | separate | 8 | 0 | 64 | 4.777 | 7.188 | 8.766 | 1.447 | 0.797 |
| step_2+step_3 | separate | 8 | 1 | 64 | 4.494 | 7.892 | 8.11 | 1.495 | 0.781 |
| planner+step_1+aggregator | separate | 8 | 0 | 64 | 5.911 | 10.688 | 11.248 | 1.163 | 0.859 |
| planner+step_1+aggregator | separate | 8 | 1 | 64 | 5.783 | 11.196 | 11.703 | 1.154 | 0.828 |
| planner+step_1+step_3+verifier | separate | 8 | 0 | 64 | 8.091 | 11.997 | 13.52 | 0.895 | 0.922 |
| planner+step_1+step_3+verifier | separate | 8 | 1 | 64 | 8.042 | 11.948 | 13.683 | 0.874 | 0.922 |
| planner+step_1+step_2+aggregator | separate | 8 | 0 | 64 | 5.826 | 11.426 | 11.722 | 1.097 | 0.875 |
| planner+step_1+step_2+aggregator | separate | 8 | 1 | 64 | 6.035 | 11.466 | 12.473 | 1.094 | 0.812 |

30 of 32 rows shown.

## math_q15_7/separate_k1

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 1 | 0 | 32 | 1.113 | 1.73 | 2.121 | 0.896 | 0.562 |
| all_large | separate | 1 | 0 | 32 | 2.253 | 4.419 | 5.011 | 0.388 | 0.906 |
| only_verifier | separate | 1 | 0 | 32 | 1.979 | 2.85 | 2.875 | 0.49 | 0.719 |
| aggregator+verifier | separate | 1 | 0 | 32 | 2.335 | 3.789 | 4.52 | 0.424 | 0.875 |

## math_q15_7/separate_k32

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 32 | 0 | 64 | 1.477 | 3.091 | 3.39 | 13.28 | 0.531 |
| all_small | separate | 32 | 1 | 64 | 1.737 | 2.686 | 3.034 | 13.367 | 0.5 |
| all_large | separate | 32 | 0 | 64 | 2.78 | 5.252 | 5.617 | 5.268 | 0.828 |
| all_large | separate | 32 | 1 | 64 | 2.732 | 5.366 | 5.569 | 6.453 | 0.828 |
| only_planner | separate | 32 | 0 | 64 | 1.655 | 3.071 | 3.241 | 10.385 | 0.562 |
| only_planner | separate | 32 | 1 | 64 | 1.759 | 3.022 | 3.094 | 12.774 | 0.516 |
| only_step_1 | separate | 32 | 0 | 64 | 1.317 | 2.21 | 3.301 | 12.333 | 0.531 |
| only_step_1 | separate | 32 | 1 | 64 | 1.325 | 2.378 | 2.85 | 12.579 | 0.484 |
| only_step_2 | separate | 32 | 0 | 64 | 1.594 | 2.704 | 3.03 | 14.83 | 0.531 |
| only_step_2 | separate | 32 | 1 | 64 | 1.571 | 2.781 | 3.045 | 14.926 | 0.5 |
| only_step_3 | separate | 32 | 0 | 64 | 1.591 | 2.71 | 3.238 | 11.305 | 0.516 |
| only_step_3 | separate | 32 | 1 | 64 | 1.483 | 3.077 | 3.756 | 12.765 | 0.531 |
| only_aggregator | separate | 32 | 0 | 64 | 1.853 | 3.721 | 4.094 | 10.114 | 0.578 |
| only_aggregator | separate | 32 | 1 | 64 | 1.84 | 3.495 | 3.992 | 10.53 | 0.594 |
| only_verifier | separate | 32 | 0 | 64 | 2.634 | 3.922 | 4.265 | 8.665 | 0.828 |
| only_verifier | separate | 32 | 1 | 64 | 2.569 | 3.752 | 4.092 | 8.736 | 0.828 |
| planner+step_1+step_2+aggregator+verifier | separate | 32 | 0 | 64 | 2.799 | 4.91 | 5.478 | 7.287 | 0.859 |
| planner+step_1+step_2+aggregator+verifier | separate | 32 | 1 | 64 | 2.771 | 5.447 | 5.895 | 6.069 | 0.797 |
| step_1+step_2+step_3 | separate | 32 | 0 | 64 | 1.251 | 2.545 | 2.619 | 14.599 | 0.531 |
| step_1+step_2+step_3 | separate | 32 | 1 | 64 | 1.209 | 2.404 | 2.528 | 14.577 | 0.5 |
| step_2+step_3+verifier | separate | 32 | 0 | 64 | 2.582 | 4.073 | 4.425 | 9.565 | 0.828 |
| step_2+step_3+verifier | separate | 32 | 1 | 64 | 2.543 | 4.068 | 4.434 | 9.574 | 0.812 |
| step_2+step_3 | separate | 32 | 0 | 64 | 1.455 | 2.761 | 3.045 | 16 | 0.562 |
| step_2+step_3 | separate | 32 | 1 | 64 | 1.445 | 2.533 | 2.907 | 15.647 | 0.578 |
| planner+step_1+aggregator | separate | 32 | 0 | 64 | 1.697 | 3.574 | 3.748 | 8.167 | 0.625 |
| planner+step_1+aggregator | separate | 32 | 1 | 64 | 1.672 | 3.393 | 3.737 | 10.344 | 0.609 |
| planner+step_1+step_3+verifier | separate | 32 | 0 | 64 | 2.638 | 4.631 | 5.017 | 7.18 | 0.781 |
| planner+step_1+step_3+verifier | separate | 32 | 1 | 64 | 2.857 | 4.647 | 5.026 | 6.786 | 0.766 |
| planner+step_1+step_2+aggregator | separate | 32 | 0 | 64 | 1.814 | 3.445 | 3.884 | 10.373 | 0.672 |
| planner+step_1+step_2+aggregator | separate | 32 | 1 | 64 | 1.785 | 3.464 | 3.892 | 10.24 | 0.672 |

30 of 32 rows shown.

## math_q15_7/separate_k4

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 4 | 0 | 64 | 1.151 | 2.237 | 2.681 | 3.141 | 0.516 |
| all_small | separate | 4 | 1 | 64 | 1.177 | 2.073 | 2.145 | 3.189 | 0.562 |
| all_large | separate | 4 | 0 | 64 | 2.595 | 4.918 | 5.129 | 1.381 | 0.875 |
| all_large | separate | 4 | 1 | 64 | 2.482 | 4.776 | 5.242 | 1.377 | 0.875 |
| only_planner | separate | 4 | 0 | 64 | 1.384 | 2.43 | 2.783 | 2.597 | 0.547 |
| only_planner | separate | 4 | 1 | 64 | 1.37 | 2.302 | 2.452 | 2.714 | 0.531 |
| only_step_1 | separate | 4 | 0 | 64 | 0.993 | 1.725 | 1.98 | 3.563 | 0.547 |
| only_step_1 | separate | 4 | 1 | 64 | 1.027 | 1.823 | 1.99 | 3.473 | 0.562 |
| only_step_2 | separate | 4 | 0 | 64 | 1.254 | 2.29 | 2.658 | 3.021 | 0.453 |
| only_step_2 | separate | 4 | 1 | 64 | 1.241 | 2.297 | 2.544 | 3.086 | 0.516 |
| only_step_3 | separate | 4 | 0 | 64 | 1.21 | 2.168 | 2.272 | 3.07 | 0.516 |
| only_step_3 | separate | 4 | 1 | 64 | 1.212 | 2.246 | 2.282 | 3.051 | 0.531 |
| only_aggregator | separate | 4 | 0 | 64 | 1.431 | 2.905 | 3.239 | 2.494 | 0.562 |
| only_aggregator | separate | 4 | 1 | 64 | 1.431 | 2.892 | 3.644 | 2.469 | 0.625 |
| only_verifier | separate | 4 | 0 | 64 | 2.297 | 3.036 | 3.215 | 1.765 | 0.734 |
| only_verifier | separate | 4 | 1 | 64 | 2.294 | 3.035 | 3.547 | 1.757 | 0.797 |
| planner+step_1+step_2+aggregator+verifier | separate | 4 | 0 | 64 | 2.558 | 5.011 | 5.482 | 1.422 | 0.844 |
| planner+step_1+step_2+aggregator+verifier | separate | 4 | 1 | 64 | 2.564 | 4.846 | 5.06 | 1.413 | 0.859 |
| step_1+step_2+step_3 | separate | 4 | 0 | 64 | 1.063 | 2.347 | 2.617 | 3.288 | 0.562 |
| step_1+step_2+step_3 | separate | 4 | 1 | 64 | 1.069 | 2.35 | 2.619 | 3.303 | 0.594 |
| step_2+step_3+verifier | separate | 4 | 0 | 64 | 2.359 | 3.462 | 3.804 | 1.669 | 0.828 |
| step_2+step_3+verifier | separate | 4 | 1 | 64 | 2.273 | 3.466 | 3.802 | 1.67 | 0.781 |
| step_2+step_3 | separate | 4 | 0 | 64 | 1.174 | 2.587 | 2.741 | 3.043 | 0.594 |
| step_2+step_3 | separate | 4 | 1 | 64 | 1.155 | 2.401 | 2.727 | 3.087 | 0.578 |
| planner+step_1+aggregator | separate | 4 | 0 | 64 | 1.52 | 3.397 | 3.734 | 2.16 | 0.641 |
| planner+step_1+aggregator | separate | 4 | 1 | 64 | 1.641 | 3.111 | 3.426 | 2.291 | 0.641 |
| planner+step_1+step_3+verifier | separate | 4 | 0 | 64 | 2.433 | 4.287 | 4.591 | 1.541 | 0.781 |
| planner+step_1+step_3+verifier | separate | 4 | 1 | 64 | 2.436 | 4.311 | 4.579 | 1.552 | 0.797 |
| planner+step_1+step_2+aggregator | separate | 4 | 0 | 64 | 1.639 | 3.368 | 4.498 | 1.98 | 0.656 |
| planner+step_1+step_2+aggregator | separate | 4 | 1 | 64 | 1.647 | 3.466 | 4.629 | 2.018 | 0.656 |

30 of 32 rows shown.

## math_q15_7/separate_k8

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 8 | 0 | 64 | 1.229 | 1.986 | 2.373 | 5.948 | 0.516 |
| all_small | separate | 8 | 1 | 64 | 1.238 | 2.002 | 2.358 | 5.918 | 0.516 |
| all_large | separate | 8 | 0 | 64 | 2.604 | 4.811 | 5.15 | 2.435 | 0.812 |
| all_large | separate | 8 | 1 | 64 | 2.549 | 4.684 | 5.323 | 2.673 | 0.812 |
| only_planner | separate | 8 | 0 | 64 | 1.417 | 2.53 | 2.625 | 5.006 | 0.516 |
| only_planner | separate | 8 | 1 | 64 | 1.43 | 2.554 | 2.611 | 5.035 | 0.516 |
| only_step_1 | separate | 8 | 0 | 64 | 1.077 | 1.97 | 2.077 | 5.786 | 0.516 |
| only_step_1 | separate | 8 | 1 | 64 | 1.087 | 2.046 | 2.118 | 5.805 | 0.5 |
| only_step_2 | separate | 8 | 0 | 64 | 1.316 | 2.4 | 2.592 | 5.636 | 0.484 |
| only_step_2 | separate | 8 | 1 | 64 | 1.321 | 2.401 | 2.597 | 5.627 | 0.5 |
| only_step_3 | separate | 8 | 0 | 64 | 1.257 | 2.35 | 2.361 | 5.802 | 0.5 |
| only_step_3 | separate | 8 | 1 | 64 | 1.254 | 2.349 | 2.36 | 5.783 | 0.5 |
| only_aggregator | separate | 8 | 0 | 64 | 1.512 | 2.956 | 3.367 | 4.649 | 0.609 |
| only_aggregator | separate | 8 | 1 | 64 | 1.512 | 2.966 | 3.703 | 4.646 | 0.609 |
| only_verifier | separate | 8 | 0 | 64 | 2.362 | 3.082 | 3.591 | 3.37 | 0.781 |
| only_verifier | separate | 8 | 1 | 64 | 2.33 | 3.055 | 3.599 | 3.349 | 0.781 |
| planner+step_1+step_2+aggregator+verifier | separate | 8 | 0 | 64 | 2.595 | 4.59 | 5.106 | 2.703 | 0.828 |
| planner+step_1+step_2+aggregator+verifier | separate | 8 | 1 | 64 | 2.537 | 4.542 | 5.105 | 2.759 | 0.844 |
| step_1+step_2+step_3 | separate | 8 | 0 | 64 | 1.124 | 2.378 | 2.7 | 5.977 | 0.562 |
| step_1+step_2+step_3 | separate | 8 | 1 | 64 | 1.113 | 2.368 | 2.695 | 5.983 | 0.547 |
| step_2+step_3+verifier | separate | 8 | 0 | 64 | 2.301 | 3.516 | 3.864 | 3.16 | 0.812 |
| step_2+step_3+verifier | separate | 8 | 1 | 64 | 2.386 | 3.546 | 3.865 | 3.149 | 0.828 |
| step_2+step_3 | separate | 8 | 0 | 64 | 1.214 | 2.509 | 2.757 | 5.691 | 0.578 |
| step_2+step_3 | separate | 8 | 1 | 64 | 1.22 | 2.504 | 2.745 | 5.663 | 0.578 |
| planner+step_1+aggregator | separate | 8 | 0 | 64 | 1.665 | 3.218 | 3.585 | 4.058 | 0.609 |
| planner+step_1+aggregator | separate | 8 | 1 | 64 | 1.697 | 3.393 | 3.613 | 3.966 | 0.609 |
| planner+step_1+step_3+verifier | separate | 8 | 0 | 64 | 2.577 | 4.309 | 4.707 | 2.73 | 0.797 |
| planner+step_1+step_3+verifier | separate | 8 | 1 | 64 | 2.573 | 4.384 | 4.754 | 2.759 | 0.781 |
| planner+step_1+step_2+aggregator | separate | 8 | 0 | 64 | 1.662 | 3.494 | 4.655 | 3.518 | 0.688 |
| planner+step_1+step_2+aggregator | separate | 8 | 1 | 64 | 1.657 | 3.401 | 4.584 | 3.69 | 0.656 |

30 of 32 rows shown.

## math_q15_7/shared_k1

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 1 | 0 | 32 | 0.882 | 1.701 | 2.785 | 0.93 | 0.594 |
| all_large | shared | 1 | 0 | 32 | 2.406 | 4.353 | 4.937 | 0.389 | 0.906 |
| only_verifier | shared | 1 | 0 | 32 | 1.98 | 2.78 | 4.046 | 0.496 | 0.75 |
| aggregator+verifier | shared | 1 | 0 | 32 | 2.187 | 3.999 | 4.149 | 0.435 | 0.906 |

## math_q15_7/shared_k32

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 32 | 0 | 64 | 1.481 | 2.351 | 2.903 | 14.79 | 0.531 |
| all_small | shared | 32 | 1 | 64 | 1.411 | 2.575 | 3.705 | 13.291 | 0.531 |
| all_large | shared | 32 | 0 | 64 | 2.718 | 5.068 | 5.608 | 6.503 | 0.828 |
| all_large | shared | 32 | 1 | 64 | 2.797 | 5.216 | 5.527 | 5.662 | 0.844 |
| only_planner | shared | 32 | 0 | 64 | 3.3 | 7.419 | 7.62 | 7.126 | 0.5 |
| only_planner | shared | 32 | 1 | 64 | 3.497 | 6.73 | 7.629 | 7.017 | 0.531 |
| only_step_1 | shared | 32 | 0 | 64 | 2.795 | 5.895 | 6.231 | 7.055 | 0.5 |
| only_step_1 | shared | 32 | 1 | 64 | 2.988 | 5.592 | 5.627 | 8.517 | 0.5 |
| only_step_2 | shared | 32 | 0 | 64 | 2.989 | 5.637 | 6.281 | 7.385 | 0.531 |
| only_step_2 | shared | 32 | 1 | 64 | 2.936 | 5.195 | 5.68 | 8.181 | 0.531 |
| only_step_3 | shared | 32 | 0 | 64 | 3.258 | 6.341 | 7.66 | 6.221 | 0.547 |
| only_step_3 | shared | 32 | 1 | 64 | 3.297 | 5.877 | 6.35 | 7.334 | 0.594 |
| only_aggregator | shared | 32 | 0 | 64 | 4.287 | 7.441 | 8.513 | 4.65 | 0.562 |
| only_aggregator | shared | 32 | 1 | 64 | 4.31 | 7.488 | 7.935 | 5.027 | 0.594 |
| only_verifier | shared | 32 | 0 | 64 | 5.174 | 8.038 | 9.091 | 4.597 | 0.766 |
| only_verifier | shared | 32 | 1 | 64 | 5.135 | 7.874 | 8.968 | 5.052 | 0.766 |
| planner+step_1+step_2+aggregator+verifier | shared | 32 | 0 | 64 | 4.782 | 8.447 | 9.673 | 4.17 | 0.797 |
| planner+step_1+step_2+aggregator+verifier | shared | 32 | 1 | 64 | 5.052 | 8.858 | 10.013 | 4.24 | 0.844 |
| step_1+step_2+step_3 | shared | 32 | 0 | 64 | 2.668 | 4.973 | 5.855 | 7.391 | 0.562 |
| step_1+step_2+step_3 | shared | 32 | 1 | 64 | 2.679 | 5.889 | 6.182 | 7.161 | 0.5 |
| step_2+step_3+verifier | shared | 32 | 0 | 64 | 4.748 | 7.3 | 7.563 | 5.379 | 0.828 |
| step_2+step_3+verifier | shared | 32 | 1 | 64 | 4.738 | 7.455 | 7.597 | 5.489 | 0.828 |
| step_2+step_3 | shared | 32 | 0 | 64 | 3.547 | 6.892 | 7.63 | 5.822 | 0.609 |
| step_2+step_3 | shared | 32 | 1 | 64 | 2.983 | 5.974 | 6.676 | 8.013 | 0.562 |
| planner+step_1+aggregator | shared | 32 | 0 | 64 | 3.291 | 7.047 | 7.275 | 5.216 | 0.594 |
| planner+step_1+aggregator | shared | 32 | 1 | 64 | 3.417 | 7.087 | 7.351 | 5.249 | 0.625 |
| planner+step_1+step_3+verifier | shared | 32 | 0 | 64 | 4.716 | 8.29 | 8.851 | 5.25 | 0.828 |
| planner+step_1+step_3+verifier | shared | 32 | 1 | 64 | 5.279 | 8.908 | 9.367 | 4.452 | 0.797 |
| planner+step_1+step_2+aggregator | shared | 32 | 0 | 64 | 3.679 | 6.879 | 7.539 | 5.038 | 0.656 |
| planner+step_1+step_2+aggregator | shared | 32 | 1 | 64 | 3.638 | 7.011 | 8.08 | 4.812 | 0.641 |

30 of 32 rows shown.

## math_q15_7/shared_k4

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 4 | 0 | 64 | 1.216 | 2.216 | 2.546 | 3.072 | 0.484 |
| all_small | shared | 4 | 1 | 64 | 1.144 | 2.209 | 2.496 | 3.187 | 0.5 |
| all_large | shared | 4 | 0 | 64 | 2.513 | 4.759 | 5.061 | 1.366 | 0.844 |
| all_large | shared | 4 | 1 | 64 | 2.564 | 4.622 | 4.921 | 1.411 | 0.844 |
| only_planner | shared | 4 | 0 | 64 | 2.59 | 4.793 | 5.058 | 1.443 | 0.484 |
| only_planner | shared | 4 | 1 | 64 | 2.542 | 4.885 | 5.903 | 1.412 | 0.484 |
| only_step_1 | shared | 4 | 0 | 64 | 1.338 | 2.743 | 3.771 | 2.525 | 0.578 |
| only_step_1 | shared | 4 | 1 | 64 | 1.439 | 2.887 | 3.943 | 2.453 | 0.547 |
| only_step_2 | shared | 4 | 0 | 64 | 1.701 | 3.336 | 3.371 | 2.177 | 0.5 |
| only_step_2 | shared | 4 | 1 | 64 | 1.708 | 3.002 | 3.809 | 2.166 | 0.516 |
| only_step_3 | shared | 4 | 0 | 64 | 1.785 | 3.607 | 3.919 | 2.037 | 0.516 |
| only_step_3 | shared | 4 | 1 | 64 | 1.639 | 3.575 | 4.123 | 2.032 | 0.516 |
| only_aggregator | shared | 4 | 0 | 64 | 2.771 | 6.361 | 7.014 | 1.34 | 0.562 |
| only_aggregator | shared | 4 | 1 | 64 | 2.719 | 6.364 | 8.327 | 1.311 | 0.578 |
| only_verifier | shared | 4 | 0 | 64 | 4.9 | 7.143 | 7.904 | 0.842 | 0.766 |
| only_verifier | shared | 4 | 1 | 64 | 4.613 | 6.8 | 8.385 | 0.858 | 0.797 |
| planner+step_1+step_2+aggregator+verifier | shared | 4 | 0 | 64 | 2.786 | 5.191 | 5.48 | 1.251 | 0.859 |
| planner+step_1+step_2+aggregator+verifier | shared | 4 | 1 | 64 | 2.756 | 5.197 | 5.388 | 1.245 | 0.844 |
| step_1+step_2+step_3 | shared | 4 | 0 | 64 | 1.854 | 4.266 | 5.336 | 1.751 | 0.594 |
| step_1+step_2+step_3 | shared | 4 | 1 | 64 | 1.796 | 4.337 | 5.279 | 1.785 | 0.609 |
| step_2+step_3+verifier | shared | 4 | 0 | 64 | 4.126 | 6.505 | 7.217 | 0.924 | 0.812 |
| step_2+step_3+verifier | shared | 4 | 1 | 64 | 4.192 | 6.673 | 6.822 | 0.926 | 0.797 |
| step_2+step_3 | shared | 4 | 0 | 64 | 2.111 | 5.583 | 6.665 | 1.589 | 0.547 |
| step_2+step_3 | shared | 4 | 1 | 64 | 2.2 | 5.138 | 5.399 | 1.644 | 0.547 |
| planner+step_1+aggregator | shared | 4 | 0 | 64 | 3.241 | 6.446 | 7.118 | 1.123 | 0.609 |
| planner+step_1+aggregator | shared | 4 | 1 | 64 | 3.24 | 6.407 | 7.327 | 1.134 | 0.625 |
| planner+step_1+step_3+verifier | shared | 4 | 0 | 64 | 3.272 | 5.915 | 6.228 | 1.145 | 0.781 |
| planner+step_1+step_3+verifier | shared | 4 | 1 | 64 | 3.289 | 5.959 | 6.376 | 1.138 | 0.797 |
| planner+step_1+step_2+aggregator | shared | 4 | 0 | 64 | 3.093 | 5.377 | 6.616 | 1.192 | 0.641 |
| planner+step_1+step_2+aggregator | shared | 4 | 1 | 64 | 3.165 | 6.203 | 7.888 | 1.104 | 0.625 |

30 of 32 rows shown.

## math_q15_7/shared_k8

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 8 | 0 | 64 | 1.158 | 1.967 | 2.634 | 6.299 | 0.516 |
| all_small | shared | 8 | 1 | 64 | 1.15 | 1.958 | 2.627 | 6.297 | 0.516 |
| all_large | shared | 8 | 0 | 64 | 2.517 | 4.723 | 5.09 | 2.522 | 0.844 |
| all_large | shared | 8 | 1 | 64 | 2.569 | 4.681 | 5.091 | 2.605 | 0.828 |
| only_planner | shared | 8 | 0 | 64 | 2.948 | 5.961 | 6.987 | 2.318 | 0.5 |
| only_planner | shared | 8 | 1 | 64 | 2.966 | 5.937 | 6.858 | 2.446 | 0.484 |
| only_step_1 | shared | 8 | 0 | 64 | 1.937 | 3.873 | 4.048 | 3.501 | 0.531 |
| only_step_1 | shared | 8 | 1 | 64 | 1.993 | 3.767 | 3.961 | 3.561 | 0.531 |
| only_step_2 | shared | 8 | 0 | 64 | 2.11 | 4.081 | 5.476 | 3.464 | 0.531 |
| only_step_2 | shared | 8 | 1 | 64 | 2.125 | 4.124 | 5.472 | 3.486 | 0.531 |
| only_step_3 | shared | 8 | 0 | 64 | 2.529 | 4.486 | 6.105 | 2.971 | 0.516 |
| only_step_3 | shared | 8 | 1 | 64 | 2.493 | 4.509 | 6.15 | 2.969 | 0.516 |
| only_aggregator | shared | 8 | 0 | 64 | 3.256 | 6.375 | 7.283 | 2.252 | 0.547 |
| only_aggregator | shared | 8 | 1 | 64 | 3.341 | 6.712 | 8.628 | 2.177 | 0.594 |
| only_verifier | shared | 8 | 0 | 64 | 5.182 | 7.232 | 9.113 | 1.561 | 0.781 |
| only_verifier | shared | 8 | 1 | 64 | 4.997 | 7.306 | 9.154 | 1.565 | 0.797 |
| planner+step_1+step_2+aggregator+verifier | shared | 8 | 0 | 64 | 3.439 | 6.106 | 6.804 | 2.031 | 0.859 |
| planner+step_1+step_2+aggregator+verifier | shared | 8 | 1 | 64 | 3.029 | 5.662 | 6.145 | 2.188 | 0.875 |
| step_1+step_2+step_3 | shared | 8 | 0 | 64 | 2.125 | 4.663 | 5.59 | 2.841 | 0.594 |
| step_1+step_2+step_3 | shared | 8 | 1 | 64 | 2.208 | 4.36 | 5.611 | 2.883 | 0.594 |
| step_2+step_3+verifier | shared | 8 | 0 | 64 | 4.652 | 7.523 | 8.165 | 1.648 | 0.844 |
| step_2+step_3+verifier | shared | 8 | 1 | 64 | 4.579 | 7.487 | 8.133 | 1.647 | 0.859 |
| step_2+step_3 | shared | 8 | 0 | 64 | 2.591 | 5.194 | 5.527 | 2.691 | 0.562 |
| step_2+step_3 | shared | 8 | 1 | 64 | 2.622 | 5.218 | 5.638 | 2.67 | 0.578 |
| planner+step_1+aggregator | shared | 8 | 0 | 64 | 3.391 | 6.775 | 6.832 | 2.001 | 0.625 |
| planner+step_1+aggregator | shared | 8 | 1 | 64 | 3.452 | 6.544 | 6.807 | 2.015 | 0.641 |
| planner+step_1+step_3+verifier | shared | 8 | 0 | 64 | 4.014 | 7.304 | 8.482 | 1.745 | 0.828 |
| planner+step_1+step_3+verifier | shared | 8 | 1 | 64 | 3.986 | 7.279 | 7.341 | 1.801 | 0.859 |
| planner+step_1+step_2+aggregator | shared | 8 | 0 | 64 | 3.381 | 7.079 | 7.868 | 1.909 | 0.672 |
| planner+step_1+step_2+aggregator | shared | 8 | 1 | 64 | 3.362 | 6.656 | 8.076 | 2.058 | 0.672 |

30 of 32 rows shown.

## math_q15_7/shared_mps_k32

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared_mps | 32 | 0 | 64 | 1.501 | 3.101 | 3.16 | 13.634 | 0.5 |
| all_small | shared_mps | 32 | 1 | 64 | 1.508 | 3.149 | 3.378 | 13.941 | 0.516 |
| all_large | shared_mps | 32 | 0 | 64 | 2.879 | 5.541 | 5.829 | 5.237 | 0.844 |
| all_large | shared_mps | 32 | 1 | 64 | 2.892 | 5.448 | 5.938 | 5.597 | 0.859 |
| only_planner | shared_mps | 32 | 0 | 64 | 2.702 | 5.531 | 5.804 | 8.734 | 0.516 |
| only_planner | shared_mps | 32 | 1 | 64 | 2.72 | 4.913 | 5.528 | 9.06 | 0.531 |
| only_step_1 | shared_mps | 32 | 0 | 64 | 2.341 | 4.564 | 4.762 | 8.202 | 0.516 |
| only_step_1 | shared_mps | 32 | 1 | 64 | 2.378 | 4.281 | 5.228 | 8.693 | 0.484 |
| only_step_2 | shared_mps | 32 | 0 | 64 | 2.419 | 4.827 | 5.107 | 9.276 | 0.594 |
| only_step_2 | shared_mps | 32 | 1 | 64 | 2.677 | 4.94 | 5.825 | 8.171 | 0.547 |
| only_step_3 | shared_mps | 32 | 0 | 64 | 2.795 | 5.184 | 7.909 | 6.393 | 0.5 |
| only_step_3 | shared_mps | 32 | 1 | 64 | 2.693 | 5.606 | 5.947 | 8.058 | 0.5 |
| only_aggregator | shared_mps | 32 | 0 | 64 | 3.516 | 6.23 | 6.844 | 5.781 | 0.594 |
| only_aggregator | shared_mps | 32 | 1 | 64 | 3.575 | 5.82 | 6.666 | 6.573 | 0.578 |
| only_verifier | shared_mps | 32 | 0 | 64 | 3.904 | 6.229 | 7.25 | 5.038 | 0.797 |
| only_verifier | shared_mps | 32 | 1 | 64 | 3.935 | 6.778 | 7.843 | 5.07 | 0.797 |
| planner+step_1+step_2+aggregator+verifier | shared_mps | 32 | 0 | 64 | 3.352 | 6.143 | 6.805 | 6.202 | 0.844 |
| planner+step_1+step_2+aggregator+verifier | shared_mps | 32 | 1 | 64 | 3.467 | 6.761 | 6.913 | 5.476 | 0.828 |
| step_1+step_2+step_3 | shared_mps | 32 | 0 | 64 | 2.198 | 4.541 | 4.701 | 9.039 | 0.578 |
| step_1+step_2+step_3 | shared_mps | 32 | 1 | 64 | 2.39 | 4.4 | 5.732 | 9.368 | 0.547 |
| step_2+step_3+verifier | shared_mps | 32 | 0 | 64 | 3.795 | 5.721 | 6.237 | 6.357 | 0.828 |
| step_2+step_3+verifier | shared_mps | 32 | 1 | 64 | 3.81 | 6.054 | 6.286 | 6.526 | 0.828 |
| step_2+step_3 | shared_mps | 32 | 0 | 64 | 2.516 | 4.992 | 5.201 | 9.234 | 0.594 |
| step_2+step_3 | shared_mps | 32 | 1 | 64 | 2.5 | 5.227 | 5.43 | 8.921 | 0.594 |
| planner+step_1+aggregator | shared_mps | 32 | 0 | 64 | 2.772 | 5.608 | 5.811 | 7.577 | 0.625 |
| planner+step_1+aggregator | shared_mps | 32 | 1 | 64 | 2.883 | 5.614 | 6.192 | 7.715 | 0.625 |
| planner+step_1+step_3+verifier | shared_mps | 32 | 0 | 64 | 3.575 | 6.065 | 6.204 | 5.863 | 0.812 |
| planner+step_1+step_3+verifier | shared_mps | 32 | 1 | 64 | 3.55 | 6.061 | 6.317 | 5.646 | 0.781 |
| planner+step_1+step_2+aggregator | shared_mps | 32 | 0 | 64 | 2.75 | 5.578 | 6.412 | 6.19 | 0.656 |
| planner+step_1+step_2+aggregator | shared_mps | 32 | 1 | 64 | 2.674 | 4.912 | 6.064 | 6.41 | 0.641 |

30 of 32 rows shown.

## math_q15_7/shared_mps_k4

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared_mps | 4 | 0 | 64 | 1.222 | 2.276 | 2.679 | 2.998 | 0.531 |
| all_small | shared_mps | 4 | 1 | 64 | 1.223 | 2.172 | 2.728 | 2.987 | 0.547 |
| all_large | shared_mps | 4 | 0 | 64 | 2.627 | 5.077 | 5.311 | 1.333 | 0.844 |
| all_large | shared_mps | 4 | 1 | 64 | 2.67 | 4.803 | 5.281 | 1.337 | 0.844 |
| only_planner | shared_mps | 4 | 0 | 64 | 2.039 | 4.074 | 5.026 | 1.673 | 0.5 |
| only_planner | shared_mps | 4 | 1 | 64 | 1.965 | 4.235 | 4.458 | 1.718 | 0.469 |
| only_step_1 | shared_mps | 4 | 0 | 64 | 1.333 | 2.476 | 3.086 | 2.733 | 0.5 |
| only_step_1 | shared_mps | 4 | 1 | 64 | 1.309 | 2.577 | 3.229 | 2.664 | 0.547 |
| only_step_2 | shared_mps | 4 | 0 | 64 | 1.671 | 2.987 | 3.141 | 2.339 | 0.453 |
| only_step_2 | shared_mps | 4 | 1 | 64 | 1.569 | 2.91 | 3.224 | 2.338 | 0.5 |
| only_step_3 | shared_mps | 4 | 0 | 64 | 1.592 | 3.09 | 3.9 | 2.239 | 0.531 |
| only_step_3 | shared_mps | 4 | 1 | 64 | 1.589 | 3.064 | 3.427 | 2.236 | 0.531 |
| only_aggregator | shared_mps | 4 | 0 | 64 | 2.32 | 4.965 | 6.288 | 1.517 | 0.578 |
| only_aggregator | shared_mps | 4 | 1 | 64 | 2.371 | 4.815 | 6.594 | 1.521 | 0.594 |
| only_verifier | shared_mps | 4 | 0 | 64 | 3.731 | 5.696 | 6.284 | 1.051 | 0.797 |
| only_verifier | shared_mps | 4 | 1 | 64 | 3.745 | 5.713 | 6.629 | 1.045 | 0.797 |
| planner+step_1+step_2+aggregator+verifier | shared_mps | 4 | 0 | 64 | 2.889 | 4.909 | 5.413 | 1.247 | 0.859 |
| planner+step_1+step_2+aggregator+verifier | shared_mps | 4 | 1 | 64 | 2.687 | 5.242 | 5.422 | 1.275 | 0.891 |
| step_1+step_2+step_3 | shared_mps | 4 | 0 | 64 | 1.598 | 4.018 | 4.266 | 2.022 | 0.594 |
| step_1+step_2+step_3 | shared_mps | 4 | 1 | 64 | 1.742 | 3.962 | 4.391 | 2.026 | 0.578 |
| step_2+step_3+verifier | shared_mps | 4 | 0 | 64 | 3.458 | 5.245 | 5.809 | 1.123 | 0.797 |
| step_2+step_3+verifier | shared_mps | 4 | 1 | 64 | 3.401 | 5.234 | 5.803 | 1.127 | 0.781 |
| step_2+step_3 | shared_mps | 4 | 0 | 64 | 1.759 | 3.622 | 3.998 | 2.028 | 0.609 |
| step_2+step_3 | shared_mps | 4 | 1 | 64 | 1.843 | 3.775 | 4.499 | 1.999 | 0.578 |
| planner+step_1+aggregator | shared_mps | 4 | 0 | 64 | 2.405 | 4.972 | 5.703 | 1.416 | 0.641 |
| planner+step_1+aggregator | shared_mps | 4 | 1 | 64 | 2.612 | 5.082 | 5.735 | 1.348 | 0.656 |
| planner+step_1+step_3+verifier | shared_mps | 4 | 0 | 64 | 3.08 | 5.401 | 5.769 | 1.195 | 0.797 |
| planner+step_1+step_3+verifier | shared_mps | 4 | 1 | 64 | 3.113 | 5.084 | 7.119 | 1.191 | 0.75 |
| planner+step_1+step_2+aggregator | shared_mps | 4 | 0 | 64 | 2.435 | 4.625 | 4.865 | 1.453 | 0.656 |
| planner+step_1+step_2+aggregator | shared_mps | 4 | 1 | 64 | 2.564 | 4.4 | 5.283 | 1.432 | 0.656 |

30 of 32 rows shown.

## math_q15_7/shared_mps_k8

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared_mps | 8 | 0 | 64 | 1.253 | 2.232 | 2.275 | 5.653 | 0.547 |
| all_small | shared_mps | 8 | 1 | 64 | 1.261 | 2.168 | 2.261 | 5.691 | 0.531 |
| all_large | shared_mps | 8 | 0 | 64 | 2.691 | 4.933 | 5.314 | 2.274 | 0.812 |
| all_large | shared_mps | 8 | 1 | 64 | 2.735 | 4.654 | 4.959 | 2.635 | 0.844 |
| only_planner | shared_mps | 8 | 0 | 64 | 2.337 | 4.699 | 5.347 | 2.885 | 0.484 |
| only_planner | shared_mps | 8 | 1 | 64 | 2.324 | 4.965 | 5.766 | 2.695 | 0.516 |
| only_step_1 | shared_mps | 8 | 0 | 64 | 1.719 | 3.301 | 3.323 | 4.099 | 0.516 |
| only_step_1 | shared_mps | 8 | 1 | 64 | 1.677 | 3.303 | 3.359 | 4.112 | 0.547 |
| only_step_2 | shared_mps | 8 | 0 | 64 | 1.857 | 3.724 | 4.572 | 3.827 | 0.516 |
| only_step_2 | shared_mps | 8 | 1 | 64 | 1.877 | 3.703 | 4.574 | 3.838 | 0.516 |
| only_step_3 | shared_mps | 8 | 0 | 64 | 1.936 | 3.604 | 4.004 | 3.557 | 0.531 |
| only_step_3 | shared_mps | 8 | 1 | 64 | 1.908 | 3.531 | 4.039 | 3.576 | 0.531 |
| only_aggregator | shared_mps | 8 | 0 | 64 | 2.964 | 5.094 | 7.046 | 2.446 | 0.594 |
| only_aggregator | shared_mps | 8 | 1 | 64 | 2.877 | 5.063 | 6.959 | 2.442 | 0.578 |
| only_verifier | shared_mps | 8 | 0 | 64 | 4.027 | 5.952 | 6.995 | 1.906 | 0.797 |
| only_verifier | shared_mps | 8 | 1 | 64 | 4.045 | 5.964 | 7.006 | 1.903 | 0.781 |
| planner+step_1+step_2+aggregator+verifier | shared_mps | 8 | 0 | 64 | 2.91 | 5.609 | 5.936 | 2.208 | 0.812 |
| planner+step_1+step_2+aggregator+verifier | shared_mps | 8 | 1 | 64 | 2.873 | 5.251 | 5.795 | 2.202 | 0.844 |
| step_1+step_2+step_3 | shared_mps | 8 | 0 | 64 | 2.023 | 4.54 | 4.685 | 3.285 | 0.578 |
| step_1+step_2+step_3 | shared_mps | 8 | 1 | 64 | 2.021 | 4.558 | 4.721 | 3.307 | 0.594 |
| step_2+step_3+verifier | shared_mps | 8 | 0 | 64 | 3.663 | 5.419 | 6.064 | 2.041 | 0.812 |
| step_2+step_3+verifier | shared_mps | 8 | 1 | 64 | 3.651 | 5.425 | 6.072 | 2.051 | 0.797 |
| step_2+step_3 | shared_mps | 8 | 0 | 64 | 2.123 | 3.944 | 4.35 | 3.24 | 0.578 |
| step_2+step_3 | shared_mps | 8 | 1 | 64 | 2.122 | 3.933 | 4.324 | 3.247 | 0.578 |
| planner+step_1+aggregator | shared_mps | 8 | 0 | 64 | 2.643 | 5.382 | 6.104 | 2.648 | 0.625 |
| planner+step_1+aggregator | shared_mps | 8 | 1 | 64 | 2.71 | 5.371 | 5.944 | 2.382 | 0.578 |
| planner+step_1+step_3+verifier | shared_mps | 8 | 0 | 64 | 3.182 | 5.58 | 6.01 | 2.194 | 0.812 |
| planner+step_1+step_3+verifier | shared_mps | 8 | 1 | 64 | 3.236 | 5.654 | 6.043 | 2.174 | 0.812 |
| planner+step_1+step_2+aggregator | shared_mps | 8 | 0 | 64 | 2.676 | 5.376 | 6.313 | 2.407 | 0.672 |
| planner+step_1+step_2+aggregator | shared_mps | 8 | 1 | 64 | 2.664 | 4.706 | 5.021 | 2.641 | 0.672 |

30 of 32 rows shown.
