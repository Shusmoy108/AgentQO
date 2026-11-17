# AgentQO v2 — Offline multi-objective plan search: pre-registration

Registered: 2026-11-17T21:27:24Z (UTC). Tag: `search-prereg-20261117T2127Z`.
Branch: v2-search, cut from origin/v2-lease1 at 340b73d8.
At registration time no X2 data (eval_x2 / HotpotQA extra) exists on origin/v2-lease1,
and none has been opened. No search has been run.

## Hypotheses

**S1:** NSGA-II with the pairwise-corrected surrogate reaches >= 95% of the true hypervolume
(accuracy vs API cost) while verifying <= 10% of the plans, in every setting with >= 256 plans.

**S2:** At the same verification budget it beats (a) the same search with the independence (additive)
surrogate, (b) an Abacus-style method (independence estimates + exact Pareto pruning), (c) random
search, (d) greedy-by-UV, (e) the fixed rules.

**S3:** The surrogate gap is largest where interactions are strongest (largest independence error).

**S4 (3 objectives):** With a placement gene and measured latency (X1) or predicted latency
(latsim frozen tag) as the third objective, joint search over plan + placement beats searching the
plan first and then the placement, on accuracy-cost-p95 hypervolume.

**S5 (generalization):** Plans chosen on the 400 eval problems keep >= 95% of their hypervolume
when re-scored on the X2 held-out problems (eval_x2 / HotpotQA extra).

## Evaluation

30 seeds, mean and 95% CI. Differences smaller than the X4 run-to-run noise
(per-plan |delta| up to ~3.75 points) are reported as ties.

X2 data must NOT be opened before this tag exists (S5 is then a true held-out test).

## Protocol details fixed at registration

- Hypervolume reference point: cost of the most expensive plan, accuracy 0 (as in
  results/v2/P6/search_ground_truth.md; true fronts via tools_lease/search_gt.py).
- Verification budgets B = 1, 2, 5, 10, 20% of the plan space (minimum 4 plans). Fronts are built
  from verified plans only. Measured pair plans used by pairwise_corrected count against B.
- Surrogate single-agent terms come only from label data (labels_v2*).
- Hyperparameters (NSGA-II, and shared population size for MOPSO/GDE3): population 40,
  crossover probability 0.9, mutation probability 1/n (n = genome length). Chosen once on
  math_q15_7 and frozen before any other setting is run; any change is logged as an amendment
  in docs/search_log.md before use.
- Scalability (S-extra, simulated and labeled as such): synthetic 10/15/20/30-agent workflows,
  3 tiers, fixed budget 200 verified plans, vs a long oracle NSGA-II run.

## Amendment 1 (2026-11-17T21:34:00Z): frozen hyperparameters and protocol choices — before any setting other than math_q15_7 was run

Tuning on math_q15_7 only (nsga2_pairwise_m3, 30 seeds x 5 budgets; results/search/hp_generations_math_q15_7.txt):
mean HV ratio 0.9121 / 0.9119 / 0.9119 / 0.9119 / 0.9119 for 5 / 10 / 25 / 50 / 100 generations. Ties within
0.0002 (the 64-plan space is exhausted at any setting), so the pre-written value is kept. FROZEN:
- all evolutionary engines: population 40, 50 generations, per-gene mutation 1/n (n = genome length);
- NSGA-II: binary tournament (rank, crowding), uniform crossover p 0.9;
- MOPSO (discrete): keep gene w 0.4, personal best c1 0.3, archive leader c2 0.3, then mutation 1/n;
- GDE3: F 0.5, CR 0.9, continuous genes floored/clipped to tier indices (rounding repair);
- active-learning variant (exploratory): 4 verification rounds, ridge (lambda 1) on pair residuals;
- pairwise_corrected: measures all_small plus pairs of the top-m label-UV options (same-agent pairs dropped),
  at most floor(B/2) - 1 pairs; all of them are charged to B;
- verification choice: surrogate non-dominated fronts in order, each spread evenly along predicted cost;
- seeds 0-29; numpy default_rng(seed), same seed for every method (common random numbers).
