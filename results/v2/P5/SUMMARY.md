# Phase P5

Generated 2026-11-16 18:25 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| separate | finished |

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
