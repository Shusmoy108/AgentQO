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
