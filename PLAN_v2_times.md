# PLAN v2: runtime per phase (ESTIMATE)

**Every H100 number here is an estimate, not a measurement.** Measured: Ollama on the Mac
(Qwen2.5 1.5B/7B, one worker), 2026-11-07. H100 estimates use two rules:

- **10x rule (brief):** H100 = Ollama time / 10. Conservative upper bound.
- **Session 1 rate:** vLLM on the H100 did 1,994 new calls in about 70 s (~28 calls/s
  with 32 workers). Likely closer to reality for P1-P4, which are throughput-bound.

## Measured on Ollama (20 problems per module)

The 20-problem run reused problems 1-10 from the 10-problem run's cache, so calls/problem
and s/call below come from the 10 new problems (11-20). Ollama runs one request at a time.

| Module | calls/problem | s/call | wall for 20 problems |
|---|---|---|---|
| M3 math labels (realistic + disagree-only) | 126.7 | 1.75 | 2,232 s (10 new) |
| M2 math all_subsets (64 plans) | 78.8 | 3.58 | 2,830 s (10 new) |
| M3/M8 HotpotQA labels | 91.0 | 1.69 | 1,548 s (10 new) |
| M2/M8 HotpotQA all_subsets (32 plans) | 41.8 | 3.95 | 1,656 s (10 new) |
| M6 placement, all_small + all_large, K=4, 1 repeat | 6 per plan | 2.71 (wall) | 652 s |
| M1 M4 M5 M7 + H5a offline (P6) | 0 | - | 11 s |

The disagree-only label run makes no new calls: it replays the full run's cache.
all_subsets calls cost more per call because most plans call the 7B model.

## Per phase at full size

Updated 2026-11-16 (A13-A17). **Lease 1: 2026-11-16 12:00 UTC to 2026-11-19 12:00 UTC, 72 h per VM.**
Only the tag `v2-lease1-start` freezes at 12:00 UTC on 2026-11-16; the lease then runs 72 h.

Calls per problem from the q4 runs (Ollama 4-bit, 200 problems per setting): math labels 124,
math all_subsets 72, HotpotQA labels 91, HotpotQA all_subsets 42. s/call from the Ollama table
above. One setting at full size: math = 200 x 124 + 400 x 72 = 53,600 calls; HotpotQA (either
workflow) = 200 x 91 + 400 x 42 = 35,000 calls.

| Phase | VM | Work | New calls | H100, 10x rule | H100, Session 1 rate |
|---|---|---|---|---|---|
| P0 | A, B | smoke test, 5 problems: Qwen isolated, A16 (all_xl too), A17; Granite hotpot + isolated; Phi math + hotpot | ~600 | **< 15 min** + server starts | **< 5 min** |
| P1 | A | Qwen 1.5B/7B labels 200: math, HotpotQA, HotpotQA isolated (A13) | 61,200 | **2.9 h** | **36 min** |
| P2 | A | Qwen 1.5B/7B all_subsets 400: math (64 plans), HotpotQA, HotpotQA isolated (32 plans) | 62,400 | **6.6 h** | **37 min** |
| P2b | A | A16: math chain, 1.5B/7B/14B per agent: labels 200 (1.5B->14B) + 729 plans x 200 | 149,600 | **~18.9 h** | **~2.1 h** |
| P2c | A | A17: complex_r2_s2_ver, Qwen 1.5B/7B: labels 200 + 1,024 plans x 200 (x 100 if reduced) | 252,800 (147,100) | **~23.0 h** (12.5 h) | **~2.5 h** (1.5 h) |
| P3 | B | Qwen 3B/14B math: labels 200 + all_subsets 400 | 53,600 | **~8.1 h** | **~64 min** |
| P4 | B | Granite 2B/8B, max_tokens 512: math, then hotpot_chain, then hotpot_chain_isolated (A14) | 123,600 | **~18.9 h** | **~2.5 h** |
| P4b | B | Phi-3.5-mini/phi-4 (A15), max_tokens 512: math, then hotpot_chain; last on VM-B | 88,600 | **~27.1 h** | **~3.5 h** |
| P5 | | 7 plans x 64 problems x 3 repeats x 3 placements, K=16 | 24,192 | **~1.8 h** + server restarts | n/a (latency-bound) |
| P5 cal | | A11 calibration: 3 model/task sets x 2 placements x 2 plans x 3 repeats x 64 problems | ~13,800 | **~1-1.5 h** + 6 server restarts | n/a (latency-bound) |
| P6 | | offline analysis, all settings | 0 | **< 10 min** | **< 10 min** |
| final | | zip with SQLite cache | 0 | **< 5 min** | **< 5 min** |
| **Total** | | | **~830,000** | **~109 h** (of 144 VM-hours) | **~16 h** |

**Per VM against the 72 h lease (10x rule, the conservative bound):**

| VM | Order | Work | + reserve | Slack in 72 h |
|---|---|---|---|---|
| VM-A | P1, P2, P2b (A16), P2c (A17) | ~51.4 h | P5 + P5 cal + P6 + final ~4 h | **~16 h** |
| VM-B | P3, P4, P4b (Phi) | ~54.2 h | ~4 h (if P5 runs here) | **~14 h** |

At the Session 1 rate VM-A needs ~5.9 h and VM-B ~7.0 h. Either way the full plan fits; the
cut order below is a safeguard if the real rate is worse than the 10x rule. Moving A17 from
VM-B to VM-A balances the two VMs (with A17 on VM-B, VM-B would need ~77 h, over the lease). Whichever VM finishes first takes the next unstarted setting
from the other VM (`scripts/v2/smoke_check.py moved SETTING VM-x` on the VM giving it up).

**Time-budget cut (automatic in `run_phase.sh`, logged in FAILURES.md and as a lease-time
deviation).** Before a cuttable setting starts on a VM, its 10x-rule hours (column above) must
fit in the time to 2026-11-19 12:00 UTC minus a 4 h reserve. Cut order, first to last:
Phi hotpot (11 h), Phi math (16.5 h), A17 200 -> 100 eval problems (23 h -> 12.5 h), A17,
A16 (19 h), E1, P5 K=1 runs, Granite isolated (5.5 h). A setting cut for time also cuts the
not-yet-started settings before it in the order on its VM. E1 and the P5 K=1 runs are run from
the lease prompt, not by `run_phase.sh`; cut them by hand at their place in the order.

**Session 1 caches no longer exist.** Every call above is generated fresh; the lease cache is a
new file (`data/cache/v2_lease1.sqlite`) and nothing looks for a Session 1 cache.

Assumptions behind the rows without a direct measurement:
- A16: at most 1,092 distinct prompts per problem (3 tiers, each node's prompt depends on its own
  and its ancestors' tiers), times the binary q4 ratio 72/126 = 0.57 -> ~624 calls per problem.
  About a third of calls go to 14B, timed at 2x the 7B, so plan calls are timed at 1.33x the
  Qwen 1.5B/7B math rate; the 1.5B->14B labels at 2x (as P3).
- A17: at most 1,850 distinct prompts per problem for the 10-agent DAG, x 0.57 -> ~1,057 calls
  per problem; labels ~207 calls per problem (math labels 124 / 6 agents x 10). Timed at the Qwen
  1.5B/7B math rates. The aggregator, verifier and formatter see many upstream outputs, so their
  prompts are longer; this is the least certain row.
- Calls per problem are the q4 counts for every model family. Granite and Phi may stop at
  different points in the shared-prefix tree, but the call count per plan is fixed by the DAG,
  so this mostly affects token counts, not calls.
- The isolated HotpotQA prompts are shorter (no paragraphs in two of five nodes), so timing them
  like hotpot_chain is an upper bound.
- P3 (Qwen 14B decodes about 2x slower than 7B) and P4 (Granite, 512-token cap against Qwen's 256)
  are timed at twice the Qwen 1.5B/7B time for the same task. P4b is timed at 4x: phi-4 is a 14B
  model (2x) and has the 512-token cap (2x). Not measured; no Phi run was made on the Mac.
- P5 runs in real time against live servers and bypasses the cache, so it scales with
  latency, not throughput. Taken from the M6 run: mean plan wall 325 s per 20 problems, times
  64/20 problems, 7 plans, 3 repeats, 3 placements, / 10. Switching placement means
  restarting vLLM (~2-5 min each in Session 1), which isn't counted.
- P5 cal (A11) is timed like P5: the M6 run's mean plan wall (325 s per 20 problems on Ollama)
  x 64/20 x 2 plans x 3 repeats x 6 (set, placement) pairs / 10. Qwen 14B and Granite 8B are
  slower than Qwen 7B, hence the range. Each set needs its own servers in both placements.
  There is no Phi calibration set (A15 adds none), so Phi GPU costs use the latency fallback.
- P6 grows with bootstrap resamples and plan count, not model calls.

## Advice for the lease

- Run P0 first on each VM (V2_P0=qwen on VM-A, V2_P0=granite on VM-B); V2_P0=tiers, complex and phi
  when those servers come up (every new setting is smoke-tested before its first step anyway).
  VM-A: P1, P2, P2b (servers 1.5B, 7B, 14B; VLLM_ENDPOINTS keyed by model id), then stop the 14B
  server, restore the 1.5B/7B memory split and run P2c. VM-B: P3, P4, P4b. P5 last.
- The time-budget cut runs by itself on the vllm backend (V2_LEASE_END defaults to the lease end).
- Start vLLM with `--max-model-len 8192` for HotpotQA (prompts up to 3,281 tokens), for every family (A14, A15).
- Set `V2_WORKERS=32` (the default), as in Session 1. The Mac runs used 1.
