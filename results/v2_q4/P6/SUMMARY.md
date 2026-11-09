# Phase P6

Generated 2026-11-09 19:57 UTC, backend `ollama`.

Code run: `fd2d6e8b7cae0e8011fe5a587a5d826c25c36a61`; packaged at `fd2d6e8b7cae0e8011fe5a587a5d826c25c36a61`.

**Test run on `ollama`: not a reported result.**

| step | status |
|---|---|
| hotpot_q15_7/adaptive | finished |
| hotpot_q15_7/cost | finished |
| hotpot_q15_7/pareto_api | finished |
| hotpot_q15_7/pareto_estimated | finished |
| hotpot_q15_7/routing | finished |
| hotpot_q15_7/rules | finished |
| hypotheses | finished |
| math_q15_7/adaptive | finished |
| math_q15_7/cost | finished |
| math_q15_7/pareto_api | finished |
| math_q15_7/pareto_estimated | finished |
| math_q15_7/routing | finished |
| math_q15_7/rules | finished |

## hotpot_q15_7/cost

### plan_costs.csv

| plan | n_problems | tokens_out_small | tokens_out_large | tokens_in_small | tokens_in_large | tokens_in | tokens_out | api_usd | gpu_seconds | gpu_seconds_shared | cost_units | model_small | model_large | gpu_usd_latency | gpu_usd_latency_1 | gpu_usd_latency_shared_1 | gpu_usd_latency_2 | gpu_usd_latency_shared_2 | gpu_usd_latency_4 | gpu_usd_latency_shared_4 | gpu_usd_throughput_separate | gpu_cost_basis_separate | gpu_usd_throughput_shared | gpu_cost_basis_shared | gpu_usd_throughput_shared_mps | gpu_cost_basis_shared_mps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_small | 200 | 130.895 | 0 | 7966.535 | 0 | 7966.535 | 130.895 | 8.62e-04 | 19.771 | 4.943 | 5 | qwen2.5:1.5b-instruct |  | 0.011 | 0.005 | 0.001 | 0.011 | 0.003 | 0.022 | 0.005 | 0.011 | fallback_latency | 0.003 | fallback_latency | 0.003 | fallback_latency |
| only_aggregator | 200 | 108.745 | 12.395 | 6309.54 | 1655.105 | 7964.645 | 121.14 | 0.004 | 24.889 | 9.056 | 8 | qwen2.5:1.5b-instruct | qwen2.5:7b-instruct | 0.014 | 0.007 | 0.003 | 0.014 | 0.005 | 0.028 | 0.01 | 0.014 | fallback_latency | 0.005 | fallback_latency | 0.005 | fallback_latency |
| only_planner | 200 | 96.095 | 38.56 | 6444.695 | 1523.155 | 7967.85 | 134.655 | 0.004 | 27.833 | 10.902 | 8 | qwen2.5:1.5b-instruct | qwen2.5:7b-instruct | 0.015 | 0.008 | 0.003 | 0.015 | 0.006 | 0.031 | 0.012 | 0.015 | fallback_latency | 0.006 | fallback_latency | 0.006 | fallback_latency |
| only_hop_2 | 200 | 101.34 | 25.595 | 6371.195 | 1593.02 | 7964.215 | 126.935 | 0.004 | 23.564 | 8.191 | 8 | qwen2.5:1.5b-instruct | qwen2.5:7b-instruct | 0.013 | 0.007 | 0.002 | 0.013 | 0.005 | 0.026 | 0.009 | 0.013 | fallback_latency | 0.005 | fallback_latency | 0.005 | fallback_latency |
| only_hop_1 | 200 | 86.99 | 34.845 | 6403.11 | 1561.005 | 7964.115 | 121.835 | 0.004 | 28.976 | 11.234 | 8 | qwen2.5:1.5b-instruct | qwen2.5:7b-instruct | 0.016 | 0.008 | 0.003 | 0.016 | 0.006 | 0.032 | 0.012 | 0.016 | fallback_latency | 0.006 | fallback_latency | 0.006 | fallback_latency |

5 of 32 rows shown.

### cost_summary

```json
{
  "n_plans": 32,
  "api_large_small_ratio": 20.079329452117587,
  "a3_kendall_tau_latency_vs_units": 0.8044668875040308,
  "p5_runs": [],
  "gpu_cost_basis": {
    "separate": {
      "fallback_latency": 32
    },
    "shared": {
      "fallback_latency": 32
    },
    "shared_mps": {
      "fallback_latency": 32
    }
  },
  "a3_kendall_tau_separate": 0.8044668875040308,
  "a3_basis_separate": "fallback",
  "a3_kendall_tau_shared": 0.8318918950325773,
  "a3_basis_shared": "fallback",
  "a3_kendall_tau_shared_mps": 0.8318918950325773,
  "a3_basis_shared_mps": "fallback"
}
```

## hotpot_q15_7/pareto_api

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| hop_1+aggregator+verifier | separate | 0.56 | 0.011 | 55.183 | api |
| planner+aggregator+verifier | separate | 0.525 | 0.011 | 57.485 | api |
| hop_1+hop_2+aggregator | separate | 0.515 | 0.011 | 53.93 | api |
| hop_1+aggregator | separate | 0.51 | 0.007 | 45.633 | api |
| aggregator+verifier | separate | 0.505 | 0.007 | 44.067 | api |
| only_aggregator | separate | 0.48 | 0.004 | 32.947 | api |
| all_small | separate | 0.275 | 8.62e-04 | 26.571 | api |
| all_small | shared | 0.275 | 8.62e-04 | 26.571 | api |
| all_small | shared_mps | 0.275 | 8.62e-04 | 26.571 | api |

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 39.857 | only_aggregator | 0.48 |
| shared | 39.857 | all_small | 0.275 |
| shared_mps | 39.857 | all_small | 0.275 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_aggregator | 0.48 | gpu_usd_throughput_separate | only_aggregator | 0.48 | False | fallback_latency |
| 0.5 | hop_1+aggregator | 0.51 | gpu_usd_throughput_separate | hop_1+aggregator | 0.51 | False | fallback_latency |
| 0.75 | hop_1+aggregator+verifier | 0.56 | gpu_usd_throughput_separate | hop_1+aggregator+verifier | 0.56 | False | fallback_latency |

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
  "n_front": 9,
  "hypervolume_joint": 0.3499897464309193,
  "hypervolume_two_step": 0.3497816382469737,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.025000000000000022,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 39.856695000082254,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": false
}
```

## hotpot_q15_7/pareto_estimated

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| hop_1+hop_2+aggregator | separate | 0.535 | 0.011 | 53.93 | api |
| hop_1+aggregator | separate | 0.51 | 0.007 | 45.633 | api |
| hop_2+aggregator | separate | 0.505 | 0.007 | 44.54 | api |
| aggregator+verifier | separate | 0.505 | 0.007 | 44.067 | api |
| only_aggregator | separate | 0.48 | 0.004 | 32.947 | api |
| all_small | separate | 0.275 | 8.62e-04 | 26.571 | api |
| all_small | shared | 0.275 | 8.62e-04 | 26.571 | api |
| all_small | shared_mps | 0.275 | 8.62e-04 | 26.571 | api |

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 39.857 | only_aggregator | 0.48 |
| shared | 39.857 | all_small | 0.275 |
| shared_mps | 39.857 | all_small | 0.275 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_aggregator | 0.48 | gpu_usd_throughput_separate | hop_2+aggregator | 0.505 | True | fallback_latency |
| 0.5 | hop_1+aggregator | 0.51 | gpu_usd_throughput_separate | hop_2+aggregator+verifier | 0.53 | True | fallback_latency |
| 0.75 | hop_1+hop_2+aggregator | 0.535 | gpu_usd_throughput_separate | hop_1+hop_2+aggregator | 0.535 | False | fallback_latency |

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
  "hypervolume_joint": 0.34458658037286427,
  "hypervolume_two_step": 0.34440204251257567,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.02499999999999991,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 39.856695000082254,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "regret_hypervolume": 0.010021093733232456,
  "regret_accuracy_mean": 0.006111111111111117
}
```

## hotpot_q15_7/routing

### routing.csv

| agent | rule | threshold | routed_share | accuracy | cost | baseline_accuracy | fixed_accuracy | fixed_cost | h6_match | primary |
|---|---|---|---|---|---|---|---|---|---|---|
| aggregator | samples_disagree |  | 0.695 | 0.425 | 0.004 | 0.32 | 0.455 | 0.004 | False | True |
| aggregator | entropy | 0 | 0.695 | 0.425 | 0.004 | 0.32 | 0.455 | 0.004 | False | False |
| aggregator | entropy | 0.5 | 0.695 | 0.425 | 0.004 | 0.32 | 0.455 | 0.004 | False | False |
| aggregator | entropy | 1 | 0.505 | 0.405 | 0.003 | 0.32 | 0.455 | 0.004 | False | False |
| verifier | samples_disagree |  | 0.52 | 0.38 | 0.004 | 0.32 | 0.41 | 0.004 | False | False |
| verifier | entropy | 0 | 0.52 | 0.38 | 0.004 | 0.32 | 0.41 | 0.004 | False | False |
| verifier | entropy | 0.5 | 0.52 | 0.38 | 0.004 | 0.32 | 0.41 | 0.004 | False | False |
| aggregator | baseline_vs_majority |  | 0.3 | 0.375 | 0.003 | 0.32 | 0.455 | 0.004 | False | False |

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
    "routed_share": 0.695,
    "accuracy": 0.425,
    "cost": 0.0040094595,
    "baseline_accuracy": 0.32,
    "fixed_accuracy": 0.455,
    "fixed_cost": 0.004131348,
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
| structural_topk | 1 | planner | 0.25 | 0.48 | 0.23 | False |
| structural_topk | 2 | hop_1,planner | 0.335 | 0.51 | 0.175 | False |
| structural_topk | 3 | hop_1,hop_2,planner | 0.36 | 0.56 | 0.2 | False |
| structural_topk | 4 | aggregator,hop_1,hop_2,planner | 0.535 | 0.56 | 0.025 | False |
| structural_topk | 5 | all | 0.555 | 0.56 | 0.005 | False |
| output_topk | 1 | verifier | 0.465 | 0.48 | 0.015 | False |
| output_topk | 2 | aggregator,verifier | 0.505 | 0.51 | 0.005 | False |
| output_topk | 3 | aggregator,hop_2,verifier | 0.51 | 0.56 | 0.05 | False |
| output_topk | 4 | aggregator,hop_1,hop_2,verifier | 0.55 | 0.56 | 0.01 | False |
| output_topk | 5 | all | 0.555 | 0.56 | 0.005 | False |
| ec_topk | 1 | verifier | 0.465 | 0.48 | 0.015 | False |
| ec_topk | 2 | aggregator,verifier | 0.505 | 0.51 | 0.005 | False |
| ec_topk | 3 | aggregator,hop_1,verifier | 0.56 | 0.56 | 0 | True |
| ec_topk | 4 | aggregator,hop_1,planner,verifier | 0.535 | 0.56 | 0.025 | False |
| ec_topk | 5 | all | 0.555 | 0.56 | 0.005 | False |
| ec_real_topk | 1 | verifier | 0.465 | 0.48 | 0.015 | False |

16 of 40 rows shown.

### estimator_errors.csv

| estimator | m | n_plans | n_held_out | mae_all | mae_held_out | feasibility_wrong_p25 | feasibility_wrong_p50 | feasibility_wrong_p75 |
|---|---|---|---|---|---|---|---|---|
| independence_additive | 3 | 32 | 23 | 0.055 | 0.067 | 0 | 0.13 | 0.174 |
| independence_multiplicative | 3 | 32 | 23 | 0.106 | 0.129 | 0 | 0.174 | 0.174 |
| pairwise_corrected | 3 | 32 | 23 | 0.025 | 0.035 | 0 | 0.261 | 0.435 |
| logit_additive | 3 | 32 | 23 | 0.058 | 0.071 | 0 | 0.13 | 0.174 |

### rules_summary

```json
{
  "accuracy_thresholds": {
    "p25": 0.41625,
    "p50": 0.4775,
    "p75": 0.5175000000000001
  },
  "h1c": {
    "reruns_used": 665,
    "reruns_full": 800,
    "share": 0.83125,
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
      "hop_1": 0.004999999999999999,
      "hop_2": 0.005,
      "aggregator": 0.009999999999999981,
      "verifier": 0.0
    },
    "a1_max_uv_abs_diff": 0.009999999999999981,
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
        "reruns_used": 665,
        "share": 0.83125,
        "uv_abs_error": {
          "planner": 0.0,
          "hop_1": 0.004999999999999999,
          "hop_2": 0.005,
          "aggregator": 0.009999999999999981,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.009999999999999981
      },
      "exact": {
        "reruns_used": 748,
        "share": 0.935,
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

## math_q15_7/cost

### plan_costs.csv

| plan | n_problems | tokens_out_small | tokens_out_large | tokens_in_small | tokens_in_large | tokens_in | tokens_out | api_usd | gpu_seconds | gpu_seconds_shared | cost_units | model_small | model_large | gpu_usd_latency | gpu_usd_latency_1 | gpu_usd_latency_shared_1 | gpu_usd_latency_2 | gpu_usd_latency_shared_2 | gpu_usd_latency_4 | gpu_usd_latency_shared_4 | gpu_usd_throughput_separate | gpu_cost_basis_separate | gpu_usd_throughput_shared | gpu_cost_basis_shared | gpu_usd_throughput_shared_mps | gpu_cost_basis_shared_mps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all_small | 200 | 296.6 | 0 | 1195.755 | 0 | 1195.755 | 296.6 | 2.68e-04 | 14.495 | 3.624 | 6 | qwen2.5:1.5b-instruct |  | 0.008 | 0.004 | 0.001 | 0.008 | 0.002 | 0.016 | 0.004 | 0.008 | fallback_latency | 0.002 | fallback_latency | 0.002 | fallback_latency |
| only_step_1 | 200 | 227.08 | 40.39 | 960.12 | 193.205 | 1153.325 | 267.47 | 1.00e-03 | 15.912 | 5.385 | 9 | qwen2.5:1.5b-instruct | qwen2.5:7b-instruct | 0.009 | 0.004 | 0.001 | 0.009 | 0.003 | 0.018 | 0.006 | 0.009 | fallback_latency | 0.003 | fallback_latency | 0.003 | fallback_latency |
| only_step_2 | 200 | 259.26 | 31.465 | 938.34 | 249.545 | 1187.885 | 290.725 | 0.001 | 16.229 | 5.085 | 9 | qwen2.5:1.5b-instruct | qwen2.5:7b-instruct | 0.009 | 0.005 | 0.001 | 0.009 | 0.003 | 0.018 | 0.006 | 0.009 | fallback_latency | 0.003 | fallback_latency | 0.003 | fallback_latency |
| only_step_3 | 200 | 268.925 | 24.245 | 902.315 | 290.635 | 1192.95 | 293.17 | 0.001 | 15.911 | 4.807 | 9 | qwen2.5:1.5b-instruct | qwen2.5:7b-instruct | 0.009 | 0.004 | 0.001 | 0.009 | 0.003 | 0.018 | 0.005 | 0.009 | fallback_latency | 0.003 | fallback_latency | 0.003 | fallback_latency |
| only_planner | 200 | 184.68 | 75.145 | 1020.505 | 132.45 | 1152.955 | 259.825 | 0.001 | 16.877 | 6.54 | 9 | qwen2.5:1.5b-instruct | qwen2.5:7b-instruct | 0.009 | 0.005 | 0.002 | 0.009 | 0.004 | 0.019 | 0.007 | 0.009 | fallback_latency | 0.004 | fallback_latency | 0.004 | fallback_latency |

5 of 64 rows shown.

### cost_summary

```json
{
  "n_plans": 64,
  "api_large_small_ratio": 21.604850014279034,
  "a3_kendall_tau_latency_vs_units": 0.6330668482713273,
  "p5_runs": [],
  "gpu_cost_basis": {
    "separate": {
      "fallback_latency": 64
    },
    "shared": {
      "fallback_latency": 64
    },
    "shared_mps": {
      "fallback_latency": 64
    }
  },
  "a3_kendall_tau_separate": 0.6330668482713273,
  "a3_basis_separate": "fallback",
  "a3_kendall_tau_shared": 0.6621476575558759,
  "a3_basis_shared": "fallback",
  "a3_kendall_tau_shared_mps": 0.6621476575558759,
  "a3_basis_shared_mps": "fallback"
}
```

## math_q15_7/pareto_api

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| step_1+verifier | separate | 0.81 | 0.003 | 38.396 | api |
| only_verifier | separate | 0.765 | 0.002 | 36.315 | api |
| step_1+step_2+aggregator | separate | 0.63 | 0.003 | 35.118 | api |
| step_1+aggregator | separate | 0.605 | 0.002 | 32.259 | api |
| only_aggregator | separate | 0.555 | 0.001 | 30.75 | api |
| planner+step_1+step_3 | separate | 0.515 | 0.002 | 29.956 | api |
| step_1+step_3 | separate | 0.465 | 0.002 | 25.657 | api |
| step_1+step_2 | separate | 0.455 | 0.002 | 25.496 | api |
| only_step_1 | separate | 0.415 | 1.00e-03 | 21.159 | api |
| all_small | separate | 0.37 | 2.68e-04 | 20.49 | api |

10 of 12 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 30.734 | planner+step_1+step_3 | 0.515 |
| shared | 30.734 | all_small | 0.37 |
| shared_mps | 30.734 | all_small | 0.37 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_aggregator | 0.555 | gpu_usd_throughput_separate | planner+step_1+step_3 | 0.515 | True | fallback_latency |
| 0.5 | only_verifier | 0.765 | gpu_usd_throughput_separate | planner+step_1+step_2+step_3+aggregator | 0.68 | True | fallback_latency |
| 0.75 | step_1+verifier | 0.81 | gpu_usd_throughput_separate | step_1+verifier | 0.81 | False | fallback_latency |

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
  "hypervolume_joint": 0.5031789476488668,
  "hypervolume_two_step": 0.4642421753572984,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.235,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 30.734320125135127,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true
}
```

## math_q15_7/pareto_estimated

### pareto_front.csv

| plan | placement | accuracy | cost | p95_latency | cost_basis |
|---|---|---|---|---|---|
| all_large | separate | 0.875 | 0.006 | 59.294 | api |
| all_large | shared | 0.875 | 0.006 | 59.294 | api |
| all_large | shared_mps | 0.875 | 0.006 | 59.294 | api |
| planner+step_1+step_2+step_3+verifier | separate | 0.87 | 0.005 | 50.57 | api |
| planner+step_1+step_2+verifier | separate | 0.855 | 0.005 | 47.377 | api |
| step_1+step_2+step_3+verifier | separate | 0.85 | 0.005 | 46.843 | api |
| planner+step_1+step_3+verifier | separate | 0.845 | 0.005 | 47.059 | api |
| step_1+step_2+verifier | separate | 0.835 | 0.004 | 42.814 | api |
| step_1+verifier | separate | 0.81 | 0.003 | 38.396 | api |
| only_verifier | separate | 0.765 | 0.002 | 36.315 | api |

10 of 23 rows shown.

### constrained_best.csv

| placement | limit_s | plan | accuracy |
|---|---|---|---|
| separate | 30.734 | step_1+step_2+step_3 | 0.455 |
| shared | 30.734 | all_small | 0.37 |
| shared_mps | 30.734 | all_small | 0.37 |

### budget_best.csv

| budget_fraction | api_usd_plan | api_usd_accuracy | gpu_column | gpu_usd_plan | gpu_usd_accuracy | differs | gpu_cost_basis |
|---|---|---|---|---|---|---|---|
| 0.25 | only_aggregator | 0.555 | gpu_usd_throughput_separate | planner+step_1+step_2 | 0.46 | True | fallback_latency |
| 0.5 | only_verifier | 0.765 | gpu_usd_throughput_separate | planner+step_1+step_2+step_3+aggregator | 0.665 | True | fallback_latency |
| 0.75 | step_1+step_2+verifier | 0.835 | gpu_usd_throughput_separate | planner+step_1+verifier | 0.83 | True | fallback_latency |

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
  "n_front": 23,
  "hypervolume_joint": 0.5110538720391173,
  "hypervolume_two_step": 0.4728234451868097,
  "a2_hv_strictly_higher": true,
  "a2_max_limit_gap": 0.235,
  "a2_gap_ge_2_points": true,
  "h3a_limit_s": 30.734320125135127,
  "h3a_best_differs": true,
  "h4a_any_budget_differs": true,
  "regret_hypervolume": 0.00026437750688801387,
  "regret_accuracy_mean": 0.000833333333333334
}
```

## math_q15_7/routing

### routing.csv

| agent | rule | threshold | routed_share | accuracy | cost | baseline_accuracy | fixed_accuracy | fixed_cost | h6_match | primary |
|---|---|---|---|---|---|---|---|---|---|---|
| verifier | samples_disagree |  | 0.88 | 0.79 | 0.002 | 0.405 | 0.805 | 0.002 | False | True |
| verifier | entropy | 0 | 0.88 | 0.79 | 0.002 | 0.405 | 0.805 | 0.002 | False | False |
| verifier | entropy | 0.5 | 0.88 | 0.79 | 0.002 | 0.405 | 0.805 | 0.002 | False | False |
| verifier | entropy | 1 | 0.575 | 0.67 | 0.002 | 0.405 | 0.805 | 0.002 | False | False |
| verifier | baseline_vs_majority |  | 0.35 | 0.59 | 0.001 | 0.405 | 0.805 | 0.002 | False | False |
| planner | baseline_vs_majority |  | 0.59 | 0.495 | 0.002 | 0.405 | 0.425 | 0.001 | False | False |
| aggregator | samples_disagree |  | 0.295 | 0.48 | 7.22e-04 | 0.405 | 0.57 | 0.001 | False | False |
| aggregator | entropy | 0 | 0.295 | 0.48 | 7.22e-04 | 0.405 | 0.57 | 0.001 | False | False |

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
    "routed_share": 0.88,
    "accuracy": 0.79,
    "cost": 0.0024184185,
    "baseline_accuracy": 0.405,
    "fixed_accuracy": 0.805,
    "fixed_cost": 0.002249466,
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
| structural_topk | 1 | planner | 0.39 | 0.765 | 0.375 | False |
| structural_topk | 2 | planner,step_1 | 0.395 | 0.81 | 0.415 | False |
| structural_topk | 3 | planner,step_1,step_2 | 0.505 | 0.81 | 0.305 | False |
| structural_topk | 4 | planner,step_1,step_2,step_3 | 0.535 | 0.81 | 0.275 | False |
| structural_topk | 5 | aggregator,planner,step_1,step_2,step_3 | 0.68 | 0.81 | 0.13 | False |
| structural_topk | 6 | all | 0.785 | 0.81 | 0.025 | False |
| output_topk | 1 | verifier | 0.765 | 0.765 | 0 | True |
| output_topk | 2 | aggregator,verifier | 0.765 | 0.81 | 0.045 | False |
| output_topk | 3 | aggregator,step_3,verifier | 0.75 | 0.81 | 0.06 | False |
| output_topk | 4 | aggregator,step_2,step_3,verifier | 0.735 | 0.81 | 0.075 | False |
| output_topk | 5 | aggregator,step_1,step_2,step_3,verifier | 0.775 | 0.81 | 0.035 | False |
| output_topk | 6 | all | 0.785 | 0.81 | 0.025 | False |
| ec_topk | 1 | verifier | 0.765 | 0.765 | 0 | True |
| ec_topk | 2 | step_3,verifier | 0.775 | 0.81 | 0.035 | False |
| ec_topk | 3 | step_2,step_3,verifier | 0.805 | 0.81 | 0.005 | False |
| ec_topk | 4 | step_1,step_2,step_3,verifier | 0.8 | 0.81 | 0.01 | False |

16 of 48 rows shown.

### estimator_errors.csv

| estimator | m | n_plans | n_held_out | mae_all | mae_held_out | feasibility_wrong_p25 | feasibility_wrong_p50 | feasibility_wrong_p75 |
|---|---|---|---|---|---|---|---|---|
| independence_additive | 3 | 64 | 54 | 0.078 | 0.089 | 0.037 | 0 | 0.204 |
| independence_multiplicative | 3 | 64 | 54 | 0.101 | 0.114 | 0.037 | 0.019 | 0.204 |
| pairwise_corrected | 3 | 64 | 54 | 0.036 | 0.043 | 0.037 | 0 | 0.204 |
| logit_additive | 3 | 64 | 54 | 0.052 | 0.059 | 0.037 | 0 | 0.204 |

### rules_summary

```json
{
  "accuracy_thresholds": {
    "p25": 0.5225,
    "p50": 0.7075,
    "p75": 0.77
  },
  "h1c": {
    "reruns_used": 616,
    "reruns_full": 1000,
    "share": 0.616,
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
      "step_2": 0.0,
      "step_3": 0.009999999999999995,
      "aggregator": 0.03,
      "verifier": 0.0
    },
    "a1_max_uv_abs_diff": 0.03,
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
    "a1_holds_without_share": false,
    "e3_skip_variants": {
      "reruns_full": 1000,
      "key": {
        "reruns_used": 616,
        "share": 0.616,
        "uv_abs_error": {
          "planner": 0.0,
          "step_1": 0.015,
          "step_2": 0.0,
          "step_3": 0.009999999999999995,
          "aggregator": 0.03,
          "verifier": 0.0
        },
        "max_uv_abs_error": 0.03
      },
      "exact": {
        "reruns_used": 891,
        "share": 0.891,
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

