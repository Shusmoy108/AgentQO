# S5d pre-registration (confirmatory)

Registered 20261118T1418Z, before any X11 data exists: `git ls-tree origin/v2-lease1 -- results/v2` lists no X11 path, there
is no local results/v2/X11*, and no X11 amendment is on v2-lease1 yet (so the folder is registered as a glob).

## Hypothesis

S5d: re-score math500_q15_7 and code_c15_7 fronts (registered methods, same budgets and seeds as the new-settings
run) on the X11 held-out problems; retention and ratio-to-best-front metrics as in S5; HELD if retention >= 0.95 in
both.

## Frozen procedure (scripts/search/s5d.py at this tag; S5's procedure, scripts/search/s5_rescore.py)

- Settings: math500_q15_7 (X5; 64 plans, 300 eval problems) and code_c15_7 (X7; 32 plans, 178 eval problems), ground
  truth as in the new-settings run (eval accuracy from their plans folders, tier-priced API cost from h3_calls).
- Methods: every registered 2-objective method in the new-settings run (results/search/new_settings/results.csv):
  all 14 of METHODS_2D on math500_q15_7; on code_c15_7 the 11 without rule_* (no code workflow graph on this branch).
  Hyperparameters frozen (Amendment 1): pop 40, crossover 0.9, mutation 1/n, 50 generations, active_rounds 4.
- Budgets 1/2/5/10/20% (B = max(4, round(frac x plans)): math500 4/4/4/6/13, code 4/4/4/4/6); seeds 0-29.
- Per run: the verified front = verified plans non-dominated on (eval API cost, eval accuracy). Retention =
  HV(front plans, X11 accuracy, eval API cost) / HV(front plans, eval accuracy, eval API cost); 2D HV as in S1-S5.
  Ratio to best front = HV(front plans, X11 accuracy) / HV of the best possible front among the plans X11 scored.
- X11 accuracy from results/v2/X11*/<setting>/plans/h3_plans.csv (column accuracy). Front plans X11 did not score
  are dropped from both HVs and counted. If the folder layout differs, only the path is changed, and logged, before
  running.

## Decision rule (as in S5)

Decision quantity: nsga2_pairwise_m3 at the 10% budget, mean retention over the 30 seeds, per setting. S5d is HELD if
it is >= 0.95 in both settings, PARTIAL if in one, FAILED if in neither. All other methods and budgets, and the ratio
to the best front, are reported and not used for the decision.

## Pre-tag dry run (pipeline check only, no X11 data)

s5d.py --held pointed at the two eval files themselves, output to a scratch folder: retention 1.0000 in all 3,750
runs (as it must); ratio to best front for the decision cell 0.9597 (math500_q15_7) and 0.9457 (code_c15_7), equal to
the new-settings HV ratios at 10%.
