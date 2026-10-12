# Where Do Errors Matter in a Multi-Agent LLM Workflow?
## H1 on Real Models: Epistemic Criticality with Qwen2.5 on GSM8K

**Shusmoy Chowdhury**
Laptop pilot with Ollama, October 11, 2026

---

## 1. The question

A multi-agent LLM workflow is a small graph of model calls. A planner writes a plan, a few workers carry out steps, something combines their results, and often a verifier checks the answer at the end. Every one of these calls can be wrong. The question behind this work is simple: **are they all equally worth protecting?**

If they are, a serving system has no choice but to treat every call the same. If they are not, then compute should be spent unevenly: a larger model, more samples, or a verification pass for the calls whose mistakes actually reach the final answer, and the cheapest option everywhere else.

I call the property **epistemic criticality (EC)**. Informally, a node is critical if it fails often *and* its failures change the final answer.

**H1** is the first and most basic hypothesis of the AgentQO project:

> **H1: Epistemic criticality varies substantially across the nodes of a workflow.**

If H1 fails, there is nothing to schedule and the rest of the project has no foundation. If it holds, the next questions are whether we can predict EC cheaply (H2) and whether spending by EC beats the alternatives (H3).

H1 had already passed in my CPU simulator. But the simulator was built by me, and in it, criticality followed graph position almost perfectly (correlation with downstream reach of +0.95). That left the obvious objection open: *is EC just a fancy name for "how many nodes sit below this one"?* Only real models can answer that, which is what this report is about.

---

## 2. How EC is measured

EC is measured by **fault injection**, never assumed.

For each task and each node:

1. **Baseline.** Run the whole workflow normally and record whether the final answer is correct.
2. **Substitute.** Replace that node's output with a corrupted version (a wrong but plausible answer), then re-run only the nodes downstream of it. Everything upstream is reused from the cache, so the comparison is exact.
3. **Compare.** The drop in final accuracy is the node's **consequence**: how much the final answer suffers when this node is wrong.

Separately, each node is sampled several times to estimate **p_err**, how often it is wrong on its own.

The two combine into the label:

> **EC = consequence × p_err**

The product matters. A node that is never wrong does not need protection, however bad its failure would be. A node that is often wrong but whose errors are always repaired downstream does not need protection either.

Two quality checks come with every run:

- **key_change** is the fraction of corruptions that actually changed the node's answer. If it were low, the "faults" would not be faults.
- **baseline_acc** is the workflow's normal accuracy. If it is near 0 or near 1, no single node can move the outcome and the experiment says nothing.

Confidence intervals are 95% bootstrap intervals over tasks.

---

## 3. Setup

| Item | Value |
|---|---|
| Hardware | 2023 MacBook Pro, 18 GB unified memory, Apple GPU via Ollama |
| Small model | `qwen2.5:1.5b-instruct` |
| Large model | `qwen2.5:7b-instruct` |
| Task | GSM8K grade-school math, test problems (dev split) |
| Tasks per workflow | 10 (pilot), then 30 |
| Corruptions per node | 2 |
| Samples per node for p_err | 3 |
| Max output tokens | 256 (no outputs came close; longest seen was 139) |
| Concurrency | 2 workers |
| Caching | Every generation stored in SQLite; reruns make no new calls |

A smoke test confirmed the plumbing before any labeling. Both models followed the prompt formats, Ollama returned real token log-probabilities (so confidence comes from logprobs, not a fallback), and reruns were served entirely from the cache. Latency was about 1 to 1.5 s per call for the 1.5B model and 5 to 13 s for the 7B model.

### The two workflows

The prompts determine what each agent is allowed to see and do, and that turns out to matter a lot, so I describe them concretely.

**Math (planner, 3 steps, aggregator, verifier)**

| Node | What it sees | What it does |
|---|---|---|
| planner | the problem | writes a numbered plan, told not to solve |
| step_1, step_2, step_3 | problem, plan, results so far | carry out one step, end with a number |
| aggregator | problem and step results | states the final answer |
| verifier | **problem** and proposed solution | checks it and **corrects it if wrong**, then writes the final number |

**Self-consistency (encoder, 3 samplers, vote)**

| Node | What it sees | What it does |
|---|---|---|
| prompt_encoder | the problem | restates it and lists the quantities, told not to solve |
| sampler_1, 2, 3 | problem and the encoder's notes | each solves the problem independently |
| aggregator | the three answers | majority vote, computed in code (not an LLM) |

### Cost

The full set of runs made about 4,160 model calls and took roughly 2.5 hours of laptop time: about 1 hour for the 10-task pilot on both workflows, and about 1.5 hours to extend both to 30 tasks. The final tie-break experiment (Section 6) made zero new calls.

---

## 4. Results at a glance

| Workflow | Tasks | Baseline acc | Range | CV | key_change | Gate |
|---|---|---|---|---|---|---|
| Math | 10 | 0.50 | 0.450 | 0.94 | 0.97 | False |
| Math | **30** | **0.47** | **0.383** | **1.28** | **0.98** | False |
| Self-consistency (first-answer ties) | 10 | 0.50 | 0.650 | 0.77 | 1.00 | True |
| Self-consistency (first-answer ties) | 30 | 0.53 | 0.383 | 0.42 | 1.00 | True |
| Self-consistency (**fair ties**) | **30** | **0.53** | **0.267** | **0.26** | **1.00** | **True** |

The pre-registered H1 thresholds are a range above 0.10 and a coefficient of variation above 0.20. **Every run clears both.** Baseline accuracy sits near 0.5 everywhere, which is the ideal range for this experiment, and corruptions change the targeted answer 97 to 100% of the time, so the fault injection is doing what it should.

The math gate reports `False` despite clearing both thresholds. I discuss why in Section 5.4. In short, I believe it is the simulator's built-in expectation about *which* nodes should be critical that fails, and that failure is itself the main finding.

---

## 5. Finding 1: in the math workflow, the verifier is the single point of failure

### 5.1 The numbers

Math workflow, 30 tasks:

| Node | Consequence (95% CI) | p_err | EC |
|---|---|---|---|
| **verifier** | **+0.350 [+0.150, +0.550]** | 0.73 | **0.257** |
| aggregator | +0.167 [+0.017, +0.333] | 0.36 | 0.059 |
| step_2 | +0.050 [−0.100, +0.217] | 0.66 | 0.033 |
| planner | +0.067 [−0.117, +0.233] | 0.40 | 0.027 |
| step_3 | +0.000 [−0.183, +0.183] | 0.47 | 0.000 |
| step_1 | −0.033 [−0.150, +0.117] | 0.53 | −0.018 |

Only two nodes have consequence intervals that exclude zero, and both sit at the end of the graph. The verifier dominates: when it is wrong, the final answer drops by 35 points. The aggregator is a clear second at about 17 points. The planner and all three steps are statistically indistinguishable from zero. Corrupting them barely changes the final answer.

The verifier's interval [0.15, 0.55] does not overlap step 1's [−0.15, 0.12]. That is a real separation, not noise, even at 30 tasks.

### 5.2 This is the opposite of what the simulator predicted

| | Simulator | Real models |
|---|---|---|
| Most critical | planner (0.58), step 1, step 2 | **verifier (0.35)**, aggregator (0.17) |
| Least critical | verifier (0.06) | planner, steps 1 to 3 (all about 0) |
| Ordering follows downstream reach? | Yes, almost perfectly | **No, roughly reversed** |

In the simulator, an early error poisoned everything below it, so the planner mattered most. With real models, early errors mostly disappear, and the last node carries almost all the risk.

### 5.3 Why: the prompts let late agents repair earlier work

The explanation is in the prompts in Section 3, not in the graph.

The verifier is given the **original problem** along with the proposed solution, and it is told to **correct the solution if it is wrong** and write the final number itself. In effect, it re-solves the problem. The aggregator also sees the original problem. So when the planner or a step goes wrong, the later agents have both the information and the permission to fix it, and often do. That is why upstream consequence is near zero.

The same mechanism makes the verifier dangerous. It has the last word, and nothing comes after it. If it is wrong, its answer goes straight out. Its high error rate (p_err 0.73 with the 1.5B model) multiplied by its large consequence gives it by far the highest EC.

The general lesson I take from this:

> **In real LLM workflows, criticality is set by what each agent is allowed to see and override, not by where it sits in the graph.** Agents that re-read the original input and can rewrite the answer absorb upstream errors and become single points of failure.

A structural scheduler would protect the planner here. EC says protect the verifier.

### 5.4 Why the gate says False

Range (0.38) and CV (1.28) both pass by a wide margin, and the top and bottom intervals do not overlap. The `False` most likely comes from the smoke test that the simulator runs alongside H1, which checks that a "critical" role such as the planner beats the verifier (in the simulator: 0.580 vs 0.062). That check encodes the simulator's assumption about ordering, and the real models invert it. I still need to confirm this in the gate code. If confirmed, the right way to report it is: **the variation test passes; the ordering the simulator assumed is wrong for real models.**

### 5.5 Ten tasks would have misled me

| Node | 10 tasks | 30 tasks |
|---|---|---|
| verifier | +0.30 | +0.35 |
| aggregator | +0.30 | +0.17 |
| step_3 | **+0.25** | **+0.00** |
| planner | +0.20 | +0.07 |
| step_1 | **−0.15** | **−0.03** |

At 10 tasks, step 3 looked important and step 1 looked oddly harmful to corrupt. Both were noise. With 30 tasks, step 3 is exactly zero and step 1 is essentially zero. The overall story (late nodes matter, early nodes do not) survived, but the details did not. Any claim at the level of a single mid-graph node needs more than 10 tasks.

---

## 6. Finding 2: a one-line voting rule created a "critical" sampler

### 6.1 The puzzle

The three samplers in the self-consistency workflow are interchangeable by design: same prompt, same model, same inputs, same position in the graph. They should come out equally critical. They did not:

| Node | 10 tasks | 30 tasks |
|---|---|---|
| sampler_1 | **+0.70 [+0.40, +1.00]** | **+0.600 [+0.400, +0.767]** |
| sampler_2 | +0.05 [0.00, +0.15] | +0.283 [+0.133, +0.450] |
| sampler_3 | +0.10 [0.00, +0.30] | +0.233 [+0.100, +0.400] |

Sampler 1 mattered about twice as much as the others, and the gap held up at 30 tasks.

### 6.2 The hypothesis

The aggregator is a majority vote in code. Its p_err is exactly 0.00, which confirms it is deterministic. The code used Python's `Counter.most_common`, and the source carried the comment *"ties go to the first answer seen."*

With a 1.5B model that is wrong about half the time, the three samplers frequently produce three different answers. In a three-way tie, the vote returns sampler 1's answer. So sampler 1 was quietly acting as the tie-breaker, and it effectively decided every disagreement. A model-level explanation was not needed.

### 6.3 The test, with a prediction stated in advance

I changed one line so that ties are broken by a hash of the answer *value* rather than by sampler order. This makes the vote symmetric: swapping samplers can no longer change the outcome. If the hypothesis was right, sampler 1's extra weight should spread evenly, and each sampler should land near the average of the three original values:

> **Prediction: (0.600 + 0.283 + 0.233) / 3 ≈ 0.37 for each sampler.**

Because the vote is code and every model output was already cached, the rerun used **exactly the same LLM outputs** and made **zero new model calls**. The only thing that changed was the tie-break rule.

### 6.4 The result

| Node | First-answer tie-break | **Fair tie-break** |
|---|---|---|
| sampler_1 | 0.600 [0.400, 0.767] | **0.383 [0.217, 0.550]** |
| sampler_2 | 0.283 [0.133, 0.450] | **0.433 [0.266, 0.617]** |
| sampler_3 | 0.233 [0.100, 0.400] | **0.300 [0.150, 0.467]** |
| Sampler mean | 0.372 | **0.372** |
| prompt_encoder | 0.217 | 0.233 |
| aggregator | 0.483 | 0.500 |

The prediction held. The sampler mean is 0.372, the three intervals now overlap heavily, and no sampler stands out. The nodes the tie-break should not affect (encoder and aggregator) barely moved.

### 6.5 What it means

This is a controlled experiment in the strict sense: identical model outputs, one line of code changed, a prediction stated beforehand and confirmed. It shows two things.

First, **EC depends on implementation details that no structural feature can see.** In the graph, the three samplers are identical, so any structure-based scheduler must treat them identically. Fault injection found that one of them carried twice the risk, and found it for a reason (the tie-break) that lives in a single line of code.

Second, it is a useful warning for how to read EC labels. A surprising criticality pattern can be an artifact of the workflow's implementation rather than a property of the model. **EC is a diagnostic tool as much as a scheduling signal**: here, it surfaced a bias in the voting rule that I would not otherwise have noticed.

After the fix, the samplers are genuinely interchangeable, so for this workflow structure is an adequate proxy. The structure-defying evidence comes from the math verifier.

---

## 7. Finding 3: high consequence does not mean high criticality

The self-consistency aggregator has the highest consequence in its workflow (0.50): if the vote produced a wrong answer, the final answer would be wrong. But it never does. It is deterministic code with p_err of 0.00, so its EC is exactly zero.

This is the reason EC multiplies consequence by error rate. A scheduler that ranked nodes by "how bad would a failure be" alone would waste its budget protecting the one node that cannot fail. The math verifier is the mirror image: high consequence *and* a high error rate, which is what makes it the right place to spend.

---

## 8. What H1 tells us, overall

| Claim | Evidence | Strength |
|---|---|---|
| EC varies substantially across nodes in real workflows | Range and CV clear the thresholds in every run | Strong |
| Real EC does not follow graph structure | Math: verifier highest, planner near zero; reversed relative to the simulator | Strong for this workflow; one workflow so far |
| Agents that can re-read the input and override earlier work absorb upstream errors | Verifier and aggregator prompts; upstream consequence near zero | Plausible mechanism, not yet tested causally |
| EC depends on implementation details invisible to structure | Tie-break experiment with a confirmed prediction | Strong (controlled) |
| Consequence alone is the wrong ranking signal | Aggregator: highest consequence, zero EC | Strong (by construction, but shows up clearly in real data) |

**H1 holds on real models.** More importantly, the simulator's picture of *why* it holds was wrong. Criticality in real workflows is driven by agent roles and permissions, and by implementation details, much more than by graph position. That is the strongest argument so far for why AgentQO needs measured or learned criticality rather than structural heuristics.

---

## 9. Limitations

I want to be explicit about what this pilot cannot show.

- **Small models.** 1.5B and 7B Qwen models. Larger models make fewer errors and may repair upstream mistakes even more reliably, which could strengthen or change the verifier effect.
- **One task family.** GSM8K only. Tasks where agents cannot easily re-derive the answer from the original input (long documents, tool use, retrieval) may behave very differently, and may restore the importance of early nodes.
- **Two workflows, 30 tasks each.** Enough for the big effects here, not for fine distinctions between mid-graph nodes. Section 5.5 shows what 10 tasks can do.
- **Light fault injection.** 2 corruptions and 3 samples per node. The style of corruption matters: a plausible wrong number is one kind of fault, and agents may handle other kinds (garbled text, confident nonsense) differently. key_change near 1.0 shows the corruptions do bite.
- **The verifier's high error rate deserves a closer look.** A p_err of 0.73 may partly reflect how strictly the pipeline judges verifier outputs. If the checker is too strict, the verifier's EC is inflated.
- **A small unexplained difference.** The prompt encoder's p_err moved from 0.66 to 0.61 between the two tie-break runs, even though no model outputs changed. This likely means p_err is computed in a way that touches downstream results, and I need to check it.
- **The math gate interpretation is not yet confirmed** in code (Section 5.4).
- **Single seed and Ollama serving.** vLLM on real GPUs will be needed for the systems experiments, though it should not change correctness labels.

---

## 10. Next steps

**A causal test of the verifier mechanism.** If the verifier matters because it re-reads the problem and is allowed to correct the answer, then removing that permission should change the picture. I will run a version where the verifier may only output "correct" or "incorrect" and cannot rewrite the answer. **Prediction:** upstream nodes, especially the aggregator and the last step, become much more critical, and the verifier's consequence drops. This is cheap because the upstream generations are cached.

**Real-model H3 on math.** On the same 30 tasks, compare four plans: all small, all large, only the verifier upgraded to 7B, and only the planner upgraded (what the simulator would choose). If upgrading the verifier alone recovers most of the all-large accuracy at a fraction of the cost, the core AgentQO claim is demonstrated on real models.

**H2 with real hidden states.** Extract hidden-state embeddings for the cached generations and test whether they predict EC better than structure. The math workflow is the right test case, because structure gets it wrong.

**Confidence versus criticality.** Compare each node's logprob confidence with its EC. If low confidence does not line up with high EC, that is real-model evidence for the project's central claim that "uncertain" and "important" are different things.

**Broaden.** Add the multi-hop QA and complex workflows, then move to Chameleon for more tasks, larger models, and vLLM, where the multi-GPU scheduling experiments live.

---

## Appendix: raw H1 outputs

**Math, 10 tasks** (baseline 0.50, range 0.450, CV 0.943, key_change 0.97)

| Node | Consequence | p_err | EC |
|---|---|---|---|
| planner | +0.200 [−0.150, +0.500] | 0.43 | +0.087 |
| step_1 | −0.150 [−0.400, +0.150] | 0.67 | −0.100 |
| step_2 | +0.100 [−0.100, +0.350] | 0.70 | +0.070 |
| step_3 | +0.250 [+0.050, +0.500] | 0.67 | +0.167 |
| aggregator | +0.300 [+0.100, +0.500] | 0.30 | +0.090 |
| verifier | +0.300 [+0.000, +0.600] | 0.77 | +0.230 |

**Self-consistency, 10 tasks, first-answer ties** (baseline 0.50, range 0.650, CV 0.773, key_change 1.0)

| Node | Consequence | p_err | EC |
|---|---|---|---|
| prompt_encoder | +0.250 [−0.050, +0.550] | 0.77 | +0.192 |
| sampler_1 | +0.700 [+0.400, +1.000] | 0.60 | +0.420 |
| sampler_2 | +0.050 [+0.000, +0.150] | 0.60 | +0.030 |
| sampler_3 | +0.100 [+0.000, +0.300] | 0.60 | +0.060 |
| aggregator | +0.450 [+0.100, +0.800] | 0.00 | +0.000 |

**Math, 30 tasks** (baseline 0.47, range 0.383, CV 1.280, key_change 0.983): see Section 5.1.

**Self-consistency, 30 tasks, first-answer ties** (baseline 0.53, range 0.383, CV 0.418, key_change 1.0)

| Node | Consequence | p_err | EC |
|---|---|---|---|
| prompt_encoder | +0.217 [+0.067, +0.383] | 0.66 | +0.142 |
| sampler_1 | +0.600 [+0.400, +0.767] | 0.50 | +0.300 |
| sampler_2 | +0.283 [+0.133, +0.450] | 0.54 | +0.154 |
| sampler_3 | +0.233 [+0.100, +0.400] | 0.54 | +0.127 |
| aggregator | +0.483 [+0.283, +0.683] | 0.00 | +0.000 |

**Self-consistency, 30 tasks, fair ties** (baseline 0.53, range 0.267, CV 0.255, key_change 1.0, 0 new model calls)

| Node | Consequence | p_err | EC |
|---|---|---|---|
| prompt_encoder | +0.233 [+0.067, +0.383] | 0.61 | +0.143 |
| sampler_1 | +0.383 [+0.217, +0.550] | 0.50 | +0.192 |
| sampler_2 | +0.433 [+0.266, +0.617] | 0.54 | +0.236 |
| sampler_3 | +0.300 [+0.150, +0.467] | 0.54 | +0.163 |
| aggregator | +0.500 [+0.317, +0.700] | 0.00 | +0.000 |

Logs: `logs/11_ollama_smoke.txt`, `logs/12_ollama_h1.txt`, `logs/14_ollama_h1_n30.txt`, `logs/15_ollama_sc_fairtie.txt`. Artifacts: `data/ollama/h1`, `data/ollama/h1_n30`, `data/ollama/h1_n30_fairtie`.
