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

Sizes after amendment A8 (FIX 4): math labels 200, HotpotQA eval 400.

| Phase | Work | New calls | Ollama (measured rate) | H100, 10x rule | H100, Session 1 rate |
|---|---|---|---|---|---|
| P1 | math labels 200 + HotpotQA labels 200 | 43,540 | 20.9 h | **2.1 h** | **26 min** |
| P2 | math all_subsets 400 + HotpotQA all_subsets 400 | 48,240 | 49.7 h | **5.0 h** | **29 min** |
| P3 | Qwen 3B/14B math: labels 200 + all_subsets 400 | 56,860 | - | **~8.7 h** | **~70 min** |
| P4 | Granite 2B/8B math (labels 200, max_tokens 512) | 56,860 | - | **~8.7 h** | **~70 min** |
| P5 | 7 plans x 64 problems x 3 repeats x 3 placements, K=16 | 24,192 | ~18 h | **~1.8 h** + server restarts | n/a (latency-bound) |
| P5 cal | A11 calibration: 3 model/task sets x 2 placements x 2 plans x 3 repeats x 64 problems | ~13,800 | ~10 h | **~1-1.5 h** + 6 server restarts | n/a (latency-bound) |
| P1+P2 A13 | Qwen 1.5B/7B hotpot_chain_isolated: labels 200 + all_subsets 400 (VM-A, after HotpotQA) | 34,920 | 26.9 h | **2.7 h** | **21 min** |
| P4 A14 | Granite 2B/8B hotpot_chain + hotpot_chain_isolated: labels 200 + all_subsets 400 each, max_tokens 512 (VM-B, after Granite math) | 69,840 | - | **~10.8 h** | **~83 min** |
| P6 | offline analysis, all settings | 0 | ~1 min | **< 5 min** | **< 5 min** |
| final | zip with SQLite cache | 0 | - | **< 5 min** | **< 5 min** |
| **Total** | | ~349,000 | | **~41 h** | **~8.2 h** (P5 and P5 cal at ~3 h) |

The first 100 math label problems and the first 200 math eval problems are the Session 1
ones, so on the H100 their Qwen 1.5B/7B calls replay from the Session 1 vLLM cache if it is
copied over; the table does not count that saving. HotpotQA calls per problem were measured
before FIX 1; the new prompts are about the same length.

Assumptions behind the rows without a direct measurement:
- A13/A14 (added 2026-11-12): calls per problem as measured for HotpotQA (labels 91.0, all_subsets
  41.8), so one HotpotQA setting = 18,200 + 16,720 calls. The isolated prompts are shorter
  (no paragraphs in two of five nodes), so this is an upper bound. Granite HotpotQA is timed
  as twice the Qwen HotpotQA time, as for Granite math (512-token cap). Per VM: VM-A +2.7 h
  (10x rule) or +21 min (Session 1 rate); VM-B +10.8 h or +83 min. VM-B now carries the most work.
- P3 and P4 make the same number of calls as P1+P2 math (labels 200). Their time is twice the Qwen
  1.5B/7B math time: 14B decodes about 2x slower than 7B, and Granite has a 512-token cap
  against Qwen's 256. Not measured; only `qwen2.5:3b` has a local Ollama build.
- P5 runs in real time against live servers and bypasses the cache, so it scales with
  latency, not throughput. Taken from the M6 run: mean plan wall 325 s per 20 problems, times
  64/20 problems, 7 plans, 3 repeats, 3 placements, / 10. Switching placement means
  restarting vLLM (~2-5 min each in Session 1), which isn't counted.
- P5 cal (A11) is timed like P5: the M6 run's mean plan wall (325 s per 20 problems on Ollama)
  x 64/20 x 2 plans x 3 repeats x 6 (set, placement) pairs / 10. Qwen 14B and Granite 8B are
  slower than Qwen 7B, hence the range. Each set needs its own servers in both placements.
- P6 grows with bootstrap resamples and plan count, not model calls.

## Advice for the lease

- Run P1 and P2 first. The 10x rule puts the full lease at just over a day of GPU time,
  and the Session 1 rate at about half a working day. Either way it fits, with P5 last
  because it needs the servers re-placed.
- Start vLLM with `--max-model-len 8192` for HotpotQA (prompts up to 3,281 tokens).
- Set `V2_WORKERS=32` (the default), as in Session 1. The Mac runs used 1.
