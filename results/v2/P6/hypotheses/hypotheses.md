# Hypotheses: values per setting

Values and the code's flags as read in `prereg/v2_lease1.md` and `prereg/v2_amendments.md`. E-rows are exploratory. `-` = no data for that setting.

| item | math_q15_7 | hotpot_q15_7 | hotpot_iso_q15_7 | math_q3_14 | math_granite | hotpot_granite | hotpot_iso_granite | math_phi | hotpot_phi | complex_q15_7 |
|---|---|---|---|---|---|---|---|---|---|---|
| H1a ec_real / ec_synthetic best picks at budgets 1-2 | 1 / 1 | 2 / 2 | 1 / 1 | 1 / 1 | 1 / 2 | 0 / 0 | 2 / 0 | 1 / 1 | 1 / 0 | 1 / 1 |
| H1b confident_uv max regret, budgets 1-2 | 0.022 | 0.010 | 0.040 | 0.000 | 0.000 | 0.020 | 0.013 | 0.007 | 0.085 | 0.005 |
| A1 rerun share (<= 0.5) | 0.507 | 0.790 | 0.784 | 0.505 | 0.351 | 0.797 | 0.794 | 0.476 | 0.772 | 0.580 |
| A1 max UV change (<= 0.02) | 0.020 | 0.005 | 0.015 | 0.020 | 0.040 | 0.000 | 0.000 | 0.060 | 0.015 | 0.015 |
| A1/A10 top-2 agents same | yes | yes | yes | yes | no | yes | yes | yes | yes | yes |
| A1/A10 confident_uv budget-1/2 picks same | yes | yes | yes | yes | no | yes | yes | yes | no | yes |
| E3 exact-skip rerun share / max UV error | 0.848 / 0.000 | 0.909 / 0.000 | 0.924 / 0.000 | 0.995 / 0.000 | 0.879 / 0.005 | 0.819 / 0.000 | 0.824 / 0.000 | 1.000 / 0.000 | 1.000 / 0.000 | 0.881 / 0.000 |
| E3 key-skip rerun share / max UV error | 0.507 / 0.020 | 0.790 / 0.005 | 0.784 / 0.015 | 0.505 / 0.020 | 0.349 / 0.040 | 0.797 / 0.000 | 0.794 / 0.000 | 0.474 / 0.060 | 0.772 / 0.015 | 0.580 / 0.015 |
| H2 MAE held-out, independence_additive | 0.046 | 0.073 | 0.039 | 0.029 | 0.057 | 0.017 | 0.014 | 0.032 | 0.073 | 0.067 |
| H2 MAE held-out, independence_multiplicative | 0.065 | 0.118 | 0.039 | 0.036 | 0.097 | 0.017 | 0.014 | 0.033 | 0.092 | 0.080 |
| H2 MAE held-out, pairwise_corrected | 0.024 | 0.031 | 0.047 | 0.016 | 0.027 | 0.018 | 0.021 | 0.021 | 0.039 | 0.052 |
| H2 MAE held-out, logit_additive | 0.029 | 0.081 | 0.039 | 0.016 | 0.042 | 0.017 | 0.014 | 0.024 | 0.073 | 0.053 |
| H2b feasibility wrong p25: additive / pairwise | 0.000 / 0.000 | 0.087 / 0.087 | 0.174 / 0.217 | 0.111 / 0.111 | 0.056 / 0.056 | 0.348 / 0.348 | 0.130 / 0.130 | 0.074 / 0.074 | 0.174 / 0.174 | 0.139 / 0.139 |
| H2b feasibility wrong p50: additive / pairwise | 0.000 / 0.000 | 0.304 / 0.304 | 0.348 / 0.391 | 0.000 / 0.000 | 0.111 / 0.056 | 0.304 / 0.304 | 0.217 / 0.304 | 0.000 / 0.000 | 0.261 / 0.304 | 0.008 / 0.051 |
| H2b feasibility wrong p75: additive / pairwise | 0.130 / 0.278 | 0.391 / 0.391 | 0.304 / 0.348 | 0.259 / 0.278 | 0.222 / 0.259 | 0.130 / 0.174 | 0.174 / 0.348 | 0.241 / 0.296 | 0.522 / 0.565 | 0.222 / 0.196 |
| H3a best allocation differs, separate vs shared | yes | yes | yes | yes | yes | yes | no | yes | yes | yes |
| A2 joint hypervolume strictly higher | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| A2 max accuracy gap under (cost, p95) limits | 0.160 | 0.122 | 0.127 | 0.215 | 0.090 | 0.023 | 0.037 | 0.013 | 0.035 | 0.360 |
| H3c share of plans within 10% of measured p95 | 0.492 | - | - | - | - | - | - | - | - | - |
| H4a best plan differs, API vs GPU pricing | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| A3 Kendall tau, separate | 0.343 | 0.635 | 0.567 | 0.711 | 0.611 | 0.654 | 0.430 | 0.707 | 0.690 | 0.011 |
| A3 Kendall tau, shared | 0.344 | 0.832 | 0.791 | 0.794 | 0.730 | 0.754 | 0.503 | 0.712 | 0.681 | -0.054 |
| A3 Kendall tau, shared_mps | 0.311 | 0.526 | 0.631 | 0.777 | 0.693 | 0.686 | 0.512 | 0.751 | 0.718 | -0.088 |
| H5a mean gap / mean problems used | 0.000 / 398.375 | 0.000 / 393.875 | 0.000 / 303.875 | 0.000 / 400.000 | 0.000 / 400.000 | 0.000 / 397.000 | 0.000 / 333.750 | 0.000 / 400.000 | 0.000 / 397.750 | 0.000 / 200.000 |
| A4 agent (K samples), H6 match | verifier (5), no | aggregator (5), no | hop_2 (5), no | verifier (5), yes | verifier (5), no | aggregator (5), yes | aggregator (5), no | verifier (5), no | planner (3), no | verifier (5), no |

## Cost basis (A7, A11)

GPU cost per plan is `measured` only for P5 placement runs (`placement_costs.csv`). Every quality-phase plan cost is `estimated_rates` (a_m x prompt + b_m x completion, rates fitted on P5) or `fallback_latency` (no P5 rates for a model and placement: the per-call latency price).

| setting | P5 runs used | separate | shared | shared_mps | Pareto metric | Pareto has fallback |
|---|---|---|---|---|---|---|
| math_q15_7 | cal_granite_hotpot_separate, cal_granite_hotpot_shared, cal_granite_math_separate, cal_granite_math_shared, cal_phi_math_separate, cal_phi_math_shared, cal_qwen3_14_math_separate, cal_qwen3_14_math_shared, cal_qwen_hotpot_separate, cal_qwen_hotpot_shared, separate, separate_k1, separate_k32, shared, shared_k1, shared_k32, shared_mps, shared_mps_k1, shared_mps_k32 | estimated_rates 64 | estimated_rates 64 | estimated_rates 64 | gpu_usd_throughput | no |
| hotpot_q15_7 | cal_granite_hotpot_separate, cal_granite_hotpot_shared, cal_granite_math_separate, cal_granite_math_shared, cal_phi_math_separate, cal_phi_math_shared, cal_qwen3_14_math_separate, cal_qwen3_14_math_shared, cal_qwen_hotpot_separate, cal_qwen_hotpot_shared, separate, separate_k1, separate_k32, shared, shared_k1, shared_k32, shared_mps, shared_mps_k1, shared_mps_k32 | estimated_rates 32 | estimated_rates 32 | estimated_rates 32 | gpu_usd_throughput | no |
| hotpot_iso_q15_7 | cal_granite_hotpot_separate, cal_granite_hotpot_shared, cal_granite_math_separate, cal_granite_math_shared, cal_phi_math_separate, cal_phi_math_shared, cal_qwen3_14_math_separate, cal_qwen3_14_math_shared, cal_qwen_hotpot_separate, cal_qwen_hotpot_shared, separate, separate_k1, separate_k32, shared, shared_k1, shared_k32, shared_mps, shared_mps_k1, shared_mps_k32 | estimated_rates 32 | estimated_rates 32 | estimated_rates 32 | gpu_usd_throughput | no |
| math_q3_14 | cal_granite_hotpot_separate, cal_granite_hotpot_shared, cal_granite_math_separate, cal_granite_math_shared, cal_phi_math_separate, cal_phi_math_shared, cal_qwen3_14_math_separate, cal_qwen3_14_math_shared, cal_qwen_hotpot_separate, cal_qwen_hotpot_shared, separate, separate_k1, separate_k32, shared, shared_k1, shared_k32, shared_mps, shared_mps_k1, shared_mps_k32 | estimated_rates 64 | estimated_rates 64 | fallback_latency 64 | gpu_usd_throughput | yes |
| math_granite | cal_granite_hotpot_separate, cal_granite_hotpot_shared, cal_granite_math_separate, cal_granite_math_shared, cal_phi_math_separate, cal_phi_math_shared, cal_qwen3_14_math_separate, cal_qwen3_14_math_shared, cal_qwen_hotpot_separate, cal_qwen_hotpot_shared, separate, separate_k1, separate_k32, shared, shared_k1, shared_k32, shared_mps, shared_mps_k1, shared_mps_k32 | estimated_rates 64 | estimated_rates 64 | fallback_latency 64 | gpu_usd_throughput | yes |
| hotpot_granite | cal_granite_hotpot_separate, cal_granite_hotpot_shared, cal_granite_math_separate, cal_granite_math_shared, cal_phi_math_separate, cal_phi_math_shared, cal_qwen3_14_math_separate, cal_qwen3_14_math_shared, cal_qwen_hotpot_separate, cal_qwen_hotpot_shared, separate, separate_k1, separate_k32, shared, shared_k1, shared_k32, shared_mps, shared_mps_k1, shared_mps_k32 | estimated_rates 32 | estimated_rates 32 | fallback_latency 32 | gpu_usd_throughput | yes |
| hotpot_iso_granite | cal_granite_hotpot_separate, cal_granite_hotpot_shared, cal_granite_math_separate, cal_granite_math_shared, cal_phi_math_separate, cal_phi_math_shared, cal_qwen3_14_math_separate, cal_qwen3_14_math_shared, cal_qwen_hotpot_separate, cal_qwen_hotpot_shared, separate, separate_k1, separate_k32, shared, shared_k1, shared_k32, shared_mps, shared_mps_k1, shared_mps_k32 | estimated_rates 32 | estimated_rates 32 | fallback_latency 32 | gpu_usd_throughput | yes |
| math_phi | cal_granite_hotpot_separate, cal_granite_hotpot_shared, cal_granite_math_separate, cal_granite_math_shared, cal_phi_math_separate, cal_phi_math_shared, cal_qwen3_14_math_separate, cal_qwen3_14_math_shared, cal_qwen_hotpot_separate, cal_qwen_hotpot_shared, separate, separate_k1, separate_k32, shared, shared_k1, shared_k32, shared_mps, shared_mps_k1, shared_mps_k32 | estimated_rates 64 | estimated_rates 64 | fallback_latency 64 | gpu_usd_throughput | yes |
| hotpot_phi | cal_granite_hotpot_separate, cal_granite_hotpot_shared, cal_granite_math_separate, cal_granite_math_shared, cal_phi_math_separate, cal_phi_math_shared, cal_qwen3_14_math_separate, cal_qwen3_14_math_shared, cal_qwen_hotpot_separate, cal_qwen_hotpot_shared, separate, separate_k1, separate_k32, shared, shared_k1, shared_k32, shared_mps, shared_mps_k1, shared_mps_k32 | estimated_rates 32 | estimated_rates 32 | fallback_latency 32 | gpu_usd_throughput | yes |
| complex_q15_7 | cal_granite_hotpot_separate, cal_granite_hotpot_shared, cal_granite_math_separate, cal_granite_math_shared, cal_phi_math_separate, cal_phi_math_shared, cal_qwen3_14_math_separate, cal_qwen3_14_math_shared, cal_qwen_hotpot_separate, cal_qwen_hotpot_shared, separate, separate_k1, separate_k32, shared, shared_k1, shared_k32, shared_mps, shared_mps_k1, shared_mps_k32 | estimated_rates 1024 | estimated_rates 1024 | estimated_rates 1024 | gpu_usd_throughput | no |
