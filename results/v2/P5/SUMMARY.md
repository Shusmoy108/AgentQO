# Phase P5

Generated 2026-11-16 19:20 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| separate | finished |
| separate_k1 | finished |
| separate_k32 | finished |
| shared | finished |

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
