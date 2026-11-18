# Phase X1

Generated 2026-11-18 00:01 UTC, backend `vllm`.

Code run: `c1bb8338fa64acd82d82f1eb0c5a5ce6cb7b019b`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| complex_q15_7/shared | finished |
| hotpot_iso_q15_7/separate | finished |
| hotpot_iso_q15_7/shared | finished |
| hotpot_q15_7/separate | finished |
| hotpot_q15_7/shared | finished |
| math_granite/separate | finished |
| math_phi/separate | finished |
| math_q15_7/separate | finished |
| math_q15_7/shared | finished |
| math_q3_14/separate | finished |
| math_tiers/shared | finished |

## complex_q15_7/shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 3.03 | 5.348 | 5.663 | 4.138 | 0.641 |
| all_small | shared | 16 | 1 | 64 | 3.035 | 5.695 | 5.932 | 4.188 | 0.625 |
| only_aggregator | shared | 16 | 0 | 64 | 7.169 | 11.43 | 12.35 | 1.985 | 0.547 |
| only_aggregator | shared | 16 | 1 | 64 | 7.147 | 13.569 | 13.981 | 1.823 | 0.578 |
| only_planner | shared | 16 | 0 | 64 | 6.782 | 15.075 | 16.189 | 1.913 | 0.625 |
| only_planner | shared | 16 | 1 | 64 | 6.512 | 15.79 | 16.742 | 1.963 | 0.578 |
| only_researcher_1 | shared | 16 | 0 | 64 | 2.945 | 5.228 | 5.693 | 4.278 | 0.516 |
| only_researcher_1 | shared | 16 | 1 | 64 | 3.001 | 5.161 | 5.814 | 4.342 | 0.578 |
| only_researcher_2 | shared | 16 | 0 | 64 | 3.463 | 5.866 | 6.581 | 3.71 | 0.406 |
| only_researcher_2 | shared | 16 | 1 | 64 | 3.597 | 5.46 | 7.406 | 3.756 | 0.422 |
| only_step_1_1 | shared | 16 | 0 | 64 | 4.467 | 8.012 | 8.529 | 3.144 | 0.562 |
| only_step_1_1 | shared | 16 | 1 | 64 | 4.397 | 7.907 | 8.526 | 3.016 | 0.594 |
| only_step_2_1 | shared | 16 | 0 | 64 | 3.871 | 7.289 | 8.47 | 3.159 | 0.578 |
| only_step_2_1 | shared | 16 | 1 | 64 | 4.57 | 7.959 | 9.522 | 2.881 | 0.594 |
| only_verifier | shared | 16 | 0 | 64 | 9.607 | 15.287 | 17.791 | 1.371 | 0.844 |
| only_verifier | shared | 16 | 1 | 64 | 9.84 | 15.384 | 17.739 | 1.381 | 0.812 |
| planner+aggregator | shared | 16 | 0 | 64 | 7.996 | 15.702 | 15.815 | 1.731 | 0.609 |
| planner+aggregator | shared | 16 | 1 | 64 | 7.773 | 15.661 | 15.96 | 1.657 | 0.672 |
| planner+researcher_1+researcher_2+step_1_2+step_2_1 | shared | 16 | 0 | 64 | 3.591 | 5.788 | 6.195 | 3.764 | 0.453 |
| planner+researcher_1+researcher_2+step_1_2+step_2_1 | shared | 16 | 1 | 64 | 3.681 | 6.385 | 6.597 | 3.665 | 0.422 |
| planner+researcher_1+researcher_2+step_2_1+step_2_2+verifier | shared | 16 | 0 | 64 | 4.907 | 7.198 | 7.926 | 2.879 | 0.797 |
| planner+researcher_1+researcher_2+step_2_1+step_2_2+verifier | shared | 16 | 1 | 64 | 4.823 | 7.15 | 7.787 | 2.873 | 0.828 |
| planner+researcher_1+step_1_1+step_2_1+step_2_2+verifier | shared | 16 | 0 | 64 | 6.097 | 8.743 | 9.358 | 2.311 | 0.891 |
| planner+researcher_1+step_1_1+step_2_1+step_2_2+verifier | shared | 16 | 1 | 64 | 6.201 | 8.676 | 10.189 | 2.247 | 0.891 |
| planner+researcher_1+step_1_1+step_2_1+verifier | shared | 16 | 0 | 64 | 6.581 | 9.775 | 10.445 | 2.169 | 0.828 |
| planner+researcher_1+step_1_1+step_2_1+verifier | shared | 16 | 1 | 64 | 6.616 | 9.051 | 10.097 | 2.198 | 0.844 |
| planner+researcher_1+step_2_1+verifier | shared | 16 | 0 | 64 | 6.344 | 9.494 | 12.484 | 2.155 | 0.875 |
| planner+researcher_1+step_2_1+verifier | shared | 16 | 1 | 64 | 6.439 | 9.401 | 11.89 | 2.16 | 0.844 |
| planner+step_1_1+verifier | shared | 16 | 0 | 64 | 8.158 | 14.53 | 15.725 | 1.61 | 0.812 |
| planner+step_1_1+verifier | shared | 16 | 1 | 64 | 7.839 | 13.684 | 15.612 | 1.573 | 0.844 |

30 of 368 rows shown.

## hotpot_iso_q15_7/separate

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 16 | 0 | 64 | 0.792 | 1.328 | 1.349 | 17.13 | 0.312 |
| all_small | separate | 16 | 1 | 64 | 0.563 | 0.891 | 1.049 | 22.633 | 0.297 |
| only_planner | separate | 16 | 0 | 64 | 1.112 | 1.428 | 1.566 | 13.333 | 0.359 |
| only_planner | separate | 16 | 1 | 64 | 0.743 | 1.08 | 1.198 | 17.384 | 0.359 |
| only_hop_1 | separate | 16 | 0 | 64 | 1.017 | 1.405 | 1.806 | 14.683 | 0.328 |
| only_hop_1 | separate | 16 | 1 | 64 | 0.678 | 0.925 | 0.977 | 20.404 | 0.344 |
| only_hop_2 | separate | 16 | 0 | 64 | 0.628 | 1.002 | 1.053 | 21.864 | 0.375 |
| only_hop_2 | separate | 16 | 1 | 64 | 0.611 | 0.981 | 1.114 | 21.994 | 0.375 |
| only_aggregator | separate | 16 | 0 | 64 | 0.603 | 0.997 | 1.018 | 23.422 | 0.266 |
| only_aggregator | separate | 16 | 1 | 64 | 0.598 | 1.04 | 1.054 | 22.967 | 0.359 |
| only_verifier | separate | 16 | 0 | 64 | 0.611 | 0.973 | 1.17 | 21.408 | 0.344 |
| only_verifier | separate | 16 | 1 | 64 | 0.602 | 0.929 | 0.995 | 23.242 | 0.359 |
| planner+hop_1 | separate | 16 | 0 | 64 | 0.883 | 1.241 | 1.303 | 15.489 | 0.297 |
| planner+hop_1 | separate | 16 | 1 | 64 | 0.872 | 1.237 | 1.316 | 15.82 | 0.266 |
| planner+hop_2 | separate | 16 | 0 | 64 | 0.791 | 1.267 | 1.284 | 16.05 | 0.328 |
| planner+hop_2 | separate | 16 | 1 | 64 | 0.772 | 1.274 | 1.356 | 16.611 | 0.328 |
| planner+aggregator | separate | 16 | 0 | 64 | 0.783 | 1.19 | 1.247 | 17.643 | 0.344 |
| planner+aggregator | separate | 16 | 1 | 64 | 0.774 | 1.203 | 1.337 | 17.423 | 0.375 |
| planner+verifier | separate | 16 | 0 | 64 | 0.797 | 1.307 | 1.336 | 16.341 | 0.422 |
| planner+verifier | separate | 16 | 1 | 64 | 0.767 | 1.201 | 1.564 | 15.637 | 0.438 |
| hop_1+hop_2 | separate | 16 | 0 | 64 | 0.726 | 0.976 | 1.156 | 19.284 | 0.375 |
| hop_1+hop_2 | separate | 16 | 1 | 64 | 0.708 | 0.954 | 1.11 | 19.629 | 0.375 |
| hop_1+aggregator | separate | 16 | 0 | 64 | 0.731 | 1.046 | 1.093 | 19.067 | 0.312 |
| hop_1+aggregator | separate | 16 | 1 | 64 | 0.71 | 1.087 | 1.116 | 18.251 | 0.297 |
| hop_1+verifier | separate | 16 | 0 | 64 | 0.78 | 1.119 | 1.221 | 18.193 | 0.375 |
| hop_1+verifier | separate | 16 | 1 | 64 | 0.765 | 1.095 | 1.221 | 18.635 | 0.375 |
| hop_2+aggregator | separate | 16 | 0 | 64 | 0.675 | 0.959 | 1.102 | 19.708 | 0.438 |
| hop_2+aggregator | separate | 16 | 1 | 64 | 0.688 | 0.976 | 1.095 | 19.996 | 0.391 |
| hop_2+verifier | separate | 16 | 0 | 64 | 0.675 | 1.039 | 1.1 | 20.432 | 0.391 |
| hop_2+verifier | separate | 16 | 1 | 64 | 0.693 | 1.003 | 1.119 | 19.997 | 0.391 |

30 of 64 rows shown.

## hotpot_iso_q15_7/shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 0.59 | 1.006 | 1.108 | 23.627 | 0.266 |
| all_small | shared | 16 | 1 | 64 | 0.559 | 1.013 | 1.134 | 22.649 | 0.328 |
| only_planner | shared | 16 | 0 | 64 | 1.497 | 2.315 | 2.631 | 9.821 | 0.359 |
| only_planner | shared | 16 | 1 | 64 | 1.476 | 2.291 | 2.478 | 9.455 | 0.391 |
| only_hop_1 | shared | 16 | 0 | 64 | 1.479 | 2.001 | 2.077 | 10.119 | 0.328 |
| only_hop_1 | shared | 16 | 1 | 64 | 1.439 | 2.144 | 2.526 | 9.835 | 0.375 |
| only_hop_2 | shared | 16 | 0 | 64 | 1.421 | 2.176 | 2.446 | 9.91 | 0.328 |
| only_hop_2 | shared | 16 | 1 | 64 | 1.384 | 2.257 | 2.341 | 10.144 | 0.375 |
| only_aggregator | shared | 16 | 0 | 64 | 1.318 | 2.303 | 2.928 | 10.179 | 0.328 |
| only_aggregator | shared | 16 | 1 | 64 | 1.24 | 2.044 | 2.134 | 11.252 | 0.312 |
| only_verifier | shared | 16 | 0 | 64 | 1.275 | 2.138 | 2.149 | 11.125 | 0.359 |
| only_verifier | shared | 16 | 1 | 64 | 1.35 | 2.196 | 2.498 | 10.334 | 0.328 |
| planner+hop_1 | shared | 16 | 0 | 64 | 1.641 | 2.556 | 2.618 | 8.607 | 0.266 |
| planner+hop_1 | shared | 16 | 1 | 64 | 1.607 | 2.331 | 2.551 | 8.683 | 0.281 |
| planner+hop_2 | shared | 16 | 0 | 64 | 1.595 | 2.745 | 2.929 | 8.151 | 0.328 |
| planner+hop_2 | shared | 16 | 1 | 64 | 1.558 | 2.479 | 2.896 | 8.491 | 0.344 |
| planner+aggregator | shared | 16 | 0 | 64 | 1.504 | 2.535 | 2.675 | 8.665 | 0.359 |
| planner+aggregator | shared | 16 | 1 | 64 | 1.473 | 2.501 | 2.513 | 8.697 | 0.391 |
| planner+verifier | shared | 16 | 0 | 64 | 1.654 | 2.593 | 2.817 | 8.014 | 0.422 |
| planner+verifier | shared | 16 | 1 | 64 | 1.618 | 2.542 | 2.724 | 8.51 | 0.422 |
| hop_1+hop_2 | shared | 16 | 0 | 64 | 1.493 | 2.075 | 2.249 | 9.542 | 0.375 |
| hop_1+hop_2 | shared | 16 | 1 | 64 | 1.451 | 1.947 | 2.08 | 10.169 | 0.375 |
| hop_1+aggregator | shared | 16 | 0 | 64 | 1.479 | 2.204 | 2.277 | 9.499 | 0.344 |
| hop_1+aggregator | shared | 16 | 1 | 64 | 1.507 | 2.093 | 2.289 | 9.651 | 0.297 |
| hop_1+verifier | shared | 16 | 0 | 64 | 1.57 | 2.272 | 2.463 | 8.999 | 0.375 |
| hop_1+verifier | shared | 16 | 1 | 64 | 1.566 | 2.219 | 2.266 | 9.218 | 0.359 |
| hop_2+aggregator | shared | 16 | 0 | 64 | 1.438 | 2.099 | 2.247 | 9.955 | 0.422 |
| hop_2+aggregator | shared | 16 | 1 | 64 | 1.433 | 2.533 | 2.614 | 9.643 | 0.438 |
| hop_2+verifier | shared | 16 | 0 | 64 | 1.366 | 2.07 | 2.275 | 10.359 | 0.453 |
| hop_2+verifier | shared | 16 | 1 | 64 | 1.389 | 2.144 | 2.576 | 9.879 | 0.406 |

30 of 64 rows shown.

## hotpot_q15_7/separate

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 16 | 0 | 64 | 0.969 | 1.521 | 1.896 | 13.992 | 0.297 |
| all_small | separate | 16 | 1 | 64 | 0.593 | 1.019 | 1.113 | 22.811 | 0.328 |
| only_planner | separate | 16 | 0 | 64 | 1.127 | 1.485 | 1.561 | 13.012 | 0.375 |
| only_planner | separate | 16 | 1 | 64 | 0.764 | 1.205 | 1.242 | 17.547 | 0.391 |
| only_hop_1 | separate | 16 | 0 | 64 | 1.049 | 1.452 | 1.697 | 13.795 | 0.344 |
| only_hop_1 | separate | 16 | 1 | 64 | 0.709 | 1.043 | 1.079 | 18.754 | 0.344 |
| only_hop_2 | separate | 16 | 0 | 64 | 0.647 | 1.036 | 1.126 | 19.061 | 0.297 |
| only_hop_2 | separate | 16 | 1 | 64 | 0.672 | 0.998 | 1.046 | 20.517 | 0.266 |
| only_aggregator | separate | 16 | 0 | 64 | 0.913 | 1.201 | 1.216 | 16.312 | 0.469 |
| only_aggregator | separate | 16 | 1 | 64 | 0.609 | 0.98 | 1.016 | 23.011 | 0.422 |
| only_verifier | separate | 16 | 0 | 64 | 0.969 | 1.951 | 2.572 | 13.357 | 0.5 |
| only_verifier | separate | 16 | 1 | 64 | 0.735 | 1.532 | 1.953 | 12.624 | 0.484 |
| planner+hop_1 | separate | 16 | 0 | 64 | 0.897 | 1.291 | 1.424 | 14.984 | 0.312 |
| planner+hop_1 | separate | 16 | 1 | 64 | 0.899 | 1.269 | 1.406 | 15.226 | 0.312 |
| planner+hop_2 | separate | 16 | 0 | 64 | 0.822 | 1.3 | 1.361 | 15.503 | 0.344 |
| planner+hop_2 | separate | 16 | 1 | 64 | 0.826 | 1.318 | 1.37 | 15.682 | 0.359 |
| planner+aggregator | separate | 16 | 0 | 64 | 0.82 | 1.237 | 1.259 | 16.364 | 0.516 |
| planner+aggregator | separate | 16 | 1 | 64 | 0.819 | 1.212 | 1.25 | 16.799 | 0.531 |
| planner+verifier | separate | 16 | 0 | 64 | 0.825 | 1.484 | 1.758 | 14.947 | 0.5 |
| planner+verifier | separate | 16 | 1 | 64 | 0.821 | 1.595 | 2.146 | 14.829 | 0.484 |
| hop_1+hop_2 | separate | 16 | 0 | 64 | 0.767 | 1.146 | 1.242 | 17.586 | 0.344 |
| hop_1+hop_2 | separate | 16 | 1 | 64 | 0.767 | 1.109 | 1.152 | 17.804 | 0.359 |
| hop_1+aggregator | separate | 16 | 0 | 64 | 0.737 | 1.093 | 1.172 | 18.713 | 0.453 |
| hop_1+aggregator | separate | 16 | 1 | 64 | 0.717 | 1.041 | 1.097 | 19.405 | 0.438 |
| hop_1+verifier | separate | 16 | 0 | 64 | 0.798 | 1.421 | 1.59 | 16.352 | 0.5 |
| hop_1+verifier | separate | 16 | 1 | 64 | 0.77 | 1.255 | 1.523 | 16.679 | 0.516 |
| hop_2+aggregator | separate | 16 | 0 | 64 | 0.706 | 1.042 | 1.104 | 18.684 | 0.484 |
| hop_2+aggregator | separate | 16 | 1 | 64 | 0.699 | 1.067 | 1.1 | 18.82 | 0.531 |
| hop_2+verifier | separate | 16 | 0 | 64 | 0.719 | 1.273 | 1.585 | 16.653 | 0.484 |
| hop_2+verifier | separate | 16 | 1 | 64 | 0.723 | 1.176 | 1.368 | 18.221 | 0.469 |

30 of 64 rows shown.

## hotpot_q15_7/shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 0.932 | 1.589 | 1.978 | 14.527 | 0.312 |
| all_small | shared | 16 | 1 | 64 | 0.598 | 0.943 | 0.994 | 22.67 | 0.312 |
| only_planner | shared | 16 | 0 | 64 | 1.915 | 2.742 | 2.993 | 7.65 | 0.359 |
| only_planner | shared | 16 | 1 | 64 | 1.481 | 2.42 | 2.816 | 9.456 | 0.359 |
| only_hop_1 | shared | 16 | 0 | 64 | 1.81 | 2.674 | 2.73 | 7.898 | 0.359 |
| only_hop_1 | shared | 16 | 1 | 64 | 1.449 | 2.21 | 2.328 | 9.816 | 0.375 |
| only_hop_2 | shared | 16 | 0 | 64 | 1.295 | 2.2 | 2.553 | 10.398 | 0.297 |
| only_hop_2 | shared | 16 | 1 | 64 | 1.342 | 2.183 | 2.875 | 10.505 | 0.328 |
| only_aggregator | shared | 16 | 0 | 64 | 1.543 | 2.362 | 2.449 | 9.135 | 0.469 |
| only_aggregator | shared | 16 | 1 | 64 | 1.24 | 1.968 | 2.199 | 11.266 | 0.469 |
| only_verifier | shared | 16 | 0 | 64 | 1.779 | 3.841 | 4.441 | 6.428 | 0.469 |
| only_verifier | shared | 16 | 1 | 64 | 1.533 | 2.616 | 2.767 | 9.041 | 0.5 |
| planner+hop_1 | shared | 16 | 0 | 64 | 1.719 | 2.574 | 2.595 | 8.373 | 0.344 |
| planner+hop_1 | shared | 16 | 1 | 64 | 1.683 | 2.62 | 2.72 | 8.389 | 0.312 |
| planner+hop_2 | shared | 16 | 0 | 64 | 1.692 | 2.716 | 2.998 | 7.916 | 0.359 |
| planner+hop_2 | shared | 16 | 1 | 64 | 1.623 | 2.755 | 2.774 | 8.328 | 0.359 |
| planner+aggregator | shared | 16 | 0 | 64 | 1.564 | 2.503 | 2.615 | 8.526 | 0.531 |
| planner+aggregator | shared | 16 | 1 | 64 | 1.59 | 2.506 | 2.53 | 8.449 | 0.531 |
| planner+verifier | shared | 16 | 0 | 64 | 1.753 | 2.835 | 3.618 | 7.627 | 0.516 |
| planner+verifier | shared | 16 | 1 | 64 | 1.793 | 2.829 | 3.558 | 7.52 | 0.516 |
| hop_1+hop_2 | shared | 16 | 0 | 64 | 1.455 | 2.166 | 2.344 | 9.557 | 0.375 |
| hop_1+hop_2 | shared | 16 | 1 | 64 | 1.493 | 2.24 | 2.349 | 9.519 | 0.375 |
| hop_1+aggregator | shared | 16 | 0 | 64 | 1.548 | 2.206 | 2.301 | 9.329 | 0.422 |
| hop_1+aggregator | shared | 16 | 1 | 64 | 1.48 | 2.136 | 2.212 | 9.221 | 0.438 |
| hop_1+verifier | shared | 16 | 0 | 64 | 1.641 | 2.556 | 2.716 | 8.672 | 0.516 |
| hop_1+verifier | shared | 16 | 1 | 64 | 1.609 | 2.415 | 2.709 | 8.671 | 0.516 |
| hop_2+aggregator | shared | 16 | 0 | 64 | 1.494 | 2.174 | 2.561 | 9.271 | 0.5 |
| hop_2+aggregator | shared | 16 | 1 | 64 | 1.453 | 2.099 | 2.313 | 9.767 | 0.484 |
| hop_2+verifier | shared | 16 | 0 | 64 | 1.516 | 2.675 | 2.932 | 8.567 | 0.469 |
| hop_2+verifier | shared | 16 | 1 | 64 | 1.487 | 2.829 | 3.009 | 8.898 | 0.453 |

30 of 64 rows shown.

## math_granite/separate

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 16 | 0 | 64 | 2.107 | 4.016 | 4.637 | 5.912 | 0.578 |
| all_small | separate | 16 | 1 | 64 | 2.075 | 3.883 | 4.545 | 5.318 | 0.609 |
| only_planner | separate | 16 | 0 | 64 | 2.605 | 4.329 | 4.667 | 4.981 | 0.547 |
| only_planner | separate | 16 | 1 | 64 | 2.588 | 4.31 | 4.712 | 4.728 | 0.641 |
| only_step_1 | separate | 16 | 0 | 64 | 2.025 | 3.812 | 4.165 | 4.645 | 0.547 |
| only_step_1 | separate | 16 | 1 | 64 | 2.065 | 3.654 | 4.911 | 5.375 | 0.562 |
| only_step_2 | separate | 16 | 0 | 64 | 2.163 | 3.595 | 4.859 | 4.905 | 0.484 |
| only_step_2 | separate | 16 | 1 | 64 | 2.088 | 4.456 | 4.974 | 5.222 | 0.547 |
| only_step_3 | separate | 16 | 0 | 64 | 2.148 | 3.708 | 3.975 | 5.538 | 0.484 |
| only_step_3 | separate | 16 | 1 | 64 | 2.12 | 3.664 | 4.649 | 5.856 | 0.531 |
| only_aggregator | separate | 16 | 0 | 64 | 2.324 | 4.71 | 5.494 | 4.679 | 0.594 |
| only_aggregator | separate | 16 | 1 | 64 | 2.342 | 4.402 | 5.489 | 4.886 | 0.562 |
| only_verifier | separate | 16 | 0 | 64 | 2.821 | 4.173 | 4.642 | 4.537 | 0.719 |
| only_verifier | separate | 16 | 1 | 64 | 2.897 | 4.316 | 4.66 | 4.5 | 0.719 |
| planner+step_1 | separate | 16 | 0 | 64 | 2.819 | 5.132 | 7.026 | 3.723 | 0.719 |
| planner+step_1 | separate | 16 | 1 | 64 | 2.793 | 5.128 | 6.35 | 3.832 | 0.688 |
| planner+step_2 | separate | 16 | 0 | 64 | 2.805 | 4.784 | 5.608 | 4.329 | 0.578 |
| planner+step_2 | separate | 16 | 1 | 64 | 2.861 | 4.738 | 5.476 | 3.774 | 0.562 |
| planner+step_3 | separate | 16 | 0 | 64 | 2.753 | 4.346 | 4.985 | 4.74 | 0.609 |
| planner+step_3 | separate | 16 | 1 | 64 | 2.863 | 4.459 | 4.716 | 4.792 | 0.609 |
| planner+aggregator | separate | 16 | 0 | 64 | 2.901 | 4.982 | 6.549 | 3.654 | 0.578 |
| planner+aggregator | separate | 16 | 1 | 64 | 3.147 | 5.141 | 6.543 | 3.204 | 0.609 |
| planner+verifier | separate | 16 | 0 | 64 | 3.536 | 5.845 | 6.058 | 3.791 | 0.672 |
| planner+verifier | separate | 16 | 1 | 64 | 3.437 | 5.856 | 7.539 | 3.263 | 0.641 |
| step_1+step_2 | separate | 16 | 0 | 64 | 2.273 | 3.882 | 5.316 | 3.961 | 0.562 |
| step_1+step_2 | separate | 16 | 1 | 64 | 2.236 | 3.685 | 3.892 | 4.628 | 0.609 |
| step_1+step_3 | separate | 16 | 0 | 64 | 2.185 | 3.957 | 4.216 | 5.368 | 0.547 |
| step_1+step_3 | separate | 16 | 1 | 64 | 2.226 | 3.795 | 4.298 | 5.13 | 0.594 |
| step_1+aggregator | separate | 16 | 0 | 64 | 2.449 | 4.856 | 6.639 | 4.415 | 0.578 |
| step_1+aggregator | separate | 16 | 1 | 64 | 2.378 | 4.601 | 4.982 | 4.811 | 0.578 |

30 of 128 rows shown.

## math_phi/separate

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 16 | 0 | 64 | 3.617 | 5.358 | 5.851 | 3.696 | 0.797 |
| all_small | separate | 16 | 1 | 64 | 3.611 | 5.387 | 5.996 | 3.838 | 0.797 |
| only_planner | separate | 16 | 0 | 64 | 3.996 | 6.237 | 7.157 | 3.296 | 0.797 |
| only_planner | separate | 16 | 1 | 64 | 4.019 | 6.224 | 6.685 | 3.245 | 0.828 |
| only_step_1 | separate | 16 | 0 | 64 | 4.783 | 7.137 | 7.877 | 2.739 | 0.781 |
| only_step_1 | separate | 16 | 1 | 64 | 4.776 | 7.069 | 7.161 | 2.778 | 0.812 |
| only_step_2 | separate | 16 | 0 | 64 | 4.145 | 5.974 | 6.336 | 3.276 | 0.781 |
| only_step_2 | separate | 16 | 1 | 64 | 4.127 | 6.377 | 6.814 | 3.019 | 0.812 |
| only_step_3 | separate | 16 | 0 | 64 | 4.288 | 6.502 | 6.762 | 3.078 | 0.734 |
| only_step_3 | separate | 16 | 1 | 64 | 4.23 | 5.889 | 6.334 | 3.23 | 0.797 |
| only_aggregator | separate | 16 | 0 | 64 | 4.217 | 7.751 | 9.122 | 2.651 | 0.812 |
| only_aggregator | separate | 16 | 1 | 64 | 4.328 | 8.814 | 9.225 | 2.706 | 0.828 |
| only_verifier | separate | 16 | 0 | 64 | 5.322 | 8.084 | 9.076 | 2.421 | 0.906 |
| only_verifier | separate | 16 | 1 | 64 | 5.251 | 8.026 | 8.823 | 2.32 | 0.922 |
| planner+step_1 | separate | 16 | 0 | 64 | 5.073 | 7.379 | 7.517 | 2.512 | 0.828 |
| planner+step_1 | separate | 16 | 1 | 64 | 5.058 | 7.456 | 7.707 | 2.505 | 0.844 |
| planner+step_2 | separate | 16 | 0 | 64 | 4.451 | 7.279 | 8.126 | 2.627 | 0.828 |
| planner+step_2 | separate | 16 | 1 | 64 | 4.575 | 7.295 | 8.521 | 2.623 | 0.828 |
| planner+step_3 | separate | 16 | 0 | 64 | 4.928 | 7.008 | 8.221 | 2.619 | 0.875 |
| planner+step_3 | separate | 16 | 1 | 64 | 4.954 | 7.009 | 8.07 | 2.637 | 0.859 |
| planner+aggregator | separate | 16 | 0 | 64 | 4.624 | 9.35 | 10.273 | 2.409 | 0.859 |
| planner+aggregator | separate | 16 | 1 | 64 | 4.673 | 9.339 | 9.529 | 2.361 | 0.891 |
| planner+verifier | separate | 16 | 0 | 64 | 5.881 | 9.421 | 10.486 | 2.012 | 0.906 |
| planner+verifier | separate | 16 | 1 | 64 | 5.96 | 9.449 | 11.321 | 2.057 | 0.875 |
| step_1+step_2 | separate | 16 | 0 | 64 | 5.132 | 7.568 | 7.76 | 2.574 | 0.812 |
| step_1+step_2 | separate | 16 | 1 | 64 | 4.977 | 7.711 | 8.338 | 2.513 | 0.828 |
| step_1+step_3 | separate | 16 | 0 | 64 | 5.304 | 7.865 | 8.151 | 2.395 | 0.766 |
| step_1+step_3 | separate | 16 | 1 | 64 | 5.451 | 7.743 | 7.892 | 2.48 | 0.734 |
| step_1+aggregator | separate | 16 | 0 | 64 | 5.848 | 8.977 | 9.32 | 2.141 | 0.859 |
| step_1+aggregator | separate | 16 | 1 | 64 | 5.695 | 9.676 | 10.286 | 2.095 | 0.875 |

30 of 128 rows shown.

## math_q15_7/separate

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 16 | 0 | 64 | 1.385 | 2.619 | 3.329 | 9.515 | 0.562 |
| all_small | separate | 16 | 1 | 64 | 1.289 | 2.502 | 2.975 | 9.366 | 0.531 |
| only_planner | separate | 16 | 0 | 64 | 1.433 | 2.587 | 2.738 | 8.408 | 0.5 |
| only_planner | separate | 16 | 1 | 64 | 1.498 | 2.687 | 2.791 | 8.676 | 0.5 |
| only_step_1 | separate | 16 | 0 | 64 | 1.129 | 2.052 | 2.378 | 9.119 | 0.469 |
| only_step_1 | separate | 16 | 1 | 64 | 1.062 | 2.149 | 2.297 | 8.935 | 0.5 |
| only_step_2 | separate | 16 | 0 | 64 | 1.451 | 2.571 | 2.897 | 8.57 | 0.484 |
| only_step_2 | separate | 16 | 1 | 64 | 1.409 | 2.391 | 2.884 | 9.254 | 0.469 |
| only_step_3 | separate | 16 | 0 | 64 | 1.241 | 2.491 | 2.842 | 9.998 | 0.422 |
| only_step_3 | separate | 16 | 1 | 64 | 1.375 | 2.4 | 2.555 | 10.058 | 0.516 |
| only_aggregator | separate | 16 | 0 | 64 | 1.649 | 2.985 | 3.213 | 7.394 | 0.625 |
| only_aggregator | separate | 16 | 1 | 64 | 1.599 | 3.048 | 3.437 | 7.668 | 0.641 |
| only_verifier | separate | 16 | 0 | 64 | 2.362 | 3.532 | 4.269 | 5.487 | 0.766 |
| only_verifier | separate | 16 | 1 | 64 | 2.322 | 3.442 | 3.623 | 5.627 | 0.812 |
| planner+step_1 | separate | 16 | 0 | 64 | 1.449 | 2.604 | 2.687 | 8.404 | 0.5 |
| planner+step_1 | separate | 16 | 1 | 64 | 1.34 | 2.641 | 3.061 | 7.787 | 0.484 |
| planner+step_2 | separate | 16 | 0 | 64 | 1.507 | 2.46 | 2.507 | 8.152 | 0.5 |
| planner+step_2 | separate | 16 | 1 | 64 | 1.492 | 2.393 | 2.832 | 8.425 | 0.5 |
| planner+step_3 | separate | 16 | 0 | 64 | 1.49 | 2.423 | 2.538 | 8.338 | 0.516 |
| planner+step_3 | separate | 16 | 1 | 64 | 1.486 | 2.327 | 2.587 | 9.068 | 0.531 |
| planner+aggregator | separate | 16 | 0 | 64 | 1.94 | 4.083 | 4.26 | 6.366 | 0.656 |
| planner+aggregator | separate | 16 | 1 | 64 | 1.914 | 3.962 | 4.154 | 6.651 | 0.672 |
| planner+verifier | separate | 16 | 0 | 64 | 2.673 | 3.886 | 4.169 | 5.003 | 0.781 |
| planner+verifier | separate | 16 | 1 | 64 | 2.601 | 3.874 | 3.927 | 5.23 | 0.797 |
| step_1+step_2 | separate | 16 | 0 | 64 | 1.086 | 2.359 | 2.998 | 9.178 | 0.484 |
| step_1+step_2 | separate | 16 | 1 | 64 | 1.077 | 2.258 | 2.374 | 9.241 | 0.5 |
| step_1+step_3 | separate | 16 | 0 | 64 | 1.089 | 1.947 | 2.957 | 8.948 | 0.469 |
| step_1+step_3 | separate | 16 | 1 | 64 | 1.025 | 2.075 | 2.694 | 9.113 | 0.469 |
| step_1+aggregator | separate | 16 | 0 | 64 | 1.453 | 3.186 | 4.089 | 7.867 | 0.656 |
| step_1+aggregator | separate | 16 | 1 | 64 | 1.517 | 3.346 | 3.76 | 6.962 | 0.688 |

30 of 128 rows shown.

## math_q15_7/shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 1.345 | 2.289 | 2.668 | 9.719 | 0.469 |
| all_small | shared | 16 | 1 | 64 | 1.361 | 2.758 | 3.028 | 7.953 | 0.484 |
| only_planner | shared | 16 | 0 | 64 | 3.316 | 6.902 | 7.214 | 4.096 | 0.547 |
| only_planner | shared | 16 | 1 | 64 | 3.245 | 6.286 | 6.737 | 4.154 | 0.547 |
| only_step_1 | shared | 16 | 0 | 64 | 2.336 | 4.547 | 5.101 | 5.322 | 0.531 |
| only_step_1 | shared | 16 | 1 | 64 | 2.372 | 5.556 | 6.341 | 4.798 | 0.453 |
| only_step_2 | shared | 16 | 0 | 64 | 3.017 | 5.41 | 5.849 | 4.48 | 0.484 |
| only_step_2 | shared | 16 | 1 | 64 | 2.861 | 5.671 | 6.341 | 4.719 | 0.531 |
| only_step_3 | shared | 16 | 0 | 64 | 3.058 | 5.838 | 6.321 | 4.506 | 0.516 |
| only_step_3 | shared | 16 | 1 | 64 | 2.857 | 5.781 | 6.373 | 4.808 | 0.547 |
| only_aggregator | shared | 16 | 0 | 64 | 4.175 | 8.227 | 9.23 | 3.102 | 0.578 |
| only_aggregator | shared | 16 | 1 | 64 | 4.348 | 7.745 | 8.958 | 2.884 | 0.594 |
| only_verifier | shared | 16 | 0 | 64 | 5.052 | 7.675 | 9.318 | 2.766 | 0.766 |
| only_verifier | shared | 16 | 1 | 64 | 5.199 | 7.568 | 9.343 | 2.742 | 0.766 |
| planner+step_1 | shared | 16 | 0 | 64 | 3.01 | 5.706 | 6.288 | 4.252 | 0.484 |
| planner+step_1 | shared | 16 | 1 | 64 | 3.023 | 6.346 | 6.604 | 4.006 | 0.5 |
| planner+step_2 | shared | 16 | 0 | 64 | 3.304 | 5.839 | 6.37 | 3.827 | 0.562 |
| planner+step_2 | shared | 16 | 1 | 64 | 3.352 | 5.7 | 6.763 | 3.925 | 0.531 |
| planner+step_3 | shared | 16 | 0 | 64 | 3.314 | 5.835 | 6.01 | 4.053 | 0.578 |
| planner+step_3 | shared | 16 | 1 | 64 | 3.302 | 5.691 | 5.966 | 3.994 | 0.594 |
| planner+aggregator | shared | 16 | 0 | 64 | 4.41 | 8.215 | 9.004 | 3.142 | 0.594 |
| planner+aggregator | shared | 16 | 1 | 64 | 4.319 | 8.627 | 8.933 | 3.138 | 0.625 |
| planner+verifier | shared | 16 | 0 | 64 | 5.21 | 7.565 | 8.048 | 2.824 | 0.781 |
| planner+verifier | shared | 16 | 1 | 64 | 5.118 | 6.932 | 7.538 | 2.853 | 0.828 |
| step_1+step_2 | shared | 16 | 0 | 64 | 2.702 | 4.859 | 5.699 | 4.505 | 0.594 |
| step_1+step_2 | shared | 16 | 1 | 64 | 2.704 | 4.98 | 7.539 | 4.445 | 0.516 |
| step_1+step_3 | shared | 16 | 0 | 64 | 2.588 | 5.936 | 7.355 | 4.43 | 0.547 |
| step_1+step_3 | shared | 16 | 1 | 64 | 2.425 | 4.95 | 6.905 | 4.881 | 0.531 |
| step_1+aggregator | shared | 16 | 0 | 64 | 3.327 | 6.459 | 7.149 | 3.757 | 0.672 |
| step_1+aggregator | shared | 16 | 1 | 64 | 3.33 | 7.054 | 8.031 | 3.716 | 0.672 |

30 of 128 rows shown.

## math_q3_14/separate

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 16 | 0 | 64 | 1.896 | 3.124 | 3.241 | 7.036 | 0.688 |
| all_small | separate | 16 | 1 | 64 | 1.912 | 2.75 | 2.86 | 7.315 | 0.719 |
| only_planner | separate | 16 | 0 | 64 | 2.719 | 3.891 | 3.948 | 4.986 | 0.719 |
| only_planner | separate | 16 | 1 | 64 | 2.665 | 3.788 | 3.892 | 4.714 | 0.734 |
| only_step_1 | separate | 16 | 0 | 64 | 2.617 | 4.21 | 4.429 | 4.277 | 0.688 |
| only_step_1 | separate | 16 | 1 | 64 | 2.592 | 3.992 | 4.179 | 4.875 | 0.766 |
| only_step_2 | separate | 16 | 0 | 64 | 2.594 | 4.15 | 5.07 | 4.712 | 0.703 |
| only_step_2 | separate | 16 | 1 | 64 | 2.586 | 4.281 | 4.612 | 4.756 | 0.719 |
| only_step_3 | separate | 16 | 0 | 64 | 2.588 | 3.983 | 4.258 | 5.267 | 0.766 |
| only_step_3 | separate | 16 | 1 | 64 | 2.546 | 3.873 | 4.248 | 5.331 | 0.75 |
| only_aggregator | separate | 16 | 0 | 64 | 2.126 | 3.003 | 4.991 | 5.899 | 0.781 |
| only_aggregator | separate | 16 | 1 | 64 | 2.129 | 2.923 | 3.111 | 6.468 | 0.797 |
| only_verifier | separate | 16 | 0 | 64 | 3.323 | 5.121 | 5.34 | 3.847 | 0.891 |
| only_verifier | separate | 16 | 1 | 64 | 3.399 | 5.141 | 5.33 | 3.834 | 0.844 |
| planner+step_1 | separate | 16 | 0 | 64 | 3.756 | 5.023 | 6.511 | 3.424 | 0.766 |
| planner+step_1 | separate | 16 | 1 | 64 | 3.67 | 5.242 | 6.568 | 3.28 | 0.781 |
| planner+step_2 | separate | 16 | 0 | 64 | 3.332 | 4.996 | 5.328 | 3.707 | 0.75 |
| planner+step_2 | separate | 16 | 1 | 64 | 3.297 | 4.916 | 5.244 | 3.955 | 0.703 |
| planner+step_3 | separate | 16 | 0 | 64 | 3.437 | 4.932 | 5.487 | 3.361 | 0.766 |
| planner+step_3 | separate | 16 | 1 | 64 | 3.452 | 4.902 | 5.682 | 3.401 | 0.766 |
| planner+aggregator | separate | 16 | 0 | 64 | 2.933 | 4.673 | 7.128 | 3.432 | 0.766 |
| planner+aggregator | separate | 16 | 1 | 64 | 2.915 | 4.314 | 4.975 | 3.393 | 0.734 |
| planner+verifier | separate | 16 | 0 | 64 | 4.12 | 6.046 | 6.487 | 3.151 | 0.891 |
| planner+verifier | separate | 16 | 1 | 64 | 4.227 | 5.88 | 6.343 | 2.899 | 0.891 |
| step_1+step_2 | separate | 16 | 0 | 64 | 3.632 | 5.566 | 5.871 | 3.497 | 0.734 |
| step_1+step_2 | separate | 16 | 1 | 64 | 3.671 | 5.432 | 5.834 | 3.529 | 0.734 |
| step_1+step_3 | separate | 16 | 0 | 64 | 3.387 | 5.252 | 5.456 | 3.865 | 0.766 |
| step_1+step_3 | separate | 16 | 1 | 64 | 3.296 | 5.275 | 6.442 | 3.54 | 0.75 |
| step_1+aggregator | separate | 16 | 0 | 64 | 2.978 | 4.412 | 4.737 | 4.469 | 0.75 |
| step_1+aggregator | separate | 16 | 1 | 64 | 2.949 | 4.627 | 5.639 | 4.472 | 0.844 |

30 of 128 rows shown.

## math_tiers/shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| aggregator=large | shared | 16 | 0 | 64 | 3.885 | 7.556 | 8.273 | 3.488 | 0.594 |
| aggregator=large | shared | 16 | 1 | 64 | 3.87 | 7.846 | 8.936 | 3.199 | 0.625 |
| aggregator=large+verifier=xl | shared | 16 | 0 | 64 | 9.731 | 16.368 | 16.87 | 1.37 | 0.906 |
| aggregator=large+verifier=xl | shared | 16 | 1 | 64 | 9.849 | 17.34 | 20.116 | 1.341 | 0.875 |
| aggregator=xl+verifier=xl | shared | 16 | 0 | 64 | 6.866 | 10.535 | 12.929 | 1.861 | 0.875 |
| aggregator=xl+verifier=xl | shared | 16 | 1 | 64 | 6.808 | 12.539 | 13.257 | 1.783 | 0.891 |
| all_small | shared | 16 | 0 | 64 | 1.373 | 2.583 | 3.369 | 9.37 | 0.531 |
| all_small | shared | 16 | 1 | 64 | 1.312 | 2.465 | 2.783 | 10.195 | 0.516 |
| planner=large+aggregator=large+verifier=xl | shared | 16 | 0 | 64 | 10.405 | 17.764 | 18.957 | 1.345 | 0.844 |
| planner=large+aggregator=large+verifier=xl | shared | 16 | 1 | 64 | 10.264 | 17.538 | 20.39 | 1.342 | 0.844 |
| planner=large+step_1=large+step_3=large+verifier=xl | shared | 16 | 0 | 64 | 9.282 | 15.989 | 17.442 | 1.377 | 0.828 |
| planner=large+step_1=large+step_3=large+verifier=xl | shared | 16 | 1 | 64 | 9.327 | 15.603 | 16.993 | 1.396 | 0.922 |
| planner=large+step_3=xl+verifier=xl | shared | 16 | 0 | 64 | 11.228 | 17.935 | 21.014 | 1.23 | 0.891 |
| planner=large+step_3=xl+verifier=xl | shared | 16 | 1 | 64 | 10.969 | 17.871 | 20.101 | 1.24 | 0.875 |
| step_1=large | shared | 16 | 0 | 64 | 2.39 | 4.982 | 5.447 | 4.835 | 0.516 |
| step_1=large | shared | 16 | 1 | 64 | 2.254 | 4.425 | 5.123 | 4.688 | 0.531 |
| step_1=large+step_2=xl+aggregator=large+verifier=xl | shared | 16 | 0 | 64 | 9.81 | 18.64 | 20.582 | 1.284 | 0.891 |
| step_1=large+step_2=xl+aggregator=large+verifier=xl | shared | 16 | 1 | 64 | 9.862 | 17.049 | 23.18 | 1.291 | 0.891 |
| step_2=large | shared | 16 | 0 | 64 | 2.685 | 5.263 | 6.867 | 4.819 | 0.516 |
| step_2=large | shared | 16 | 1 | 64 | 2.532 | 5.39 | 5.802 | 5.111 | 0.547 |
| step_2=large+aggregator=large | shared | 16 | 0 | 64 | 3.853 | 7.271 | 9.291 | 3.426 | 0.562 |
| step_2=large+aggregator=large | shared | 16 | 1 | 64 | 4.145 | 7.583 | 8.806 | 3.458 | 0.547 |
| step_2=large+verifier=large | shared | 16 | 0 | 64 | 4.695 | 7.825 | 8.223 | 2.969 | 0.844 |
| step_2=large+verifier=large | shared | 16 | 1 | 64 | 4.682 | 8.099 | 8.177 | 2.917 | 0.859 |
| verifier=large | shared | 16 | 0 | 64 | 5.035 | 7.742 | 9.717 | 2.769 | 0.781 |
| verifier=large | shared | 16 | 1 | 64 | 5.161 | 8.235 | 9.145 | 2.491 | 0.781 |
| verifier=xl | shared | 16 | 0 | 64 | 6.805 | 9.978 | 11.673 | 2.064 | 0.891 |
| verifier=xl | shared | 16 | 1 | 64 | 6.88 | 10.185 | 12.466 | 2.047 | 0.875 |
| planner=xl+step_1=xl+step_3=large+aggregator=large+verifier=large | shared | 16 | 0 | 64 | 10.315 | 17.055 | 17.549 | 1.351 | 0.812 |
| planner=xl+step_1=xl+step_3=large+aggregator=large+verifier=large | shared | 16 | 1 | 64 | 10.429 | 16.697 | 17.455 | 1.371 | 0.859 |

30 of 228 rows shown.
