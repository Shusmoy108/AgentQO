# AgentQO on Chameleon: Session 1 Report

**Lease:** AGENTQO, KVM@TACC, 2 × NVIDIA H100. Friday Oct 23, 2026, 6 PM, to Saturday Oct 24, 3 PM Chicago (20:00 UTC).
**Scope:** everything done in this session, from SSH setup to the final archive. Every number below comes from a real run and its log. Nothing is estimated unless it's marked as an estimate.

---

## 1. Summary

| Block | What | Outcome |
|---|---|---|
| Setup | SSH, first checks, install, model servers | Done. Two install problems found and fixed (CUDA 13 wheels, torchcodec) |
| C1–C2 | Smoke test, timed run | Pipeline works; the 1.5B LLM verifier wipes out accuracy (0.10) |
| C3–C6 | Placement test (H4 pilot) | Sharing a GPU makes the small model about 3× slower at ≥ 4 requests in flight |
| C7–C11 | H1 (100 dev), passthrough H1, H3 (200 eval), analyses | Verifier dominates criticality; criticality pair beats structural pair by +0.280 |
| C12–C14 | Q+ pair, budget curve, cautious verifier | 4 of 7 predictions held; all 3 C14 predictions failed (the cautious verifier helps, not neutral) |
| H4 (P1–P4) | Interference cost model, MPS, prefixes, placement choice | 10 of 14 predictions held; AgentIconq fits held-out latency to 3–5% MAPE |
| E1–E2 | Closest-to-answer rule; second, branching workflow | 6 of 7 predictions held |
| F1 | Branching workflow with no LLM verifier | 1 of 4 predictions held |
| F2 | Second model family (Granite 3.1 2B/8B) | **Skipped**: answer extraction failed on Granite output in the smoke test |
| F3 | F2 rerun with max_tokens 512 | Ran; 2 of 5 predictions held. On Granite, structural selection beat EC |
| F4 | More label problems (500) and a plan-level check on 100 VALID problems | 2 of 5 held. Planner becomes the clear top node, but the 100-problem check missed on Granite; on Qwen it picked the best plan 11/12 |
| F5 | Larger check sets (400) and a 500-problem reference (EVALBIG) on Granite | 3 of 4 held. Checking on 400 problems picks the best plan at every budget |
| Delivery | Archives, GitHub branches, servers stopped | All verified; VMs left running for you to delete |

---

## 2. Setup

### 2.1 Machines

| | VM-A (`agentqo-1`) | VM-B (`agentqo-2`) |
|---|---|---|
| Address | floating IP 129.114.27.58 | private 10.56.3.219 (reached via VM-A) |
| GPU | NVIDIA H100, 95,830 MiB | NVIDIA H100, 95,830 MiB |
| Driver / CUDA | 560.35.05 / 12.6 | 560.35.05 / 12.6 |
| RAM / `/dev/shm` / disk | 240 GiB / 121 GB / 37 GB | 240 GiB / 121 GB / 37 GB |
| Role | AgentQO code, small model `Qwen2.5-1.5B-Instruct` on :8001 | large model `Qwen2.5-7B-Instruct` on :8002 |

SSH aliases `agentqo-a` and `agentqo-b` (ProxyJump through A) went into `~/.ssh/config` on the Mac.

### 2.2 Problems found during install, and fixes

1. **vLLM from PyPI is built for CUDA 13.** `pip install vllm` installed vLLM 0.32.0 with `torch 2.13.0+cu130`. `torch.cuda.is_available()` printed `True`, but every GPU operation failed with `The NVIDIA driver on your system is too old (found version 12060)`. **Fix:** the official cu129 build (`vllm-0.32.0+cu129` with `torch 2.13.0+cu129`), checked with a real bf16 matmul.
2. **torchcodec crashed `vllm serve`.** The cu129 wheel still pulled `torchcodec 0.17.0` (CUDA 13 only), and the server died at startup (`libnvrtc.so.13` missing; vLLM's import guard doesn't catch `OSError`). **Fix:** `pip uninstall torchcodec`. It's only used for audio and video.
3. **Guide fixes:** time output captured in the logs (`( time … ) 2>&1 | tee`), and `set -o pipefail` in the overnight chain. Without it, `cmd | tee log && next` ignores a failed step.

### 2.3 Model servers

| | Small (VM-A :8001) | Large (VM-B :8002) |
|---|---|---|
| `--gpu-memory-utilization` | 0.25 | 0.85 |
| Weights loaded | 2.98 GiB in 12.0 s | 14.29 GiB in 19.9 s |
| KV cache | 18.25 GiB (683,568 tokens) | 61.93 GiB (1,159,632 tokens) |

Both return logprobs, and VM-A reaches VM-B:8002 without any security-group change.

---

## 3. Night 1: C1–C11

### C1 smoke test and C2 timed run
- **C1:** all checks pass. Every output starts with `PLAN:`, `conf_src=logprobs` everywhere, and reruns are cache hits with the same text. Latency was 0.20–0.46 s (small) and 0.39–1.41 s (large).
- **C2 (10 math problems):** `real 0m27.313s`, `baseline_acc=0.10`, below the guide's 0.2–0.8. The aggregator was correct on 7/10, and the 1.5B verifier changed the answer on 10/10. Example: the aggregator said `#### 6` (correct), and the verifier replied only `VERDICT: incorrect #### 5`.

### C3–C6 placement test (first H4 measurement)

Small-model p50 latency in seconds; 32 small + 32 large requests per level, 128 tokens each:

| Concurrency | Split | Colocated | Split + prefix | Colocated + prefix |
|---|---|---|---|---|
| 1 | 0.34 | 0.33 | 0.35 | 0.33 |
| 4 | 0.35 | 1.06 | 0.35 | 1.06 |
| 32 | 0.37 | 1.11 | 0.38 | 1.12 |

- **Colocation:** the small model is about 3× slower at concurrency ≥ 4, and the large model goes from 1.04 to 1.78 s at concurrency 32.
- **Throughput:** at concurrency 32 it falls from 1996.9 to 1238.1 tok/s per model.
- **Shared prefix (about 250 tokens):** no measurable effect.

### C7–C9 overnight chain

| Run | Result |
|---|---|
| **C7** H1, 100 dev problems | **Math:** baseline 0.16; verifier consequence +0.320 [+0.220, +0.430], aggregator +0.165, others about 0. **Self-consistency:** baseline 0.56, `holds=True`, samplers +0.205 / +0.225 / +0.270. 13,312 HTTP calls |
| **C8** passthrough verifier | Baseline 0.48; aggregator +0.625, step_3 +0.405, planner +0.235. All from cache (0 HTTP calls) |
| **C9** H3, 200 eval problems | all_small 0.460, all_large 0.630; **ec_top2 (aggregator + step_3) 0.615: 91% of the gain for 40% of the cost**; struct_top2 (planner + step_1) 0.335; Spearman(EC, gain) +0.67 (p = 0.15). Ran 01:37–01:53 UTC* |

\*I first reported C9 as 54 minutes. The log's timestamps show it took about 16 minutes; the watcher only noticed late.

### C10–C11 analyses
- **C10 verifier analysis (C7):** the aggregator is right on 0.48, final accuracy is 0.16. The verifier changed 78/100: fixed 5, **broke 37**, wrong → other wrong 36, no number 9. With the passthrough verifier: 0.48 → 0.48, 0 changes.
- **C11:** `ec_top2 − struct_top2 = +0.280, 95% CI [+0.205, +0.355]` (65 wins, 9 losses). Laptop result: +0.26 [+0.14, +0.38].

---

## 4. Follow-up: C12–C14

**Code added on `followup-c12`:**
- the `AGENTQO_VERIFIER=cautious` mode
- the plans `qplus_top2`, `ec_top1/3/4` and `struct_top1/3/4`
- `--compare A:B` (reproduces C11 exactly)
- `--budget-plot`
- `verifier_analysis --details`

All runs were pre-registered in `logs/preregistration.txt`.

### C12: aggregator + planner (Q+ pair), 200 eval problems
- **Result:** qplus_top2 reached **0.620**, a gain of +0.160 [+0.075, +0.245] (94% of the gain for 40% of the cost).
- **Against ec_top2:** qplus_top2 − ec_top2 = **+0.005 [−0.070, +0.080]** (29 wins, 28 losses).
- **Checks:** the task IDs match C9, and the C9 plans reproduce problem by problem with 0 HTTP calls.

### C13: budget curve

| Agents upgraded | EC order | Structure order |
|---|---|---|
| 1 | 0.600 (aggregator) | 0.465 (planner) |
| 2 | 0.615 | 0.335 |
| 3 | **0.660** | 0.400 |
| 4 | 0.660 | 0.465 |

all_large reached 0.630. ec_top1 is identical to C9's only_aggregator on every problem.

### C14: cautious verifier prompt
- **C14a (H1, 100 dev):** baseline 0.60; verifier consequence **+0.830**, aggregator +0.155. 1,994 new calls in about 70 s.
- **C14b:**
  - The aggregator is right on 0.48; **final accuracy is 0.60**.
  - The verifier changed 32/100: fixed 15, broke 3, wrong → wrong 14, no number 0.
  - Median output is 115 tokens (the old verifier's was 11), and 6/100 outputs hit the 256-token limit.
- **C14c (H3, 200 eval):** all_small 0.470, all_large **0.810**, ec_top2 (planner + verifier) **0.760**, only_verifier 0.740, struct_top2 0.455.

### C12–C14 predictions

| Prediction | Number | Verdict |
|---|---|---|
| qplus_top2 accuracy between 0.57 and 0.64 | 0.620 | HELD |
| qplus_top2 vs ec_top2: 95% CI includes zero | [−0.070, +0.080] | HELD |
| EC plan beats structure plan at every budget 1–4 | 0.600 > 0.465 · 0.615 > 0.335 · 0.660 > 0.400 · 0.660 > 0.465 | HELD |
| ec_top3 within 3 points of all_large (0.630) | 0.660, exactly +3.0 points | HELD (at the boundary) |
| Cautious verifier changes fewer than 25/100 | 32/100 | **FAILED** |
| Final accuracy within 5 points of 0.48 | 0.60 (+12 points) | **FAILED** |
| Verifier consequence lower than C7's 0.320, and the aggregator most critical | 0.830; aggregator 0.155 | **FAILED** |

---

## 5. H4: interference cost model (branch `h4-complete`)

**Setup:**
- **Separate placement:** small on VM-A:8001 (0.25 memory), large on VM-B:8002 (0.85).
- **Shared placement:** small on VM-A:8001 (0.25) plus a second large server on VM-A:8003 (0.55).
- **Software:** vLLM 0.32.0+cu129.
- **Code:** `placement_test.py` got new options (`--small-share`, `--ignore-eos`, `--prefix-tokens`, `--repeat-id`, `--pause`, `--prefix-metrics`, and a per-request CSV). The defaults reproduce C3. New scripts: `h4_fit.py` and `h4_workflow_load.py`.
- **Cache:** every timing run bypassed the generation cache.

### P1: grid and model fit
- **Grid:** 2 placements × 3 small shares × 3 max_tokens × 4 concurrency levels × 3 repeats. All 6 runs exited 0, at 1,275–1,478 s each.
- **Fitted interference (p50):** **β_large→small = 2.398 [2.325, 2.477]**, **β_small→large = 0.901 [0.877, 0.923]**.

| Held-out test | B0 | B1 | B2 | **AgentIconq** |
|---|---|---|---|---|
| A: small_share → 0.5 (p50 MAPE) | 0.414 | 0.317 | 0.222 | **0.029** |
| B: max_tokens → 512 | 0.411 | 0.299 | 0.236 | **0.043** |
| C: repeat 0 → 1, 2 | 0.406 | 0.312 | 0.230 | **0.043** |

- **Direction accuracy (concurrency ≥ 4):** AgentIconq 1.00 in every test; B0, B1 and B2 score 0.00, since they predict the same slowdown for both models. Including concurrency 1, AgentIconq scores 0.75.
- **Separate placement, concurrency 64 vs 1:** up to **1.579×** (small model, share 0.75, 32 tokens).

### P2: MPS

| Concurrency | Small, no MPS | Small, MPS | Large, no MPS | Large, MPS |
|---|---|---|---|---|
| 4 | 3.081× | 2.798× | 1.717× | 1.243× |
| 16 | 3.061× | 2.794× | 1.753× | 1.267× |
| 32 | 3.077× | 2.846× | 1.742× | 1.264× |

MPS barely helps the small model, while the large model's slowdown falls from about 1.74× to about 1.26×. P2 needed 4 attempts because of bugs in my check scripts (see section 8). MPS itself worked every time.

### P3: 2,007-token shared prefix
- **Prefix-cache hit rate:** 0.981 on both servers.
- **Latency still rose** in the separate placement: ×1.18 / ×1.35 for the small model and ×1.09 / ×1.17 for the large one, at concurrency 16 / 32.
- **Shared GPU:** the small model's slowdown fell from 2.704 to 2.402 (ratio 0.888).

### P4: placement choice for the real math workflow (64 problems, ec_top2)

| Placement | GPUs | p95 at K = 16 | AgentIconq prediction |
|---|---|---|---|
| S (separate) | 2 | 3.01 s | 2.57 s (−14.7%) |
| C (shared) | 1 | 6.03 s | 6.25 s (+3.6%) |
| CM (shared + MPS) | 1 | 4.93 s | 4.81 s (−2.4%) |

- **Goal:** p95 at most 1.5 × S = 4.51 s. Only S meets it.
- **Recommendations:** AgentIconq → S (correct); B2 → S (correct, with similar errors); B0 → C (wrong, −57.5% error).
- **Correctness vs C9:** per-problem correctness matches C9 on 87–95% of problems. Accuracy was 0.58–0.63.

### H4 predictions

| Prediction | Number | Verdict |
|---|---|---|
| AgentIconq has the lowest p50 MAPE in Tests A and B | 0.029 / 0.043 | HELD |
| AgentIconq's MAPE ≥ 20% lower than B2's | 87% / 82% lower | HELD |
| Direction accuracy ≥ 0.9 in A and B | 1.00 (concurrency ≥ 4, defined in advance; 0.75 including concurrency 1) | HELD |
| β_large→small > β_small→large, CIs not overlapping | 2.398 vs 0.901 | HELD |
| Separate placement: p50 at concurrency 64 within 25% of concurrency 1, everywhere | 1.579× | **FAILED** |
| With MPS, small slowdown < 2.0× | 2.79–2.85× | **FAILED** |
| Without MPS, reproduces C5 within 10% | 3.073× (+0.1%), 1.737× (−0.7%) | HELD |
| Prefix makes separate p50 ≥ 20% lower, and hit rate > 80% | latency rose (×1.09–1.35); hit rate 0.981 | **FAILED** |
| Prefix lowers small slowdown on the shared GPU by ≥ 10% | 2.704 → 2.402 (−11.2%) | HELD |
| AgentIconq's recommendation meets the goal | S, 3.01 ≤ 4.51 s | HELD |
| B0 recommends C, and C violates the goal | C: 6.03 > 4.51 s | HELD |
| AgentIconq's p95 within 25% at K = 16 everywhere | −14.7%, +3.6%, −2.4% | HELD |

P4 doesn't distinguish AgentIconq from B2.

---

## 6. Follow-up E (branch `followup-e`)

**Code added:**
- the plans `output_top1/2/3` (the LLM nodes nearest the final answer)
- `--qplus-from`, which builds `qplus_top2/3` from H1 substitution files
- Spearman correlations for EC, consequence and Q+
- the 4-line budget plot
- `--workers`, to run problems in parallel; its default keeps the old sequential loop
- `verifier_analysis --workflow-dir`

**Gate:** I confirmed H4 was finished, MPS was off, and only the 8001 and 8002 servers were running before E touched the GPUs.

### E1: closest-to-answer rule, cautious math (200 eval problems)

| Plan | Upgrades | Accuracy |
|---|---|---|
| **output_top2** | aggregator, verifier | **0.820** |
| all_large | all | 0.810 |
| output_top3 | + step_3 | 0.795 |
| ec_top3 | planner, step_3, verifier | 0.765 |
| ec_top2 | planner, verifier | 0.760 |

- **Paired:** output_top2 − ec_top2 = **+0.060 [+0.005, +0.115]**; output_top3 − ec_top3 = +0.030 [−0.020, +0.080].
- **Reproduction:** all_small, ec_top2 and all_large match C14c on every problem.
- **Passthrough setting:** `output_top2` is the same pair as C9's ec_top2.

### E2: complex workflow (10 nodes, two parallel branches, cautious verifier)

**E2a (H1, 100 dev; 5 min 9 s, 17,106 calls):**
- Baseline accuracy is 0.630.
- **Verifier** consequence is +0.790, formatter +0.490, aggregator +0.145. The planner and branch nodes are near 0.
- The branch nodes absorb 0.585–0.760 of corruptions (mean 0.677).
- Verifier analysis: 0.49 → 0.63; changed 39, fixed 18, broke 4.

**E2b (H3, 200 eval; 4 min 9 s with 16 workers, 13,108 calls):**

| Plan | Upgrades | Accuracy |
|---|---|---|
| only_verifier = ec_top1 | verifier | **0.840** |
| ec_top2 = output_top2 | formatter, verifier | 0.835 |
| qplus_top3 | aggregator, step_2_1, verifier | 0.825 |
| qplus_top2 | aggregator, verifier | 0.810 |
| all_large | all | 0.765 |
| all_small | none | 0.530 |
| struct_top2 | planner, researcher_1 | 0.510 |
| only_formatter | formatter | 0.470 |

- **Spearman correlation with the single-node gains:** EC +0.58, consequence +0.60, **Q+ − baseline +0.86**.
- **Paired comparisons:**
  - ec_top2 − struct_top2 = **+0.325 [+0.245, +0.405]**
  - qplus_top2 − output_top2 = **−0.025** [−0.085, +0.030]
  - qplus_top3 − ec_top3 = +0.045 [−0.010, +0.100]
- **Observation:** upgrading everything (0.765) is worse than upgrading only the verifier (0.840).

### E predictions

| Prediction | Number | Verdict |
|---|---|---|
| output_top2 ≥ ec_top2 (0.760) | 0.820 | HELD |
| output_top2 − ec_top2 positive | +0.060 | HELD |
| E2a: max consequence ≥ 3 × median | 0.790 / 0.0275 = 28.7× | HELD |
| E2a: branch nodes' mean absorbed share ≥ 0.3 | 0.677 | HELD |
| E2b: ec_top2 beats struct_top2, CI excluding 0 | +0.325 [+0.245, +0.405] | HELD |
| E2b: formatter gain < 3 points, so qplus_top2 beats output_top2 by ≥ 5 points | formatter −0.060, but qplus_top2 − output_top2 = −0.025 | **FAILED** |
| E2b: Q+ correlates better than EC | +0.86 vs +0.58 | HELD |

---

## 6b. Last run (branch `lastrun`, 15:06–15:16 UTC)

**Setup:**
- The Qwen servers were restarted with the C9 command lines.
- `run_real_h3` gained `qplus_top1`, built only with `--qplus-from`.

### F1: complex workflow with the passthrough verifier (Qwen)

Without an LLM verifier, the last LLM node is the formatter, so the closest-to-answer pair becomes aggregator + formatter. The verifier is code here, so 9 of the 10 nodes are LLM nodes.

- **F1a (H1, 100 dev):** exit 0, 18 s, 1,948 new calls, task IDs match C7.
  - Baseline accuracy is 0.45.
  - The aggregator is most critical: consequence +0.550 [+0.440, +0.645], EC +0.196.
  - Then the formatter (+0.435) and the planner (+0.200).
- **F1b (H3, 200 eval, 16 workers):** exit 0, 49 s, 2,183 new calls, task IDs match C9.

| Plan | Upgrades | Accuracy | Gain [95% CI] |
|---|---|---|---|
| ec_top3 | aggregator, formatter, planner | **0.570** | +0.135 [+0.060, +0.215] |
| qplus_top3 | aggregator, planner, step_1_1 | 0.560 | +0.125 |
| ec_top2 = qplus_top2 | aggregator, planner | 0.545 | +0.110 [+0.040, +0.180] |
| output_top2 | aggregator, formatter | 0.530 | +0.095 [+0.025, +0.165] |
| ec_top1 = qplus_top1 = only_aggregator | aggregator | 0.490 | +0.055 |
| output_top1 = only_formatter | formatter | 0.465 | +0.030 [−0.010, +0.070] |
| all_large | all | 0.445 | +0.010 [−0.080, +0.095] |
| all_small | none | 0.435 | — |
| struct_top2 | planner, researcher_1 | 0.345 | −0.090 |
| struct_top3 | planner, researcher_1, researcher_2 | 0.185 | −0.250 |

| Paired comparison | Budget 1 | Budget 2 | Budget 3 |
|---|---|---|---|
| ec − output | +0.025 [−0.040, +0.090] | +0.015 [−0.060, +0.090] | +0.040 [−0.025, +0.110] |
| qplus − output | +0.025 | +0.015 [−0.060, +0.090] | +0.030 |
| ec − struct | +0.100 [+0.020, +0.175] | **+0.200 [+0.130, +0.270]** | +0.385 [+0.310, +0.460] |

- **Spearman correlation with the single-node gains** (9 LLM nodes): EC +0.68 (p = 0.04), consequence +0.75 (p = 0.02), Q+ − baseline +0.50 (p = 0.17).
- **Upgrading every node** barely helps here: all_large 0.445 vs all_small 0.435.

| F1 prediction | Number | Verdict |
|---|---|---|
| output_top1 (the formatter) gains less than +0.01 over all_small | +0.030 | **FAILED** |
| qplus_top2 − output_top2 positive, with CI excluding zero | +0.015 [−0.060, +0.090] | **FAILED** |
| ec_top2 beats struct_top2, with CI excluding zero | +0.200 [+0.130, +0.270] | HELD |
| Q+ − baseline correlates better than EC | +0.50 vs +0.68 | **FAILED** |

### F2: Granite 3.1 (skipped)
- **What worked:** `ibm-granite/granite-3.1-2b-instruct` (5.07 GB) and `granite-3.1-8b-instruct` (16.34 GB) are ungated, downloaded to `/dev/shm/hf`, and served on :8001 (0.25) and :8002 (0.85). Logprobs were returned on every smoke call.
- **The failure:** on gsm8k-test-1282, Granite-2B's aggregator re-solved the problem and hit the **256-token limit** (the C8/C9 setting) before writing `#### <number>`. Its output ends "So, total cost =", so the extractor returned "2" where the answer is 12. The 2B planner also doesn't start with `PLAN:`.
- **Decision:** making it work would need different prompts or settings, which were ruled out, so F2 was skipped as instructed. Nothing was written to `data/vllm/f2_*`, and the F2 predictions were never pre-registered. `data/cache/vllm_granite.sqlite` (2.9 MB) holds only the smoke-test generations.

### F3: Granite rerun with max_tokens = 512 (15:24–15:34 UTC)

**The one change:** max_tokens = 512 for every node in H1 and H3. This was logged in `logs/changes.txt` before any F3 run; everything else is identical to F2. The Qwen runs used 256, so Qwen–Granite comparisons are across different token limits.

**Checks before running:**
- `--max-tokens` already reaches every node's request.
- `max_tokens` is part of the cache key, so the 256-token smoke generations couldn't be reused.
- Nothing parses the `PLAN:` prefix.
- The servers used the same commands as F2.

**Smoke gate** (3 dev problems, including gsm8k-test-1282): passed on all three criteria.
- Every aggregator output ended in `#### n`; gsm8k-test-1282 now finishes in 284 tokens.
- 0 of 253 calls hit the limit.
- 253/253 calls returned logprobs.

**F3a (H1, 100 dev):** exit 0, 2 min 35 s, 8,254 calls, task IDs match C7.
- Truncation: **9/8,254 calls (0.1%)** hit 512 tokens.
- The passthrough verifier changed 0/100 answers.
- Baseline accuracy is 0.600.

| Node | Consequence [95% CI] | p_err | EC | Absorbed | Q+ − baseline |
|---|---|---|---|---|---|
| planner | +0.235 [+0.145, +0.330] | 0.55 | +0.128 | 0.395 | +0.030 |
| step_1 | −0.010 [−0.065, +0.045] | 0.12 | −0.001 | 0.795 | +0.000 |
| step_2 | +0.085 [+0.025, +0.145] | 0.38 | +0.032 | 0.775 | +0.040 |
| step_3 | +0.230 [+0.125, +0.335] | 0.13 | +0.029 | 0.295 | +0.000 |
| aggregator | +0.585 [+0.480, +0.700] | 0.26 | +0.154 | 0.000 | +0.040 |
| verifier (code) | +0.595 [+0.500, +0.690] | 0.00 | 0.000 | 0.000 | +0.000 |

**F3b (H3, 200 eval, 16 workers):** exit 0, 3 min 18 s, 6,528 calls, task IDs match C9, truncation **19/6,528 (0.3%)**.

| Plan | Upgrades | Accuracy | Gain [95% CI] |
|---|---|---|---|
| all_large | all | **0.675** | +0.170 [+0.085, +0.255] |
| struct_top2 | planner, step_1 | **0.650** | +0.145 [+0.065, +0.235] |
| struct_top3 | planner, step_1, step_2 | 0.630 | +0.125 |
| only_planner = struct_top1 | planner | 0.600 | +0.095 [+0.010, +0.185] |
| ec_top3 = qplus_top3 | aggregator, planner, step_2 | 0.595 | +0.090 [+0.000, +0.180] |
| ec_top2 | aggregator, planner | 0.565 | +0.060 [−0.025, +0.145] |
| output_top2 | aggregator, step_3 | 0.550 | +0.045 |
| qplus_top2 | aggregator, step_2 | 0.515 | +0.010 |
| all_small | none | 0.505 | — |
| qplus_top1 = only_step_2 | step_2 | 0.495 | −0.010 |
| ec_top1 = output_top1 = only_aggregator | aggregator | 0.470 | −0.035 [−0.090, +0.020] |

| Paired comparison | Budget 1 | Budget 2 | Budget 3 |
|---|---|---|---|
| ec − output | 0 (same node) | +0.015 [−0.065, +0.100] | **+0.085 [+0.005, +0.170]** |
| qplus − output | +0.025 [−0.040, +0.085] | −0.035 [−0.090, +0.020] | +0.085 [+0.005, +0.170] |
| qplus − ec | +0.025 | −0.050 [−0.135, +0.030] | 0 (same nodes) |
| ec − struct | **−0.130 [−0.215, −0.050]** | **−0.085 [−0.145, −0.025]** | −0.035 [−0.095, +0.025] |

**Spearman correlation with the single-node gains** (5 LLM nodes): EC −0.40, consequence −0.30, Q+ − baseline −0.63. None is significant.

**What F3 shows:** on Granite, upgrading the **planner** is what pays. EC and Q+ rank the aggregator first, but upgrading the aggregator alone *lowers* accuracy (−0.035), so the structural (planner-first) plans win at budgets 1 and 2.

| F3 prediction | Number | Verdict |
|---|---|---|
| (F3a) "…criticality is uneven. Largest node-level consequence ≥ 3 × median" | 0.595 / 0.232 = 2.56 (2.54 without the code verifier) | **FAILED** |
| F3b: ec_top2 beats struct_top2, with CI excluding zero | −0.085 [−0.145, −0.025]: struct_top2 is significantly *better* | **FAILED** |
| F3b: qplus_top2 within 3 points of the best of ec_top2 / output_top2 / qplus_top2 | 0.515 vs 0.565: 5.0 points | **FAILED** |
| F3b: at least one single-node upgrade has a negative gain | only_aggregator −0.035, only_step_2 −0.010 | HELD |
| F3b: best measured plan (ec_/qplus_ top 1–3) within 6 points of the best rule plan | 0.595 vs struct_top2 0.650: 5.5 points | HELD |

---

## 6c. F4: more labels and a plan-level check (branch `f4`, 15:42–16:07 UTC)

**Purpose:** test two fixes for F3's failure. (a) Use more label problems. (b) Choose between candidate plans by running them directly on a separate check set.

**Problem sets** (logged before any run; none overlap EVAL):
- The dev split has only 100 problems, so new `--split label/valid` options draw extra GSM8K test problems from outside the 300-problem working set.
- **LABEL** = 500 problems: the 100 C7/F3a problems in the same order, plus 400 more.
- **VALID** = 100 more.
- **EVAL** = the C9 200.

**New options** (defaults unchanged): `--name-tag 500` (plan names `ec500_*` / `qplus500_*`) and `--custom-plan`.

### F4a: Granite H1 on 500 LABEL problems
Exit 0, 10 min 20 s, 33,791 calls; the first 100 came from the cache.

| n | Q+ ranking | Spearman Q+ vs F3b gains | Q+(planner) − Q+(aggregator) |
|---|---|---|---|
| 100 | step_2 > aggregator > planner > step_1 > step_3 | −0.63 | −0.010 [−0.130, +0.110] |
| 200 | planner > aggregator > step_2 > step_3 > step_1 | 0.00 | +0.065 [−0.020, +0.150] |
| 300 | planner > step_2 > aggregator > step_1 > step_3 | +0.20 | +0.063 [−0.003, +0.130] |
| 400 | planner > step_1 > step_3 > aggregator > step_2 | +0.90 | +0.072 [+0.013, +0.130] |
| 500 | **planner** > aggregator > step_1 > step_3 > step_2 | **+0.36** | **+0.060 [+0.008, +0.112]** |

- **Q+ at n = 500:** the planner scores +0.082 [+0.032, +0.132]; every other node is at +0.022 or less.
- **EC is stuck:** its Spearman correlation stays at −0.30 for every n.
- Files: `data/vllm/f4_granite_h1_n500/label_size_curve.csv` and `.png`.

### F4b: plans from the 500-problem labels, on EVAL
Exit 0, 30 s. Every node set F3b also ran gives identical per-problem results.

| Plan | Upgrades | Accuracy | vs struct_topk |
|---|---|---|---|
| qplus500_top1 = struct_top1 | planner | 0.600 | 0 |
| ec500_top1 | aggregator | 0.470 | −0.130 [−0.215, −0.050] |
| qplus500_top2 = ec500_top2 | aggregator, planner | **0.565** | −0.085 [−0.145, −0.025] |
| qplus500_top3 | aggregator, planner, step_1 | 0.635 | +0.005 [−0.055, +0.065] |
| ec500_top3 | aggregator, planner, step_3 | 0.620 | −0.010 [−0.075, +0.050] |

### F4c and F4d: plan-level selection (pick the best on VALID, score on EVAL)
- **Selector rule:** the candidates for budget k are the distinct node sets chosen by the rule plans. The selector takes the highest VALID accuracy, breaking ties by lower cost and then alphabetically.
- **F4c (Granite):** shortfalls from the best candidate on EVAL were **0.130 / 0.085 / 0.015** at k = 1 / 2 / 3. At k = 1, aggregator and planner tied on VALID (0.580 each), and the alphabetical tie-break chose the aggregator. The cheaper version (only the top 2 candidates by Q+) made the same picks.
- **F4d (Qwen, 4 settings):** after swapping back to the Qwen servers, the selector picked the best EVAL candidate in **11 of 12** cases. The exception was complex/cautious at k = 2: aggregator + verifier, 2.5 points short. Two candidates were excluded because no EVAL result exists for their node sets: math/passthrough `output_top3` and math/cautious `struct_top3`.

| F4 prediction | Number | Verdict |
|---|---|---|
| F4a: at n = 500, the planner has the highest Q+ − baseline | +0.082 vs at most +0.022 | HELD |
| F4a: Spearman of the Q+ ranking with the F3b gains is at least +0.5 at n = 500 | +0.36 | **FAILED** |
| F4b: qplus500_top2 accuracy on EVAL is at least 0.60 | 0.565 | **FAILED** |
| F4c: Granite selector within 3 points at every k | 0.130 / 0.085 / 0.015 | **FAILED** |
| F4d: Qwen selector within 3 points in ≥ 80% of cases, never > 6 points short | 12/12, maximum 0.025 | HELD |

## 6d. F5: larger check sets for the Granite near-tie (branch `f5`, 16:44–16:56 UTC)

**Problem sets:** only 519 unused GSM8K test problems remained. So **EVAL2** = the next 300 unused test problems, and **VALID2** = 300 problems from the GSM8K *train* split (`--split valid2/eval2`). **EVALBIG** = EVAL (200) + EVAL2 (300) = 500 problems, used as the reference truth. None of the sets overlap.

**Runs:** all 13 F4c candidate plans on VALID2 (3 min 53 s, 8,779 calls) and on EVAL2 (4 min 16 s, 8,769 calls). Both exited 0, as did the analysis.

**Time gates:** at your request ("finish it for full results"), the 17:15 and 17:45 UTC gates were dropped. That decision is logged.

| k | Best on EVALBIG | Runner-up | Best − runner-up (paired) |
|---|---|---|---|
| 1 | planner 0.582 [0.538, 0.624] | aggregator 0.500 | +0.082 [+0.028, +0.132] |
| 2 | planner + step_1 0.630 [0.586, 0.672] | aggregator + planner 0.592 | +0.038 [+0.000, +0.078] |
| 3 | aggregator + planner + step_3 0.648 | aggregator + planner + step_1 0.644 | +0.004 [−0.032, +0.042] (tie) |

| Selector: shortfall at k = 1 / 2 / 3 | |
|---|---|
| S100 (VALID 100, as in F4) | 0.082 / 0.038 / 0 |
| **S400 (VALID + VALID2)** | **0 / 0 / 0** |
| Successive halving | 0 / 0 / 0, but it used all **400** check problems at every budget |
| Hybrid (top 2 by Q+, checked on 400) | 0 / 0 / 0 |
| Q+ (500 labels) | 0 / 0.038 / 0.004 |
| Structure | 0 / 0 / 0.020 |
| Closest-to-answer | 0.082 / 0.082 / 0.116 |
| EC (100 labels) | 0.082 / 0.038 / 0.032 |

| F5 prediction | Number | Verdict |
|---|---|---|
| Planner alone beats aggregator alone on EVALBIG (CI excludes 0) | +0.082 [+0.028, +0.132] | HELD |
| agg + planner vs planner + step_1: CI includes 0 | −0.038 [−0.078, +0.000] (zero at the edge) | HELD (on the boundary) |
| S400 within 3 points at every budget | 0 / 0 / 0 | HELD |
| Successive halving within 3 points, using < 300 problems on average | 0 / 0 / 0, but 400 problems | **FAILED** |

---

## 7. Results across the session

1. **A small LLM verifier is decisive either way.** With the original prompt it destroys accuracy (0.48 → 0.16). With the cautious prompt it adds about 12 points (0.48 → 0.60) and is by far the most critical node, in both workflows.
2. **On Qwen, criticality-based selection beats structural selection consistently:** C11 +0.280, C13 at every budget, E2b +0.325, F1 +0.200. **On Granite (F3) it reverses:** struct_top2 beats ec_top2 by 0.085 [0.025, 0.145], because the planner matters most there and upgrading the aggregator alone hurts.
3. **The simple closest-to-answer rule is a strong competitor.** It beat EC in cautious math (E1: +0.060). In the complex workflow it picked the same pair as EC (E2), or came within the CI (F1: EC − output +0.015 [−0.060, +0.090]).
4. **Q+ vs EC as a predictor of node value is mixed.** Q+ was better in E2 (Spearman +0.86 vs +0.58); EC was better in F1 (+0.68 vs +0.50).
5. **Choosing plans by running them works, given enough check problems.** On Qwen, a 100-problem check picked the best plan in 11 of 12 cases (F4d). On Granite, where the candidates are close, 100 problems weren't enough (shortfalls up to 0.130), but 400 problems found the best plan at every budget (F5). On Granite, the hybrid (Q+ shortlist + 400-problem check) and plain structure also matched or nearly matched the best. More labels alone made Q+ name the right single node (the planner) but still didn't produce the best pairs.
6. **The findings don't transfer cleanly across model families.** F2 couldn't run at 256 tokens. At 512 tokens (F3), Granite showed a different critical node (the planner), and every node-value predictor (EC, consequence, Q+) correlated *negatively* with the single-node gains.
7. **GPU sharing costs are asymmetric and predictable.** The large model slows the small one about 3×, the reverse about 1.7×. AgentIconq's two directional terms fit held-out conditions to 3–5% and chose the right placement for a real workflow. MPS mainly helps the large model.

---

## 8. What went wrong (all logged)

| Issue | Effect | Resolution |
|---|---|---|
| CUDA 13 wheels on a CUDA 12.6 driver | GPU unusable despite `cuda True` | cu129 build; guide updated |
| torchcodec CUDA 13 build | `vllm serve` crashed | Uninstalled; guide updated |
| `cmd \| tee && next` | Chain wouldn't stop on failure | `set -o pipefail` |
| Mac–VM connection stalls | Several commands started 40–60 min late (~2 h lost in total) | Remaining work chained to run on the VM by itself |
| Background watcher noticed late | I first misreported C9's duration (54 min instead of 16) | Corrected in the reports |
| P2 attempts 1–3 | My check scripts: counted the MPS server process; MPS-off check too early, then unable to match the process name (15-char limit); `grep -q` under `pipefail` | Each fixed, logged, and P2 rerun from scratch; partial data kept in `data/h4/p2_failed_attempt{1,3}` |
| P3 report lookup | Hit rates printed empty | Analysis-only fix; original kept |
| C2 count | I first said 6/10 correct aggregator answers | Corrected to 7/10 |
| Repeated identical prompts | Prefix-cache hits about 0.92 even with no prefix on servers that had seen them | Reported as a caveat; small latency impact |
| VM-A has no GitHub credentials | Couldn't push from the VM | Pushed from the Mac clone (no token handled) |
| Granite-2B output format | Aggregator ran out of the 256-token budget without `####` | F2 skipped (no prompt or setting changes allowed) |
| First `scp` of the full archive | Your `~/Downloads` copy stopped at 27.7 of 277.6 MB (sha mismatch) | Replaced with the verified copy; sha now matches |

---

## 9. Deliverables

### Archives (all copies verified with `unzip -t`)

| File | Contents | Size | sha256 |
|---|---|---|---|
| `session1_c01_to_c11.zip` | C1–C11 | 32 MB | `ef9f9053…` |
| `session1_followup.zip` | C12–C14 | 44 MB | `3e46d844…` |
| `h4_complete.zip` | H4 | 1.3 MB | `6150fbae…` |
| `session1_final.zip` | E1, E2, logs, cache, patch | 92 MB | `7e9d2f04…` |
| **`session1_ALL_results.zip`** | Everything from both VMs + code + MANIFEST.txt (4,478 files), up to E2 | **265 MB** | `ce1fae710c256554e093d46c4694af3b88ed31695308da021366f8fc34b1d25c` |
| **`session1_lastrun.zip`** | Last run: logs/, F1 data, both caches, `lastrun.patch`, MANIFEST.txt (1,193 files) | **93 MB** | `be517e6540e31ee10e6a16a3f71ebfcf815a7e629b59848d43d1ef0b5095cbab` |
| **`session1_granite.zip`** | F3: logs/, data/vllm/f3_*, Granite cache, granite.patch, MANIFEST.txt (799 files) | **20 MB** | `d1b5c9f9c47adeb7117d730f3a53cd3c9296eea22286534952df1af98bddc744` |
| **`session1_f4.zip`** | F4: logs/, data/vllm/f4_*, both caches, f4.patch, MANIFEST.txt (3,644 files) | **172 MB** | `fe0071c0a33bb94d8a3179dad607954de440e5377ad57f1762864a656840453c` |
| **`session1_f5.zip`** | F5: logs/, data/vllm/f5_*, Granite cache, f5.patch, MANIFEST.txt (121 files) | **89 MB** | `218e1b5f7996dd6b48407e94901d2e117fee12260c1f28e4d566c48e1dc64a5b` |

Both archives are on the Mac in `~/AgentQO/`, and the full archive is also in `~/Downloads/`; every sha256 matches. Every file on the `session1-results` branch at `447f08f` is also in the full zip (0 missing). The last-run files are in `session1_lastrun.zip`.

### GitHub ([Shusmoy108/AgentQO](https://github.com/Shusmoy108/AgentQO))

| Branch | Commit | Contents |
|---|---|---|
| `main` | `fac9739` | C12–C14 code + H4 code + guide and report (merged earlier, at your request) |
| `followup-c12` | `15df67e` | C12–C14 code |
| `h4-complete` | `817459b` | H4 code |
| `followup-e` | `89e64ba` | E code, `scripts/chameleon/` run scripts, RESULTS.md entries |
| `lastrun` | `8dc861b` | `qplus_top1`, last-run and F3 scripts, the report up to F3 |
| `f4` | `4449282` | `--split label/valid`, `--name-tag`, `--custom-plan`, F4 scripts |
| `f5` | latest | `--split valid2/eval2`, F5 scripts, this report |
| `session1-results` | `4a50d95` | `logs/`, all result CSV/JSON/PNG files under 20 MB from every round (through F5), and the MANIFEST files |

`followup-e`, `lastrun`, `f4`, `f5` and `session1-results` aren't merged into `main`.

### State at hand-off
- **vLLM servers:** stopped on both VMs after the last run (0 GPU processes, 1 MiB used). The Qwen model files in `/dev/shm` are untouched.
- **VMs:** still running.
- **Left for you:** delete both instances, release the floating IP, then delete the lease. Also record the SU usage in `RESULTS.md`.
