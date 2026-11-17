# Phase P5

Generated 2026-11-17 05:34 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| cal_granite_hotpot_shared | finished |
| cal_granite_math_shared | finished |
| cal_phi_math_shared | finished |
| cal_qwen3_14_math_shared | finished |

## cal_granite_hotpot_shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 2.902 | 4.343 | 5.792 | 4.922 | 0.5 |
| all_small | shared | 16 | 1 | 64 | 2.985 | 4.361 | 4.985 | 4.79 | 0.516 |
| all_small | shared | 16 | 2 | 64 | 2.947 | 4.496 | 5.359 | 4.711 | 0.531 |
| all_large | shared | 16 | 0 | 64 | 5.716 | 9.828 | 10.204 | 2.446 | 0.578 |
| all_large | shared | 16 | 1 | 64 | 5.654 | 8.876 | 9.719 | 2.478 | 0.609 |
| all_large | shared | 16 | 2 | 64 | 5.629 | 9.727 | 10.242 | 2.431 | 0.609 |

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

## cal_phi_math_shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 3.697 | 5.351 | 5.447 | 3.821 | 0.797 |
| all_small | shared | 16 | 1 | 64 | 3.692 | 5.675 | 6.033 | 3.769 | 0.766 |
| all_small | shared | 16 | 2 | 64 | 3.59 | 5.987 | 6.608 | 3.683 | 0.828 |
| all_large | shared | 16 | 0 | 64 | 8.879 | 14.32 | 15.062 | 1.305 | 0.953 |
| all_large | shared | 16 | 1 | 64 | 9.11 | 14.133 | 16.681 | 1.369 | 0.938 |
| all_large | shared | 16 | 2 | 64 | 9.181 | 13.876 | 16.674 | 1.352 | 0.922 |

## cal_qwen3_14_math_shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| all_small | shared | 16 | 0 | 64 | 1.924 | 2.766 | 2.884 | 7.124 | 0.688 |
| all_small | shared | 16 | 1 | 64 | 1.886 | 2.854 | 3.041 | 6.643 | 0.703 |
| all_small | shared | 16 | 2 | 64 | 1.919 | 2.884 | 3.289 | 6.648 | 0.703 |
| all_large | shared | 16 | 0 | 64 | 7.366 | 10.757 | 11.917 | 1.772 | 0.812 |
| all_large | shared | 16 | 1 | 64 | 7.382 | 10.322 | 11.72 | 1.562 | 0.812 |
| all_large | shared | 16 | 2 | 64 | 6.999 | 10.249 | 11.914 | 1.688 | 0.859 |
