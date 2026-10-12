# Where Do Errors Matter in a Multi-Agent LLM Workflow?
## H1 on Real Models: Epistemic Criticality, Repair, and Why Structure Is Not Enough

**Shusmoy Chowdhury**
Laptop study with Ollama (Qwen2.5 1.5B and 7B on GSM8K), October 11, 2026

---

## Summary

AgentQO rests on one idea: in a workflow of LLM agents, some calls matter much more than others, so compute should be spent where errors actually reach the final answer. I call this property **epistemic criticality (EC)**. The first hypothesis, H1, is that EC varies substantially across the agents of a workflow.

My simulator supported H1, but in it, criticality simply followed graph position. This study tests H1 with real models and asks the harder question: **is criticality anything more than "how many agents sit below this one"?**

The main findings:

1. **H1 holds on real models.** Criticality varies strongly across agents in every configuration I tested.
2. **In a math workflow with a verifier, the ordering is the reverse of the simulator's.** The verifier, last in the graph, is the most critical agent. The planner and all intermediate steps are indistinguishable from zero.
3. **The cause is repair.** The verifier re-reads the original problem and may rewrite the answer. It changes 63% of answers, fixing 7 and breaking 2 out of 30, for a net gain of 17 accuracy points. In doing so, it absorbs upstream errors.
4. **A clean causal test confirms it.** When the verifier is replaced by a code passthrough, using identical cached model outputs, every upstream agent becomes clearly critical, and the ordering snaps back to exactly what graph structure predicts.
5. **Criticality also depends on code details invisible in the graph.** A one-line tie-break rule in a majority vote made one of three identical samplers look twice as critical. Fixing that rule removed the asymmetry, matching a prediction made before the rerun.
6. **High consequence is not high criticality.** A node that is harmful when wrong but is never wrong has zero EC.

The unifying result:

> **Graph structure predicts criticality only when no agent can repair upstream errors. Add one agent that re-reads the input and may override the answer, and the ordering inverts.**

A scheduler that relies on structural rules will get one of these two regimes wrong. That is the strongest evidence so far for why AgentQO needs measured or learned criticality.

---

## 1. The question

A multi-agent workflow is a small graph of model calls: a planner, a few workers, something that combines their results, and often a verifier at the end. Each call can be wrong. If all calls mattered equally, a serving system would have no choice but to treat them the same. If they do not, compute should be spent unevenly: a larger model, more samples, or extra checking for the calls whose mistakes reach the answer, and the cheapest option everywhere else.

**H1: Epistemic criticality varies substantially across the nodes of a workflow.**

H1 comes first because everything else depends on it. If it fails, there is nothing to schedule. If it holds, the next questions are whether EC can be predicted cheaply (H2) and whether spending by EC beats the alternatives (H3).

In my CPU simulator, H1 held, but criticality correlated with downstream reach at +0.95. That left an obvious objection: *maybe EC is just graph position under another name.* If so, no learned predictor is needed, because a structural rule would do. Only real models can settle this.

---

## 2. How EC is measured

EC is measured by fault injection, never assumed.

For each task and each node:

1. **Baseline.** Run the workflow normally and record whether the final answer is correct.
2. **Substitute.** Replace that node's output with a corrupted one (a plausible wrong answer), then re-run only the nodes downstream of it. Upstream outputs come from the cache, so the comparison is exact.
3. **Compare.** The effect on the final answer is the node's **consequence**.

Separately, each node is sampled several times to estimate **p_err**, how often it is wrong on its own. The label is:

> **EC = consequence × p_err**

The product is deliberate. A node that is never wrong needs no protection, however bad its failure would be. A node that is often wrong but always repaired downstream needs no protection either.

Two quality checks accompany every run:

- **key_change**, the fraction of corruptions that actually changed the node's answer. Low values would mean the faults are not real faults.
- **baseline_acc**, the workflow's normal accuracy. Near 0 or 1, no single node can move the outcome.

Intervals are 95% bootstrap intervals over tasks.

---

## 3. Setup

| Item | Value |
|---|---|
| Hardware | 2023 MacBook Pro, 18 GB unified memory, models on the Apple GPU via Ollama |
| Small model | `qwen2.5:1.5b-instruct` |
| Large model | `qwen2.5:7b-instruct` |
| Task | GSM8K grade-school math, dev split |
| Tasks | 10 (pilot), then 30 per configuration |
| Fault injection | 2 corruptions per node, 3 samples per node for p_err |
| Output limit | 256 tokens (longest output seen: 139) |
| Concurrency | 2 workers |
| Caching | Every generation stored in SQLite; reruns make no new calls |

A smoke test confirmed both models followed the prompt formats, Ollama returned real token log-probabilities, and reruns came entirely from the cache. Latency was about 1 to 1.5 s per call for the 1.5B model and 5 to 13 s for the 7B model.

### The workflows

What each agent is allowed to see and do turns out to be central, so the prompts matter.

**Math (planner, 3 steps, aggregator, verifier)**

| Node | Sees | Does |
|---|---|---|
| planner | the problem | writes a numbered plan; told not to solve |
| step_1, step_2, step_3 | problem, plan, results so far | carry out one step |
| aggregator | problem and step results | states the final answer |
| verifier | **the problem** and the proposed solution | checks it and **corrects it if wrong**, then writes the final number |

**Self-consistency (encoder, 3 samplers, vote)**

| Node | Sees | Does |
|---|---|---|
| prompt_encoder | the problem | restates it and lists quantities; told not to solve |
| sampler_1, 2, 3 | problem and the encoder's notes | each solves independently |
| aggregator | the three answers | majority vote in code |

### Cost

About 4,700 model calls and roughly 3 hours of laptop time in total. Three of the experiments (the tie-break fix, the passthrough ablation, and the verifier change analysis) made **zero** new model calls, because the cache let me change code while holding every model output fixed.

---

## 4. All runs at a glance

| Run | Tasks | Baseline acc | Range | CV | key_change | Gate |
|---|---|---|---|---|---|---|
| Math, original verifier | 10 | 0.50 | 0.450 | 0.94 | 0.97 | False |
| Math, original verifier | **30** | **0.47** | 0.383 | 1.28 | 0.98 | False |
| Math, judge-only verifier (failed ablation) | 30 | 0.17 | 0.233 | 0.56 | 0.98 | False |
| Math, **passthrough verifier** | **30** | **0.30** | 0.283 | 0.33 | 0.98 | **True** |
| Self-consistency, first-answer ties | 10 | 0.50 | 0.650 | 0.77 | 1.00 | True |
| Self-consistency, first-answer ties | 30 | 0.53 | 0.383 | 0.42 | 1.00 | True |
| Self-consistency, **fair ties** | **30** | **0.53** | 0.267 | 0.26 | 1.00 | True |

The pre-registered H1 thresholds are a range above 0.10 and a CV above 0.20. **Every run clears both.** Corruptions change the targeted answer 97 to 100% of the time.

The gate's `False` on the original math runs is explained in Section 7.5.

---

## 5. Finding 1: criticality varies a lot

In every run, some agents' errors change the final answer far more often than others'. The spread is large (ranges of 0.23 to 0.65), not marginal. **H1 holds on real models.** The rest of this report is about *why* it holds, which turns out to be the more important question.

---

## 6. Finding 2: with a repairing verifier, the ordering inverts

### 6.1 The numbers

Math workflow, original verifier, 30 tasks:

| Node | Consequence (95% CI) | p_err | EC |
|---|---|---|---|
| **verifier** | **+0.350 [+0.150, +0.550]** | 0.73 | **0.257** |
| aggregator | +0.167 [+0.017, +0.333] | 0.36 | 0.059 |
| step_2 | +0.050 [−0.100, +0.217] | 0.66 | 0.033 |
| planner | +0.067 [−0.117, +0.233] | 0.40 | 0.027 |
| step_3 | +0.000 [−0.183, +0.183] | 0.47 | 0.000 |
| step_1 | −0.033 [−0.150, +0.117] | 0.53 | −0.018 |

Only the last two nodes have intervals that exclude zero. The verifier dominates. The planner and every step are indistinguishable from zero.

### 6.2 The opposite of the simulator

| | Simulator | Real models, repairing verifier |
|---|---|---|
| Most critical | planner (0.58) | **verifier (0.35)** |
| Least critical | verifier (0.06) | planner and steps (about 0) |
| Follows downstream reach? | Yes | **No, roughly reversed** |

### 6.3 Ten tasks would have misled me

| Node | 10 tasks | 30 tasks |
|---|---|---|
| step_3 | **+0.25** | **+0.00** |
| step_1 | **−0.15** | **−0.03** |
| aggregator | +0.30 | +0.17 |
| verifier | +0.30 | +0.35 |

At 10 tasks, step 3 looked important and step 1 looked oddly harmful to corrupt. Both were noise. The broad picture survived; the details did not.

---

## 7. Finding 3: the cause is repair, shown causally

The prompts suggested an explanation: the verifier sees the original problem and is told to correct the answer, so it can undo upstream mistakes. I tested this in three steps.

### 7.1 What the verifier actually does

Reading the saved baseline traces (no model calls), I compared the aggregator's answer with the verifier's final answer on all 30 tasks:

| | Count |
|---|---|
| Aggregator correct | 9 / 30 (0.30) |
| Verifier (final) correct | 14 / 30 (0.47) |
| **Verifier changed the answer** | **19 / 30 (63%)** |
| wrong → right (fixed) | **7** |
| right → wrong (broke) | 2 |
| wrong → a different wrong | 10 |

The verifier is not a light-touch checker. It rewrites nearly two answers in three, which means it is effectively re-solving the problem. Its fixes outnumber its breaks 7 to 2, a **net gain of 17 accuracy points**.

### 7.2 A first ablation that failed, and what it taught me

My first attempt kept the verifier as an LLM but told it to judge only: say "correct" or "incorrect," then repeat the proposed answer exactly. The 1.5B model did not comply:

| | Count |
|---|---|
| Changed the answer anyway | 13 / 30 (43%) |
| wrong → right | 1 |
| **right → wrong** | **5** |
| No usable number in the output | **7 / 30 (23%)** |
| Final accuracy | **0.17** (below the aggregator's 0.30) |

Instead of a neutral verifier, I got one that garbled answers. This run cannot test the hypothesis, and I exclude it from the conclusions. (When I first saw its accuracy drop from 0.47 to 0.17, I read it as the verifier being worth 30 points. The trace analysis showed that reading was wrong: the true contribution is 17 points, and the rest of the drop came from the judge actively doing damage.)

The failure is itself worth noting: **a 1.5B model told only to repeat an answer still changed it 43% of the time.** Small models are unreliable even as simple copy steps, which matters for anyone building workflows from them.

### 7.3 The clean ablation: passthrough in code

To remove the verifier's influence completely, I replaced it with a code passthrough that copies the aggregator's number. All upstream model outputs were reused from the cache, so this run made **zero new model calls**. The only change was whether a repair step exists.

Every check passed: baseline accuracy is exactly the aggregator's 0.30, the verifier changed 0 of 30 answers, and its p_err is 0.00.

**Prediction, stated before the run:** with no repair, upstream agents become critical.

| Node | Repairing verifier | **Passthrough (no repair)** | EC (passthrough) |
|---|---|---|---|
| planner | +0.067 [−0.117, +0.233] | **+0.333 [+0.133, +0.550]** | **0.215** |
| step_1 | −0.033 [−0.150, +0.117] | **+0.283 [+0.133, +0.450]** | 0.151 |
| step_2 | +0.050 [−0.100, +0.217] | **+0.200 [+0.050, +0.367]** | 0.131 |
| step_3 | +0.000 [−0.183, +0.183] | **+0.183 [+0.050, +0.317]** | 0.086 |
| aggregator | +0.167 [+0.017, +0.333] | **+0.467 [+0.283, +0.667]** | 0.166 |
| verifier | +0.350 [+0.150, +0.550] | +0.267, but never errs | 0.000 |

The prediction holds in full. Every upstream agent goes from indistinguishable-from-zero to clearly critical, with every interval excluding zero.

### 7.4 Structure comes back when repair goes away

Look at the order without repair: planner 0.33 > step 1 0.28 > step 2 0.20 > step 3 0.18. That is a clean decreasing sequence, exactly what downstream reach predicts, and the same pattern the simulator produced. The aggregator rises to the top because it now effectively writes the final answer.

So the three math runs together give a precise answer to the simulator's open question:

> **Is criticality just downstream reach? Yes, when no agent can repair upstream errors. No, when one can.**

The simulator was not wrong. It was modeling a workflow without repair.

### 7.5 The gate

The H1 gate reports `False` for the original math runs and `True` for the passthrough run, even though the variation thresholds pass in all of them. This is consistent with the gate's smoke test, which checks that critical upstream roles beat the verifier (the simulator's expected order). That order is true without repair and false with it. I still need to confirm this in the gate code, but the pattern across runs makes it very likely. If confirmed, the right report is: **the variation test passes everywhere; the expected ordering holds only when there is no repair step.**

---

## 8. Finding 4: a one-line voting rule created a "critical" sampler

### 8.1 The puzzle

The three samplers in the self-consistency workflow are identical by design. They did not come out equal:

| Node | 10 tasks | 30 tasks |
|---|---|---|
| sampler_1 | **+0.70 [+0.40, +1.00]** | **+0.600 [+0.400, +0.767]** |
| sampler_2 | +0.05 [0.00, +0.15] | +0.283 [+0.133, +0.450] |
| sampler_3 | +0.10 [0.00, +0.30] | +0.233 [+0.100, +0.400] |

### 8.2 The cause

The aggregator is a majority vote in code (p_err exactly 0.00). It used Python's `Counter.most_common`, and the source said so directly: *"ties go to the first answer seen."* With a 1.5B model wrong about half the time, three-way disagreements are common, and every one of them was settled by sampler 1.

### 8.3 The test

I changed one line so ties are broken by a hash of the answer value, which makes the vote symmetric in the samplers.

**Prediction, stated before the rerun:** sampler 1's extra weight spreads evenly, so each sampler lands near the average of the three original values, (0.600 + 0.283 + 0.233) / 3 ≈ **0.37**.

The rerun used identical model outputs (zero new calls):

| Node | First-answer ties | **Fair ties** |
|---|---|---|
| sampler_1 | 0.600 [0.400, 0.767] | **0.383 [0.217, 0.550]** |
| sampler_2 | 0.283 [0.133, 0.450] | **0.433 [0.266, 0.617]** |
| sampler_3 | 0.233 [0.100, 0.400] | **0.300 [0.150, 0.467]** |
| Sampler mean | 0.372 | **0.372** |
| prompt_encoder | 0.217 | 0.233 |
| aggregator | 0.483 | 0.500 |

The prediction holds: the mean is 0.372, the intervals overlap heavily, and the untouched nodes barely moved.

### 8.4 What it means

In the graph, the three samplers are identical, so any structure-based scheduler must treat them identically. Fault injection found that one carried twice the risk, for a reason that lives in one line of code. **Criticality depends on implementation details that structure cannot see.** It also shows that EC labels work as a diagnostic: they exposed a bias in the voting rule I would not otherwise have noticed.

After the fix, the samplers really are interchangeable, so in this workflow structure is an adequate proxy.

---

## 9. Finding 5: high consequence is not high criticality

The self-consistency aggregator has the highest consequence in its workflow (0.50). But it is deterministic code that never errs, so its EC is exactly zero. The passthrough verifier shows the same thing. A scheduler ranking nodes by "how bad would a failure be" would spend its budget protecting the nodes that cannot fail. The repairing math verifier is the opposite case: a high error rate *and* high consequence, which is what makes it the right place to spend.

---

## 10. Synthesis: the repair principle

Putting the findings together:

| Workflow regime | What drives criticality | Most critical | Does structure work? |
|---|---|---|---|
| No repair step (passthrough) | Errors propagate forward | Planner and early nodes, plus whoever writes the answer | **Yes** |
| A repairing step exists (verifier re-reads and may override) | Errors are absorbed by the repairer | **The repairer itself** | **No, roughly inverted** |
| Symmetric parallel branches with a vote | Depends on how the vote breaks ties | Whoever wins ties, if ties are not fair | **Only if the code is symmetric** |

**The trade-off of a repair step.** The verifier buys accuracy (0.30 → 0.47, net +17 points) but concentrates risk: it makes everything before it look unimportant and becomes the one place where errors go straight out.

**What this means for AgentQO.** Where to spend compute depends on the workflow's repair structure, which a scheduler cannot read off the graph:

| Workflow | Where AgentQO should spend |
|---|---|
| Math with a repairing verifier | Upgrade or double-check the **verifier** |
| Math without repair | Upgrade the **planner and aggregator** |

A structural rule ("protect the root") is right in the second case and wrong in the first. A confidence rule fares no better. This is the core motivation for measured or learned EC.

---

## 11. Notes on method

A few practices made this study more reliable than its size suggests, and I would keep them:

- **Caching enabled controlled experiments.** Because every generation was cached, I could change one thing in the code (the tie-break rule, the verifier) while holding every model output fixed. Three experiments cost zero new model calls.
- **Predictions were stated before reruns.** Both the tie-break value (≈0.37) and the passthrough outcome were written down first and then checked.
- **Counting beats inferring.** The trace analysis of the verifier corrected my own first reading of the failed ablation. Simple counts of what an agent actually did were more trustworthy than inferences from aggregate accuracy.
- **Sample size matters at the node level.** Ten tasks produced two spurious node-level effects that disappeared at thirty.

---

## 12. Limitations

- **Small models.** 1.5B and 7B Qwen. Larger models repair more reliably and fail less often, which could change magnitudes.
- **One task family.** GSM8K lets agents re-derive the answer from the problem. In tasks where later agents cannot easily do that (long documents, tool use, retrieval), repair may be weaker and early nodes may matter more.
- **Two workflows, 30 tasks each.** Enough for the large effects reported here, not for fine distinctions.
- **Light fault injection.** 2 corruptions and 3 samples per node. Other kinds of faults (garbled text, confident nonsense) may be repaired differently.
- **The verifier's p_err.** At 0.73 in the original run, it may partly reflect how strictly the pipeline judges a verifier's output. This could inflate its EC.
- **A small unexplained difference.** The prompt encoder's p_err moved from 0.66 to 0.61 between the two tie-break runs, though no model outputs changed. p_err may be computed in a way that touches downstream results, which I need to check.
- **The gate interpretation** is consistent across runs but not yet confirmed in code.
- **Single seed, Ollama serving.** vLLM on GPUs will be needed for the systems experiments, although correctness labels should not depend on the serving stack.

---

## 13. Next steps

1. **H3 on real models (running next).** On the same 30 tasks, compare all-small, all-large, verifier-only upgrade, planner-only upgrade, and the top two EC nodes upgraded. If upgrading the verifier alone recovers most of the all-large gain at a fraction of the cost, the core AgentQO claim is shown on real models. The passthrough result predicts the opposite choice would be right in a workflow without repair, which is a natural follow-up.
2. **More workflows.** Label the complex workflow and the multi-hop QA workflow. This tests whether the repair principle generalizes, and gives enough labeled workflows for H2.
3. **H2 with real hidden states.** Test whether hidden-state embeddings predict EC better than structure. The repair regime is the key test case, since structure gets it wrong.
4. **Confidence versus criticality.** Compare logprob confidence with EC per node, to test on real data whether "uncertain" and "important" diverge.
5. **Scale on Chameleon.** More tasks, larger models, and vLLM, then the multi-GPU scheduling experiments.

---

## Appendix A: raw H1 outputs

**Math, original verifier, 10 tasks** (baseline 0.50, range 0.450, CV 0.943, key_change 0.97)

| Node | Consequence | p_err | EC |
|---|---|---|---|
| planner | +0.200 [−0.150, +0.500] | 0.43 | +0.087 |
| step_1 | −0.150 [−0.400, +0.150] | 0.67 | −0.100 |
| step_2 | +0.100 [−0.100, +0.350] | 0.70 | +0.070 |
| step_3 | +0.250 [+0.050, +0.500] | 0.67 | +0.167 |
| aggregator | +0.300 [+0.100, +0.500] | 0.30 | +0.090 |
| verifier | +0.300 [+0.000, +0.600] | 0.77 | +0.230 |

**Math, original verifier, 30 tasks:** Section 6.1.

**Math, judge-only verifier, 30 tasks** (excluded from conclusions; baseline 0.17, range 0.233, CV 0.559, key_change 0.983, 571 new calls)

| Node | Consequence | p_err | EC |
|---|---|---|---|
| planner | +0.117 [−0.034, +0.300] | 0.74 | +0.087 |
| step_1 | +0.167 [+0.000, +0.333] | 0.53 | +0.089 |
| step_2 | +0.033 [−0.067, +0.167] | 0.66 | +0.022 |
| step_3 | +0.067 [−0.033, +0.183] | 0.47 | +0.031 |
| aggregator | +0.167 [+0.017, +0.317] | 0.36 | +0.059 |
| verifier | +0.267 [+0.100, +0.433] | 0.43 | +0.116 |

**Math, passthrough verifier, 30 tasks:** Section 7.3 (baseline 0.30, range 0.283, CV 0.326, key_change 0.983, 0 new calls).

**Self-consistency, first-answer ties, 10 tasks** (baseline 0.50, range 0.650, CV 0.773, key_change 1.0)

| Node | Consequence | p_err | EC |
|---|---|---|---|
| prompt_encoder | +0.250 [−0.050, +0.550] | 0.77 | +0.192 |
| sampler_1 | +0.700 [+0.400, +1.000] | 0.60 | +0.420 |
| sampler_2 | +0.050 [+0.000, +0.150] | 0.60 | +0.030 |
| sampler_3 | +0.100 [+0.000, +0.300] | 0.60 | +0.060 |
| aggregator | +0.450 [+0.100, +0.800] | 0.00 | +0.000 |

**Self-consistency, 30 tasks, both tie rules:** Section 8.3. Full p_err values: first-answer ties, prompt_encoder 0.66, samplers 0.50 / 0.54 / 0.54, aggregator 0.00. Fair ties: prompt_encoder 0.61, samplers 0.50 / 0.54 / 0.54, aggregator 0.00.

## Appendix B: verifier change analysis

| Run | Aggregator acc | Final acc | Changed | Fixed | Broke | Wrong → wrong | No number |
|---|---|---|---|---|---|---|---|
| Original verifier | 0.30 | 0.47 | 19/30 | 7 | 2 | 10 | 1 |
| Judge-only verifier | 0.30 | 0.17 | 13/30 | 1 | 5 | 7 | 7 |
| Passthrough | 0.30 | 0.30 | 0/30 | 0 | 0 | 0 | 0 |

## Appendix C: reproducibility

| Run | Command setting | Log | Artifacts |
|---|---|---|---|
| Smoke | `--stage smoke` | `logs/11_ollama_smoke.txt` | n/a |
| Pilot, 10 tasks | `--stage h1 --n-tasks 10 --workflows math,sc` | `logs/12_ollama_h1.txt` | `data/ollama/h1` |
| 30 tasks | `--stage h1 --n-tasks 30 --workflows math,sc` | `logs/14_ollama_h1_n30.txt` | `data/ollama/h1_n30` |
| Fair ties | same, with the hash tie-break in `code_output` | `logs/15_ollama_sc_fairtie.txt` | `data/ollama/h1_n30_fairtie` |
| Judge-only verifier | `AGENTQO_VERIFIER=judge` | `logs/17_math_judge.txt` | `data/ollama/h1_math_judge` |
| Passthrough verifier | `AGENTQO_VERIFIER=passthrough` | `logs/18_math_passthrough.txt` | `data/ollama/h1_math_passthrough` |
| Verifier analysis | `scripts/verifier_analysis.py` | n/a | reads the traces above |

All runs: `--backend ollama --workers 2 --max-tokens 256 --k 3 --corruptions 2 --cache data/cache/ollama.sqlite`, seed 42.
