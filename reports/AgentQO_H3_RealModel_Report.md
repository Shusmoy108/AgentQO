# Does Spending by Criticality Pay Off?
## H3 on Real Models: Upgrade Allocation in a Multi-Agent Math Workflow

**Shusmoy Chowdhury**
Laptop study with Ollama (Qwen2.5 1.5B and 7B on GSM8K), October 11, 2026
Companion to the H1 report (*AgentQO_H1_Full_Report.md*)

---

## Summary

H1 showed that, in real multi-agent workflows, some agents' errors matter far more than others'. H3 asks the practical follow-up: **if we upgrade only the agents that epistemic criticality (EC) points to, do we get most of the accuracy of upgrading everything, for a fraction of the cost?** And does EC choose better than a simple structural rule?

I ran three experiments on a five-agent math workflow, using a 1.5B model as the cheap option and a 7B model as the expensive one.

1. **With the original verifier in place, no targeted upgrade helped.** The verifier, a small model that re-solves the problem and may rewrite the answer, behaved like a noisy rewriter. It improved bad upstream answers but broke good ones, pinning final accuracy near 47% in four of five plans. Upstream upgrades that nearly doubled the quality of the answer reaching the verifier (0.30 to 0.57) were thrown away.
2. **With the verifier replaced by a passthrough, EC-guided upgrades worked.** On the problems where EC was measured, upgrading the two highest-EC agents recovered **69% of the full upgrade's gain for 40% of its extra cost**, and the EC ranking matched the ranking of single-agent gains exactly (Spearman +1.00).
3. **On 30 new problems, the set-level result held, the node-level ranking did not.** The EC-chosen pair again recovered **62% of the gain for 40% of the cost**, and it **beat the structurally chosen pair at equal cost by 26.7 points (95% CI [+6.7, +46.7]; 10 wins, 2 losses)**. But the ranking of single upgrades scrambled (Spearman −0.35), and the gains turned out to interact: the planner upgrade alone slightly hurt, while the planner and aggregator together gave more than the sum of their parts.

4. **A pre-registered 100-problem replication confirmed the set-level result.** The EC pair beat the structural pair by **26 points (95% CI [+14, +38]; 34 wins, 8 losses)** and recovered **52% of the full gain for 40% of the extra cost**. With 100 problems, the single-upgrade gains also became precise enough to reveal a clear pattern: the value of upgrading an agent **rises along the chain** (planner −0.07, step 1 −0.04, step 2 +0.08, step 3 +0.09, aggregator +0.15), the reverse of the order in which the agents' *errors* matter.

The resulting claim:

> **On unseen problems, measured criticality chooses a better set of upgrades than graph structure at equal cost. But where errors hurt most is not where a bigger model helps most, upgrades interact strongly, and a noisy repair step can cancel any upgrade. Allocation should therefore estimate the value of each upgrade in its role and select sets of upgrades jointly, and it should be able to change the workflow itself, not only its models.**

---

## 1. The question

AgentQO's central bet is that compute should be spent unevenly across the agents of a workflow: expensive models where errors matter, cheap ones elsewhere. H1 established that errors do matter unevenly. H3 tests whether acting on that knowledge pays off.

**H3: Allocating a fixed upgrade budget by epistemic criticality yields more accuracy per unit cost than upgrading everything, and more than allocating by graph structure.**

Two baselines matter:

- **All-large** is the accuracy ceiling. Everything on the 7B model, at full cost.
- **A structural rule** is the obvious cheap heuristic: upgrade the agents with the most agents downstream of them, on the theory that their errors propagate furthest. If structure works as well as EC, there is no reason to measure criticality at all.

---

## 2. Setup

### 2.1 Workflow and models

The math workflow from H1: **planner → step 1 → step 2 → step 3 → aggregator → verifier**. The planner writes a plan, the steps carry it out, the aggregator states the answer, and the verifier sees the original problem and the proposed solution, checks it, and is allowed to correct it.

| Item | Value |
|---|---|
| Cheap model | `qwen2.5:1.5b-instruct` |
| Expensive model | `qwen2.5:7b-instruct` |
| Task | GSM8K grade-school math |
| Problems | 30 per run (dev split for experiments 1 and 2, eval split for experiment 3) |
| Serving | Ollama on a 2023 MacBook Pro, 18 GB |
| Caching | All generations cached; reruns of a plan make no new calls |

### 2.2 Plans

Each plan fixes which agents run on the 7B model. Everything else runs on the 1.5B model.

| Plan | Agents on 7B |
|---|---|
| `all_small` | none |
| `all_large` | all |
| `only_X` | only agent X (one plan per agent) |
| `ec_top2` | the two agents with the highest EC from H1 |
| `struct_top2` | the two agents with the most agents downstream (planner and step 1) |

### 2.3 Measures

- **Accuracy**: fraction of problems with the correct final answer.
- **Cost units**: 1 per small-model call, 4 per large-model call, summed over the LLM agents in a run. A code passthrough costs nothing.
- **Gain**: accuracy minus all-small accuracy on the same problems, with a 95% paired bootstrap interval.
- **Share of full gain** and **share of full extra cost**: a plan's gain and extra cost as fractions of all-large's. The ideal plan has a high first number and a low second one.
- **Spearman**: rank correlation between each agent's EC (from H1) and the gain from upgrading that agent alone.

For every plan I also logged how the final agent changed the answer it received: how often, and whether the change fixed or broke it. This diagnostic turned out to explain the first experiment.

---

## 3. Experiment 1: upgrades with the original verifier

### 3.1 Design

The original workflow, verifier included. EC came from the H1 run with this verifier, where the verifier was the most critical agent (EC 0.257) and the aggregator second (0.059). So `ec_top2` upgrades the verifier and the aggregator.

**Prediction:** upgrading the verifier alone recovers much of the all-large gain cheaply. Upgrading the planner, which the simulator would favor, helps little.

### 3.2 Results (dev problems, n = 30)

| Plan | Accuracy | Gain vs. all-small [95% CI] | Share of gain | Share of cost |
|---|---|---|---|---|
| all_large | 0.667 | +0.200 [−0.067, +0.433] | 100% | 100% |
| all_small | 0.467 | (baseline) | 0% | 0% |
| only_planner | 0.467 | +0.000 [−0.200, +0.200] | 0% | 17% |
| ec_top2 (verifier + aggregator) | 0.467 | +0.000 [−0.233, +0.233] | 0% | 33% |
| only_verifier | 0.400 | −0.067 [−0.267, +0.133] | −33% | 17% |

**The prediction failed.** Upgrading the verifier alone did not help, and was two problems worse (within noise). No targeted plan beat all-small. Even all-large's gain was not statistically clear at 30 problems.

### 3.3 Why: the verifier cancels upstream gains

The diagnostic shows what the verifier did with the answer it received under each plan:

| Plan | Aggregator accuracy | Verifier changed | Fixed | Broke | Final accuracy |
|---|---|---|---|---|---|
| all_small | 0.30 | 19/30 | 7 | 2 | **0.47** |
| only_verifier (7B verifier) | 0.30 | 16/30 | 5 | 2 | **0.40** |
| ec_top2 (7B aggregator and verifier) | 0.50 | 10/30 | 3 | 4 | **0.47** |
| only_planner (7B planner) | **0.57** | 20/30 | 6 | **9** | **0.47** |
| all_large | **0.73** | 9/30 | 3 | 5 | **0.67** |

Upstream upgrades worked. A 7B planner nearly doubled the accuracy of the answer reaching the verifier (0.30 to 0.57), and a 7B aggregator raised it to 0.50. The verifier then undid the improvement. With the 7B planner, the small verifier broke nine correct answers and fixed six, pulling accuracy from 0.57 back to 0.47. Even the 7B verifier in the all-large plan broke five correct answers, lowering accuracy from 0.73 to 0.67.

The verifier behaves like a noisy rewriter: it helps when the answers it receives are mostly wrong and hurts when they are mostly right. Final accuracy lands between 0.40 and 0.47 in four of five plans, almost regardless of upstream quality. **Every upstream upgrade was cancelled at the last step.**

### 3.4 What this taught me

H1 correctly identified the verifier as the point where the final answer gets decided. But that does not make it the right place to spend money. **The value of upgrading an agent depends on how much the bigger model reduces errors in that role, and on whether downstream agents preserve the improvement.** H1's EC measures neither directly.

It also suggested a different remedy. If the verifier is destroying good answers, the fix is not a bigger verifier but **removing or gating the verifier when upstream work is strong**. That is a logical change to the workflow, not a physical one. The AgentQO edit space already contains exactly this operation (turning the verifier on or off), so this is real-model support for jointly optimizing the workflow's structure and its model assignments.

---

## 4. Experiment 2: upgrades with the verifier removed (in-sample)

### 4.1 Design

I replaced the verifier with a code passthrough that copies the aggregator's answer, the same configuration as the clean ablation in the H1 report. EC came from the H1 passthrough run, where the ranking was planner (0.215), aggregator (0.166), step 1 (0.151), step 2 (0.131), step 3 (0.086), verifier (0, since code cannot err). So `ec_top2` upgrades the **planner and aggregator**.

The diagnostic confirmed the passthrough worked: the verifier changed 0 of 30 answers in every plan. Only 18 new model calls were needed; everything else came from the cache.

### 4.2 Results (dev problems, n = 30)

| Plan | Accuracy | Gain [95% CI] | Share of gain | Share of cost |
|---|---|---|---|---|
| all_large | 0.733 | **+0.433 [+0.200, +0.667]** | 100% | 100% |
| **ec_top2 (planner + aggregator)** | **0.600** | **+0.300 [+0.067, +0.533]** | **69%** | **40%** |
| only_planner | 0.567 | +0.267 [+0.067, +0.467] | 62% | 20% |
| only_aggregator | 0.500 | +0.200 [+0.033, +0.367] | 46% | 20% |
| only_step_1 | 0.467 | +0.167 [−0.033, +0.367] | 38% | 20% |
| only_step_2 | 0.400 | +0.100 [−0.067, +0.267] | 23% | 20% |
| only_step_3 | 0.333 | +0.033 [−0.100, +0.167] | 8% | 20% |
| all_small | 0.300 | (baseline) | 0% | 0% |
| only_verifier | 0.300 | 0 (code, nothing to upgrade) | 0% | 0% |

### 4.3 EC versus single-agent gains

| Agent | EC (H1) | EC rank | Gain when upgraded alone | Gain rank |
|---|---|---|---|---|
| planner | 0.215 | 1 | +0.267 | 1 |
| aggregator | 0.166 | 2 | +0.200 | 2 |
| step_1 | 0.151 | 3 | +0.167 | 3 |
| step_2 | 0.131 | 4 | +0.100 | 4 |
| step_3 | 0.086 | 5 | +0.033 | 5 |
| verifier | 0.000 | 6 | 0.000 | 6 |

**Spearman = +1.00.** The two rankings match in every position.

### 4.4 Reading these results carefully

On these problems, EC looked like a perfect guide: it ranked single upgrades exactly, and its top pair delivered 69% of the gain for 40% of the extra cost. With the verifier gone, the gains from upstream upgrades finally reached the answer, and all-large's gain doubled to +0.433 with an interval that clearly excludes zero.

Two reasons for caution, though. First, **EC was measured on the same 30 problems** used here, so this is an in-sample check. Second, the single-agent gains have intervals of roughly ±0.15 to ±0.20, so a perfect ranking of six such numbers is less informative than it looks. Both called for a test on new problems.

There is also a subtlety worth stating. Without a repair step, criticality in this workflow largely follows structure (H1 report, Section 7.4), so a structural rule might do almost as well. The structural top two are planner and step 1. EC's top two are planner and aggregator. Experiment 3 compares them directly.

---

## 5. Experiment 3: out-of-sample replication with a structural baseline

### 5.1 Design

Same configuration as experiment 2 (verifier passthrough), but on **30 problems from the eval split, which played no part in measuring EC**. EC was kept from the dev-split H1 run. I added `struct_top2` (planner and step 1). Both pairs were fixed before this run, so neither was chosen after seeing the results.

### 5.2 Results (eval problems, n = 30)

| Plan | Accuracy | Gain [95% CI] | Share of gain | Share of cost |
|---|---|---|---|---|
| all_large | 0.833 | **+0.433 [+0.267, +0.600]** | 100% | 100% |
| **ec_top2 (planner + aggregator)** | **0.667** | **+0.267 [+0.067, +0.467]** | **62%** | **40%** |
| only_step_3 | 0.533 | +0.133 [+0.033, +0.267] | 31% | 20% |
| only_aggregator | 0.533 | +0.133 [+0.000, +0.300] | 31% | 20% |
| only_step_2 | 0.467 | +0.067 [−0.100, +0.233] | 15% | 20% |
| all_small | 0.400 | (baseline) | 0% | 0% |
| only_verifier | 0.400 | 0 | 0% | 0% |
| **struct_top2 (planner + step 1)** | **0.400** | **+0.000 [−0.200, +0.167]** | **0%** | **40%** |
| only_step_1 | 0.367 | −0.033 [−0.233, +0.167] | −8% | 20% |
| only_planner | 0.333 | −0.067 [−0.267, +0.100] | −15% | 20% |

Spearman between EC and single-agent gain: **−0.35 (p = 0.50)**.

### 5.3 The set-level result held

`ec_top2` delivered 62% of the full gain for 40% of the extra cost, almost exactly what it did in-sample (69% for 40%). On problems it had never seen, the EC-chosen pair continued to buy most of the accuracy for a fraction of the cost.

### 5.4 EC beat structure at equal cost

Both pairs cost the same: two upgraded agents, 11 cost units. A paired comparison on the same 30 problems:

| Comparison | Difference | 95% CI | Problems won / lost |
|---|---|---|---|
| ec_top2 − struct_top2 | **+0.267** | **[+0.067, +0.467]** | **10 / 2** |

The interval excludes zero, and on the 12 problems where the two plans disagreed, the EC plan won 10 (two-sided sign test, p ≈ 0.04). Since both plans upgrade the planner, the comparison isolates one choice: **EC chose the aggregator as the second upgrade, structure chose step 1, and EC's choice was worth 26.7 points.**

This matters because it is exactly the case where structure should do well. There is no repair step here, and criticality in this configuration broadly follows graph position. Even so, measured criticality made a better choice than the structural rule, on problems it had not seen.

### 5.5 The node-level ranking did not hold

The ranking of single upgrades scrambled. Upgrading the planner alone, the best single upgrade in-sample (+0.267), slightly *hurt* on the new problems (−0.067). Step 3, nearly useless in-sample (+0.033), became one of the best (+0.133). The Spearman correlation fell from +1.00 to −0.35.

I see two reasons, and both are informative.

**Single-agent gains are noisy at 30 problems.** Most of the single-upgrade intervals in both runs overlap zero, and each problem is worth 3.3 points. Ranking six noisy numbers will flip between problem sets, and EC itself, estimated from 30 problems with intervals of about ±0.17, carries its own noise. The in-sample +1.00 was partly luck and partly the fact that EC and H3 shared problems.

**Upgrades interact.** On the eval problems:

| Upgrade | Gain |
|---|---|
| planner alone | −0.067 |
| aggregator alone | +0.133 |
| sum of the two | +0.067 |
| **planner and aggregator together** | **+0.267** |

The pair is worth four times the sum of its parts. A better plan seems to help only when the aggregator is strong enough to use it. In-sample the interaction went the other way (planner +0.267 and aggregator +0.200 alone, +0.300 together, less than the sum), consistent with overlapping fixes. Either way, the value of upgrading one agent depends on what the others are running, so scoring agents one at a time is the wrong model of the problem.

---

## 6. What H3 shows

| Claim | Evidence | Status |
|---|---|---|
| Spending by EC gets most of the gain for a fraction of the cost | 69% of gain for 40% of cost in-sample; 62% for 40% on 30 new problems; **52% for 40% on 100 new problems** | **Supported, replicated twice** |
| EC chooses a better upgrade set than structure at equal cost | +0.267 [+0.067, +0.467] at n = 30; **+0.260 [+0.140, +0.380], 34 wins vs. 8 losses, at n = 100** | **Supported, pre-registered confirmation passed** |
| EC ranks single-agent upgrades correctly | Spearman +1.00 in-sample, −0.35 (n = 30) and −0.26 (n = 100) on new problems | **Not supported** |
| Upgrade value follows error consequence | Upgrade gains rise along the chain while consequence falls along it (Section 9.3) | **Not supported; roughly reversed** |
| Single-agent upgrades add up | Planner −0.07 and aggregator +0.15 alone, +0.23 together (n = 100) | **Not supported; strong interactions** |
| A bigger model at the most critical agent always helps | The 7B verifier did not help; the small verifier cancelled every upstream gain | **Not supported** |

---

## 7. What this changes in the AgentQO design

Three lessons go straight into the proposal.

**Allocate by error reduction, not by error rate.** H1's EC multiplies consequence by the small model's error rate. What determines whether an upgrade pays is consequence multiplied by **how much the upgrade reduces error in that role**, and whether downstream agents keep the improvement. Two results make this concrete. The verifier had the highest EC, yet upgrading it bought nothing. And in the passthrough workflow, the planner's errors matter most while upgrading the planner alone slightly hurts; upgrade value instead rises toward the end of the chain (Section 9.3). The allocator needs per-role estimates of the upgrade's effect, not only the current error rate.

**Choose sets, not rankings.** Because upgrades interact, a greedy "upgrade the top-k agents" rule is fragile. The allocator should evaluate candidate sets of upgrades jointly. This is exactly the joint optimization AgentQO's runtime was designed for, and H3 now provides a real-model reason for it.

**Treat logical edits as first-class.** The best way to improve the verifier-on workflow was to change the workflow, not the models. A small-model verifier capped accuracy at about 47%, and removing it unlocked every upstream gain. A practical scheduler should be able to switch a repair step off (or gate it on its own confidence) when upstream work is strong.

---

## 8. Limitations

- **Sample size.** Experiments 1 to 3 used 30 problems each, which was enough for the set-level comparison but not for ranking single upgrades. The 100-problem confirmation resolves the main comparison and the single-upgrade pattern, but per-agent intervals are still around ±0.08.
- **One workflow, one task family.** A five-agent GSM8K chain. The interaction pattern and the noisy-verifier effect may look different with other workflows or tasks.
- **Small, quantized models.** Ollama serves 4-bit 1.5B and 7B models. Larger models may change both the size of the gains and the verifier's behavior.
- **A simple cost model.** Cost units count calls at a fixed 1:4 ratio and ignore token lengths and real latency. The ratio roughly reflects the size difference, but real GPU cost would need measured timings.
- **One structural baseline.** `struct_top2` uses downstream reach. Other structural rules (for example, "protect the last agent") would pick differently and deserve comparison.
- **EC is from 30 dev problems.** Its own uncertainty contributes to the ranking noise.
- **The passthrough is a deliberate simplification.** Real workflows usually want some checking step. The finding is that a *noisy* repair step can cancel upgrades, not that verification is useless.

---

## 9. Confirmation at 100 problems

### 9.1 Design and pre-registered criteria

I repeated experiment 3 on **100 eval problems** (the first 30 are the problems from Section 5), with the same configuration: verifier passthrough, EC taken from the dev-split H1 run, and both `ec_top2` and `struct_top2` fixed in advance. Before the results came in, I wrote down three criteria:

- **Primary:** `ec_top2 − struct_top2` stays positive with a 95% interval excluding zero.
- **Secondary:** `ec_top2` recovers at least half of the all-large gain at 40% of the extra cost.
- **Exploratory:** the Spearman correlation between EC and single-agent gains, reported whatever it is.

The diagnostic confirmed the passthrough worked in every plan (0 of 100 answers changed by the verifier). The run made 1,851 new model calls.

### 9.2 Results (eval problems, n = 100)

| Plan | Accuracy | Gain vs. all-small [95% CI] | Share of gain | Share of cost |
|---|---|---|---|---|
| all_large | 0.760 | **+0.440 [+0.320, +0.550]** | 100% | 100% |
| **ec_top2 (planner + aggregator)** | **0.550** | **+0.230 [+0.110, +0.350]** | **52%** | **40%** |
| only_aggregator | 0.470 | +0.150 [+0.070, +0.230] | 34% | 20% |
| only_step_3 | 0.410 | +0.090 [+0.020, +0.160] | 20% | 20% |
| only_step_2 | 0.400 | +0.080 [+0.010, +0.160] | 18% | 20% |
| all_small | 0.320 | (baseline) | 0% | 0% |
| only_verifier | 0.320 | 0 (code) | 0% | 0% |
| **struct_top2 (planner + step 1)** | **0.290** | **−0.030 [−0.140, +0.080]** | **−7%** | **40%** |
| only_step_1 | 0.280 | −0.040 [−0.130, +0.050] | −9% | 20% |
| only_planner | 0.250 | −0.070 [−0.180, +0.030] | −16% | 20% |

Paired comparison at equal cost:

| Comparison | Difference | 95% CI | Problems won / lost |
|---|---|---|---|
| ec_top2 − struct_top2 | **+0.260** | **[+0.140, +0.380]** | **34 / 8** |

| Criterion | Result | Verdict |
|---|---|---|
| Primary | +0.260, interval [+0.140, +0.380] | **Pass** |
| Secondary | 52% of the gain for 40% of the extra cost | **Pass** |
| Exploratory | Spearman −0.26 (p = 0.62) | Single ranking not supported |

The gap between the two pairs is essentially the same size as at 30 problems (+0.26 versus +0.27), and the interval is now about half as wide. On the 42 problems where the two plans disagreed, the EC plan won 34. **The set-level result is confirmed.**

### 9.3 Upgrade value rises along the chain

With 100 problems, the single-upgrade gains are precise enough to show a clean pattern:

| Agent upgraded alone | Position | Gain [95% CI] | Consequence of its errors (H1 passthrough) |
|---|---|---|---|
| planner | 1st | −0.07 [−0.18, +0.03] | +0.333 (highest) |
| step 1 | 2nd | −0.04 [−0.13, +0.05] | +0.283 |
| step 2 | 3rd | **+0.08 [+0.01, +0.16]** | +0.200 |
| step 3 | 4th | **+0.09 [+0.02, +0.16]** | +0.183 |
| aggregator | 5th | **+0.15 [+0.07, +0.23]** | +0.467 |

Among the four chain agents (planner and steps), the consequence of errors falls along the chain while the value of an upgrade rises along it. The two quantities run in nearly opposite directions. The aggregator is high on both, which is why including it made the EC pair work.

I see two plausible explanations, both testable:

- **Agents that see the original problem can partly re-solve it.** The aggregator receives the problem along with the step results, so a 7B aggregator can recover from weak upstream work. It is a mild version of the repair mechanism behind the verifier finding in H1.
- **Capability mismatch.** A 7B planner may write plans that 1.5B steps cannot follow well, which would explain why upgrading the planner alone slightly lowers accuracy.

This is the clearest evidence so far for the first design lesson in Section 7: **where errors hurt most is not where a bigger model helps most.**

### 9.4 The interaction replicated

| Upgrade | Gain (n = 100) |
|---|---|
| planner alone | −0.07 |
| aggregator alone | +0.15 |
| sum of the two | +0.08 |
| **planner and aggregator together** | **+0.23** |

The same super-additive pattern appeared in the 30-problem eval run. The 7B planner pays off only when a 7B aggregator is there to use its plan. The EC pair won mainly because it included the aggregator, with the planner then adding value through the interaction. The structural pair combined two upgrades that each do nothing alone, and gained nothing.

### 9.5 A cost note

Upgrading only the aggregator recovers 34% of the gain for 20% of the extra cost, about as efficient per unit cost as the EC pair (52% for 40%). If the budget allows only one upgrade, the aggregator is the right choice here. A joint allocator should find this automatically, which a per-agent EC ranking would not (it ranks the planner first).

---

## 10. Next steps

1. **Estimate the effect of each upgrade directly.** Measure how much the 7B model reduces each agent's error in its role, and test whether consequence × error reduction predicts the single-agent gains in Section 9.3 better than EC does.
2. **Test the two explanations for Section 9.3.** Give the aggregator the step results without the original problem (does its upgrade value drop?), and pair a 7B planner with 7B steps (does the planner upgrade stop hurting?).
3. **Test sets, not just pairs.** Run a small sweep over upgrade sets at fixed budgets (for example, all pairs) to see how large the interactions are and whether a simple joint search beats both greedy EC and structure.
4. **Repeat with the verifier gated rather than removed.** For example, let the verifier override only when it is confident, and check whether that keeps its fixes while avoiding its breaks.
5. **Broaden.** Add the complex and multi-hop QA workflows, which also supply the labeled data H2 needs.
6. **Scale on Chameleon.** Hundreds of problems, larger models and vLLM, and measured GPU time in place of cost units.

---

## Appendix A: commands

All runs use `--backend ollama --cache data/cache/ollama.sqlite --n-tasks 30`.

| Experiment | Extra settings | Log | Output |
|---|---|---|---|
| 1. Verifier on (dev) | `--plans all_large,only_verifier,only_planner,ec_top2 --h1-summary data/ollama/h1_n30/.../h1_summary.json` | `logs/19_h3_math.txt` | `data/ollama/h3_math` |
| 2. Passthrough (dev) | `AGENTQO_VERIFIER=passthrough --h1-summary data/ollama/h1_math_passthrough/.../h1_summary.json` | `logs/20_h3_passthrough.txt` | `data/ollama/h3_math_passthrough` |
| 3. Passthrough (eval) | same as 2, plus `--split eval` | `logs/21_h3_passthrough_eval.txt` | `data/ollama/h3_math_passthrough_eval` |
| 4. Confirmation (eval, 100) | same as 3, `--n-tasks 100` | `logs/22_h3_eval100.txt` | `data/ollama/h3_math_passthrough_eval100` |

The paired comparisons in Sections 5.4 and 9.2 were computed from `h3_traces.json` with a 5,000-sample paired bootstrap over problems.

## Appendix B: cost units per plan

| Configuration | all_small | single upgrade | pair upgrade | all_large |
|---|---|---|---|---|
| Verifier on (6 LLM agents) | 6 | 9 | 12 | 24 |
| Verifier passthrough (5 LLM agents) | 5 | 8 | 11 | 20 |
