# Phase X1

Generated 2026-11-17 10:42 UTC, backend `vllm`.

Code run: `c1bb8338fa64acd82d82f1eb0c5a5ce6cb7b019b`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| math_granite/shared | finished |
| math_phi/shared | finished |
| math_q3_14/shared | finished |

## math_granite/shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 2.108 | 3.344 | 3.543 | 4.979 | 0.547 |
| all_small | shared | 16 | 1 | 64 | 2.043 | 3.402 | 3.727 | 5.861 | 0.609 |
| only_planner | shared | 16 | 0 | 64 | 5.321 | 9.85 | 10.125 | 2.617 | 0.625 |
| only_planner | shared | 16 | 1 | 64 | 5.448 | 10.545 | 10.655 | 2.546 | 0.578 |
| only_step_1 | shared | 16 | 0 | 64 | 4.234 | 6.541 | 7.62 | 2.987 | 0.562 |
| only_step_1 | shared | 16 | 1 | 64 | 4.29 | 7.238 | 7.354 | 2.903 | 0.531 |
| only_step_2 | shared | 16 | 0 | 64 | 4.495 | 7.626 | 9.464 | 2.643 | 0.469 |
| only_step_2 | shared | 16 | 1 | 64 | 4.496 | 8.919 | 11.74 | 2.322 | 0.5 |
| only_step_3 | shared | 16 | 0 | 64 | 4.482 | 9.105 | 11.036 | 2.491 | 0.5 |
| only_step_3 | shared | 16 | 1 | 64 | 4.911 | 7.819 | 8.315 | 2.647 | 0.578 |
| only_aggregator | shared | 16 | 0 | 64 | 5.731 | 11.031 | 11.212 | 2.17 | 0.609 |
| only_aggregator | shared | 16 | 1 | 64 | 5.234 | 9.938 | 13.03 | 2.103 | 0.547 |
| only_verifier | shared | 16 | 0 | 64 | 6.16 | 10.114 | 10.259 | 2.078 | 0.672 |
| only_verifier | shared | 16 | 1 | 64 | 6.254 | 9.534 | 10.242 | 2.204 | 0.672 |
| planner+step_1 | shared | 16 | 0 | 64 | 5.846 | 11.758 | 14.889 | 2.062 | 0.656 |
| planner+step_1 | shared | 16 | 1 | 64 | 6.107 | 11.125 | 11.305 | 2.068 | 0.688 |
| planner+step_2 | shared | 16 | 0 | 64 | 5.969 | 10.119 | 11.009 | 1.932 | 0.594 |
| planner+step_2 | shared | 16 | 1 | 64 | 5.991 | 10.324 | 12.847 | 2.179 | 0.562 |
| planner+step_3 | shared | 16 | 0 | 64 | 6.382 | 9.371 | 9.818 | 2.251 | 0.609 |
| planner+step_3 | shared | 16 | 1 | 64 | 5.987 | 9.579 | 10.207 | 2.367 | 0.609 |
| planner+aggregator | shared | 16 | 0 | 64 | 6.144 | 11.99 | 13.157 | 1.835 | 0.578 |
| planner+aggregator | shared | 16 | 1 | 64 | 6.446 | 10.464 | 12.994 | 1.939 | 0.562 |
| planner+verifier | shared | 16 | 0 | 64 | 7.383 | 12.619 | 12.973 | 1.879 | 0.766 |
| planner+verifier | shared | 16 | 1 | 64 | 7.063 | 12.223 | 12.942 | 1.937 | 0.719 |
| step_1+step_2 | shared | 16 | 0 | 64 | 5.135 | 8.358 | 8.778 | 2.388 | 0.562 |
| step_1+step_2 | shared | 16 | 1 | 64 | 5.102 | 8.75 | 8.834 | 2.226 | 0.5 |
| step_1+step_3 | shared | 16 | 0 | 64 | 4.78 | 8.664 | 11.238 | 2.211 | 0.531 |
| step_1+step_3 | shared | 16 | 1 | 64 | 5.125 | 8.299 | 10.738 | 2.431 | 0.562 |
| step_1+aggregator | shared | 16 | 0 | 64 | 5.498 | 12.953 | 16.708 | 2.168 | 0.562 |
| step_1+aggregator | shared | 16 | 1 | 64 | 5.692 | 9.785 | 10.329 | 2.121 | 0.531 |

30 of 128 rows shown.

## math_phi/shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 3.585 | 5.379 | 6.328 | 3.753 | 0.797 |
| all_small | shared | 16 | 1 | 64 | 3.548 | 5.199 | 6.251 | 3.818 | 0.766 |
| only_planner | shared | 16 | 0 | 64 | 8.769 | 14.298 | 15.653 | 1.643 | 0.812 |
| only_planner | shared | 16 | 1 | 64 | 9.068 | 14.167 | 15.974 | 1.616 | 0.828 |
| only_step_1 | shared | 16 | 0 | 64 | 10.8 | 16.135 | 17.649 | 1.307 | 0.828 |
| only_step_1 | shared | 16 | 1 | 64 | 11.807 | 16.597 | 17.815 | 1.224 | 0.797 |
| only_step_2 | shared | 16 | 0 | 64 | 9.645 | 15.329 | 16.417 | 1.409 | 0.781 |
| only_step_2 | shared | 16 | 1 | 64 | 9.576 | 15.685 | 18.104 | 1.427 | 0.844 |
| only_step_3 | shared | 16 | 0 | 64 | 9.768 | 14.755 | 16.691 | 1.265 | 0.797 |
| only_step_3 | shared | 16 | 1 | 64 | 10.222 | 19.434 | 20.574 | 1.13 | 0.812 |
| only_aggregator | shared | 16 | 0 | 64 | 10.258 | 19.136 | 19.617 | 1.209 | 0.906 |
| only_aggregator | shared | 16 | 1 | 64 | 10.298 | 19.176 | 19.474 | 1.165 | 0.828 |
| only_verifier | shared | 16 | 0 | 64 | 11.482 | 17.172 | 19.237 | 1.179 | 0.922 |
| only_verifier | shared | 16 | 1 | 64 | 11.333 | 18.101 | 18.973 | 1.142 | 0.922 |
| planner+step_1 | shared | 16 | 0 | 64 | 10.73 | 17.612 | 19.733 | 1.224 | 0.797 |
| planner+step_1 | shared | 16 | 1 | 64 | 10.883 | 15.952 | 17.431 | 1.244 | 0.812 |
| planner+step_2 | shared | 16 | 0 | 64 | 10.314 | 16.013 | 19.221 | 1.311 | 0.859 |
| planner+step_2 | shared | 16 | 1 | 64 | 9.934 | 17.725 | 19.127 | 1.257 | 0.859 |
| planner+step_3 | shared | 16 | 0 | 64 | 10.708 | 15.893 | 17.538 | 1.236 | 0.828 |
| planner+step_3 | shared | 16 | 1 | 64 | 10.732 | 15.607 | 17.671 | 1.239 | 0.859 |
| planner+aggregator | shared | 16 | 0 | 64 | 10.31 | 20.25 | 20.582 | 1.125 | 0.812 |
| planner+aggregator | shared | 16 | 1 | 64 | 10.288 | 19.46 | 21.166 | 1.133 | 0.828 |
| planner+verifier | shared | 16 | 0 | 64 | 11.292 | 17.409 | 24.59 | 1.175 | 0.875 |
| planner+verifier | shared | 16 | 1 | 64 | 12.113 | 18.594 | 23.188 | 1.118 | 0.906 |
| step_1+step_2 | shared | 16 | 0 | 64 | 11.475 | 17.329 | 17.872 | 1.198 | 0.844 |
| step_1+step_2 | shared | 16 | 1 | 64 | 11.783 | 17.173 | 17.567 | 1.175 | 0.859 |
| step_1+step_3 | shared | 16 | 0 | 64 | 12.471 | 18.034 | 19.154 | 1.094 | 0.828 |
| step_1+step_3 | shared | 16 | 1 | 64 | 12.438 | 17.595 | 18.267 | 1.114 | 0.797 |
| step_1+aggregator | shared | 16 | 0 | 64 | 13.335 | 20.669 | 21.067 | 0.992 | 0.859 |
| step_1+aggregator | shared | 16 | 1 | 64 | 13.107 | 21.843 | 23.096 | 0.988 | 0.891 |

30 of 128 rows shown.

## math_q3_14/shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 1.909 | 2.893 | 3.215 | 6.779 | 0.719 |
| all_small | shared | 16 | 1 | 64 | 1.885 | 2.697 | 2.833 | 7.177 | 0.703 |
| only_planner | shared | 16 | 0 | 64 | 5.959 | 8.855 | 9.462 | 2.461 | 0.734 |
| only_planner | shared | 16 | 1 | 64 | 6.08 | 8.307 | 9.295 | 2.414 | 0.688 |
| only_step_1 | shared | 16 | 0 | 64 | 6.686 | 10.497 | 10.943 | 2.178 | 0.75 |
| only_step_1 | shared | 16 | 1 | 64 | 6.906 | 10.632 | 10.906 | 2.127 | 0.719 |
| only_step_2 | shared | 16 | 0 | 64 | 6.331 | 9.924 | 11.796 | 2.185 | 0.641 |
| only_step_2 | shared | 16 | 1 | 64 | 6.298 | 9.663 | 10.964 | 2.172 | 0.688 |
| only_step_3 | shared | 16 | 0 | 64 | 6.024 | 9.921 | 10.348 | 2.426 | 0.703 |
| only_step_3 | shared | 16 | 1 | 64 | 6.182 | 9.647 | 9.972 | 2.359 | 0.719 |
| only_aggregator | shared | 16 | 0 | 64 | 5.581 | 9.047 | 11.957 | 2.575 | 0.75 |
| only_aggregator | shared | 16 | 1 | 64 | 4.918 | 7.886 | 8.129 | 2.892 | 0.703 |
| only_verifier | shared | 16 | 0 | 64 | 6.486 | 11.212 | 11.955 | 2.066 | 0.891 |
| only_verifier | shared | 16 | 1 | 64 | 6.663 | 11.229 | 11.559 | 2.031 | 0.891 |
| planner+step_1 | shared | 16 | 0 | 64 | 7.775 | 10.731 | 11.505 | 1.761 | 0.688 |
| planner+step_1 | shared | 16 | 1 | 64 | 7.677 | 10.712 | 11.545 | 1.771 | 0.688 |
| planner+step_2 | shared | 16 | 0 | 64 | 7.41 | 10.057 | 10.754 | 1.917 | 0.688 |
| planner+step_2 | shared | 16 | 1 | 64 | 7.379 | 10.529 | 11.318 | 1.909 | 0.703 |
| planner+step_3 | shared | 16 | 0 | 64 | 7.438 | 11.093 | 12.614 | 1.703 | 0.719 |
| planner+step_3 | shared | 16 | 1 | 64 | 7.431 | 11.071 | 12.166 | 1.715 | 0.703 |
| planner+aggregator | shared | 16 | 0 | 64 | 6.478 | 9.261 | 9.567 | 2.199 | 0.766 |
| planner+aggregator | shared | 16 | 1 | 64 | 6.986 | 9.185 | 11.177 | 1.874 | 0.766 |
| planner+verifier | shared | 16 | 0 | 64 | 7.46 | 11.625 | 11.928 | 1.81 | 0.859 |
| planner+verifier | shared | 16 | 1 | 64 | 7.482 | 11.587 | 12.465 | 1.695 | 0.875 |
| step_1+step_2 | shared | 16 | 0 | 64 | 7.884 | 11.36 | 12.518 | 1.834 | 0.719 |
| step_1+step_2 | shared | 16 | 1 | 64 | 7.974 | 12.571 | 13.021 | 1.726 | 0.734 |
| step_1+step_3 | shared | 16 | 0 | 64 | 8.153 | 11.723 | 12.649 | 1.744 | 0.719 |
| step_1+step_3 | shared | 16 | 1 | 64 | 8.264 | 11.79 | 12.142 | 1.744 | 0.734 |
| step_1+aggregator | shared | 16 | 0 | 64 | 7.297 | 10.734 | 11.753 | 1.864 | 0.781 |
| step_1+aggregator | shared | 16 | 1 | 64 | 7.306 | 10.075 | 11.678 | 2.04 | 0.797 |

30 of 128 rows shown.
