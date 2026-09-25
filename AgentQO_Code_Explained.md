# AgentQO Code, Explained Simply

Repository: `github.com/Shusmoy108/AgentQO`, commit `c22a74f` (2026-09-21).
Every file below was read directly from this commit.

---

## 1. The whole project in one paragraph

AgentQO asks one question: when many AI agents work together on a task, which
agent's mistakes hurt the final answer the most, and can we spend GPU money on
those agents first? The code builds a small pretend world where agents solve
tasks, breaks one agent on purpose to see how much the final answer suffers
(that damage is called **epistemic criticality**, or EC), trains a small model to
guess EC without breaking anything, and then uses those guesses to decide which
agents get the expensive, more accurate model. A second part, the runtime,
acts like a live scheduler that places agent calls on GPUs as tasks arrive.

**An analogy.** Think of a kitchen. The head chef plans the meal, cooks prepare
dishes, a taster checks, and a server plates it. If the head chef misreads the
order, everything after is wrong. If the server plates it a little crooked,
almost nothing is lost. AgentQO measures which "cooks" matter most, learns to
predict it, and gives the best equipment to the ones who matter.

---

## 2. Real versus simulated (read this first)

Most of the code runs in a **simulator**. That is intentional: it lets you test
the ideas on a laptop before paying for GPUs. The labels below appear on every
file.

| Label | Meaning |
|---|---|
| [REAL] | Works the same with real LLMs. No pretending. |
| [SIM] | Pretend world. Numbers come from formulas, not real models. |
| [MIXED] | Real logic, but currently fed by simulated inputs. |

The single most important fact: **every quality score today comes from a
formula in `simulator/task_model.py`**, even when the vLLM backend is used.

---

## 3. How the pieces connect

```
 workflows/        builds the agent graph (who talks to whom)
     |
     v
 backends/  or  simulator/MockBackend      "runs" one agent, returns output,
     |                                     confidence, embedding, cost
     v
 executor.py       runs the whole graph in order, can force an agent wrong
     |
     v
 simulator/task_model.py                   scores the final answer (0 to 1)
     |
     v
 labeling/ec_labeler.py                    breaks each agent on purpose,
     |                                     measures the damage = EC   (H1)
     v
 predictors/       learns to GUESS EC from cheap clues             (H2)
     |
     v
 policies/allocation.py                    spends budget by guessed EC (H3)

 simulator/interaction_model.py + predictors/agenticonq.py
                   GPU crowding cost: how a call slows itself
                   and its neighbors                               (H4)

 runtime/          the live scheduler: tasks arrive, it picks edits,
                   model size, and GPU at every event
```

---

## 4. File by file

### 4.1 Top-level files

| File | What it is |
|---|---|
| `README.md` | Short guide. Lists what is real vs simulated, the commands to run, and the current results. Your own notes here are accurate. |
| `pyproject.toml` | Package definition. Says the code needs Python 3.10+, numpy, scipy, scikit-learn, tqdm; torch and matplotlib are optional. Registers pytest settings. |
| `requirements.txt` | The same dependencies as a flat list for `pip install -r`. |
| `.gitignore` | Tells git to ignore generated files (`data/`, caches, databases). |
| `AgentQO_Proposal.pdf`, `AgentQO_Presentation.pdf` | Your proposal and slides. Not code. |
| `AgentQO_Prototype_Implementation_Plan.md` | The earlier plan that guided this code. |
| `agentqo/vllm_gpu_path_b9f57eb9.plan.md` | A planning note for moving to vLLM on a GPU. Not code. |

### 4.2 `agentqo/__init__.py`

Just the package's front door. It has a description of the project and makes
`agentqo` importable. Nothing runs here.

### 4.3 `agentqo/workflows/`: building the agent graph [REAL]

**`dag.py`**: the core building blocks.
- `NodeRole`: the job an agent has: planner, researcher, aggregator, verifier,
  sampler, formatter.
- `Fidelity`: one way to run an agent. It has a cost and an error rate. The file
  defines two: `SMALL_FIDELITY` (cost 1, 30% error, pretend "7B") and
  `LARGE_FIDELITY` (cost 4, 5% error, pretend "70B", 2 GPUs). These numbers are
  made up for the simulator.
- `NodeSpec`: one agent: its id, role, which agents feed it, whether it is
  optional (can be skipped) or speculative (a spare copy, like one of five
  attempts).
- `Workflow`: the whole graph. It can answer questions like "who comes after this
  agent?" (descendants), "how deep is it?", "how many agents depend on it?"
  (fan-out, downstream reach), and "is there a checker after it?". It also
  refuses graphs with loops.
- `WorkflowBuilder`: a convenient way to assemble a graph step by step.

**`library.py`**: ready-made graphs.
- `create_math_reasoning_workflow`: planner, then step 1, step 2, step 3 in a
  chain, then an aggregator, then an optional verifier. Like solving a word
  problem one step at a time.
- `create_multihop_qa_workflow`: a planner sends several researchers out in
  parallel, then an aggregator combines their findings.
- `create_self_consistency_workflow`: several samplers each solve the whole
  problem; the answer is right if any of them is right. Extra samplers are
  optional so the runtime can add or drop them.
- `create_complex_workflow`: a mix of the above plus a formatter at the end.
- `create_refinement_workflow`: draft, critique, revise, repeated, with rounds the
  runtime can stop or extend.

**`__init__.py`**: re-exports these names.

### 4.4 `agentqo/backends/`: who actually "runs" an agent

**`base.py`** [REAL]: the contract every runner must follow.
- `NodeResult`: what running one agent gives back: the output, whether it was
  correct, a confidence number, an embedding (a list of numbers describing the
  agent's internal state), the cost, and which fidelity was used.
- `ModelBackend`: the promise: "give me an agent and a fidelity, I give you a
  `NodeResult`". Anything that keeps this promise can be swapped in.

**`vllm_http.py`** [MIXED]: the real LLM runner.
- Talks to a vLLM server over HTTP (the same format as OpenAI's API).
- Picks the small or large model name based on fidelity.
- Builds a simple prompt: "Role: planner. Instructions: ...".
- Turns token probabilities (logprobs) into a confidence score. If the server
  gives no logprobs, it quietly uses 0.5.
- **Correctness:** it only knows if an answer is correct when you pass a scorer
  function. Otherwise it marks it wrong and flags "unknown".
- **Embedding:** not a real model embedding yet. It hashes the output text into
  numbers (`_placeholder_embedding`). Good for plumbing, meaningless for H2.
- `health_check` asks the server if it is alive.

**`vllm_backend.py`**: an old name kept so older imports still work. It just
points to `vllm_http.py`.

**`__init__.py`**: re-exports.

### 4.5 `agentqo/simulator/`: the pretend world [SIM]

**`task_model.py`**: the heart of the simulator. Two jobs.

*Job 1, the "quality channel": decides how good the final answer is.*
- `TaskInstance`: one pretend problem. It carries **hidden** values the rest of
  the system must never peek at: how important each agent is
  (`node_importance`) and how hard each agent's step is (`node_difficulties`).
  The "right answer" is a random number.
- `_hidden_importance`: gives each agent an importance based on its position and
  role, plus random noise, so importance is related to structure but not a copy
  of it.
- `MathReasoningTaskModel`: final quality adds up the importance of every correct
  agent, but an agent's contribution shrinks if something before it was wrong
  (`_ancestor_survival`). A correct verifier can recover part of the loss.
  Formatters are forced to matter almost nothing.
- `MultiHopQATaskModel`: similar idea for parallel researchers.
- `SelfConsistencyTaskModel`: the group of samplers counts as right if **any**
  sampler is right.
- `task_model_for_workflow`: picks the right scoring rule for a graph by name.

*Job 2, `MockBackend`: a fake LLM.*
- Decides if an agent is correct by rolling dice against an error rate that
  depends on fidelity and hidden difficulty.
- Makes a noisy confidence number.
- Makes an embedding where the first 16 numbers lean toward hidden importance,
  the next 16 toward hidden difficulty, and a few toward correctness, mixed
  with noise. **This is why the predictor can learn EC in the simulator: the
  answer is partly planted in the embedding.** Real embeddings will have to earn
  that signal.

**`interaction_model.py`**: a pretend GPU for H4.
- `CallSpec`: one LLM call: which model, which GPU, how many prompt and output
  tokens, and a prefix id (calls with the same prefix share their starting text).
- `simulate_batch`: for calls sitting on the same GPU, computes (a) each call's
  own slowdown from crowding and (b) the delay it pushes onto its neighbors.
  Calls sharing a prefix get a discount, because the shared part only has to be
  processed once. Calls on different GPUs never affect each other.
- `generate_interaction_dataset`: makes many random batches to train H4 on.

### 4.6 `agentqo/executor.py`: running a whole graph [REAL logic, SIM scoring]

- `FidelityPlan`: which agents use small and which use large.
- `ExecutionOverrides`: instructions to tamper with a run: force an agent to be
  correct or wrong, force its output text, or skip it.
- `WorkflowExecutor.run_workflow`: runs agents in dependency order, passes each
  agent's output to the ones after it, adds up cost, then asks the task model for
  the final quality.
- `run_with_partial_recompute`: reruns only the agents after a chosen agent and
  reuses everything before it. This is what makes fault injection cheap.
- `verify_partial_recompute_invariant`: a safety check that agents before the
  tampered one really stayed identical.
- `_apply_overrides`: applies the tampering **after** the agent runs. Note: to
  "force wrong" it flips the correct/incorrect flag but does not change the text.
  In the simulator that is fine. With a real LLM the next agent reads the text,
  so it would never see the error.

### 4.7 `agentqo/labeling/ec_labeler.py`: measuring EC (H1) [SIM today]

- For every agent on every pretend task:
  1. Run the task normally.
  2. Force this agent correct, rerun what comes after, record quality (Q+).
  3. Force this agent wrong, rerun what comes after, record quality (Q-).
  4. Damage = Q+ minus Q-. That is the **consequence**.
  5. How often this agent is wrong on its own = **p_err**.
  6. **EC = consequence x p_err**.
- `compute_bootstrap_ci`: resamples the results many times to get a range of
  uncertainty for each number.
- `analyze_h1_results`: declares H1 passed if damage varies a lot across agents
  (range above 0.1 and spread above 0.2).
- `_h1_smoke_test`: a common-sense check: breaking a planner or aggregator must
  hurt more than breaking a formatter.

### 4.8 `agentqo/predictors/`: guessing EC and GPU cost

**`features.py`** [REAL]: turns an agent into numbers a model can learn from.
- Structural clues: role, depth, fan-out, downstream reach, checker after it,
  optional or speculative.
- Plus the embedding and confidence from a run.
- `average_features_over_runs`: averages several runs to reduce noise.

**`ec_predictor.py`** [REAL logic]: the H2 contestants.
- `GBTECPredictor`: gradient-boosted trees on structure + embedding. This is
  "AgentQO".
- `MLPECPredictor`: a small neural network, in the style of TRAIL. Uses PyTorch if
  installed, otherwise scikit-learn.
- `ConfidenceBaseline`: guesses EC from confidence only.
- `StructureOnlyBaseline`: guesses EC from graph position only.
- `analyze_h2_results`: H2 passes if AgentQO ranks agents better than confidence
  alone.

**`agenticonq.py`** [REAL logic, trained on SIM data]: the H4 contestants.
- `AgentIconqPredictor`: two small tree models: one guesses a call's own latency,
  the other guesses the delay it causes neighbors.
- `SingleCallBaseline`: ignores crowding entirely.
- `AdditiveBaseline`: a crude rule: more neighbors, proportionally slower.
- `q_error`: how far off a guess is, as a ratio (1.0 means perfect).

### 4.9 `agentqo/experiments/`: glue for fair experiments [REAL]

- `suite.py`: the standard set of test graphs (math 3 and 5 steps, QA 3 and 5
  researchers, self-consistency 3 and 5, complex with formatter). Quick mode uses
  four of them. It refuses duplicate names, so train and test can't mix by
  accident.
- `dataset.py`: turns labels into training rows, and splits them
  **leave-one-workflow-out**: train on some graphs, test on a graph never seen.
  This is the honest test of whether the predictor generalizes.
- `scoring.py`: `predict_node_scores` runs a few cheap probe runs, averages the
  embeddings, and asks a trained predictor for EC guesses on every agent. This is
  how H3 gets predicted EC.

### 4.10 `agentqo/policies/allocation.py`: spending the budget (H3) [MIXED]

- Everyone starts on the small model. Given a budget, upgrade agents to the large
  model, highest value per unit of cost first.
- Policies compared: `ECPolicy` (by predicted EC, this is AgentQO),
  `ConfidencePolicy` (least confident first), `UniformPolicy` (random),
  `OracleECPolicy` (by true measured EC, a best-possible reference),
  `AllSmallPolicy`, `AllLargePolicy`.
- `compute_quality_cost_curve`: for several budgets, runs each policy and records
  quality and cost.
- `analyze_h3_results`: H3 passes if the EC policy's area under the quality-cost
  curve beats confidence and uniform.

### 4.11 `agentqo/runtime/`: the live scheduler [MIXED]

This is the part that acts like a real serving system. Tasks arrive over time;
at every event (a task arrives, a call finishes) it makes decisions.

**`cluster.py`**: a pretend group of GPUs.
- Each `GPU` has calls running on it, stored KV cache regions (saved work that
  can be reused), and memory in use.
- `physical_cost`: for a candidate call on a GPU, returns its own latency, the
  delay it would push onto the calls already there, and a total cost that also
  counts moving saved state between GPUs and credit for reusing it.
- `admit`, `complete`, `next_completion`: start calls and advance the pretend
  clock to the next finish.
- `store_kv`, `evict_kv`: keep or drop saved state.

**`edits.py`**: the small set of plan changes the scheduler may make.
- `noop` (change nothing), `set_fidelity` (small or large model for an agent),
  `skip_optional` and `admit_optional` (drop or add optional work),
  `set_verifier` (turn a checker on or off), plus changes to the number of
  speculative copies and to refinement loops.

**`scores.py`**: the scoring formulas from your proposal.
- `expected_quality`: a quick estimate of how good the current plan is.
- `marginal_edit_value`: how much an edit changes that estimate.
- `kv_value`: how much saved state is worth keeping: chance of reuse x cost to
  recompute x (1 + importance of its owner).
- `branch_index`: whether a speculative copy is still worth its cost; drops as
  the copies start agreeing.
- `risk_term`: penalty for important work sitting on a crowded GPU.

**`optimizer.py`**: `JointOptimizer.decide` tries every allowed edit combined with
every GPU, scores each pair as "expected quality minus latency, cost, and risk
penalties", and picks the best. This is equation 6 of your proposal.

**`system.py`**: the main loop.
- `AgentQO.serve`: takes a list of task arrivals, repeatedly: admit new tasks,
  ask the optimizer for a decision, dispatch ready agents to GPUs, and process
  completions. It also stops low-value speculative copies and evicts low-value
  saved state.
- Two comparison schedulers: `FCFSFixed` (first come, first served, everything
  small, least busy GPU, no edits) and `FixedPlanEC` (uses EC to pick model size
  and placement, but never changes the plan).
- Two important details: when it dispatches an agent, it calls the backend right
  away, but the **clock and GPU time come from the pretend cluster**, and token
  counts are fixed guesses. So even with vLLM, the timing numbers are simulated.

### 4.12 `agentqo/metrics/`: numbers and pictures [REAL]

- `ranking.py`: Spearman and Kendall correlation (do two lists agree on order?),
  top-k precision and recall, NDCG. Used for H2.
- `quality_cost.py`: quality per cost, the Pareto frontier (the best trade-offs),
  area under the quality-cost curve. Used for H3.
- `figures.py`: draws the H1 bar chart, H2 ranking chart, H3 curves, H4 chart.
  Works without matplotlib by skipping figures.
- `io.py`: writes CSV and JSON files.
- `report.py`: assembles summary reports for H1 to H3.

### 4.13 `agentqo/database.py`: optional storage [REAL]

A SQLite database that can save tasks, runs, EC labels, experiments, and
predictions, and turn numpy arrays into storable bytes and back. The main
scripts write CSV and JSON instead; this is available for larger runs.

---

## 5. Scripts: what happens when you run them

| Script | What it does | What you see |
|---|---|---|
| `run_h1_labeling.py` | Breaks every agent in every suite graph, measures damage, computes EC with uncertainty ranges | Per-agent consequence table, H1 PASS/FAIL, bar chart |
| `run_h2_predictor.py` | Uses H1 labels, trains the predictors, tests on unseen graphs | Spearman per graph for AgentQO vs confidence vs structure, H2 PASS/FAIL |
| `run_h3_allocation.py` | Runs every budget policy at several budgets | Quality-cost curves, area under curve per policy, H3 PASS/FAIL |
| `run_h4_agenticonq.py` | Makes pretend GPU batches, trains AgentIconq and baselines | Error table, H4 PASS/FAIL |
| `run_demo.py` | Runs H1, then H2, then H3, then H4 with shared labels. `--quick` for a small version | All four summaries in one go |
| `run_agentqo.py` | Runs the live scheduler vs FCFS vs FixedPlan-EC on arriving tasks | Quality, completion time, quality per GPU, edits used |
| `run_vllm_smoke.py` | Checks a running vLLM server answers for the small and large model | OK or a clean error message |

**Current results (from running the code):** H1, H2, H4 pass in quick mode; H3
fails in quick mode. In the runtime, AgentQO finishes fastest but has lower
quality than FCFS on 3 of 4 graphs.

---

## 6. Tests: what each one checks

| Test file | Checks |
|---|---|
| `test_dag.py` | Graphs are built correctly: order, descendants, depth, fan-out, loops rejected, bad links rejected, library graphs have the expected shape |
| `test_executor_overrides.py` | Runs are repeatable with the same seed; forcing an agent right or wrong works; rerunning after an agent leaves the earlier agents untouched; a planner error hurts |
| `test_fault_injection.py` | Uncertainty ranges behave; EC labels are valid; damage varies across agents; important agents cause more damage |
| `test_quality_channel.py` | Honesty checks: graph names are unique, train and test never share a graph, formatter errors barely matter, importance is not just a copy of structure, self-consistency uses "any correct", embeddings do not simply copy structure |
| `test_agenticonq.py` | Crowding slows calls; shared prefixes help; different GPUs don't interact; AgentIconq beats the single-call baseline |
| `test_agentqo_runtime.py` | The scheduler finishes workflows; skipping optional work doesn't deadlock; loops are editable; KV value grows with EC; branch value drops as copies agree; co-located calls have nonzero crowding cost |
| `test_vllm_backend.py` | The vLLM client works against a fake HTTP server: picks the right model, uses a scorer, handles errors, computes confidence, placeholder embedding is repeatable |

All 66 tests pass.

---

## 7. Follow one run through the code: `run_demo.py --quick`

1. `experiments/suite.py` builds four graphs and gives each a scoring rule from
   `simulator/task_model.py`.
2. For each graph, `labeling/ec_labeler.py` asks the task model for pretend
   problems. Each problem secretly carries importance and difficulty per agent.
3. `executor.py` runs the graph with `MockBackend`. For each agent, the mock
   rolls dice for correctness, makes a confidence number, and makes an embedding
   that leans toward the hidden importance.
4. The task model turns "who was correct" into a final quality score.
5. The labeler forces each agent right, then wrong, reruns only what comes after,
   and records the damage. EC = damage x how often the agent is wrong. **H1
   done.**
6. `experiments/dataset.py` turns labels into rows and holds out one graph at a
   time. `predictors/features.py` builds the clues. `predictors/ec_predictor.py`
   trains AgentQO and the baselines and compares their rankings on the held-out
   graph. **H2 done.**
7. `experiments/scoring.py` gets predicted EC for each agent.
   `policies/allocation.py` spends budgets by predicted EC, confidence, and
   random, and measures quality and cost. **H3 done.**
8. `simulator/interaction_model.py` makes pretend GPU batches;
   `predictors/agenticonq.py` learns crowding costs. **H4 done.**
9. `metrics/` writes the tables and figures into `data/demo/`.

## 8. Follow one run through the code: `run_agentqo.py`

1. The script makes a list of task arrivals over time, and scores each agent's EC
   with a simple rule (how many agents come after it).
2. `runtime/system.py` starts a pretend cluster of GPUs (`cluster.py`).
3. At each event, `optimizer.py` tries every allowed edit (`edits.py`) on every
   GPU, scores them with `scores.py` and the cluster's crowding cost, and picks the
   best.
4. Ready agents are sent to GPUs; the backend produces a result right away; the
   pretend clock decides when they finish.
5. When a task finishes, the task model scores it.
6. The same arrivals are run through FCFS and FixedPlan-EC, and the three are
   compared.

---

## 9. What this means for moving to real LLMs

The graph, executor, labeling logic, predictors, policies, metrics, and tests are
real and reusable. Four things are still pretend and must be replaced before real
results mean anything (all covered in `AgentQO_RealModel_Test_Plan.md`):

1. **Scoring:** quality comes from a formula with hidden importance, not from
   checking the real answer against a real dataset.
2. **Breaking an agent:** it flips a flag, not the text the next agent reads.
3. **Embeddings:** the vLLM backend hashes text instead of reading the model's
   internal state.
4. **Runtime timing:** the clock and GPU time are simulated, and the runtime's EC
   comes from a simple rule instead of the trained predictor.

---

## 10. Glossary

| Term | Plain meaning |
|---|---|
| Agent / node | One LLM call with a job (plan, research, check, format) |
| Workflow / DAG | The graph of agents and who feeds whom |
| Fidelity | Which model runs an agent: small (cheap, more mistakes) or large (costly, fewer mistakes) |
| Descendants | All agents that come after a given agent |
| Fault injection | Breaking one agent on purpose to see what happens |
| Consequence | How much the final answer drops when that agent is wrong |
| p_err | How often that agent is wrong on its own |
| EC (epistemic criticality) | consequence x p_err: how much that agent's mistakes cost you |
| Embedding | A list of numbers describing an agent's internal state |
| Confidence | How sure the model seems about its own output |
| Leave-one-workflow-out | Train on some graphs, test on a graph never seen |
| Spearman | A score from -1 to 1 for whether two rankings agree |
| Budget / allocation | How many agents get upgraded to the large model |
| Oracle | Using the true answer, as a best-possible reference only |
| KV cache | Saved intermediate work on a GPU that can be reused |
| Prefix | The shared starting text of several prompts |
| Co-location / externality | Calls sharing a GPU slow each other; the delay pushed onto others is the externality |
| Speculative branch | A spare attempt (like one of five tries) that can be cancelled |
| FCFS | First come, first served: the simple baseline scheduler |
