# Phase P5

Generated 2026-11-16 21:09 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| cal_qwen_hotpot_shared | finished |
| separate | finished |
| separate_k1 | finished |
| separate_k32 | finished |
| shared | finished |
| shared_k1 | finished |
| shared_k32 | finished |
| shared_mps | finished |
| shared_mps_k1 | finished |
| shared_mps_k32 | finished |

## cal_qwen_hotpot_shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 0.991 | 1.561 | 1.664 | 14.65 | 0.297 |
| all_small | shared | 16 | 1 | 64 | 0.626 | 0.98 | 1.006 | 21.702 | 0.312 |
| all_small | shared | 16 | 2 | 64 | 0.646 | 0.994 | 1.087 | 21.397 | 0.297 |
| all_large | shared | 16 | 0 | 64 | 2.72 | 4.272 | 4.94 | 5.099 | 0.547 |
| all_large | shared | 16 | 1 | 64 | 1.195 | 1.689 | 2.051 | 11.309 | 0.547 |
| all_large | shared | 16 | 2 | 64 | 1.205 | 1.693 | 2.032 | 11.271 | 0.531 |

## separate

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 16 | 0 | 64 | 1.491 | 2.564 | 2.665 | 9.209 | 0.516 |
| all_small | separate | 16 | 1 | 64 | 1.314 | 2.39 | 2.991 | 9.616 | 0.516 |
| all_small | separate | 16 | 2 | 64 | 1.378 | 2.367 | 2.765 | 9.734 | 0.562 |
| only_planner | separate | 16 | 0 | 64 | 1.455 | 2.549 | 2.806 | 8.673 | 0.531 |
| only_planner | separate | 16 | 1 | 64 | 1.44 | 2.291 | 2.705 | 8.955 | 0.484 |
| only_planner | separate | 16 | 2 | 64 | 1.458 | 2.493 | 2.689 | 8.798 | 0.562 |
| only_aggregator | separate | 16 | 0 | 64 | 1.627 | 3.076 | 3.436 | 7.85 | 0.609 |
| only_aggregator | separate | 16 | 1 | 64 | 1.698 | 3.292 | 3.861 | 8.05 | 0.562 |
| only_aggregator | separate | 16 | 2 | 64 | 1.609 | 3.062 | 3.445 | 8.261 | 0.578 |
| only_verifier | separate | 16 | 0 | 64 | 2.424 | 3.518 | 4.157 | 5.197 | 0.797 |
| only_verifier | separate | 16 | 1 | 64 | 2.438 | 3.506 | 4.069 | 5.415 | 0.781 |
| only_verifier | separate | 16 | 2 | 64 | 2.428 | 3.457 | 4.062 | 5.743 | 0.797 |
| planner+verifier | separate | 16 | 0 | 64 | 2.661 | 3.623 | 3.706 | 5.198 | 0.766 |
| planner+verifier | separate | 16 | 1 | 64 | 2.619 | 3.578 | 3.746 | 5.279 | 0.797 |
| planner+verifier | separate | 16 | 2 | 64 | 2.688 | 3.62 | 3.937 | 5.182 | 0.844 |
| aggregator+verifier | separate | 16 | 0 | 64 | 2.598 | 5.249 | 5.442 | 4.566 | 0.828 |
| aggregator+verifier | separate | 16 | 1 | 64 | 2.58 | 4.559 | 4.829 | 4.832 | 0.797 |
| aggregator+verifier | separate | 16 | 2 | 64 | 2.59 | 4.461 | 4.884 | 4.817 | 0.797 |
| all_large | separate | 16 | 0 | 64 | 2.653 | 5.188 | 5.405 | 4.071 | 0.844 |
| all_large | separate | 16 | 1 | 64 | 2.594 | 5.005 | 5.318 | 3.821 | 0.828 |
| all_large | separate | 16 | 2 | 64 | 2.666 | 5.104 | 5.324 | 4.028 | 0.844 |

## separate_k1

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 1 | 0 | 64 | 1.119 | 2.081 | 2.448 | 0.845 | 0.562 |
| all_small | separate | 1 | 1 | 64 | 1.119 | 2.081 | 2.449 | 0.845 | 0.562 |
| all_small | separate | 1 | 2 | 64 | 1.119 | 2.081 | 2.448 | 0.845 | 0.562 |
| only_planner | separate | 1 | 0 | 64 | 1.211 | 2.018 | 2.276 | 0.75 | 0.562 |
| only_planner | separate | 1 | 1 | 64 | 1.228 | 2.017 | 2.295 | 0.752 | 0.578 |
| only_planner | separate | 1 | 2 | 64 | 1.211 | 2.017 | 2.281 | 0.752 | 0.578 |
| only_aggregator | separate | 1 | 0 | 64 | 1.441 | 3.101 | 3.176 | 0.63 | 0.625 |
| only_aggregator | separate | 1 | 1 | 64 | 1.428 | 3.101 | 3.448 | 0.628 | 0.609 |
| only_aggregator | separate | 1 | 2 | 64 | 1.427 | 3.099 | 3.448 | 0.629 | 0.609 |
| only_verifier | separate | 1 | 0 | 64 | 2.237 | 3.155 | 3.365 | 0.455 | 0.734 |
| only_verifier | separate | 1 | 1 | 64 | 2.232 | 3.152 | 3.368 | 0.455 | 0.734 |
| only_verifier | separate | 1 | 2 | 64 | 2.233 | 3.156 | 3.373 | 0.455 | 0.734 |
| planner+verifier | separate | 1 | 0 | 64 | 2.561 | 3.37 | 3.511 | 0.419 | 0.828 |
| planner+verifier | separate | 1 | 1 | 64 | 2.582 | 3.371 | 3.508 | 0.415 | 0.828 |
| planner+verifier | separate | 1 | 2 | 64 | 2.58 | 3.369 | 3.513 | 0.415 | 0.828 |
| aggregator+verifier | separate | 1 | 0 | 64 | 2.392 | 4.275 | 4.508 | 0.412 | 0.797 |
| aggregator+verifier | separate | 1 | 1 | 64 | 2.395 | 4.275 | 4.509 | 0.412 | 0.781 |
| aggregator+verifier | separate | 1 | 2 | 64 | 2.395 | 4.273 | 4.504 | 0.412 | 0.781 |
| all_large | separate | 1 | 0 | 64 | 2.536 | 4.808 | 5.007 | 0.358 | 0.844 |
| all_large | separate | 1 | 1 | 64 | 2.509 | 4.807 | 5.004 | 0.359 | 0.844 |
| all_large | separate | 1 | 2 | 64 | 2.509 | 4.809 | 5.004 | 0.359 | 0.844 |

## separate_k32

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | separate | 32 | 0 | 64 | 1.436 | 3.253 | 3.517 | 13.174 | 0.5 |
| all_small | separate | 32 | 1 | 64 | 1.602 | 3.12 | 3.442 | 12.983 | 0.453 |
| all_small | separate | 32 | 2 | 64 | 1.426 | 2.706 | 3.271 | 13.467 | 0.484 |
| only_planner | separate | 32 | 0 | 64 | 1.589 | 2.641 | 3.038 | 13.294 | 0.516 |
| only_planner | separate | 32 | 1 | 64 | 1.602 | 2.792 | 2.958 | 13.419 | 0.547 |
| only_planner | separate | 32 | 2 | 64 | 1.751 | 2.845 | 2.989 | 13.134 | 0.547 |
| only_aggregator | separate | 32 | 0 | 64 | 1.804 | 2.97 | 3.68 | 12.4 | 0.625 |
| only_aggregator | separate | 32 | 1 | 64 | 1.777 | 3.503 | 3.645 | 12.544 | 0.594 |
| only_aggregator | separate | 32 | 2 | 64 | 1.74 | 3.541 | 4.314 | 11.514 | 0.625 |
| only_verifier | separate | 32 | 0 | 64 | 2.544 | 3.709 | 4.701 | 8.806 | 0.781 |
| only_verifier | separate | 32 | 1 | 64 | 2.582 | 3.728 | 4.624 | 7.927 | 0.781 |
| only_verifier | separate | 32 | 2 | 64 | 2.605 | 3.624 | 4.044 | 8.863 | 0.75 |
| planner+verifier | separate | 32 | 0 | 64 | 2.72 | 3.72 | 3.779 | 8.698 | 0.828 |
| planner+verifier | separate | 32 | 1 | 64 | 2.789 | 3.702 | 3.781 | 8.631 | 0.797 |
| planner+verifier | separate | 32 | 2 | 64 | 2.809 | 3.724 | 4.183 | 8.585 | 0.75 |
| aggregator+verifier | separate | 32 | 0 | 64 | 2.666 | 4.496 | 5.015 | 7.933 | 0.781 |
| aggregator+verifier | separate | 32 | 1 | 64 | 2.638 | 4.485 | 5.002 | 8.003 | 0.797 |
| aggregator+verifier | separate | 32 | 2 | 64 | 2.655 | 4.4 | 5.011 | 8.522 | 0.797 |
| all_large | separate | 32 | 0 | 64 | 2.792 | 5.096 | 5.336 | 7.166 | 0.844 |
| all_large | separate | 32 | 1 | 64 | 2.795 | 5.003 | 5.559 | 6.28 | 0.859 |
| all_large | separate | 32 | 2 | 64 | 2.832 | 5.253 | 5.557 | 6.061 | 0.844 |

## shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 1.341 | 2.641 | 2.885 | 9.539 | 0.609 |
| all_small | shared | 16 | 1 | 64 | 1.335 | 2.527 | 2.672 | 8.836 | 0.484 |
| all_small | shared | 16 | 2 | 64 | 1.401 | 2.338 | 3.342 | 9.243 | 0.547 |
| only_planner | shared | 16 | 0 | 64 | 3.125 | 6.57 | 7.235 | 4.161 | 0.484 |
| only_planner | shared | 16 | 1 | 64 | 3.242 | 6.579 | 6.952 | 4.118 | 0.453 |
| only_planner | shared | 16 | 2 | 64 | 3.39 | 6.105 | 6.967 | 4.002 | 0.453 |
| only_aggregator | shared | 16 | 0 | 64 | 4.032 | 7.381 | 8.594 | 3.322 | 0.594 |
| only_aggregator | shared | 16 | 1 | 64 | 3.977 | 7.401 | 9.069 | 3.32 | 0.578 |
| only_aggregator | shared | 16 | 2 | 64 | 4.042 | 7.267 | 8.495 | 3.337 | 0.578 |
| only_verifier | shared | 16 | 0 | 64 | 5.059 | 8.149 | 9.576 | 2.508 | 0.781 |
| only_verifier | shared | 16 | 1 | 64 | 5.039 | 8.092 | 9.506 | 2.707 | 0.75 |
| only_verifier | shared | 16 | 2 | 64 | 5.021 | 8.088 | 9.6 | 2.712 | 0.75 |
| planner+verifier | shared | 16 | 0 | 64 | 5.27 | 7.784 | 8.262 | 2.649 | 0.828 |
| planner+verifier | shared | 16 | 1 | 64 | 5.043 | 7.849 | 8.359 | 2.749 | 0.828 |
| planner+verifier | shared | 16 | 2 | 64 | 5.215 | 7.789 | 8.234 | 2.634 | 0.797 |
| aggregator+verifier | shared | 16 | 0 | 64 | 5.303 | 8.834 | 10.277 | 2.547 | 0.766 |
| aggregator+verifier | shared | 16 | 1 | 64 | 5.187 | 8.759 | 10.033 | 2.562 | 0.781 |
| aggregator+verifier | shared | 16 | 2 | 64 | 5.364 | 8.745 | 10.218 | 2.564 | 0.797 |
| all_large | shared | 16 | 0 | 64 | 2.686 | 5.026 | 5.352 | 4.09 | 0.859 |
| all_large | shared | 16 | 1 | 64 | 2.579 | 4.98 | 5.283 | 4.109 | 0.859 |
| all_large | shared | 16 | 2 | 64 | 2.577 | 4.818 | 5.277 | 4.24 | 0.828 |

## shared_k1

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 1 | 0 | 64 | 1.082 | 2.017 | 2.267 | 0.893 | 0.5 |
| all_small | shared | 1 | 1 | 64 | 1.083 | 2.015 | 2.277 | 0.895 | 0.5 |
| all_small | shared | 1 | 2 | 64 | 1.083 | 2.024 | 2.271 | 0.895 | 0.5 |
| only_planner | shared | 1 | 0 | 64 | 1.322 | 2.104 | 2.33 | 0.74 | 0.453 |
| only_planner | shared | 1 | 1 | 64 | 1.321 | 2.098 | 2.355 | 0.743 | 0.453 |
| only_planner | shared | 1 | 2 | 64 | 1.318 | 2.095 | 2.353 | 0.744 | 0.453 |
| only_aggregator | shared | 1 | 0 | 64 | 1.415 | 3.019 | 3.097 | 0.635 | 0.609 |
| only_aggregator | shared | 1 | 1 | 64 | 1.437 | 2.96 | 3.095 | 0.636 | 0.609 |
| only_aggregator | shared | 1 | 2 | 64 | 1.436 | 2.959 | 3.11 | 0.636 | 0.609 |
| only_verifier | shared | 1 | 0 | 64 | 2.161 | 3.078 | 3.688 | 0.471 | 0.75 |
| only_verifier | shared | 1 | 1 | 64 | 2.163 | 3.072 | 3.685 | 0.47 | 0.75 |
| only_verifier | shared | 1 | 2 | 64 | 2.163 | 3.073 | 3.683 | 0.47 | 0.75 |
| planner+verifier | shared | 1 | 0 | 64 | 2.446 | 3.652 | 3.802 | 0.416 | 0.781 |
| planner+verifier | shared | 1 | 1 | 64 | 2.447 | 3.654 | 3.797 | 0.416 | 0.766 |
| planner+verifier | shared | 1 | 2 | 64 | 2.441 | 3.65 | 3.795 | 0.416 | 0.766 |
| aggregator+verifier | shared | 1 | 0 | 64 | 2.407 | 4.434 | 4.775 | 0.409 | 0.797 |
| aggregator+verifier | shared | 1 | 1 | 64 | 2.41 | 4.438 | 4.759 | 0.409 | 0.797 |
| aggregator+verifier | shared | 1 | 2 | 64 | 2.411 | 4.433 | 4.756 | 0.409 | 0.797 |
| all_large | shared | 1 | 0 | 64 | 2.422 | 4.742 | 4.94 | 0.369 | 0.844 |
| all_large | shared | 1 | 1 | 64 | 2.434 | 4.745 | 4.939 | 0.372 | 0.844 |
| all_large | shared | 1 | 2 | 64 | 2.422 | 4.74 | 4.94 | 0.369 | 0.859 |

## shared_k32

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 32 | 0 | 64 | 1.514 | 2.757 | 2.887 | 12.771 | 0.578 |
| all_small | shared | 32 | 1 | 64 | 1.592 | 2.577 | 2.994 | 13.726 | 0.578 |
| all_small | shared | 32 | 2 | 64 | 1.594 | 2.751 | 3.661 | 13.263 | 0.609 |
| only_planner | shared | 32 | 0 | 64 | 3.209 | 6.462 | 7.392 | 7.6 | 0.484 |
| only_planner | shared | 32 | 1 | 64 | 3.356 | 6.229 | 7.136 | 7.205 | 0.5 |
| only_planner | shared | 32 | 2 | 64 | 3.319 | 6.279 | 7.216 | 7.415 | 0.516 |
| only_aggregator | shared | 32 | 0 | 64 | 4.552 | 7.243 | 7.987 | 5.428 | 0.547 |
| only_aggregator | shared | 32 | 1 | 64 | 4.395 | 7.951 | 8.162 | 5.303 | 0.656 |
| only_aggregator | shared | 32 | 2 | 64 | 4.503 | 8.248 | 9.138 | 4.313 | 0.625 |
| only_verifier | shared | 32 | 0 | 64 | 5.151 | 8.497 | 9.069 | 4.539 | 0.781 |
| only_verifier | shared | 32 | 1 | 64 | 4.929 | 8.036 | 8.449 | 4.666 | 0.812 |
| only_verifier | shared | 32 | 2 | 64 | 5.017 | 8.449 | 9.147 | 4.638 | 0.734 |
| planner+verifier | shared | 32 | 0 | 64 | 5.41 | 7.733 | 8.618 | 4.44 | 0.859 |
| planner+verifier | shared | 32 | 1 | 64 | 5.393 | 8.308 | 8.453 | 4.117 | 0.812 |
| planner+verifier | shared | 32 | 2 | 64 | 5.405 | 8.35 | 8.605 | 4.404 | 0.797 |
| aggregator+verifier | shared | 32 | 0 | 64 | 5.474 | 9.178 | 9.244 | 4.441 | 0.766 |
| aggregator+verifier | shared | 32 | 1 | 64 | 5.467 | 9.008 | 10.152 | 4.693 | 0.766 |
| aggregator+verifier | shared | 32 | 2 | 64 | 5.526 | 9.208 | 9.551 | 4.325 | 0.812 |
| all_large | shared | 32 | 0 | 64 | 2.779 | 5.222 | 5.557 | 5.794 | 0.844 |
| all_large | shared | 32 | 1 | 64 | 2.681 | 5.082 | 5.545 | 6.948 | 0.828 |
| all_large | shared | 32 | 2 | 64 | 2.728 | 5.236 | 5.541 | 5.476 | 0.875 |

## shared_mps

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared_mps | 16 | 0 | 64 | 1.498 | 2.62 | 2.828 | 8.567 | 0.562 |
| all_small | shared_mps | 16 | 1 | 64 | 1.464 | 2.742 | 3.279 | 8.371 | 0.516 |
| all_small | shared_mps | 16 | 2 | 64 | 1.482 | 2.612 | 3.266 | 9.259 | 0.516 |
| only_planner | shared_mps | 16 | 0 | 64 | 2.574 | 5.365 | 5.911 | 4.999 | 0.531 |
| only_planner | shared_mps | 16 | 1 | 64 | 2.607 | 4.596 | 5.26 | 5.015 | 0.531 |
| only_planner | shared_mps | 16 | 2 | 64 | 2.703 | 5.396 | 6.212 | 4.859 | 0.594 |
| only_aggregator | shared_mps | 16 | 0 | 64 | 3.409 | 5.954 | 6.09 | 3.782 | 0.656 |
| only_aggregator | shared_mps | 16 | 1 | 64 | 3.529 | 6.593 | 8.098 | 3.901 | 0.641 |
| only_aggregator | shared_mps | 16 | 2 | 64 | 3.427 | 6.851 | 7.18 | 3.72 | 0.594 |
| only_verifier | shared_mps | 16 | 0 | 64 | 4.268 | 6.671 | 7.361 | 3.177 | 0.781 |
| only_verifier | shared_mps | 16 | 1 | 64 | 4.111 | 6.884 | 8.176 | 3.22 | 0.797 |
| only_verifier | shared_mps | 16 | 2 | 64 | 4.324 | 6.661 | 8.175 | 3.227 | 0.797 |
| planner+verifier | shared_mps | 16 | 0 | 64 | 3.847 | 6.399 | 7.61 | 3.336 | 0.828 |
| planner+verifier | shared_mps | 16 | 1 | 64 | 3.89 | 6.63 | 7.278 | 3.205 | 0.812 |
| planner+verifier | shared_mps | 16 | 2 | 64 | 4.002 | 6.186 | 6.49 | 3.376 | 0.812 |
| aggregator+verifier | shared_mps | 16 | 0 | 64 | 4.443 | 7.422 | 8.585 | 2.779 | 0.812 |
| aggregator+verifier | shared_mps | 16 | 1 | 64 | 4.429 | 7.172 | 7.66 | 2.983 | 0.781 |
| aggregator+verifier | shared_mps | 16 | 2 | 64 | 4.186 | 7.151 | 8.551 | 2.788 | 0.797 |
| all_large | shared_mps | 16 | 0 | 64 | 2.711 | 5.125 | 5.261 | 4.379 | 0.828 |
| all_large | shared_mps | 16 | 1 | 64 | 2.827 | 5.155 | 5.523 | 3.759 | 0.828 |
| all_large | shared_mps | 16 | 2 | 64 | 2.82 | 5.136 | 5.26 | 4.205 | 0.844 |

## shared_mps_k1

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared_mps | 1 | 0 | 64 | 1.212 | 2.171 | 2.422 | 0.79 | 0.547 |
| all_small | shared_mps | 1 | 1 | 64 | 1.206 | 2.297 | 2.423 | 0.785 | 0.547 |
| all_small | shared_mps | 1 | 2 | 64 | 1.21 | 2.299 | 2.429 | 0.785 | 0.547 |
| only_planner | shared_mps | 1 | 0 | 64 | 1.351 | 2.268 | 2.647 | 0.706 | 0.562 |
| only_planner | shared_mps | 1 | 1 | 64 | 1.352 | 2.265 | 2.754 | 0.702 | 0.562 |
| only_planner | shared_mps | 1 | 2 | 64 | 1.351 | 2.269 | 2.754 | 0.702 | 0.562 |
| only_aggregator | shared_mps | 1 | 0 | 64 | 1.583 | 3.246 | 4.409 | 0.584 | 0.578 |
| only_aggregator | shared_mps | 1 | 1 | 64 | 1.586 | 3.246 | 4.41 | 0.585 | 0.578 |
| only_aggregator | shared_mps | 1 | 2 | 64 | 1.582 | 3.245 | 4.404 | 0.584 | 0.578 |
| only_verifier | shared_mps | 1 | 0 | 64 | 2.369 | 3.257 | 3.67 | 0.443 | 0.797 |
| only_verifier | shared_mps | 1 | 1 | 64 | 2.366 | 3.258 | 3.67 | 0.443 | 0.797 |
| only_verifier | shared_mps | 1 | 2 | 64 | 2.367 | 3.254 | 3.669 | 0.443 | 0.797 |
| planner+verifier | shared_mps | 1 | 0 | 64 | 2.44 | 3.793 | 4.453 | 0.409 | 0.812 |
| planner+verifier | shared_mps | 1 | 1 | 64 | 2.436 | 3.793 | 4.455 | 0.409 | 0.812 |
| planner+verifier | shared_mps | 1 | 2 | 64 | 2.44 | 3.799 | 4.459 | 0.409 | 0.812 |
| aggregator+verifier | shared_mps | 1 | 0 | 64 | 2.491 | 4.302 | 5.68 | 0.393 | 0.812 |
| aggregator+verifier | shared_mps | 1 | 1 | 64 | 2.505 | 4.296 | 5.672 | 0.393 | 0.797 |
| aggregator+verifier | shared_mps | 1 | 2 | 64 | 2.505 | 4.3 | 5.678 | 0.393 | 0.797 |
| all_large | shared_mps | 1 | 0 | 64 | 2.545 | 4.762 | 5.065 | 0.357 | 0.844 |
| all_large | shared_mps | 1 | 1 | 64 | 2.542 | 4.761 | 5.065 | 0.357 | 0.844 |
| all_large | shared_mps | 1 | 2 | 64 | 2.542 | 4.763 | 5.066 | 0.356 | 0.844 |

## shared_mps_k32

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared_mps | 32 | 0 | 64 | 1.666 | 3.195 | 3.609 | 11.978 | 0.547 |
| all_small | shared_mps | 32 | 1 | 64 | 1.64 | 3.054 | 3.416 | 13.38 | 0.531 |
| all_small | shared_mps | 32 | 2 | 64 | 1.727 | 3.081 | 3.526 | 12.722 | 0.547 |
| only_planner | shared_mps | 32 | 0 | 64 | 2.657 | 4.925 | 5.594 | 8.812 | 0.5 |
| only_planner | shared_mps | 32 | 1 | 64 | 2.645 | 5.033 | 5.868 | 8.449 | 0.531 |
| only_planner | shared_mps | 32 | 2 | 64 | 2.705 | 4.957 | 5.817 | 8.603 | 0.5 |
| only_aggregator | shared_mps | 32 | 0 | 64 | 3.405 | 6.146 | 6.936 | 5.922 | 0.578 |
| only_aggregator | shared_mps | 32 | 1 | 64 | 3.481 | 6.227 | 6.581 | 6.532 | 0.641 |
| only_aggregator | shared_mps | 32 | 2 | 64 | 3.413 | 6.406 | 7.095 | 5.906 | 0.625 |
| only_verifier | shared_mps | 32 | 0 | 64 | 4.231 | 6.263 | 6.7 | 5.5 | 0.781 |
| only_verifier | shared_mps | 32 | 1 | 64 | 4.067 | 5.796 | 6.7 | 5.305 | 0.75 |
| only_verifier | shared_mps | 32 | 2 | 64 | 4.068 | 6.701 | 8.42 | 4.752 | 0.781 |
| planner+verifier | shared_mps | 32 | 0 | 64 | 4.082 | 6.751 | 7.523 | 5.199 | 0.797 |
| planner+verifier | shared_mps | 32 | 1 | 64 | 4.107 | 6.437 | 6.65 | 5.149 | 0.812 |
| planner+verifier | shared_mps | 32 | 2 | 64 | 4.079 | 6.617 | 8.459 | 5.138 | 0.812 |
| aggregator+verifier | shared_mps | 32 | 0 | 64 | 4.248 | 7.626 | 8.569 | 4.428 | 0.828 |
| aggregator+verifier | shared_mps | 32 | 1 | 64 | 4.211 | 7.883 | 8.673 | 4.644 | 0.781 |
| aggregator+verifier | shared_mps | 32 | 2 | 64 | 4.204 | 7.024 | 8.29 | 4.942 | 0.766 |
| all_large | shared_mps | 32 | 0 | 64 | 2.912 | 5.144 | 5.225 | 7.297 | 0.859 |
| all_large | shared_mps | 32 | 1 | 64 | 2.896 | 5.299 | 5.514 | 6.894 | 0.875 |
| all_large | shared_mps | 32 | 2 | 64 | 2.938 | 5.277 | 5.923 | 5.813 | 0.844 |
