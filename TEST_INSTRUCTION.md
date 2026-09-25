# Testing Phase A (laptop hardening, WP0 to WP7)

Run the steps in order from the repository root. Nothing here needs a GPU or a
running LLM server. The first run needs internet access to download GSM8K
(about 750 KB) and a tiny test model (a few MB). After that, everything runs
offline from the cache.

Every experiment script appends one entry to `RESULTS.md`. To start with a
clean log, run step 0.3 first.

Total time: about 20 to 30 minutes, most of it in steps 2 and 3.

---

## 0. Setup

### 0.1 Activate the environment

```bash
cd ~/AgentQO
source .venv/bin/activate
python --version          # 3.12.x
```

### 0.2 Install dependencies (once)

```bash
pip install -e ".[all]"
python -c "import torch, transformers; print(torch.__version__, transformers.__version__, torch.backends.mps.is_available())"
```

Pass: prints two version numbers and `True` (Apple GPU available).

### 0.3 Start a clean results log and clean outputs (optional)

```bash
mv RESULTS.md RESULTS.prev.md 2>/dev/null
rm -rf data/h2 data/h2_noise data/h3 data/agentqo_* data/real data/cache
```

---

## 1. Unit tests

### 1.1 Full suite

```bash
pytest tests/ -q
```

Pass: `109 passed` (about 20 s). If you are offline and GSM8K or the tiny model
is not cached yet, one or two tests show as `skipped`, not failed.

### 1.2 Per work package (run these to see what each WP guarantees)

```bash
# WP0.2  runtime predictor never trained on the runtime workflow; CSV has ec_source
pytest tests/test_runtime_ec_source.py -v

# Leak fix  different workflows never share task instances
pytest tests/test_label_seeds.py -v

# WP1  answer extraction (19 output styles), 50 gold strings score 1.0, answer-node priority
pytest tests/test_answers.py -v

# WP1  no code outside the simulator reads hidden importance or difficulty
pytest tests/test_no_leakage.py -v

# WP3/WP4  substitution changes descendant inputs, non-descendants byte-identical,
#          forced node not executed, flag mode refused for real backends, p_err 0 and 1
pytest tests/test_substitution.py -v

# WP5  cached rerun gives identical labels with zero HTTP calls; seed in every
#      request; 32 workers at least 15x faster than 1
pytest tests/test_cache.py -v

# WP6  probe embeddings deterministic, dimension = model hidden size
pytest tests/test_probe.py -v
```

Pass: every test passes.

---

## 2. WP0: simulator experiments

### 2.1 WP0.1: full H3 with oracle bound and bootstrap CIs (about 5 min)

```bash
python scripts/run_h3_allocation.py --num-runs 30 --oracle | tee data/h3_full.log
grep -E "AUC|Confidence|Uniform|bottleneck" data/h3_full.log | grep -v "^ *-"
```

Pass:
- Prints AUC with a 95% CI for AgentQO, Oracle-EC, Confidence, Uniform.
- Prints paired differences, for example `AgentQO - Confidence +1.554 [+0.844, +2.226]`.
- Prints a `bottleneck:` line (`none`, `predictor`, or `allocator`).
- Files exist: `data/h3/h3_results.json`, `data/h3/h3_quality_cost.csv`
  (with `ci_low`, `ci_high`), `data/h3/h3_quality_cost_<workflow>.png`.
- `RESULTS.md` has a new `S-H3` entry.

Expected value: AgentQO beats both baselines with CIs excluding 0; bottleneck
`none`.

### 2.2 WP0.2 and WP0.3: runtime with predicted EC, 5 seeds, 3 loads (about 1 min each)

```bash
for src in predicted structure oracle; do
  python scripts/run_agentqo.py --ec-source $src --seeds 5 --loads low,med,high \
      --output-dir data/agentqo_$src | tee data/agentqo_$src.log
done
head -2 data/agentqo_predicted/agentqo_runtime.csv
grep "predictor_trained_on" -A8 data/agentqo_predicted/agentqo_runtime.json
```

Pass:
- The CSV header contains `ec_source`.
- Each cell prints `Q=mean [low, high]` and an `AgentQO-FCFS` paired
  difference with a CI.
- `predictor_trained_on` for `math_reasoning_s3_ver` does **not** contain
  `math_reasoning_s3_ver`.
- Files exist: `agentqo_runtime.csv`, `agentqo_runtime_summary.csv`,
  `agentqo_runtime.json`, `agentqo_pareto.png` in each output directory.
- `RESULTS.md` has three new `S-RT` entries.

Known result (not a test failure): AgentQO numbers are almost the same for all
three EC sources, and it makes about 250 edits per episode on self-consistency.
See the `S-RT note` in `RESULTS.md`.

### 2.3 WP0.4: circularity check (about 3 min each)

```bash
python scripts/run_h2_predictor.py --output-dir data/h2 | tee data/h2_hidden.log
python scripts/run_h2_predictor.py --embedding-signal none --output-dir data/h2_noise | tee data/h2_noise.log
grep -A6 "^Model " data/h2_hidden.log | head -7
grep -A6 "^Model " data/h2_noise.log | head -7
```

Pass:
- Both runs print a table with `AgentQO`, `Structure-Only`, `Confidence-Only`,
  `Structure+Noise`.
- In the noise run, AgentQO is about equal to `Structure+Noise` (expected
  about 0.33 vs 0.33). This shows that noise embeddings give no gain.
- `RESULTS.md` has `S-H2` and `S-CIRC` entries.

Known result: sim H2 fails (AgentQO about 0.35 vs Structure-Only about 0.38)
now that the seed leak is fixed.

---

## 3. WP1 to WP7: real-task pipeline on the fake server

### 3.1 Smoke stage (seconds)

```bash
python scripts/run_real_pipeline.py --backend fake --n-tasks 5 --stage smoke
```

Pass: 10 lines (5 small, 5 large), each with `conf_src=logprobs` and
`cache_hit_on_rerun=True`.

### 3.2 WP7 acceptance: dry run, 10 GSM8K tasks (seconds)

```bash
python scripts/run_real_pipeline.py --backend fake --n-tasks 10 | tee data/dry.log
grep -E "^H1|HTTP|skipped" data/dry.log
```

Pass:
- Three `H1` lines (math, self-consistency, complex), each with
  `key_change=1.0` (every corruption changed the key: V4 target is at least 0.9).
- Per-node lines with consequence, CI, `p_err`, and `ec`.
- H2/H3 print `skipped: embeddings are placeholders`. This is intended: H2
  refuses hash embeddings.
- `data/real/fake/h1/<workflow>/` contains `traces/`, `substitutions/`,
  `h1_labels.csv`, `role_summary.csv`, `absorption.csv`, `h1_summary.json`,
  `h1_consequence.png`. Check with:

```bash
ls data/real/fake/h1/*/
python -c "import json; print(json.load(open('data/real/fake/h1/math_reasoning_s3_ver/h1_summary.json'))['invariant_violations'])"
```

  The second command must print `0` (V5 isolation invariant).

Known result: math and complex print `holds=False` because the H1 smoke test
compares planner consequence against the verifier or formatter. On real text
those two hold the final answer, so their consequence is highest; their EC is
about 0 because `p_err` is about 0. This is an open decision (see the end of
this file).

### 3.3 Determinism: rerun from the cache (V6)

```bash
python scripts/run_real_pipeline.py --backend fake --n-tasks 10 | grep HTTP
```

Pass: `HTTP calls: 0`. Every request came from `data/cache/generations.sqlite`.

### 3.4 Full dry run with a real hidden-state probe (H2 and H3 included, about 1 min)

```bash
python scripts/run_real_pipeline.py --backend fake --n-tasks 10 --probe hf \
    --probe-model trl-internal-testing/tiny-Qwen2ForCausalLM-2.5 \
    --output-dir data/real/fake_hfprobe | tee data/dry_hf.log
grep -E "HTTP|H2 HOLDS|H3 holds|bottleneck" data/dry_hf.log | sort -u
ls data/real/fake_hfprobe/h2 data/real/fake_hfprobe/h3
```

Pass:
- `HTTP calls: 0` (same prompts as step 3.2, so all cached).
- H2 and H3 run and print a result (PASS or FAIL does not matter here: the
  fake server and a tiny random model are not a result).
- `h2/` and `h3/` contain CSV, JSON, and PNG files.

### 3.5 Read the evidence by hand (V9-style spot check)

```bash
# One task, every node: prompt, output, extracted key, confidence, tokens
python -m json.tool "$(ls data/real/fake/h1/math_reasoning_s3_ver/traces/*.json | head -1)" | head -60

# One substitution chain: reference, 3 corruptions, recomputed descendants, q_plus, q_minus
python -m json.tool "$(ls data/real/fake/h1/math_reasoning_s3_ver/substitutions/*_aggregator.json | head -1)" | head -60

# Where errors die: which node absorbed each corruption
column -s, -t < data/real/fake/h1/complex_r2_s2_ver/absorption.csv | head -20
column -s, -t < data/real/fake/h1/complex_r2_s2_ver/role_summary.csv
```

Pass: for a corrupted aggregator, the verifier's text in `descendants` differs
from `descendants_plus`, and `quality` matches whether the final `####` number
equals the gold answer.

---

## 4. Acceptance checklist

| WP | Criterion | Where to check |
|---|---|---|
| WP0.1 | Oracle and predicted curves with bootstrap CIs; bottleneck stated | step 2.1, `RESULTS.md` S-H3 |
| WP0.2 | `ec_source` column; predictor never trained on runtime workflow | step 2.2, `test_runtime_ec_source.py` |
| WP0.3 | Table with CIs, paired AgentQO minus FCFS, Pareto plot | step 2.2 |
| WP0.4 | Both H2 runs reported; noise run about equal to control | step 2.3, `RESULTS.md` S-CIRC |
| WP1 | 15+ extraction styles; 50 gold strings score 1.0; no leakage | `test_answers.py`, `test_no_leakage.py` |
| WP2 | Answer extractable from answer node | step 3.2 traces: every `final_key` is a number |
| WP3 | Descendants see substituted text; non-descendants identical | `test_substitution.py`, step 3.2 `invariant_violations = 0` |
| WP4 | p_err 0 for always-agree, 1 for always-disagree | `test_substitution.py::test_p_err_*` |
| WP5 | Identical labels and zero HTTP calls on rerun; at least 15x speedup | `test_cache.py`, step 3.3 |
| WP6 | Deterministic; dim = hidden size | `test_probe.py` (the under-50 ms GPU cost is measured in Phase B) |
| WP7 | Dry run completes and writes all artifacts | steps 3.2 and 3.4 |

## 5. Known open items (not failures of this phase)

1. **H1 formatter smoke test on real text.** The verifier and formatter are
   answer nodes, so their consequence is high by construction while their EC
   is about 0. Decide whether the check compares EC, or whether the formatter
   should stop being an answer node.
2. **Runtime speculative stopping reads ground-truth correctness.** A real
   runtime cannot see it; to be fixed in WP13.
3. **Real H2 folds share GSM8K problems across workflows.** Decide whether to
   use problem-disjoint folds.
4. Not in Phase A: HotpotQA loader, Ollama backend (WP7b), GPU timing of the
   probe.
