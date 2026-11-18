# AgentQO v2 search — S6 confirmatory pre-registration

Registered: 2026-11-18T00:54:09Z (UTC). Tag: `search-prereg-s6-20261118T0054Z` (the commit it points to freezes the code below).
Branch v2-search. Earlier registration: search-prereg-20261117T2127Z (S1-S5, unchanged).

## Hypothesis

**S6:** active-learning NSGA-II (settings frozen exactly as in the exploratory run) has higher hypervolume than
Abacus-style (next-best fill) at budgets 2, 5 and 10% on
(a) X3 cross-family (729 plans), and
(b) a fresh simulated sweep with seeds 1000-1029 at 20 and 30 agents, interaction scale 1x and 2x, B = 100 and 200.
Decision: paired 95% CI above the tie threshold. Also report strict HV (above all_small).

(The 2/5/10% budgets apply to (a); (b) uses B = 100 and 200 as stated.)

## Decision rule (scripts/search/s6.py)

- Per cell, paired by seed: d = HV ratio(active) - HV ratio(Abacus-style next-best). 95% t-interval over the 30
  seeds. PASS if the lower bound > tau = 0.0134 (the X4-derived tie threshold in docs/search_log.md).
- HV ratio as registered for S1-S4: cost / max plan cost, reference (cost 1, accuracy 0). Real setting: true front
  over all 729 plans. Simulation: reference = oracle NSGA-II front (pop 200, 300 generations) united with every
  method's verified plans in the same run (nsga2_pairwise, nsga2_independence, abacus random-fill,
  abacus_nextbest, greedy_uv, random, nsga2_active), as in the exploratory sweep.
- S6(a) HELD if all 3 cells (2, 5, 10% -> B = 15, 36, 73) PASS; S6(b) HELD if all 8 cells PASS; PARTIAL if some;
  FAILED if none. Strict HV (reference accuracy = all_small's true accuracy) is reported, not used to decide.
- Seeds: (a) 0-29 (numpy default_rng(seed)); Abacus-style is deterministic. (b) 1000-1029; instance stream
  np.random.default_rng([n, seed, 2026]) (agentqo/search/scalability.py inst_rng), so no confirmatory instance shares
  a stream with an exploratory one; search streams default_rng(seed).

## Frozen methods (code at this tag)

Active-learning NSGA-II
- Real settings: agentqo/search/methods.py run_active (registered as nsga2_active_m3). Surrogate pairwise_corrected
  m = 3: label-UV single terms; measured all_small as base; pair plans of the top-3 label-UV options (same-agent
  pairs dropped), at most floor(B/2) - 1; all charged to B. 4 rounds; round k verifies ceil(left / (4 - k)) new
  plans in the surrogate's non-dominated order, spread along predicted cost; after each round a ridge (lambda 1,
  primal) on the residual truth - surrogate over indicators of every cross-agent option pair, fitted on all
  verified plans. NSGA-II: population 40, 50 generations, binary tournament, uniform crossover 0.9, per-gene
  mutation 1/n; one default_rng(seed) across rounds.
- Simulation: agentqo/search/scalability.py run_active_syn. Same, except the top-3 option pairs are all
  measured (no cap) and the ridge is solved in dual form (same estimator).
Abacus-style, next-best fill
- Real settings: methods.run_abacus. Independence-additive estimate (label terms) for every plan (exact
  enumeration); verify successive non-dominated layers of the estimate, spread along estimated cost within the
  last layer needed. (This is how the registered abacus already filled its budget on the real settings.)
- Simulation: scalability.abacus_layers + pick: exact layers 1..L of the independence estimate by layered Pareto
  DP (verified equal to brute force on a 3^6 instance), L the smallest with >= B plans; then the same pick.

## X3 data (part (a))

- Setting x3_cross_family: workflow math (6 agents), tiers small = Qwen2.5-7B, large = Granite 8B, xl = Phi-4
  (3^6 = 729 plans, split eval_ext, 200 problems per results/v2/X3_vmB/plans/run_config.v2.json).
- Accuracy: results/v2/X3_vmB/plans/h3_plans.csv (and h3_per_problem.csv). API cost: h3_calls.csv(.gz) priced
  by tier name with agentqo.metrics.cost_model.price_plans and configs/v2_prices.yaml (this reproduces P6's
  math_tiers api_usd exactly: max abs diff 0.0 over 729 plans). Labels: large = X3_vmB/labels_q7_G8,
  xl = X3_vmB/labels_q7_P4 (base accuracy from the large-tier label run), as for math_tiers.
- X3 files on origin/v2-lease1 at registration (111a0b3d): X3_vmB/labels_q7_G8/* and labels_q7_P4/* (labels_v2,
  by_strategy, per_problem, pipeline_summary, run_config, 2,808 h1 files), X3_vmB/plans/run_config.v2.json (the
  only file in plans/; no plan accuracies exist yet), X3_vmB/smoke/h3_{calls,per_problem,plans,summary,traces},
  X3_vmB/x3_run_note.txt.
- What I have read: only the two run_config.v2.json files (plans/ and labels_q7_G8/), for tiers/split/workflow.
  I have NOT opened any X3 accuracy file: not the smoke h3_plans/per_problem, not the label files, not
  x3_run_note.txt. Disclosure: earlier in this session STATUS.md lines were printed that contain the X3 smoke
  gate (all_small 0.6, all_large 0.6, all_xl 1.0 on the smoke problems) and "plans 40/200 problems when paused";
  no X3 plan accuracy was in them.
- If X3 lands under a different path or name, only the path in agentqo/search/ground_truth.py EXTRA changes,
  logged in docs/search_log.md before the run.

## State at registration

- The exploratory fairness check (sweep seeds 0-29 with abacus_nextbest added) has NOT been run yet; it runs
  after this tag. The confirmatory sweep (b) runs after this tag, once, with the code at this tag.
