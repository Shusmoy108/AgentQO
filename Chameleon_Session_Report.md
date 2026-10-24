# Chameleon Session Report: Sections 4 to 10 (C1–C11)

Run on Oct 23, 2026, at about 7:38 PM Chicago time (00:38 UTC on Oct 24, according to the VMs' clocks). All commands ran from the Mac over SSH (`agentqo-a` directly, `agentqo-b` through `agentqo-a`). Every value below was copied from real command output.

## Summary

| Section | VM-A (`agentqo-1`) | VM-B (`agentqo-2`) |
|---|---|---|
| 4. First checks | ✅ Pass | ✅ Pass |
| 5.1 tmux, git, python3-venv | ✅ Done | ✅ Done |
| 5.2 Python env (`~/env.sh`, `~/venv`) | ✅ Done | ✅ Done |
| 5.3 vLLM (VM-B only) | n/a | ✅ Done, **after a fix** (the original command gave a non-working install; see 5.3) |
| 5.4 AgentQO + vLLM (VM-A only) | ✅ Done (with the same fix) | n/a |
| 6. Model servers | ✅ 1.5B on :8001 | ✅ 7B on :8002 (after a second fix: remove torchcodec) |
| 7.1 C1 smoke test | ✅ All checks pass | (serves large) |
| 7.2 C2 timed run | ⚠️ Ran fine (27.3 s), but `baseline_acc=0.10` is **below** the guide's 0.2–0.8 range; see 7.2 | (serves large) |
| 8. Placement test C3–C6 | ✅ All 4 runs exit 0; colocation roughly **triples** small-model latency at concurrency ≥ 4 | (serves large for split) |
| 9. C7 H1 n=100 (math + SC) | ✅ exit 0 | (serves large) |
| 9. C8 H1 passthrough | ✅ exit 0 | (serves large) |
| 9. C9 H3 eval n=200 | ✅ exit 0 | (serves large) |
| 10. C10 verifier analysis, C11 ec vs struct | ✅ exit 0 | n/a |

---

## 4. First checks (both VMs)

The results were identical on both VMs.

| Check | Expected | Actual | Result |
|---|---|---|---|
| `nvidia-smi` | 1 × H100, ~94 GB | 1 × NVIDIA H100, 95830 MiB, 0% used, driver 560.35.05, CUDA 12.6 | ✅ |
| `df -h /` | ~40 GB | 37 G total, 12 G used, 24 G free | ✅ |
| `df -h /dev/shm` | Large | 121 G tmpfs, empty | ✅ |
| `free -h` | ~250 GB | 240 Gi total, 238 Gi free, no swap | ✅ |
| `python3 --version` | — | Python 3.12.3 | ✅ |
| `curl -sI https://pypi.org` | HTTP status line | `HTTP/2 200` (on VM-B too) | ✅ |

VM-B has internet access, so the "copy through VM-A" fallback isn't needed.

## 5.1 tmux (both VMs)

- `apt-get install tmux git python3-venv` succeeded on both.
- tmux session `agentqo` created on both. It was started **detached** (`tmux new -d -s agentqo`) because I can't attach interactively. Attach with `tmux attach -t agentqo`.

## 5.2 Python environment (both VMs)

- `~/env.sh` created exactly as in the guide (`HF_HOME=/dev/shm/hf`, `PIP_NO_CACHE_DIR=1`, activates `~/venv`).
- `~/venv` created and pip upgraded to **26.2.2** (Python 3.12).

## 5.3 VM-B: vLLM

### First attempt, exactly as the guide says: install works, GPU unusable

`pip install vllm` → exit 0, installed **vllm 0.32.0** with **torch 2.13.0+cu130** (CUDA 13).

The guide's check printed:

```
vllm 0.32.0 cuda True
```

This is a **false pass**. A real GPU operation (bf16 matmul) failed with:

```
RuntimeError: The NVIDIA driver on your system is too old (found version 12060).
```

**Cause:** the default PyPI vLLM wheel is now built against CUDA 13, but the `CC-Ubuntu24.04-CUDA` image ships driver 560.35.05, which supports up to CUDA 12.6. `torch.cuda.is_available()` returns True, but no kernel can run.

### Fix: the CUDA 12.9 build of the same vLLM version

1. Deleted and recreated `~/venv`, which freed the CUDA 13 libraries (disk went back to 12 G used).
2. Installed the official cu129 variant wheel with matching torch:
   ```bash
   source ~/env.sh
   pip install --upgrade pip
   pip install https://wheels.vllm.ai/5df63a7203cdb9328d824a27b682e77c7b9928be/vllm-0.32.0%2Bcu129-cp38-abi3-manylinux_2_28_x86_64.whl \
       --extra-index-url https://download.pytorch.org/whl/cu129
   ```
   (Found through the index `https://wheels.vllm.ai/0.32.0/cu129/vllm/`.) Exit 0. Log: `~/vllm_install_cu129.log` on VM-B.

### Verification after the fix

```
vllm 0.32.0 cuda True
torch 2.13.0+cu129
matmul ok on NVIDIA H100 finite: True
```

The guide's check passes, and a real 4096×4096 bf16 matmul runs on the H100. CUDA 12.9 binaries run on the 12.6 driver through CUDA minor-version compatibility.

**Caveats:**
- Only a matmul was tested. vLLM has **not** yet loaded a model or served a request; that happens in Section 6.1. If a vLLM kernel there needs the newer driver (for example, PTX JIT), it will show up at that point.
- One optional package, `nvidia-cutlass-dsl-libs-cu13`, was still pulled in as a dependency. It didn't affect the test above.

### VM-B state now

- Disk: 37 G total, 23 G used, **13 G free** (models go to `/dev/shm`, per the guide).
- Install logs: `~/vllm_install.log` (first, broken attempt) and `~/vllm_install_cu129.log` (working).

---

## 5.4 VM-A: AgentQO code and vLLM

Run on Oct 23, 2026, at about 7:50 PM Chicago time, using the corrected commands that are now in the guide (cu129 wheel, then `pip install -e ".[dev,viz]"`). Log: `~/install_54.log` on VM-A.

| Check | Actual | Result |
|---|---|---|
| `git clone` + `git log` | Latest commit `0c1d5fc Add placement test`, same as GitHub HEAD and the Mac | ✅ |
| Install | exit 0; `vllm-0.32.0+cu129`, `torch-2.13.0+cu129`, `agentqo-0.1.0` | ✅ |
| Version check | `vllm 0.32.0 torch 2.13.0+cu129` | ✅ |
| Real GPU matmul | `GPU matmul ok: True` | ✅ |
| `pytest tests/ -q` | **120 passed** in 22.83 s | ✅ |
| Tonight's scripts | `placement_test.py`, `run_real_h3.py`, `verifier_analysis.py` all present | ✅ |
| Passthrough verifier | Found in `agentqo/tasks/prompts.py` lines 143 and 146 | ✅ |
| Disk after install | 37 G total, 23 G used, **13 G free** | ✅ |

`agentqo-sync` (guide Section 3.4) was also run once against the real VM-A repo: exit 0, `0 logs, 0B` (correct, since nothing has run yet).

## 6. Model servers

Run on Oct 23, 2026, at about 7:57 PM Chicago time (00:57 UTC Oct 24). Each server runs in tmux window `agentqo:0` on its VM, with output also teed to `~/vllm_8001.log` (VM-A) and `~/vllm_8002.log` (VM-B).

### First start: both servers crashed

```
OSError: libnvrtc.so.13: cannot open shared object file: No such file or directory
OSError: Could not load this library: /home/cc/venv/lib/python3.12/site-packages/torchcodec/libtorchcodec_image.so
```

**Cause:** the cu129 vLLM wheel pulls `torchcodec 0.17.0` from PyPI, which is CUDA 13 only. The cu129 index only has up to 0.16. `vllm/multimodal/media/audio.py` imports torchcodec at startup inside `try/except (ImportError, RuntimeError)`. This failure raises `OSError`, which that block doesn't catch, so the server dies.

**Fix:** `pip uninstall -y torchcodec` on both VMs. The import now raises `ImportError`, which vLLM handles (`AudioDecoder = None`). Only audio and video input are affected; these are text models.

### Second start: both servers up

| | VM-A small | VM-B large |
|---|---|---|
| Model | Qwen/Qwen2.5-1.5B-Instruct | Qwen/Qwen2.5-7B-Instruct |
| Bind | 127.0.0.1:8001 | 0.0.0.0:8002 |
| `--gpu-memory-utilization` | 0.25 | 0.85 |
| Weights loaded | 2.98 GiB in 12.0 s | 14.29 GiB in 19.9 s |
| KV cache | 18.25 GiB, 683,568 tokens (166.89× concurrency at 4096 tokens) | 61.93 GiB, 1,159,632 tokens (283.11×) |
| GPU memory used (`nvidia-smi`) | 23,962 / 95,830 MiB | 80,410 / 95,830 MiB |
| Model files in `/dev/shm/hf` | 3.0 G | 15 G |
| Log | `Application startup complete.` | `Application startup complete.` |

### 6.3 checks from VM-A

- `GET localhost:8001/v1/models` → lists `Qwen/Qwen2.5-1.5B-Instruct`, `max_model_len` 4096 ✅
- `GET 10.56.3.219:8002/v1/models` → lists `Qwen/Qwen2.5-7B-Instruct` ✅. VM-A reaches VM-B on 8002 **without any security-group change**.
- `POST .../v1/completions` with `"logprobs":1` on **both** servers → responses include a `logprobs` field with `token_logprobs` and `top_logprobs` ✅
  - 7B, prompt `2+2=`: text `4. 证明这个`, first-token logprob −1.628
  - 1.5B, prompt `2+2=`: text `4\n3. `, first-token logprob −1.066

(These are raw completions at default sampling with no chat template, so the odd continuations are expected. The check here is only that the servers respond with logprobs.)

### 6.4 env

Appended to `~/env.sh` on VM-A as in the guide, with `VMB=10.56.3.219`. `echo $VLLM_ENDPOINTS` printed:

```
{"small":"http://localhost:8001","large":"http://10.56.3.219:8002"}
```

## 7. Smoke test and timing

Both runs ran on VM-A in tmux window `agentqo:1`, with **all console output (stdout and stderr, including the tqdm progress bars and the `time` output)** written to the log through `2>&1 | tee`. The exit code was appended as the last line. Both logs were copied to the Mac with `agentqo-sync` straight after each run. They now live in `~/AgentQO/logs/` and `~/AgentQO/data/` (see "Where the results are"). The cache copy passes `PRAGMA integrity_check` → `ok`.

### 7.1 C1: smoke test (`logs/c01_smoke.txt`, exit 0)

```
small  gsm8k-test-159   conf_src=logprobs cache_hit_on_rerun=True same_text=True latency=0.46s tokens=130+76  text='PLAN: \n1. Identify the initial number of tadpoles '
small  gsm8k-test-1282  conf_src=logprobs cache_hit_on_rerun=True same_text=True latency=0.38s tokens=136+127 text='PLAN:  \n1. Calculate the total number of hot dogs '
small  gsm8k-test-586   conf_src=logprobs cache_hit_on_rerun=True same_text=True latency=0.20s tokens=140+68  text='PLAN: \n1. Calculate the total number of calories b'
large  gsm8k-test-159   conf_src=logprobs cache_hit_on_rerun=True same_text=True latency=1.41s tokens=130+68  text='PLAN:\n1. Start with the initial number of visible '
large  gsm8k-test-1282  conf_src=logprobs cache_hit_on_rerun=True same_text=True latency=0.89s tokens=136+102 text='PLAN:\n1. Calculate the total number of hot dogs ne'
large  gsm8k-test-586   conf_src=logprobs cache_hit_on_rerun=True same_text=True latency=0.39s tokens=140+39  text='PLAN:\n1. Calculate total calories burned from aero'
```

| Guide check | Result |
|---|---|
| Every output starts with `PLAN:` | ✅ 6/6 |
| `conf_src=logprobs` | ✅ 6/6 |
| `cache_hit_on_rerun=True` and `same_text=True` | ✅ 6/6 |
| Small latency well under 1 s | ✅ 0.20–0.46 s (large: 0.39–1.41 s) |

### 7.2 C2: timed run (`logs/c02_h1_n10.txt`, exit 0)

```
C2 time for 10 problems (math) = real 0m27.313s   (user 0m15.973s, sys 0m0.511s)
```

All 10 problems finished: there are 10 trace files in `data/vllm/h1_math_n10/h1/math_reasoning_s3_ver/traces/`. The log's last tqdm frame shows 6/10 only because tqdm cleared the bar before the final redraw.

Result as printed:

```
H1 Math 3-step + verifier: holds=False range=0.550 cv=2.027 baseline_acc=0.10 key_change=1.0
  planner       consequence=+0.000 [-0.200,+0.250] p_err=0.73 ec=+0.000
  step_1        consequence=+0.000 [-0.150,+0.150] p_err=0.67 ec=+0.000
  step_2        consequence=-0.050 [-0.150,+0.000] p_err=0.37 ec=-0.018
  step_3        consequence=+0.050 [-0.150,+0.300] p_err=0.47 ec=+0.023
  aggregator    consequence=+0.050 [-0.250,+0.350] p_err=0.30 ec=+0.015
  verifier      consequence=+0.500 [+0.200,+0.800] p_err=0.83 ec=+0.417

HTTP calls: 935  cache hits: 110  misses: 935
```

**Time estimate (guide's rule: C7 ≈ 20 × C2):** 20 × 27.3 s ≈ **9 minutes**, far below the 6-hour limit. That's a rough extrapolation only; C7 also includes the self-consistency workflow, which hasn't been timed.

### ⚠️ `baseline_acc=0.10` is below the guide's 0.2–0.8 range

The guide says to flag this. I read all 10 baseline traces (every node on the small 1.5B model) and compared each node's answer with the gold answer:

| Task | Gold | Aggregator | Verifier (final) |
|---|---|---|---|
| gsm8k-test-1164 | 9 | 63 | 63 |
| gsm8k-test-1186 | 19 | **19** ✅ | 20 ❌ |
| gsm8k-test-1282 | 12 | **12** ✅ | 18 ❌ |
| gsm8k-test-159 | 15 | 9 | 9 |
| gsm8k-test-19 | 6 | **6** ✅ | 5 ❌ |
| gsm8k-test-2 | 70000 | **70000** ✅ | −20000 ❌ |
| gsm8k-test-519 | 280 | **280** ✅ | 160 ❌ |
| gsm8k-test-547 | 81 | 135 ❌ | **81** ✅ |
| gsm8k-test-586 | 800 | **800** ✅ | 400 ❌ |
| gsm8k-test-948 | 15 | **15** ✅ | 42 ❌ |

So, from these traces:
- **The aggregator was correct on 7/10** (1186, 1282, 19, 2, 519, 586, 948).
- **The verifier changed the answer on 10/10** (`key_change=1.0`), turning 7 correct answers into wrong ones and fixing 1 (547). That gives a final accuracy of 1/10.
- Example (gsm8k-test-19): the aggregator answered `#### 6` (correct). The 1.5B verifier replied, in full, `VERDICT: incorrect\n\n#### 5` (10 tokens, no reasoning).
- No truncation explains it: only one node in one task (gsm8k-test-2, step_2) reached the 256-token limit.

This is consistent with the printed labels, where the verifier is the only clearly critical node (+0.50, CI [+0.20, +0.80]). It's also what C8 (passthrough verifier) is designed to test. **I have not changed anything because of this.** Whether to go ahead with C7 as planned is your call. Note that 10 problems is a small sample.

## 8. Placement test (H4)

Run on Oct 23, 2026, at about 8:10–8:18 PM Chicago time (01:12–01:18 UTC). All four runs ran in tmux window `agentqo:1` with `2>&1 | tee` into the log, and each exited 0. Each run used 32 small and 32 large requests per concurrency level (64 total, alternating), `max_tokens=128`, `temperature=0`.

| Run | Log | CSV | Small → | Large → |
|---|---|---|---|---|
| C3 split | `c03_place_split.txt` | `placement_split.csv` | VM-A :8001 | VM-B :8002 |
| C4 split + shared prefix | `c04_place_split_prefix.txt` | `placement_split_prefix.csv` | VM-A :8001 | VM-B :8002 |
| C5 colocated | `c05_place_coloc.txt` | `placement_colocated.csv` | VM-A :8001 | VM-A :8003 |
| C6 colocated + shared prefix | `c06_place_coloc_prefix.txt` | `placement_colocated_prefix.csv` | VM-A :8001 | VM-A :8003 |

**Colocated server (8.3):** second Qwen2.5-7B on VM-A :8003, `--gpu-memory-utilization 0.55`. Weights loaded (14.29 GiB) in 21.1 s, with 34.0 GiB of KV cache. VM-A's GPU held 75,957 / 95,830 MiB with both servers up.

**8.4:** the 8003 server was stopped with Ctrl+C after C6. VM-A's GPU went back to 24,158 MiB (a single process, the small model), and 8001 and 8002 still return health 200.

### p50 latency, seconds (from the logs)

| conc | small split | small coloc | small split+prefix | small coloc+prefix | large split | large coloc | large split+prefix | large coloc+prefix |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1  | 0.34 | 0.33 | 0.35 | 0.33 | 0.97 | 0.96 | 0.98 | 0.96 |
| 4  | 0.35 | 1.06 | 0.35 | 1.06 | 0.99 | 1.76 | 1.00 | 1.77 |
| 16 | 0.36 | 1.10 | 0.36 | 1.11 | 1.02 | 1.79 | 1.03 | 1.79 |
| 32 | 0.37 | 1.11 | 0.38 | 1.12 | 1.04 | 1.78 | 1.04 | 1.83 |

p95 tracks p50 closely in every row (maximum p95 − p50 gap: 0.04 s). The full p95 and mean values are in the logs and CSVs.

### Throughput, tok/s per model (from the logs)

| conc | split | coloc | split+prefix | coloc+prefix |
|---:|---:|---:|---:|---:|
| 1  | 97.3 | 99.6 | 96.5 | 99.0 |
| 4  | 369.2 | 178.8 | 365.9 | 178.0 |
| 16 | 1205.5 | 645.7 | 1189.6 | 639.7 |
| 32 | 1996.9 | 1238.1 | 1977.9 | 1222.6 |

The small and large tok/s are identical within each run. I checked `scripts/placement_test.py`: `tokens_per_s` is that model's completion tokens divided by the level's shared wall time. The values match because every request generated exactly the 128-token limit, so both models produced the same token count. Check: C3 conc 1, 32 × 0.34 + 32 × 0.97 ≈ 42 s, and 4096 / 42 ≈ 97 tok/s, matching the 97.3 in the log. It's not a bug, but the column doesn't show the two models' throughputs separately.

### What the numbers show

- **Concurrency 1: no difference** between split and colocated (0.34 vs 0.33 s small). The script runs one request at a time at this level, so small and large requests never overlap, and no interference is expected.
- **Concurrency ≥ 4: colocation slows the small model about 3×.** Small p50 at conc 32: 0.37 s (split) vs 1.11 s (colocated), 3.0×; at conc 16: 0.36 vs 1.10, 3.06×. The jump is already full at conc 4 (0.35 → 1.06) and barely grows after that.
- The large model also slows when colocated: 1.04 → 1.78 s at conc 32 (1.7×).
- Throughput at conc 32 falls from 1996.9 to 1238.1 tok/s per model (−38%).
- **Shared prefix: no measurable effect** in either placement. All prefix and plain values are within 0.05 s (p50) of each other.
- **In split mode, small latency barely rises** with concurrency (0.34 → 0.37 s from conc 1 to 32).

**Caveats:**
- One run per configuration (no repeats), with fixed prompts and seed.
- The colocated large server had less KV cache (34.0 GiB vs 61.93 GiB on VM-B). This load doesn't come close to filling either, but it is a difference between the configurations.
- I haven't drawn any H4 conclusion beyond these measured numbers.

## 9. Overnight chain (C7 → C8 → C9)

Started at 01:35 UTC (8:35 PM Chicago) in tmux window `agentqo:1`. Logs end with an exit-code line. I ran the chain with `set -o pipefail` and an explicit exit-code check between steps, because the guide's `cmd | tee log && next` as written would have continued after a failed step (now fixed in the guide).

### C7: H1, 100 dev problems, math and self-consistency (`logs/c07_h1_n100.txt`, exit 0)

Took about 3 minutes. 13,312 HTTP calls, plus 2,036 cache hits.

```
H1 Math 3-step + verifier: holds=False range=0.400 cv=1.486 baseline_acc=0.16 key_change=0.9939759036144579
  planner       consequence=-0.080 [-0.150,-0.010] p_err=0.67 ec=-0.054
  step_1        consequence=+0.015 [-0.040,+0.070] p_err=0.46 ec=+0.007
  step_2        consequence=+0.025 [-0.030,+0.090] p_err=0.41 ec=+0.010
  step_3        consequence=+0.070 [-0.005,+0.150] p_err=0.36 ec=+0.025
  aggregator    consequence=+0.165 [+0.070,+0.255] p_err=0.32 ec=+0.053
  verifier      consequence=+0.320 [+0.220,+0.430] p_err=0.83 ec=+0.265

H1 Self-consistency k=3: holds=True range=0.455 cv=0.563 baseline_acc=0.56 key_change=1.0
  prompt_encoder consequence=+0.100 [+0.005,+0.190] p_err=0.63 ec=+0.063
  sampler_1     consequence=+0.205 [+0.125,+0.285] p_err=0.44 ec=+0.091
  sampler_2     consequence=+0.225 [+0.145,+0.305] p_err=0.46 ec=+0.104
  sampler_3     consequence=+0.270 [+0.190,+0.360] p_err=0.49 ec=+0.132
  aggregator    consequence=+0.555 [+0.465,+0.655] p_err=0.00 ec=+0.000
```

Compared with the laptop numbers listed in guide 10.3:
- **Math:** the verifier is still the most critical node (+0.32 here vs +0.35 on the laptop). Unlike the laptop, the aggregator is also clearly above 0 (+0.165, CI [+0.07, +0.255]).
- **SC:** the samplers are +0.205, +0.225 and +0.270, all a bit below the laptop's "about 0.30 to 0.43". They're still roughly equal, with overlapping CIs ([+0.125, +0.285], [+0.145, +0.305], [+0.190, +0.360]).

### C8: H1 with passthrough verifier (`logs/c08_h1_passthrough.txt`, exit 0)

Took seconds: 0 HTTP calls, 8,144 cache hits (all from C7).

```
H1 Math 3-step + verifier: holds=False range=0.570 cv=0.642 baseline_acc=0.48 key_change=0.9939759036144579
  planner       consequence=+0.235 [+0.130,+0.340] p_err=0.61 ec=+0.143
  step_1        consequence=+0.055 [-0.045,+0.165] p_err=0.46 ec=+0.025
  step_2        consequence=+0.105 [+0.015,+0.205] p_err=0.41 ec=+0.043
  step_3        consequence=+0.405 [+0.305,+0.505] p_err=0.36 ec=+0.147
  aggregator    consequence=+0.625 [+0.525,+0.725] p_err=0.32 ec=+0.202
  verifier      consequence=+0.470 [+0.365,+0.570] p_err=0.00 ec=+0.000
```

- Without the LLM verifier, baseline accuracy is 0.48 (vs 0.16 with it).
- Upstream nodes become critical: planner +0.235, step_3 +0.405, aggregator +0.625. On the laptop it was planner +0.33 and step 1 +0.28. Here, step_1 is not clearly above 0 (+0.055, CI [−0.045, +0.165]).
- The verifier's consequence of +0.47 comes with `p_err=0.00` (code can't make errors), so its EC is 0.

### C9: H3, 200 eval problems, passthrough verifier (`logs/c09_h3_eval200.txt`, exit 0)

Ran 01:37–02:31 UTC (about 54 minutes). 5,120 HTTP calls, plus 4,880 cache hits.

```
plan                  acc      gain vs small [95% CI]   %gain   %cost
all_large           0.630      +0.170 [+0.085,+0.255]    100%    100%
ec_top2             0.615      +0.155 [+0.080,+0.230]     91%     40%
only_aggregator     0.600      +0.140 [+0.080,+0.205]     82%     20%
only_planner        0.465      +0.005 [-0.075,+0.080]      3%     20%
all_small           0.460      +0.000 [+0.000,+0.000]      0%      0%
only_step_3         0.460      +0.000 [-0.055,+0.055]      0%     20%
only_verifier       0.460      +0.000 [+0.000,+0.000]      0%      0%
only_step_2         0.440      -0.020 [-0.080,+0.040]    -12%     20%
struct_top2         0.335      -0.125 [-0.210,-0.040]    -74%     40%
only_step_1         0.310      -0.150 [-0.230,-0.075]    -88%     20%

Does measured EC predict the gain from upgrading a node? Spearman = +0.67 (p = 0.15, n = 6 nodes)
```

- `ec_top2` upgraded **aggregator + step_3** (from C8's EC ranking). `struct_top2` upgraded **planner + step_1** (largest downstream reach). Source: `data/vllm/h3_eval_n200/h3_plans.csv`.
- `ec_top2` gets **91% of the full gain for 40% of the extra cost** (laptop: 52% of gain for 40% of cost).
- `struct_top2` makes accuracy **worse** than all-small (−0.125, CI [−0.21, −0.04]). So does `only_step_1` (−0.150).
- Verifier vs. aggregator: 0 of 200 changes in every plan (passthrough), as expected.
- The Spearman correlation between EC and per-node gain is +0.67 but not significant (p = 0.15, only 6 nodes).

## 10. Analyses

### C10: verifier analysis (`logs/c10_verifier.txt`, exit 0)

| Run | Aggregator acc | Final acc | Verifier changed | Fixed | Broke | Wrong → other wrong | No number |
|---|---|---|---|---|---|---|---|
| C7 `h1_n100` (LLM verifier) | 0.48 | 0.16 | 78/100 | 5 | 37 | 36 | 9/100 |
| C8 `h1_math_passthrough_n100` | 0.48 | 0.48 | 0/100 | 0 | 0 | 0 | 0/100 |

(`logs/c10a_verifier_c7.txt` is the same analysis on C7 only, made earlier at the reviewer's request. Its numbers are identical to the first row.)

### C11: criticality pair vs structural pair (`logs/c11_ec_vs_struct.txt`, exit 0)

```
ec_top2 - struct_top2 = +0.280  95% CI [+0.205, +0.355]  (65 wins, 9 losses)
```

Paired over the 200 eval problems, with a bootstrap of 5000 resamples (seed 0). Laptop result: +0.26 [+0.14, +0.38].

## Where the results are (Mac)

As requested, everything from the Chameleon runs was moved out of `chameleon_runs/2026-10-23/` (now removed) into the repo's folders, matching the layout on VM-A:

| What | Mac path |
|---|---|
| Logs C1–C11 | `~/AgentQO/logs/c00_system_info.txt` … `c11_ec_vs_struct.txt` (13 files) |
| H1 / H3 / smoke outputs | `~/AgentQO/data/vllm/` (`smoke`, `h1_math_n10`, `h1_n100`, `h1_math_passthrough_n100`, `h3_eval_n200`) |
| Placement CSVs | `~/AgentQO/data/placement/placement_*.csv` (4 files) |
| Generation cache | `~/AgentQO/data/cache/vllm.sqlite` (240 MB after C9, `integrity_check` = ok) |
| Everything in one file | `~/AgentQO/session1_c01_to_c11.zip` (32 MB, 2140 files) |

No existing file was overwritten. `data/vllm`, `data/placement` and `data/cache/vllm.sqlite` didn't exist before, and the `c0*` log names don't clash with the laptop logs.

`agentqo-sync` (guide 3.4) now writes directly to these paths, and it was tested after the change (exit 0, 6 logs, cache 8.2 MB). **Note:** `data/` and `logs/` are in `.gitignore`, so these results aren't committed to git.

## Guide changes

- A note above 5.3 explains the CUDA 13 / driver 560 problem and the torchcodec crash.
- 5.3 and 5.4 now include `pip uninstall -y torchcodec`.
- 5.3 and 5.4 now use the cu129 wheel and check with a real GPU matmul instead of `torch.cuda.is_available()`.
- 7.2: `time` is wrapped as `( time ... ) 2>&1 | tee` so the timing lands in the log.
- 9.1: added `set -o pipefail` so `&&` really stops the chain when a step fails.
- 3.4 and 11.1: `agentqo-sync` and the final-copy and restore commands now use `~/AgentQO/logs/` and `~/AgentQO/data/` instead of `chameleon_runs/`.

## Not yet done

Final check: the Mac has every file from VM-A's `logs/`, `data/vllm/` and `data/placement/` (2116 on VM-A; 2117 on the Mac, the extra one being `c00_system_info.txt`, created on the Mac).

These are left to you:
- **11.2 Shut down:** stop the servers, delete both instances, release the floating IP, and delete the lease (lease ends Sat 3:00 PM Chicago). This is done in the Chameleon dashboard and can't be undone. The model servers on both VMs are **still running**.
- **11.3 SU usage:** record it from the Chameleon dashboard into `RESULTS.md`.
- **11.4 Send:** `session1_c01_to_c11.zip` has everything.
- `agentqo-sync` isn't in your Mac's `~/.zshrc` yet (only needed for a future session). Paste the block from Section 3.4.
