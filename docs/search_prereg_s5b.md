# S5b pre-registration (confirmatory)

Registered 20261118T0336Z, before any X8 data exists: `git ls-tree origin/v2-lease1 -- results/v2` lists no X8 path and
there is no local results/v2/X8*. No A17 data beyond what the registered run already used (P2c/complex_q15_7) has
been read.

## Hypothesis

S5b: plans chosen on complex_q15_7's 200 eval problems (NSGA-II pairwise and active-learning NSGA-II, 10% budget,
frozen settings) keep >= 95% of their hypervolume, and report the ratio to the best possible front, when re-scored
on 200 new GSM8K problems (results/v2/X8/complex_q15_7).

## Frozen procedure (scripts/search/s5b.py at this tag)

- Setting complex_q15_7 (1024 plans, 10 agents); ground truth as in the registered run (P2c accuracy, P6 API cost).
- Methods: nsga2_pairwise_m3 (pairwise_corrected m 3, pair cap floor(B/2) - 1) and nsga2_active_m3
  (run_active), both from agentqo/search/methods.py at this tag. Hyperparameters frozen as Amendment 1 / S6:
  pop 40, crossover 0.9, mutation 1/n, 50 generations, active_rounds 4, ridge lambda 1.
- Budget B = max(4, round(0.10 x 1024)) = 102 verified plans; seeds 0-29 (numpy default_rng(seed)).
- Per run: the verified front = plans the method verified that are non-dominated on (eval API cost, eval accuracy).
- Retention = HV(front plans, X8 accuracy, eval API cost) / HV(front plans, eval accuracy, eval API cost). HV is
  2D, cost normalised by the most expensive plan, reference (cost 1, accuracy 0), as in S1-S5.
- X8 accuracy read from results/v2/X8*/complex_q15_7/plans/h3_plans.csv (column accuracy). If X8 scores only a subset
  of plans, front plans it did not score are dropped from both HVs and counted; this is reported. If the folder name
  differs, only the path is changed, and logged, before running.
- Reported, not used for the decision: X8 HV / HV of the best possible front among the plans X8 scored (the
  "ratio to the best possible front"), mean over seeds.

## Decision rule

Per method, mean retention over the 30 seeds >= 0.95 passes. S5b is HELD if both methods pass, PARTIAL if one,
FAILED if neither. The 95% t-CI of retention is reported alongside.

## Pre-tag dry run (pipeline check only, no X8 data)

s5b.py --x8 pointed at the eval file itself (P2c/complex_q15_7/plans/h3_plans.csv), output to a scratch folder:
retention 1.0000 for both methods (as it must), best-front ratio 0.9882, matching S1's complex_q15_7 HV ratio at 10%.
