# AgentQO Prototype: Implementation Plan

Shusmoy Chowdhury. Engineering plan for a prototype that demonstrates the
novel claims of the AgentQO proposal. TRAIL is used only as a reference for how
Dr. Liu's group writes, tests, and evaluates systems. The novelty here is my
own: epistemic criticality as a schedulable resource, a two-sided interaction
cost model for agent batches, and value-aware allocation over a workflow DAG.

## 0. What this prototype proves, and what it is not

The prototype must produce evidence for three claims from the proposal, in order
of importance:

1. H1. Downstream importance varies across nodes in a workflow. Corrupting some
   nodes wrecks the final answer, corrupting others barely changes it. If this
   is false there is nothing to schedule on.
2. H2. That importance, which I call epistemic criticality (EC), can be
   predicted cheaply, before a node finishes, better than a confidence-only or
   structure-only baseline.
3. H3. Spending GPU resources by predicted EC gives more task quality per unit
   of GPU cost than spending uniformly or by confidence.

A fourth claim is the systems half and comes after the three above hold:

4. H4. A two-sided interaction cost model (AgentIconq) predicts both a call's
   own latency under load and the delay it imposes on already-running calls,
   including the case where shared prefixes make co-location cheaper.

What this prototype is not: it is not the full AgentQO optimizer, not joint
runtime graph rewriting, and not a production serving system. Those are later.
The prototype is the smallest thing that can prove or kill the core idea.

## 1. Relationship to TRAIL (reference only)

TRAIL recycles a layer embedding into a light classifier to predict one thing:
remaining output length, for single-stream SRPT scheduling. I borrow its style,
not its target:

- style I reuse: recycle an internal embedding as a cheap feature; train a small
  model; compare against a prompt-only baseline; measure predictor overhead;
  evaluate with clear error and ranking metrics; keep everything reproducible
  with saved splits.
- what is different and novel: the unit is a workflow DAG, not a single request;
  the predicted quantity is a value signal (EC) and a two-sided cost, not a
  length; and the scheduler spends resources by value, not only by size.

The prototype does not depend on TRAIL's code to run. It can adopt TRAIL's exact
predictor and timing scripts later when moving to real models, but the novel
logic stands on its own.

## 2. Design principles

1. Simulator first, then hardware. The proposal endorses this. A simulator with
   a quality channel lets me measure EC and test allocation on a laptop, then
   swap in real models without changing the AgentQO logic.
2. The model backend is an interface. AgentQO calls a backend to run a node and
   get back an output, a correctness signal (for labeling and evaluation only),
   a confidence, a recycled embedding, and a cost. A mock backend fills these
   from the simulator; a real backend fills them from a served model. Swapping
   backends is the only change needed to go from sim to hardware.
3. Data first, models second. Every run and every EC label is written to disk in
   a plain schema so any analysis can be redone without re-running anything.
4. The executor supports forced node outputs and descendant-only recompute, so
   fault-injection labeling is correct and cheap.
5. Each experiment (H1 to H4) is a separate script with an explicit success and
   stop threshold. The prototype is a test, not a demo.

## 3. The quality channel: why the simulator is honest

The reason current agent-serving simulators cannot test EC is that they model
latency and memory but not task outcome. This prototype adds a quality channel:
a ground-truth mapping from which nodes are correct to a final task quality.
Design requirements so the result is meaningful and not circular:

- Final quality degrades as important nodes fail, and importance differs across
  nodes and correlates with structural position (fan-out, downstream reach,
  role) plus noise. This makes H1 non-trivial and makes structure a real but
  incomplete predictor.
- A node's error probability depends on its fidelity (small or large model) and
  a hidden difficulty. Confidence is informative about local correctness but is
  not the same as criticality. A node can be low-confidence yet low-criticality,
  or the reverse. That gap is exactly what AgentQO exploits, and it is why the
  confidence-only baseline should lose.
- Speculative groups (best-of-N, self-consistency) count as correct if any
  branch is correct, so the value of one more branch has diminishing returns.

When moving to real models, the quality channel is replaced by the real task
benchmark score (GSM8K exact match, HotpotQA exact match and F1), and the EC
labels come from real fault injection instead of the simulator. The AgentQO code
does not change.

## 4. Core abstractions

- Fidelity: a (cost, base error rate) option for a node. Small is cheap and
  error-prone; large is costly and reliable.
- NodeSpec: node_id, role (planner, researcher, verifier, aggregator, sampler),
  inputs, flags optional and speculative, a group id for speculative branches,
  and a list of fidelities. The optional and speculative flags are what let the
  scheduler add, skip, or cancel work, which single-stream systems cannot do.
- Workflow: the DAG plus graph helpers (topological order, descendants, fan-out,
  downstream reach, depth, has-downstream-verifier, speculative groups).
- NodeResult: output, correctness (sim or eval only), confidence, recycled
  embedding, cost, fidelity.
- RunRecord: final quality, total cost, per-node results, cancelled set.
- ECLabel: per node, the measured consequence with a bootstrap confidence
  interval, the local error probability, and EC.

## 5. Components to build, in order

### 5.1 Workflow DAG and library
The DAG data structures and two example workflows: a planner to researchers to
aggregator to optional verifier chain, and a self-consistency workflow with k
speculative sampler branches feeding an aggregator. These two cover the patterns
the proposal cares about (fan-out, verification, redundancy).

Definition of done: graph helpers return correct descendants, fan-out, reach,
and speculative groups on both workflows, checked by unit tests.

### 5.2 Backend interface and mock backend
The ModelBackend protocol and a MockBackend that runs a node against the quality
channel. The mock backend emits a recycled embedding aligned to the hidden EC
signal plus noise, so a learned predictor can recover EC from it while confidence
cannot. Real backends (vLLM, an API) are stubs with the same signature.

Definition of done: running any node returns a NodeResult; results are
reproducible for a fixed seed.

### 5.3 Executor with overrides
Run a workflow under a chosen per-node fidelity plan, with optional skipping of
optional nodes, forced correctness for chosen nodes, and descendant-only
recompute when only a subgraph changes. This one function serves both baseline
runs and fault injection.

Definition of done: a forced output at node v changes v and only its
descendants; upstream results are byte-identical to the baseline; verified by a
unit test.

### 5.4 Fault injection and EC labeler (H1)
For each node, pin it correct, then incorrect, re-run only its descendants, and
take the quality gap as the downstream consequence. Average over many tasks
(seeds), report a bootstrap confidence interval, and combine with the measured
local error probability to get EC. The distribution of consequence across nodes
is the H1 result.

Definition of done: an ec_labels table with consequence, confidence interval,
p_err, and EC per node, over at least a few hundred tasks; the H1 histogram.

### 5.5 Feature extraction
Two views: structural features (role one-hot, depth, fan-out, downstream reach,
has-downstream-verifier, optional, speculative), and the recycled embedding, plus
a single confidence scalar. The AgentQO predictor uses structure plus embedding;
baselines use structure only or confidence only.

Definition of done: feature vectors of fixed length for every node.

### 5.6 EC predictor and baselines (H2)
Train a small, robust regressor (gradient-boosted trees, which need no feature
scaling) to predict EC from structure plus the recycled embedding. Average the
embedding and confidence over a few runs, the way TRAIL averages over prompt
tokens, to denoise. Compare against structure-only and confidence-only.
Evaluate ranking quality (Spearman correlation with true EC, and precision on
the top fraction of nodes) with a train-on-some-workflows, test-on-unseen-
workflows split, which is the honest generalization test. Measure predictor
overhead so the cheapness claim is backed by a number, the way TRAIL reports its
Table 1.

Success for H2: AgentQO beats confidence-only clearly and is at least as good as
structure-only, ideally better because the embedding carries the hidden
difficulty signal that structure cannot see. If it cannot beat confidence, try
richer signals; if nothing beats confidence, report that as a negative result.

Definition of done: one table, three predictors, ranking metrics plus overhead;
the H2 figure.

### 5.7 Value-aware allocation and budget (H3)
Every node starts on the small fidelity. Given a per-node score and a fixed
budget, greedily upgrade the highest value-per-cost nodes to the large,
lower-error fidelity. Compare policies at equal budget: AgentQO (score is
predicted EC), confidence, uniform, and all-small. Sweep the budget and plot the
quality-versus-cost curve. This is the first end-to-end demonstration that
spending by value beats spending blindly.

Success for H3: AgentQO's curve sits above confidence and uniform at equal cost.

Definition of done: quality-versus-cost curves for four policies; the H3 figure.

### 5.8 AgentIconq two-sided cost (H4, later, real GPUs)
Measure, on a real serving stack, a call's own latency under a running set and
the extra latency it imposes on each already-running call, sweeping model, prompt
and decode length, batch composition, prefix sharing, and GPU type. Include
shared-prefix cases so the model can learn positive reuse, not only contention.
Train a predictor for both targets and evaluate with absolute error and Q-error,
the metrics IconqSched and TRAIL use, against a single-call baseline and a naive
additive baseline.

Success for H4: AgentIconq beats both baselines and captures both signs of
interaction.

Definition of done: the two-sided prediction table and a plot showing contention
and reuse.

## 6. Repository layout

```
agentqo_proto/
  README.md
  agentqo/
    workflows/
      dag.py            # Fidelity, NodeSpec, Workflow, graph helpers
      library.py        # example workflows
    backends/
      base.py           # ModelBackend protocol, NodeResult
      vllm_backend.py   # stub for real serving (later)
    simulator/
      task_model.py     # quality channel + MockBackend
    executor.py         # run_workflow with overrides and subgraph recompute
    labeling/
      ec_labeler.py     # fault injection, consequence, EC, bootstrap CI
    predictors/
      features.py       # structural + embedding features
      ec_predictor.py   # train and evaluate EC ranking vs baselines
      agenticonq.py     # two-sided cost model (H4)
    policies/
      allocation.py     # value-aware allocation + budget
    metrics/
      ranking.py  quality_cost.py  report.py
  scripts/
    run_h1_labeling.py
    run_h2_predictor.py
    run_h3_allocation.py
    run_demo.py         # all three, writes figures
  tests/
    test_dag.py  test_executor_overrides.py  test_fault_injection.py
  data/                 # runs, labels, figures (gitignored)
```

## 7. Reproducibility and metrics

- One global seed control; every run and label carries its seed. Train and test
  splits are by workflow instance and saved, so results are reproducible and the
  generalization test is honest.
- Metrics: consequence distribution and confidence intervals (H1); Spearman and
  top-k precision plus predictor overhead (H2); quality and quality per GPU cost
  as a quality-versus-cost curve (H3); absolute error and Q-error (H4).
- Every experiment writes a CSV of numbers and a PNG figure named by config, so
  the meeting artifacts are one folder.

## 8. Sanity tests

- Corrupting a node the final answer clearly depends on lowers quality;
  corrupting a pure formatting node barely changes it. This is the built-in
  smoke test for H1 and it should pass before any plot is trusted.
- Override at v leaves all non-descendants identical to baseline.
- The EC predictor with more features never scores worse than a strict subset of
  those features on the same split. If it does, the model or training is wrong,
  not the idea.

## 9. Build order and gates

| Step | Builds | Gate |
|------|--------|------|
| 1 | dag, library, backend interface, mock backend, executor, tests | overrides and graph helpers pass tests |
| 2 | ec_labeler, run_h1_labeling | H1: consequence varies across nodes |
| 3 | features, ec_predictor, run_h2_predictor | H2: beats confidence, at least matches structure |
| 4 | allocation, quality_cost, run_h3_allocation | H3: value allocation wins at equal cost |
| 5 | vllm_backend, real task scorers | same H1 to H3 on real models on one GPU |
| 6 | agenticonq, interaction profiling | H4: two-sided cost beats baselines (multi-GPU) |

Steps 1 to 4 need no GPU. Steps 5 and 6 use the GPU allocation Dr. Liu offered.

## 10. Decision gates and fallbacks

- After step 2, if consequence does not vary across nodes, stop the EC direction
  and lead with the two-sided cost model instead.
- After step 3, if EC cannot be predicted above the confidence baseline, try
  structural, disagreement, and verifier signals; if none help, write the
  negative result honestly and pivot.
- After step 4, if value allocation does not beat confidence and uniform, the
  fixed-plan value claim fails; fall back to AgentIconq as a standalone systems
  contribution.
- Each step yields a usable result on its own, so no single failure sinks the
  project. This staging is the point Dr. Liu already liked.

## 11. Path from simulator to real models

Only the backend and the label source change:
- backends/vllm_backend.py runs each node on a served model, returns the real
  output, a recycled layer embedding (the TRAIL hook), a confidence from
  logprobs, and a measured cost.
- correctness comes from the real task scorer, not the simulator.
- EC labels come from real fault injection on real outputs.
Everything in labeling, predictors, and policies is unchanged, which is why the
simulator work is not throwaway.

## 12. First week, concretely

1. Build the DAG, the two example workflows, the backend interface, the mock
   backend, and the executor with overrides; write the three unit tests.
2. Build the EC labeler and produce the H1 histogram on both workflows.
3. Build the feature extractor and the EC predictor with baselines; produce the
   H2 table and figure.
4. Build allocation and produce the H3 quality-versus-cost curves.

Walking into the meeting with H1, H2, and H3 figures from your own prototype,
plus this plan for moving to real models on his GPUs, is the goal.
