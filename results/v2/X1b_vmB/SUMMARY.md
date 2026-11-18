# Phase X1b

Generated 2026-11-18 00:04 UTC, backend `vllm`.

Code run: `c1bb8338fa64acd82d82f1eb0c5a5ce6cb7b019b`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| math_granite/shared_k32 | finished |
| math_granite/shared_k4 | finished |
| math_granite/shared_k8 | finished |
| math_phi/shared_k32 | finished |
| math_phi/shared_k4 | finished |
| math_phi/shared_k8 | finished |
| math_phi/superseded_server_swap_2109Z/shared_k8 | UNFINISHED |

## math_granite/shared_k32

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 32 | 0 | 64 | 2.311 | 3.872 | 4.157 | 9.369 | 0.547 |
| all_small | shared | 32 | 1 | 64 | 2.245 | 3.689 | 3.774 | 9.004 | 0.625 |
| all_large | shared | 32 | 0 | 64 | 4.636 | 8.9 | 9.365 | 4.138 | 0.75 |
| all_large | shared | 32 | 1 | 64 | 4.639 | 7.668 | 8.454 | 4.345 | 0.781 |
| only_planner | shared | 32 | 0 | 64 | 5.831 | 9.859 | 10.705 | 4.334 | 0.594 |
| only_planner | shared | 32 | 1 | 64 | 6.223 | 10.945 | 11.097 | 3.396 | 0.547 |
| only_step_1 | shared | 32 | 0 | 64 | 5.27 | 8.73 | 9.644 | 4.227 | 0.594 |
| only_step_1 | shared | 32 | 1 | 64 | 5.269 | 7.887 | 8.719 | 4.185 | 0.531 |
| only_step_2 | shared | 32 | 0 | 64 | 6.021 | 10.033 | 11.509 | 4.028 | 0.609 |
| only_step_2 | shared | 32 | 1 | 64 | 5.298 | 10.128 | 10.846 | 3.504 | 0.484 |
| only_step_3 | shared | 32 | 0 | 64 | 5.63 | 10.413 | 10.771 | 3.93 | 0.469 |
| only_step_3 | shared | 32 | 1 | 64 | 5.556 | 11.328 | 12.295 | 3.775 | 0.531 |
| only_aggregator | shared | 32 | 0 | 64 | 6.556 | 12.058 | 12.449 | 2.984 | 0.547 |
| only_aggregator | shared | 32 | 1 | 64 | 6.452 | 12.007 | 12.211 | 3.326 | 0.578 |
| only_verifier | shared | 32 | 0 | 64 | 6.674 | 10.497 | 11.617 | 3.791 | 0.703 |
| only_verifier | shared | 32 | 1 | 64 | 6.753 | 11.109 | 11.867 | 3.989 | 0.625 |
| planner+step_1+step_2+aggregator+verifier | shared | 32 | 0 | 64 | 8.241 | 13.271 | 15.621 | 2.741 | 0.812 |
| planner+step_1+step_2+aggregator+verifier | shared | 32 | 1 | 64 | 7.636 | 13.099 | 15.234 | 3.161 | 0.828 |
| step_1+step_2+step_3 | shared | 32 | 0 | 64 | 6.032 | 11.336 | 12.338 | 3.091 | 0.562 |
| step_1+step_2+step_3 | shared | 32 | 1 | 64 | 6.011 | 10.454 | 11.392 | 3.226 | 0.562 |
| step_2+step_3+verifier | shared | 32 | 0 | 64 | 7.399 | 11.04 | 11.401 | 3.034 | 0.672 |
| step_2+step_3+verifier | shared | 32 | 1 | 64 | 7.284 | 11.375 | 12.631 | 3.26 | 0.688 |
| step_2+step_3 | shared | 32 | 0 | 64 | 5.856 | 10.053 | 10.662 | 3.78 | 0.531 |
| step_2+step_3 | shared | 32 | 1 | 64 | 5.934 | 10.768 | 11.588 | 3.371 | 0.516 |
| planner+step_1+aggregator | shared | 32 | 0 | 64 | 7.097 | 12.424 | 15.757 | 3.099 | 0.688 |
| planner+step_1+aggregator | shared | 32 | 1 | 64 | 6.712 | 11.816 | 12.3 | 3.062 | 0.719 |
| planner+step_1+step_3+verifier | shared | 32 | 0 | 64 | 7.848 | 13.149 | 16.763 | 2.621 | 0.766 |
| planner+step_1+step_3+verifier | shared | 32 | 1 | 64 | 7.717 | 14.904 | 16.501 | 2.527 | 0.781 |
| planner+step_1+step_2+aggregator | shared | 32 | 0 | 64 | 7.212 | 13.559 | 15.193 | 2.643 | 0.625 |
| planner+step_1+step_2+aggregator | shared | 32 | 1 | 64 | 6.636 | 13.39 | 15.082 | 2.903 | 0.672 |

30 of 32 rows shown.

## math_granite/shared_k4

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 4 | 0 | 64 | 1.757 | 3.258 | 3.382 | 2.12 | 0.594 |
| all_small | shared | 4 | 1 | 64 | 1.79 | 2.989 | 3.483 | 2.046 | 0.609 |
| all_large | shared | 4 | 0 | 64 | 4.163 | 6.593 | 8.374 | 0.849 | 0.797 |
| all_large | shared | 4 | 1 | 64 | 4.199 | 6.992 | 7.802 | 0.866 | 0.812 |
| only_planner | shared | 4 | 0 | 64 | 4.999 | 9.128 | 9.595 | 0.751 | 0.578 |
| only_planner | shared | 4 | 1 | 64 | 4.999 | 8.134 | 8.878 | 0.74 | 0.609 |
| only_step_1 | shared | 4 | 0 | 64 | 2.645 | 4.055 | 4.49 | 1.412 | 0.578 |
| only_step_1 | shared | 4 | 1 | 64 | 2.571 | 4.808 | 5.024 | 1.436 | 0.578 |
| only_step_2 | shared | 4 | 0 | 64 | 3.702 | 6.774 | 9.321 | 0.978 | 0.547 |
| only_step_2 | shared | 4 | 1 | 64 | 3.229 | 5.939 | 6.984 | 1.077 | 0.516 |
| only_step_3 | shared | 4 | 0 | 64 | 3.06 | 5.999 | 6.436 | 1.136 | 0.469 |
| only_step_3 | shared | 4 | 1 | 64 | 3.224 | 5.993 | 6.583 | 1.113 | 0.578 |
| only_aggregator | shared | 4 | 0 | 64 | 3.515 | 6.81 | 7.198 | 0.981 | 0.531 |
| only_aggregator | shared | 4 | 1 | 64 | 3.331 | 6.919 | 7.42 | 1.008 | 0.5 |
| only_verifier | shared | 4 | 0 | 64 | 5.205 | 7.893 | 9.329 | 0.751 | 0.75 |
| only_verifier | shared | 4 | 1 | 64 | 5.432 | 8.76 | 9.707 | 0.716 | 0.734 |
| planner+step_1+step_2+aggregator+verifier | shared | 4 | 0 | 64 | 4.414 | 8.006 | 9.497 | 0.788 | 0.797 |
| planner+step_1+step_2+aggregator+verifier | shared | 4 | 1 | 64 | 4.708 | 8.017 | 9.072 | 0.8 | 0.75 |
| step_1+step_2+step_3 | shared | 4 | 0 | 64 | 4.474 | 7.485 | 8.372 | 0.821 | 0.609 |
| step_1+step_2+step_3 | shared | 4 | 1 | 64 | 4.694 | 7.979 | 9.54 | 0.776 | 0.531 |
| step_2+step_3+verifier | shared | 4 | 0 | 64 | 5.968 | 10.468 | 10.675 | 0.617 | 0.75 |
| step_2+step_3+verifier | shared | 4 | 1 | 64 | 6.209 | 10.36 | 11.055 | 0.613 | 0.75 |
| step_2+step_3 | shared | 4 | 0 | 64 | 4.384 | 7.977 | 9.225 | 0.86 | 0.516 |
| step_2+step_3 | shared | 4 | 1 | 64 | 4.546 | 8.319 | 8.948 | 0.801 | 0.5 |
| planner+step_1+aggregator | shared | 4 | 0 | 64 | 5.926 | 9.634 | 14.325 | 0.629 | 0.625 |
| planner+step_1+aggregator | shared | 4 | 1 | 64 | 5.981 | 9.266 | 12.44 | 0.651 | 0.688 |
| planner+step_1+step_3+verifier | shared | 4 | 0 | 64 | 5.288 | 10.062 | 11.791 | 0.669 | 0.75 |
| planner+step_1+step_3+verifier | shared | 4 | 1 | 64 | 5.286 | 9.882 | 10.996 | 0.694 | 0.719 |
| planner+step_1+step_2+aggregator | shared | 4 | 0 | 64 | 5.952 | 8.905 | 10.488 | 0.656 | 0.625 |
| planner+step_1+step_2+aggregator | shared | 4 | 1 | 64 | 5.492 | 8.377 | 9.893 | 0.68 | 0.641 |

30 of 32 rows shown.

## math_granite/shared_k8

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 8 | 0 | 64 | 1.822 | 3.187 | 4.562 | 3.53 | 0.531 |
| all_small | shared | 8 | 1 | 64 | 1.79 | 3.062 | 3.273 | 3.865 | 0.625 |
| all_large | shared | 8 | 0 | 64 | 3.997 | 6.689 | 8.446 | 1.62 | 0.797 |
| all_large | shared | 8 | 1 | 64 | 4.295 | 6.971 | 8.248 | 1.578 | 0.828 |
| only_planner | shared | 8 | 0 | 64 | 5.718 | 9.458 | 9.622 | 1.313 | 0.625 |
| only_planner | shared | 8 | 1 | 64 | 5.543 | 8.596 | 9.562 | 1.318 | 0.578 |
| only_step_1 | shared | 8 | 0 | 64 | 3.276 | 5.276 | 5.815 | 2.267 | 0.594 |
| only_step_1 | shared | 8 | 1 | 64 | 3.274 | 5.666 | 6.472 | 2.267 | 0.547 |
| only_step_2 | shared | 8 | 0 | 64 | 3.939 | 7.746 | 8.354 | 1.672 | 0.547 |
| only_step_2 | shared | 8 | 1 | 64 | 4.188 | 7.477 | 8.294 | 1.648 | 0.578 |
| only_step_3 | shared | 8 | 0 | 64 | 4.327 | 7.545 | 8.053 | 1.715 | 0.578 |
| only_step_3 | shared | 8 | 1 | 64 | 4.608 | 7.517 | 8.554 | 1.643 | 0.578 |
| only_aggregator | shared | 8 | 0 | 64 | 5.027 | 9.366 | 10.372 | 1.306 | 0.578 |
| only_aggregator | shared | 8 | 1 | 64 | 4.253 | 7.83 | 8.501 | 1.638 | 0.531 |
| only_verifier | shared | 8 | 0 | 64 | 6.345 | 9.355 | 10.01 | 1.24 | 0.719 |
| only_verifier | shared | 8 | 1 | 64 | 6.334 | 9.836 | 10.787 | 1.129 | 0.688 |
| planner+step_1+step_2+aggregator+verifier | shared | 8 | 0 | 64 | 5.037 | 8.112 | 8.878 | 1.403 | 0.766 |
| planner+step_1+step_2+aggregator+verifier | shared | 8 | 1 | 64 | 5.215 | 9.524 | 10.076 | 1.369 | 0.734 |
| step_1+step_2+step_3 | shared | 8 | 0 | 64 | 5.215 | 10.927 | 11.983 | 1.303 | 0.578 |
| step_1+step_2+step_3 | shared | 8 | 1 | 64 | 5.215 | 8.733 | 9.624 | 1.378 | 0.547 |
| step_2+step_3+verifier | shared | 8 | 0 | 64 | 6.87 | 11.228 | 12.31 | 1.083 | 0.734 |
| step_2+step_3+verifier | shared | 8 | 1 | 64 | 6.163 | 11.933 | 12.774 | 1.046 | 0.703 |
| step_2+step_3 | shared | 8 | 0 | 64 | 5.162 | 8.849 | 9.754 | 1.428 | 0.578 |
| step_2+step_3 | shared | 8 | 1 | 64 | 5.188 | 8.984 | 10.643 | 1.316 | 0.531 |
| planner+step_1+aggregator | shared | 8 | 0 | 64 | 6.658 | 11.159 | 14.89 | 1.093 | 0.625 |
| planner+step_1+aggregator | shared | 8 | 1 | 64 | 6.564 | 11.693 | 15.158 | 1.066 | 0.656 |
| planner+step_1+step_3+verifier | shared | 8 | 0 | 64 | 6.226 | 10.248 | 13.781 | 1.046 | 0.766 |
| planner+step_1+step_3+verifier | shared | 8 | 1 | 64 | 6.253 | 10.171 | 13.073 | 1.106 | 0.766 |
| planner+step_1+step_2+aggregator | shared | 8 | 0 | 64 | 6.575 | 15.006 | 15.754 | 1.071 | 0.641 |
| planner+step_1+step_2+aggregator | shared | 8 | 1 | 64 | 6.523 | 10.591 | 15.442 | 1.136 | 0.672 |

30 of 32 rows shown.

## math_phi/shared_k32

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 32 | 0 | 64 | 4.297 | 6.76 | 7.146 | 5.778 | 0.844 |
| all_small | shared | 32 | 1 | 64 | 4.284 | 6.501 | 7.079 | 5.688 | 0.797 |
| all_large | shared | 32 | 0 | 64 | 9.524 | 15.192 | 15.755 | 1.895 | 0.953 |
| all_large | shared | 32 | 1 | 64 | 9.614 | 14.288 | 15.273 | 2.106 | 0.938 |
| only_planner | shared | 32 | 0 | 64 | 9.84 | 15.131 | 16.935 | 2.575 | 0.844 |
| only_planner | shared | 32 | 1 | 64 | 9.812 | 14.51 | 14.942 | 2.778 | 0.812 |
| only_step_1 | shared | 32 | 0 | 64 | 13.038 | 19.072 | 22.242 | 1.978 | 0.812 |
| only_step_1 | shared | 32 | 1 | 64 | 12.732 | 19.35 | 20.57 | 2.004 | 0.812 |
| only_step_2 | shared | 32 | 0 | 64 | 10.75 | 16.34 | 16.936 | 2.387 | 0.766 |
| only_step_2 | shared | 32 | 1 | 64 | 11.712 | 17.707 | 18.73 | 2.204 | 0.812 |
| only_step_3 | shared | 32 | 0 | 64 | 11.892 | 17.782 | 19.401 | 2.081 | 0.781 |
| only_step_3 | shared | 32 | 1 | 64 | 11.234 | 18.549 | 19.335 | 2.001 | 0.797 |
| only_aggregator | shared | 32 | 0 | 64 | 11.464 | 21.867 | 22.318 | 1.792 | 0.859 |
| only_aggregator | shared | 32 | 1 | 64 | 11.622 | 21.026 | 21.421 | 1.829 | 0.859 |
| only_verifier | shared | 32 | 0 | 64 | 11.832 | 18.869 | 19.931 | 2.069 | 0.938 |
| only_verifier | shared | 32 | 1 | 64 | 11.573 | 16.31 | 18.004 | 2.184 | 0.938 |
| planner+step_1+step_2+aggregator+verifier | shared | 32 | 0 | 64 | 14.169 | 22.395 | 23.73 | 1.463 | 0.938 |
| planner+step_1+step_2+aggregator+verifier | shared | 32 | 1 | 64 | 14.278 | 23.094 | 24.243 | 1.464 | 0.938 |
| step_1+step_2+step_3 | shared | 32 | 0 | 64 | 14.333 | 20.774 | 21.55 | 1.746 | 0.859 |
| step_1+step_2+step_3 | shared | 32 | 1 | 64 | 14.215 | 20 | 20.451 | 1.699 | 0.797 |
| step_2+step_3+verifier | shared | 32 | 0 | 64 | 13.494 | 19.037 | 21.876 | 1.896 | 0.906 |
| step_2+step_3+verifier | shared | 32 | 1 | 64 | 13.305 | 18.883 | 21.719 | 1.85 | 0.922 |
| step_2+step_3 | shared | 32 | 0 | 64 | 11.551 | 17.247 | 17.86 | 2.082 | 0.797 |
| step_2+step_3 | shared | 32 | 1 | 64 | 11.861 | 17.085 | 18.887 | 2.006 | 0.781 |
| planner+step_1+aggregator | shared | 32 | 0 | 64 | 13.187 | 23.136 | 24.806 | 1.622 | 0.844 |
| planner+step_1+aggregator | shared | 32 | 1 | 64 | 13.474 | 22.463 | 23.485 | 1.681 | 0.828 |
| planner+step_1+step_3+verifier | shared | 32 | 0 | 64 | 15.397 | 23.141 | 24.43 | 1.48 | 0.922 |
| planner+step_1+step_3+verifier | shared | 32 | 1 | 64 | 15.004 | 23.027 | 25.101 | 1.606 | 0.906 |
| planner+step_1+step_2+aggregator | shared | 32 | 0 | 64 | 13.145 | 24.146 | 25.532 | 1.538 | 0.797 |
| planner+step_1+step_2+aggregator | shared | 32 | 1 | 64 | 12.891 | 24.184 | 25.752 | 1.516 | 0.828 |

30 of 32 rows shown.

## math_phi/shared_k4

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 4 | 0 | 64 | 2.987 | 4.333 | 5.153 | 1.237 | 0.828 |
| all_small | shared | 4 | 1 | 64 | 2.98 | 4.323 | 4.616 | 1.226 | 0.812 |
| all_large | shared | 4 | 0 | 64 | 8.865 | 13.651 | 13.98 | 0.428 | 0.938 |
| all_large | shared | 4 | 1 | 64 | 8.639 | 13.942 | 14.59 | 0.426 | 0.953 |
| only_planner | shared | 4 | 0 | 64 | 6.826 | 12.513 | 13.284 | 0.542 | 0.812 |
| only_planner | shared | 4 | 1 | 64 | 7.263 | 12.183 | 12.698 | 0.541 | 0.828 |
| only_step_1 | shared | 4 | 0 | 64 | 8.104 | 13.004 | 14.922 | 0.488 | 0.781 |
| only_step_1 | shared | 4 | 1 | 64 | 8.01 | 13.02 | 13.49 | 0.507 | 0.797 |
| only_step_2 | shared | 4 | 0 | 64 | 6.829 | 9.495 | 11.147 | 0.556 | 0.797 |
| only_step_2 | shared | 4 | 1 | 64 | 6.388 | 10.155 | 10.262 | 0.578 | 0.75 |
| only_step_3 | shared | 4 | 0 | 64 | 7.422 | 12.835 | 14.555 | 0.509 | 0.797 |
| only_step_3 | shared | 4 | 1 | 64 | 7.693 | 13.537 | 14.9 | 0.498 | 0.797 |
| only_aggregator | shared | 4 | 0 | 64 | 8.029 | 15.263 | 17.629 | 0.472 | 0.828 |
| only_aggregator | shared | 4 | 1 | 64 | 7.291 | 14.936 | 16.538 | 0.483 | 0.859 |
| only_verifier | shared | 4 | 0 | 64 | 10.17 | 14.903 | 16.979 | 0.385 | 0.938 |
| only_verifier | shared | 4 | 1 | 64 | 9.458 | 14.073 | 14.766 | 0.405 | 0.906 |
| planner+step_1+step_2+aggregator+verifier | shared | 4 | 0 | 64 | 10.048 | 16.891 | 19.243 | 0.364 | 0.938 |
| planner+step_1+step_2+aggregator+verifier | shared | 4 | 1 | 64 | 9.959 | 16.533 | 17.231 | 0.372 | 0.953 |
| step_1+step_2+step_3 | shared | 4 | 0 | 64 | 10.968 | 16.697 | 20.881 | 0.339 | 0.812 |
| step_1+step_2+step_3 | shared | 4 | 1 | 64 | 10.661 | 15.467 | 17.104 | 0.35 | 0.812 |
| step_2+step_3+verifier | shared | 4 | 0 | 64 | 10.756 | 15.552 | 16.877 | 0.352 | 0.953 |
| step_2+step_3+verifier | shared | 4 | 1 | 64 | 10.844 | 16.285 | 17.095 | 0.345 | 0.922 |
| step_2+step_3 | shared | 4 | 0 | 64 | 8.832 | 13.793 | 14.007 | 0.42 | 0.781 |
| step_2+step_3 | shared | 4 | 1 | 64 | 9.4 | 13.227 | 13.531 | 0.425 | 0.766 |
| planner+step_1+aggregator | shared | 4 | 0 | 64 | 11.097 | 18.493 | 20.9 | 0.339 | 0.844 |
| planner+step_1+aggregator | shared | 4 | 1 | 64 | 11.288 | 20.904 | 21.599 | 0.328 | 0.875 |
| planner+step_1+step_3+verifier | shared | 4 | 0 | 64 | 11.397 | 19.092 | 19.144 | 0.343 | 0.922 |
| planner+step_1+step_3+verifier | shared | 4 | 1 | 64 | 10.737 | 17.357 | 19.203 | 0.35 | 0.922 |
| planner+step_1+step_2+aggregator | shared | 4 | 0 | 64 | 10.792 | 19.418 | 21.068 | 0.343 | 0.828 |
| planner+step_1+step_2+aggregator | shared | 4 | 1 | 64 | 11.2 | 20.007 | 21.869 | 0.335 | 0.812 |

30 of 32 rows shown.

## math_phi/shared_k8

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 8 | 0 | 64 | 3.197 | 4.675 | 5.719 | 2.223 | 0.828 |
| all_small | shared | 8 | 1 | 64 | 3.191 | 4.6 | 5.22 | 2.256 | 0.859 |
| all_large | shared | 8 | 0 | 64 | 9.019 | 14.123 | 14.86 | 0.802 | 0.938 |
| all_large | shared | 8 | 1 | 64 | 8.767 | 14.055 | 14.78 | 0.8 | 0.938 |
| only_planner | shared | 8 | 0 | 64 | 8.213 | 13.251 | 14.207 | 0.922 | 0.781 |
| only_planner | shared | 8 | 1 | 64 | 8.111 | 12.499 | 13.78 | 0.935 | 0.859 |
| only_step_1 | shared | 8 | 0 | 64 | 9.589 | 13.613 | 14.73 | 0.787 | 0.812 |
| only_step_1 | shared | 8 | 1 | 64 | 9.45 | 13.333 | 14.32 | 0.81 | 0.781 |
| only_step_2 | shared | 8 | 0 | 64 | 8.723 | 12.993 | 13.43 | 0.837 | 0.75 |
| only_step_2 | shared | 8 | 1 | 64 | 9.096 | 12.819 | 13.507 | 0.826 | 0.781 |
| only_step_3 | shared | 8 | 0 | 64 | 9.21 | 13.229 | 17.739 | 0.817 | 0.812 |
| only_step_3 | shared | 8 | 1 | 64 | 8.967 | 14.335 | 15.889 | 0.813 | 0.766 |
| only_aggregator | shared | 8 | 0 | 64 | 9.326 | 17.399 | 19.569 | 0.707 | 0.797 |
| only_aggregator | shared | 8 | 1 | 64 | 9.33 | 17.507 | 17.741 | 0.717 | 0.859 |
| only_verifier | shared | 8 | 0 | 64 | 11.008 | 16.117 | 19.176 | 0.683 | 0.938 |
| only_verifier | shared | 8 | 1 | 64 | 11.16 | 18.317 | 19.137 | 0.652 | 0.922 |
| planner+step_1+step_2+aggregator+verifier | shared | 8 | 0 | 64 | 11.421 | 19.621 | 20.235 | 0.594 | 0.938 |
| planner+step_1+step_2+aggregator+verifier | shared | 8 | 1 | 64 | 11.503 | 19.416 | 20.273 | 0.6 | 0.953 |
| step_1+step_2+step_3 | shared | 8 | 0 | 64 | 12.153 | 17.852 | 18.534 | 0.613 | 0.812 |
| step_1+step_2+step_3 | shared | 8 | 1 | 64 | 12.034 | 17.601 | 18.374 | 0.63 | 0.812 |
| step_2+step_3+verifier | shared | 8 | 0 | 64 | 12.491 | 18.27 | 18.353 | 0.597 | 0.938 |
| step_2+step_3+verifier | shared | 8 | 1 | 64 | 12.625 | 17.957 | 21.398 | 0.589 | 0.938 |
| step_2+step_3 | shared | 8 | 0 | 64 | 10.619 | 15.426 | 15.944 | 0.679 | 0.781 |
| step_2+step_3 | shared | 8 | 1 | 64 | 10.519 | 15.67 | 16.584 | 0.683 | 0.797 |
| planner+step_1+aggregator | shared | 8 | 0 | 64 | 12.51 | 22.44 | 23.943 | 0.574 | 0.859 |
| planner+step_1+aggregator | shared | 8 | 1 | 64 | 12.213 | 21.583 | 23.696 | 0.563 | 0.891 |
| planner+step_1+step_3+verifier | shared | 8 | 0 | 64 | 12.608 | 20.624 | 21.54 | 0.575 | 0.906 |
| planner+step_1+step_3+verifier | shared | 8 | 1 | 64 | 12.624 | 19.884 | 21.465 | 0.583 | 0.922 |
| planner+step_1+step_2+aggregator | shared | 8 | 0 | 64 | 12.112 | 21.558 | 22.878 | 0.566 | 0.844 |
| planner+step_1+step_2+aggregator | shared | 8 | 1 | 64 | 12.32 | 21.779 | 23.277 | 0.566 | 0.828 |

30 of 32 rows shown.
