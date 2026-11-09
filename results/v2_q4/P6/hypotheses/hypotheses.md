# Hypotheses: values per setting

Setting q4 (A12): Qwen2.5 1.5B/7B Q4_K_M via Ollama on a Mac. A separate 4-bit setting, never pooled with vLLM data.

Values and the code's flags as read in `prereg/v2_lease1.md` and `prereg/v2_amendments.md`. E-rows are exploratory. `-` = no data for that setting.

| item | math_q15_7 | hotpot_q15_7 |
|---|---|---|
| H1a ec_real / ec_synthetic best picks at budgets 1-2 | 1 / 1 | 0 / 0 |
| H1b confident_uv max regret, budgets 1-2 | 0.045 | 0.005 |
| A1 rerun share (<= 0.5) | 0.616 | 0.831 |
| A1 max UV change (<= 0.02) | 0.030 | 0.010 |
| A1/A10 top-2 agents same | yes | yes |
| A1/A10 confident_uv budget-1/2 picks same | yes | yes |
| E3 exact-skip rerun share / max UV error | 0.891 / 0.000 | 0.935 / 0.000 |
| E3 key-skip rerun share / max UV error | 0.616 / 0.030 | 0.831 / 0.010 |
| H2 MAE held-out, independence_additive | 0.089 | 0.067 |
| H2 MAE held-out, independence_multiplicative | 0.114 | 0.129 |
| H2 MAE held-out, pairwise_corrected | 0.043 | 0.035 |
| H2 MAE held-out, logit_additive | 0.059 | 0.071 |
| H2b feasibility wrong p25: additive / pairwise | 0.037 / 0.037 | 0.000 / 0.000 |
| H2b feasibility wrong p50: additive / pairwise | 0.000 / 0.000 | 0.130 / 0.261 |
| H2b feasibility wrong p75: additive / pairwise | 0.204 / 0.204 | 0.174 / 0.435 |
| H3a best allocation differs, separate vs shared | not testable on Mac | not testable on Mac |
| A2 joint hypervolume strictly higher | not testable on Mac | not testable on Mac |
| A2 max accuracy gap under (cost, p95) limits | not testable on Mac | not testable on Mac |
| H3c share of plans within 10% of measured p95 | not testable on Mac | not testable on Mac |
| H4a best plan differs, API vs GPU pricing | not testable on Mac | not testable on Mac |
| A3 Kendall tau, separate | not testable on Mac | not testable on Mac |
| A3 Kendall tau, shared | not testable on Mac | not testable on Mac |
| A3 Kendall tau, shared_mps | not testable on Mac | not testable on Mac |
| H5a mean gap / mean problems used | 0.000 / 198.875 | 0.000 / 199.375 |
| A4 agent (K samples), H6 match | verifier (5), no | aggregator (5), no |

## Cost basis (A12)

Not testable on Mac: placement (H3a, A2, H3c) and GPU throughput cost (A3, H4a). Costs are API prices from token counts only (`cost/plan_costs.csv` api_usd, `pareto_api/`, `pareto_estimated/`).

