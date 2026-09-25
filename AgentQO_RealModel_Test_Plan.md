# AgentQO: Real-Model Test and Prototype Completion Plan

Repository audited: `github.com/Shusmoy108/AgentQO`, commit `c22a74f` (2026-09-21).
Audit performed by cloning the repo and running its tests, demo, and runtime.
Hardware target: Chameleon Cloud project CHI-251518 (8,000 SU visible).
Decisions (v3):
- Budget: finish the full prototype within 1,000 SU (hard cap), planned use
  about 600 SU (Section 7).
- Local tier: all debugging and small-scale real-model testing on a MacBook Pro
  (2023, 18 GB) with Ollama before any Chameleon lease (WP7b).
- Phase B and H4 on one H100 VM (`g1.h100.pci.1`, KVM@TACC, 4 SU/hour).
- Phase C (multi-GPU runtime only) on one bare-metal 4-GPU node (`gpu_a100` at
  CHI@UC or `gpu_h100` at CHI@TACC, 16 SU/hour), kept short.
- Models: Qwen2.5-1.5B-Instruct (small) and Qwen2.5-7B-Instruct (large).
- First update to Dr. Liu: real, explainable H1 to H3 (Section 13).

---

## 0. How to use this document

This plan is written so that a researcher or an AI coding assistant can finish
the prototype without guessing. Follow these rules.

1. Do the work packages (WPs) in order. Each WP lists its goal, the files to
   create or change, a specification, acceptance criteria, and commands.
2. A WP is done only when every acceptance criterion passes. Do not mark it done
   because the code runs.
3. Never let predictors, policies, or the runtime read simulator internals
   (`TaskInstance.node_importance`, `node_difficulties`). WP1 adds a test that
   enforces this.
4. Every experiment writes a CSV, a JSON summary, and a PNG under `data/`, and
   appends one entry to `RESULTS.md` (template in Appendix C).
5. When a gate fails, go to the tuning playbook (Section 9). Do not change the
   pass threshold after seeing the result.
6. Section 12 lists open questions. Each has a default so work is never
   blocked. If the answer differs from the default, update the affected WP.

---

## 1. Direct answers

**Do I need to deploy an LLM to test?** Yes, for results that count as real.
The current results are simulator results, which are valid only as evidence
that the method works as designed. To show real task quality, real criticality,
and real GPU interaction, you must serve real models. The staging is:

| Stage | What you learn | Needs a deployed LLM? | Hardware |
|---|---|---|---|
| A1. Laptop hardening | The pipeline is correct end to end, sim results have CIs | No (fake server for dry runs) | Laptop |
| A2. Local real models | Prompts, extraction, corruptions, validation checks, and a small real H1 work on real text | Yes, via Ollama on the Mac | MacBook Pro, 18 GB |
| B. Single GPU | Real H1, H2, H3 on GSM8K at full scale, plus H4 traces (same-GPU interference) | Yes, 2 models via vLLM | 1 H100 VM |
| C. Multi-GPU, same node | The runtime's placement across GPUs on hardware | Yes, vLLM per GPU | 1 bare-metal node, 2 to 4 GPUs |

Golden rule for the budget: nothing runs on Chameleon that has not already run
end to end on the Mac with the same script. Only `--backend` and the endpoint
config change between the Mac and Chameleon.

**What do the current simulator numbers mean?** They show the logic is
consistent. They do not show that real LLM errors propagate the way the
quality channel assumes, that real hidden states predict criticality, or that
real co-location behaves like the interaction model. Stages B and C test those.

**What is the next step, concretely?** Finish Phase A (about one week of
laptop work), then bring up one GPU on Chameleon and run Phase B. Section 5
gives the exact order.

---

## 2. Current state (verified by running the code)

### 2.1 What passes

- `pytest tests/`: 66 of 66 tests pass.
- `run_demo.py --quick`:

| Gate | Result | Key number |
|---|---|---|
| H1 EC varies across nodes | PASS | |
| H2 EC predicted on unseen workflows | PASS | LOWO Spearman: AgentQO 0.37 / 0.24 / 0.25 / 0.20 by fold; beats confidence (negative) on every fold; loses to structure-only on self-consistency (0.25 vs 0.31) |
| H3 predicted-EC allocation wins | FAIL | AUC AgentQO 12.37 vs confidence 12.81 (minus 3.5%), vs uniform 11.70 (plus 5.7%) |
| H4 two-sided cost (sim) | PASS | own MAE 3.39 vs single-call 6.72 vs additive 35.46 |

- `run_agentqo.py --n-jobs 8 --n-gpus 2`:

| Workflow | Policy | Q | T | Q/GPU | edits |
|---|---|---|---|---|---|
| math s3 + verifier | FCFS-Fixed | 0.759 | 170.4 | 0.0006 | 0 |
| | FixedPlan-EC | 0.856 | 324.3 | 0.0004 | 0 |
| | AgentQO | 0.722 | 142.3 | 0.0007 | 8 |
| multihop QA r3 | FCFS-Fixed | 0.625 | 114.0 | 0.0005 | 0 |
| | FixedPlan-EC | 0.753 | 258.4 | 0.0003 | 0 |
| | AgentQO | 0.564 | 86.2 | 0.0006 | 8 |
| self-consistency | FCFS-Fixed | 0.665 | 86.2 | 0.0005 | 0 |
| | FixedPlan-EC | 0.870 | 229.6 | 0.0004 | 0 |
| | AgentQO | 0.627 | 86.2 | 0.0005 | 12 |
| refinement r2 | all three | 0.760 | 113.2 | 0.0007 | 0 |

Honest reading of the runtime table: AgentQO is fastest but has lower quality
than FCFS on 3 of 4 workflows. Its Q/GPU edge is one unit in the fourth decimal,
from a single seed with no confidence interval. On refinement it makes zero
edits and is identical to FCFS. This is not yet a win; it is a starting point.

### 2.2 What is real and what is simulated today

| Component | Status |
|---|---|
| DAG, executor, partial recompute, overrides | Real, tested |
| vLLM HTTP client (`backends/vllm_http.py`) | Real, tested with mocked HTTP |
| Task data | Simulated. `TaskInstance.ground_truth` is a random integer. No dataset loader |
| Final quality | Simulated. `TaskModel.compute_quality` uses correctness flags and hidden `node_importance` |
| Node correctness with vLLM | Undefined. `_score` returns `False` with `correctness_unknown=True` unless a scorer is passed |
| Embedding with vLLM | Placeholder (hash of output text) |
| Runtime clock and GPU-seconds | Simulated (`Cluster` + `interaction_model`). Real latency is discarded |
| Runtime EC scores | Structural heuristic `_structure_ec` (downstream reach), not the H2 predictor |

---

## 3. Gaps that block real results

Each gap lists the evidence in the code, why it matters, and which WP fixes it.

| ID | Gap | Evidence | Why it matters | Fix |
|---|---|---|---|---|
| G1 | No real tasks | `generate_task` sets `ground_truth=int(rng.integers(0,1000))` | Nothing to score against | WP1 |
| G2 | Final quality is always simulated | `WorkflowExecutor.run_workflow` calls `self.task_model.compute_quality`, which reads hidden `node_importance` | With vLLM, the quality number ignores the actual text | WP1 |
| G3 | Fault injection only flips a flag | `ECLabeler._forced_quality` uses `ExecutionOverrides(forced_correctness=...)`; `_apply_overrides` changes `correctness`, not `output` | With a real LLM, descendants still receive the same text, so the measured consequence is fake | WP3 |
| G4 | Node error probability is undefined for real models | `vllm_http._score` returns `(False, True)` without a scorer | `p_err` and therefore EC cannot be computed | WP4 |
| G5 | Embedding is a hash placeholder | `_placeholder_embedding` | H2 on real models is invalid until a real hidden state is used | WP6 |
| G6 | Generic prompts, no extractable answer | `_build_prompt` emits "Role / Node / Instructions" | Scorer cannot find the answer; quality collapses | WP2 |
| G7 | Runtime timing is simulated | `_dispatch` calls `execute_node` synchronously, then uses `CallSpec` with hard-coded tokens (`prompt = 80 + 40*depth`, `decode = 24 or 64`) and simulated `remaining` | Runtime numbers are not hardware numbers | WP13 |
| G8 | Runtime ignores the predictor | `run_agentqo.py::_structure_ec` | The runtime does not test predicted EC, which is the central claim | WP0.2 |
| G9 | Weak statistics | one seed, no CI, 4-decimal Q/GPU | Cannot claim a win | WP0.3, WP16 |
| G10 | No cache, no concurrency | labeler loops sequentially; no request cache | Real labeling costs roughly 100 calls per task (Section 7); sequential runs take hours | WP5 |
| G11 | Sim H2 is partly by construction | README: "The mock embedding carries hidden importance + difficulty" | A reviewer will ask whether H2 is circular in sim; real H2 is the real test | WP0.4, WP11 |
| G12 | No per-request seed | request payload has no `seed` | Runs are not reproducible | WP5 |

---

## 4. Target architecture for real runs

One GPU node (Phase B) or one multi-GPU node (Phase C). Everything runs on the
node so network latency does not pollute measurements.

```
                 Chameleon GPU node
 +--------------------------------------------------------------+
 |  GPU 0                                                       |
 |   vLLM "small"  (Qwen2.5-1.5B-Instruct)   port 8001          |
 |   vLLM "large"  (Qwen2.5-7B-Instruct)     port 8002          |
 |   Probe encoder (HF transformers, small model, hidden states)|
 |                                                              |
 |  GPU 1..3 (Phase C only): same two servers per GPU,          |
 |   ports 8101/8102, 8201/8202, ...                            |
 |                                                              |
 |  AgentQO process (CPU):                                      |
 |   RealTaskModel + prompts -> CompositeBackend                |
 |     text + logprobs + usage  <- vLLM (per fidelity, per GPU) |
 |     embedding                <- probe encoder                |
 |   GenerationCache (sqlite) + thread pool                     |
 |   ECLabeler (substitute mode) / predictors / policies        |
 |   RealTimeCluster (Phase C) for the runtime                  |
 +--------------------------------------------------------------+
```

Design choices, each with a default (see Section 12 to change):

- **GPU.** Phase B uses one H100 (80 GB) as a KVM VM, flavor `g1.h100.pci.1`,
  charged at 4 SU per hour (a quarter of the 4-GPU host rate). It fits both
  servers and the probe with room to spare. H4 also runs here: AgentIconq models
  interference between calls on the same GPU (cross-GPU pairs do not interact in
  your model), so one GPU is enough to measure it. The VM's host is shared, so
  H4 uses repeats and medians, and this limitation is stated in the results.
  Phase C (placement across GPUs) needs several GPUs on one machine: one
  `gpu_a100` node (4x A100, CHI@UC) or `gpu_h100` node (4x H100, CHI@TACC; only
  two exist, so availability is tighter), at 16 SU per hour, used only for the
  runtime experiment.
- **Model pair.** Small = `Qwen2.5-1.5B-Instruct`, large = `Qwen2.5-7B-Instruct`.
  Same family and tokenizer, so the only difference between fidelities is model
  capacity, and the probe encoder shares the tokenizer. Non-thinking by default,
  so outputs stay short and latency is predictable. If WP9 shows the gap is too
  small, switch large to `Qwen2.5-14B-Instruct` (still fits on one 80 GB GPU
  next to the 1.5B). A Llama-3.1-8B and 70B pair is possible later for Phase C if
  Dr. Liu wants it, but needs Hugging Face approval and 2 GPUs for the 70B.
- **Both models on every GPU.** Then fidelity means "which port" and placement
  means "which GPU". This keeps the runtime's model of the world intact.
- **Probe embedding from one fixed model.** Every node's embedding comes from
  the small model's hidden state, whatever fidelity executed it. This gives one
  consistent feature space. The executing-model variant is an ablation (WP11).
- **Benchmark.** GSM8K first (numeric exact match, cheap, the GSM8K answer field
  ends with `#### <number>`). HotpotQA second (exact match and F1).

---

## 5. Work packages

### Phase A: laptop hardening (no GPU)

#### WP0. Fix the simulator-side weaknesses first

These are cheap and make every later result more credible.

**WP0.1 Full H3 with an oracle upper bound.**
Run `run_h3_allocation.py --num-runs 30` with the full suite (not `--quick`),
and report oracle-EC allocation next to predicted-EC allocation.
Acceptance: `data/h3/` contains both curves with bootstrap CIs; `RESULTS.md`
states whether the bottleneck is the predictor (oracle wins, predicted loses)
or the allocator (both lose).

**WP0.2 Wire the H2 predictor into the runtime (fixes G8).**
Change `scripts/run_agentqo.py`: add `--ec-source {structure,predicted,oracle}`,
default `predicted`. For `predicted`, train `ECPredictor` on the H2 training
workflows and compute scores with
`agentqo.experiments.scoring.predict_node_scores`. Pass them as
`Arrival.ec_scores`. The test workflow must be unseen by the predictor.
Acceptance: the runtime CSV has an `ec_source` column; a test asserts the
predictor never trained on the runtime workflow.

**WP0.3 Seeds and CIs for the runtime (fixes G9 in sim).**
Add `--seeds 5` and `--loads low,med,high` (mean inter-arrival 16, 8, 4).
Report mean and 95% bootstrap CI per policy, and a paired difference
AgentQO minus FCFS per seed. Print Q/GPU with enough precision or rescale it
(for example quality per GPU-hour).
Acceptance: a table with CIs; a Pareto plot of quality vs completion time.

**WP0.4 Circularity check (addresses G11).**
Add a `MockBackend` option `embedding_signal="none"` that emits pure noise
embeddings. Rerun H2. Expected: AgentQO drops to about structure-only.
Acceptance: `RESULTS.md` reports both runs. This shows the predictor is not
magic and that real hidden states must carry the signal.

#### WP1. Real task layer (fixes G1, G2)

Create `agentqo/tasks/`:

```
agentqo/tasks/
  __init__.py
  datasets.py      # load_gsm8k(split, n, seed), load_hotpotqa(split, n, seed)
  answers.py       # extract_gsm8k_number(text), normalize_answer(text), f1(pred, gold)
  real_task_model.py
```

Specification:

- `load_gsm8k` reads `test.jsonl` (1,319 problems) from the official
  `openai/grade-school-math` repository or the Hugging Face `openai/gsm8k`
  dataset. Gold answer = number after `####` in the `answer` field, with commas
  removed. Keep a fixed sample of 300 problems (seeded) as the working set and
  save the chosen ids to `data/tasks/gsm8k_ids.json`.
- `extract_gsm8k_number` takes the last `#### <number>` in the model output; if
  absent, the last number in the text. Handles commas, `$`, trailing periods.
- `RealTaskModel(TaskModel)`:
  - `generate_task(workflow, rng)` draws the next problem from the working set
    and returns a `TaskInstance` with `ground_truth=gold`,
    `metadata={"problem": question, "dataset": "gsm8k", "qid": id}`, and **empty**
    `node_importance` and `node_difficulties`.
  - `compute_quality(task, node_results, workflow)` finds the answer node (WP2),
    extracts the answer from its output text, and returns 1.0 or 0.0 for GSM8K,
    or token F1 for HotpotQA. It must not read correctness flags.
  - `compute_node_error_prob` raises `NotImplementedError` (only the simulator
    uses it).
- Add `tests/test_no_leakage.py`: monkeypatch `TaskInstance.node_importance`
  to raise on access, then run a full predictor fit and a runtime episode on
  the mock backend. Any access fails the test.

Acceptance:
- Unit tests for extraction cover at least 15 real output styles.
- `compute_quality` on 50 gold-answer strings returns 1.0 for all.
- `test_no_leakage.py` passes.

#### WP2. Prompts and answer nodes (fixes G6)

Create `agentqo/tasks/prompts.py` with one template per (workflow family, role):

| Role | Template intent | Required output format |
|---|---|---|
| planner | Break the problem into numbered steps; do not solve | `PLAN:` numbered list |
| step / researcher | Execute exactly step i given the plan and prior results | `RESULT: <value>` |
| aggregator | Combine results and state the final answer | ends with `#### <number>` |
| verifier | Check the aggregator's answer; fix if wrong | `VERDICT: correct or incorrect` then `#### <number>` |
| sampler (self-consistency) | Solve fully | ends with `#### <number>` |
| formatter | Restate the answer cleanly | ends with `#### <number>` |

Add `answer_nodes: List[str]` (priority list) to each workflow in
`workflows/library.py`, for example `["verifier", "aggregator"]` for math.
`RealTaskModel` uses the first executed node in that list. For
self-consistency the aggregator takes a majority vote over sampler answers in
code, not by the LLM (this matches the method and removes a failure point).

Change `VLLMHTTPBackend._build_prompt` to accept a template function from
`task_context["prompt_fn"]`, keeping the current generic prompt as a fallback.

Acceptance: on 20 GSM8K problems with the large model (or the fake server in
WP7), the answer is extractable from the answer node in at least 95% of runs.

#### WP3. Output-substitution fault injection (fixes G3)

This is the most important scientific change. With a real LLM, a node is "wrong"
only if its text is wrong, and descendants only see the text.

Add `mode: Literal["flag", "substitute"]` to `ECLabeler`. `flag` keeps the
current behaviour and is allowed only with `MockBackend`. `substitute` is
required for real backends; the labeler raises if a real backend is used with
`flag`.

Substitute-mode definition for node v on task t:

- **Good side:** replace v's output with a reference output: the large model at
  temperature 0 on v's baseline inputs. Recompute descendants.
  `q_plus = Q(v := reference)`.
- **Bad side:** replace v's output with each of C corruptions (default C = 3),
  recompute descendants, average. `q_minus = mean Q(v := corruption_c)`.
- **Consequence:** `Delta_v,t = q_plus - q_minus`.

Corruption strategies (create `agentqo/labeling/corruptions.py`):

| Strategy | How | Applies to |
|---|---|---|
| `numeric_perturb` | Change the key number in `RESULT:` or `####` by a plausible error (off by one step, wrong operation, digit swap) | math nodes |
| `resample_disagree` | Sample v at temperature 1.0 up to 8 times, keep the first output whose extracted key differs from the reference | all nodes |
| `swap_other_task` | Use the same node's output from a different task | all nodes |
| `llm_subtle_wrong` | Ask the small model to rewrite v's output with one subtle error, same format | fallback when others fail |

Engineering details:

- Implement substitution through `ExecutionOverrides.force_outputs`. Add
  `skip_forced_execution=True` so a forced node is not executed first and then
  overwritten (the current `_apply_overrides` runs the node and discards the
  result, which wastes a call).
- During labeling, run all non-target nodes at temperature 0, except samplers
  (temperature 0.7 with fixed seeds). The only thing that changes between the
  good and bad sides is the substituted text.
- Record for each corruption: strategy used, whether its key actually differs
  from the reference, and the recomputed descendants' outputs.

Acceptance:
- A unit test with a scripted fake backend shows that substituting a planner
  output changes the text every descendant receives, and that non-descendants
  stay byte-identical (reuse `verify_partial_recompute_invariant`).
- The existing sanity test is reproduced on real text: corrupting the
  aggregator lowers quality; corrupting a formatter barely changes it.

#### WP4. Node error probability for real models (fixes G4)

Default definition (reference agreement):

```
p_err(v) = fraction of K samples of v (small model, temperature 0.7, fixed seeds,
           on baseline inputs) whose extracted key differs from the reference key
```

"Key" is the extracted number for math nodes and the normalized answer span for
QA nodes. For planner nodes, whose output has no single key, use the final
answer obtained by running descendants greedily from each sample (this is more
expensive; cap K at 3 for planners). Default K = 5.

Also compute, as an alternative for the ablation, final-attribution error:
`p_err_final(v) = P(final wrong | v sampled)` using the same K samples.

EC per (task, node) keeps the current definition in
`experiments/dataset.py`: `y_ec = Delta_v,t * p_err(v)`.

Acceptance: on the fake server, p_err for a node that always agrees is 0, and
for a node that always disagrees is 1. On real models (Phase B), report the
distribution of p_err per role.

#### WP5. Generation cache, seeds, concurrency (fixes G10, G12)

- Add `agentqo/backends/cache.py`: a sqlite cache keyed by
  `sha256(model, messages, temperature, top_p, max_tokens, seed)`. Store text,
  logprob summary, `usage.prompt_tokens`, `usage.completion_tokens`, latency,
  timestamp. Reuse `agentqo/database.py` if it fits.
- Pass `seed` in every request. vLLM's OpenAI-compatible server accepts it, but
  batched sampling is still not guaranteed bit-identical, so the cache is the
  source of reproducibility.
- Capture `usage` from each response into `NodeResult.metadata`.
- Parallelize labeling across tasks with a thread pool (default 32 workers).
  Tasks are independent; within a task keep topological order.

Acceptance: running the same labeling config twice gives identical labels with
zero new HTTP calls on the second run; with a fake server that sleeps 200 ms per
call, 32 workers give at least a 15x speedup over sequential.

#### WP6. Probe embeddings (fixes G5)

Create `agentqo/backends/probe.py`:

```python
class ProbeEncoder(Protocol):
    dim: int
    def encode(self, prompt: str, output: str | None) -> np.ndarray: ...

class HFHiddenStateProbe:   # transformers, output_hidden_states=True
    def __init__(self, model_id, layer: int, pool: Literal["mean", "last"],
                 device="cuda", max_tokens=1024): ...

class PlaceholderProbe:     # current hash embedding, for CI only
```

- Default: small model, one prefill-only forward pass over `prompt + output`,
  mean-pooled hidden state of a middle layer. Start with the layer at about 40%
  depth (TRAIL found middle layers best for length; criticality may differ, so
  WP11 sweeps layers).
- Create `CompositeBackend(text_backend, probe)` that calls vLLM for text and the
  probe for the embedding, and sets `metadata["embedding_kind"]="probe_hidden_state"`.
- H2 refuses to run if any sample has `embedding_kind == "placeholder"`, unless
  `--allow-placeholder` is passed for debugging.

Acceptance: embeddings are deterministic for the same input; dimension matches
the model's hidden size; encoding one node costs under 50 ms on the GPU (measure
and report, this is the overhead claim).

#### WP7. Laptop dry run with a fake server

Before spending GPU hours, run the entire real pipeline end to end on the laptop.

- Add `agentqo/backends/fake_server.py`: a scripted `request_fn` that returns
  role-appropriate text with configurable error rates per fidelity (for example
  it knows the gold answer and is wrong with probability 0.35 for small, 0.1 for
  large). This is a test double, never used for results.
- Add `scripts/run_real_pipeline.py` with `--backend {fake,vllm}`, running:
  task load, baseline, substitute labeling, p_err, dataset build, H2 fit, H3.

Acceptance: `python scripts/run_real_pipeline.py --backend fake --n-tasks 10`
completes, writes all artifacts, and H1 shows the aggregator and planner with
larger consequence than the formatter.

### Phase A2: local real models on the Mac

#### WP7b. Local real-model tier on the Mac (Ollama)

Goal: find every prompt, extraction, corruption, and pipeline bug on real text
for free, so Chameleon hours are spent only on production runs.

Setup (MacBook Pro 2023, 18 GB unified memory):

```bash
ollama pull qwen2.5:1.5b
ollama pull qwen2.5:7b
# keep both models loaded and allow concurrent requests
export OLLAMA_MAX_LOADED_MODELS=2
export OLLAMA_NUM_PARALLEL=4
ollama serve
```

Memory: the default 4-bit builds use roughly 1 GB (1.5B) and 5 GB (7B); the probe
encoder (1.5B in fp16 through PyTorch on the Apple GPU, `device="mps"`) needs
about 3 to 4 GB. That fits in 18 GB with room for the OS. If memory is tight,
drop `OLLAMA_NUM_PARALLEL` to 2.

Code: create `agentqo/backends/ollama_backend.py` implementing `ModelBackend`.
- Endpoints: `small -> qwen2.5:1.5b`, `large -> qwen2.5:7b` on
  `http://localhost:11434`.
- Confidence needs token logprobs. Ollama's documentation lists logprobs and
  `seed` as supported on the OpenAI-compatible `/v1/chat/completions`, but a
  May 2026 issue reports that endpoint dropping logprobs while the native API
  returns them. So: call `/v1/chat/completions` first; if the response has no
  logprobs, switch to the native `/api/chat` or `/api/generate` with logprobs
  requested. Record `metadata["confidence_source"]` as `logprobs` or
  `missing`.
- Fail loudly: the existing vLLM client returns a constant 0.5 when logprobs are
  missing. With a constant confidence the confidence-only baseline becomes
  meaningless without any error. The Ollama backend must raise if more than 5%
  of calls in a run have no logprobs (override with `--allow-missing-logprobs`
  for debugging only). Apply the same guard to the vLLM client.
- Token counts: Ollama may report `prompt_tokens = 0` when the prompt was served
  from its cache; take prompt length from the tokenizer instead when that
  happens.
- Pass `seed` in every request and go through the generation cache (WP5), with
  the model tag (including quantization) in the cache key.

Local gates, run with the same `scripts/run_real_pipeline.py --backend ollama`:

| Gate | Scale | Pass when |
|---|---|---|
| M1 Smoke | 5 prompts per model | Text returned, logprobs present, seeds reproducible from cache |
| M2 Validation | 20 dev tasks | V1 to V7 from Section 13 pass |
| M3 Extraction | 50 tasks | At least 95% of answer-node outputs extractable |
| M4 Corruptions | 20 tasks | At least 90% of corruptions change the key |
| M5 Mini H1 | 30 dev tasks, math workflow | Consequence spread visible (planner and aggregator above formatter) |
| M6 End to end | 30 dev tasks | H2 and H3 stages complete and write all artifacts |
| M7 Realtime logic | 5 workflows | WP13 `RealTimeCluster` runs with both "GPUs" mapped to the one Ollama server (tests the code path, not performance) |

What the Mac numbers mean, and what they do not:
- They show the pipeline works on real text and give an early read on whether
  criticality varies (M5). That is valuable and worth a short note to yourself.
- They are not the reported results. Ollama's default builds are 4-bit
  quantized, so accuracy differs from the bf16 models on vLLM. If you want local
  numbers closer to Chameleon, pull an 8-bit tag of the 7B model if memory
  allows, but still report only Chameleon numbers.
- Mac latency and concurrency say nothing about GPU serving. Do not run H4 or
  the runtime comparison on the Mac for results.
- Generations from the Mac are not reused on Chameleon (different model builds,
  different cache keys). What carries over is the code, prompts, corruption
  settings, and validated configuration.

Rough throughput to plan around (measure it in M1): a labeling task is about 110
to 120 calls, mostly on the small model. Expect minutes per task on the Mac, so
30 tasks is an overnight run at worst.

Acceptance: M1 to M7 all pass. Write the chosen prompts, corruption settings,
probe layer default, and any fixes into `configs/phase_b.yaml`. That file is the
only configuration used on Chameleon.

### Phase B: one H100 VM on Chameleon

#### WP8. Chameleon bring-up runbook

1. Portal: confirm CHI-251518 shows an active allocation. Switch site to the one
   with GPU nodes (CHI@TACC or CHI@UC).
2. Phase B: go to KVM@TACC and plan a VM with flavor `g1.h100.pci.1` (one H100,
   4 SU per hour). Phase C: use the resource browser at CHI@UC or CHI@TACC and
   filter `node_type=gpu_a100` or `gpu_h100` (4-GPU bare metal, 16 SU per hour).
   Confirm the SU rate shown before reserving.
3. Add your SSH public key under Key Pairs.
4. Create a lease: for Phase B a GPU VM reservation on KVM@TACC; for Phase C one
   bare-metal node. Start with 2 days (maximum 7 days, renewable when 30% or less
   remains). Leases burn SUs for the whole window, so do not reserve
   ahead of need, and do not stack overlapping leases.
5. Launch an instance on the lease using a Chameleon-supported Ubuntu image with
   CUDA (the appliance catalog lists them). Attach a floating IP. SSH in.
6. Verify the GPU:
   ```bash
   nvidia-smi
   ```
7. Environment:
   ```bash
   python3 -m venv ~/venv && source ~/venv/bin/activate
   pip install -U pip
   pip install vllm transformers accelerate
   git clone https://github.com/Shusmoy108/AgentQO.git && cd AgentQO
   pip install -e ".[all]"
   pytest tests/ -q
   ```
8. Download models once (they are cached in `~/.cache/huggingface`):
   ```bash
   huggingface-cli download Qwen/Qwen2.5-1.5B-Instruct
   huggingface-cli download Qwen/Qwen2.5-7B-Instruct
   ```
9. Start two servers on GPU 0 (use `tmux` so they survive disconnects):
   ```bash
   CUDA_VISIBLE_DEVICES=0 vllm serve Qwen/Qwen2.5-7B-Instruct \
     --port 8002 --gpu-memory-utilization 0.45 --max-model-len 4096 \
     --enable-prefix-caching
   CUDA_VISIBLE_DEVICES=0 vllm serve Qwen/Qwen2.5-1.5B-Instruct \
     --port 8001 --gpu-memory-utilization 0.20 --max-model-len 4096 \
     --enable-prefix-caching
   ```
   The probe encoder loads the 1.5B model in the AgentQO process and needs about
   4 GB more. Adjust utilization fractions if memory errors appear. Flag names
   can change across vLLM versions; check `vllm serve --help` for the installed
   version and record the version in `RESULTS.md`.
10. Smoke test, pointing each fidelity at its port:
    ```bash
    VLLM_BASE_URL=http://localhost:8001 VLLM_SMALL_MODEL=Qwen/Qwen2.5-1.5B-Instruct \
      python scripts/run_vllm_smoke.py
    ```
11. After the first successful bring-up, save a snapshot of the instance with
    the venv and both models installed. For the KVM@TACC VM, use "Create
    Snapshot" on the instance in the dashboard (OpenStack image snapshot); for
    the bare-metal node in Phase C, use Chameleon's `cc-snapshot` tool. Launch
    later sessions from the snapshot to skip about an hour of installs and
    downloads each time. Check the current image size limit before snapshotting
    about 20 GB of model weights.
12. Before the lease ends, copy `data/` and the generation cache back to your
    laptop (`rsync`). The instance disk disappears with the lease. Then delete
    the lease immediately; SUs are charged for the active window.

Code change needed for step 10: `VLLMHTTPConfig` currently has one `base_url`.
Add `endpoints: Dict[str, str]` mapping fidelity name to base URL (for example
`{"small": "http://localhost:8001", "large": "http://localhost:8002"}`), with an
env var `VLLM_ENDPOINTS` as JSON.

Acceptance: smoke test prints `OK` for both fidelities; `RESULTS.md` records node
type, GPU model, driver, CUDA, vLLM version, model ids.

#### WP9. Fidelity calibration

Measure the real small vs large gap before trusting any allocation result.

- Run the single-sampler workflow (one node solves the problem) on the 300-task
  working set with each model at temperature 0.
- Record accuracy with a 95% Wilson CI, mean and p95 latency, mean tokens.
- Write the measured values into real `Fidelity` objects (`REAL_SMALL`,
  `REAL_LARGE`): `base_error_rate = 1 - accuracy`, `cost = mean GPU-seconds per
  call` (latency times number of GPUs for that fidelity).

Gate: large must beat small by at least 10 accuracy points with non-overlapping
CIs. If not, switch the pair (for example 0.5B vs 7B, or 1.5B vs 14B) and rerun.
Without a real gap, H3 cannot pass for reasons unrelated to AgentQO.

#### WP10. Real H1 (criticality varies)

Config: GSM8K, workflows Math 3-step + verifier, Self-consistency k=3, Complex +
formatter; 200 tasks each; substitute mode; C = 3 corruptions; K = 5 for p_err.

Outputs per node: mean consequence with bootstrap CI, p_err, EC, and the
distribution across roles. Reuse `analyze_h1_results` thresholds (range above
0.1 and CV above 0.2) and the formatter smoke test.

Acceptance: H1 PASS/FAIL printed with CIs. Also report the share of corruptions
whose key actually differed from the reference (target at least 90%; if lower,
corruptions are too weak and consequence is underestimated).

#### WP11. Real H2 (criticality is predictable)

- Features: structural + probe embedding + confidence (from logprobs).
- Split: leave-one-workflow-out, exactly as in the simulator.
- Baselines: confidence-only, structure-only, prompt-only text model (TF-IDF plus
  ridge on the node prompt, the analogue of TRAIL's BERT baseline).
- Sweeps: probe layer (every 4th layer), pooling (mean vs last token), probe
  model (small vs executing model).
- Report predictor overhead per node in milliseconds (`timing` like TRAIL's
  Table 1).

Acceptance: H2 PASS if AgentQO beats confidence-only on every fold and at least
matches structure-only on average, with a paired bootstrap CI on the Spearman
difference. Report the numbers even if it fails.

#### WP12. Real H3 (spending by predicted EC)

- Every node starts on small. Budgets sweep from 0 to "all large".
- Policies at equal budget: predicted EC, confidence, uniform, all small, and
  oracle EC (upper bound only).
- Same tasks for every policy (paired design). 200 tasks per budget level.
- Metrics: accuracy vs GPU-seconds curve, AUC with bootstrap CI.

Acceptance: H3 PASS if predicted EC beats both confidence and uniform AUC with
the CI of the difference excluding zero. If oracle wins and predicted loses, the
predictor is the bottleneck (Section 9).

### Phase C: multi-GPU runtime (WP14 runs on the Phase B VM)

#### WP13. Real-time runtime (fixes G7)

Create `agentqo/runtime/realtime_cluster.py` implementing the same interface as
`Cluster` (`admit`, `complete`, `next_completion`, `least_loaded_gpu`,
`physical_cost`, `store_kv`, `now`) but backed by real servers:

- `gpu_endpoints: Dict[int, Dict[str, str]]`, for example
  `{0: {"small": ":8001", "large": ":8002"}, 1: {"small": ":8101", ...}}`.
- `admit(call)` submits the HTTP request to a thread pool and returns
  immediately. `next_completion()` blocks on the earliest finished future
  (`concurrent.futures.wait(..., return_when=FIRST_COMPLETED)`).
- `now` is wall-clock seconds since the episode started.
- Real `prompt_tokens` and `completion_tokens` come from the response `usage`.
- `physical_cost` uses the AgentIconq model trained on real traces (WP14), not
  the simulator formula.
- Scrape each server's Prometheus `/metrics` endpoint every 0.5 s (running and
  waiting requests, KV cache usage) for batch-state features. Metric names vary
  by vLLM version; log the raw names you find.

Change `AgentQO._dispatch` so `execute_node` is not called synchronously in
realtime mode: the cluster owns the call and delivers the `NodeResult` on
completion.

Efficiency metric on hardware: continuous batching makes the sum of per-call
latencies overcount GPU use. Report both
- `correct_per_reserved_gpu_hour = total correct answers / (makespan * n_gpus)`
  (primary), and
- sum of latency times GPUs (secondary, comparable to the simulator).

Acceptance: the code path is first proven on the Mac (gate M7, both "GPUs"
mapped to the one Ollama server). On the bare-metal node, an episode of 20
workflows on 2 GPUs completes; every call has real start and end timestamps and
token counts; results replay from the cache.

#### WP14. Real H4 traces (two-sided cost), on the single H100 VM

Run this during the Phase B lease: it needs one GPU, since the model covers
interference between calls sharing a GPU. Trim the sweep to fit the budget:
m in {0, 1, 2, 4, 8}, prompt in {128, 1024}, decode in {64, 256}, model in
{small, large}, prefix shared in {yes, no}: 80 cells, 5 repeats each.

Controlled co-location protocol (create `scripts/run_h4_real_traces.py`):

1. Warm up each server with 20 requests; discard.
2. For each configuration, run a paired pair of trials in random order:
   - Trial W: start background set R (m requests), wait 300 ms so they are
     decoding, then send candidate a. Record latency of a and of every j in R.
   - Trial O: start the same R without a. Record latency of every j in R.
   - Isolated: send a alone on an idle GPU.
3. Own latency under load = latency of a in W. Imposed delay on j =
   latency_j(W) minus latency_j(O).
4. Sweep (the trimmed grid above): prefix shared means the same 1,500-token
   prefix as R, with prefix caching on. 5 repeats per cell; report medians.
   Expected run time is a few hours; budget 6 VM hours (24 SU).
5. Write rows with the `CallSpec` fields plus measured own latency, imposed delay
   per running call, and batch-state metrics. Add
   `agentqo/predictors/trace_adapter.py::traces_to_xy()` so the existing
   `AgentIconqPredictor`, `SingleCallBaseline`, and `AdditiveBaseline` train and
   evaluate on real rows unchanged.

Acceptance: H4 PASS if AgentIconq beats both baselines on own-latency MAE and
Q-error on held-out configurations, and the sign of imposed delay is correct for
both contention (positive) and shared-prefix reuse (lower or negative). If
reuse never shows up, report it; it is a real finding about vLLM prefix caching
at these sizes.

#### WP15. Runtime on hardware

- Policies: FCFS-Fixed, FixedPlan-EC (predicted EC), AgentQO (predicted EC), each
  on the same arrival traces.
- Arrivals: Poisson, 3 load levels chosen so FCFS runs at about 40%, 70%, 90% GPU
  busy time (measure in a pilot).
- Budget-shaped design: 2 GPUs at all 3 load levels with 3 seeds (27 episodes),
  plus 4 GPUs at the high load level with 3 seeds (9 episodes). 40 workflows per
  episode; mix of math, self-consistency, complex workflows. Add seeds 4 and 5
  only if the SU ledger allows (Section 7).
- Before the lease, run a 1-hour pilot to choose the three arrival rates; do
  not tune them during the main runs.
- Metrics: accuracy, mean and p95 completion time, correct per reserved GPU-hour,
  edits used, wasted speculative GPU-seconds.

Acceptance (pre-registered): AgentQO wins if, at 2 of 3 load levels, its correct
per reserved GPU-hour is higher than FCFS with a paired 95% CI excluding zero,
and its accuracy is no more than 2 points below FCFS (or it lies on the Pareto
frontier of accuracy vs p95 completion time). Report every cell regardless.

### Phase D: statistics, reporting, tuning

#### WP16. Statistics and reporting

- H1: bootstrap CI per node (1,000 resamples), range, CV.
- H2: Spearman per fold and seed; mean and 95% CI; paired bootstrap on the
  difference against each baseline.
- H3 and runtime: paired design (same tasks or arrivals across policies);
  bootstrap CI on AUC and on per-seed differences; Wilcoxon signed-rank as a
  second test.
- Always report n (tasks, seeds, workflows), model ids, vLLM version, GPU type,
  and SU used.
- `scripts/make_report.py` regenerates every table and figure from `data/` and
  writes `RESULTS.md` sections (template in Appendix C).

#### WP17. Definition of done for the full prototype

The prototype is complete when all of these exist and pass review:

1. `pytest tests/ -q` passes, including the new leakage, substitution, cache, and
   realtime tests.
2. Simulator results with CIs, oracle bound, circularity check (WP0).
3. Real calibration (WP9) and real H1, H2, H3 on GSM8K with CIs (WP10 to WP12).
4. Real H4 traces and fit (WP14).
5. Runtime on hardware for three policies with CIs (WP15).
6. `RESULTS.md` filled in, with every gate marked PASS or FAIL and one paragraph
   of interpretation each.
7. One command per experiment documented in the README; configs committed.

---

## 6. Experiment matrix

| Exp | Phase | Workflows | Tasks / runs | Models | Primary metric | Gate |
|---|---|---|---|---|---|---|
| S-H3 | A | full sim suite | 30 runs | sim | AUC vs baselines, oracle | report bottleneck |
| S-RT | A | 4 sim workflows | 5 seeds x 3 loads | sim | Q/GPU paired diff | CI reported |
| S-CIRC | A | sim suite | as H2 | sim, noise embedding | H2 Spearman drop | report |
| DRY | A | math, SC, complex | 10 tasks | fake server | pipeline completes | all artifacts |
| LOCAL | A2 | math, SC, complex | 20 to 50 tasks | Ollama 1.5B, 7B | gates M1 to M7 | all pass |
| CAL | B | single sampler | 300 | small, large | accuracy gap | 10 points, disjoint CIs |
| R-H1 | B | 3 workflows | 200 each | small, large | consequence spread | range 0.1, CV 0.2 |
| R-H2 | B | LOWO over 3 | from R-H1 | probe | Spearman vs baselines | beats confidence, matches structure |
| R-H3 | B | 3 workflows | 200 per budget | small, large | AUC | beats confidence and uniform, CI excludes 0 |
| R-H4 | B (VM) | synthetic calls | 80 cells x 5 repeats | small, large | own MAE, Q-error, sign | beats both baselines |
| R-RT | C | mixed | 2 GPUs: 3 loads x 3 seeds; 4 GPUs: 1 load x 3 seeds | small, large | correct per reserved GPU-hour | Section WP15 |

---

## 7. Compute and SU estimate

Calls per GSM8K task in substitute labeling for a 6-node workflow (planner, 3
steps, aggregator, verifier), with C = 3 and K = 5:

| Item | Calls |
|---|---|
| Baseline | 6 |
| Reference output per node | 6 |
| Good-side descendant recompute (about 2.5 per node) | 15 |
| Bad-side recompute (3 corruptions x 2.5 x 6) | 45 |
| Corruption generation (resample or LLM) | about 6 to 20 |
| p_err samples (K = 5 x 6) | 30 |
| **Total** | **about 110 to 120** |

200 tasks is about 23,000 calls per workflow, three workflows about 70,000
calls. With short outputs and 32 concurrent requests, a 1.5B and 7B pair on one
A100-class GPU should handle this in a few hours; sequentially it would take
days. Treat this as an estimate and measure throughput in WP9.

SU budget, capped at 1,000 (rates from the Chameleon FAQ: a single-H100 VM is 4
SU per hour, a 4-GPU bare-metal host is 16 SU per hour; confirm on the lease
page before reserving):

| Step | Hardware | Hours | SU |
|---|---|---|---|
| B1 bring-up, smoke test, snapshot | 1 H100 VM | 4 | 16 |
| B2 calibration, 2 models x 300 tasks (WP9) | 1 H100 VM | 2 | 8 |
| B3 dev split, 100 tasks, up to 3 generation rounds of tweaks | 1 H100 VM | 18 | 72 |
| B4 evaluation split, 200 tasks x 3 workflows (WP10) | 1 H100 VM | 12 | 48 |
| B5 H2 probe sweeps and H3 executions (WP11, WP12) | 1 H100 VM | 6 | 24 |
| B6 H4 traces (WP14) | 1 H100 VM | 6 | 24 |
| **Phase B subtotal** | | **48** | **192** |
| C1 bring-up on bare metal, pilot for arrival rates | 4-GPU node | 3 | 48 |
| C2 runtime, 36 episodes (WP15) | 4-GPU node | 6 | 96 |
| C3 reruns and fixes | 4-GPU node | 3 | 48 |
| **Phase C subtotal** | | **12** | **192** |
| **Planned total** | | | **384** |
| Contingency (about 50%) | | | 200 |
| **Expected ceiling** | | | **about 600** |
| Reserve kept untouched | | | 400 |
| **Hard cap** | | | **1,000** |

Rules that keep you under the cap:

1. **Mac first, always.** A script runs on Chameleon only after it has passed on
   the Mac with the same config (WP7b). Debugging on a lease is the fastest way
   to burn SUs.
2. **Unattended runs.** Each lease session runs one prepared script
   (`scripts/phase_b_session.sh`, `scripts/phase_c_session.sh`) that starts
   servers, runs the planned steps, copies results out, and logs SU-relevant
   timestamps. You watch; you do not type experiments by hand.
3. **Short leases, deleted early.** Reserve in hours, not days. Delete the lease
   the moment the script finishes. Never leave a 4-GPU node idle (16 SU per
   hour).
4. **Snapshot once.** After B1, snapshot the VM (dashboard snapshot, WP8 step 11). Later sessions skip installs and
   model downloads.
5. **SU ledger.** After every lease, add a row to `RESULTS.md`: date, hardware,
   hours, SU, what ran. Check it before each new lease.
6. **Stop rules.** If Phase B passes 300 SU, stop and review before continuing
   (something is being redone). If the total passes 700 SU, spend the rest only
   on the experiments needed for the gate summary; drop optional seeds and
   sweeps first.
7. **Cheapest place first for each experiment.** H4 runs on the 4 SU per hour
   VM, not the 16 SU per hour node. Only the multi-GPU placement experiment
   needs the bare-metal node.

If the 8,000 SU is shared with other project members, tell Dr. Liu you plan to
use at most 1,000.

---

## 8. Pre-registered pass criteria (summary)

| Gate | Pass when |
|---|---|
| CAL | large beats small by at least 10 points, disjoint 95% CIs |
| H1 | consequence range above 0.1 and CV above 0.2; formatter smoke test holds; at least 90% of corruptions change the key |
| H2 | beats confidence-only on every LOWO fold; mean Spearman at least structure-only; paired CI reported |
| H3 | predicted-EC AUC above confidence and uniform, CI of difference excludes 0 |
| H4 | AgentIconq beats single-call and additive on own MAE and Q-error on held-out configs; imposed-delay sign correct |
| RT | Section WP15 criterion |

Fix these before running Phase B. Changing them after seeing results
invalidates the claim.

---

## 9. Tuning playbook (what to try when a gate fails)

| Symptom | Likely cause | Try, in this order |
|---|---|---|
| H1 fails on real models | corruptions too weak; verifier repairs everything | check key-change rate; add stronger corruptions; remove verifier in one variant; use harder GSM8K subset |
| H1 passes but consequence is near 0 for most nodes | workflow too shallow; answer mostly decided by aggregator | deeper math workflow (5 steps); complex workflow |
| H2 loses to structure-only | probe layer wrong; embedding does not carry difficulty | layer sweep; pooling sweep; add prompt length and upstream disagreement features; more tasks |
| H2 loses to confidence | confidence is actually informative for this model | report honestly; combine confidence into the AgentQO view (already present); check calibration |
| H3 fails, oracle wins | predictor too weak | improve H2 first; do not tune the allocator |
| H3 fails, oracle also loses | fidelity gap too small or allocation granularity too coarse | recheck CAL; add a middle fidelity; finer budget steps |
| H4 reuse sign never appears | prefix caching off or prefix too short | confirm prefix caching in server logs; longer shared prefix |
| Runtime: fast but lower accuracy | optimizer skips too much optional work | raise lambda_R or add a quality floor constraint; restrict cancel edits to low predicted EC |
| Runtime: zero edits | edit scores never beat no-op | log per-event scores; check lambda scales against measured real costs |
| Results change between reruns | cache misses or unseeded sampling | verify cache hit rate; confirm seeds in payload |

Record every tuning change and its result in `RESULTS.md`. Tune on a validation
workflow or task split, then report once on the held-out split.

---

## 10. Risks

| Risk | Mitigation |
|---|---|
| Real criticality not cheaply predictable | Planned negative result; WP0.4 and WP11 baselines make the finding clean |
| Model pair gap too small | WP9 gate before any H3 run |
| vLLM version changes flags or metrics | Record version; pin it in `requirements-gpu.txt` after bring-up works |
| GPU memory pressure with two servers and a probe | Lower `--gpu-memory-utilization`; lower `--max-model-len`; move probe to a second GPU in Phase C |
| Lease expiry loses data | rsync `data/` and cache after every run; keep work in `tmux` |
| Labeling cost higher than estimated | cache, concurrency, reduce C or K, fewer tasks for sweeps |
| Scope creep into full graph rewriting | Keep the constrained edit set from the proposal |

---

## 11. Suggested schedule

| Week | Work | Deliverable |
|---|---|---|
| 1 | WP0 to WP3 | sim CIs, oracle bound, real task layer, substitution labeling |
| 2 | WP4 to WP7 | p_err, cache and concurrency, probe, laptop dry run passes |
| 3 | WP7b | Ollama tier on the Mac, gates M1 to M7, `configs/phase_b.yaml` frozen |
| 4 | WP8, WP9, WP10 | H100 VM up, snapshot, calibration gate, real H1 |
| 5 | WP11, WP12, WP14, Section 13 | real H2, H3, H4 with CIs, validation table, casebook; first update to Dr. Liu |
| 6 | WP13 | realtime cluster finished and tested on the Mac (M7) |
| 7 | WP15, WP16 | runtime on bare metal, final report, SU ledger |

The first update to Dr. Liu is the end of week 5: calibrated real models, real
H1 to H3, each backed by the explain and validate artifacts from Section 13, and
an honest account of what passed and what you changed.

---

## 12. Decisions and remaining questions

Decided (v2):

| Question | Decision |
|---|---|
| Budget | Hard cap 1,000 SU; planned about 400, expected ceiling about 600 |
| Local tier | MacBook Pro 18 GB with Ollama (qwen2.5:1.5b, qwen2.5:7b) for all debugging and gates M1 to M7 |
| GPU | Phase B and H4: 1 H100 VM (`g1.h100.pci.1`, 4 SU/hour). Phase C: one 4-GPU bare-metal node (16 SU/hour), runtime only |
| Model pair | Qwen2.5-1.5B-Instruct and Qwen2.5-7B-Instruct; fallback large = 14B |
| First update scope | Real, explainable H1 to H3 on GSM8K (Section 13); runtime on hardware follows |

Still open (defaults in parentheses):

1. **Good-side reference.** (Large model at temperature 0.)
2. **Probe embedding source.** (Small model for all nodes; executing model as an ablation.)
3. **Is the 8,000 SU yours alone or shared?** (Assume shared; keep leases short.)
4. **HotpotQA in the first update?** (No; GSM8K only, HotpotQA after.)

---

## 13. Making results explainable, verifiable, and tunable

A number you cannot explain is not a result you can defend or improve. Every
real experiment must produce three kinds of evidence: traces you can read, checks
that prove the pipeline measures what it claims, and a tuning protocol that
does not fool you. This section is part of the definition of done for Phase B.

### 13.1 Explain: every number traces back to text

Build `agentqo/analysis/` with these artifacts, written for every run:

| Artifact | Content | Answers the question |
|---|---|---|
| `traces/<task>.json` | Every node's prompt, output, extracted key, confidence, tokens, latency, fidelity | What actually happened on this task? |
| `substitutions/<task>_<node>.json` | Reference output, each corruption and its strategy, every recomputed descendant output, final answers, q_plus, q_minus | Why is this node's consequence high or low? |
| `casebook.md` | Auto-generated: top 5 highest-EC and bottom 5 lowest-EC (task, node) pairs with the full chain shown side by side | Can I show Dr. Liu one concrete example of an error propagating and one being absorbed? |
| `role_summary.csv` | Per role: mean consequence, p_err, EC, share of corruptions absorbed downstream | Which roles matter, and is that intuitive? |
| `absorption.csv` | For each corruption: did a downstream node (verifier, majority vote) repair it? Which one? | Where do errors die, and where do they survive? |
| `predictor_explain.csv` | Feature importances (permutation importance) for the H2 model, per view | Is the predictor using the embedding, or leaning on structure? |
| `allocation_trace.csv` | For each H3 budget level: which nodes each policy upgraded, and the quality change per upgrade | Why does predicted EC win or lose against confidence at this budget? |

What to be able to say from these, in one sentence each:
- "Planner errors propagate to the final answer in X% of corruptions; formatter
  errors in Y%; the verifier repairs Z% of aggregator errors."
- "The predictor ranks planners high because of <features>, and misses on
  <case> because <reason visible in the trace>."
- "At budget B, predicted EC upgraded <nodes>; confidence upgraded <nodes>; the
  difference in accuracy comes from <node>."

### 13.2 Validate: checks that must pass before a number is trusted

Run `scripts/validate_pipeline.py` before every reported experiment. Each check
prints PASS or FAIL; any FAIL blocks the report.

| Check | Procedure | Pass when |
|---|---|---|
| V1 Gold injection | Force the answer node's output to `#### <gold>` | Quality is 1.0 on 100% of tasks |
| V2 Wrong injection | Force the answer node's output to `#### <gold+1>` | Quality is 0.0 on 100% of tasks |
| V3 Extraction audit | Hand-check 50 random answer-node outputs against extracted keys | At least 98% extracted correctly; log every miss |
| V4 Corruption effectiveness | For each corruption, compare its key with the reference key | At least 90% differ (else consequence is underestimated) |
| V5 Isolation invariant | Rerun `verify_partial_recompute_invariant` on real runs | Zero violations |
| V6 Determinism | Rerun one labeling config with the cache | Identical labels, zero new HTTP calls |
| V7 Leakage | `test_no_leakage.py` on the real pipeline | Passes |
| V8 Label stability | Split the 200 tasks into two halves; label each | Spearman between halves' per-node EC at least 0.6 (otherwise add tasks) |
| V9 Human spot check | Read 10 substitution chains end to end | The recorded consequence matches what a person concludes from the text |
| V10 Baseline sanity | Small-only and large-only accuracy on the workflow | Matches WP9 calibration within CI |

V8 matters most for explanation: if two halves of the data disagree about which
nodes are critical, the labels are noise and no predictor built on them means
anything.

### 13.3 Tweak: a protocol that improves results without fooling you

1. **Split the tasks once and freeze it.** From the 300-task GSM8K working set:
   100 tasks for development (tweak freely), 200 for final evaluation (touch once
   per frozen configuration). Save ids in `data/tasks/split.json`. Workflows are
   still split leave-one-workflow-out for H2.
2. **Iterate on the dev split with the cache.** Most tweaks (features, predictor
   hyperparameters, allocation granularity, corruption strategies) reuse cached
   generations and cost no GPU time. Only changes to prompts, models, or
   temperatures require new generations.
3. **Change one thing at a time** and log it in `RESULTS.md` under
   "Changes made since last run and why", with the dev-split effect.
4. **Freeze, then evaluate.** When a configuration is frozen, run it once on the
   200 evaluation tasks. That is the number you report. Report how many
   configurations you tried.
5. **Know which knobs are legitimate.** Good tweaks improve the method for a
   stated reason (a better probe layer, a feature a trace shows is missing, a
   stronger corruption that V4 shows is needed). Bad tweaks change the question
   (dropping hard tasks, changing the pass threshold, picking the one seed that
   won).

Tweak priority, based on the current simulator results:

| Order | Knob | Why first | Cost |
|---|---|---|---|
| 1 | Corruption strength (V4) | Weak corruptions flatten consequence and break everything downstream | new generations |
| 2 | Probe layer and pooling | Largest expected effect on H2; TRAIL found middle layers best for its target | cache only |
| 3 | Predictor features (upstream disagreement, prompt length, depth) | Traces will show what the model misses | cache only |
| 4 | Workflow depth (3 vs 5 steps) | Shallow workflows concentrate all consequence in the aggregator | new generations |
| 5 | Allocation granularity (finer budget steps, a middle fidelity) | Current H3 fails partly from coarse steps | cache plus a few calls |
| 6 | Model pair (14B large) | Only if WP9 gap is under 10 points | new generations |

### 13.4 What the first update to Dr. Liu contains

1. Calibration table (WP9): small vs large accuracy and latency with CIs.
2. H1: per-role consequence with CIs, the absorption table, and two casebook
   examples (one propagating error, one absorbed).
3. H2: LOWO Spearman against three baselines with paired CIs, permutation
   importance, and predictor overhead in milliseconds.
4. H3: accuracy vs GPU-seconds curves with the oracle bound, and the allocation
   trace at the budget where the policies differ most.
5. The validation table (V1 to V10), all PASS.
6. A short list of tweaks tried on the dev split and their effects.
7. H4 traces from the same VM lease (two-sided cost on real vLLM).
8. The SU ledger so far, and the next step: the multi-GPU runtime on bare metal.

---

## Appendix A. New and changed files

| File | Status | WP |
|---|---|---|
| `scripts/run_agentqo.py` | change: `--ec-source`, `--seeds`, `--loads` | WP0.2, WP0.3 |
| `agentqo/simulator/task_model.py` | change: `embedding_signal` option on MockBackend | WP0.4 |
| `agentqo/tasks/datasets.py`, `answers.py`, `real_task_model.py`, `prompts.py` | new | WP1, WP2 |
| `agentqo/workflows/library.py` | change: `answer_nodes` per workflow | WP2 |
| `agentqo/backends/vllm_http.py` | change: prompt_fn, endpoints map, seed, usage capture | WP2, WP5, WP8 |
| `agentqo/labeling/ec_labeler.py` | change: `mode="substitute"`, guard for real backends | WP3 |
| `agentqo/labeling/corruptions.py` | new | WP3 |
| `agentqo/executor.py` | change: `skip_forced_execution` | WP3 |
| `agentqo/labeling/p_err.py` | new | WP4 |
| `agentqo/backends/cache.py` | new | WP5 |
| `agentqo/backends/probe.py`, `composite.py` | new | WP6 |
| `agentqo/backends/fake_server.py` | new (test double) | WP7 |
| `agentqo/backends/ollama_backend.py` | new | WP7b |
| `configs/phase_b.yaml` | new (frozen config used on Chameleon) | WP7b |
| `scripts/phase_b_session.sh`, `scripts/phase_c_session.sh` | new (unattended lease sessions) | Section 7 |
| `scripts/run_real_pipeline.py` | new | WP7, WP10 to WP12 |
| `scripts/run_calibration.py` | new | WP9 |
| `agentqo/runtime/realtime_cluster.py` | new | WP13 |
| `agentqo/runtime/system.py` | change: async dispatch in realtime mode | WP13 |
| `scripts/run_h4_real_traces.py`, `agentqo/predictors/trace_adapter.py` | new | WP14 |
| `scripts/run_runtime_hw.py` | new | WP15 |
| `scripts/make_report.py`, `RESULTS.md` | new | WP16 |
| `agentqo/analysis/` (traces, casebook, absorption, explain) | new | Section 13 |
| `scripts/validate_pipeline.py` | new | Section 13 |
| `tests/test_no_leakage.py`, `test_substitution.py`, `test_cache.py`, `test_answers.py`, `test_realtime_cluster.py` | new | WP1 to WP13 |

## Appendix B. Command sequence

```bash
# Phase A (laptop)
pytest tests/ -q
python scripts/run_h3_allocation.py --num-runs 30 --oracle
python scripts/run_agentqo.py --ec-source predicted --seeds 5 --loads low,med,high
python scripts/run_h2_predictor.py --embedding-signal none
python scripts/run_real_pipeline.py --backend fake --n-tasks 10

# Phase A2 (Mac, Ollama running with qwen2.5:1.5b and qwen2.5:7b)
python scripts/run_real_pipeline.py --backend ollama --n-tasks 5 --stage smoke
python scripts/validate_pipeline.py --backend ollama --n-tasks 20
python scripts/run_real_pipeline.py --backend ollama --n-tasks 30 --split dev

# Phase B (GPU node, servers running)
export VLLM_ENDPOINTS='{"small":"http://localhost:8001","large":"http://localhost:8002"}'
python scripts/run_calibration.py --n-tasks 300
python scripts/run_real_pipeline.py --backend vllm --n-tasks 200 --stage h1
python scripts/run_real_pipeline.py --backend vllm --stage h2 --layer-sweep
python scripts/run_real_pipeline.py --backend vllm --stage h3 --oracle

# Phase C (multi-GPU node)
python scripts/run_h4_real_traces.py --gpus 0,1 --repeats 5
python scripts/run_runtime_hw.py --gpus 0,1 --seeds 5 --loads low,med,high

# Report
python scripts/make_report.py
```

## Appendix C. RESULTS.md template

```markdown
# AgentQO Results

## Environment
- Commit:
- Chameleon site / node type / GPU / driver / CUDA:
- vLLM version:
- Models (small / large / probe):
- SU used this phase (see ledger):

## Gate summary
| Gate | Result | Key number (95% CI) | n |
|---|---|---|---|
| CAL | | | |
| H1 | | | |
| H2 | | | |
| H3 | | | |
| H4 | | | |
| RT | | | |

## SU ledger (hard cap 1,000)
| Date | Hardware | Hours | SU | Cumulative | What ran |
|---|---|---|---|---|---|

## Per-experiment entries
### <Exp id> <date>
- Config:
- Result:
- Figure:
- Interpretation (one paragraph):
- Changes made since last run and why:
```

## Appendix D. Example prompt templates (math workflow)

Planner:
```
You are planning how to solve a math word problem. Do not solve it.
Problem: {problem}
Write a numbered plan of at most {n_steps} computation steps.
Start your answer with "PLAN:".
```

Step i:
```
Problem: {problem}
Plan:
{plan}
Results so far:
{prior_results}
Carry out step {i} only. Show the calculation briefly.
End with "RESULT: <number>".
```

Aggregator:
```
Problem: {problem}
Step results:
{step_results}
State the final answer. End with "#### <number>".
```

Verifier:
```
Problem: {problem}
Proposed solution:
{aggregator_output}
Check the solution. If it is wrong, correct it.
Write "VERDICT: correct" or "VERDICT: incorrect", then end with "#### <number>".
```
