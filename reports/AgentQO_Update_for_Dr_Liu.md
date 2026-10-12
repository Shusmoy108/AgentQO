# AgentQO Progress Update: First Real-Model Results

**Shusmoy Chowdhury**, October 2026

---

## In brief

- I ran the first real-model experiments for AgentQO on my laptop (Qwen2.5 1.5B and 7B via Ollama, GSM8K, two multi-agent workflows) before using any Chameleon allocation.
- **H1 holds on real models**: the criticality of an agent's errors varies strongly across a workflow. But the simulator's picture of *why* was wrong. Criticality is driven by what each agent is allowed to see and override, not by its position in the graph.
- **The clearest example is a verifier.** When the verifier can re-read the problem and rewrite the answer, it absorbs upstream errors and becomes the single point of failure, while the planner's errors stop mattering. Replacing it with a code passthrough, using identical cached model outputs, makes every upstream agent critical again and restores the structural ordering.
- **H3 (spending by criticality) works at the level of upgrade sets.** In a pre-registered test on 100 problems not used to measure criticality, upgrading the two highest-criticality agents recovered 52% of the full upgrade's accuracy gain for 40% of its extra cost, and **beat the structurally chosen pair at equal cost by 26 points (95% CI [+14, +38]; 34 problems won, 8 lost)**.
- Three results changed the design: **where errors hurt most is not where a bigger model helps most** (upgrade value rises along the chain while error consequence falls); upgrades interact strongly, so allocation should be a joint choice over sets rather than a per-agent ranking; and a noisy repair step can cancel every upgrade, so turning a step off (a logical edit) can matter more than a bigger model.

These are pilot results: small quantized models, 30 to 100 problems per run, one task family. The plan is to repeat the strongest experiments at scale on Chameleon with vLLM.

---

## 1. What I measured

AgentQO treats reliability as a resource to allocate. Its core quantity is **epistemic criticality (EC)** of each agent call: how often the call is wrong times how much its errors change the final answer. I measure it by fault injection: replace one agent's output with a plausible wrong answer, re-run only its descendants (everything upstream is cached, so comparisons are exact), and record the effect on the final answer.

In cost-based optimizer terms, EC plays the role of a per-operator sensitivity estimate, and H3 asks whether allocating a fixed "fidelity budget" by that estimate beats the obvious heuristics.

---

## 2. Finding 1: criticality varies, but not by graph position

Math workflow (planner → three steps → aggregator → verifier), 30 problems:

| Agent | Effect of its errors on the final answer [95% CI] |
|---|---|
| verifier | **+0.35 [+0.15, +0.55]** |
| aggregator | +0.17 [+0.02, +0.33] |
| planner | +0.07 [−0.12, +0.23] |
| steps 1 to 3 | about 0 (all intervals include 0) |

In my simulator, the planner was most critical and the verifier least. With real models, the order is roughly reversed. The prompts explain why: the verifier sees the original problem and is told to correct the answer. Trace analysis shows it rewrites 63% of answers, fixing 7 and breaking 2 of 30 (a net +17 points). It repairs upstream mistakes, so they stop mattering, and nothing checks the verifier itself.

**Causal test.** Replacing the verifier with a code passthrough (zero new model calls, identical upstream outputs) makes every upstream agent clearly critical, in exactly the order downstream reach predicts:

| Agent | With repairing verifier | Verifier as passthrough |
|---|---|---|
| planner | +0.07 | **+0.33** |
| step 1 | −0.03 | **+0.28** |
| step 2 | +0.05 | **+0.20** |
| step 3 | 0.00 | **+0.18** |
| aggregator | +0.17 | **+0.47** |

> **Structure predicts criticality only when no agent can repair upstream errors. With a repair step, the ordering inverts.**

A second controlled experiment found that a single tie-break rule in a majority vote ("ties go to the first answer") made one of three identical samplers look twice as critical. Making the vote symmetric removed the asymmetry and matched a value I had predicted beforehand (0.372 against a predicted 0.37), again with zero new model calls. Criticality depends on implementation details that are invisible in the graph.

---

## 3. Finding 2: spending by criticality pays off, at the level of sets

Each plan upgrades some agents to the 7B model and leaves the rest on 1.5B. Cost counts 1 per small call and 4 per large call. Verifier replaced by a passthrough; criticality measured on the dev problems; results below on **100 eval problems never used to measure it**, with success criteria fixed before the run:

| Plan | Accuracy | Gain vs. all-small [95% CI] | Share of full gain | Share of extra cost |
|---|---|---|---|---|
| all on 7B | 0.760 | +0.440 [+0.320, +0.550] | 100% | 100% |
| **top-2 by criticality** (planner + aggregator) | **0.550** | **+0.230 [+0.110, +0.350]** | **52%** | **40%** |
| **top-2 by structure** (planner + step 1) | **0.290** | **−0.030 [−0.140, +0.080]** | **−7%** | **40%** |
| all on 1.5B | 0.320 | (baseline) | 0% | 0% |

Paired comparison at equal cost: **criticality pair minus structural pair = +0.260, 95% CI [+0.140, +0.380]; 34 problems won, 8 lost.** The same comparison on an earlier set of 30 eval problems gave +0.267, and on the dev problems the criticality pair gave 69% of the gain for 40% of the cost, so the set-level result has replicated twice.

What did **not** hold is the ranking of *single* upgrades (Spearman with criticality: +1.00 in-sample, −0.26 on the 100 new problems). With 100 problems the reason is clear:

| Agent upgraded alone | planner | step 1 | step 2 | step 3 | aggregator |
|---|---|---|---|---|---|
| Gain | −0.07 | −0.04 | +0.08 | +0.09 | **+0.15** |
| Consequence of its errors | **+0.33** | +0.28 | +0.20 | +0.18 | +0.47 |

**The value of an upgrade rises along the chain, while the consequence of errors falls.** My working explanations: the aggregator sees the original problem and can partly re-solve it, and a 7B plan may be hard for 1.5B steps to follow. Upgrades also interact: the planner alone gives −0.07, the aggregator alone +0.15, and the two together +0.23.

---

## 4. Finding 3: a noisy repair step can cancel any upgrade

With the original verifier in place, no targeted upgrade helped at all. The diagnostic shows why:

| Plan | Accuracy reaching the verifier | Final accuracy |
|---|---|---|
| all on 1.5B | 0.30 | 0.47 |
| planner on 7B | **0.57** | 0.47 |
| aggregator and verifier on 7B | 0.50 | 0.47 |
| all on 7B | **0.73** | 0.67 |

Upgrading the planner nearly doubled the quality of the answer reaching the verifier, and the small verifier then broke 9 correct answers while fixing 6. It helps when its input is bad and hurts when its input is good, which pins final accuracy near 47% almost regardless of upstream quality. The verifier had the highest criticality, yet upgrading it bought nothing.

---

## 5. What this changes in AgentQO

1. **Allocate by error reduction, not error rate.** The value of an upgrade is roughly consequence times *how much the upgrade reduces error in that role*, and whether downstream agents preserve the improvement. Both the verifier case and the reversed upgrade-value pattern in Section 3 show these can diverge sharply from raw criticality.
2. **Optimize over sets.** Because upgrades interact, greedy per-agent ranking is fragile. The allocator should evaluate candidate upgrade sets jointly, which is the joint optimization the AgentQO runtime was designed for. This is the analogue of not costing operators independently when their inputs change each other's selectivity.
3. **Treat logical edits as first-class.** In the verifier workflow, the best move was to change the plan (switch off or gate the repair step), not the models. This is direct real-model support for the joint logical and physical optimization direction (Loom).

On the engineering side, I also found and fixed a bug in the simulator runtime: its quality estimate saturated at 1.0, which made quality-reducing edits look free. After the fix, the runtime's decisions depend on criticality, a shuffled-criticality control performs worse, and the runtime no longer oscillates between edits.

---

## 6. Limitations

- Small 4-bit models served by Ollama on a laptop. I treat these as pilot evidence, not reportable results.
- 30 to 100 problems per run; enough for the main effects above, with per-agent intervals still around ±0.08 at 100 problems.
- One task family (GSM8K) and two workflows. Tasks where later agents cannot easily re-derive the answer may show weaker repair.
- Cost is counted in call units at a 1:4 ratio, not measured GPU time.

---

## 7. Proposed next steps

**This week (laptop):**
- Measure per-role error reduction from the 7B upgrade, and test whether it predicts single-agent gains better than criticality alone.
- Test the two explanations for the reversed upgrade pattern (aggregator without the original problem; 7B planner with 7B steps).
- Label two more workflows (a complex DAG and multi-hop QA), which also provides enough data for H2 (predicting criticality from hidden states).

**On Chameleon (with your approval):**
- Repeat H1 and H3 with vLLM, larger models (for example 8B and 70B class), and several hundred problems, with measured GPU time instead of call units.
- Then start the multi-GPU scheduling experiments using the fixed runtime.

I plan to stay well within the 1,000 SU I set aside for the prototype phase, because all generations are cached and the pipeline is already debugged end to end on the laptop.

---

## 8. Questions for you

1. Is the **"repair inverts criticality"** result worth developing as its own contribution, or should it stay as motivation for the scheduler?
2. For H3 at scale, would you prefer I measure cost as **GPU time per request** or as **throughput under load** on Chameleon?
3. Would a short meeting next week work to go over these results and agree on the Chameleon plan?

---

**Attached:** full H1 report (*AgentQO_H1_Full_Report.md*), full H3 report (*AgentQO_H3_RealModel_Report.md*), and the simulator results report (*AgentQO_Laptop_Results_Report.md*). Code: github.com/Shusmoy108/AgentQO.
