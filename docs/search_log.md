# Search log (v2-search)

Times UTC. Choices made without asking, as instructed.

- 2026-11-17T21:27Z Registration tag search-prereg-20261117T2127Z pushed before any search; no X2 folder on
  origin/v2-lease1 at that time (results/v2 had E1 P0-P6 X1 X1b X3_vmB X4 only).
- Worktree ~/AgentQO-search, branch v2-search from origin/v2-lease1 340b73d8. Lease files are read only.
- pymoo is not installed; NSGA-II, MOPSO and GDE3 are implemented in numpy (agentqo/search/methods.py). No new dependency.
- Ground truth reproduces results/v2/P6/search_ground_truth.md exactly (front sizes and HV for all 11 settings).
- Surrogate single terms: label UV (labels_v2.csv) and label token counts priced with configs/v2_prices.yaml
  (API cost surrogate; rank correlation with true cost 0.976-0.998). math_tiers: large terms from
  P1/math_q15_7 labels (same 1.5B->7B pair, as tiers_report.py), xl terms from P2b/math_tiers labels.
- Independence surrogates use the label-run all_small accuracy as base (no verified plan). pairwise_corrected
  uses the measured all_small (eval) as base, so pair deltas do not absorb the label/eval base offset; that
  plan is charged to the budget.
- Latency truth: X1 (and X1_vmB) placement_summary p95 at K=16, mean of repeats; otherwise latsim frozen tag
  latsim-frozen-20261117T133315Z pred_p95 at K=16 ("predicted"). Placements: separate, shared (shared_mps not
  in X1, dropped). X1b (K sweep) not used. Measured coverage: q15_7 math/hotpot/hotpot_iso, q3_14, granite math,
  phi math: all plans both placements; complex_q15_7 184/1024 shared only; math_tiers 114/729 shared only;
  hotpot granite/phi settings: none (all predicted).
- S4: accuracy and API cost do not depend on placement; only latency does. Pair plans of the joint search are
  verified at placement separate. Plan-first: the 2-objective search's B plans, each at its lowest predicted p95.
- greedy_uv stops when every agent is at the top tier (n x (T-1) + 1 plans); it may use less than B.
- Fixed rules: prefix plans k = 0..n of the rule order (multi-tier: each prefix at every tier), evenly
  subsampled to B; confident_uv uses the top tier's label UV and CI.
- Generations: math_q15_7 tuning uninformative (all tie); kept 50 (Amendment 1).
- 2026-11-17 ~22:10Z Full run finished (results/search/results.csv, 28,050 runs: 11 settings x 17 methods x 5 budgets
  x 30 seeds). I looked at the per-method mean HV-ratio pivot before fixing the decision rules below; the rules
  were written before computing any S2-S4 test statistic.
- Tie threshold for hypervolume (prereg: "differences smaller than X4 noise are ties"). Replaying X4's plan
  accuracies instead of P2's changes the true HV by 0.66% (math_q15_7) and 1.34% (hotpot_q15_7); tau_HV = 0.0134
  HV ratio. Regret (accuracy points) uses 0.0375 directly. A cell (setting x budget) is a WIN if the paired mean
  difference over the 30 seeds is > tau and its 95% CI (t) excludes 0; LOSS symmetric; otherwise TIE.
  Sensitivity: the worst-case bound (every plan shifted 3.75 points) is reported alongside.
- Decision rules: S1 HELD if NSGA-II pairwise m3 mean HV ratio >= 0.95 at the 10% budget in every setting with
  >= 256 plans (complex_q15_7, math_tiers). S2 per comparator over the 55 cells: BEATS if W > L and W >= 28;
  LOSES if L > W; else TIE; S2 HELD if it beats all of (a)-(e) (each of the 3 fixed rules counted under (e)),
  PARTIAL if some, FAILED if none. S3: Spearman over the 11 settings between independence error (MAE of the
  additive estimate built from the eval single-upgrade plans, i.e. pure interaction) and the gap (pairwise m3
  minus independence additive, mean HV ratio over budgets): HELD rho > 0 and p < 0.05; PARTIAL rho > 0, p >= 0.05;
  FAILED rho <= 0. S4 (joint vs plan-first, hv3): HELD if W >= half the cells and L = 0; FAILED if W = 0 or L > W;
  else PARTIAL. S5 pending X2.
- Seeds barely matter on the real settings: the 50-generation archive of every evolutionary engine covers (almost)
  the whole 32-1,024-plan space, so verification picks are deterministic given the surrogate and CIs are ~0.
  On 32/64-plan spaces the 1/2/5% budgets all round up to the 4-plan minimum (flat curves).
- Abacus-style and nsga2_indep_add give identical results on every real setting (same surrogate, archive = space).
- S5 script ready (scripts/search/s5_rescore.py); refuses to run without the registration tag; reads results/v2/X2*.
- Scalability (SIMULATED): gains and label noise scaled by 6/n; interactions sparse, expected 15 interacting agent
  pairs per workflow with magnitudes from the 215 measured pair deltas; xl gain = large gain + measured
  (xl - large) difference; xl cost = 2 x large cost (price ratio). Cost surrogate exact. Abacus-style uses an
  exact Pareto DP over the independence estimate; if its front < 200 plans the rest is random (front was 28-218).
- Status 2026-11-17T21:5xZ: complete for the 11 lease settings. Not yet available: X2 (S5), X3 (729 cross-family,
  partial), X5, X6, X7, laptop q4. Re-run: run_search.py --settings <new> and summarize.py (SETTINGS dict needs
  the new setting's label/plan folders added).

## 2026-11-18 (UTC) review round; registered verdicts unchanged

- TIE THRESHOLD TIMING (stated plainly): tau = 0.0134 HV ratio was set AFTER I had seen the per-method mean
  HV-ratio pivot over all settings (printed when the full run finished), but BEFORE any S2-S4 paired test,
  W/T/L count or S3 correlation was computed. Why it had to be set then: the registration states the tie rule
  in accuracy points per plan (X4 |delta| up to ~3.75 points), while S1-S4 are judged on hypervolume ratios,
  so a translation into HV units was needed and had not been written down. I chose the empirical translation
  (replay X4's re-run plan accuracies through the same HV: 0.66% math_q15_7, 1.34% hotpot_q15_7; took the larger)
  rather than the worst-case bound (every plan shifted 3.75 points, ~5-9% HV), because X4 is the measured noise.
  The pivot I had seen showed pairwise m3 below independence on average, so a larger tau would have turned more
  S2 losses into ties; the smaller, data-driven tau was not chosen to favour the registered hypothesis.
- X1c (new on origin/v2-lease1 at 00:01Z: Phi grid and a 9-plan A16 three-model shared run) is a different
  server configuration from X1, so it is not mixed into the latency truth. X1/X1_vmB unchanged; registered
  S4 inputs unchanged.
- Figure 1 review: nsga2_indep_add was drawn but hidden under abacus (identical curves on all 11 settings).
  Redrawn with distinct styles (abacus thick dashed underneath, indep_add hollow squares), MOPSO and GDE3
  added, x labels show the effective B, and the legend states which curves coincide.
- Exploratory runs (all labeled "exploratory, not registered", outputs under results/search/exploratory/):
  strict HV (reference accuracy = all_small) + IGD + regret on complex_q15_7 and math_tiers; pair cap 25% of B
  variant on the 32/64-plan spaces; S4 redesign (budget = plans, both placements from latsim at no cost);
  active learning on real settings (registered exploratory variant) and in the simulation; simulated
  interaction-strength sweep (pair interactions x0, 0.5, 1, 2, 4; budgets 50/100/200; 10-30 agents). In the
  sweep the scale-1 instance is identical to the registered scalability instance (same rng seed); scaling
  multiplies the sampled pair magnitudes only, so gains, costs and label noise are the same across scales.
- 2026-11-18T00:2xZ Exploratory round finished (results/search/exploratory/, appended to hypotheses_search.md under
  "Exploratory, not registered"). Registered files unchanged: results.csv, scalability_SIMULATED.csv,
  search_prereg.md, and every registered verdict. Active-learning variant in the simulation uses the same 4-round
  ridge refit as on the real settings, with features = every cross-agent option pair. X2 still absent at 00:09Z.

## 2026-11-18 S6 registration, fairness check, S5

- 00:54Z S6 registered and tagged (search-prereg-s6-20261118T0054Z, docs/search_prereg_s6.md) before any X3 plan
  accuracy existed or was opened; then the confirmatory sweep (b) and the exploratory next-best fairness sweep
  were started (in that order).
- X2 landed on origin/v2-lease1 (X2: math_q15_7, hotpot_q15_7, hotpot_iso_q15_7; X2_vmB: math_granite; all plans,
  719 GSM8K / 600 HotpotQA problems). Merged origin/v2-lease1 into v2-search at ~00:58Z; the merge changed no
  ground-truth input (P1-P6, X1 placement files, configs, code unchanged; only X1 manifest/summary added).
- S5 operationalization, written BEFORE running s5_rescore.py on X2 (the script's docstring, written before X2
  existed, says "HELD if >= 0.95 everywhere" without naming the method/budget): the registered main method
  nsga2_pairwise_m3 at the 10% budget (script default); for each X2 setting, retention = HV of its verified
  front's plans with X2 accuracy / HV of the same plans with eval accuracy (same eval API cost; cost is a plan
  property). S5 HELD if mean retention over 30 seeds >= 0.95 in every X2 setting; PARTIAL if in some; FAILED if
  none. Reported alongside (not deciding): every other method; the true eval front re-scored on X2; and the
  chosen front's X2 HV divided by the true X2 front's HV.
- 01:1xZ S6(b) (confirmatory, seeds 1000-1029, code at the S6 tag) PARTIAL: 5/8 cells pass (all B = 200 cells;
  at B = 100 only 20 agents x2). Exploratory fairness check (seeds 0-29, abacus_nextbest added; file
  scalability_interaction_nextbest_SIMULATED.csv; earlier random-fill sweep file kept): active vs next-best
  Abacus W/L 7/6 (B 50), 14/1 (B 100), 16/0 (B 200) of 20 cells; next-best fill beats random fill only at weak
  interactions (x0-x0.5) and is worse at x2-x4. Existing method rows are unchanged from the first sweep
  (same seeds); only the reference front now also includes abacus_nextbest's plans.
- Watcher (git ls-tree names only, every 5 min) waits for X2_vmB/math_phi and X3_vmB/plans/h3_plans.csv.

## 2026-11-18: X2 math_phi and X5 landed (merge 5c5e651c)
- S5 re-run with all five X2 settings: HELD (math_phi retention 1.025, X2 HV / true X2 front 0.978). No X3 file came in this merge.
- X5 MATH-500 (math500_q15_7, 64 plans, 300 problems) added as EXTRA setting: labels X5/math500_q15_7/labels, plans
  X5/math500_q15_7/plans, API cost priced from h3_calls with price_plans (checked: reproduces P6 plan_costs on P2
  math_q15_7 exactly). Rule orders use the math workflow (run_config says workflow=math).
- Choice: the registered S1-S4 verdicts stay on the 11 original settings (round-2 instruction to keep them as they
  are). X5 is run with the same 14 methods, budgets, 30 seeds and metrics (2 objectives; no latency truth, so no 3D
  runs) into results/search/new_settings/results.csv and reported in NEW_SETTINGS.md as "New settings", with S3's rho
  recomputed over 12 settings as supplementary.

## 20261118T0336Z: S5b registered (docs/search_prereg_s5b.md, tag search-prereg-s5b-20261118T0336Z)
- Written and tagged before any X8 file exists on v2-lease1 or locally. scripts/search/s5b.py is frozen at the tag;
  it refuses to read X8 without the tag. One dry run on the eval file (retention 1.0) checked the pipeline.

## 2026-11-18 ~04:50Z: X3 landed (merge 3a99966c); S6(a) path change, logged before running
- The completed X3 plans are in results/v2/X3_vmB/plans_2 (X3_vmB/plans holds only a run_config). x3_run_note.txt
  shows restarts; the restart wrote to new folders (labels_q7_G8_2, labels_q7_P4_2, plans_2). The _2 label files are
  byte-identical to labels_q7_G8 / labels_q7_P4 (labels_v2.csv, per_problem, by_strategy) and the plans run_config
  differs from the frozen one only in the cache path. Per docs/search_prereg_s6.md, only the path changed:
  EXTRA x3_cross_family plans "X3_vmB/plans" -> "X3_vmB/plans_2". Labels path unchanged (identical files).
- Disclosure: while grepping run_B-x3.log.txt for the reason for the _2 folders (after the S6 tag), the grep also
  matched ~15 lines of the log's top-plan table (accuracies 0.95-0.97). No S6 code, method or decision rule changed;
  s6.py / methods.py / surrogates.py are as at search-prereg-s6-20261118T0054Z apart from changes logged above.
- X7 code_c15_7 plans landed in the same merge; X6 math_q7_32 has labels only. X8 not landed.
- S6(a) run (s6.py x3, seeds 0-29, B = 15/36/73): FAILED, 0 of 3 cells pass. Active-learning NSGA-II beats
  abacus_nextbest at every budget but by 0.0062 / 0.0056 / 0.0027 HV ratio, all below tau = 0.0134. Strict HV
  (reported, not decisive) favours active by 0.076 / 0.069 / 0.034. Both methods are near-deterministic across seeds
  on this space (seed SD <= 0.0001), so the CIs are seed spread only, not problem-sampling uncertainty.
- Bug fixed in s6.py (reporting only): re-reading S6.md keyed each part by its whole first line, so running one part
  dropped the other. Key is now the "## S6(x)" prefix. S6(b) regenerated from the unchanged s6b_sweep CSV;
  text identical to the committed one.

## 2026-11-18 ~05:00Z: X6 math_q7_32 and X7 code_c15_7 added (merge 8c533aa3)
- EXTRA settings: math_q7_32 (X6, Qwen2.5 7B -> 32B, math workflow, 64 plans, 400 eval_ext problems) and code_c15_7
  (X7_vmB, MBPP+, Qwen2.5-Coder 1.5B -> 7B, 5 agents, 32 plans, 178 problems). API cost priced from h3_calls by
  tier name (small/large prices of configs/v2_prices.yaml), the same choice as X3; it scales relative costs only.
- Choice: code_c15_7 runs without the three fixed-rule methods. They need the workflow graph (WORKFLOWS in
  scripts/run_real_pipeline.py), and the code workflow is not on this branch (it lives in the lease's x clone, which
  this session does not touch). Every other method runs.
- Same reporting as X5: results/search/new_settings/, not part of the registered S1-S4 verdicts.
- On 32 plans, budgets 1/2/5/10% all equal the 4-plan minimum (B = 4/4/4/4/6).

## 2026-11-18 ~05:25Z: X6 hotpot_q7_32 added (merge 46492c6a)
- EXTRA setting hotpot_q7_32 (X6, Qwen2.5 7B -> 32B, hotpot workflow, 5 agents, 32 plans, 400 eval problems), priced
  by tier name like the other X settings. All 14 methods run. Reported under New settings.

## 2026-11-18: exploratory size-priced variant (X3, X6, X7); registered S6(a) untouched
- Request: X3's tiers are different families (Qwen2.5-7B / Granite-3.1-8B / Phi-4 14B), so tier-name pricing makes
  Granite ~20x Qwen 7B. Variant "<setting>@size": per-token rate = main-table large rate x params / 7 (Qwen 7B =
  large; Granite 8/7; Phi-4 14/7; Qwen 32B 32/7; Coder 1.5B 1.5/7; Coder 7B 1). Each tier runs exactly one model in
  each setting (asserted from h3_calls), so it is a per-tier price table, used for both the plan costs (h3_calls)
  and the surrogates' label cost terms (label_terms reads Setting.prices), so the methods see the same cost model.
- Phi-4's size (14B) is not in its model id; SIZE_B lists all six model sizes explicitly (unknown model = KeyError).
- Refactor check: calls_cost now returns (costs, prices) and s6.part_a takes (name, out) with the registered values
  as defaults. Re-running the registered S6(a) after the refactor reproduced s6a_cells.csv byte-identically.
- Tier-priced X3 (all 14 methods via run_search) added to results/search/new_settings (it had only S6(a) before).
- Results: results/search/exploratory/size_priced/ (SIZE_PRICED.md, results.csv, s6a_*.csv), labelled
  "exploratory: size-priced".

## 2026-11-18 ~07:10Z: X6 math500_q7_32 added (merge 613abcd2)
- EXTRA setting math500_q7_32 (X6, Qwen2.5 7B -> 32B, MATH-500, 64 plans, 300 problems), tier-priced under New
  settings and size-priced (32/7) under the exploratory size-priced section. X6/latency also landed; not used
  (latency truth stays X1 + latsim for the 11 registered settings; no latsim prediction exists for X6).

## 2026-11-18 ~07:50Z: X8 landed (merge 318358bf); S5b run once: HELD
- X8 at the frozen path results/v2/X8/complex_q15_7/plans/h3_plans.csv, all 1,024 plans scored (X8 reuses P2c's
  labels, per its LABELS.txt). s5b.py and methods.py unchanged since search-prereg-s5b-20261118T0336Z; the
  ground_truth/surrogates changes since the tag only touch EXTRA and "@size" settings (prices None for complex_q15_7).
- Result: retention 0.9751 for both nsga2_pairwise_m3 and nsga2_active_m3 (>= 0.95: HELD); X8 HV / best X8 front HV
  0.9542. Cross-check: the tagged code, run from a scratch worktree on the same X8 file, gave identical per-run rows.

## 20261118T1353Z: S5c registered (docs/search_prereg_s5c.md, tag search-prereg-s5c-20261118T1353Z)
- Written and tagged before any X9 file exists on v2-lease1 or locally. scripts/search/s5c.py is s5b.py with the
  setting (math_tiers), data folder (X9) and labels changed; s5b.py itself untouched. It refuses to read X9 without
  the tag. One dry run on the eval file (retention 1.0) checked the pipeline.

## 20261118T1418Z: S5d registered (docs/search_prereg_s5d.md, tag search-prereg-s5d-20261118T1418Z)
- Written and tagged before any X11 file or X11 amendment exists on v2-lease1 or locally.
- Choice: "HELD if retention >= 0.95 in both" read as in S5: the decision cell is nsga2_pairwise_m3 at 10% (mean over
  30 seeds) per setting; all registered methods and budgets are re-scored and reported. X11 path registered as the
  glob results/v2/X11*/<setting>/plans/h3_plans.csv since no amendment names it yet.
- scripts/search/s5d.py refuses to read X11 without the tag. One dry run on the eval files (retention 1.0) checked it.
