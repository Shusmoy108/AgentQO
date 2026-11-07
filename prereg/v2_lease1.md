# AgentQO v2, Lease 1: pre-registration

Committed: 2026-11-07 09:57:34 UTC (the commit carrying this line is the registration).
Lease starts: Nov 16, 12:00 UTC.

These hypotheses do not change after the lease starts. Any change goes in
`prereg/v2_amendments.md` with a time and reason.

## Hypotheses

  H1a  On new data (Qwen 3B/14B math; Qwen 1.5B/7B HotpotQA), consequence from real errors
       (resample_disagree) ranks late agents lower than synthetic corruption does, and ec_real
       picks the best evaluated plan at least as often as ec_synthetic at budgets 1 and 2.
  H1b  confident_uv picks a plan within 2 points of the best evaluated plan at budgets 1 and 2
       in every setting.
  H1c  --disagree-only uses at most 1/5 of the full reruns and changes no top-2 agent.
  H2a  On exhaustive math-chain plans, independence estimates (additive and multiplicative) have
       mean absolute error >= 5 points.
  H2b  For constraints "accuracy >= a" (a = 25th, 50th, 75th percentile of plan accuracies),
       independence estimates misjudge feasibility more often than pairwise_corrected estimates.
  H2c  pairwise_corrected at least halves the mean absolute error of independence estimates.
  H3a  Under a p95 latency limit of 1.5x the separate-placement p95 of all_small, the best
       allocation differs between separate and shared placement in at least one setting.
  H3b  Joint search has higher hypervolume than the two-step baseline.
  H3c  Predicted plan p95 latency is within 10% of measured p95 for the plans run in phase P5.
  H4a  The accuracy-maximizing plan under a fixed budget differs between API pricing and GPU-time
       pricing in at least one setting.
  H4b  Measured large/small cost ratio per problem (API pricing) is above 4.
  H5a  Simulated adaptive checking (add 25 problems at a time, stop when the leader's CI clears the
       runner-up) ends within 2 points of the best plan using at most half the problems of a fixed
       400-problem check.
  H6   For at least one agent, disagreement-triggered routing matches the accuracy of the best fixed
       plan with the same agent upgraded, within 1 point, at lower cost.

## How each is measured (the code's reading of the text above)

The hypotheses leave these open. They are frozen with this file.

Settings: math Qwen 1.5B/7B, math Qwen 3B/14B, math Granite 2B/8B, HotpotQA Qwen 1.5B/7B.
Phases: P1-P6 as listed at the top of `scripts/v2/run_phase.sh`.

| Id | Reading | Output |
|---|---|---|
| H1a | Late agents = aggregator and verifier. Compared on their rank by mean consequence, resample_disagree against all synthetic strategies pooled. "Best evaluated plan" = highest accuracy among all plans with at most k upgrades. | `labels_v2_by_strategy.csv`, `rule_plans.csv` (`is_best`) |
| H1b | `regret` <= 0.02 at budgets 1 and 2 in all four settings. | `rule_plans.csv` |
| H1c | One rerun = recomputing one agent's descendants for one problem. Agents with no descendants count in neither total. | `h1c.json` |
| H2a, H2c | MAE over held-out plans: not all_small, not a single upgrade, not one of the measured top-3 pairs. MAE over all plans is reported next to it. m = 3. | `estimator_errors.csv` |
| H2b | Share of held-out plans whose estimate lands on the wrong side of a, per percentile. Percentiles are over all plans' measured accuracy. | `estimator_errors.csv` |
| H3a | K = 16 problems in flight. Best = highest predicted-feasible measured accuracy, ties to lower cost. | `constrained_best.csv` |
| H3b | Normalized volume in (1-accuracy, cost, p95 latency), GPU pricing at 2 USD/h. Two-step: for k = 0..n, the most accurate plan with at most k upgrades, then its fastest placement. | `pareto_summary.json` |
| H3c | Holds if the mean over repeats of each plan x placement is within 10%. Latency base = the separate-placement calls of P5 itself. | `latency_check.csv` |
| H4a | Budget = cheapest + f x (all_large - all_small) with f = 0.25, 0.5, 0.75, in separate placement, at 2 USD/h. | `budget_best.csv` |
| H4b | all_large over all_small, mean API USD per problem. | `cost_summary.json` |
| H5a | Over 200 random problem orders on the 400-problem exhaustive set: mean gap to the best plan <= 0.02 and mean problems used <= 200. CI = 95% paired bootstrap of leader minus runner-up, no multiplicity correction. | `adaptive_summary.json` |
| H6 | Fixed plan = only that agent upgraded, same problems. Routing cost includes the K small samples. Any rule and threshold in `routing.csv` counts. | `routing.csv` (`h6_match`) |
