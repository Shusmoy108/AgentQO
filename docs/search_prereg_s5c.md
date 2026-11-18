# S5c pre-registration (confirmatory)

Registered 20261118T1353Z, before any X9 data exists: `git ls-tree origin/v2-lease1 -- results/v2` lists no X9 path and
there is no local results/v2/X9*. No A16 data beyond what the registered run already used (math_tiers: plans
P2b/math_tiers, labels P1/math_q15_7 + P2b/math_tiers, cost P6/math_tiers) has been read.

## Hypothesis

S5c: plans chosen on math_tiers' 200 eval problems (NSGA-II pairwise and active-learning NSGA-II, 10% budget, frozen
settings) keep >= 95% of their hypervolume (and report the ratio to the best possible front) when re-scored on 200
new GSM8K problems (results/v2/X9/math_tiers).

## Frozen procedure (scripts/search/s5c.py at this tag; same pattern and decision rule as S5b)

- Setting math_tiers (729 plans, 6 agents, tiers small / large / xl = Qwen2.5 1.5B / 7B / 14B); ground truth as in
  the registered run (P2b accuracy, P6 tier_pareto API cost; tier pricing as registered).
- Methods: nsga2_pairwise_m3 (pairwise_corrected m 3, pair cap floor(B/2) - 1) and nsga2_active_m3 (run_active),
  from agentqo/search/methods.py at this tag. Hyperparameters frozen as Amendment 1 / S6 / S5b: pop 40, crossover
  0.9, mutation 1/n, 50 generations, active_rounds 4, ridge lambda 1.
- Budget B = max(4, round(0.10 x 729)) = 73 verified plans; seeds 0-29 (numpy default_rng(seed)).
- Per run: the verified front = plans the method verified that are non-dominated on (eval API cost, eval accuracy).
- Retention = HV(front plans, X9 accuracy, eval API cost) / HV(front plans, eval accuracy, eval API cost). 2D HV,
  cost normalised by the most expensive plan, reference (cost 1, accuracy 0), as in S1-S5b.
- X9 accuracy from results/v2/X9*/math_tiers/plans/h3_plans.csv (column accuracy). Front plans X9 did not score are
  dropped from both HVs and counted. If the folder name differs, only the path is changed, and logged, before running.
- Reported, not used for the decision: X9 HV / HV of the best possible front among the plans X9 scored, mean over seeds.

## Decision rule

Per method, mean retention over the 30 seeds >= 0.95 passes. S5c is HELD if both methods pass, PARTIAL if one,
FAILED if neither. The 95% t-CI of retention is reported alongside.

## Pre-tag dry run (pipeline check only, no X9 data)

s5c.py --x9 pointed at the eval file itself (P2b/math_tiers/plans/h3_plans.csv), output to a scratch folder:
retention 1.0000 for both methods (as it must); best-front ratio 0.9904 (pairwise; matches S1's math_tiers HV ratio
at 10%) and 0.9991 (active).
