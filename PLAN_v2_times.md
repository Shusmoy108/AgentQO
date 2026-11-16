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

Updated 2026-11-16 (A13-A15). Calls per problem from the q4 runs (Ollama 4-bit, 200 problems per
setting): math labels 124, math all_subsets 72, HotpotQA labels 91, HotpotQA all_subsets 42.
s/call from the Ollama table above. One setting at full size: math = 200 x 124 + 400 x 72 =
53,600 calls; HotpotQA (either workflow) = 200 x 91 + 400 x 42 = 35,000 calls.

| Phase | VM | Work | New calls | H100, 10x rule | H100, Session 1 rate |
|---|---|---|---|---|---|
| P0 | A, B | smoke test, 5 problems x all_small/all_large: Qwen isolated; Granite hotpot + isolated; Phi math + hotpot | ~250 | **< 10 min** + Phi server start | **< 5 min** |
| P1 | A | Qwen 1.5B/7B labels 200: math, HotpotQA, HotpotQA isolated (A13) | 61,200 | **2.9 h** | **36 min** |
| P2 | A | Qwen 1.5B/7B all_subsets 400: math (64 plans), HotpotQA, HotpotQA isolated (32 plans) | 62,400 | **6.6 h** | **37 min** |
| P3 | | Qwen 3B/14B math: labels 200 + all_subsets 400 | 53,600 | **~8.1 h** | **~64 min** |
| P4 | B | Granite 2B/8B, max_tokens 512: math, then hotpot_chain, then hotpot_chain_isolated (A14) | 123,600 | **~18.9 h** | **~2.5 h** |
| P4b | B | Phi-3.5-mini/phi-4 (A15), max_tokens 512: math, then hotpot_chain; last on VM-B | 88,600 | **~27.1 h** | **~3.5 h** |
| P5 | | 7 plans x 64 problems x 3 repeats x 3 placements, K=16 | 24,192 | **~1.8 h** + server restarts | n/a (latency-bound) |
| P5 cal | | A11 calibration: 3 model/task sets x 2 placements x 2 plans x 3 repeats x 64 problems | ~13,800 | **~1-1.5 h** + 6 server restarts | n/a (latency-bound) |
| P6 | | offline analysis, all settings | 0 | **< 5 min** | **< 5 min** |
| final | | zip with SQLite cache | 0 | **< 5 min** | **< 5 min** |
| **Total** | | | **~427,000** | **~67 h** | **~11.3 h** (8.3 h throughput + ~3 h P5 and P5 cal) |

Per VM: VM-A (P1, P2) ~9.5 h (10x rule) or ~73 min (Session 1 rate). VM-B (P4, P4b) ~46 h or
~6.0 h. P3, P5 and P5 cal add to whichever VM runs them. VM-B carries the most work, and P4b
alone is ~40% of the throughput time, which is why Phi runs last and is the first thing skipped.

**Session 1 caches no longer exist.** Every call above is generated fresh; the lease cache is a
new file (`data/cache/v2_lease1.sqlite`) and nothing looks for a Session 1 cache.

Assumptions behind the rows without a direct measurement:
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

- Run P0 first on each VM (V2_P0=qwen on VM-A, V2_P0=granite on VM-B; V2_P0=phi when the Phi
  servers come up before P4b, so the servers are swapped once). Then P1 and P2 on VM-A, P4 then
  P4b on VM-B. The 10x rule puts VM-B at about two days, the Session 1 rate at about 6 h; P5
  stays last because it needs the servers re-placed. If time runs short, skip Phi with
  `scripts/v2/smoke_check.py skip math_phi "time"` (and `hotpot_phi`); the skip is logged.
- Start vLLM with `--max-model-len 8192` for HotpotQA (prompts up to 3,281 tokens), for every family (A14, A15).
- Set `V2_WORKERS=32` (the default), as in Session 1. The Mac runs used 1.
