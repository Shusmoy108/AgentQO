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
