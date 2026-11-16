# Phase P5

Generated 2026-11-16 19:20 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| cal_granite_math_shared | finished |
| cal_qwen3_14_math_shared | finished |

## cal_granite_math_shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 2.046 | 3.776 | 4.035 | 5.592 | 0.547 |
| all_small | shared | 16 | 1 | 64 | 1.999 | 3.49 | 3.568 | 6.268 | 0.578 |
| all_small | shared | 16 | 2 | 64 | 2.074 | 3.758 | 5.013 | 4.522 | 0.578 |
| all_large | shared | 16 | 0 | 64 | 4.536 | 7.469 | 8.573 | 2.569 | 0.766 |
| all_large | shared | 16 | 1 | 64 | 4.313 | 7.045 | 8.997 | 2.643 | 0.828 |
| all_large | shared | 16 | 2 | 64 | 4.309 | 7.056 | 8.447 | 3.003 | 0.859 |

## cal_qwen3_14_math_shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 1.967 | 2.767 | 2.919 | 6.773 | 0.75 |
| all_small | shared | 16 | 1 | 64 | 1.868 | 2.874 | 3.036 | 7.062 | 0.703 |
| all_small | shared | 16 | 2 | 64 | 1.856 | 2.78 | 2.91 | 7.278 | 0.688 |
| all_large | shared | 16 | 0 | 64 | 7.366 | 10.757 | 11.917 | 1.772 | 0.812 |
| all_large | shared | 16 | 1 | 64 | 7.382 | 10.322 | 11.72 | 1.562 | 0.812 |
| all_large | shared | 16 | 2 | 64 | 6.999 | 10.249 | 11.914 | 1.688 | 0.859 |
