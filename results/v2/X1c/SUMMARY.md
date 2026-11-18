# Phase X1c

Generated 2026-11-18 00:05 UTC, backend `vllm`.

Code run: `c1bb8338fa64acd82d82f1eb0c5a5ce6cb7b019b`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| a16_three_model/shared | finished |

## a16_three_model/shared

### placement_summary.csv

| plan | placement | k | repeat | n | p50_s | p95_s | p99_s | throughput_per_s | accuracy |
|---|---|---|---|---|---|---|---|---|---|
| aggregator=large+verifier=large | shared | 16 | 0 | 64 | 5.267 | 8.727 | 9.686 | 2.547 | 0.812 |
| aggregator=large+verifier=large | shared | 16 | 1 | 64 | 5.199 | 9.279 | 9.737 | 2.721 | 0.797 |
| planner=large+step_2=large | shared | 16 | 0 | 64 | 3.305 | 5.897 | 6.677 | 3.999 | 0.484 |
| planner=large+step_2=large | shared | 16 | 1 | 64 | 3.288 | 5.894 | 6.678 | 3.888 | 0.516 |
| planner=xl+step_1=xl+aggregator=xl | shared | 16 | 0 | 64 | 5.984 | 11.048 | 11.61 | 1.953 | 0.547 |
| planner=xl+step_1=xl+aggregator=xl | shared | 16 | 1 | 64 | 5.833 | 9.461 | 11.246 | 2.141 | 0.609 |
| planner=xl+step_2=xl | shared | 16 | 0 | 64 | 5.429 | 8.767 | 9.786 | 2.424 | 0.672 |
| planner=xl+step_2=xl | shared | 16 | 1 | 64 | 5.527 | 8.791 | 9.847 | 2.433 | 0.656 |
| planner=large+step_1=large+step_2=large+step_3=large+aggregator=xl+verifier=xl | shared | 16 | 0 | 64 | 7.939 | 13.772 | 15.145 | 1.71 | 0.844 |
| planner=large+step_1=large+step_2=large+step_3=large+aggregator=xl+verifier=xl | shared | 16 | 1 | 64 | 7.762 | 13.643 | 16.028 | 1.664 | 0.875 |
| planner=xl+step_1=large+step_2=large+step_3=large+aggregator=large+verifier=large | shared | 16 | 0 | 64 | 7.123 | 11.906 | 12.303 | 1.838 | 0.906 |
| planner=xl+step_1=large+step_2=large+step_3=large+aggregator=large+verifier=large | shared | 16 | 1 | 64 | 6.888 | 11.681 | 12.001 | 1.947 | 0.906 |
| step_2=large+verifier=xl | shared | 16 | 0 | 64 | 8.282 | 12.543 | 16.178 | 1.732 | 0.828 |
| step_2=large+verifier=xl | shared | 16 | 1 | 64 | 8.528 | 13.586 | 15.785 | 1.687 | 0.828 |
| planner=xl+aggregator=large | shared | 16 | 0 | 64 | 7.77 | 14.389 | 16.276 | 1.673 | 0.594 |
| planner=xl+aggregator=large | shared | 16 | 1 | 64 | 7.692 | 14.228 | 16.628 | 1.646 | 0.703 |
| planner=large+step_1=xl | shared | 16 | 0 | 64 | 6.684 | 12.559 | 14.435 | 1.869 | 0.609 |
| planner=large+step_1=xl | shared | 16 | 1 | 64 | 6.562 | 12.061 | 14.69 | 1.922 | 0.562 |
