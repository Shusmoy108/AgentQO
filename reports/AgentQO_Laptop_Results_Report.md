# AgentQO: CPU Simulator Results and What They Tell Us

**Shusmoy Chowdhury**
Laptop evaluation, October 11, 2026

---

## 1. Why this report exists

AgentQO starts from one idea. In a multi-agent LLM workflow, not every call matters equally. If a planner gets something wrong, the whole answer usually breaks. If one of five self-consistency samplers gets something wrong, the vote often absorbs it. I call this property **epistemic criticality (EC)**: roughly, how much the final answer suffers when a given node is wrong. If we can estimate EC cheaply, a serving system can spend expensive GPU time (bigger models, more samples, verification) where it actually changes outcomes, and save it everywhere else.

Before asking for GPU hours, I wanted to know which parts of this story survive a careful test on a simulator and which parts do not. Everything below ran on CPU on my laptop, with no LLM involved. The goal is not to claim results about real models. The goal is to check that the methodology is sound, find the weak points, and decide what deserves real hardware.

The short version:

- **The core signal is real in the simulator.** EC varies a lot across nodes (H1), and spending by EC beats spending by confidence or spreading budget evenly (H3).
- **My learned predictor does not beat a simple structural baseline** (H2). The circularity control confirms this is an honest negative, not a bug.
- **The two-sided cost model works** in the setting it was designed for (H4).
- **The runtime optimizer is not ready.** It saves GPU time by giving up quality, it mostly ignores EC, and on one workflow it becomes unstable. This is the main thing to fix.

---

## 2. Setup

| Item | Value |
|---|---|
| Machine | 2023 MacBook Pro, 18 GB RAM, CPU only |
| Python | 3.12.1 |
| Code | AgentQO repo, local working copy (includes the Ollama backend, slightly ahead of the public commit `6519a9f`) |
| Tests | 115 passed in 22 s |
| Seed | 42 for all experiments |
| LLM | None. `MockBackend` simulator for H1 to H4 and the runtime. A local fake HTTP server for the real-data pipeline rehearsal |

**How the simulator works, briefly.** Each workflow is a small DAG of agent calls (planner, researchers, steps, samplers, aggregator, verifier, and so on). Each node can run on a cheap small model with a higher error rate or an expensive large model with a lower one. The simulator includes a *quality channel*: a ground-truth rule mapping which nodes were correct to the final task score. That is what lets us measure EC without a real model.

**How EC is labeled.** By fault injection, never by reading the simulator's hidden importance values. For each node, I force it to be wrong, recompute only its descendants, and measure how much final quality drops. That drop is the node's *consequence*. EC combines consequence with how likely the node is to fail in the first place.

**Evaluation protocol.** H2 uses leave-one-workflow-out splits, so the predictor is always tested on a DAG it never saw in training. H3 allocates budget using the H2 predictor's output, not oracle EC; oracle EC is reported only as an upper bound. Confidence intervals are 95% paired bootstrap.

A note on reproducibility: every number in this report matches, to the reported precision, the numbers I previously recorded on a different machine. The pipeline is deterministic across environments, which means any difference I later see on GPUs will come from the model, not from the code.

---

## 3. H1: Does criticality actually vary across nodes?

**Question.** If every node mattered about the same, there would be nothing to schedule. So the first test is whether consequence varies meaningfully across nodes. The pre-registered thresholds are a range above 0.10 and a coefficient of variation (CV) above 0.20.

**Result (quick mode, 16 tasks per workflow).**

| Workflow | Range | CV | Most critical | Least critical | Holds |
|---|---|---|---|---|---|
| Math, 3 steps + verifier | 0.518 | 0.685 | planner, step 1, step 2 | step 3, aggregator, verifier | Yes |
| Multi-hop QA, 3 researchers | 0.277 | 0.351 | planner, researcher 2, researcher 1 | aggregator, researcher 3, verifier | Yes |
| Self-consistency, k=3 | 0.515 | 0.887 | prompt encoder, aggregator, sampler 3 | samplers 1 and 2 | Yes |
| Complex + formatter | 0.416 | 0.898 | planner, aggregator, step 2.1 | step 2.2, step 1.1, formatter | Yes |

All four workflows clear both thresholds by a wide margin. The sanity check also passes: on the math workflow, the most critical node has a consequence of 0.580 against 0.062 for the verifier.

**What I think this means.** The effect we need exists, and it is large. But there is a catch that shapes the rest of the report. On the math workflow, consequence correlates with *downstream reach* (how many nodes sit below a given node) at **+0.95**, and with depth at **−0.95**. In other words, in this simulator EC is mostly a function of where a node sits in the graph. That is partly by design, since I built the quality channel so that structure would be a real but incomplete signal. Still, it means the obvious objection from a reviewer, "isn't EC just downstream reach?", cannot be answered by the simulator. Only real models can answer it.

---

## 4. H2: Can we predict EC on a workflow we have never seen?

**Question.** Fault injection is expensive, so in practice we need to *predict* EC. The AgentQO predictor uses structural features plus a recycled embedding of the node's state (the same trick TRAIL uses for length prediction). The bar it must clear is a structure-only model that sees only graph features.

I ran two versions. In the first, the mock embedding carries a small amount of hidden signal about importance and difficulty, a stand-in for what real hidden states might contain. In the second, the embedding is pure noise. That second run is a circularity control: if the predictor still wins with noise embeddings, something is leaking.

**Result (7 workflows, leave-one-workflow-out, Spearman rank correlation with true EC).**

| Model | Hidden-signal embedding (1,500 samples) | Noise embedding (2,000 samples) |
|---|---|---|
| AgentQO (structure + embedding) | 0.352 | 0.333 |
| Structure-Only | **0.375** | **0.384** |
| Structure + Noise (control) | 0.348 | 0.330 |
| Confidence-Only | −0.011 | −0.002 |

Prediction overhead is about 0.5 ms per node, so cost is not the issue.

**What I think this means.** Two things.

First, **the control behaves exactly as it should.** With noise embeddings, AgentQO collapses to the Structure + Noise level (0.333 vs 0.330). The embedding is not smuggling in task identity. I mention this because an earlier version of this experiment *did* pass H2 (0.49 vs 0.30), and the reason turned out to be leakage: every workflow was labeled with the same base seed, so the embedding effectively acted as a task ID shared across folds. After fixing the seeding, the apparent win disappeared. This control is now in place permanently.

Second, **H2 fails honestly.** Structure alone is the best predictor in the simulator, and the weak hidden signal in the mock embedding is not enough to beat it. This follows directly from the H1 observation: if EC is mostly structural, a structural model wins.

Also worth noting: **confidence is useless for predicting criticality** (Spearman around zero). This is by design in the simulator, where confidence tracks whether a node is locally correct, not whether its errors matter downstream. But it is the conceptual heart of AgentQO: "this call is uncertain" and "this call matters" are different questions, and systems that route by confidence are answering the wrong one.

So H2 comes down to an empirical question the simulator cannot settle: **do real hidden states carry information about task difficulty and node importance beyond what the graph shape gives you?** This is the most important question to take to real models.

---

## 5. H3: Does spending by EC beat the alternatives?

**Question.** Given a fixed compute budget, which nodes should get the large model? I compare four policies on a workflow held out from predictor training:

- **AgentQO:** upgrade nodes in order of predicted EC per unit cost.
- **Oracle-EC:** same, but with true EC (an upper bound).
- **Confidence:** upgrade the least confident nodes first.
- **Uniform:** spread upgrades evenly.

The metric is area under the quality vs cost curve (AUC).

**Result (30 runs, held-out workflow: complex + formatter).**

| Policy | AUC | 95% CI |
|---|---|---|
| Oracle-EC | 14.18 | [12.95, 15.22] |
| AgentQO | 13.82 | [12.62, 14.90] |
| Uniform | 12.35 | [10.77, 13.94] |
| Confidence | 12.26 | [10.65, 13.83] |

| Paired difference | Value | 95% CI |
|---|---|---|
| AgentQO − Confidence | +1.55 | [+0.84, +2.23] |
| AgentQO − Uniform | +1.46 | [+0.57, +2.36] |
| Oracle − AgentQO | +0.36 | [−0.21, +0.94] |

Quality at each budget level:

| Cost | AgentQO | Confidence | Uniform |
|---|---|---|---|
| 10 | 0.584 | 0.584 | 0.584 |
| 13 | **0.675** | 0.606 | 0.626 |
| 16 | **0.724** | 0.606 | 0.653 |
| 19 | **0.749** | 0.697 | 0.697 |
| 25 | **0.892** | 0.765 | 0.758 |
| 28 | **0.905** | 0.780 | 0.729 |

**What I think this means.** H3 holds. AgentQO beats both baselines with confidence intervals that exclude zero, about a 12% AUC improvement, and it wins at every budget above the minimum. The gap to the oracle is small and not statistically significant, so the predictor is not the bottleneck for allocation.

One detail I like: at the highest budget, Uniform quality actually *drops* (0.758 to 0.729). Spending more money in the wrong places can make things worse, which is exactly the argument for value-aware allocation.

I want to be careful about what this does and does not show. Two limitations:

1. **Only one held-out workflow.** The evidence comes from a single DAG. It needs to be repeated across all seven folds.
2. **There is no structure-based allocator in the comparison.** H2 showed my predictor is roughly as good as structure, not better. So the fair reading of H3 is "allocating by EC-like value beats allocating by confidence or evenly," not "my learned predictor adds value." The obvious missing baseline is an allocator that ranks nodes by downstream reach. If it ties AgentQO, that is still a meaningful finding, but a different one.

In the quick demo run (16 tasks), the AgentQO vs Uniform interval was [−0.40, +3.71] and included zero. With 30 runs it tightened to exclude zero. That is a reminder to report the full run, and that the script's PASS headline (based on wins per budget level) should be switched to the confidence interval criterion so the summary cannot disagree with the statistics.

---

## 6. H4: Does the two-sided cost model work?

**Question.** When several calls share a GPU, each one slows the others down. AgentIconq models the cost of a call as its own latency *plus* the delay it imposes on co-located calls. It also allows that delay to be negative, for example when calls share a prompt prefix. I compare it to a model that ignores interference (Single-call) and one that just adds up isolated costs (Naive-additive).

**Result (500 simulated batches).**

| Model | Own-latency MAE | Q-error | Impact MAE | Sign accuracy |
|---|---|---|---|---|
| AgentIconq | **3.39** | **1.05** | **2.14** | **0.82** |
| Single-call | 6.72 | 1.12 | 5.71 | 0.15 |
| Naive-additive | 35.46 | 1.33 | 22.62 | 0.67 |

**What I think this means.** AgentIconq predicts both its own latency and its impact on neighbors much better than either baseline, and it gets the *direction* of interference right 82% of the time, against 15% for a model that ignores it. That said, the simulator generates interference in roughly the form AgentIconq assumes, so this confirms the method is implemented correctly. It does not confirm that real vLLM batches behave this way. That requires real traces.

---

## 7. The runtime optimizer: where things break

H1 to H4 test the ingredients. The actual claim of the proposal is a runtime that combines them: at each event, it picks a logical edit to the workflow (change fidelity, cancel a branch, add a sample, and so on) and a physical placement, trading off predicted quality, latency, cost, and risk.

I compared three systems:

- **FCFS-Fixed:** run the workflow as written, first come first served.
- **FixedPlan-EC:** decide upfront which nodes get the large model, using EC, and do not adapt.
- **AgentQO:** the adaptive runtime.

Each comparison uses 4 workflows × 3 load levels × 5 seeds, on 8 jobs and 2 simulated GPUs. I repeated the whole thing with three EC sources (structure-based, predicted, and oracle) to see whether better EC helps.

Results barely change across load levels (time moves by about 3%), so the table averages over load.

| Workflow | EC source | FCFS Q | FixedPlan-EC Q | AgentQO Q | AgentQO edits | ΔQ vs FCFS | ΔQ/GPU-h vs FCFS |
|---|---|---|---|---|---|---|---|
| Math | all three | 0.702 | 0.876 | 0.667 | 8 | −0.035 | +2.4 |
| Multi-hop QA | structure | 0.567 | 0.747 | 0.505 | 8 | −0.062 | +1.1 |
| | predicted | 0.567 | 0.725 | 0.505 | 8 | −0.062 | +1.1 |
| | oracle | 0.567 | 0.764 | 0.505 | 8 | −0.062 | +1.1 |
| Self-consistency | structure | 0.654 | 0.873 | 0.597 | 13 | −0.057 | −1.2 |
| | oracle | 0.654 | 0.899 | 0.593 | 30 | −0.061 | −1.3 |
| | predicted | 0.654 | 0.871 | 0.40 to 0.50 | 129 to 139 | −0.16 to −0.25 | −8.5 to −9.4 |
| Refinement | all three | 0.616 | 0.738 to 0.741 | 0.616 | 0 | 0.000 | 0.0 |

All quality differences for math, QA, and self-consistency have confidence intervals that exclude zero.

Against my own success criterion (quality within 2 points of FCFS, while improving efficiency), AgentQO does not pass anywhere. It improves quality per GPU-hour in 6 of 12 cells (math and QA), but it loses quality in 9 of 12. Efficiency bought with lost accuracy is not a win.

Looking at the workflows one by one, this is not one problem. It is four.

**1. On math and QA, the edits ignore EC.** AgentQO makes exactly 8 edits and gets exactly the same result whether it uses structural, predicted, or oracle EC. Whatever the optimizer is doing, EC is not driving it. In practice it behaves like a fixed cost-cutting rule: it gets faster and cheaper by downgrading work, and pays 3.5 to 6.2 points of quality for it.

**2. On self-consistency with predicted EC, the optimizer thrashes.** Edits jump from about 13 to about 135 per episode, completion time roughly triples (85 to 250), and quality falls by 15 to 25 points. Looking at the predicted EC values, all five samplers sit in a narrow band (0.22 to 0.26) right next to the aggregator (0.20). My working hypothesis is that the optimizer keeps adding and cancelling branches as scores flicker around a decision threshold. Oracle EC spreads the samplers out more (0.07 to 0.13) and produces far fewer edits, which fits that explanation. Note that the earlier run on another machine showed about 250 edits here, so the problem is reduced but not fixed.

**3. On refinement, the optimizer never acts.** Zero edits, identical to FCFS. Either no edit in the catalog applies to this DAG, or every candidate scores below doing nothing.

**4. Load does not create contention.** Moving from low to high load changes almost nothing. That means the simulated cluster is not crowded enough for the delay externality to matter, so the two-sided cost argument from H4 never gets a chance to influence decisions.

**The most interesting line in this table is FixedPlan-EC.** It has the best quality in every workflow, 12 to 25 points above FCFS, at roughly twice the time and lower quality per GPU-hour. It is also the only system where the EC source visibly matters: on QA, oracle EC gives 0.764, structure 0.747, and predicted 0.725, with a similar ordering on self-consistency. The intervals overlap, so I would not lean on the ordering. But the picture is clear: **spending by EC buys a lot of quality, and better EC buys a bit more.** The adaptive runtime just is not using that signal. Right now FCFS sits at "cheap," FixedPlan-EC at "accurate," and AgentQO in the cheaper-but-worse corner, which proves nothing. The result we need is AgentQO matching FixedPlan-EC's quality at lower cost, or beating FCFS on quality at the same cost.

There is also a known validity issue I have not fixed yet. The runtime's speculative-stopping rule currently reads each node's ground-truth correctness from the simulator, which a real system could never see. That has to be removed before any runtime number can be trusted, even in simulation.

---

## 8. Real-data pipeline rehearsal

To prepare for real models, I ran the full GSM8K pipeline against a local fake server that speaks the same HTTP API as vLLM. This exercises dataset loading, prompting, answer parsing, fault injection, and caching end to end.

It ran cleanly across all three workflows. On the second run, every one of 4,772 requests was served from the local cache, with zero new HTTP calls. That matters for the GPU budget: re-running or extending an analysis on Chameleon will not re-spend compute on generations we already have.

The H1 numbers from this run are not results. The fake server answers by rule, not by reasoning. The H2 and H3 stages were correctly skipped because the embeddings in this mode are placeholders.

---

## 9. Threats to validity

I would rather list these myself than have someone else point them out.

- **The simulator is mine.** I designed the quality channel, including the choice that criticality correlates with structure plus noise. Results that depend on that design (especially H1's structure correlation and H2's outcome) say more about the simulator than about LLMs.
- **The mock embedding is a stand-in.** Its hidden signal strength is a parameter I chose. H2's failure says that *this* level of signal is not enough, not that real hidden states will fail.
- **H3 has one held-out workflow** and no structure-based allocator baseline.
- **The runtime uses a simulated clock and simulated GPU cost.** Latency numbers are relative, not real.
- **Load levels do not produce meaningful contention,** so the runtime results say nothing yet about crowded clusters.
- **The runtime reads ground-truth correctness** in its stopping rule.
- **Five seeds for the runtime** is enough to see the large effects here, but not to resolve small differences between EC sources.

---

## 10. What I take away

| Hypothesis | Simulator verdict | Confidence in the verdict |
|---|---|---|
| H1: EC varies across nodes | Holds, large effect | High for the simulator; open for real models, given the strong structure correlation |
| H2: EC predictable beyond structure | Fails, honestly | High; the circularity control works |
| H3: EC-based allocation wins | Holds, about 12% AUC, CI excludes 0 | Medium; one held-out workflow, missing structure baseline |
| H4: two-sided cost model | Holds | Medium; the simulator matches the model's assumptions |
| Runtime optimizer | Does not work yet | High; four distinct, diagnosable failures |

The measurement layer is sound, and the central intuition (spend where errors matter, not where the model is uncertain) holds up in the simulator. Both H3 and FixedPlan-EC show it. What the simulator *cannot* tell us is whether real criticality is anything more than graph position, and whether real hidden states can predict it. Those are exactly the questions that make this worth doing on real models.

The runtime problems are engineering problems, and the logs point to specific causes. They can all be debugged on CPU, so they should not consume GPU time.

---

## 11. Next steps

**On CPU, now:**

1. Stop the self-consistency thrashing: add hysteresis (a minimum dwell time before an edit can be reversed) and a per-node edit cap.
2. Make edit scores depend on EC. Test: oracle EC should beat structure, and randomly shuffled EC should do worst.
3. Add a quality floor: reject any edit set whose predicted quality loss exceeds 2 points relative to the fixed plan.
4. Find out why refinement never gets an edit.
5. Increase arrival rates or reduce GPU capacity so that load creates real contention.
6. Remove ground-truth correctness from the runtime's stopping rule.
7. Add a structure-based allocator to H3 and run all seven leave-one-out folds.
8. Switch the H3 PASS headline to the confidence-interval criterion.

**On GPU (Chameleon), first:**

1. Real fault-injection labeling (H1) on GSM8K workflows with a 7B-class model. The key question: does real consequence differ from downstream reach?
2. H2 with real hidden states extracted through a TRAIL-style hook. The key question: does the embedding beat Structure-Only once it carries real signal?

If real hidden states beat structure, AgentQO's predictor has a reason to exist. If they do not, the honest pivot is to keep the allocation and runtime story, use structure as the EC proxy, and put the novelty into the optimizer and the two-sided cost model. Either outcome is a result worth reporting.
