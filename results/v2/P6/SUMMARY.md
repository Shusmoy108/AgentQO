# Phase P6

Generated 2026-11-17 05:52 UTC, backend `vllm`.

Code run: `252a12bfb53acc15c4530509b778daeba2a5dd19`; packaged at `252a12bfb53acc15c4530509b778daeba2a5dd19`.

| step | status |
|---|---|
| complex_q15_7/adaptive | finished |
| complex_q15_7/cost | finished |
| complex_q15_7/pareto | finished |
| complex_q15_7/pareto_api | finished |
| complex_q15_7/pareto_estimated | finished |
| complex_q15_7/routing | finished |
| complex_q15_7/rules | finished |
| hotpot_granite/adaptive | finished |
| hotpot_granite/cost | finished |
| hotpot_granite/pareto | finished |
| hotpot_granite/pareto_api | finished |
| hotpot_granite/pareto_estimated | finished |
| hotpot_granite/routing | finished |
| hotpot_granite/rules | finished |
| hotpot_iso_granite/adaptive | finished |
| hotpot_iso_granite/cost | finished |
| hotpot_iso_granite/pareto | finished |
| hotpot_iso_granite/pareto_api | finished |
| hotpot_iso_granite/pareto_estimated | finished |
| hotpot_iso_granite/routing | finished |
| hotpot_iso_granite/rules | finished |
| hotpot_iso_q15_7/adaptive | finished |
| hotpot_iso_q15_7/cost | finished |
| hotpot_iso_q15_7/pareto | finished |
| hotpot_iso_q15_7/pareto_api | finished |
| hotpot_iso_q15_7/pareto_estimated | finished |
| hotpot_iso_q15_7/routing | finished |
| hotpot_iso_q15_7/rules | finished |
| hotpot_phi/adaptive | finished |
| hotpot_phi/cost | finished |
| hotpot_phi/pareto | finished |
| hotpot_phi/pareto_api | finished |
| hotpot_phi/pareto_estimated | finished |
| hotpot_phi/routing | finished |
| hotpot_phi/rules | finished |
| hotpot_q15_7/adaptive | finished |
| hotpot_q15_7/cost | finished |
| hotpot_q15_7/pareto | finished |
| hotpot_q15_7/pareto_api | finished |
| hotpot_q15_7/pareto_estimated | finished |
| hotpot_q15_7/routing | finished |
| hotpot_q15_7/rules | finished |
| hypotheses | finished |
| math_granite/adaptive | finished |
| math_granite/cost | finished |
| math_granite/pareto | finished |
| math_granite/pareto_api | finished |
| math_granite/pareto_estimated | finished |
| math_granite/routing | finished |
| math_granite/rules | finished |
| math_phi/adaptive | finished |
| math_phi/cost | finished |
| math_phi/pareto | finished |
| math_phi/pareto_api | finished |
| math_phi/pareto_estimated | finished |
| math_phi/routing | finished |
| math_phi/rules | finished |
| math_q15_7/adaptive | finished |
| math_q15_7/cost | finished |
| math_q15_7/pareto | finished |
| math_q15_7/pareto_api | finished |
| math_q15_7/pareto_estimated | finished |
| math_q15_7/routing | finished |
| math_q15_7/rules | finished |
| math_q3_14/adaptive | finished |
| math_q3_14/cost | finished |
| math_q3_14/pareto | finished |
| math_q3_14/pareto_api | finished |
| math_q3_14/pareto_estimated | finished |
| math_q3_14/routing | finished |
| math_q3_14/rules | finished |
| math_tiers/tiers | finished |

## complex_q15_7/cost

### plan_costs.csv

| plan | n_problems | tokens_out_small | tokens_out_large | tokens_in_small | tokens_in_large | tokens_in | tokens_out | api_usd | gpu_seconds | gpu_seconds_shared | cost_units | model_small | model_large | gpu_usd_latency | gpu_usd_latency_1 | gpu_usd_latency_shared_1 | gpu_usd_latency_2 | gpu_usd_latency_shared_2 | gpu_usd_latency_4 | gpu_usd_latency_shared_4 | gpu_usd_throughput_separate | gpu_cost_basis_separate | gpu_usd_throughput_shared | gpu_cost_basis_shared | gpu_usd_throughput_shared_mps | gpu_cost_basis_shared_mps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_small | 200 | 874.32 | 0 | 3078.74 | 0 | 3078.74 | 874.32 | 7.45e-04 | 8.45 | 2.112 | 10 | Qwen/Qwen2.5-1.5B-Instruct |  | 0.005 | 0.002 | 5.87e-04 | 0.005 | 0.001 | 0.009 | 0.002 | 0.002 | estimated_rates | 6.84e-04 | estimated_rates | 7.30e-04 | estimated_rates |
| only_researcher_1 | 200 | 587.45 | 7.84 | 2423.15 | 245.55 | 2668.7 | 595.29 | 0.001 | 5.949 | 1.537 | 13 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.003 | 0.002 | 4.27e-04 | 0.003 | 8.54e-04 | 0.007 | 0.002 | 0.002 | estimated_rates | 4.74e-04 | estimated_rates | 5.07e-04 | estimated_rates |
| only_researcher_2 | 200 | 628.015 | 9.895 | 2461.76 | 245.55 | 2707.31 | 637.91 | 0.001 | 6.245 | 1.62 | 13 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.003 | 0.002 | 4.50e-04 | 0.003 | 9.00e-04 | 0.007 | 0.002 | 0.002 | estimated_rates | 5.08e-04 | estimated_rates | 5.43e-04 | estimated_rates |
| only_formatter | 200 | 866.255 | 8.165 | 2839.34 | 239.4 | 3078.74 | 874.42 | 0.001 | 8.522 | 2.184 | 13 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.005 | 0.002 | 6.07e-04 | 0.005 | 0.001 | 0.009 | 0.002 | 0.002 | estimated_rates | 6.91e-04 | estimated_rates | 7.34e-04 | estimated_rates |
| researcher_1+researcher_2 | 200 | 357.545 | 17.735 | 1820.1 | 491.1 | 2311.2 | 375.28 | 0.002 | 3.859 | 1.074 | 16 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.002 | 0.001 | 2.98e-04 | 0.002 | 5.96e-04 | 0.004 | 0.001 | 9.28e-04 | estimated_rates | 3.11e-04 | estimated_rates | 3.33e-04 | estimated_rates |

5 of 1024 rows shown.

### placement_costs.csv

| run | plan | placement | gpu_seconds_per_problem | gpu_usd_throughput | source | repeats |
|---|---|---|---|---|---|---|
| cal_granite_hotpot_separate | all_large | separate | 0.851 | 4.73e-04 | measured | 3 |
| cal_granite_hotpot_separate | all_small | separate | 0.434 | 2.41e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_large | shared | 0.408 | 2.27e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_small | shared | 0.208 | 1.16e-04 | measured | 3 |
| cal_granite_math_separate | all_large | separate | 0.774 | 4.30e-04 | measured | 3 |
| cal_granite_math_separate | all_small | separate | 0.333 | 1.85e-04 | measured | 3 |
| cal_granite_math_shared | all_large | shared | 0.367 | 2.04e-04 | measured | 3 |
| cal_granite_math_shared | all_small | shared | 0.187 | 1.04e-04 | measured | 3 |
| cal_phi_math_separate | all_large | separate | 1.486 | 8.26e-04 | measured | 3 |
| cal_phi_math_separate | all_small | separate | 0.536 | 2.98e-04 | measured | 3 |
| cal_phi_math_shared | all_large | shared | 0.745 | 4.14e-04 | measured | 3 |
| cal_phi_math_shared | all_small | shared | 0.266 | 1.48e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_large | separate | 1.219 | 6.77e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_small | separate | 0.282 | 1.57e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_large | shared | 0.599 | 3.33e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_small | shared | 0.147 | 8.17e-05 | measured | 3 |
| cal_qwen_hotpot_separate | all_large | separate | 0.251 | 1.39e-04 | measured | 3 |
| cal_qwen_hotpot_separate | all_small | separate | 0.106 | 5.87e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_large | shared | 0.124 | 6.91e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_small | shared | 0.054 | 2.98e-05 | measured | 3 |
| separate | aggregator+verifier | separate | 0.422 | 2.35e-04 | measured | 3 |
| separate | all_large | separate | 0.504 | 2.80e-04 | measured | 3 |
| separate | all_small | separate | 0.21 | 1.17e-04 | measured | 3 |
| separate | only_aggregator | separate | 0.248 | 1.38e-04 | measured | 3 |
| separate | only_planner | separate | 0.227 | 1.26e-04 | measured | 3 |
| separate | only_verifier | separate | 0.367 | 2.04e-04 | measured | 3 |
| separate | planner+verifier | separate | 0.383 | 2.13e-04 | measured | 3 |
| separate_k1 | aggregator+verifier | separate | 4.857 | 0.003 | measured | 3 |
| separate_k1 | all_large | separate | 5.576 | 0.003 | measured | 3 |
| separate_k1 | all_small | separate | 2.367 | 0.001 | measured | 3 |

30 of 83 rows shown.

### cost_summary

```json
{
  "n_plans": 1024,
  "api_large_small_ratio": 11.519313212551362,
  "a3_kendall_tau_latency_vs_units": -0.11182637143580083,
  "p5_runs": [
    "cal_granite_hotpot_separate",
    "cal_granite_hotpot_shared",
    "cal_granite_math_separate",
    "cal_granite_math_shared",
    "cal_phi_math_separate",
    "cal_phi_math_shared",
    "cal_qwen3_14_math_separate",
    "cal_qwen3_14_math_shared",
    "cal_qwen_hotpot_separate",
    "cal_qwen_hotpot_shared",
    "separate",
    "separate_k1",
    "separate_k32",
    "shared",
    "shared_k1",
    "shared_k32",
    "shared_mps",
    "shared_mps_k1",
    "shared_mps_k32"
  ],
  "gpu_cost_basis": {
    "separate": {
      "estimated_rates": 1024
    },
    "shared": {
      "estimated_rates": 1024
    },
    "shared_mps": {
      "estimated_rates": 1024
    }
  },
  "a3_kendall_tau_separate": 0.01089922368810994,
  "a3_basis_separate": "estimated_rates",
  "a3_kendall_tau_shared": -0.05384855653932712,
  "a3_basis_shared": "estimated_rates",
  "a3_kendall_tau_shared_mps": -0.08835015004277699,
  "a3_basis_shared_mps": "estimated_rates"
}
```

## complex_q15_7/pareto

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+researcher_1+step_1_1+step_2_1+verifier | separate | 0.88 | 0.002 | 9.102 | estimated_rates |
| planner+researcher_1+step_1_1+step_2_1+verifier | shared | 0.88 | 6.41e-04 | 22.074 | estimated_rates |
| planner+researcher_1+step_1_1+step_2_1+verifier | shared_mps | 0.88 | 6.60e-04 | 17.123 | estimated_rates |
| planner+step_1_1+verifier | separate | 0.875 | 0.001 | 10.198 | estimated_rates |
| planner+step_1_2+step_2_1+verifier | separate | 0.875 | 0.001 | 9.269 | estimated_rates |
| planner+researcher_1+step_2_1+verifier | separate | 0.87 | 0.001 | 9.102 | estimated_rates |
| planner+researcher_1+step_2_1+verifier | shared | 0.87 | 6.37e-04 | 22.08 | estimated_rates |
| planner+researcher_1+step_2_1+verifier | shared_mps | 0.87 | 6.58e-04 | 17.123 | estimated_rates |
| researcher_2+step_2_1+step_2_2+aggregator+verifier | separate | 0.87 | 0.001 | 9.499 | estimated_rates |
| planner+researcher_1+step_1_1+step_2_1+step_2_2+verifier | separate | 0.865 | 0.002 | 9.017 | estimated_rates |

10 of 107 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 11.388 | planner+researcher_1+step_1_1+step_2_1+verifier | 0.88 |
| shared | 11.388 | planner+researcher_1+researcher_2+step_1_1+step_1_2+step_2_1+step_2_2+aggregator+verifier | 0.82 |
| shared_mps | 11.388 | planner+researcher_1+researcher_2+step_1_1+step_2_1+verifier | 0.83 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | researcher_1+step_1_2+aggregator | 0.615 | gpu_usd_throughput_separate | planner+researcher_1+step_1_1+step_2_1+verifier | 0.88 | True | estimated_rates |
| 0.5 | researcher_1+aggregator+verifier | 0.86 | gpu_usd_throughput_separate | planner+researcher_1+step_1_1+step_2_1+verifier | 0.88 | True | estimated_rates |
| 0.75 | planner+researcher_1+step_1_1+step_2_1+verifier | 0.88 | gpu_usd_throughput_separate | planner+researcher_1+step_1_1+step_2_1+verifier | 0.88 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 3072
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 3072,
  "n_front": 107,
  "hypervolume_joint": 0.5817597439932973,
  "hypervolume_two_step": 0.2306187538838121,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.36,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 11.38825107600178,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## complex_q15_7/pareto_api

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+researcher_1+step_1_1+step_2_1+verifier | separate | 0.88 | 0.006 | 9.102 | api |
| planner+step_1_1+verifier | separate | 0.875 | 0.005 | 10.198 | api |
| planner+step_1_2+step_2_1+verifier | separate | 0.875 | 0.006 | 9.269 | api |
| planner+researcher_1+step_2_1+verifier | separate | 0.87 | 0.005 | 9.102 | api |
| researcher_2+step_2_1+step_2_2+aggregator+verifier | separate | 0.87 | 0.005 | 9.499 | api |
| planner+researcher_1+step_1_1+step_2_1+step_2_2+verifier | separate | 0.865 | 0.006 | 9.017 | api |
| researcher_1+aggregator+verifier | separate | 0.86 | 0.004 | 10.91 | api |
| researcher_2+aggregator+verifier | separate | 0.86 | 0.004 | 9.559 | api |
| researcher_1+researcher_2+step_1_1+step_1_2+aggregator+verifier | separate | 0.86 | 0.006 | 8.731 | api |
| only_verifier | separate | 0.855 | 0.003 | 9.717 | api |

10 of 86 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 11.388 | planner+researcher_1+step_1_1+step_2_1+verifier | 0.88 |
| shared | 11.388 | planner+researcher_1+researcher_2+step_1_1+step_1_2+step_2_1+step_2_2+aggregator+verifier | 0.82 |
| shared_mps | 11.388 | planner+researcher_1+researcher_2+step_1_1+step_2_1+verifier | 0.83 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | researcher_1+step_1_2+aggregator | 0.615 | gpu_usd_throughput_separate | planner+researcher_1+step_1_1+step_2_1+verifier | 0.88 | True | estimated_rates |
| 0.5 | researcher_1+aggregator+verifier | 0.86 | gpu_usd_throughput_separate | planner+researcher_1+step_1_1+step_2_1+verifier | 0.88 | True | estimated_rates |
| 0.75 | planner+researcher_1+step_1_1+step_2_1+verifier | 0.88 | gpu_usd_throughput_separate | planner+researcher_1+step_1_1+step_2_1+verifier | 0.88 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "api_usd",
  "cost_metric_requested": "api_usd",
  "cost_basis_counts": {
    "api": 3072
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 3072,
  "n_front": 86,
  "hypervolume_joint": 0.5805650481227292,
  "hypervolume_two_step": 0.5079426666157661,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.36,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 11.38825107600178,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## complex_q15_7/pareto_estimated

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| step_1_1+step_1_2+step_2_1+step_2_2+verifier | separate | 0.94 | 0.001 | 7.982 | estimated_rates |
| step_1_1+step_1_2+step_2_1+step_2_2+verifier | shared | 0.94 | 6.91e-04 | 21.216 | estimated_rates |
| step_1_1+step_1_2+step_2_1+step_2_2+verifier | shared_mps | 0.94 | 7.09e-04 | 17.095 | estimated_rates |
| planner+step_1_1+step_1_2+step_2_1+step_2_2+verifier | shared_mps | 0.935 | 7.11e-04 | 16.354 | estimated_rates |
| researcher_1+step_1_1+step_1_2+step_2_2+verifier | separate | 0.93 | 0.001 | 9.073 | estimated_rates |
| researcher_1+step_1_1+step_1_2+step_2_1+step_2_2+verifier | separate | 0.93 | 0.001 | 7.979 | estimated_rates |
| researcher_1+step_1_1+step_1_2+step_2_1+step_2_2+verifier | shared | 0.93 | 5.70e-04 | 21.071 | estimated_rates |
| researcher_1+step_1_1+step_1_2+step_2_1+step_2_2+verifier | shared_mps | 0.93 | 5.83e-04 | 17.065 | estimated_rates |
| planner+researcher_1+step_1_1+step_1_2+step_2_1+step_2_2+verifier | shared_mps | 0.925 | 6.24e-04 | 16.345 | estimated_rates |
| researcher_1+step_1_1+step_2_1+step_2_2+verifier | separate | 0.92 | 0.001 | 7.979 | estimated_rates |

10 of 118 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 11.388 | step_1_1+step_1_2+step_2_1+step_2_2+verifier | 0.94 |
| shared | 11.388 | planner+researcher_1+researcher_2+step_1_1+step_1_2+step_2_1+step_2_2+aggregator+verifier | 0.805 |
| shared_mps | 11.388 | planner+researcher_1+researcher_2+step_1_1+step_1_2+step_2_1+step_2_2+verifier | 0.835 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | step_1_1+aggregator | 0.61 | gpu_usd_throughput_separate | step_1_1+step_1_2+step_2_1+step_2_2+verifier | 0.94 | True | estimated_rates |
| 0.5 | step_1_1+step_1_2+verifier | 0.905 | gpu_usd_throughput_separate | step_1_1+step_1_2+step_2_1+step_2_2+verifier | 0.94 | True | estimated_rates |
| 0.75 | step_1_1+step_1_2+step_2_2+verifier | 0.94 | gpu_usd_throughput_separate | step_1_1+step_1_2+step_2_1+step_2_2+verifier | 0.94 | True | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 3072
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 3072,
  "n_front": 118,
  "hypervolume_joint": 0.6147963091815514,
  "hypervolume_two_step": 0.34115939018044317,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.3400000000000001,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 11.38825107600178,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "regret_hypervolume": 0.011424705499727072,
  "regret_accuracy_mean": 0.017242990654205613
}
```

## complex_q15_7/routing

### routing.csv

| agent | rule | threshold | routed_share | accuracy | cost | baseline_accuracy | fixed_accuracy | fixed_cost | h6_match | primary |
|---|---|---|---|---|---|---|---|---|---|---|
| verifier | samples_disagree |  | 0.74 | 0.805 | 0.003 | 0.58 | 0.82 | 0.003 | False | True |
| verifier | entropy | 0 | 0.74 | 0.805 | 0.003 | 0.58 | 0.82 | 0.003 | False | False |
| verifier | entropy | 0.5 | 0.74 | 0.805 | 0.003 | 0.58 | 0.82 | 0.003 | False | False |
| verifier | entropy | 1 | 0.495 | 0.755 | 0.002 | 0.58 | 0.82 | 0.003 | False | False |
| verifier | baseline_vs_majority |  | 0.355 | 0.75 | 0.002 | 0.58 | 0.82 | 0.003 | False | False |
| planner | baseline_vs_majority |  | 0.465 | 0.605 | 0.003 | 0.58 | 0.54 | 0.002 | False | False |
| researcher_1 | samples_disagree |  | 0.91 | 0.6 | 0.002 | 0.58 | 0.6 | 0.001 | False | False |
| researcher_1 | entropy | 0 | 0.91 | 0.6 | 0.002 | 0.58 | 0.6 | 0.001 | False | False |

8 of 50 rows shown.

### routing_summary

```json
{
  "a4_agent": "verifier",
  "a4_rule": "samples_disagree (K small samples not unanimous)",
  "a4_k_samples": 5,
  "a4_h6_match": false,
  "a4_row": {
    "agent": "verifier",
    "rule": "samples_disagree",
    "threshold": "",
    "routed_share": 0.74,
    "accuracy": 0.805,
    "cost": 0.002696325,
    "baseline_accuracy": 0.58,
    "fixed_accuracy": 0.82,
    "fixed_cost": 0.0027062189999999997,
    "h6_match": false,
    "primary": true
  },
  "note": "all other rows in routing.csv are exploratory"
}
```

## complex_q15_7/rules

### rule_plans.csv

| rule | budget | upgraded | accuracy | best_accuracy_at_budget | regret | is_best |
|---|---|---|---|---|---|---|
| structural_topk | 1 | planner | 0.56 | 0.855 | 0.295 | False |
| structural_topk | 2 | planner,researcher_1 | 0.51 | 0.855 | 0.345 | False |
| structural_topk | 3 | planner,researcher_1,researcher_2 | 0.385 | 0.875 | 0.49 | False |
| structural_topk | 4 | planner,researcher_1,researcher_2,step_1_1 | 0.425 | 0.875 | 0.45 | False |
| structural_topk | 5 | planner,researcher_1,researcher_2,step_1_1,step_2_1 | 0.42 | 0.88 | 0.46 | False |
| structural_topk | 6 | planner,researcher_1,researcher_2,step_1_1,step_1_2,step_2_1 | 0.405 | 0.88 | 0.475 | False |
| structural_topk | 7 | planner,researcher_1,researcher_2,step_1_1,step_1_2,step_2_1,step_2_2 | 0.39 | 0.88 | 0.49 | False |
| structural_topk | 8 | aggregator,planner,researcher_1,researcher_2,step_1_1,step_1_2,step_2_1,step_2_2 | 0.615 | 0.88 | 0.265 | False |
| structural_topk | 9 | aggregator,planner,researcher_1,researcher_2,step_1_1,step_1_2,step_2_1,step_2_2,verifier | 0.82 | 0.88 | 0.06 | False |
| structural_topk | 10 | all | 0.795 | 0.88 | 0.085 | False |
| output_topk | 1 | formatter | 0.435 | 0.855 | 0.42 | False |
| output_topk | 2 | formatter,verifier | 0.81 | 0.855 | 0.045 | False |
| output_topk | 3 | aggregator,formatter,verifier | 0.785 | 0.875 | 0.09 | False |
| output_topk | 4 | aggregator,formatter,step_2_2,verifier | 0.78 | 0.875 | 0.095 | False |
| output_topk | 5 | aggregator,formatter,step_1_2,step_2_2,verifier | 0.755 | 0.88 | 0.125 | False |
| output_topk | 6 | aggregator,formatter,step_1_2,step_2_1,step_2_2,verifier | 0.78 | 0.88 | 0.1 | False |

16 of 80 rows shown.

### estimator_errors.csv

| estimator | m | n_plans | n_held_out | mae_all | mae_held_out | feasibility_wrong_p25 | feasibility_wrong_p50 | feasibility_wrong_p75 |
|---|---|---|---|---|---|---|---|---|
| independence_additive | 3 | 1024 | 1010 | 0.066 | 0.067 | 0.139 | 0.008 | 0.222 |
| independence_multiplicative | 3 | 1024 | 1010 | 0.079 | 0.08 | 0.149 | 0.057 | 0.204 |
| pairwise_corrected | 3 | 1024 | 1010 | 0.052 | 0.052 | 0.139 | 0.051 | 0.196 |
| logit_additive | 3 | 1024 | 1010 | 0.053 | 0.053 | 0.139 | 0 | 0.23 |

### rules_summary

```json
{
  "accuracy_thresholds": {
    "p25": 0.515,
    "p50": 0.7075,
    "p75": 0.815
  },
  "h1c": {
    "reruns_used": 1044,
    "reruns_full": 1800,
    "share": 0.58,
    "top2_full": [
      "aggregator",
      "verifier"
    ],
    "top2_disagree_only": [
      "aggregator",
      "verifier"
    ],
    "top2_same": true,
    "a1_uv_abs_diff": {
      "planner": 0.0,
      "researcher_1": 0.01,
      "researcher_2": 0.015,
      "step_1_1": 0.005,
      "step_1_2": 0.01,
      "step_2_1": 0.0,
      "step_2_2": 0.004999999999999999,
      "aggregator": 0.0,
      "verifier": 0.0050000000000000044,
      "formatter": 0.0
    },
    "a1_max_uv_abs_diff": 0.015,
    "a1_share_le_half": false,
    "a1_confident_uv_full": {
      "1": [
        "verifier"
      ],
      "2": [
        "planner",
        "verifier"
      ]
    },
    "a1_confident_uv_disagree_only": {
      "1": [
        "verifier"
      ],
      "2": [
        "planner",
        "verifier"
      ]
    },
    "a1_confident_uv_same": true,
    "a1_holds_without_share": true,
    "e3_skip_variants": {
      "reruns_full": 1800,
      "key": {
        "reruns_used": 1044,
        "share": 0.58,
        "uv_abs_error": {
          "planner": 0.0,
          "researcher_1": 0.01,
          "researcher_2": 0.015,
          "step_1_1": 0.005,
          "step_1_2": 0.01,
          "step_2_1": 0.0,
          "step_2_2": 0.004999999999999999,
          "aggregator": 0.0,
          "verifier": 0.0050000000000000044,
          "formatter": 0.0
        },
        "max_uv_abs_error": 0.015
      },
      "exact": {
        "reruns_used": 1585,
        "share": 0.8805555555555555,
        "uv_abs_error": {
          "planner": 0.0,
          "researcher_1": 0.0,
          "researcher_2": 0.0,
          "step_1_1": 0.0,
          "step_1_2": 0.0,
          "step_2_1": 0.0,
          "step_2_2": 0.0,
          "aggregator": 0.0,
          "verifier": 0.0,
          "formatter": 0.0
        },
        "max_uv_abs_error": 0.0
      }
    }
  }
}
```

## hotpot_granite/cost

### plan_costs.csv

| plan | n_problems | tokens_out_small | tokens_out_large | tokens_in_small | tokens_in_large | tokens_in | tokens_out | api_usd | gpu_seconds | gpu_seconds_shared | cost_units | model_small | model_large | gpu_usd_latency | gpu_usd_latency_1 | gpu_usd_latency_shared_1 | gpu_usd_latency_2 | gpu_usd_latency_shared_2 | gpu_usd_latency_4 | gpu_usd_latency_shared_4 | gpu_usd_throughput_separate | gpu_cost_basis_separate | gpu_usd_throughput_shared | gpu_cost_basis_shared | gpu_usd_throughput_shared_mps | gpu_cost_basis_shared_mps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_small | 400 | 396.475 | 0 | 9714.562 | 0 | 9714.562 | 396.475 | 0.001 | 6.923 | 1.731 | 5 | ibm-granite/granite-3.1-2b-instruct |  | 0.004 | 0.002 | 4.81e-04 | 0.004 | 9.62e-04 | 0.008 | 0.002 | 2.33e-04 | estimated_rates | 1.19e-04 | estimated_rates | 9.62e-04 | fallback_latency |
| only_aggregator | 400 | 393.012 | 11.255 | 7704.51 | 2010.17 | 9714.68 | 404.267 | 0.005 | 7.288 | 1.984 | 8 | ibm-granite/granite-3.1-2b-instruct | ibm-granite/granite-3.1-8b-instruct | 0.004 | 0.002 | 5.51e-04 | 0.004 | 0.001 | 0.008 | 0.002 | 2.16e-04 | estimated_rates | 1.35e-04 | estimated_rates | 0.001 | fallback_latency |
| only_hop_1 | 400 | 345.348 | 33.005 | 7732.53 | 1946.447 | 9678.978 | 378.353 | 0.005 | 7.236 | 2.196 | 8 | ibm-granite/granite-3.1-2b-instruct | ibm-granite/granite-3.1-8b-instruct | 0.004 | 0.002 | 6.10e-04 | 0.004 | 0.001 | 0.008 | 0.002 | 1.98e-04 | estimated_rates | 1.35e-04 | estimated_rates | 0.001 | fallback_latency |
| only_hop_2 | 400 | 345.668 | 39.78 | 7707.767 | 1995.912 | 9703.68 | 385.447 | 0.005 | 7.423 | 2.288 | 8 | ibm-granite/granite-3.1-2b-instruct | ibm-granite/granite-3.1-8b-instruct | 0.004 | 0.002 | 6.36e-04 | 0.004 | 0.001 | 0.008 | 0.003 | 1.98e-04 | estimated_rates | 1.38e-04 | estimated_rates | 0.001 | fallback_latency |
| only_verifier | 400 | 239.917 | 80.728 | 7768.323 | 1946.24 | 9714.562 | 320.645 | 0.006 | 7.07 | 2.629 | 8 | ibm-granite/granite-3.1-2b-instruct | ibm-granite/granite-3.1-8b-instruct | 0.004 | 0.002 | 7.30e-04 | 0.004 | 0.001 | 0.008 | 0.003 | 1.56e-04 | estimated_rates | 1.34e-04 | estimated_rates | 0.001 | fallback_latency |

5 of 32 rows shown.

### placement_costs.csv

| run | plan | placement | gpu_seconds_per_problem | gpu_usd_throughput | source | repeats |
|---|---|---|---|---|---|---|
| cal_granite_hotpot_separate | all_large | separate | 0.851 | 4.73e-04 | measured | 3 |
| cal_granite_hotpot_separate | all_small | separate | 0.434 | 2.41e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_large | shared | 0.408 | 2.27e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_small | shared | 0.208 | 1.16e-04 | measured | 3 |
| cal_granite_math_separate | all_large | separate | 0.774 | 4.30e-04 | measured | 3 |
| cal_granite_math_separate | all_small | separate | 0.333 | 1.85e-04 | measured | 3 |
| cal_granite_math_shared | all_large | shared | 0.367 | 2.04e-04 | measured | 3 |
| cal_granite_math_shared | all_small | shared | 0.187 | 1.04e-04 | measured | 3 |
| cal_phi_math_separate | all_large | separate | 1.486 | 8.26e-04 | measured | 3 |
| cal_phi_math_separate | all_small | separate | 0.536 | 2.98e-04 | measured | 3 |
| cal_phi_math_shared | all_large | shared | 0.745 | 4.14e-04 | measured | 3 |
| cal_phi_math_shared | all_small | shared | 0.266 | 1.48e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_large | separate | 1.219 | 6.77e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_small | separate | 0.282 | 1.57e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_large | shared | 0.599 | 3.33e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_small | shared | 0.147 | 8.17e-05 | measured | 3 |
| cal_qwen_hotpot_separate | all_large | separate | 0.251 | 1.39e-04 | measured | 3 |
| cal_qwen_hotpot_separate | all_small | separate | 0.106 | 5.87e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_large | shared | 0.124 | 6.91e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_small | shared | 0.054 | 2.98e-05 | measured | 3 |
| separate | aggregator+verifier | separate | 0.422 | 2.35e-04 | measured | 3 |
| separate | all_large | separate | 0.504 | 2.80e-04 | measured | 3 |
| separate | all_small | separate | 0.21 | 1.17e-04 | measured | 3 |
| separate | only_aggregator | separate | 0.248 | 1.38e-04 | measured | 3 |
| separate | only_planner | separate | 0.227 | 1.26e-04 | measured | 3 |
| separate | only_verifier | separate | 0.367 | 2.04e-04 | measured | 3 |
| separate | planner+verifier | separate | 0.383 | 2.13e-04 | measured | 3 |
| separate_k1 | aggregator+verifier | separate | 4.857 | 0.003 | measured | 3 |
| separate_k1 | all_large | separate | 5.576 | 0.003 | measured | 3 |
| separate_k1 | all_small | separate | 2.367 | 0.001 | measured | 3 |

30 of 83 rows shown.

### cost_summary

```json
{
  "n_plans": 32,
  "api_large_small_ratio": 18.94486484175882,
  "a3_kendall_tau_latency_vs_units": 0.594208496451841,
  "p5_runs": [
    "cal_granite_hotpot_separate",
    "cal_granite_hotpot_shared",
    "cal_granite_math_separate",
    "cal_granite_math_shared",
    "cal_phi_math_separate",
    "cal_phi_math_shared",
    "cal_qwen3_14_math_separate",
    "cal_qwen3_14_math_shared",
    "cal_qwen_hotpot_separate",
    "cal_qwen_hotpot_shared",
    "separate",
    "separate_k1",
    "separate_k32",
    "shared",
    "shared_k1",
    "shared_k32",
    "shared_mps",
    "shared_mps_k1",
    "shared_mps_k32"
  ],
  "gpu_cost_basis": {
    "separate": {
      "estimated_rates": 32
    },
    "shared": {
      "estimated_rates": 32
    },
    "shared_mps": {
      "fallback_latency": 32
    }
  },
  "a3_kendall_tau_separate": 0.653629346097025,
  "a3_basis_separate": "estimated_rates",
  "a3_kendall_tau_shared": 0.7541877070350289,
  "a3_basis_shared": "estimated_rates",
  "a3_kendall_tau_shared_mps": 0.6856251882136627,
  "a3_basis_shared_mps": "fallback"
}
```

## hotpot_granite/pareto

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| hop_2+aggregator+verifier | separate | 0.52 | 2.37e-04 | 11.956 | estimated_rates |
| hop_2+aggregator+verifier | shared | 0.52 | 1.66e-04 | 29.445 | estimated_rates |
| all_large | shared | 0.517 | 2.19e-04 | 15.746 | estimated_rates |
| hop_1+hop_2+aggregator+verifier | shared | 0.515 | 1.81e-04 | 28.693 | estimated_rates |
| hop_2+aggregator | separate | 0.497 | 1.79e-04 | 10.323 | estimated_rates |
| hop_2+aggregator | shared | 0.497 | 1.53e-04 | 29.335 | estimated_rates |
| hop_2+verifier | shared | 0.495 | 1.53e-04 | 29.305 | estimated_rates |
| hop_1+aggregator+verifier | shared | 0.492 | 1.63e-04 | 28.672 | estimated_rates |
| aggregator+verifier | separate | 0.477 | 1.60e-04 | 11.104 | estimated_rates |
| aggregator+verifier | shared | 0.477 | 1.47e-04 | 29.568 | estimated_rates |

10 of 18 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 14.471 | hop_2+aggregator+verifier | 0.52 |
| shared | 14.471 | all_small | 0.435 |
| shared_mps | 14.471 | all_small | 0.435 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_hop_2 | 0.465 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.52 | True | estimated_rates |
| 0.5 | hop_2+aggregator | 0.497 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.52 | True | estimated_rates |
| 0.75 | hop_2+aggregator+verifier | 0.52 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.52 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 64,
    "fallback_latency": 32
  },
  "any_fallback": true,
  "k": 16,
  "n_candidates": 96,
  "n_front": 18,
  "hypervolume_joint": 0.3611928715719901,
  "hypervolume_two_step": 0.3568252895845706,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.02250000000000002,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 14.470619068499218,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## hotpot_granite/pareto_api

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| hop_2+aggregator+verifier | separate | 0.52 | 0.014 | 11.956 | api |
| hop_2+aggregator | separate | 0.497 | 0.009 | 10.323 | api |
| only_hop_2 | separate | 0.465 | 0.005 | 10.114 | api |
| hop_1+aggregator | separate | 0.465 | 0.009 | 10.091 | api |
| only_aggregator | separate | 0.455 | 0.005 | 9.957 | api |
| all_small | separate | 0.435 | 0.001 | 9.647 | api |
| all_small | shared | 0.435 | 0.001 | 9.647 | api |
| all_small | shared_mps | 0.435 | 0.001 | 9.647 | api |

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 14.471 | hop_2+aggregator+verifier | 0.52 |
| shared | 14.471 | all_small | 0.435 |
| shared_mps | 14.471 | all_small | 0.435 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_hop_2 | 0.465 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.52 | True | estimated_rates |
| 0.5 | hop_2+aggregator | 0.497 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.52 | True | estimated_rates |
| 0.75 | hop_2+aggregator+verifier | 0.52 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.52 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "api_usd",
  "cost_metric_requested": "api_usd",
  "cost_basis_counts": {
    "api": 96
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 96,
  "n_front": 8,
  "hypervolume_joint": 0.33112563948078577,
  "hypervolume_two_step": 0.3309024831094275,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.0,
  "a2_gap_ge_2_points": false,
  "h3a_limit_s": 14.470619068499218,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## hotpot_granite/pareto_estimated

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| hop_2+aggregator+verifier | separate | 0.525 | 2.37e-04 | 11.956 | estimated_rates |
| hop_2+aggregator+verifier | shared | 0.525 | 1.66e-04 | 29.445 | estimated_rates |
| hop_1+hop_2+aggregator+verifier | shared | 0.525 | 1.81e-04 | 28.693 | estimated_rates |
| all_large | shared | 0.52 | 2.19e-04 | 15.746 | estimated_rates |
| hop_2+aggregator | separate | 0.497 | 1.79e-04 | 10.323 | estimated_rates |
| hop_2+aggregator | shared | 0.497 | 1.53e-04 | 29.335 | estimated_rates |
| hop_2+verifier | shared | 0.495 | 1.53e-04 | 29.305 | estimated_rates |
| hop_1+hop_2+verifier | shared | 0.495 | 1.66e-04 | 28.638 | estimated_rates |
| aggregator+verifier | separate | 0.477 | 1.60e-04 | 11.104 | estimated_rates |
| aggregator+verifier | shared | 0.477 | 1.47e-04 | 29.568 | estimated_rates |

10 of 19 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 14.471 | hop_2+aggregator+verifier | 0.525 |
| shared | 14.471 | all_small | 0.435 |
| shared_mps | 14.471 | all_small | 0.435 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_hop_2 | 0.465 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.525 | True | estimated_rates |
| 0.5 | hop_2+aggregator | 0.497 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.525 | True | estimated_rates |
| 0.75 | hop_2+aggregator+verifier | 0.525 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.525 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 64,
    "fallback_latency": 32
  },
  "any_fallback": true,
  "k": 16,
  "n_candidates": 96,
  "n_front": 19,
  "hypervolume_joint": 0.36429656270328525,
  "hypervolume_two_step": 0.3599185045970247,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.027499999999999913,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 14.470619068499218,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "regret_hypervolume": 9.29347772571365e-07,
  "regret_accuracy_mean": 0.000833333333333334
}
```

## hotpot_granite/routing

### routing.csv

| agent | rule | threshold | routed_share | accuracy | cost | baseline_accuracy | fixed_accuracy | fixed_cost | h6_match | primary |
|---|---|---|---|---|---|---|---|---|---|---|
| aggregator | samples_disagree |  | 0.46 | 0.505 | 0.004 | 0.41 | 0.515 | 0.005 | True | True |
| aggregator | entropy | 0 | 0.46 | 0.505 | 0.004 | 0.41 | 0.515 | 0.005 | True | False |
| aggregator | entropy | 0.5 | 0.46 | 0.505 | 0.004 | 0.41 | 0.515 | 0.005 | True | False |
| planner | baseline_vs_majority |  | 0.33 | 0.46 | 0.006 | 0.41 | 0.445 | 0.006 | False | False |
| aggregator | entropy | 1 | 0.2 | 0.46 | 0.003 | 0.41 | 0.515 | 0.005 | False | False |
| aggregator | baseline_vs_majority |  | 0.14 | 0.45 | 0.003 | 0.41 | 0.515 | 0.005 | False | False |
| planner | samples_disagree |  | 0.555 | 0.43 | 0.007 | 0.41 | 0.445 | 0.006 | False | False |
| planner | entropy | 0 | 0.555 | 0.43 | 0.007 | 0.41 | 0.445 | 0.006 | False | False |

8 of 25 rows shown.

### routing_summary

```json
{
  "a4_agent": "aggregator",
  "a4_rule": "samples_disagree (K small samples not unanimous)",
  "a4_k_samples": 5,
  "a4_h6_match": true,
  "a4_row": {
    "agent": "aggregator",
    "rule": "samples_disagree",
    "threshold": "",
    "routed_share": 0.46,
    "accuracy": 0.505,
    "cost": 0.004066974,
    "baseline_accuracy": 0.41,
    "fixed_accuracy": 0.515,
    "fixed_cost": 0.005139684500000002,
    "h6_match": true,
    "primary": true
  },
  "note": "all other rows in routing.csv are exploratory"
}
```

## hotpot_granite/rules

### rule_plans.csv

| rule | budget | upgraded | accuracy | best_accuracy_at_budget | regret | is_best |
|---|---|---|---|---|---|---|
| structural_topk | 1 | planner | 0.43 | 0.465 | 0.035 | False |
| structural_topk | 2 | hop_1,planner | 0.448 | 0.497 | 0.05 | False |
| structural_topk | 3 | hop_1,hop_2,planner | 0.472 | 0.52 | 0.048 | False |
| structural_topk | 4 | aggregator,hop_1,hop_2,planner | 0.502 | 0.52 | 0.018 | False |
| structural_topk | 5 | all | 0.517 | 0.52 | 0.003 | False |
| output_topk | 1 | verifier | 0.46 | 0.465 | 0.005 | False |
| output_topk | 2 | aggregator,verifier | 0.477 | 0.497 | 0.02 | False |
| output_topk | 3 | aggregator,hop_2,verifier | 0.52 | 0.52 | 0 | True |
| output_topk | 4 | aggregator,hop_1,hop_2,verifier | 0.515 | 0.52 | 0.005 | False |
| output_topk | 5 | all | 0.517 | 0.52 | 0.003 | False |
| ec_topk | 1 | aggregator | 0.455 | 0.465 | 0.01 | False |
| ec_topk | 2 | aggregator,verifier | 0.477 | 0.497 | 0.02 | False |
| ec_topk | 3 | aggregator,planner,verifier | 0.5 | 0.52 | 0.02 | False |
| ec_topk | 4 | aggregator,hop_1,planner,verifier | 0.512 | 0.52 | 0.008 | False |
| ec_topk | 5 | all | 0.517 | 0.52 | 0.003 | False |
| ec_real_topk | 1 | aggregator | 0.455 | 0.465 | 0.01 | False |

16 of 40 rows shown.

### estimator_errors.csv

| estimator | m | n_plans | n_held_out | mae_all | mae_held_out | feasibility_wrong_p25 | feasibility_wrong_p50 | feasibility_wrong_p75 |
|---|---|---|---|---|---|---|---|---|
| independence_additive | 3 | 32 | 23 | 0.013 | 0.017 | 0.348 | 0.304 | 0.13 |
| independence_multiplicative | 3 | 32 | 23 | 0.013 | 0.017 | 0.348 | 0.304 | 0.13 |
| pairwise_corrected | 3 | 32 | 23 | 0.013 | 0.018 | 0.348 | 0.304 | 0.174 |
| logit_additive | 3 | 32 | 23 | 0.013 | 0.017 | 0.348 | 0.304 | 0.13 |

### rules_summary

```json
{
  "accuracy_thresholds": {
    "p25": 0.45875,
    "p50": 0.4775,
    "p75": 0.495625
  },
  "h1c": {
    "reruns_used": 638,
    "reruns_full": 800,
    "share": 0.7975,
    "top2_full": [
      "aggregator",
      "planner"
    ],
    "top2_disagree_only": [
      "aggregator",
      "planner"
    ],
    "top2_same": true,
    "a1_uv_abs_diff": {
      "planner": 0.0,
      "hop_1": 0.0,
      "hop_2": 0.0,
      "aggregator": 0.0,
      "verifier": 0.0
    },
    "a1_max_uv_abs_diff": 0.0,
    "a1_share_le_half": false,
    "a1_confident_uv_full": {
      "1": [
        "aggregator"
      ],
      "2": [
        "aggregator",
        "planner"
      ]
    },
    "a1_confident_uv_disagree_only": {
      "1": [
        "aggregator"
      ],
      "2": [
        "aggregator",
        "planner"
      ]
    },
    "a1_confident_uv_same": true,
    "a1_holds_without_share": true,
    "e3_skip_variants": {
      "reruns_full": 800,
      "key": {
        "reruns_used": 638,
        "share": 0.7975,
        "uv_abs_error": {
          "planner": 0.0,
          "hop_1": 0.0,
          "hop_2": 0.0,
          "aggregator": 0.0,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.0
      },
      "exact": {
        "reruns_used": 655,
        "share": 0.81875,
        "uv_abs_error": {
          "planner": 0.0,
          "hop_1": 0.0,
          "hop_2": 0.0,
          "aggregator": 0.0,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.0
      }
    }
  }
}
```

## hotpot_iso_granite/cost

### plan_costs.csv

| plan | n_problems | tokens_out_small | tokens_out_large | tokens_in_small | tokens_in_large | tokens_in | tokens_out | api_usd | gpu_seconds | gpu_seconds_shared | cost_units | model_small | model_large | gpu_usd_latency | gpu_usd_latency_1 | gpu_usd_latency_shared_1 | gpu_usd_latency_2 | gpu_usd_latency_shared_2 | gpu_usd_latency_4 | gpu_usd_latency_shared_4 | gpu_usd_throughput_separate | gpu_cost_basis_separate | gpu_usd_throughput_shared | gpu_cost_basis_shared | gpu_usd_throughput_shared_mps | gpu_cost_basis_shared_mps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_small | 400 | 338.525 | 0 | 6437.525 | 0 | 6437.525 | 338.525 | 8.13e-04 | 5.507 | 1.377 | 5 | ibm-granite/granite-3.1-2b-instruct |  | 0.003 | 0.002 | 3.82e-04 | 0.003 | 7.65e-04 | 0.006 | 0.002 | 1.85e-04 | estimated_rates | 9.43e-05 | estimated_rates | 7.65e-04 | fallback_latency |
| only_aggregator | 400 | 332.488 | 10.28 | 6121.12 | 313.683 | 6434.802 | 342.767 | 0.002 | 5.671 | 1.496 | 8 | ibm-granite/granite-3.1-2b-instruct | ibm-granite/granite-3.1-8b-instruct | 0.003 | 0.002 | 4.16e-04 | 0.003 | 8.31e-04 | 0.006 | 0.002 | 1.80e-04 | estimated_rates | 9.94e-05 | estimated_rates | 8.31e-04 | fallback_latency |
| only_verifier | 400 | 241.785 | 15.4 | 6071.835 | 365.69 | 6437.525 | 257.185 | 0.002 | 4.526 | 1.243 | 8 | ibm-granite/granite-3.1-2b-instruct | ibm-granite/granite-3.1-8b-instruct | 0.003 | 0.001 | 3.45e-04 | 0.003 | 6.90e-04 | 0.005 | 0.001 | 1.43e-04 | estimated_rates | 8.35e-05 | estimated_rates | 6.90e-04 | fallback_latency |
| aggregator+verifier | 400 | 228.775 | 24.79 | 5758.153 | 676.65 | 6434.802 | 253.565 | 0.002 | 4.555 | 1.322 | 11 | ibm-granite/granite-3.1-2b-instruct | ibm-granite/granite-3.1-8b-instruct | 0.003 | 0.001 | 3.67e-04 | 0.003 | 7.35e-04 | 0.005 | 0.001 | 1.36e-04 | estimated_rates | 8.67e-05 | estimated_rates | 7.35e-04 | fallback_latency |
| only_hop_1 | 400 | 292.015 | 33.005 | 4435.185 | 1946.447 | 6381.632 | 325.02 | 0.005 | 5.949 | 1.874 | 8 | ibm-granite/granite-3.1-2b-instruct | ibm-granite/granite-3.1-8b-instruct | 0.003 | 0.002 | 5.21e-04 | 0.003 | 0.001 | 0.007 | 0.002 | 1.51e-04 | estimated_rates | 1.11e-04 | estimated_rates | 0.001 | fallback_latency |

5 of 32 rows shown.

### placement_costs.csv

| run | plan | placement | gpu_seconds_per_problem | gpu_usd_throughput | source | repeats |
|---|---|---|---|---|---|---|
| cal_granite_hotpot_separate | all_large | separate | 0.851 | 4.73e-04 | measured | 3 |
| cal_granite_hotpot_separate | all_small | separate | 0.434 | 2.41e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_large | shared | 0.408 | 2.27e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_small | shared | 0.208 | 1.16e-04 | measured | 3 |
| cal_granite_math_separate | all_large | separate | 0.774 | 4.30e-04 | measured | 3 |
| cal_granite_math_separate | all_small | separate | 0.333 | 1.85e-04 | measured | 3 |
| cal_granite_math_shared | all_large | shared | 0.367 | 2.04e-04 | measured | 3 |
| cal_granite_math_shared | all_small | shared | 0.187 | 1.04e-04 | measured | 3 |
| cal_phi_math_separate | all_large | separate | 1.486 | 8.26e-04 | measured | 3 |
| cal_phi_math_separate | all_small | separate | 0.536 | 2.98e-04 | measured | 3 |
| cal_phi_math_shared | all_large | shared | 0.745 | 4.14e-04 | measured | 3 |
| cal_phi_math_shared | all_small | shared | 0.266 | 1.48e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_large | separate | 1.219 | 6.77e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_small | separate | 0.282 | 1.57e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_large | shared | 0.599 | 3.33e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_small | shared | 0.147 | 8.17e-05 | measured | 3 |
| cal_qwen_hotpot_separate | all_large | separate | 0.251 | 1.39e-04 | measured | 3 |
| cal_qwen_hotpot_separate | all_small | separate | 0.106 | 5.87e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_large | shared | 0.124 | 6.91e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_small | shared | 0.054 | 2.98e-05 | measured | 3 |
| separate | aggregator+verifier | separate | 0.422 | 2.35e-04 | measured | 3 |
| separate | all_large | separate | 0.504 | 2.80e-04 | measured | 3 |
| separate | all_small | separate | 0.21 | 1.17e-04 | measured | 3 |
| separate | only_aggregator | separate | 0.248 | 1.38e-04 | measured | 3 |
| separate | only_planner | separate | 0.227 | 1.26e-04 | measured | 3 |
| separate | only_verifier | separate | 0.367 | 2.04e-04 | measured | 3 |
| separate | planner+verifier | separate | 0.383 | 2.13e-04 | measured | 3 |
| separate_k1 | aggregator+verifier | separate | 4.857 | 0.003 | measured | 3 |
| separate_k1 | all_large | separate | 5.576 | 0.003 | measured | 3 |
| separate_k1 | all_small | separate | 2.367 | 0.001 | measured | 3 |

30 of 83 rows shown.

### cost_summary

```json
{
  "n_plans": 32,
  "api_large_small_ratio": 18.335338216392053,
  "a3_kendall_tau_latency_vs_units": 0.31081675199019376,
  "p5_runs": [
    "cal_granite_hotpot_separate",
    "cal_granite_hotpot_shared",
    "cal_granite_math_separate",
    "cal_granite_math_shared",
    "cal_phi_math_separate",
    "cal_phi_math_shared",
    "cal_qwen3_14_math_separate",
    "cal_qwen3_14_math_shared",
    "cal_qwen_hotpot_separate",
    "cal_qwen_hotpot_shared",
    "separate",
    "separate_k1",
    "separate_k32",
    "shared",
    "shared_k1",
    "shared_k32",
    "shared_mps",
    "shared_mps_k1",
    "shared_mps_k32"
  ],
  "gpu_cost_basis": {
    "separate": {
      "estimated_rates": 32
    },
    "shared": {
      "estimated_rates": 32
    },
    "shared_mps": {
      "fallback_latency": 32
    }
  },
  "a3_kendall_tau_separate": 0.42965845128056196,
  "a3_basis_separate": "estimated_rates",
  "a3_kendall_tau_shared": 0.5027918046900193,
  "a3_basis_shared": "estimated_rates",
  "a3_kendall_tau_shared_mps": 0.5119334738662015,
  "a3_basis_shared_mps": "fallback"
}
```

## hotpot_iso_granite/pareto

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| all_large | shared | 0.542 | 1.59e-04 | 10.468 | estimated_rates |
| planner+hop_1+aggregator+verifier | separate | 0.52 | 2.55e-04 | 9.998 | estimated_rates |
| planner+hop_1+aggregator+verifier | shared | 0.52 | 1.40e-04 | 20.389 | estimated_rates |
| hop_2+aggregator+verifier | separate | 0.505 | 1.12e-04 | 7.209 | estimated_rates |
| hop_2+aggregator+verifier | shared | 0.505 | 1.05e-04 | 20.595 | estimated_rates |
| hop_1+aggregator+verifier | separate | 0.492 | 1.05e-04 | 7.034 | estimated_rates |
| hop_1+aggregator+verifier | shared | 0.492 | 1.02e-04 | 20.02 | estimated_rates |
| aggregator+verifier | separate | 0.485 | 1.36e-04 | 6.501 | estimated_rates |
| aggregator+verifier | shared | 0.485 | 8.67e-05 | 15.726 | estimated_rates |
| only_aggregator | shared | 0.46 | 9.94e-05 | 12.441 | estimated_rates |

10 of 14 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 11.428 | all_large | 0.542 |
| shared | 11.428 | all_large | 0.542 |
| shared_mps | 11.428 | all_large | 0.542 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | aggregator+verifier | 0.485 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.505 | True | estimated_rates |
| 0.5 | hop_2+aggregator+verifier | 0.505 | gpu_usd_throughput_separate | planner+hop_1+aggregator+verifier | 0.52 | True | estimated_rates |
| 0.75 | planner+hop_1+aggregator+verifier | 0.52 | gpu_usd_throughput_separate | planner+hop_1+aggregator+verifier | 0.52 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 64,
    "fallback_latency": 32
  },
  "any_fallback": true,
  "k": 16,
  "n_candidates": 96,
  "n_front": 14,
  "hypervolume_joint": 0.3961575350971327,
  "hypervolume_two_step": 0.39263947692673123,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.03749999999999998,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 11.428313376001142,
  "h3a_best_differs": false,
  "h4a_any_budget_differs": true
}
```

## hotpot_iso_granite/pareto_api

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| all_large | separate | 0.542 | 0.015 | 10.468 | api |
| all_large | shared | 0.542 | 0.015 | 10.468 | api |
| all_large | shared_mps | 0.542 | 0.015 | 10.468 | api |
| planner+hop_1+aggregator+verifier | separate | 0.52 | 0.011 | 9.998 | api |
| hop_2+aggregator+verifier | separate | 0.505 | 0.006 | 7.209 | api |
| hop_1+aggregator+verifier | separate | 0.492 | 0.006 | 7.034 | api |
| aggregator+verifier | separate | 0.485 | 0.002 | 6.501 | api |
| only_aggregator | separate | 0.46 | 0.002 | 7.706 | api |
| only_verifier | separate | 0.445 | 0.002 | 6.485 | api |
| all_small | separate | 0.41 | 8.13e-04 | 7.619 | api |

10 of 12 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 11.428 | all_large | 0.542 |
| shared | 11.428 | all_large | 0.542 |
| shared_mps | 11.428 | all_large | 0.542 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | aggregator+verifier | 0.485 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.505 | True | estimated_rates |
| 0.5 | hop_2+aggregator+verifier | 0.505 | gpu_usd_throughput_separate | planner+hop_1+aggregator+verifier | 0.52 | True | estimated_rates |
| 0.75 | planner+hop_1+aggregator+verifier | 0.52 | gpu_usd_throughput_separate | planner+hop_1+aggregator+verifier | 0.52 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "api_usd",
  "cost_metric_requested": "api_usd",
  "cost_basis_counts": {
    "api": 96
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 96,
  "n_front": 12,
  "hypervolume_joint": 0.3546656598946558,
  "hypervolume_two_step": 0.35348123812457455,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.007500000000000007,
  "a2_gap_ge_2_points": false,
  "h3a_limit_s": 11.428313376001142,
  "h3a_best_differs": false,
  "h4a_any_budget_differs": true
}
```

## hotpot_iso_granite/pareto_estimated

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| hop_2+aggregator+verifier | separate | 0.49 | 1.12e-04 | 7.209 | estimated_rates |
| hop_2+aggregator+verifier | shared | 0.49 | 1.05e-04 | 20.595 | estimated_rates |
| aggregator+verifier | separate | 0.485 | 1.36e-04 | 6.501 | estimated_rates |
| aggregator+verifier | shared | 0.485 | 8.67e-05 | 15.726 | estimated_rates |
| hop_1+aggregator+verifier | separate | 0.478 | 1.05e-04 | 7.034 | estimated_rates |
| only_aggregator | shared | 0.46 | 9.94e-05 | 12.441 | estimated_rates |
| only_verifier | separate | 0.445 | 1.43e-04 | 6.485 | estimated_rates |
| only_verifier | shared | 0.445 | 8.35e-05 | 12.727 | estimated_rates |
| hop_1+verifier | separate | 0.445 | 1.07e-04 | 6.962 | estimated_rates |
| all_small | shared | 0.41 | 9.43e-05 | 7.619 | estimated_rates |

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 11.428 | hop_2+aggregator+verifier | 0.49 |
| shared | 11.428 | all_large | 0.478 |
| shared_mps | 11.428 | all_large | 0.478 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | aggregator+verifier | 0.485 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.49 | True | estimated_rates |
| 0.5 | hop_2+aggregator+verifier | 0.49 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.49 | False | estimated_rates |
| 0.75 | hop_2+aggregator+verifier | 0.49 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.49 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 64,
    "fallback_latency": 32
  },
  "any_fallback": true,
  "k": 16,
  "n_candidates": 96,
  "n_front": 10,
  "hypervolume_joint": 0.3631901701503848,
  "hypervolume_two_step": 0.3606131121330231,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.0,
  "a2_gap_ge_2_points": false,
  "h3a_limit_s": 11.428313376001142,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "regret_hypervolume": 0.02223892143135342,
  "regret_accuracy_mean": 0.005357142857142858
}
```

## hotpot_iso_granite/routing

### routing.csv

| agent | rule | threshold | routed_share | accuracy | cost | baseline_accuracy | fixed_accuracy | fixed_cost | h6_match | primary |
|---|---|---|---|---|---|---|---|---|---|---|
| aggregator | samples_disagree |  | 0.46 | 0.48 | 0.001 | 0.415 | 0.5 | 0.002 | False | True |
| aggregator | entropy | 0 | 0.46 | 0.48 | 0.001 | 0.415 | 0.5 | 0.002 | False | False |
| aggregator | entropy | 0.5 | 0.46 | 0.48 | 0.001 | 0.415 | 0.5 | 0.002 | False | False |
| planner | baseline_vs_majority |  | 0.415 | 0.465 | 0.005 | 0.415 | 0.44 | 0.005 | True | False |
| aggregator | entropy | 1 | 0.225 | 0.45 | 0.001 | 0.415 | 0.5 | 0.002 | False | False |
| planner | entropy | 1 | 0.225 | 0.435 | 0.004 | 0.415 | 0.44 | 0.005 | True | False |
| aggregator | baseline_vs_majority |  | 0.115 | 0.435 | 0.001 | 0.415 | 0.5 | 0.002 | False | False |
| planner | samples_disagree |  | 0.635 | 0.43 | 0.006 | 0.415 | 0.44 | 0.005 | False | False |

8 of 25 rows shown.

### routing_summary

```json
{
  "a4_agent": "aggregator",
  "a4_rule": "samples_disagree (K small samples not unanimous)",
  "a4_k_samples": 5,
  "a4_h6_match": false,
  "a4_row": {
    "agent": "aggregator",
    "rule": "samples_disagree",
    "threshold": "",
    "routed_share": 0.46,
    "accuracy": 0.48,
    "cost": 0.0013529675,
    "baseline_accuracy": 0.415,
    "fixed_accuracy": 0.5,
    "fixed_cost": 0.001528984,
    "h6_match": false,
    "primary": true
  },
  "note": "all other rows in routing.csv are exploratory"
}
```

## hotpot_iso_granite/rules

### rule_plans.csv

| rule | budget | upgraded | accuracy | best_accuracy_at_budget | regret | is_best |
|---|---|---|---|---|---|---|
| structural_topk | 1 | planner | 0.405 | 0.46 | 0.055 | False |
| structural_topk | 2 | hop_1,planner | 0.448 | 0.485 | 0.037 | False |
| structural_topk | 3 | hop_1,hop_2,planner | 0.44 | 0.505 | 0.065 | False |
| structural_topk | 4 | aggregator,hop_1,hop_2,planner | 0.515 | 0.52 | 0.005 | False |
| structural_topk | 5 | all | 0.542 | 0.542 | 0 | True |
| output_topk | 1 | verifier | 0.445 | 0.46 | 0.015 | False |
| output_topk | 2 | aggregator,verifier | 0.485 | 0.485 | 0 | True |
| output_topk | 3 | aggregator,hop_2,verifier | 0.505 | 0.505 | 0 | True |
| output_topk | 4 | aggregator,hop_1,hop_2,verifier | 0.502 | 0.52 | 0.018 | False |
| output_topk | 5 | all | 0.542 | 0.542 | 0 | True |
| ec_topk | 1 | planner | 0.405 | 0.46 | 0.055 | False |
| ec_topk | 2 | hop_2,planner | 0.403 | 0.485 | 0.082 | False |
| ec_topk | 3 | aggregator,hop_2,planner | 0.477 | 0.505 | 0.028 | False |
| ec_topk | 4 | aggregator,hop_2,planner,verifier | 0.497 | 0.52 | 0.023 | False |
| ec_topk | 5 | all | 0.542 | 0.542 | 0 | True |
| ec_real_topk | 1 | aggregator | 0.46 | 0.46 | 0 | True |

16 of 40 rows shown.

### estimator_errors.csv

| estimator | m | n_plans | n_held_out | mae_all | mae_held_out | feasibility_wrong_p25 | feasibility_wrong_p50 | feasibility_wrong_p75 |
|---|---|---|---|---|---|---|---|---|
| independence_additive | 3 | 32 | 23 | 0.011 | 0.014 | 0.13 | 0.217 | 0.174 |
| independence_multiplicative | 3 | 32 | 23 | 0.011 | 0.014 | 0.087 | 0.217 | 0.174 |
| pairwise_corrected | 3 | 32 | 23 | 0.015 | 0.021 | 0.13 | 0.304 | 0.348 |
| logit_additive | 3 | 32 | 23 | 0.011 | 0.014 | 0.087 | 0.217 | 0.174 |

### rules_summary

```json
{
  "accuracy_thresholds": {
    "p25": 0.44,
    "p50": 0.465,
    "p75": 0.49375
  },
  "h1c": {
    "reruns_used": 635,
    "reruns_full": 800,
    "share": 0.79375,
    "top2_full": [
      "aggregator",
      "planner"
    ],
    "top2_disagree_only": [
      "aggregator",
      "planner"
    ],
    "top2_same": true,
    "a1_uv_abs_diff": {
      "planner": 0.0,
      "hop_1": 0.0,
      "hop_2": 0.0,
      "aggregator": 0.0,
      "verifier": 0.0
    },
    "a1_max_uv_abs_diff": 0.0,
    "a1_share_le_half": false,
    "a1_confident_uv_full": {
      "1": [
        "aggregator"
      ],
      "2": [
        "aggregator",
        "planner"
      ]
    },
    "a1_confident_uv_disagree_only": {
      "1": [
        "aggregator"
      ],
      "2": [
        "aggregator",
        "planner"
      ]
    },
    "a1_confident_uv_same": true,
    "a1_holds_without_share": true,
    "e3_skip_variants": {
      "reruns_full": 800,
      "key": {
        "reruns_used": 635,
        "share": 0.79375,
        "uv_abs_error": {
          "planner": 0.0,
          "hop_1": 0.0,
          "hop_2": 0.0,
          "aggregator": 0.0,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.0
      },
      "exact": {
        "reruns_used": 659,
        "share": 0.82375,
        "uv_abs_error": {
          "planner": 0.0,
          "hop_1": 0.0,
          "hop_2": 0.0,
          "aggregator": 0.0,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.0
      }
    }
  }
}
```

## hotpot_iso_q15_7/cost

### plan_costs.csv

| plan | n_problems | tokens_out_small | tokens_out_large | tokens_in_small | tokens_in_large | tokens_in | tokens_out | api_usd | gpu_seconds | gpu_seconds_shared | cost_units | model_small | model_large | gpu_usd_latency | gpu_usd_latency_1 | gpu_usd_latency_shared_1 | gpu_usd_latency_2 | gpu_usd_latency_shared_2 | gpu_usd_latency_4 | gpu_usd_latency_shared_4 | gpu_usd_throughput_separate | gpu_cost_basis_separate | gpu_usd_throughput_shared | gpu_cost_basis_shared | gpu_usd_throughput_shared_mps | gpu_cost_basis_shared_mps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_small | 400 | 126.397 | 0 | 5151.028 | 0 | 5151.028 | 126.397 | 5.78e-04 | 1.608 | 0.402 | 5 | Qwen/Qwen2.5-1.5B-Instruct |  | 8.93e-04 | 4.47e-04 | 1.12e-04 | 8.93e-04 | 2.23e-04 | 0.002 | 4.47e-04 | 4.72e-04 | estimated_rates | 1.10e-04 | estimated_rates | 1.53e-04 | estimated_rates |
| only_aggregator | 400 | 114.035 | 12.773 | 4910.908 | 240.86 | 5151.767 | 126.808 | 0.001 | 1.749 | 0.523 | 8 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 9.72e-04 | 4.86e-04 | 1.45e-04 | 9.72e-04 | 2.90e-04 | 0.002 | 5.81e-04 | 4.34e-04 | estimated_rates | 1.20e-04 | estimated_rates | 1.61e-04 | estimated_rates |
| only_verifier | 400 | 112.625 | 18.655 | 4865.403 | 285.625 | 5151.028 | 131.28 | 0.001 | 1.845 | 0.582 | 8 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.001 | 5.12e-04 | 1.62e-04 | 0.001 | 3.23e-04 | 0.002 | 6.47e-04 | 4.29e-04 | estimated_rates | 1.28e-04 | estimated_rates | 1.69e-04 | estimated_rates |
| aggregator+verifier | 400 | 100.438 | 29.238 | 4624.542 | 527.225 | 5151.767 | 129.675 | 0.002 | 1.933 | 0.676 | 11 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.001 | 5.37e-04 | 1.88e-04 | 0.001 | 3.75e-04 | 0.002 | 7.51e-04 | 3.92e-04 | estimated_rates | 1.36e-04 | estimated_rates | 1.73e-04 | estimated_rates |
| only_hop_2 | 400 | 98.692 | 23.058 | 3564.265 | 1577.22 | 5141.485 | 121.75 | 0.004 | 1.97 | 0.706 | 8 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.001 | 5.47e-04 | 1.96e-04 | 0.001 | 3.92e-04 | 0.002 | 7.84e-04 | 3.54e-04 | estimated_rates | 1.28e-04 | estimated_rates | 1.54e-04 | estimated_rates |

5 of 32 rows shown.

### placement_costs.csv

| run | plan | placement | gpu_seconds_per_problem | gpu_usd_throughput | source | repeats |
|---|---|---|---|---|---|---|
| cal_granite_hotpot_separate | all_large | separate | 0.851 | 4.73e-04 | measured | 3 |
| cal_granite_hotpot_separate | all_small | separate | 0.434 | 2.41e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_large | shared | 0.408 | 2.27e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_small | shared | 0.208 | 1.16e-04 | measured | 3 |
| cal_granite_math_separate | all_large | separate | 0.774 | 4.30e-04 | measured | 3 |
| cal_granite_math_separate | all_small | separate | 0.333 | 1.85e-04 | measured | 3 |
| cal_granite_math_shared | all_large | shared | 0.367 | 2.04e-04 | measured | 3 |
| cal_granite_math_shared | all_small | shared | 0.187 | 1.04e-04 | measured | 3 |
| cal_phi_math_separate | all_large | separate | 1.486 | 8.26e-04 | measured | 3 |
| cal_phi_math_separate | all_small | separate | 0.536 | 2.98e-04 | measured | 3 |
| cal_phi_math_shared | all_large | shared | 0.745 | 4.14e-04 | measured | 3 |
| cal_phi_math_shared | all_small | shared | 0.266 | 1.48e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_large | separate | 1.219 | 6.77e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_small | separate | 0.282 | 1.57e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_large | shared | 0.599 | 3.33e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_small | shared | 0.147 | 8.17e-05 | measured | 3 |
| cal_qwen_hotpot_separate | all_large | separate | 0.251 | 1.39e-04 | measured | 3 |
| cal_qwen_hotpot_separate | all_small | separate | 0.106 | 5.87e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_large | shared | 0.124 | 6.91e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_small | shared | 0.054 | 2.98e-05 | measured | 3 |
| separate | aggregator+verifier | separate | 0.422 | 2.35e-04 | measured | 3 |
| separate | all_large | separate | 0.504 | 2.80e-04 | measured | 3 |
| separate | all_small | separate | 0.21 | 1.17e-04 | measured | 3 |
| separate | only_aggregator | separate | 0.248 | 1.38e-04 | measured | 3 |
| separate | only_planner | separate | 0.227 | 1.26e-04 | measured | 3 |
| separate | only_verifier | separate | 0.367 | 2.04e-04 | measured | 3 |
| separate | planner+verifier | separate | 0.383 | 2.13e-04 | measured | 3 |
| separate_k1 | aggregator+verifier | separate | 4.857 | 0.003 | measured | 3 |
| separate_k1 | all_large | separate | 5.576 | 0.003 | measured | 3 |
| separate_k1 | all_small | separate | 2.367 | 0.001 | measured | 3 |

30 of 83 rows shown.

### cost_summary

```json
{
  "n_plans": 32,
  "api_large_small_ratio": 19.927676134334792,
  "a3_kendall_tau_latency_vs_units": 0.7404752032707557,
  "p5_runs": [
    "cal_granite_hotpot_separate",
    "cal_granite_hotpot_shared",
    "cal_granite_math_separate",
    "cal_granite_math_shared",
    "cal_phi_math_separate",
    "cal_phi_math_shared",
    "cal_qwen3_14_math_separate",
    "cal_qwen3_14_math_shared",
    "cal_qwen_hotpot_separate",
    "cal_qwen_hotpot_shared",
    "separate",
    "separate_k1",
    "separate_k32",
    "shared",
    "shared_k1",
    "shared_k32",
    "shared_mps",
    "shared_mps_k1",
    "shared_mps_k32"
  ],
  "gpu_cost_basis": {
    "separate": {
      "estimated_rates": 32
    },
    "shared": {
      "estimated_rates": 32
    },
    "shared_mps": {
      "estimated_rates": 32
    }
  },
  "a3_kendall_tau_separate": 0.5667834889232944,
  "a3_basis_separate": "estimated_rates",
  "a3_kendall_tau_shared": 0.7907543837397576,
  "a3_basis_shared": "estimated_rates",
  "a3_kendall_tau_shared_mps": 0.6307751731565696,
  "a3_basis_shared_mps": "estimated_rates"
}
```

## hotpot_iso_q15_7/pareto

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| all_large | shared_mps | 0.527 | 2.02e-04 | 4.701 | estimated_rates |
| hop_1+hop_2+aggregator+verifier | separate | 0.485 | 5.69e-04 | 3.789 | estimated_rates |
| hop_1+hop_2+aggregator+verifier | shared | 0.485 | 1.82e-04 | 8.304 | estimated_rates |
| hop_1+hop_2+aggregator+verifier | shared_mps | 0.485 | 1.86e-04 | 6.153 | estimated_rates |
| planner+hop_1+hop_2+verifier | shared_mps | 0.453 | 1.94e-04 | 5.757 | estimated_rates |
| hop_2+aggregator+verifier | separate | 0.445 | 3.50e-04 | 2.93 | estimated_rates |
| hop_2+aggregator+verifier | shared | 0.445 | 1.57e-04 | 7.739 | estimated_rates |
| hop_2+aggregator+verifier | shared_mps | 0.445 | 1.77e-04 | 6.353 | estimated_rates |
| hop_1+hop_2+verifier | shared_mps | 0.438 | 1.77e-04 | 6.178 | estimated_rates |
| hop_2+verifier | separate | 0.4 | 3.12e-04 | 2.824 | estimated_rates |

10 of 30 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 3.363 | hop_2+aggregator+verifier | 0.445 |
| shared | 3.363 | all_small | 0.292 |
| shared_mps | 3.363 | all_small | 0.292 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | aggregator+verifier | 0.355 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.445 | True | estimated_rates |
| 0.5 | hop_2+aggregator+verifier | 0.445 | gpu_usd_throughput_separate | hop_1+hop_2+aggregator+verifier | 0.485 | True | estimated_rates |
| 0.75 | hop_1+hop_2+aggregator+verifier | 0.485 | gpu_usd_throughput_separate | hop_1+hop_2+aggregator+verifier | 0.485 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 96
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 96,
  "n_front": 30,
  "hypervolume_joint": 0.3003131671460668,
  "hypervolume_two_step": 0.2028015261809657,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.12749999999999995,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 3.3632502495000836,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## hotpot_iso_q15_7/pareto_api

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| all_large | separate | 0.527 | 0.012 | 4.701 | api |
| all_large | shared | 0.527 | 0.012 | 4.701 | api |
| all_large | shared_mps | 0.527 | 0.012 | 4.701 | api |
| hop_1+hop_2+aggregator+verifier | separate | 0.485 | 0.008 | 3.789 | api |
| planner+hop_2+aggregator+verifier | separate | 0.48 | 0.008 | 4.026 | api |
| hop_2+aggregator+verifier | separate | 0.445 | 0.005 | 2.93 | api |
| hop_2+verifier | separate | 0.4 | 0.004 | 2.824 | api |
| hop_2+aggregator | separate | 0.385 | 0.004 | 2.723 | api |
| only_hop_1 | separate | 0.357 | 0.004 | 3.026 | api |
| aggregator+verifier | separate | 0.355 | 0.002 | 2.626 | api |

10 of 16 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 3.363 | hop_2+aggregator+verifier | 0.445 |
| shared | 3.363 | all_small | 0.292 |
| shared_mps | 3.363 | all_small | 0.292 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | aggregator+verifier | 0.355 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.445 | True | estimated_rates |
| 0.5 | hop_2+aggregator+verifier | 0.445 | gpu_usd_throughput_separate | hop_1+hop_2+aggregator+verifier | 0.485 | True | estimated_rates |
| 0.75 | hop_1+hop_2+aggregator+verifier | 0.485 | gpu_usd_throughput_separate | hop_1+hop_2+aggregator+verifier | 0.485 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "api_usd",
  "cost_metric_requested": "api_usd",
  "cost_basis_counts": {
    "api": 96
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 96,
  "n_front": 16,
  "hypervolume_joint": 0.29026385579019515,
  "hypervolume_two_step": 0.27987527616031715,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.09250000000000003,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 3.3632502495000836,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## hotpot_iso_q15_7/pareto_estimated

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| hop_1+hop_2+aggregator+verifier | separate | 0.43 | 5.69e-04 | 3.789 | estimated_rates |
| hop_1+hop_2+aggregator+verifier | shared | 0.43 | 1.82e-04 | 8.304 | estimated_rates |
| hop_1+hop_2+aggregator+verifier | shared_mps | 0.43 | 1.86e-04 | 6.153 | estimated_rates |
| hop_1+hop_2+verifier | separate | 0.415 | 5.00e-04 | 3.611 | estimated_rates |
| hop_1+hop_2+verifier | shared | 0.415 | 1.71e-04 | 8.21 | estimated_rates |
| hop_1+hop_2+verifier | shared_mps | 0.415 | 1.77e-04 | 6.178 | estimated_rates |
| hop_1+hop_2+aggregator | separate | 0.413 | 4.80e-04 | 3.581 | estimated_rates |
| hop_1+hop_2+aggregator | shared | 0.413 | 1.66e-04 | 8.12 | estimated_rates |
| hop_1+hop_2+aggregator | shared_mps | 0.413 | 1.73e-04 | 6.17 | estimated_rates |
| hop_1+hop_2 | separate | 0.398 | 4.10e-04 | 3.374 | estimated_rates |

10 of 36 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 3.363 | hop_1+aggregator+verifier | 0.39 |
| shared | 3.363 | all_small | 0.292 |
| shared_mps | 3.363 | all_small | 0.292 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | aggregator+verifier | 0.325 | gpu_usd_throughput_separate | hop_1+hop_2+verifier | 0.415 | True | estimated_rates |
| 0.5 | hop_1+aggregator+verifier | 0.39 | gpu_usd_throughput_separate | hop_1+hop_2+aggregator+verifier | 0.43 | True | estimated_rates |
| 0.75 | hop_1+hop_2+aggregator+verifier | 0.43 | gpu_usd_throughput_separate | hop_1+hop_2+aggregator+verifier | 0.43 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 96
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 96,
  "n_front": 36,
  "hypervolume_joint": 0.25487769474423555,
  "hypervolume_two_step": 0.17191699424458412,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.08750000000000002,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 3.3632502495000836,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "regret_hypervolume": 6.320970790335556e-05,
  "regret_accuracy_mean": 0.000833333333333334
}
```

## hotpot_iso_q15_7/routing

### routing.csv

| agent | rule | threshold | routed_share | accuracy | cost | baseline_accuracy | fixed_accuracy | fixed_cost | h6_match | primary |
|---|---|---|---|---|---|---|---|---|---|---|
| hop_1 | samples_disagree |  | 0.94 | 0.335 | 0.005 | 0.285 | 0.335 | 0.004 | False | False |
| hop_1 | entropy | 0 | 0.94 | 0.335 | 0.005 | 0.285 | 0.335 | 0.004 | False | False |
| hop_1 | entropy | 0.5 | 0.94 | 0.335 | 0.005 | 0.285 | 0.335 | 0.004 | False | False |
| hop_1 | baseline_vs_majority |  | 0.65 | 0.325 | 0.004 | 0.285 | 0.335 | 0.004 | True | False |
| hop_1 | entropy | 1 | 0.85 | 0.315 | 0.004 | 0.285 | 0.335 | 0.004 | False | False |
| hop_2 | samples_disagree |  | 0.63 | 0.315 | 0.004 | 0.285 | 0.345 | 0.004 | False | True |
| hop_2 | entropy | 0 | 0.63 | 0.315 | 0.004 | 0.285 | 0.345 | 0.004 | False | False |
| hop_2 | entropy | 0.5 | 0.63 | 0.315 | 0.004 | 0.285 | 0.345 | 0.004 | False | False |

8 of 25 rows shown.

### routing_summary

```json
{
  "a4_agent": "hop_2",
  "a4_rule": "samples_disagree (K small samples not unanimous)",
  "a4_k_samples": 5,
  "a4_h6_match": false,
  "a4_row": {
    "agent": "hop_2",
    "rule": "samples_disagree",
    "threshold": "",
    "routed_share": 0.63,
    "accuracy": 0.315,
    "cost": 0.0035334135,
    "baseline_accuracy": 0.285,
    "fixed_accuracy": 0.345,
    "fixed_cost": 0.003843525,
    "h6_match": false,
    "primary": true
  },
  "note": "all other rows in routing.csv are exploratory"
}
```

## hotpot_iso_q15_7/rules

### rule_plans.csv

| rule | budget | upgraded | accuracy | best_accuracy_at_budget | regret | is_best |
|---|---|---|---|---|---|---|
| structural_topk | 1 | planner | 0.323 | 0.357 | 0.035 | False |
| structural_topk | 2 | hop_1,planner | 0.323 | 0.4 | 0.078 | False |
| structural_topk | 3 | hop_1,hop_2,planner | 0.405 | 0.445 | 0.04 | False |
| structural_topk | 4 | aggregator,hop_1,hop_2,planner | 0.365 | 0.485 | 0.12 | False |
| structural_topk | 5 | all | 0.527 | 0.527 | 0 | True |
| output_topk | 1 | verifier | 0.31 | 0.357 | 0.047 | False |
| output_topk | 2 | aggregator,verifier | 0.355 | 0.4 | 0.045 | False |
| output_topk | 3 | aggregator,hop_2,verifier | 0.445 | 0.445 | 0 | True |
| output_topk | 4 | aggregator,hop_1,hop_2,verifier | 0.485 | 0.485 | 0 | True |
| output_topk | 5 | all | 0.527 | 0.527 | 0 | True |
| ec_topk | 1 | hop_1 | 0.357 | 0.357 | 0 | True |
| ec_topk | 2 | hop_1,verifier | 0.395 | 0.4 | 0.005 | False |
| ec_topk | 3 | aggregator,hop_1,verifier | 0.44 | 0.445 | 0.005 | False |
| ec_topk | 4 | aggregator,hop_1,hop_2,verifier | 0.485 | 0.485 | 0 | True |
| ec_topk | 5 | all | 0.527 | 0.527 | 0 | True |
| ec_real_topk | 1 | hop_1 | 0.357 | 0.357 | 0 | True |

16 of 40 rows shown.

### estimator_errors.csv

| estimator | m | n_plans | n_held_out | mae_all | mae_held_out | feasibility_wrong_p25 | feasibility_wrong_p50 | feasibility_wrong_p75 |
|---|---|---|---|---|---|---|---|---|
| independence_additive | 3 | 32 | 23 | 0.031 | 0.039 | 0.174 | 0.348 | 0.304 |
| independence_multiplicative | 3 | 32 | 23 | 0.032 | 0.039 | 0.174 | 0.304 | 0.261 |
| pairwise_corrected | 3 | 32 | 23 | 0.034 | 0.047 | 0.217 | 0.391 | 0.348 |
| logit_additive | 3 | 32 | 23 | 0.031 | 0.039 | 0.174 | 0.348 | 0.304 |

### rules_summary

```json
{
  "accuracy_thresholds": {
    "p25": 0.346875,
    "p50": 0.3775,
    "p75": 0.431875
  },
  "h1c": {
    "reruns_used": 627,
    "reruns_full": 800,
    "share": 0.78375,
    "top2_full": [
      "hop_1",
      "hop_2"
    ],
    "top2_disagree_only": [
      "hop_1",
      "hop_2"
    ],
    "top2_same": true,
    "a1_uv_abs_diff": {
      "planner": 0.0,
      "hop_1": 0.0049999999999999975,
      "hop_2": 0.0,
      "aggregator": 0.015,
      "verifier": 0.0
    },
    "a1_max_uv_abs_diff": 0.015,
    "a1_share_le_half": false,
    "a1_confident_uv_full": {
      "1": [
        "hop_2"
      ],
      "2": [
        "hop_2",
        "planner"
      ]
    },
    "a1_confident_uv_disagree_only": {
      "1": [
        "hop_2"
      ],
      "2": [
        "hop_2",
        "planner"
      ]
    },
    "a1_confident_uv_same": true,
    "a1_holds_without_share": true,
    "e3_skip_variants": {
      "reruns_full": 800,
      "key": {
        "reruns_used": 627,
        "share": 0.78375,
        "uv_abs_error": {
          "planner": 0.0,
          "hop_1": 0.0049999999999999975,
          "hop_2": 0.0,
          "aggregator": 0.015,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.015
      },
      "exact": {
        "reruns_used": 739,
        "share": 0.92375,
        "uv_abs_error": {
          "planner": 0.0,
          "hop_1": 0.0,
          "hop_2": 0.0,
          "aggregator": 0.0,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.0
      }
    }
  }
}
```

## hotpot_phi/cost

### plan_costs.csv

| plan | n_problems | tokens_out_small | tokens_out_large | tokens_in_small | tokens_in_large | tokens_in | tokens_out | api_usd | gpu_seconds | gpu_seconds_shared | cost_units | model_small | model_large | gpu_usd_latency | gpu_usd_latency_1 | gpu_usd_latency_shared_1 | gpu_usd_latency_2 | gpu_usd_latency_shared_2 | gpu_usd_latency_4 | gpu_usd_latency_shared_4 | gpu_usd_throughput_separate | gpu_cost_basis_separate | gpu_usd_throughput_shared | gpu_cost_basis_shared | gpu_usd_throughput_shared_mps | gpu_cost_basis_shared_mps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_small | 400 | 315.05 | 0 | 9137.122 | 0 | 9137.122 | 315.05 | 0.001 | 10.957 | 2.739 | 5 | microsoft/Phi-3.5-mini-instruct |  | 0.006 | 0.003 | 7.61e-04 | 0.006 | 0.002 | 0.012 | 0.003 | 1.87e-04 | estimated_rates | 9.37e-05 | estimated_rates | 0.002 | fallback_latency |
| only_verifier | 400 | 264.505 | 15.633 | 7321.477 | 1557.197 | 8878.675 | 280.137 | 0.004 | 10.271 | 2.922 | 8 | microsoft/Phi-3.5-mini-instruct | microsoft/phi-4 | 0.006 | 0.003 | 8.12e-04 | 0.006 | 0.002 | 0.011 | 0.003 | 1.56e-04 | estimated_rates | 9.55e-05 | estimated_rates | 0.002 | fallback_latency |
| only_aggregator | 400 | 318.223 | 11.252 | 7273.047 | 1600.05 | 8873.097 | 329.475 | 0.004 | 11.799 | 3.234 | 8 | microsoft/Phi-3.5-mini-instruct | microsoft/phi-4 | 0.007 | 0.003 | 8.98e-04 | 0.007 | 0.002 | 0.013 | 0.004 | 1.83e-04 | estimated_rates | 1.06e-04 | estimated_rates | 0.002 | fallback_latency |
| only_planner | 400 | 140.55 | 113.96 | 7373.04 | 1441.642 | 8814.683 | 254.51 | 0.005 | 12.3 | 5.153 | 8 | microsoft/Phi-3.5-mini-instruct | microsoft/phi-4 | 0.007 | 0.003 | 0.001 | 0.007 | 0.003 | 0.014 | 0.006 | 1.66e-04 | estimated_rates | 1.31e-04 | estimated_rates | 0.003 | fallback_latency |
| only_hop_1 | 400 | 272.825 | 87.775 | 7390.142 | 1584.162 | 8974.305 | 360.6 | 0.005 | 14.971 | 5.383 | 8 | microsoft/Phi-3.5-mini-instruct | microsoft/phi-4 | 0.008 | 0.004 | 0.001 | 0.008 | 0.003 | 0.017 | 0.006 | 1.61e-04 | estimated_rates | 1.47e-04 | estimated_rates | 0.003 | fallback_latency |

5 of 32 rows shown.

### placement_costs.csv

| run | plan | placement | gpu_seconds_per_problem | gpu_usd_throughput | source | repeats |
|---|---|---|---|---|---|---|
| cal_granite_hotpot_separate | all_large | separate | 0.851 | 4.73e-04 | measured | 3 |
| cal_granite_hotpot_separate | all_small | separate | 0.434 | 2.41e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_large | shared | 0.408 | 2.27e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_small | shared | 0.208 | 1.16e-04 | measured | 3 |
| cal_granite_math_separate | all_large | separate | 0.774 | 4.30e-04 | measured | 3 |
| cal_granite_math_separate | all_small | separate | 0.333 | 1.85e-04 | measured | 3 |
| cal_granite_math_shared | all_large | shared | 0.367 | 2.04e-04 | measured | 3 |
| cal_granite_math_shared | all_small | shared | 0.187 | 1.04e-04 | measured | 3 |
| cal_phi_math_separate | all_large | separate | 1.486 | 8.26e-04 | measured | 3 |
| cal_phi_math_separate | all_small | separate | 0.536 | 2.98e-04 | measured | 3 |
| cal_phi_math_shared | all_large | shared | 0.745 | 4.14e-04 | measured | 3 |
| cal_phi_math_shared | all_small | shared | 0.266 | 1.48e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_large | separate | 1.219 | 6.77e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_small | separate | 0.282 | 1.57e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_large | shared | 0.599 | 3.33e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_small | shared | 0.147 | 8.17e-05 | measured | 3 |
| cal_qwen_hotpot_separate | all_large | separate | 0.251 | 1.39e-04 | measured | 3 |
| cal_qwen_hotpot_separate | all_small | separate | 0.106 | 5.87e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_large | shared | 0.124 | 6.91e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_small | shared | 0.054 | 2.98e-05 | measured | 3 |
| separate | aggregator+verifier | separate | 0.422 | 2.35e-04 | measured | 3 |
| separate | all_large | separate | 0.504 | 2.80e-04 | measured | 3 |
| separate | all_small | separate | 0.21 | 1.17e-04 | measured | 3 |
| separate | only_aggregator | separate | 0.248 | 1.38e-04 | measured | 3 |
| separate | only_planner | separate | 0.227 | 1.26e-04 | measured | 3 |
| separate | only_verifier | separate | 0.367 | 2.04e-04 | measured | 3 |
| separate | planner+verifier | separate | 0.383 | 2.13e-04 | measured | 3 |
| separate_k1 | aggregator+verifier | separate | 4.857 | 0.003 | measured | 3 |
| separate_k1 | all_large | separate | 5.576 | 0.003 | measured | 3 |
| separate_k1 | all_small | separate | 2.367 | 0.001 | measured | 3 |

30 of 83 rows shown.

### cost_summary

```json
{
  "n_plans": 32,
  "api_large_small_ratio": 17.802989020406027,
  "a3_kendall_tau_latency_vs_units": 0.5302168122185658,
  "p5_runs": [
    "cal_granite_hotpot_separate",
    "cal_granite_hotpot_shared",
    "cal_granite_math_separate",
    "cal_granite_math_shared",
    "cal_phi_math_separate",
    "cal_phi_math_shared",
    "cal_qwen3_14_math_separate",
    "cal_qwen3_14_math_shared",
    "cal_qwen_hotpot_separate",
    "cal_qwen_hotpot_shared",
    "separate",
    "separate_k1",
    "separate_k32",
    "shared",
    "shared_k1",
    "shared_k32",
    "shared_mps",
    "shared_mps_k1",
    "shared_mps_k32"
  ],
  "gpu_cost_basis": {
    "separate": {
      "estimated_rates": 32
    },
    "shared": {
      "estimated_rates": 32
    },
    "shared_mps": {
      "fallback_latency": 32
    }
  },
  "a3_kendall_tau_separate": 0.6901960228017537,
  "a3_basis_separate": "estimated_rates",
  "a3_kendall_tau_shared": 0.6810543536255715,
  "a3_basis_shared": "estimated_rates",
  "a3_kendall_tau_shared_mps": 0.7176210303303002,
  "a3_basis_shared_mps": "fallback"
}
```

## hotpot_phi/pareto

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+verifier | separate | 0.54 | 2.01e-04 | 16.555 | estimated_rates |
| planner+verifier | shared | 0.54 | 1.32e-04 | 39.334 | estimated_rates |
| planner+aggregator | separate | 0.512 | 1.95e-04 | 17.957 | estimated_rates |
| hop_1+verifier | separate | 0.512 | 1.66e-04 | 20.408 | estimated_rates |
| only_aggregator | separate | 0.505 | 1.83e-04 | 16.861 | estimated_rates |
| only_aggregator | shared | 0.505 | 1.06e-04 | 32.04 | estimated_rates |
| only_verifier | separate | 0.5 | 1.56e-04 | 14.914 | estimated_rates |
| only_verifier | shared | 0.5 | 9.55e-05 | 32.341 | estimated_rates |
| aggregator+verifier | separate | 0.49 | 1.46e-04 | 15.439 | estimated_rates |
| all_small | shared | 0.427 | 9.37e-05 | 16.346 | estimated_rates |

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 24.52 | planner+verifier | 0.54 |
| shared | 24.52 | all_small | 0.427 |
| shared_mps | 24.52 | all_small | 0.427 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_aggregator | 0.505 | gpu_usd_throughput_separate | planner+verifier | 0.54 | True | estimated_rates |
| 0.5 | planner+verifier | 0.54 | gpu_usd_throughput_separate | planner+verifier | 0.54 | False | estimated_rates |
| 0.75 | planner+verifier | 0.54 | gpu_usd_throughput_separate | planner+verifier | 0.54 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 64,
    "fallback_latency": 32
  },
  "any_fallback": true,
  "k": 16,
  "n_candidates": 96,
  "n_front": 10,
  "hypervolume_joint": 0.42147511245360747,
  "hypervolume_two_step": 0.40762541316780154,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.03500000000000003,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 24.519576391501232,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## hotpot_phi/pareto_api

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+verifier | separate | 0.54 | 0.008 | 16.555 | api |
| only_aggregator | separate | 0.505 | 0.004 | 16.861 | api |
| only_verifier | separate | 0.5 | 0.004 | 14.914 | api |
| all_small | separate | 0.427 | 0.001 | 16.346 | api |
| all_small | shared | 0.427 | 0.001 | 16.346 | api |
| all_small | shared_mps | 0.427 | 0.001 | 16.346 | api |

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 24.52 | planner+verifier | 0.54 |
| shared | 24.52 | all_small | 0.427 |
| shared_mps | 24.52 | all_small | 0.427 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_aggregator | 0.505 | gpu_usd_throughput_separate | planner+verifier | 0.54 | True | estimated_rates |
| 0.5 | planner+verifier | 0.54 | gpu_usd_throughput_separate | planner+verifier | 0.54 | False | estimated_rates |
| 0.75 | planner+verifier | 0.54 | gpu_usd_throughput_separate | planner+verifier | 0.54 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "api_usd",
  "cost_metric_requested": "api_usd",
  "cost_basis_counts": {
    "api": 96
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 96,
  "n_front": 6,
  "hypervolume_joint": 0.38134677628586516,
  "hypervolume_two_step": 0.37306481096511646,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.0,
  "a2_gap_ge_2_points": false,
  "h3a_limit_s": 24.519576391501232,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## hotpot_phi/pareto_estimated

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+hop_1+hop_2+verifier | separate | 0.595 | 4.77e-04 | 28.359 | estimated_rates |
| planner+hop_1+hop_2+verifier | shared | 0.595 | 2.46e-04 | 33.967 | estimated_rates |
| planner+hop_1+verifier | separate | 0.568 | 3.46e-04 | 21.73 | estimated_rates |
| planner+hop_1+verifier | shared | 0.568 | 1.93e-04 | 44.068 | estimated_rates |
| planner+hop_2+verifier | separate | 0.568 | 3.26e-04 | 22.057 | estimated_rates |
| planner+hop_2+verifier | shared | 0.568 | 1.84e-04 | 47.337 | estimated_rates |
| hop_1+hop_2+aggregator | separate | 0.56 | 2.94e-04 | 28.167 | estimated_rates |
| hop_1+hop_2+verifier | separate | 0.555 | 2.95e-04 | 26.533 | estimated_rates |
| all_large | shared | 0.55 | 2.54e-04 | 28.908 | estimated_rates |
| planner+verifier | separate | 0.54 | 2.01e-04 | 16.555 | estimated_rates |

10 of 20 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 24.52 | planner+hop_2+verifier | 0.568 |
| shared | 24.52 | all_small | 0.427 |
| shared_mps | 24.52 | all_small | 0.427 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_aggregator | 0.505 | gpu_usd_throughput_separate | planner+verifier | 0.54 | True | estimated_rates |
| 0.5 | planner+verifier | 0.54 | gpu_usd_throughput_separate | planner+hop_2+verifier | 0.568 | True | estimated_rates |
| 0.75 | planner+hop_2+verifier | 0.568 | gpu_usd_throughput_separate | planner+hop_2+verifier | 0.568 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 64,
    "fallback_latency": 32
  },
  "any_fallback": true,
  "k": 16,
  "n_candidates": 96,
  "n_front": 20,
  "hypervolume_joint": 0.45622057458183907,
  "hypervolume_two_step": 0.4416662017663694,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.06250000000000011,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 24.519576391501232,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "regret_hypervolume": 0.0,
  "regret_accuracy_mean": 0.0
}
```

## hotpot_phi/routing

### routing.csv

| agent | rule | threshold | routed_share | accuracy | cost | baseline_accuracy | fixed_accuracy | fixed_cost | h6_match | primary |
|---|---|---|---|---|---|---|---|---|---|---|
| aggregator | samples_disagree |  | 0.24 | 0.5 | 0.003 | 0.465 | 0.505 | 0.004 | True | False |
| aggregator | entropy | 0 | 0.24 | 0.5 | 0.003 | 0.465 | 0.505 | 0.004 | True | False |
| aggregator | entropy | 0.5 | 0.24 | 0.5 | 0.003 | 0.465 | 0.505 | 0.004 | True | False |
| aggregator | entropy | 1 | 0.08 | 0.49 | 0.002 | 0.465 | 0.505 | 0.004 | False | False |
| planner | baseline_vs_majority |  | 0.275 | 0.485 | 0.005 | 0.465 | 0.45 | 0.005 | False | False |
| verifier | samples_disagree |  | 0.27 | 0.485 | 0.003 | 0.465 | 0.48 | 0.004 | True | False |
| verifier | entropy | 0 | 0.27 | 0.485 | 0.003 | 0.465 | 0.48 | 0.004 | True | False |
| verifier | entropy | 0.5 | 0.27 | 0.485 | 0.003 | 0.465 | 0.48 | 0.004 | True | False |

8 of 25 rows shown.

### routing_summary

```json
{
  "a4_agent": "planner",
  "a4_rule": "samples_disagree (K small samples not unanimous)",
  "a4_k_samples": 3,
  "a4_h6_match": false,
  "a4_row": {
    "agent": "planner",
    "rule": "samples_disagree",
    "threshold": "",
    "routed_share": 0.42,
    "accuracy": 0.46,
    "cost": 0.005968658,
    "baseline_accuracy": 0.465,
    "fixed_accuracy": 0.45,
    "fixed_cost": 0.0049174625,
    "h6_match": false,
    "primary": true
  },
  "note": "all other rows in routing.csv are exploratory"
}
```

## hotpot_phi/rules

### rule_plans.csv

| rule | budget | upgraded | accuracy | best_accuracy_at_budget | regret | is_best |
|---|---|---|---|---|---|---|
| structural_topk | 1 | planner | 0.47 | 0.505 | 0.035 | False |
| structural_topk | 2 | hop_1,planner | 0.455 | 0.54 | 0.085 | False |
| structural_topk | 3 | hop_1,hop_2,planner | 0.47 | 0.54 | 0.07 | False |
| structural_topk | 4 | aggregator,hop_1,hop_2,planner | 0.517 | 0.54 | 0.023 | False |
| structural_topk | 5 | all | 0.5 | 0.54 | 0.04 | False |
| output_topk | 1 | verifier | 0.5 | 0.505 | 0.005 | False |
| output_topk | 2 | aggregator,verifier | 0.49 | 0.54 | 0.05 | False |
| output_topk | 3 | aggregator,hop_2,verifier | 0.48 | 0.54 | 0.06 | False |
| output_topk | 4 | aggregator,hop_1,hop_2,verifier | 0.475 | 0.54 | 0.065 | False |
| output_topk | 5 | all | 0.5 | 0.54 | 0.04 | False |
| ec_topk | 1 | verifier | 0.5 | 0.505 | 0.005 | False |
| ec_topk | 2 | aggregator,verifier | 0.49 | 0.54 | 0.05 | False |
| ec_topk | 3 | aggregator,hop_2,verifier | 0.48 | 0.54 | 0.06 | False |
| ec_topk | 4 | aggregator,hop_2,planner,verifier | 0.51 | 0.54 | 0.03 | False |
| ec_topk | 5 | all | 0.5 | 0.54 | 0.04 | False |
| ec_real_topk | 1 | aggregator | 0.505 | 0.505 | 0 | True |

16 of 40 rows shown.

### estimator_errors.csv

| estimator | m | n_plans | n_held_out | mae_all | mae_held_out | feasibility_wrong_p25 | feasibility_wrong_p50 | feasibility_wrong_p75 |
|---|---|---|---|---|---|---|---|---|
| independence_additive | 3 | 32 | 23 | 0.056 | 0.073 | 0.174 | 0.261 | 0.522 |
| independence_multiplicative | 3 | 32 | 23 | 0.071 | 0.092 | 0.174 | 0.261 | 0.522 |
| pairwise_corrected | 3 | 32 | 23 | 0.028 | 0.039 | 0.174 | 0.304 | 0.565 |
| logit_additive | 3 | 32 | 23 | 0.056 | 0.073 | 0.174 | 0.261 | 0.522 |

### rules_summary

```json
{
  "accuracy_thresholds": {
    "p25": 0.47875,
    "p50": 0.5025,
    "p75": 0.5125
  },
  "h1c": {
    "reruns_used": 618,
    "reruns_full": 800,
    "share": 0.7725,
    "top2_full": [
      "aggregator",
      "verifier"
    ],
    "top2_disagree_only": [
      "aggregator",
      "verifier"
    ],
    "top2_same": true,
    "a1_uv_abs_diff": {
      "planner": 0.0,
      "hop_1": 0.009999999999999998,
      "hop_2": 0.005,
      "aggregator": 0.015,
      "verifier": 0.0
    },
    "a1_max_uv_abs_diff": 0.015,
    "a1_share_le_half": false,
    "a1_confident_uv_full": {
      "1": [
        "planner"
      ],
      "2": [
        "hop_1",
        "planner"
      ]
    },
    "a1_confident_uv_disagree_only": {
      "1": [
        "aggregator"
      ],
      "2": [
        "aggregator",
        "planner"
      ]
    },
    "a1_confident_uv_same": false,
    "a1_holds_without_share": false,
    "e3_skip_variants": {
      "reruns_full": 800,
      "key": {
        "reruns_used": 618,
        "share": 0.7725,
        "uv_abs_error": {
          "planner": 0.0,
          "hop_1": 0.009999999999999998,
          "hop_2": 0.005,
          "aggregator": 0.015,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.015
      },
      "exact": {
        "reruns_used": 800,
        "share": 1.0,
        "uv_abs_error": {
          "planner": 0.0,
          "hop_1": 0.0,
          "hop_2": 0.0,
          "aggregator": 0.0,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.0
      }
    }
  }
}
```

## hotpot_q15_7/cost

### plan_costs.csv

| plan | n_problems | tokens_out_small | tokens_out_large | tokens_in_small | tokens_in_large | tokens_in | tokens_out | api_usd | gpu_seconds | gpu_seconds_shared | cost_units | model_small | model_large | gpu_usd_latency | gpu_usd_latency_1 | gpu_usd_latency_shared_1 | gpu_usd_latency_2 | gpu_usd_latency_shared_2 | gpu_usd_latency_4 | gpu_usd_latency_shared_4 | gpu_usd_throughput_separate | gpu_cost_basis_separate | gpu_usd_throughput_shared | gpu_cost_basis_shared | gpu_usd_throughput_shared_mps | gpu_cost_basis_shared_mps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_small | 400 | 128.99 | 0 | 7873.89 | 0 | 7873.89 | 128.99 | 8.52e-04 | 1.727 | 0.432 | 5 | Qwen/Qwen2.5-1.5B-Instruct |  | 9.59e-04 | 4.80e-04 | 1.20e-04 | 9.59e-04 | 2.40e-04 | 0.002 | 4.80e-04 | 5.65e-04 | estimated_rates | 1.18e-04 | estimated_rates | 1.83e-04 | estimated_rates |
| only_hop_2 | 400 | 102.358 | 23.058 | 6291.89 | 1577.22 | 7869.11 | 125.415 | 0.004 | 2.059 | 0.728 | 8 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.001 | 5.72e-04 | 2.02e-04 | 0.001 | 4.05e-04 | 0.002 | 8.09e-04 | 4.50e-04 | estimated_rates | 1.37e-04 | estimated_rates | 1.85e-04 | estimated_rates |
| only_planner | 400 | 94.035 | 38.63 | 6375.512 | 1503.43 | 7878.943 | 132.665 | 0.004 | 2.424 | 0.962 | 8 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.001 | 6.73e-04 | 2.67e-04 | 0.001 | 5.34e-04 | 0.003 | 0.001 | 4.32e-04 | estimated_rates | 1.54e-04 | estimated_rates | 2.03e-04 | estimated_rates |
| only_aggregator | 400 | 114.483 | 13.21 | 6237.752 | 1637.48 | 7875.233 | 127.692 | 0.004 | 1.973 | 0.638 | 8 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.001 | 5.48e-04 | 1.77e-04 | 0.001 | 3.54e-04 | 0.002 | 7.09e-04 | 4.77e-04 | estimated_rates | 1.32e-04 | estimated_rates | 1.79e-04 | estimated_rates |
| only_hop_1 | 400 | 90.132 | 38.09 | 6333.845 | 1543.892 | 7877.738 | 128.222 | 0.004 | 2.346 | 0.935 | 8 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.001 | 6.52e-04 | 2.60e-04 | 0.001 | 5.20e-04 | 0.003 | 0.001 | 4.21e-04 | estimated_rates | 1.51e-04 | estimated_rates | 1.99e-04 | estimated_rates |

5 of 32 rows shown.

### placement_costs.csv

| run | plan | placement | gpu_seconds_per_problem | gpu_usd_throughput | source | repeats |
|---|---|---|---|---|---|---|
| cal_granite_hotpot_separate | all_large | separate | 0.851 | 4.73e-04 | measured | 3 |
| cal_granite_hotpot_separate | all_small | separate | 0.434 | 2.41e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_large | shared | 0.408 | 2.27e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_small | shared | 0.208 | 1.16e-04 | measured | 3 |
| cal_granite_math_separate | all_large | separate | 0.774 | 4.30e-04 | measured | 3 |
| cal_granite_math_separate | all_small | separate | 0.333 | 1.85e-04 | measured | 3 |
| cal_granite_math_shared | all_large | shared | 0.367 | 2.04e-04 | measured | 3 |
| cal_granite_math_shared | all_small | shared | 0.187 | 1.04e-04 | measured | 3 |
| cal_phi_math_separate | all_large | separate | 1.486 | 8.26e-04 | measured | 3 |
| cal_phi_math_separate | all_small | separate | 0.536 | 2.98e-04 | measured | 3 |
| cal_phi_math_shared | all_large | shared | 0.745 | 4.14e-04 | measured | 3 |
| cal_phi_math_shared | all_small | shared | 0.266 | 1.48e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_large | separate | 1.219 | 6.77e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_small | separate | 0.282 | 1.57e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_large | shared | 0.599 | 3.33e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_small | shared | 0.147 | 8.17e-05 | measured | 3 |
| cal_qwen_hotpot_separate | all_large | separate | 0.251 | 1.39e-04 | measured | 3 |
| cal_qwen_hotpot_separate | all_small | separate | 0.106 | 5.87e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_large | shared | 0.124 | 6.91e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_small | shared | 0.054 | 2.98e-05 | measured | 3 |
| separate | aggregator+verifier | separate | 0.422 | 2.35e-04 | measured | 3 |
| separate | all_large | separate | 0.504 | 2.80e-04 | measured | 3 |
| separate | all_small | separate | 0.21 | 1.17e-04 | measured | 3 |
| separate | only_aggregator | separate | 0.248 | 1.38e-04 | measured | 3 |
| separate | only_planner | separate | 0.227 | 1.26e-04 | measured | 3 |
| separate | only_verifier | separate | 0.367 | 2.04e-04 | measured | 3 |
| separate | planner+verifier | separate | 0.383 | 2.13e-04 | measured | 3 |
| separate_k1 | aggregator+verifier | separate | 4.857 | 0.003 | measured | 3 |
| separate_k1 | all_large | separate | 5.576 | 0.003 | measured | 3 |
| separate_k1 | all_small | separate | 2.367 | 0.001 | measured | 3 |

30 of 83 rows shown.

### cost_summary

```json
{
  "n_plans": 32,
  "api_large_small_ratio": 20.119916561409735,
  "a3_kendall_tau_latency_vs_units": 0.8181793912683041,
  "p5_runs": [
    "cal_granite_hotpot_separate",
    "cal_granite_hotpot_shared",
    "cal_granite_math_separate",
    "cal_granite_math_shared",
    "cal_phi_math_separate",
    "cal_phi_math_shared",
    "cal_qwen3_14_math_separate",
    "cal_qwen3_14_math_shared",
    "cal_qwen_hotpot_separate",
    "cal_qwen_hotpot_shared",
    "separate",
    "separate_k1",
    "separate_k32",
    "shared",
    "shared_k1",
    "shared_k32",
    "shared_mps",
    "shared_mps_k1",
    "shared_mps_k32"
  ],
  "gpu_cost_basis": {
    "separate": {
      "estimated_rates": 32
    },
    "shared": {
      "estimated_rates": 32
    },
    "shared_mps": {
      "estimated_rates": 32
    }
  },
  "a3_kendall_tau_separate": 0.6353460077446608,
  "a3_basis_separate": "estimated_rates",
  "a3_kendall_tau_shared": 0.8318918950325773,
  "a3_basis_shared": "estimated_rates",
  "a3_kendall_tau_shared_mps": 0.5256459776304747,
  "a3_basis_shared_mps": "estimated_rates"
}
```

## hotpot_q15_7/pareto

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+hop_1+aggregator+verifier | separate | 0.505 | 8.70e-04 | 5.516 | estimated_rates |
| planner+hop_1+aggregator+verifier | shared_mps | 0.505 | 2.39e-04 | 7.909 | estimated_rates |
| aggregator+verifier | separate | 0.49 | 3.92e-04 | 4.095 | estimated_rates |
| aggregator+verifier | shared | 0.49 | 1.76e-04 | 10.41 | estimated_rates |
| aggregator+verifier | shared_mps | 0.49 | 2.06e-04 | 8.226 | estimated_rates |
| all_large | shared_mps | 0.49 | 2.33e-04 | 5.955 | estimated_rates |
| hop_1+aggregator+verifier | shared_mps | 0.487 | 2.22e-04 | 7.971 | estimated_rates |
| hop_1+hop_2+aggregator+verifier | shared_mps | 0.48 | 2.17e-04 | 7.613 | estimated_rates |
| hop_2+aggregator+verifier | shared | 0.475 | 1.91e-04 | 10.38 | estimated_rates |
| hop_2+aggregator+verifier | shared_mps | 0.475 | 2.04e-04 | 7.954 | estimated_rates |

10 of 25 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 3.584 | hop_1+aggregator | 0.435 |
| shared | 3.584 | all_small | 0.312 |
| shared_mps | 3.584 | all_small | 0.312 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_verifier | 0.432 | gpu_usd_throughput_separate | aggregator+verifier | 0.49 | True | estimated_rates |
| 0.5 | aggregator+verifier | 0.49 | gpu_usd_throughput_separate | aggregator+verifier | 0.49 | False | estimated_rates |
| 0.75 | aggregator+verifier | 0.49 | gpu_usd_throughput_separate | planner+hop_1+aggregator+verifier | 0.505 | True | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 96
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 96,
  "n_front": 25,
  "hypervolume_joint": 0.316585914024696,
  "hypervolume_two_step": 0.21582237687081707,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.1225,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 3.5840995312502173,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## hotpot_q15_7/pareto_api

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+hop_1+aggregator+verifier | separate | 0.505 | 0.014 | 5.516 | api |
| aggregator+verifier | separate | 0.49 | 0.007 | 4.095 | api |
| hop_1+hop_2+aggregator | separate | 0.44 | 0.011 | 3.812 | api |
| hop_1+aggregator | separate | 0.435 | 0.007 | 3.413 | api |
| only_verifier | separate | 0.432 | 0.004 | 3.8 | api |
| only_aggregator | separate | 0.422 | 0.004 | 2.689 | api |
| only_planner | separate | 0.34 | 0.004 | 3.203 | api |
| only_hop_2 | separate | 0.325 | 0.004 | 2.647 | api |
| all_small | separate | 0.312 | 8.52e-04 | 2.389 | api |
| all_small | shared | 0.312 | 8.52e-04 | 2.389 | api |

10 of 11 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 3.584 | hop_1+aggregator | 0.435 |
| shared | 3.584 | all_small | 0.312 |
| shared_mps | 3.584 | all_small | 0.312 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_verifier | 0.432 | gpu_usd_throughput_separate | aggregator+verifier | 0.49 | True | estimated_rates |
| 0.5 | aggregator+verifier | 0.49 | gpu_usd_throughput_separate | aggregator+verifier | 0.49 | False | estimated_rates |
| 0.75 | aggregator+verifier | 0.49 | gpu_usd_throughput_separate | planner+hop_1+aggregator+verifier | 0.505 | True | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "api_usd",
  "cost_metric_requested": "api_usd",
  "cost_basis_counts": {
    "api": 96
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 96,
  "n_front": 11,
  "hypervolume_joint": 0.32295146261801705,
  "hypervolume_two_step": 0.31349835280576854,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.1225,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 3.5840995312502173,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## hotpot_q15_7/pareto_estimated

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+hop_2+aggregator+verifier | separate | 0.53 | 8.07e-04 | 5.047 | estimated_rates |
| planner+hop_2+aggregator+verifier | shared_mps | 0.53 | 2.26e-04 | 7.794 | estimated_rates |
| planner+aggregator+verifier | separate | 0.518 | 6.17e-04 | 4.743 | estimated_rates |
| planner+aggregator+verifier | shared | 0.518 | 2.10e-04 | 11.016 | estimated_rates |
| planner+aggregator+verifier | shared_mps | 0.518 | 2.23e-04 | 8.506 | estimated_rates |
| hop_2+aggregator+verifier | separate | 0.502 | 5.44e-04 | 4.337 | estimated_rates |
| hop_2+aggregator+verifier | shared | 0.502 | 1.91e-04 | 10.38 | estimated_rates |
| hop_2+aggregator+verifier | shared_mps | 0.502 | 2.04e-04 | 7.954 | estimated_rates |
| aggregator+verifier | separate | 0.49 | 3.92e-04 | 4.095 | estimated_rates |
| aggregator+verifier | shared | 0.49 | 1.76e-04 | 10.41 | estimated_rates |

10 of 29 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 3.584 | planner+aggregator | 0.45 |
| shared | 3.584 | all_small | 0.312 |
| shared_mps | 3.584 | all_small | 0.312 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_verifier | 0.432 | gpu_usd_throughput_separate | planner+aggregator+verifier | 0.518 | True | estimated_rates |
| 0.5 | aggregator+verifier | 0.49 | gpu_usd_throughput_separate | planner+aggregator+verifier | 0.518 | True | estimated_rates |
| 0.75 | planner+aggregator+verifier | 0.518 | gpu_usd_throughput_separate | planner+hop_2+aggregator+verifier | 0.53 | True | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 96
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 96,
  "n_front": 29,
  "hypervolume_joint": 0.32741871629570324,
  "hypervolume_two_step": 0.22237975723596792,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.1225,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 3.5840995312502173,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "regret_hypervolume": 0.0043914282283221695,
  "regret_accuracy_mean": 0.007500000000000002
}
```

## hotpot_q15_7/routing

### routing.csv

| agent | rule | threshold | routed_share | accuracy | cost | baseline_accuracy | fixed_accuracy | fixed_cost | h6_match | primary |
|---|---|---|---|---|---|---|---|---|---|---|
| aggregator | samples_disagree |  | 0.63 | 0.415 | 0.004 | 0.35 | 0.44 | 0.004 | False | True |
| aggregator | entropy | 0 | 0.63 | 0.415 | 0.004 | 0.35 | 0.44 | 0.004 | False | False |
| aggregator | entropy | 0.5 | 0.63 | 0.415 | 0.004 | 0.35 | 0.44 | 0.004 | False | False |
| verifier | samples_disagree |  | 0.445 | 0.41 | 0.003 | 0.35 | 0.415 | 0.004 | True | False |
| verifier | entropy | 0 | 0.445 | 0.41 | 0.003 | 0.35 | 0.415 | 0.004 | True | False |
| verifier | entropy | 0.5 | 0.445 | 0.41 | 0.003 | 0.35 | 0.415 | 0.004 | True | False |
| verifier | entropy | 1 | 0.195 | 0.395 | 0.002 | 0.35 | 0.415 | 0.004 | False | False |
| aggregator | entropy | 1 | 0.37 | 0.39 | 0.003 | 0.35 | 0.44 | 0.004 | False | False |

8 of 25 rows shown.

### routing_summary

```json
{
  "a4_agent": "aggregator",
  "a4_rule": "samples_disagree (K small samples not unanimous)",
  "a4_k_samples": 5,
  "a4_h6_match": false,
  "a4_row": {
    "agent": "aggregator",
    "rule": "samples_disagree",
    "threshold": "",
    "routed_share": 0.63,
    "accuracy": 0.415,
    "cost": 0.003779749,
    "baseline_accuracy": 0.35,
    "fixed_accuracy": 0.44,
    "fixed_cost": 0.0041444360000000005,
    "h6_match": false,
    "primary": true
  },
  "note": "all other rows in routing.csv are exploratory"
}
```

## hotpot_q15_7/rules

### rule_plans.csv

| rule | budget | upgraded | accuracy | best_accuracy_at_budget | regret | is_best |
|---|---|---|---|---|---|---|
| structural_topk | 1 | planner | 0.34 | 0.432 | 0.092 | False |
| structural_topk | 2 | hop_1,planner | 0.35 | 0.49 | 0.14 | False |
| structural_topk | 3 | hop_1,hop_2,planner | 0.378 | 0.49 | 0.112 | False |
| structural_topk | 4 | aggregator,hop_1,hop_2,planner | 0.427 | 0.505 | 0.078 | False |
| structural_topk | 5 | all | 0.49 | 0.505 | 0.015 | False |
| output_topk | 1 | verifier | 0.432 | 0.432 | 0 | True |
| output_topk | 2 | aggregator,verifier | 0.49 | 0.49 | 0 | True |
| output_topk | 3 | aggregator,hop_2,verifier | 0.475 | 0.49 | 0.015 | False |
| output_topk | 4 | aggregator,hop_1,hop_2,verifier | 0.48 | 0.505 | 0.025 | False |
| output_topk | 5 | all | 0.49 | 0.505 | 0.015 | False |
| ec_topk | 1 | verifier | 0.432 | 0.432 | 0 | True |
| ec_topk | 2 | aggregator,verifier | 0.49 | 0.49 | 0 | True |
| ec_topk | 3 | aggregator,hop_1,verifier | 0.487 | 0.49 | 0.003 | False |
| ec_topk | 4 | aggregator,hop_1,planner,verifier | 0.505 | 0.505 | 0 | True |
| ec_topk | 5 | all | 0.49 | 0.505 | 0.015 | False |
| ec_real_topk | 1 | verifier | 0.432 | 0.432 | 0 | True |

16 of 40 rows shown.

### estimator_errors.csv

| estimator | m | n_plans | n_held_out | mae_all | mae_held_out | feasibility_wrong_p25 | feasibility_wrong_p50 | feasibility_wrong_p75 |
|---|---|---|---|---|---|---|---|---|
| independence_additive | 3 | 32 | 23 | 0.057 | 0.073 | 0.087 | 0.304 | 0.391 |
| independence_multiplicative | 3 | 32 | 23 | 0.093 | 0.118 | 0.087 | 0.304 | 0.435 |
| pairwise_corrected | 3 | 32 | 23 | 0.023 | 0.031 | 0.087 | 0.304 | 0.391 |
| logit_additive | 3 | 32 | 23 | 0.064 | 0.081 | 0.087 | 0.304 | 0.391 |

### rules_summary

```json
{
  "accuracy_thresholds": {
    "p25": 0.40125,
    "p50": 0.43125,
    "p75": 0.455625
  },
  "h1c": {
    "reruns_used": 632,
    "reruns_full": 800,
    "share": 0.79,
    "top2_full": [
      "aggregator",
      "verifier"
    ],
    "top2_disagree_only": [
      "aggregator",
      "verifier"
    ],
    "top2_same": true,
    "a1_uv_abs_diff": {
      "planner": 0.0,
      "hop_1": 0.0,
      "hop_2": 0.005,
      "aggregator": 0.0,
      "verifier": 0.0
    },
    "a1_max_uv_abs_diff": 0.005,
    "a1_share_le_half": false,
    "a1_confident_uv_full": {
      "1": [
        "aggregator"
      ],
      "2": [
        "aggregator",
        "verifier"
      ]
    },
    "a1_confident_uv_disagree_only": {
      "1": [
        "aggregator"
      ],
      "2": [
        "aggregator",
        "verifier"
      ]
    },
    "a1_confident_uv_same": true,
    "a1_holds_without_share": true,
    "e3_skip_variants": {
      "reruns_full": 800,
      "key": {
        "reruns_used": 632,
        "share": 0.79,
        "uv_abs_error": {
          "planner": 0.0,
          "hop_1": 0.0,
          "hop_2": 0.005,
          "aggregator": 0.0,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.005
      },
      "exact": {
        "reruns_used": 727,
        "share": 0.90875,
        "uv_abs_error": {
          "planner": 0.0,
          "hop_1": 0.0,
          "hop_2": 0.0,
          "aggregator": 0.0,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.0
      }
    }
  }
}
```

## math_granite/cost

### plan_costs.csv

| plan | n_problems | tokens_out_small | tokens_out_large | tokens_in_small | tokens_in_large | tokens_in | tokens_out | api_usd | gpu_seconds | gpu_seconds_shared | cost_units | model_small | model_large | gpu_usd_latency | gpu_usd_latency_1 | gpu_usd_latency_shared_1 | gpu_usd_latency_2 | gpu_usd_latency_shared_2 | gpu_usd_latency_4 | gpu_usd_latency_shared_4 | gpu_usd_throughput_separate | gpu_cost_basis_separate | gpu_usd_throughput_shared | gpu_cost_basis_shared | gpu_usd_throughput_shared_mps | gpu_cost_basis_shared_mps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_small | 400 | 446.793 | 0 | 1727.37 | 0 | 1727.37 | 446.793 | 3.96e-04 | 5.193 | 1.298 | 6 | ibm-granite/granite-3.1-2b-instruct |  | 0.003 | 0.001 | 3.61e-04 | 0.003 | 7.21e-04 | 0.006 | 0.001 | 1.92e-04 | estimated_rates | 9.76e-05 | estimated_rates | 7.21e-04 | fallback_latency |
| only_aggregator | 400 | 450.55 | 53.705 | 1558.582 | 167.338 | 1725.92 | 504.255 | 0.001 | 6.347 | 1.933 | 9 | ibm-granite/granite-3.1-2b-instruct | ibm-granite/granite-3.1-8b-instruct | 0.004 | 0.002 | 5.37e-04 | 0.004 | 0.001 | 0.007 | 0.002 | 1.92e-04 | estimated_rates | 1.23e-04 | estimated_rates | 0.001 | fallback_latency |
| only_step_1 | 400 | 424.467 | 19.953 | 1365.3 | 360.74 | 1726.04 | 444.42 | 0.001 | 5.341 | 1.473 | 9 | ibm-granite/granite-3.1-2b-instruct | ibm-granite/granite-3.1-8b-instruct | 0.003 | 0.001 | 4.09e-04 | 0.003 | 8.18e-04 | 0.006 | 0.002 | 1.80e-04 | estimated_rates | 1.04e-04 | estimated_rates | 8.18e-04 | fallback_latency |
| only_step_2 | 400 | 413.238 | 41.63 | 1354.068 | 383.142 | 1737.21 | 454.868 | 0.002 | 5.658 | 1.685 | 9 | ibm-granite/granite-3.1-2b-instruct | ibm-granite/granite-3.1-8b-instruct | 0.003 | 0.002 | 4.68e-04 | 0.003 | 9.36e-04 | 0.006 | 0.002 | 1.75e-04 | estimated_rates | 1.11e-04 | estimated_rates | 9.36e-04 | fallback_latency |
| only_step_3 | 400 | 395.998 | 45 | 1296.938 | 424.735 | 1721.672 | 440.998 | 0.002 | 5.548 | 1.679 | 9 | ibm-granite/granite-3.1-2b-instruct | ibm-granite/granite-3.1-8b-instruct | 0.003 | 0.002 | 4.66e-04 | 0.003 | 9.33e-04 | 0.006 | 0.002 | 1.68e-04 | estimated_rates | 1.09e-04 | estimated_rates | 9.33e-04 | fallback_latency |

5 of 64 rows shown.

### placement_costs.csv

| run | plan | placement | gpu_seconds_per_problem | gpu_usd_throughput | source | repeats |
|---|---|---|---|---|---|---|
| cal_granite_hotpot_separate | all_large | separate | 0.851 | 4.73e-04 | measured | 3 |
| cal_granite_hotpot_separate | all_small | separate | 0.434 | 2.41e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_large | shared | 0.408 | 2.27e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_small | shared | 0.208 | 1.16e-04 | measured | 3 |
| cal_granite_math_separate | all_large | separate | 0.774 | 4.30e-04 | measured | 3 |
| cal_granite_math_separate | all_small | separate | 0.333 | 1.85e-04 | measured | 3 |
| cal_granite_math_shared | all_large | shared | 0.367 | 2.04e-04 | measured | 3 |
| cal_granite_math_shared | all_small | shared | 0.187 | 1.04e-04 | measured | 3 |
| cal_phi_math_separate | all_large | separate | 1.486 | 8.26e-04 | measured | 3 |
| cal_phi_math_separate | all_small | separate | 0.536 | 2.98e-04 | measured | 3 |
| cal_phi_math_shared | all_large | shared | 0.745 | 4.14e-04 | measured | 3 |
| cal_phi_math_shared | all_small | shared | 0.266 | 1.48e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_large | separate | 1.219 | 6.77e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_small | separate | 0.282 | 1.57e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_large | shared | 0.599 | 3.33e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_small | shared | 0.147 | 8.17e-05 | measured | 3 |
| cal_qwen_hotpot_separate | all_large | separate | 0.251 | 1.39e-04 | measured | 3 |
| cal_qwen_hotpot_separate | all_small | separate | 0.106 | 5.87e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_large | shared | 0.124 | 6.91e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_small | shared | 0.054 | 2.98e-05 | measured | 3 |
| separate | aggregator+verifier | separate | 0.422 | 2.35e-04 | measured | 3 |
| separate | all_large | separate | 0.504 | 2.80e-04 | measured | 3 |
| separate | all_small | separate | 0.21 | 1.17e-04 | measured | 3 |
| separate | only_aggregator | separate | 0.248 | 1.38e-04 | measured | 3 |
| separate | only_planner | separate | 0.227 | 1.26e-04 | measured | 3 |
| separate | only_verifier | separate | 0.367 | 2.04e-04 | measured | 3 |
| separate | planner+verifier | separate | 0.383 | 2.13e-04 | measured | 3 |
| separate_k1 | aggregator+verifier | separate | 4.857 | 0.003 | measured | 3 |
| separate_k1 | all_large | separate | 5.576 | 0.003 | measured | 3 |
| separate_k1 | all_small | separate | 2.367 | 0.001 | measured | 3 |

30 of 83 rows shown.

### cost_summary

```json
{
  "n_plans": 64,
  "api_large_small_ratio": 19.55620993693407,
  "a3_kendall_tau_latency_vs_units": 0.6990579154939568,
  "p5_runs": [
    "cal_granite_hotpot_separate",
    "cal_granite_hotpot_shared",
    "cal_granite_math_separate",
    "cal_granite_math_shared",
    "cal_phi_math_separate",
    "cal_phi_math_shared",
    "cal_qwen3_14_math_separate",
    "cal_qwen3_14_math_shared",
    "cal_qwen_hotpot_separate",
    "cal_qwen_hotpot_shared",
    "separate",
    "separate_k1",
    "separate_k32",
    "shared",
    "shared_k1",
    "shared_k32",
    "shared_mps",
    "shared_mps_k1",
    "shared_mps_k32"
  ],
  "gpu_cost_basis": {
    "separate": {
      "estimated_rates": 64
    },
    "shared": {
      "estimated_rates": 64
    },
    "shared_mps": {
      "fallback_latency": 64
    }
  },
  "a3_kendall_tau_separate": 0.6106969949755207,
  "a3_basis_separate": "estimated_rates",
  "a3_kendall_tau_shared": 0.730375710108086,
  "a3_basis_shared": "estimated_rates",
  "a3_kendall_tau_shared_mps": 0.6934654521700052,
  "a3_basis_shared_mps": "fallback"
}
```

## math_granite/pareto

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+step_2+step_3+aggregator+verifier | separate | 0.75 | 4.20e-04 | 13.307 | estimated_rates |
| planner+step_2+step_3+aggregator+verifier | shared | 0.75 | 2.09e-04 | 20.136 | estimated_rates |
| all_large | shared | 0.743 | 2.12e-04 | 13.697 | estimated_rates |
| planner+step_1+aggregator+verifier | separate | 0.738 | 3.54e-04 | 12.353 | estimated_rates |
| planner+step_1+aggregator+verifier | shared | 0.738 | 1.89e-04 | 25.429 | estimated_rates |
| planner+step_2+aggregator+verifier | shared | 0.733 | 1.97e-04 | 25.02 | estimated_rates |
| planner+step_1+step_3+aggregator+verifier | shared | 0.73 | 2.02e-04 | 21.788 | estimated_rates |
| planner+step_3+aggregator+verifier | shared | 0.723 | 1.94e-04 | 25.324 | estimated_rates |
| planner+step_1+verifier | separate | 0.718 | 3.03e-04 | 12.007 | estimated_rates |
| planner+step_1+verifier | shared | 0.718 | 1.78e-04 | 26.588 | estimated_rates |

10 of 47 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 11.609 | planner+verifier | 0.703 |
| shared | 11.609 | all_small | 0.472 |
| shared_mps | 11.609 | all_small | 0.472 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_verifier | 0.66 | gpu_usd_throughput_separate | step_1+aggregator+verifier | 0.695 | True | estimated_rates |
| 0.5 | planner+verifier | 0.703 | gpu_usd_throughput_separate | planner+step_1+verifier | 0.718 | True | estimated_rates |
| 0.75 | planner+step_1+aggregator+verifier | 0.738 | gpu_usd_throughput_separate | planner+step_1+aggregator+verifier | 0.738 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 128,
    "fallback_latency": 64
  },
  "any_fallback": true,
  "k": 16,
  "n_candidates": 192,
  "n_front": 47,
  "hypervolume_joint": 0.5163459359622415,
  "hypervolume_two_step": 0.5023227410973787,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.08999999999999997,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 11.609032994250128,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## math_granite/pareto_api

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+step_2+step_3+aggregator+verifier | separate | 0.75 | 0.007 | 13.307 | api |
| planner+step_1+aggregator+verifier | separate | 0.738 | 0.006 | 12.353 | api |
| planner+step_1+verifier | separate | 0.718 | 0.005 | 12.007 | api |
| step_2+step_3+aggregator+verifier | separate | 0.705 | 0.005 | 11.808 | api |
| planner+verifier | separate | 0.703 | 0.004 | 11.59 | api |
| step_1+aggregator+verifier | separate | 0.695 | 0.004 | 10.826 | api |
| aggregator+verifier | separate | 0.677 | 0.003 | 10.509 | api |
| only_verifier | separate | 0.66 | 0.002 | 10.005 | api |
| planner+step_1 | separate | 0.618 | 0.003 | 9.727 | api |
| only_planner | separate | 0.588 | 0.002 | 9.304 | api |

10 of 16 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 11.609 | planner+verifier | 0.703 |
| shared | 11.609 | all_small | 0.472 |
| shared_mps | 11.609 | all_small | 0.472 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_verifier | 0.66 | gpu_usd_throughput_separate | step_1+aggregator+verifier | 0.695 | True | estimated_rates |
| 0.5 | planner+verifier | 0.703 | gpu_usd_throughput_separate | planner+step_1+verifier | 0.718 | True | estimated_rates |
| 0.75 | planner+step_1+aggregator+verifier | 0.738 | gpu_usd_throughput_separate | planner+step_1+aggregator+verifier | 0.738 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "api_usd",
  "cost_metric_requested": "api_usd",
  "cost_basis_counts": {
    "api": 192
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 192,
  "n_front": 16,
  "hypervolume_joint": 0.45256763993771854,
  "hypervolume_two_step": 0.44202451363874073,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.03499999999999992,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 11.609032994250128,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## math_granite/pareto_estimated

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+step_1+step_2+step_3+verifier | separate | 0.768 | 4.07e-04 | 13.353 | estimated_rates |
| planner+step_1+step_2+step_3+verifier | shared | 0.768 | 2.05e-04 | 21.928 | estimated_rates |
| planner+step_1+step_3+verifier | separate | 0.755 | 3.54e-04 | 12.855 | estimated_rates |
| planner+step_1+step_3+verifier | shared | 0.755 | 1.93e-04 | 26.342 | estimated_rates |
| planner+step_1+step_2+verifier | separate | 0.75 | 3.55e-04 | 12.71 | estimated_rates |
| planner+step_1+step_2+verifier | shared | 0.75 | 1.91e-04 | 25.593 | estimated_rates |
| step_1+step_2+step_3+aggregator+verifier | separate | 0.742 | 2.91e-04 | 12.338 | estimated_rates |
| step_1+step_2+step_3+aggregator+verifier | shared | 0.742 | 1.84e-04 | 28.841 | estimated_rates |
| planner+step_1+verifier | separate | 0.738 | 3.03e-04 | 12.007 | estimated_rates |
| planner+step_1+verifier | shared | 0.738 | 1.78e-04 | 26.588 | estimated_rates |

10 of 46 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 11.609 | step_1+step_2+aggregator+verifier | 0.725 |
| shared | 11.609 | all_small | 0.472 |
| shared_mps | 11.609 | all_small | 0.472 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_verifier | 0.66 | gpu_usd_throughput_separate | step_1+step_3+aggregator+verifier | 0.73 | True | estimated_rates |
| 0.5 | step_1+aggregator+verifier | 0.712 | gpu_usd_throughput_separate | step_1+step_2+step_3+aggregator+verifier | 0.742 | True | estimated_rates |
| 0.75 | planner+step_1+step_2+verifier | 0.75 | gpu_usd_throughput_separate | planner+step_1+step_3+verifier | 0.755 | True | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 128,
    "fallback_latency": 64
  },
  "any_fallback": true,
  "k": 16,
  "n_candidates": 192,
  "n_front": 46,
  "hypervolume_joint": 0.527181003281797,
  "hypervolume_two_step": 0.5116906691725429,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.10750000000000004,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 11.609032994250128,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "regret_hypervolume": 0.012640278347549438,
  "regret_accuracy_mean": 0.00936170212765958
}
```

## math_granite/routing

### routing.csv

| agent | rule | threshold | routed_share | accuracy | cost | baseline_accuracy | fixed_accuracy | fixed_cost | h6_match | primary |
|---|---|---|---|---|---|---|---|---|---|---|
| verifier | samples_disagree |  | 0.615 | 0.655 | 0.002 | 0.535 | 0.695 | 0.002 | False | True |
| verifier | entropy | 0 | 0.615 | 0.655 | 0.002 | 0.535 | 0.695 | 0.002 | False | False |
| verifier | entropy | 0.5 | 0.615 | 0.655 | 0.002 | 0.535 | 0.695 | 0.002 | False | False |
| verifier | entropy | 1 | 0.31 | 0.615 | 0.001 | 0.535 | 0.695 | 0.002 | False | False |
| planner | samples_disagree |  | 0.65 | 0.61 | 0.003 | 0.535 | 0.595 | 0.002 | False | False |
| planner | baseline_vs_majority |  | 0.46 | 0.61 | 0.002 | 0.535 | 0.595 | 0.002 | False | False |
| planner | entropy | 0 | 0.65 | 0.61 | 0.003 | 0.535 | 0.595 | 0.002 | False | False |
| planner | entropy | 0.5 | 0.65 | 0.61 | 0.003 | 0.535 | 0.595 | 0.002 | False | False |

8 of 30 rows shown.

### routing_summary

```json
{
  "a4_agent": "verifier",
  "a4_rule": "samples_disagree (K small samples not unanimous)",
  "a4_k_samples": 5,
  "a4_h6_match": false,
  "a4_row": {
    "agent": "verifier",
    "rule": "samples_disagree",
    "threshold": "",
    "routed_share": 0.615,
    "accuracy": 0.655,
    "cost": 0.0018095214999999999,
    "baseline_accuracy": 0.535,
    "fixed_accuracy": 0.695,
    "fixed_cost": 0.0020052375,
    "h6_match": false,
    "primary": true
  },
  "note": "all other rows in routing.csv are exploratory"
}
```

## math_granite/rules

### rule_plans.csv

| rule | budget | upgraded | accuracy | best_accuracy_at_budget | regret | is_best |
|---|---|---|---|---|---|---|
| structural_topk | 1 | planner | 0.588 | 0.66 | 0.073 | False |
| structural_topk | 2 | planner,step_1 | 0.618 | 0.703 | 0.085 | False |
| structural_topk | 3 | planner,step_1,step_2 | 0.583 | 0.718 | 0.135 | False |
| structural_topk | 4 | planner,step_1,step_2,step_3 | 0.625 | 0.738 | 0.113 | False |
| structural_topk | 5 | aggregator,planner,step_1,step_2,step_3 | 0.675 | 0.75 | 0.075 | False |
| structural_topk | 6 | all | 0.743 | 0.75 | 0.007 | False |
| output_topk | 1 | verifier | 0.66 | 0.66 | 0 | True |
| output_topk | 2 | aggregator,verifier | 0.677 | 0.703 | 0.025 | False |
| output_topk | 3 | aggregator,step_3,verifier | 0.675 | 0.718 | 0.042 | False |
| output_topk | 4 | aggregator,step_2,step_3,verifier | 0.705 | 0.738 | 0.033 | False |
| output_topk | 5 | aggregator,step_1,step_2,step_3,verifier | 0.685 | 0.75 | 0.065 | False |
| output_topk | 6 | all | 0.743 | 0.75 | 0.007 | False |
| ec_topk | 1 | verifier | 0.66 | 0.66 | 0 | True |
| ec_topk | 2 | planner,verifier | 0.703 | 0.703 | 0 | True |
| ec_topk | 3 | aggregator,planner,verifier | 0.698 | 0.718 | 0.02 | False |
| ec_topk | 4 | aggregator,planner,step_3,verifier | 0.723 | 0.738 | 0.015 | False |

16 of 48 rows shown.

### estimator_errors.csv

| estimator | m | n_plans | n_held_out | mae_all | mae_held_out | feasibility_wrong_p25 | feasibility_wrong_p50 | feasibility_wrong_p75 |
|---|---|---|---|---|---|---|---|---|
| independence_additive | 3 | 64 | 54 | 0.051 | 0.057 | 0.056 | 0.111 | 0.222 |
| independence_multiplicative | 3 | 64 | 54 | 0.086 | 0.097 | 0.074 | 0.13 | 0.315 |
| pairwise_corrected | 3 | 64 | 54 | 0.022 | 0.027 | 0.056 | 0.056 | 0.259 |
| logit_additive | 3 | 64 | 54 | 0.038 | 0.042 | 0.056 | 0.093 | 0.204 |

### rules_summary

```json
{
  "accuracy_thresholds": {
    "p25": 0.571875,
    "p50": 0.66,
    "p75": 0.6956249999999999
  },
  "h1c": {
    "reruns_used": 351,
    "reruns_full": 1000,
    "share": 0.351,
    "top2_full": [
      "planner",
      "verifier"
    ],
    "top2_disagree_only": [
      "aggregator",
      "verifier"
    ],
    "top2_same": false,
    "a1_uv_abs_diff": {
      "planner": 0.0,
      "step_1": 0.04,
      "step_2": 0.030000000000000002,
      "step_3": 0.01,
      "aggregator": 0.03,
      "verifier": 0.0
    },
    "a1_max_uv_abs_diff": 0.04,
    "a1_share_le_half": true,
    "a1_confident_uv_full": {
      "1": [
        "verifier"
      ],
      "2": [
        "planner",
        "verifier"
      ]
    },
    "a1_confident_uv_disagree_only": {
      "1": [
        "verifier"
      ],
      "2": [
        "aggregator",
        "verifier"
      ]
    },
    "a1_confident_uv_same": false,
    "a1_holds_without_share": false,
    "e3_skip_variants": {
      "reruns_full": 1000,
      "key": {
        "reruns_used": 349,
        "share": 0.349,
        "uv_abs_error": {
          "planner": 0.0,
          "step_1": 0.04,
          "step_2": 0.030000000000000002,
          "step_3": 0.01,
          "aggregator": 0.03,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.04
      },
      "exact": {
        "reruns_used": 879,
        "share": 0.879,
        "uv_abs_error": {
          "planner": 0.0,
          "step_1": 0.005000000000000001,
          "step_2": 0.0,
          "step_3": 0.0,
          "aggregator": 0.0,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.005000000000000001
      }
    }
  }
}
```

## math_phi/cost

### plan_costs.csv

| plan | n_problems | tokens_out_small | tokens_out_large | tokens_in_small | tokens_in_large | tokens_in | tokens_out | api_usd | gpu_seconds | gpu_seconds_shared | cost_units | model_small | model_large | gpu_usd_latency | gpu_usd_latency_1 | gpu_usd_latency_shared_1 | gpu_usd_latency_2 | gpu_usd_latency_shared_2 | gpu_usd_latency_4 | gpu_usd_latency_shared_4 | gpu_usd_throughput_separate | gpu_cost_basis_separate | gpu_usd_throughput_shared | gpu_cost_basis_shared | gpu_usd_throughput_shared_mps | gpu_cost_basis_shared_mps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_small | 400 | 547.977 | 0 | 1724.085 | 0 | 1724.085 | 547.977 | 4.46e-04 | 8.241 | 2.06 | 6 | microsoft/Phi-3.5-mini-instruct |  | 0.005 | 0.002 | 5.72e-04 | 0.005 | 0.001 | 0.009 | 0.002 | 2.83e-04 | estimated_rates | 1.41e-04 | estimated_rates | 0.001 | fallback_latency |
| only_planner | 400 | 379.145 | 99.595 | 1366.505 | 129.507 | 1496.013 | 478.74 | 0.002 | 9.264 | 3.319 | 9 | microsoft/Phi-3.5-mini-instruct | microsoft/phi-4 | 0.005 | 0.003 | 9.22e-04 | 0.005 | 0.002 | 0.01 | 0.004 | 1.96e-04 | estimated_rates | 1.66e-04 | estimated_rates | 0.002 | fallback_latency |
| only_step_1 | 400 | 571.615 | 71.047 | 1526.757 | 303.587 | 1830.345 | 642.663 | 0.002 | 11.052 | 3.488 | 9 | microsoft/Phi-3.5-mini-instruct | microsoft/phi-4 | 0.006 | 0.003 | 9.69e-04 | 0.006 | 0.002 | 0.012 | 0.004 | 2.95e-04 | estimated_rates | 1.96e-04 | estimated_rates | 0.002 | fallback_latency |
| only_step_2 | 400 | 509.817 | 74.355 | 1378.533 | 331.11 | 1709.642 | 584.173 | 0.002 | 10.171 | 3.299 | 9 | microsoft/Phi-3.5-mini-instruct | microsoft/phi-4 | 0.006 | 0.003 | 9.16e-04 | 0.006 | 0.002 | 0.011 | 0.004 | 2.63e-04 | estimated_rates | 1.83e-04 | estimated_rates | 0.002 | fallback_latency |
| only_aggregator | 400 | 460.71 | 128.738 | 1675.402 | 140.17 | 1815.572 | 589.447 | 0.002 | 11.221 | 4.102 | 9 | microsoft/Phi-3.5-mini-instruct | microsoft/phi-4 | 0.006 | 0.003 | 0.001 | 0.006 | 0.002 | 0.012 | 0.005 | 2.39e-04 | estimated_rates | 2.07e-04 | estimated_rates | 0.002 | fallback_latency |

5 of 64 rows shown.

### placement_costs.csv

| run | plan | placement | gpu_seconds_per_problem | gpu_usd_throughput | source | repeats |
|---|---|---|---|---|---|---|
| cal_granite_hotpot_separate | all_large | separate | 0.851 | 4.73e-04 | measured | 3 |
| cal_granite_hotpot_separate | all_small | separate | 0.434 | 2.41e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_large | shared | 0.408 | 2.27e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_small | shared | 0.208 | 1.16e-04 | measured | 3 |
| cal_granite_math_separate | all_large | separate | 0.774 | 4.30e-04 | measured | 3 |
| cal_granite_math_separate | all_small | separate | 0.333 | 1.85e-04 | measured | 3 |
| cal_granite_math_shared | all_large | shared | 0.367 | 2.04e-04 | measured | 3 |
| cal_granite_math_shared | all_small | shared | 0.187 | 1.04e-04 | measured | 3 |
| cal_phi_math_separate | all_large | separate | 1.486 | 8.26e-04 | measured | 3 |
| cal_phi_math_separate | all_small | separate | 0.536 | 2.98e-04 | measured | 3 |
| cal_phi_math_shared | all_large | shared | 0.745 | 4.14e-04 | measured | 3 |
| cal_phi_math_shared | all_small | shared | 0.266 | 1.48e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_large | separate | 1.219 | 6.77e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_small | separate | 0.282 | 1.57e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_large | shared | 0.599 | 3.33e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_small | shared | 0.147 | 8.17e-05 | measured | 3 |
| cal_qwen_hotpot_separate | all_large | separate | 0.251 | 1.39e-04 | measured | 3 |
| cal_qwen_hotpot_separate | all_small | separate | 0.106 | 5.87e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_large | shared | 0.124 | 6.91e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_small | shared | 0.054 | 2.98e-05 | measured | 3 |
| separate | aggregator+verifier | separate | 0.422 | 2.35e-04 | measured | 3 |
| separate | all_large | separate | 0.504 | 2.80e-04 | measured | 3 |
| separate | all_small | separate | 0.21 | 1.17e-04 | measured | 3 |
| separate | only_aggregator | separate | 0.248 | 1.38e-04 | measured | 3 |
| separate | only_planner | separate | 0.227 | 1.26e-04 | measured | 3 |
| separate | only_verifier | separate | 0.367 | 2.04e-04 | measured | 3 |
| separate | planner+verifier | separate | 0.383 | 2.13e-04 | measured | 3 |
| separate_k1 | aggregator+verifier | separate | 4.857 | 0.003 | measured | 3 |
| separate_k1 | all_large | separate | 5.576 | 0.003 | measured | 3 |
| separate_k1 | all_small | separate | 2.367 | 0.001 | measured | 3 |

30 of 83 rows shown.

### cost_summary

```json
{
  "n_plans": 64,
  "api_large_small_ratio": 20.03073495636452,
  "a3_kendall_tau_latency_vs_units": 0.6901099741756341,
  "p5_runs": [
    "cal_granite_hotpot_separate",
    "cal_granite_hotpot_shared",
    "cal_granite_math_separate",
    "cal_granite_math_shared",
    "cal_phi_math_separate",
    "cal_phi_math_shared",
    "cal_qwen3_14_math_separate",
    "cal_qwen3_14_math_shared",
    "cal_qwen_hotpot_separate",
    "cal_qwen_hotpot_shared",
    "separate",
    "separate_k1",
    "separate_k32",
    "shared",
    "shared_k1",
    "shared_k32",
    "shared_mps",
    "shared_mps_k1",
    "shared_mps_k32"
  ],
  "gpu_cost_basis": {
    "separate": {
      "estimated_rates": 64
    },
    "shared": {
      "estimated_rates": 64
    },
    "shared_mps": {
      "fallback_latency": 64
    }
  },
  "a3_kendall_tau_separate": 0.7068873641474891,
  "a3_basis_separate": "estimated_rates",
  "a3_kendall_tau_shared": 0.7124798274714408,
  "a3_basis_shared": "estimated_rates",
  "a3_kendall_tau_shared_mps": 0.750508578074312,
  "a3_basis_shared_mps": "fallback"
}
```

## math_phi/pareto

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+step_1+step_2+step_3+verifier | separate | 0.96 | 7.56e-04 | 26.261 | estimated_rates |
| planner+step_1+step_2+step_3+verifier | shared | 0.96 | 3.82e-04 | 27.297 | estimated_rates |
| step_2+step_3+verifier | separate | 0.958 | 4.91e-04 | 23.109 | estimated_rates |
| step_2+step_3+verifier | shared | 0.958 | 3.19e-04 | 54.264 | estimated_rates |
| planner+step_1+step_2+verifier | shared | 0.958 | 3.41e-04 | 40.132 | estimated_rates |
| step_3+verifier | separate | 0.955 | 4.03e-04 | 21.209 | estimated_rates |
| step_3+verifier | shared | 0.955 | 2.88e-04 | 52.495 | estimated_rates |
| planner+step_2+verifier | separate | 0.955 | 5.19e-04 | 20.86 | estimated_rates |
| planner+step_2+verifier | shared | 0.955 | 3.03e-04 | 43.193 | estimated_rates |
| planner+verifier | separate | 0.95 | 4.14e-04 | 18.895 | estimated_rates |

10 of 23 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 19.175 | planner+verifier | 0.95 |
| shared | 19.175 | all_small | 0.745 |
| shared_mps | 19.175 | all_small | 0.745 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_aggregator | 0.848 | gpu_usd_throughput_separate | step_3+verifier | 0.955 | True | estimated_rates |
| 0.5 | step_3+verifier | 0.955 | gpu_usd_throughput_separate | step_2+step_3+verifier | 0.958 | True | estimated_rates |
| 0.75 | step_2+step_3+verifier | 0.958 | gpu_usd_throughput_separate | step_2+step_3+verifier | 0.958 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 128,
    "fallback_latency": 64
  },
  "any_fallback": true,
  "k": 16,
  "n_candidates": 192,
  "n_front": 23,
  "hypervolume_joint": 0.7423666752951429,
  "hypervolume_two_step": 0.7299786279823439,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.012500000000000067,
  "a2_gap_ge_2_points": false,
  "h3a_limit_s": 19.17452235674773,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## math_phi/pareto_api

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+step_1+step_2+step_3+verifier | separate | 0.96 | 0.008 | 26.261 | api |
| step_2+step_3+verifier | separate | 0.958 | 0.006 | 23.109 | api |
| step_3+verifier | separate | 0.955 | 0.004 | 21.209 | api |
| planner+step_2+verifier | separate | 0.955 | 0.005 | 20.86 | api |
| planner+verifier | separate | 0.95 | 0.004 | 18.895 | api |
| only_verifier | separate | 0.945 | 0.003 | 18.51 | api |
| only_aggregator | separate | 0.848 | 0.002 | 17.776 | api |
| planner+step_3 | separate | 0.78 | 0.003 | 15.98 | api |
| only_planner | separate | 0.762 | 0.002 | 13.25 | api |
| all_small | separate | 0.745 | 4.46e-04 | 12.783 | api |

10 of 12 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 19.175 | planner+verifier | 0.95 |
| shared | 19.175 | all_small | 0.745 |
| shared_mps | 19.175 | all_small | 0.745 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_aggregator | 0.848 | gpu_usd_throughput_separate | step_3+verifier | 0.955 | True | estimated_rates |
| 0.5 | step_3+verifier | 0.955 | gpu_usd_throughput_separate | step_2+step_3+verifier | 0.958 | True | estimated_rates |
| 0.75 | step_2+step_3+verifier | 0.958 | gpu_usd_throughput_separate | step_2+step_3+verifier | 0.958 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "api_usd",
  "cost_metric_requested": "api_usd",
  "cost_basis_counts": {
    "api": 192
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 192,
  "n_front": 12,
  "hypervolume_joint": 0.6823152572017032,
  "hypervolume_two_step": 0.6726175969390036,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.0050000000000000044,
  "a2_gap_ge_2_points": false,
  "h3a_limit_s": 19.17452235674773,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## math_phi/pareto_estimated

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+step_1+verifier | separate | 0.953 | 5.18e-04 | 21.433 | estimated_rates |
| planner+step_1+verifier | shared | 0.953 | 3.21e-04 | 46.533 | estimated_rates |
| planner+step_1+step_2+verifier | shared | 0.95 | 3.41e-04 | 40.132 | estimated_rates |
| planner+verifier | separate | 0.95 | 4.14e-04 | 18.895 | estimated_rates |
| planner+verifier | shared | 0.95 | 2.66e-04 | 44.088 | estimated_rates |
| step_1+verifier | separate | 0.948 | 3.72e-04 | 20.927 | estimated_rates |
| planner+step_2+verifier | shared | 0.948 | 3.03e-04 | 43.193 | estimated_rates |
| only_verifier | separate | 0.945 | 2.74e-04 | 18.51 | estimated_rates |
| only_verifier | shared | 0.945 | 2.40e-04 | 49.738 | estimated_rates |
| step_1+aggregator | separate | 0.85 | 2.53e-04 | 19.689 | estimated_rates |

10 of 18 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 19.175 | planner+verifier | 0.95 |
| shared | 19.175 | all_small | 0.745 |
| shared_mps | 19.175 | all_small | 0.745 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_aggregator | 0.848 | gpu_usd_throughput_separate | planner+verifier | 0.95 | True | estimated_rates |
| 0.5 | planner+verifier | 0.95 | gpu_usd_throughput_separate | planner+step_1+verifier | 0.953 | True | estimated_rates |
| 0.75 | planner+step_1+verifier | 0.953 | gpu_usd_throughput_separate | planner+step_1+verifier | 0.953 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 128,
    "fallback_latency": 64
  },
  "any_fallback": true,
  "k": 16,
  "n_candidates": 192,
  "n_front": 18,
  "hypervolume_joint": 0.7373216895569619,
  "hypervolume_two_step": 0.7255953012751467,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.007500000000000062,
  "a2_gap_ge_2_points": false,
  "h3a_limit_s": 19.17452235674773,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "regret_hypervolume": 0.003262653613363198,
  "regret_accuracy_mean": 0.00347826086956523
}
```

## math_phi/routing

### routing.csv

| agent | rule | threshold | routed_share | accuracy | cost | baseline_accuracy | fixed_accuracy | fixed_cost | h6_match | primary |
|---|---|---|---|---|---|---|---|---|---|---|
| verifier | samples_disagree |  | 0.36 | 0.91 | 0.002 | 0.75 | 0.93 | 0.003 | False | True |
| verifier | entropy | 0 | 0.36 | 0.91 | 0.002 | 0.75 | 0.93 | 0.003 | False | False |
| verifier | entropy | 0.5 | 0.36 | 0.91 | 0.002 | 0.75 | 0.93 | 0.003 | False | False |
| verifier | baseline_vs_majority |  | 0.11 | 0.835 | 0.001 | 0.75 | 0.93 | 0.003 | False | False |
| aggregator | samples_disagree |  | 0.16 | 0.82 | 0.001 | 0.75 | 0.91 | 0.002 | False | False |
| aggregator | entropy | 0 | 0.16 | 0.82 | 0.001 | 0.75 | 0.91 | 0.002 | False | False |
| aggregator | entropy | 0.5 | 0.16 | 0.82 | 0.001 | 0.75 | 0.91 | 0.002 | False | False |
| verifier | entropy | 1 | 0.15 | 0.82 | 0.001 | 0.75 | 0.93 | 0.003 | False | False |

8 of 30 rows shown.

### routing_summary

```json
{
  "a4_agent": "verifier",
  "a4_rule": "samples_disagree (K small samples not unanimous)",
  "a4_k_samples": 5,
  "a4_h6_match": false,
  "a4_row": {
    "agent": "verifier",
    "rule": "samples_disagree",
    "threshold": "",
    "routed_share": 0.36,
    "accuracy": 0.91,
    "cost": 0.0018681995,
    "baseline_accuracy": 0.75,
    "fixed_accuracy": 0.93,
    "fixed_cost": 0.002690324,
    "h6_match": false,
    "primary": true
  },
  "note": "all other rows in routing.csv are exploratory"
}
```

## math_phi/rules

### rule_plans.csv

| rule | budget | upgraded | accuracy | best_accuracy_at_budget | regret | is_best |
|---|---|---|---|---|---|---|
| structural_topk | 1 | planner | 0.762 | 0.945 | 0.182 | False |
| structural_topk | 2 | planner,step_1 | 0.755 | 0.955 | 0.2 | False |
| structural_topk | 3 | planner,step_1,step_2 | 0.762 | 0.958 | 0.195 | False |
| structural_topk | 4 | planner,step_1,step_2,step_3 | 0.785 | 0.958 | 0.172 | False |
| structural_topk | 5 | aggregator,planner,step_1,step_2,step_3 | 0.765 | 0.96 | 0.195 | False |
| structural_topk | 6 | all | 0.95 | 0.96 | 0.01 | False |
| output_topk | 1 | verifier | 0.945 | 0.945 | 0 | True |
| output_topk | 2 | aggregator,verifier | 0.948 | 0.955 | 0.007 | False |
| output_topk | 3 | aggregator,step_3,verifier | 0.943 | 0.958 | 0.015 | False |
| output_topk | 4 | aggregator,step_2,step_3,verifier | 0.948 | 0.958 | 0.01 | False |
| output_topk | 5 | aggregator,step_1,step_2,step_3,verifier | 0.953 | 0.96 | 0.007 | False |
| output_topk | 6 | all | 0.95 | 0.96 | 0.01 | False |
| ec_topk | 1 | verifier | 0.945 | 0.945 | 0 | True |
| ec_topk | 2 | aggregator,verifier | 0.948 | 0.955 | 0.007 | False |
| ec_topk | 3 | aggregator,step_3,verifier | 0.943 | 0.958 | 0.015 | False |
| ec_topk | 4 | aggregator,planner,step_3,verifier | 0.953 | 0.958 | 0.005 | False |

16 of 48 rows shown.

### estimator_errors.csv

| estimator | m | n_plans | n_held_out | mae_all | mae_held_out | feasibility_wrong_p25 | feasibility_wrong_p50 | feasibility_wrong_p75 |
|---|---|---|---|---|---|---|---|---|
| independence_additive | 3 | 64 | 54 | 0.029 | 0.032 | 0.074 | 0 | 0.241 |
| independence_multiplicative | 3 | 64 | 54 | 0.029 | 0.033 | 0.074 | 0 | 0.241 |
| pairwise_corrected | 3 | 64 | 54 | 0.017 | 0.021 | 0.074 | 0 | 0.296 |
| logit_additive | 3 | 64 | 54 | 0.021 | 0.024 | 0.074 | 0 | 0.37 |

### rules_summary

```json
{
  "accuracy_thresholds": {
    "p25": 0.77625,
    "p50": 0.89375,
    "p75": 0.9525
  },
  "h1c": {
    "reruns_used": 476,
    "reruns_full": 1000,
    "share": 0.476,
    "top2_full": [
      "aggregator",
      "verifier"
    ],
    "top2_disagree_only": [
      "aggregator",
      "verifier"
    ],
    "top2_same": true,
    "a1_uv_abs_diff": {
      "planner": 0.0,
      "step_1": 0.01,
      "step_2": 0.015,
      "step_3": 0.0,
      "aggregator": 0.06,
      "verifier": 0.0
    },
    "a1_max_uv_abs_diff": 0.06,
    "a1_share_le_half": true,
    "a1_confident_uv_full": {
      "1": [
        "verifier"
      ],
      "2": [
        "aggregator",
        "verifier"
      ]
    },
    "a1_confident_uv_disagree_only": {
      "1": [
        "verifier"
      ],
      "2": [
        "aggregator",
        "verifier"
      ]
    },
    "a1_confident_uv_same": true,
    "a1_holds_without_share": false,
    "e3_skip_variants": {
      "reruns_full": 1000,
      "key": {
        "reruns_used": 474,
        "share": 0.474,
        "uv_abs_error": {
          "planner": 0.0,
          "step_1": 0.01,
          "step_2": 0.015,
          "step_3": 0.0,
          "aggregator": 0.06,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.06
      },
      "exact": {
        "reruns_used": 1000,
        "share": 1.0,
        "uv_abs_error": {
          "planner": 0.0,
          "step_1": 0.0,
          "step_2": 0.0,
          "step_3": 0.0,
          "aggregator": 0.0,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.0
      }
    }
  }
}
```

## math_q15_7/cost

### plan_costs.csv

| plan | n_problems | tokens_out_small | tokens_out_large | tokens_in_small | tokens_in_large | tokens_in | tokens_out | api_usd | gpu_seconds | gpu_seconds_shared | cost_units | model_small | model_large | gpu_usd_latency | gpu_usd_latency_1 | gpu_usd_latency_shared_1 | gpu_usd_latency_2 | gpu_usd_latency_shared_2 | gpu_usd_latency_4 | gpu_usd_latency_shared_4 | gpu_usd_throughput_separate | gpu_cost_basis_separate | gpu_usd_throughput_shared | gpu_cost_basis_shared | gpu_usd_throughput_shared_mps | gpu_cost_basis_shared_mps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_small | 400 | 396.522 | 0 | 1316.01 | 0 | 1316.01 | 396.522 | 3.30e-04 | 3.747 | 0.937 | 6 | Qwen/Qwen2.5-1.5B-Instruct |  | 0.002 | 0.001 | 2.60e-04 | 0.002 | 5.20e-04 | 0.004 | 0.001 | 0.001 | estimated_rates | 3.10e-04 | estimated_rates | 3.30e-04 | estimated_rates |
| only_step_1 | 400 | 306.017 | 17.37 | 981.227 | 205.393 | 1186.62 | 323.387 | 8.36e-04 | 3.213 | 0.897 | 9 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.002 | 8.93e-04 | 2.49e-04 | 0.002 | 4.98e-04 | 0.004 | 9.97e-04 | 7.76e-04 | estimated_rates | 2.67e-04 | estimated_rates | 2.82e-04 | estimated_rates |
| only_step_2 | 400 | 354.35 | 19.71 | 1013.115 | 279.345 | 1292.46 | 374.06 | 0.001 | 3.669 | 1.022 | 9 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.002 | 0.001 | 2.84e-04 | 0.002 | 5.68e-04 | 0.004 | 0.001 | 8.94e-04 | estimated_rates | 3.08e-04 | estimated_rates | 3.24e-04 | estimated_rates |
| only_step_3 | 400 | 359.64 | 15.887 | 955.155 | 341.902 | 1297.057 | 375.527 | 0.001 | 3.659 | 1.001 | 9 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.002 | 0.001 | 2.78e-04 | 0.002 | 5.56e-04 | 0.004 | 0.001 | 9.05e-04 | estimated_rates | 3.07e-04 | estimated_rates | 3.22e-04 | estimated_rates |
| only_planner | 400 | 301.373 | 64.52 | 1121.89 | 133.938 | 1255.828 | 365.892 | 0.001 | 3.966 | 1.309 | 9 | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct | 0.002 | 0.001 | 3.64e-04 | 0.002 | 7.27e-04 | 0.004 | 0.001 | 7.69e-04 | estimated_rates | 3.34e-04 | estimated_rates | 3.51e-04 | estimated_rates |

5 of 64 rows shown.

### placement_costs.csv

| run | plan | placement | gpu_seconds_per_problem | gpu_usd_throughput | source | repeats |
|---|---|---|---|---|---|---|
| cal_granite_hotpot_separate | all_large | separate | 0.851 | 4.73e-04 | measured | 3 |
| cal_granite_hotpot_separate | all_small | separate | 0.434 | 2.41e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_large | shared | 0.408 | 2.27e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_small | shared | 0.208 | 1.16e-04 | measured | 3 |
| cal_granite_math_separate | all_large | separate | 0.774 | 4.30e-04 | measured | 3 |
| cal_granite_math_separate | all_small | separate | 0.333 | 1.85e-04 | measured | 3 |
| cal_granite_math_shared | all_large | shared | 0.367 | 2.04e-04 | measured | 3 |
| cal_granite_math_shared | all_small | shared | 0.187 | 1.04e-04 | measured | 3 |
| cal_phi_math_separate | all_large | separate | 1.486 | 8.26e-04 | measured | 3 |
| cal_phi_math_separate | all_small | separate | 0.536 | 2.98e-04 | measured | 3 |
| cal_phi_math_shared | all_large | shared | 0.745 | 4.14e-04 | measured | 3 |
| cal_phi_math_shared | all_small | shared | 0.266 | 1.48e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_large | separate | 1.219 | 6.77e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_small | separate | 0.282 | 1.57e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_large | shared | 0.599 | 3.33e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_small | shared | 0.147 | 8.17e-05 | measured | 3 |
| cal_qwen_hotpot_separate | all_large | separate | 0.251 | 1.39e-04 | measured | 3 |
| cal_qwen_hotpot_separate | all_small | separate | 0.106 | 5.87e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_large | shared | 0.124 | 6.91e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_small | shared | 0.054 | 2.98e-05 | measured | 3 |
| separate | aggregator+verifier | separate | 0.422 | 2.35e-04 | measured | 3 |
| separate | all_large | separate | 0.504 | 2.80e-04 | measured | 3 |
| separate | all_small | separate | 0.21 | 1.17e-04 | measured | 3 |
| separate | only_aggregator | separate | 0.248 | 1.38e-04 | measured | 3 |
| separate | only_planner | separate | 0.227 | 1.26e-04 | measured | 3 |
| separate | only_verifier | separate | 0.367 | 2.04e-04 | measured | 3 |
| separate | planner+verifier | separate | 0.383 | 2.13e-04 | measured | 3 |
| separate_k1 | aggregator+verifier | separate | 4.857 | 0.003 | measured | 3 |
| separate_k1 | all_large | separate | 5.576 | 0.003 | measured | 3 |
| separate_k1 | all_small | separate | 2.367 | 0.001 | measured | 3 |

30 of 83 rows shown.

### cost_summary

```json
{
  "n_plans": 64,
  "api_large_small_ratio": 17.31566737327477,
  "a3_kendall_tau_latency_vs_units": 0.287452614851115,
  "p5_runs": [
    "cal_granite_hotpot_separate",
    "cal_granite_hotpot_shared",
    "cal_granite_math_separate",
    "cal_granite_math_shared",
    "cal_phi_math_separate",
    "cal_phi_math_shared",
    "cal_qwen3_14_math_separate",
    "cal_qwen3_14_math_shared",
    "cal_qwen_hotpot_separate",
    "cal_qwen_hotpot_shared",
    "separate",
    "separate_k1",
    "separate_k32",
    "shared",
    "shared_k1",
    "shared_k32",
    "shared_mps",
    "shared_mps_k1",
    "shared_mps_k32"
  ],
  "gpu_cost_basis": {
    "separate": {
      "estimated_rates": 64
    },
    "shared": {
      "estimated_rates": 64
    },
    "shared_mps": {
      "estimated_rates": 64
    }
  },
  "a3_kendall_tau_separate": 0.3433772480906316,
  "a3_basis_separate": "estimated_rates",
  "a3_kendall_tau_shared": 0.34449574075542194,
  "a3_basis_shared": "estimated_rates",
  "a3_kendall_tau_shared_mps": 0.31094096081171196,
  "a3_basis_shared_mps": "estimated_rates"
}
```

## math_q15_7/pareto

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+step_1+step_3+aggregator+verifier | separate | 0.83 | 0.002 | 5.317 | estimated_rates |
| planner+step_1+step_3+aggregator+verifier | shared | 0.83 | 5.26e-04 | 8.882 | estimated_rates |
| planner+step_1+step_3+aggregator+verifier | shared_mps | 0.83 | 5.32e-04 | 6.847 | estimated_rates |
| step_2+verifier | separate | 0.823 | 9.15e-04 | 3.59 | estimated_rates |
| step_2+verifier | shared | 0.823 | 4.78e-04 | 8.834 | estimated_rates |
| step_2+verifier | shared_mps | 0.823 | 4.92e-04 | 6.788 | estimated_rates |
| all_large | shared | 0.82 | 5.22e-04 | 5.275 | estimated_rates |
| planner+step_1+step_2+step_3+verifier | shared | 0.807 | 4.83e-04 | 6.388 | estimated_rates |
| planner+step_1+step_2+step_3+verifier | shared_mps | 0.807 | 4.87e-04 | 5.378 | estimated_rates |
| step_2+step_3+verifier | shared | 0.805 | 4.65e-04 | 9.207 | estimated_rates |

10 of 63 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 3.34 | step_3+aggregator | 0.65 |
| shared | 3.34 | all_small | 0.49 |
| shared_mps | 3.34 | all_small | 0.49 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_aggregator | 0.625 | gpu_usd_throughput_separate | step_2+verifier | 0.823 | True | estimated_rates |
| 0.5 | only_verifier | 0.79 | gpu_usd_throughput_separate | step_2+verifier | 0.823 | True | estimated_rates |
| 0.75 | step_2+verifier | 0.823 | gpu_usd_throughput_separate | step_2+verifier | 0.823 | False | estimated_rates |

### latency_check.csv

| plan | placement | k | repeat | predicted_p95 | measured_p95 | rel_error |
|---|---|---|---|---|---|---|
| all_small | separate | 16 | 0 | 2.227 | 2.564 | -0.131 |
| all_small | separate | 16 | 1 | 2.227 | 2.39 | -0.068 |
| all_small | separate | 16 | 2 | 2.227 | 2.367 | -0.059 |
| only_planner | separate | 16 | 0 | 2.517 | 2.549 | -0.013 |
| only_planner | separate | 16 | 1 | 2.517 | 2.291 | 0.099 |
| only_planner | separate | 16 | 2 | 2.517 | 2.493 | 0.009 |
| only_aggregator | separate | 16 | 0 | 3.23 | 3.076 | 0.05 |
| only_aggregator | separate | 16 | 1 | 3.23 | 3.292 | -0.019 |
| only_aggregator | separate | 16 | 2 | 3.23 | 3.062 | 0.055 |
| only_verifier | separate | 16 | 0 | 3.504 | 3.518 | -0.004 |
| only_verifier | separate | 16 | 1 | 3.504 | 3.506 | -5.65e-04 |
| only_verifier | separate | 16 | 2 | 3.504 | 3.457 | 0.014 |
| planner+verifier | separate | 16 | 0 | 3.849 | 3.623 | 0.063 |
| planner+verifier | separate | 16 | 1 | 3.849 | 3.578 | 0.076 |
| planner+verifier | separate | 16 | 2 | 3.849 | 3.62 | 0.063 |
| aggregator+verifier | separate | 16 | 0 | 4.457 | 5.249 | -0.151 |
| aggregator+verifier | separate | 16 | 1 | 4.457 | 4.559 | -0.022 |
| aggregator+verifier | separate | 16 | 2 | 4.457 | 4.461 | -0.001 |
| all_large | separate | 16 | 0 | 5.275 | 5.188 | 0.017 |
| all_large | separate | 16 | 1 | 5.275 | 5.005 | 0.054 |
| all_large | separate | 16 | 2 | 5.275 | 5.104 | 0.034 |
| all_small | shared | 16 | 0 | 2.227 | 2.751 | -0.191 |
| all_small | shared | 16 | 1 | 2.227 | 2.253 | -0.011 |
| all_small | shared | 16 | 2 | 2.227 | 2.55 | -0.127 |
| only_planner | shared | 16 | 0 | 7.572 | 6.57 | 0.152 |
| only_planner | shared | 16 | 1 | 7.572 | 6.579 | 0.151 |
| only_planner | shared | 16 | 2 | 7.572 | 6.105 | 0.24 |
| only_aggregator | shared | 16 | 0 | 8.674 | 7.381 | 0.175 |
| only_aggregator | shared | 16 | 1 | 8.674 | 7.401 | 0.172 |
| only_aggregator | shared | 16 | 2 | 8.674 | 7.267 | 0.194 |

30 of 63 rows shown.

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 192
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 192,
  "n_front": 63,
  "hypervolume_joint": 0.4952814112512839,
  "hypervolume_two_step": 0.2994081895374691,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.16000000000000003,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 3.3404956934955408,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "h3c_share_within_10pct": 0.49206349206349204
}
```

## math_q15_7/pareto_api

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+step_1+step_3+aggregator+verifier | separate | 0.83 | 0.005 | 5.317 | api |
| step_2+verifier | separate | 0.823 | 0.003 | 3.59 | api |
| only_verifier | separate | 0.79 | 0.002 | 3.504 | api |
| step_2+aggregator | separate | 0.65 | 0.002 | 3.413 | api |
| step_3+aggregator | separate | 0.65 | 0.002 | 3.253 | api |
| planner+aggregator | separate | 0.627 | 0.002 | 3.382 | api |
| only_aggregator | separate | 0.625 | 0.001 | 3.23 | api |
| planner+step_2+step_3 | separate | 0.53 | 0.003 | 2.601 | api |
| planner+step_3 | separate | 0.525 | 0.002 | 2.681 | api |
| only_planner | separate | 0.51 | 0.001 | 2.517 | api |

10 of 15 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 3.34 | step_3+aggregator | 0.65 |
| shared | 3.34 | all_small | 0.49 |
| shared_mps | 3.34 | all_small | 0.49 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_aggregator | 0.625 | gpu_usd_throughput_separate | step_2+verifier | 0.823 | True | estimated_rates |
| 0.5 | only_verifier | 0.79 | gpu_usd_throughput_separate | step_2+verifier | 0.823 | True | estimated_rates |
| 0.75 | step_2+verifier | 0.823 | gpu_usd_throughput_separate | step_2+verifier | 0.823 | False | estimated_rates |

### latency_check.csv

| plan | placement | k | repeat | predicted_p95 | measured_p95 | rel_error |
|---|---|---|---|---|---|---|
| all_small | separate | 16 | 0 | 2.227 | 2.564 | -0.131 |
| all_small | separate | 16 | 1 | 2.227 | 2.39 | -0.068 |
| all_small | separate | 16 | 2 | 2.227 | 2.367 | -0.059 |
| only_planner | separate | 16 | 0 | 2.517 | 2.549 | -0.013 |
| only_planner | separate | 16 | 1 | 2.517 | 2.291 | 0.099 |
| only_planner | separate | 16 | 2 | 2.517 | 2.493 | 0.009 |
| only_aggregator | separate | 16 | 0 | 3.23 | 3.076 | 0.05 |
| only_aggregator | separate | 16 | 1 | 3.23 | 3.292 | -0.019 |
| only_aggregator | separate | 16 | 2 | 3.23 | 3.062 | 0.055 |
| only_verifier | separate | 16 | 0 | 3.504 | 3.518 | -0.004 |
| only_verifier | separate | 16 | 1 | 3.504 | 3.506 | -5.65e-04 |
| only_verifier | separate | 16 | 2 | 3.504 | 3.457 | 0.014 |
| planner+verifier | separate | 16 | 0 | 3.849 | 3.623 | 0.063 |
| planner+verifier | separate | 16 | 1 | 3.849 | 3.578 | 0.076 |
| planner+verifier | separate | 16 | 2 | 3.849 | 3.62 | 0.063 |
| aggregator+verifier | separate | 16 | 0 | 4.457 | 5.249 | -0.151 |
| aggregator+verifier | separate | 16 | 1 | 4.457 | 4.559 | -0.022 |
| aggregator+verifier | separate | 16 | 2 | 4.457 | 4.461 | -0.001 |
| all_large | separate | 16 | 0 | 5.275 | 5.188 | 0.017 |
| all_large | separate | 16 | 1 | 5.275 | 5.005 | 0.054 |
| all_large | separate | 16 | 2 | 5.275 | 5.104 | 0.034 |
| all_small | shared | 16 | 0 | 2.227 | 2.751 | -0.191 |
| all_small | shared | 16 | 1 | 2.227 | 2.253 | -0.011 |
| all_small | shared | 16 | 2 | 2.227 | 2.55 | -0.127 |
| only_planner | shared | 16 | 0 | 7.572 | 6.57 | 0.152 |
| only_planner | shared | 16 | 1 | 7.572 | 6.579 | 0.151 |
| only_planner | shared | 16 | 2 | 7.572 | 6.105 | 0.24 |
| only_aggregator | shared | 16 | 0 | 8.674 | 7.381 | 0.175 |
| only_aggregator | shared | 16 | 1 | 8.674 | 7.401 | 0.172 |
| only_aggregator | shared | 16 | 2 | 8.674 | 7.267 | 0.194 |

30 of 63 rows shown.

### pareto_summary

```json
{
  "cost_metric": "api_usd",
  "cost_metric_requested": "api_usd",
  "cost_basis_counts": {
    "api": 192
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 192,
  "n_front": 15,
  "hypervolume_joint": 0.524512025314245,
  "hypervolume_two_step": 0.49968683186991736,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.16000000000000003,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 3.3404956934955408,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "h3c_share_within_10pct": 0.49206349206349204
}
```

## math_q15_7/pareto_estimated

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| step_2+aggregator+verifier | separate | 0.81 | 0.001 | 4.778 | estimated_rates |
| step_2+aggregator+verifier | shared | 0.81 | 5.18e-04 | 10.537 | estimated_rates |
| step_2+aggregator+verifier | shared_mps | 0.81 | 5.30e-04 | 7.793 | estimated_rates |
| step_2+step_3+aggregator+verifier | shared | 0.802 | 5.16e-04 | 10.881 | estimated_rates |
| step_2+step_3+aggregator+verifier | shared_mps | 0.802 | 5.25e-04 | 7.89 | estimated_rates |
| step_2+verifier | separate | 0.8 | 9.15e-04 | 3.59 | estimated_rates |
| step_2+verifier | shared | 0.8 | 4.78e-04 | 8.834 | estimated_rates |
| step_2+verifier | shared_mps | 0.8 | 4.92e-04 | 6.788 | estimated_rates |
| planner+step_2+verifier | shared_mps | 0.795 | 5.16e-04 | 6.738 | estimated_rates |
| step_2+step_3+verifier | shared | 0.792 | 4.65e-04 | 9.207 | estimated_rates |

10 of 69 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 3.34 | only_aggregator | 0.625 |
| shared | 3.34 | all_small | 0.49 |
| shared_mps | 3.34 | all_small | 0.49 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_aggregator | 0.625 | gpu_usd_throughput_separate | step_2+aggregator+verifier | 0.81 | True | estimated_rates |
| 0.5 | only_verifier | 0.79 | gpu_usd_throughput_separate | step_2+aggregator+verifier | 0.81 | True | estimated_rates |
| 0.75 | step_2+aggregator+verifier | 0.81 | gpu_usd_throughput_separate | step_2+aggregator+verifier | 0.81 | False | estimated_rates |

### latency_check.csv

| plan | placement | k | repeat | predicted_p95 | measured_p95 | rel_error |
|---|---|---|---|---|---|---|
| all_small | separate | 16 | 0 | 2.227 | 2.564 | -0.131 |
| all_small | separate | 16 | 1 | 2.227 | 2.39 | -0.068 |
| all_small | separate | 16 | 2 | 2.227 | 2.367 | -0.059 |
| only_planner | separate | 16 | 0 | 2.517 | 2.549 | -0.013 |
| only_planner | separate | 16 | 1 | 2.517 | 2.291 | 0.099 |
| only_planner | separate | 16 | 2 | 2.517 | 2.493 | 0.009 |
| only_aggregator | separate | 16 | 0 | 3.23 | 3.076 | 0.05 |
| only_aggregator | separate | 16 | 1 | 3.23 | 3.292 | -0.019 |
| only_aggregator | separate | 16 | 2 | 3.23 | 3.062 | 0.055 |
| only_verifier | separate | 16 | 0 | 3.504 | 3.518 | -0.004 |
| only_verifier | separate | 16 | 1 | 3.504 | 3.506 | -5.65e-04 |
| only_verifier | separate | 16 | 2 | 3.504 | 3.457 | 0.014 |
| planner+verifier | separate | 16 | 0 | 3.849 | 3.623 | 0.063 |
| planner+verifier | separate | 16 | 1 | 3.849 | 3.578 | 0.076 |
| planner+verifier | separate | 16 | 2 | 3.849 | 3.62 | 0.063 |
| aggregator+verifier | separate | 16 | 0 | 4.457 | 5.249 | -0.151 |
| aggregator+verifier | separate | 16 | 1 | 4.457 | 4.559 | -0.022 |
| aggregator+verifier | separate | 16 | 2 | 4.457 | 4.461 | -0.001 |
| all_large | separate | 16 | 0 | 5.275 | 5.188 | 0.017 |
| all_large | separate | 16 | 1 | 5.275 | 5.005 | 0.054 |
| all_large | separate | 16 | 2 | 5.275 | 5.104 | 0.034 |
| all_small | shared | 16 | 0 | 2.227 | 2.751 | -0.191 |
| all_small | shared | 16 | 1 | 2.227 | 2.253 | -0.011 |
| all_small | shared | 16 | 2 | 2.227 | 2.55 | -0.127 |
| only_planner | shared | 16 | 0 | 7.572 | 6.57 | 0.152 |
| only_planner | shared | 16 | 1 | 7.572 | 6.579 | 0.151 |
| only_planner | shared | 16 | 2 | 7.572 | 6.105 | 0.24 |
| only_aggregator | shared | 16 | 0 | 8.674 | 7.381 | 0.175 |
| only_aggregator | shared | 16 | 1 | 8.674 | 7.401 | 0.172 |
| only_aggregator | shared | 16 | 2 | 8.674 | 7.267 | 0.194 |

30 of 63 rows shown.

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 192
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 192,
  "n_front": 69,
  "hypervolume_joint": 0.4832644876394482,
  "hypervolume_two_step": 0.2943998148528293,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.135,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 3.3404956934955408,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "regret_hypervolume": 0.002650801188409213,
  "regret_accuracy_mean": 0.003928571428571428,
  "h3c_share_within_10pct": 0.49206349206349204
}
```

## math_q15_7/routing

### routing.csv

| agent | rule | threshold | routed_share | accuracy | cost | baseline_accuracy | fixed_accuracy | fixed_cost | h6_match | primary |
|---|---|---|---|---|---|---|---|---|---|---|
| verifier | samples_disagree |  | 0.805 | 0.8 | 0.002 | 0.505 | 0.825 | 0.002 | False | True |
| verifier | entropy | 0 | 0.805 | 0.8 | 0.002 | 0.505 | 0.825 | 0.002 | False | False |
| verifier | entropy | 0.5 | 0.805 | 0.8 | 0.002 | 0.505 | 0.825 | 0.002 | False | False |
| verifier | baseline_vs_majority |  | 0.41 | 0.71 | 0.002 | 0.505 | 0.825 | 0.002 | False | False |
| verifier | entropy | 1 | 0.48 | 0.705 | 0.002 | 0.505 | 0.825 | 0.002 | False | False |
| planner | baseline_vs_majority |  | 0.45 | 0.625 | 0.002 | 0.505 | 0.595 | 0.001 | False | False |
| aggregator | samples_disagree |  | 0.28 | 0.59 | 7.62e-04 | 0.505 | 0.62 | 0.001 | False | False |
| aggregator | entropy | 0 | 0.28 | 0.59 | 7.62e-04 | 0.505 | 0.62 | 0.001 | False | False |

8 of 30 rows shown.

### routing_summary

```json
{
  "a4_agent": "verifier",
  "a4_rule": "samples_disagree (K small samples not unanimous)",
  "a4_k_samples": 5,
  "a4_h6_match": false,
  "a4_row": {
    "agent": "verifier",
    "rule": "samples_disagree",
    "threshold": "",
    "routed_share": 0.805,
    "accuracy": 0.8,
    "cost": 0.002449804,
    "baseline_accuracy": 0.505,
    "fixed_accuracy": 0.825,
    "fixed_cost": 0.002363399,
    "h6_match": false,
    "primary": true
  },
  "note": "all other rows in routing.csv are exploratory"
}
```

## math_q15_7/rules

### rule_plans.csv

| rule | budget | upgraded | accuracy | best_accuracy_at_budget | regret | is_best |
|---|---|---|---|---|---|---|
| structural_topk | 1 | planner | 0.51 | 0.79 | 0.28 | False |
| structural_topk | 2 | planner,step_1 | 0.448 | 0.823 | 0.375 | False |
| structural_topk | 3 | planner,step_1,step_2 | 0.48 | 0.823 | 0.343 | False |
| structural_topk | 4 | planner,step_1,step_2,step_3 | 0.52 | 0.823 | 0.302 | False |
| structural_topk | 5 | aggregator,planner,step_1,step_2,step_3 | 0.657 | 0.83 | 0.172 | False |
| structural_topk | 6 | all | 0.82 | 0.83 | 0.01 | False |
| output_topk | 1 | verifier | 0.79 | 0.79 | 0 | True |
| output_topk | 2 | aggregator,verifier | 0.8 | 0.823 | 0.022 | False |
| output_topk | 3 | aggregator,step_3,verifier | 0.802 | 0.823 | 0.02 | False |
| output_topk | 4 | aggregator,step_2,step_3,verifier | 0.8 | 0.823 | 0.022 | False |
| output_topk | 5 | aggregator,step_1,step_2,step_3,verifier | 0.805 | 0.83 | 0.025 | False |
| output_topk | 6 | all | 0.82 | 0.83 | 0.01 | False |
| ec_topk | 1 | verifier | 0.79 | 0.79 | 0 | True |
| ec_topk | 2 | planner,verifier | 0.785 | 0.823 | 0.037 | False |
| ec_topk | 3 | planner,step_3,verifier | 0.787 | 0.823 | 0.035 | False |
| ec_topk | 4 | aggregator,planner,step_3,verifier | 0.807 | 0.823 | 0.015 | False |

16 of 48 rows shown.

### estimator_errors.csv

| estimator | m | n_plans | n_held_out | mae_all | mae_held_out | feasibility_wrong_p25 | feasibility_wrong_p50 | feasibility_wrong_p75 |
|---|---|---|---|---|---|---|---|---|
| independence_additive | 3 | 64 | 54 | 0.041 | 0.046 | 0 | 0 | 0.13 |
| independence_multiplicative | 3 | 64 | 54 | 0.059 | 0.065 | 0 | 0 | 0.13 |
| pairwise_corrected | 3 | 64 | 54 | 0.021 | 0.024 | 0 | 0 | 0.278 |
| logit_additive | 3 | 64 | 54 | 0.026 | 0.029 | 0 | 0 | 0.13 |

### rules_summary

```json
{
  "accuracy_thresholds": {
    "p25": 0.5599999999999999,
    "p50": 0.7124999999999999,
    "p75": 0.8
  },
  "h1c": {
    "reruns_used": 507,
    "reruns_full": 1000,
    "share": 0.507,
    "top2_full": [
      "aggregator",
      "verifier"
    ],
    "top2_disagree_only": [
      "aggregator",
      "verifier"
    ],
    "top2_same": true,
    "a1_uv_abs_diff": {
      "planner": 0.0,
      "step_1": 0.015,
      "step_2": 0.02,
      "step_3": 0.010000000000000002,
      "aggregator": 0.010000000000000009,
      "verifier": 0.0
    },
    "a1_max_uv_abs_diff": 0.02,
    "a1_share_le_half": false,
    "a1_confident_uv_full": {
      "1": [
        "verifier"
      ],
      "2": [
        "aggregator",
        "verifier"
      ]
    },
    "a1_confident_uv_disagree_only": {
      "1": [
        "verifier"
      ],
      "2": [
        "aggregator",
        "verifier"
      ]
    },
    "a1_confident_uv_same": true,
    "a1_holds_without_share": true,
    "e3_skip_variants": {
      "reruns_full": 1000,
      "key": {
        "reruns_used": 507,
        "share": 0.507,
        "uv_abs_error": {
          "planner": 0.0,
          "step_1": 0.015,
          "step_2": 0.02,
          "step_3": 0.010000000000000002,
          "aggregator": 0.010000000000000009,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.02
      },
      "exact": {
        "reruns_used": 848,
        "share": 0.848,
        "uv_abs_error": {
          "planner": 0.0,
          "step_1": 0.0,
          "step_2": 0.0,
          "step_3": 0.0,
          "aggregator": 0.0,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.0
      }
    }
  }
}
```

## math_q3_14/cost

### plan_costs.csv

| plan | n_problems | tokens_out_small | tokens_out_large | tokens_in_small | tokens_in_large | tokens_in | tokens_out | api_usd | gpu_seconds | gpu_seconds_shared | cost_units | model_small | model_large | gpu_usd_latency | gpu_usd_latency_1 | gpu_usd_latency_shared_1 | gpu_usd_latency_2 | gpu_usd_latency_shared_2 | gpu_usd_latency_4 | gpu_usd_latency_shared_4 | gpu_usd_throughput_separate | gpu_cost_basis_separate | gpu_usd_throughput_shared | gpu_cost_basis_shared | gpu_usd_throughput_shared_mps | gpu_cost_basis_shared_mps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_small | 400 | 369.265 | 0 | 1162.16 | 0 | 1162.16 | 369.265 | 3.01e-04 | 5.198 | 1.299 | 6 | Qwen/Qwen2.5-3B-Instruct |  | 0.003 | 0.001 | 3.61e-04 | 0.003 | 7.22e-04 | 0.006 | 0.001 | 1.58e-04 | estimated_rates | 8.25e-05 | estimated_rates | 7.22e-04 | fallback_latency |
| only_aggregator | 400 | 351.908 | 29.08 | 1047.79 | 132.235 | 1180.025 | 380.988 | 8.36e-04 | 5.905 | 1.761 | 9 | Qwen/Qwen2.5-3B-Instruct | Qwen/Qwen2.5-14B-Instruct | 0.003 | 0.002 | 4.89e-04 | 0.003 | 9.78e-04 | 0.007 | 0.002 | 1.50e-04 | estimated_rates | 9.97e-05 | estimated_rates | 9.78e-04 | fallback_latency |
| only_planner | 400 | 298.265 | 76.435 | 1034.73 | 133.938 | 1168.668 | 374.7 | 0.001 | 6.711 | 2.398 | 9 | Qwen/Qwen2.5-3B-Instruct | Qwen/Qwen2.5-14B-Instruct | 0.004 | 0.002 | 6.66e-04 | 0.004 | 0.001 | 0.007 | 0.003 | 1.28e-04 | estimated_rates | 1.22e-04 | estimated_rates | 0.001 | fallback_latency |
| only_step_1 | 400 | 350.895 | 67.425 | 1043.78 | 200.805 | 1244.585 | 418.32 | 0.001 | 7.103 | 2.413 | 9 | Qwen/Qwen2.5-3B-Instruct | Qwen/Qwen2.5-14B-Instruct | 0.004 | 0.002 | 6.70e-04 | 0.004 | 0.001 | 0.008 | 0.003 | 1.50e-04 | estimated_rates | 1.27e-04 | estimated_rates | 0.001 | fallback_latency |
| only_step_2 | 400 | 330.775 | 66.218 | 956.378 | 234.94 | 1191.318 | 396.993 | 0.001 | 6.759 | 2.317 | 9 | Qwen/Qwen2.5-3B-Instruct | Qwen/Qwen2.5-14B-Instruct | 0.004 | 0.002 | 6.44e-04 | 0.004 | 0.001 | 0.008 | 0.003 | 1.41e-04 | estimated_rates | 1.22e-04 | estimated_rates | 0.001 | fallback_latency |

5 of 64 rows shown.

### placement_costs.csv

| run | plan | placement | gpu_seconds_per_problem | gpu_usd_throughput | source | repeats |
|---|---|---|---|---|---|---|
| cal_granite_hotpot_separate | all_large | separate | 0.851 | 4.73e-04 | measured | 3 |
| cal_granite_hotpot_separate | all_small | separate | 0.434 | 2.41e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_large | shared | 0.408 | 2.27e-04 | measured | 3 |
| cal_granite_hotpot_shared | all_small | shared | 0.208 | 1.16e-04 | measured | 3 |
| cal_granite_math_separate | all_large | separate | 0.774 | 4.30e-04 | measured | 3 |
| cal_granite_math_separate | all_small | separate | 0.333 | 1.85e-04 | measured | 3 |
| cal_granite_math_shared | all_large | shared | 0.367 | 2.04e-04 | measured | 3 |
| cal_granite_math_shared | all_small | shared | 0.187 | 1.04e-04 | measured | 3 |
| cal_phi_math_separate | all_large | separate | 1.486 | 8.26e-04 | measured | 3 |
| cal_phi_math_separate | all_small | separate | 0.536 | 2.98e-04 | measured | 3 |
| cal_phi_math_shared | all_large | shared | 0.745 | 4.14e-04 | measured | 3 |
| cal_phi_math_shared | all_small | shared | 0.266 | 1.48e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_large | separate | 1.219 | 6.77e-04 | measured | 3 |
| cal_qwen3_14_math_separate | all_small | separate | 0.282 | 1.57e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_large | shared | 0.599 | 3.33e-04 | measured | 3 |
| cal_qwen3_14_math_shared | all_small | shared | 0.147 | 8.17e-05 | measured | 3 |
| cal_qwen_hotpot_separate | all_large | separate | 0.251 | 1.39e-04 | measured | 3 |
| cal_qwen_hotpot_separate | all_small | separate | 0.106 | 5.87e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_large | shared | 0.124 | 6.91e-05 | measured | 3 |
| cal_qwen_hotpot_shared | all_small | shared | 0.054 | 2.98e-05 | measured | 3 |
| separate | aggregator+verifier | separate | 0.422 | 2.35e-04 | measured | 3 |
| separate | all_large | separate | 0.504 | 2.80e-04 | measured | 3 |
| separate | all_small | separate | 0.21 | 1.17e-04 | measured | 3 |
| separate | only_aggregator | separate | 0.248 | 1.38e-04 | measured | 3 |
| separate | only_planner | separate | 0.227 | 1.26e-04 | measured | 3 |
| separate | only_verifier | separate | 0.367 | 2.04e-04 | measured | 3 |
| separate | planner+verifier | separate | 0.383 | 2.13e-04 | measured | 3 |
| separate_k1 | aggregator+verifier | separate | 4.857 | 0.003 | measured | 3 |
| separate_k1 | all_large | separate | 5.576 | 0.003 | measured | 3 |
| separate_k1 | all_small | separate | 2.367 | 0.001 | measured | 3 |

30 of 83 rows shown.

### cost_summary

```json
{
  "n_plans": 64,
  "api_large_small_ratio": 23.634885997437273,
  "a3_kendall_tau_latency_vs_units": 0.8254475866152642,
  "p5_runs": [
    "cal_granite_hotpot_separate",
    "cal_granite_hotpot_shared",
    "cal_granite_math_separate",
    "cal_granite_math_shared",
    "cal_phi_math_separate",
    "cal_phi_math_shared",
    "cal_qwen3_14_math_separate",
    "cal_qwen3_14_math_shared",
    "cal_qwen_hotpot_separate",
    "cal_qwen_hotpot_shared",
    "separate",
    "separate_k1",
    "separate_k32",
    "shared",
    "shared_k1",
    "shared_k32",
    "shared_mps",
    "shared_mps_k1",
    "shared_mps_k32"
  ],
  "gpu_cost_basis": {
    "separate": {
      "estimated_rates": 64
    },
    "shared": {
      "estimated_rates": 64
    },
    "shared_mps": {
      "fallback_latency": 64
    }
  },
  "a3_kendall_tau_separate": 0.7113613348066504,
  "a3_basis_separate": "estimated_rates",
  "a3_kendall_tau_shared": 0.7941297920011349,
  "a3_basis_shared": "estimated_rates",
  "a3_kendall_tau_shared_mps": 0.77735240202928,
  "a3_basis_shared_mps": "fallback"
}
```

## math_q3_14/pareto

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| step_1+step_2+step_3+aggregator+verifier | separate | 0.892 | 5.46e-04 | 18.71 | estimated_rates |
| step_1+step_2+step_3+aggregator+verifier | shared | 0.892 | 2.85e-04 | 34.621 | estimated_rates |
| step_1+aggregator+verifier | separate | 0.89 | 3.62e-04 | 13.653 | estimated_rates |
| step_1+aggregator+verifier | shared | 0.89 | 2.10e-04 | 30.398 | estimated_rates |
| step_3+aggregator+verifier | separate | 0.89 | 3.51e-04 | 14.097 | estimated_rates |
| step_3+aggregator+verifier | shared | 0.89 | 2.05e-04 | 32.001 | estimated_rates |
| planner+step_1+step_2+aggregator+verifier | shared | 0.887 | 2.84e-04 | 21.065 | estimated_rates |
| all_large | shared | 0.882 | 3.23e-04 | 19.905 | estimated_rates |
| planner+step_2+step_3+verifier | shared | 0.88 | 2.63e-04 | 28.743 | estimated_rates |
| planner+verifier | separate | 0.877 | 3.48e-04 | 12.503 | estimated_rates |

10 of 30 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 10.978 | only_verifier | 0.868 |
| shared | 10.978 | all_small | 0.675 |
| shared_mps | 10.978 | all_small | 0.675 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | step_2+aggregator | 0.72 | gpu_usd_throughput_separate | only_verifier | 0.868 | True | estimated_rates |
| 0.5 | planner+verifier | 0.877 | gpu_usd_throughput_separate | step_3+aggregator+verifier | 0.89 | True | estimated_rates |
| 0.75 | step_1+aggregator+verifier | 0.89 | gpu_usd_throughput_separate | step_3+aggregator+verifier | 0.89 | True | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 128,
    "fallback_latency": 64
  },
  "any_fallback": true,
  "k": 16,
  "n_candidates": 192,
  "n_front": 30,
  "hypervolume_joint": 0.6811853611868364,
  "hypervolume_two_step": 0.669299297133295,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.21499999999999997,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 10.977917099999331,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## math_q3_14/pareto_api

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| step_1+step_2+step_3+aggregator+verifier | separate | 0.892 | 0.006 | 18.71 | api |
| step_1+aggregator+verifier | separate | 0.89 | 0.004 | 13.653 | api |
| planner+verifier | separate | 0.877 | 0.003 | 12.503 | api |
| only_verifier | separate | 0.868 | 0.002 | 10.976 | api |
| step_1+aggregator | separate | 0.72 | 0.002 | 9.935 | api |
| step_2+aggregator | separate | 0.72 | 0.002 | 10.005 | api |
| planner+aggregator | separate | 0.718 | 0.002 | 9.797 | api |
| only_step_1 | separate | 0.703 | 0.001 | 9.205 | api |
| only_aggregator | separate | 0.7 | 8.36e-04 | 8.132 | api |
| all_small | separate | 0.675 | 3.01e-04 | 7.319 | api |

10 of 12 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 10.978 | only_verifier | 0.868 |
| shared | 10.978 | all_small | 0.675 |
| shared_mps | 10.978 | all_small | 0.675 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | step_2+aggregator | 0.72 | gpu_usd_throughput_separate | only_verifier | 0.868 | True | estimated_rates |
| 0.5 | planner+verifier | 0.877 | gpu_usd_throughput_separate | step_3+aggregator+verifier | 0.89 | True | estimated_rates |
| 0.75 | step_1+aggregator+verifier | 0.89 | gpu_usd_throughput_separate | step_3+aggregator+verifier | 0.89 | True | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "api_usd",
  "cost_metric_requested": "api_usd",
  "cost_basis_counts": {
    "api": 192
  },
  "any_fallback": false,
  "k": 16,
  "n_candidates": 192,
  "n_front": 12,
  "hypervolume_joint": 0.6260121567273579,
  "hypervolume_two_step": 0.6195510723810096,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.04249999999999998,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 10.977917099999331,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## math_q3_14/pareto_estimated

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| planner+step_1+step_2+step_3+verifier | separate | 0.905 | 6.33e-04 | 19.31 | estimated_rates |
| planner+step_1+step_2+step_3+verifier | shared | 0.905 | 3.13e-04 | 19.915 | estimated_rates |
| planner+step_2+step_3+verifier | separate | 0.897 | 5.18e-04 | 17.471 | estimated_rates |
| planner+step_2+step_3+verifier | shared | 0.897 | 2.63e-04 | 28.743 | estimated_rates |
| planner+step_1+step_3+verifier | separate | 0.895 | 5.44e-04 | 17.124 | estimated_rates |
| planner+step_1+step_2+verifier | separate | 0.892 | 5.35e-04 | 16.66 | estimated_rates |
| planner+step_1+step_2+verifier | shared | 0.892 | 2.75e-04 | 23.215 | estimated_rates |
| step_2+step_3+verifier | separate | 0.89 | 4.15e-04 | 16.111 | estimated_rates |
| step_2+step_3+verifier | shared | 0.89 | 2.30e-04 | 34.311 | estimated_rates |
| planner+step_3+verifier | separate | 0.887 | 4.37e-04 | 15.256 | estimated_rates |

10 of 43 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 10.978 | only_verifier | 0.868 |
| shared | 10.978 | all_small | 0.675 |
| shared_mps | 10.978 | all_small | 0.675 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | step_1+aggregator | 0.72 | gpu_usd_throughput_separate | only_verifier | 0.868 | True | estimated_rates |
| 0.5 | step_3+verifier | 0.88 | gpu_usd_throughput_separate | step_3+verifier | 0.88 | False | estimated_rates |
| 0.75 | planner+step_2+step_3+verifier | 0.897 | gpu_usd_throughput_separate | planner+step_2+step_3+verifier | 0.897 | False | estimated_rates |

### pareto_summary

```json
{
  "cost_metric": "gpu_usd_throughput",
  "cost_metric_requested": "gpu_usd_throughput",
  "cost_basis_counts": {
    "estimated_rates": 128,
    "fallback_latency": 64
  },
  "any_fallback": true,
  "k": 16,
  "n_candidates": 192,
  "n_front": 43,
  "hypervolume_joint": 0.6867292076806139,
  "hypervolume_two_step": 0.6742231893189744,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.20999999999999996,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 10.977917099999331,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "regret_hypervolume": 0.0037856462049778994,
  "regret_accuracy_mean": 0.0029166666666666785
}
```

## math_q3_14/routing

### routing.csv

| agent | rule | threshold | routed_share | accuracy | cost | baseline_accuracy | fixed_accuracy | fixed_cost | h6_match | primary |
|---|---|---|---|---|---|---|---|---|---|---|
| verifier | samples_disagree |  | 0.575 | 0.94 | 0.002 | 0.7 | 0.94 | 0.002 | True | True |
| verifier | entropy | 0 | 0.575 | 0.94 | 0.002 | 0.7 | 0.94 | 0.002 | True | False |
| verifier | entropy | 0.5 | 0.575 | 0.94 | 0.002 | 0.7 | 0.94 | 0.002 | True | False |
| verifier | baseline_vs_majority |  | 0.295 | 0.915 | 0.001 | 0.7 | 0.94 | 0.002 | False | False |
| verifier | entropy | 1 | 0.32 | 0.87 | 0.002 | 0.7 | 0.94 | 0.002 | False | False |
| planner | baseline_vs_majority |  | 0.175 | 0.74 | 0.001 | 0.7 | 0.705 | 0.001 | False | False |
| step_2 | samples_disagree |  | 0.53 | 0.73 | 0.001 | 0.7 | 0.74 | 0.001 | True | False |
| step_2 | entropy | 0 | 0.53 | 0.73 | 0.001 | 0.7 | 0.74 | 0.001 | True | False |

8 of 30 rows shown.

### routing_summary

```json
{
  "a4_agent": "verifier",
  "a4_rule": "samples_disagree (K small samples not unanimous)",
  "a4_k_samples": 5,
  "a4_h6_match": true,
  "a4_row": {
    "agent": "verifier",
    "rule": "samples_disagree",
    "threshold": "",
    "routed_share": 0.575,
    "accuracy": 0.94,
    "cost": 0.002008719,
    "baseline_accuracy": 0.7,
    "fixed_accuracy": 0.94,
    "fixed_cost": 0.0020881650000000003,
    "h6_match": true,
    "primary": true
  },
  "note": "all other rows in routing.csv are exploratory"
}
```

## math_q3_14/rules

### rule_plans.csv

| rule | budget | upgraded | accuracy | best_accuracy_at_budget | regret | is_best |
|---|---|---|---|---|---|---|
| structural_topk | 1 | planner | 0.682 | 0.868 | 0.185 | False |
| structural_topk | 2 | planner,step_1 | 0.708 | 0.877 | 0.17 | False |
| structural_topk | 3 | planner,step_1,step_2 | 0.688 | 0.89 | 0.203 | False |
| structural_topk | 4 | planner,step_1,step_2,step_3 | 0.695 | 0.89 | 0.195 | False |
| structural_topk | 5 | aggregator,planner,step_1,step_2,step_3 | 0.74 | 0.892 | 0.152 | False |
| structural_topk | 6 | all | 0.882 | 0.892 | 0.01 | False |
| output_topk | 1 | verifier | 0.868 | 0.868 | 0 | True |
| output_topk | 2 | aggregator,verifier | 0.853 | 0.877 | 0.025 | False |
| output_topk | 3 | aggregator,step_3,verifier | 0.89 | 0.89 | 0 | True |
| output_topk | 4 | aggregator,step_2,step_3,verifier | 0.877 | 0.89 | 0.013 | False |
| output_topk | 5 | aggregator,step_1,step_2,step_3,verifier | 0.892 | 0.892 | 0 | True |
| output_topk | 6 | all | 0.882 | 0.892 | 0.01 | False |
| ec_topk | 1 | verifier | 0.868 | 0.868 | 0 | True |
| ec_topk | 2 | step_2,verifier | 0.858 | 0.877 | 0.02 | False |
| ec_topk | 3 | step_1,step_2,verifier | 0.882 | 0.89 | 0.008 | False |
| ec_topk | 4 | aggregator,step_1,step_2,verifier | 0.887 | 0.89 | 0.003 | False |

16 of 48 rows shown.

### estimator_errors.csv

| estimator | m | n_plans | n_held_out | mae_all | mae_held_out | feasibility_wrong_p25 | feasibility_wrong_p50 | feasibility_wrong_p75 |
|---|---|---|---|---|---|---|---|---|
| independence_additive | 3 | 64 | 54 | 0.025 | 0.029 | 0.111 | 0 | 0.259 |
| independence_multiplicative | 3 | 64 | 54 | 0.032 | 0.036 | 0.111 | 0 | 0.259 |
| pairwise_corrected | 3 | 64 | 54 | 0.014 | 0.016 | 0.111 | 0 | 0.278 |
| logit_additive | 3 | 64 | 54 | 0.014 | 0.016 | 0.111 | 0 | 0.259 |

### rules_summary

```json
{
  "accuracy_thresholds": {
    "p25": 0.70625,
    "p50": 0.7987500000000001,
    "p75": 0.873125
  },
  "h1c": {
    "reruns_used": 505,
    "reruns_full": 1000,
    "share": 0.505,
    "top2_full": [
      "step_2",
      "verifier"
    ],
    "top2_disagree_only": [
      "step_2",
      "verifier"
    ],
    "top2_same": true,
    "a1_uv_abs_diff": {
      "planner": 0.0,
      "step_1": 0.020000000000000004,
      "step_2": 0.015,
      "step_3": 0.015,
      "aggregator": 0.01,
      "verifier": 0.0
    },
    "a1_max_uv_abs_diff": 0.020000000000000004,
    "a1_share_le_half": false,
    "a1_confident_uv_full": {
      "1": [
        "verifier"
      ],
      "2": [
        "planner",
        "verifier"
      ]
    },
    "a1_confident_uv_disagree_only": {
      "1": [
        "verifier"
      ],
      "2": [
        "planner",
        "verifier"
      ]
    },
    "a1_confident_uv_same": true,
    "a1_holds_without_share": false,
    "e3_skip_variants": {
      "reruns_full": 1000,
      "key": {
        "reruns_used": 505,
        "share": 0.505,
        "uv_abs_error": {
          "planner": 0.0,
          "step_1": 0.020000000000000004,
          "step_2": 0.015,
          "step_3": 0.015,
          "aggregator": 0.01,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.020000000000000004
      },
      "exact": {
        "reruns_used": 995,
        "share": 0.995,
        "uv_abs_error": {
          "planner": 0.0,
          "step_1": 0.0,
          "step_2": 0.0,
          "step_3": 0.0,
          "aggregator": 0.0,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.0
      }
    }
  }
}
```


## Hypotheses: values per setting

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
