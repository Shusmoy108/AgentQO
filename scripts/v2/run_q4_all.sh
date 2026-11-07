#!/usr/bin/env bash
# A12: the q4 setting (Qwen2.5 1.5B/7B Q4_K_M via Ollama) end to end, unattended.
#   nohup caffeinate -dimsu bash scripts/v2/run_q4_all.sh > logs/v2_q4/nohup.out 2>&1 &
#   bash scripts/v2/run_q4_all.sh --dry-run     # print the plan and each step's commands
# Re-running resumes: finished steps (logs/v2_q4/done_Q4-n) are skipped, the rest resume
# from the SQLite cache and existing outputs. No code is changed; it drives run_phase.sh.
set -uo pipefail

DRY=0
case "${1:-}" in
  --dry-run) DRY=1 ;;
  -h|--help) sed -n 2,6p "$0"; exit 0 ;;
  "") ;;
  *) echo "usage: run_q4_all.sh [--dry-run]" >&2; exit 2 ;;
esac

ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cd "$ROOT"
export PATH="$PATH:/opt/homebrew/bin:/usr/local/bin"  # appended: keep the python3 that has the packages
export V2_BACKEND=ollama V2_PUSH=1 V2_RESULTS=results/v2_q4 V2_LOGS=logs/v2_q4
export V2_CACHE=data/cache/v2_q4.sqlite V2_N=200 AGENTQO_VERIFIER=cautious
BRANCH=v2-q4
R=$V2_RESULTS L=$V2_LOGS PY=python3
OUTDIR="$HOME/AgentQO_results/v2_q4"
LOG="$L/driver.log"
MODELS=(qwen2.5:1.5b-instruct qwen2.5:7b-instruct)
DEADLINE=$(date -j -u -f "%Y-%m-%d %H:%M:%S" "2026-11-15 23:00:00" +%s)
BACKOFF=(60 120 300 600 1200)
mkdir -p "$R" "$L" "$OUTDIR" "$L/zips"
[ -f "$L/started_at" ] || date -u +%s > "$L/started_at"

ts() { perl -MPOSIX -pe 'BEGIN{$|=1} $_ = strftime("%Y-%m-%dT%H:%M:%SZ ", gmtime) . $_'; }
log() { echo "$*" | ts >> "$LOG"; }
status() { echo "$(date -u +%FT%TZ) $*" >> "$R/STATUS.md"; log "STATUS $*"; }
past_deadline() { [ "$(date -u +%s)" -ge "$DEADLINE" ]; }

# ---- Ollama -------------------------------------------------------------
ollama_ok() {
  local m
  for m in "${MODELS[@]}"; do
    curl -sf -m 600 http://localhost:11434/api/generate \
      -d "{\"model\":\"$m\",\"prompt\":\"Say OK.\",\"stream\":false,\"options\":{\"num_predict\":3}}" >/dev/null || return 1
  done
}
ollama_up() {  # num_parallel
  log "starting ollama serve with OLLAMA_NUM_PARALLEL=$1"
  brew services stop ollama >/dev/null 2>&1
  pkill -f "ollama serve" 2>/dev/null; sleep 3
  OLLAMA_NUM_PARALLEL=$1 OLLAMA_KEEP_ALIVE=-1 nohup ollama serve >> "$L/ollama.log" 2>&1 &
  sleep 30
  ollama_ok && log "ollama up: both models answer" && return 0
  log "ollama serve did not answer; trying brew services restart"
  pkill -f "ollama serve" 2>/dev/null; sleep 3
  brew services restart ollama >/dev/null 2>&1; sleep 30
  ollama_ok && log "ollama up via brew (its own OLLAMA_NUM_PARALLEL)"
}
ensure_ollama() { ollama_ok || { log "ollama not responding: restarting"; ollama_up "$PAR"; }; }

# ---- Disk ---------------------------------------------------------------
disk_ok() {
  local free
  free=$(df -g "$ROOT" | awk 'NR==2 {print $4}')
  if [ "$free" -lt 10 ]; then
    local old
    for old in results/v2_dry*/ results/v2_t20/; do
      [ -d "$old" ] && { log "disk ${free} GB free < 10: deleting $old"; rm -rf "$old"; }
    done
    free=$(df -g "$ROOT" | awk 'NR==2 {print $4}')
    log "disk ${free} GB free after cleanup"
  fi
  [ "$free" -ge 2 ]  # under 2 GB the SQLite cache is at risk: fail the attempt
}

# ---- Git ----------------------------------------------------------------
push_results() {  # message
  local f
  find "$R" -type f \( -name '*.csv' -o -name '*.json' -o -name '*.md' -o -name '*.txt' \) -size -20M -print0 |
    xargs -0 git add -f -- 2>>"$LOG"
  find "$R" -type f -size +20M | while read -r f; do log "not pushed (over 20 MB): $f"; done
  git add CHANGELOG_v2.md 2>>"$LOG"
  git diff --cached --quiet || git commit -q -m "q4 results: $1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" >>"$LOG" 2>&1
  git push -q origin "$BRANCH" >>"$LOG" 2>&1 || log "push to $BRANCH failed; the next push retries"
}
changelog() { printf '\n%s\n' "$*" >> CHANGELOG_v2.md; }

# ---- Throughput test ----------------------------------------------------
calls_in() { "$PY" -c "import sqlite3,sys;print(sqlite3.connect(sys.argv[1]).execute('select count(*) from gen').fetchone()[0])" "$1"; }
keys_in() { "$PY" -c "import sqlite3,sys;print('\n'.join(k for (k,) in sqlite3.connect(sys.argv[1]).execute('select key from gen order by key')))" "$1"; }
tput_run() {  # parallel -> prints calls/s
  local p=$1 c="$L/tput_p$1.sqlite" t0 t1
  rm -rf "$c" "$L/tput/p$p"
  ollama_up "$p" || return 1
  t0=$(date +%s)
  "$PY" scripts/run_real_h3.py --backend ollama --cache "$c" --workflow math --dataset gsm8k --split eval_ext \
    --n-tasks 5 --max-tokens 256 --workers "$p" --plans all_small,all_large --allow-missing-logprobs \
    --output-dir "$L/tput/p$p" 2>&1 | ts >> "$LOG" || return 1
  t1=$(date +%s)
  "$PY" -c "print(round($(calls_in "$c") / max(1, $t1 - $t0), 4))"
}
throughput_test() {
  if [ -f "$L/parallel.txt" ]; then
    PAR=$(cut -d' ' -f1 "$L/parallel.txt"); CPS=$(cut -d' ' -f2 "$L/parallel.txt")
    log "throughput test already done: parallel $PAR ($CPS calls/s)"; return
  fi
  local c2 c1 same=no keep=1
  log "throughput test: 5 math problems, all_small + all_large, OLLAMA_NUM_PARALLEL/V2_WORKERS 2/2 then 1/1"
  c2=$(tput_run 2) || c2=0
  c1=$(tput_run 1) || c1=0
  diff -q <(keys_in "$L/tput_p2.sqlite") <(keys_in "$L/tput_p1.sqlite") >/dev/null 2>&1 && same=yes
  "$PY" -c "import sys; sys.exit(0 if $c1 > 0 and $c2 >= 1.2 * $c1 else 1)" && [ $same = yes ] && keep=2
  PAR=$keep; CPS=$([ $keep = 2 ] && echo "$c2" || echo "$c1")
  echo "$PAR $CPS" > "$L/parallel.txt"
  log "throughput test: 2/2 $c2 calls/s, 1/1 $c1 calls/s, cache keys identical: $same -> using $PAR/$PAR"
  changelog "$(date -u '+%Y-%m-%d %H:%M:%S UTC') q4 throughput test (5 math problems, all_small + all_large, fresh caches): 2/2 $c2 calls/s, 1/1 $c1 calls/s, cache keys identical: $same. Using OLLAMA_NUM_PARALLEL=$PAR, V2_WORKERS=$PAR (rule: 2/2 only if >= 20% faster and keys identical)."
  push_results "throughput test"
}

# ---- Steps --------------------------------------------------------------
NAMES=("" "math labels" "math all_subsets" "HotpotQA labels" "HotpotQA all_subsets" "analysis")
PHASE=("" P1 P2 P1 P2 P6)

analysis() {
  local sw s wf lab fast pl o
  "$PY" scripts/v2/summarize_phase.py provenance "$R/P6" || return 1
  for sw in math_q15_7:math hotpot_q15_7:hotpot; do
    s=${sw%%:*} wf=${sw##*:}
    lab="$R/P1/$s/labels" fast="$R/P1/$s/labels_disagree" pl="$R/P2/$s/plans" o="$R/P6/$s"
    if [ ! -f "$lab/DONE" ] || [ ! -f "$fast/DONE" ] || [ ! -f "$pl/DONE" ]; then
      echo "skip $s: labels or plans not finished"; continue
    fi
    "$PY" scripts/v2/cost_report.py --calls "$pl/h3_calls.csv" --output-dir "$o/cost" &&
    "$PY" scripts/v2/rules_report.py --workflow "$wf" --labels "$lab/labels_v2.csv" --plans "$pl/h3_plans.csv" \
      --labels-disagree "$fast/labels_v2.csv" --output-dir "$o/rules" &&
    "$PY" scripts/v2/routing_offline.py --labels-per-problem "$lab/labels_v2_per_problem.csv" \
      --labels "$lab/labels_v2.csv" --workflow "$wf" --output-dir "$o/routing" &&
    "$PY" scripts/v2/adaptive_check.py --per-problem "$pl/h3_per_problem.csv" --output-dir "$o/adaptive" &&
    "$PY" scripts/v2/pareto.py --workflow "$wf" --costs "$o/cost/plan_costs.csv" --calls "$pl/h3_calls.csv" \
      --cost-metric api_usd --plans "$pl/h3_plans.csv" --output-dir "$o/pareto_api" &&
    "$PY" scripts/v2/pareto.py --workflow "$wf" --costs "$o/cost/plan_costs.csv" --calls "$pl/h3_calls.csv" \
      --cost-metric api_usd --plans "$o/rules/plan_estimates.csv" --estimator pairwise_corrected \
      --true-plans "$pl/h3_plans.csv" --output-dir "$o/pareto_estimated" || return 1
  done
  "$PY" scripts/v2/hypotheses_report.py --p6 "$R/P6" --output-dir "$R/P6/hypotheses" || return 1
  # A12: placement (H3) and GPU throughput cost are not testable on the Mac.
  "$PY" - "$R/P6/hypotheses/hypotheses.md" <<'EOF'
import re, sys
p = sys.argv[1]
md = open(p).read()
if "q4 (A12)" not in md:
    untestable = ("| H3a ", "| A2 ", "| H3c ", "| H4a ", "| A3 ")
    out = []
    for line in md.split("## Cost basis")[0].splitlines():
        if line.startswith(untestable):
            cells = line.split("|")
            line = "|".join(cells[:2] + [" not testable on Mac "] * (len(cells) - 3) + [""])
        out.append(line)
    out.insert(2, "Setting q4 (A12): Qwen2.5 1.5B/7B Q4_K_M via Ollama on a Mac. A separate 4-bit "
                  "setting, never pooled with vLLM data.\n")
    out += ["## Cost basis (A12)", "",
            "Not testable on Mac: placement (H3a, A2, H3c) and GPU throughput cost (A3, H4a). "
            "Costs are API prices from token counts only (`cost/plan_costs.csv` api_usd, "
            "`pareto_api/`, `pareto_estimated/`).", ""]
    open(p, "w").write("\n".join(out) + "\n")
EOF
}

headline() {  # step
  "$PY" - "$1" "$R" <<'EOF' 2>/dev/null || echo "finished"
import csv, json, sys
n, R = int(sys.argv[1]), sys.argv[2]
s = "math_q15_7" if n in (1, 2) else "hotpot_q15_7"
if n in (1, 3):
    rows = list(csv.DictReader(open(f"{R}/P1/{s}/labels/labels_v2.csv")))
    uv = ", ".join(f"{r['agent']} {float(r['uv']):.3f}" for r in rows)
    print(f"{s} labels on {rows[0]['n']} problems; UV {uv}")
elif n in (2, 4):
    rows = {r["plan"]: r for r in csv.DictReader(open(f"{R}/P2/{s}/plans/h3_plans.csv"))}
    best = max(rows.values(), key=lambda r: float(r["accuracy"]))
    print(f"{s} {len(rows)} plans; all_small {float(rows['all_small']['accuracy']):.3f}, "
          f"all_large {float(rows['all_large']['accuracy']):.3f}, best {best['plan']} {float(best['accuracy']):.3f}")
else:
    print(f"hypotheses.md for {len(json.load(open(f'{R}/P6/hypotheses/hypotheses.json')))} settings")
EOF
}

run_step() {  # n: one attempt; output into driver.log
  case $1 in
    1) V2_PUSH=0 V2_SETTINGS=math   V2_ZIP_DIR="$L/zips/Q4-1" scripts/v2/run_phase.sh P1 ;;
    2) V2_PUSH=0 V2_SETTINGS=math   V2_ZIP_DIR="$L/zips/Q4-2" scripts/v2/run_phase.sh P2 ;;
    3) V2_PUSH=0 V2_SETTINGS=hotpot V2_ZIP_DIR="$L/zips/Q4-3" scripts/v2/run_phase.sh P1 ;;
    4) V2_PUSH=0 V2_SETTINGS=hotpot V2_ZIP_DIR="$L/zips/Q4-4" scripts/v2/run_phase.sh P2 ;;
    5) analysis && V2_PUSH=0 V2_ZIP_DIR="$L/zips/Q4-5" scripts/v2/package_phase.sh P6 ;;
  esac
}

attempt() {  # n: run one attempt in the background; stop it at the deadline
  mkdir -p "$L/zips/Q4-$1"
  run_step "$1" > >(ts >> "$LOG") 2>&1 &
  local pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    if past_deadline; then
      log "deadline passed: stopping Q4-$1 (finished calls are in the cache)"
      pkill -TERM -f "scripts/run_real_" ; pkill -TERM -f "scripts/v2/run_phase.sh"; pkill -TERM -P "$pid"
      kill -TERM "$pid" 2>/dev/null; wait "$pid" 2>/dev/null
      return 2
    fi
    sleep 30
  done
  wait "$pid"
}

do_step() {  # n
  local n=$1 i rc=1 why=""
  [ -f "$L/done_Q4-$n" ] && { log "Q4-$n already done"; return 0; }
  for i in 0 1 2 3 4 5; do
    past_deadline && return 2
    if [ "$i" -gt 0 ]; then
      log "Q4-$n retry $i after ${BACKOFF[$((i-1))]} s"; sleep "${BACKOFF[$((i-1))]}"
      past_deadline && return 2
    fi
    if ! disk_ok; then why="under 2 GB free disk"; log "Q4-$n: $why"; continue; fi
    if ! ensure_ollama; then why="Ollama not responding after restart"; log "Q4-$n: $why"; continue; fi
    log "Q4-$n (${NAMES[$n]}) attempt $((i+1)) start, commit $(git rev-parse --short HEAD)"
    attempt "$n"; rc=$?
    [ $rc = 2 ] && return 2
    [ $rc = 0 ] && break
    why="exit code $rc"; log "Q4-$n attempt $((i+1)) failed: $why"
  done
  if [ $rc = 0 ]; then
    touch "$L/done_Q4-$n"
    local z
    z=$(ls -t "$L/zips/Q4-$n"/*.zip 2>/dev/null | head -1)
    [ -n "$z" ] && cp "$z" "$OUTDIR/Q4-${n}_$(basename "$z")"
    status "GATE Q4-$n DONE: $(headline "$n")"
  else
    status "GATE Q4-$n FAILED: $why after 6 attempts"
    { echo "## Q4-$n (${NAMES[$n]}) failed $(date -u +%FT%TZ): $why"; echo; echo '```';
      tail -50 "$LOG"; echo '```'; echo; } >> "$R/FAILURES.md"
  fi
  push_results "Q4-$n ${NAMES[$n]}"
}

# ---- FINAL --------------------------------------------------------------
FINAL_DONE=0
final() {
  [ $FINAL_DONE = 1 ] && return; FINAL_DONE=1
  log "FINAL start"
  local up cache
  up=$("$PY" - "$R" "$OUTDIR" "$V2_CACHE" "$L" <<'EOF'
import sys, zipfile
from pathlib import Path
R, OUT, CACHE, L = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])

def free(name):
    p, i = OUT / f"{name}.zip", 1
    while p.exists():
        i += 1
        p = OUT / f"{name}_{i}.zip"
    return p

def big_json(p):  # the per-substitution and per-trace JSON of the label runs
    return p.suffix == ".json" and ("substitutions" in p.parts or "traces" in p.parts)

files = sorted(p for p in R.rglob("*") if p.is_file())
keep = [p for p in files if p.suffix not in (".sqlite", ".zip") and not big_json(p)]
docs = [Path(p) for p in ("CHANGELOG_v2.md", "prereg/v2_amendments.md", str(L / "driver.log"), "PLAN_v2_times.md")]
readme = ["results_v2_q4_UPLOAD: setting q4 (A12), Qwen2.5 1.5B/7B Q4_K_M via Ollama.",
          "Everything under results/v2_q4/ except SQLite caches and the per-substitution / per-trace",
          "JSON of the label runs (those are in results_v2_q4_CACHE.zip on the Mac)."]
for drop in (False, True):
    sel = [p for p in keep if not (drop and p.name == "h3_traces.json")]
    up = free("results_v2_q4_UPLOAD")
    with zipfile.ZipFile(up, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sel + [d for d in docs if d.exists()]:
            z.write(p)
        z.writestr("README.txt", "\n".join(readme + (["h3_traces.json files dropped to stay under 100 MB."] if drop else [])) + "\n")
    if up.stat().st_size < 100e6 or drop:
        break
    up.unlink()
cz = free("results_v2_q4_CACHE")
with zipfile.ZipFile(cz, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as z:
    for p in [CACHE] + sorted(L.glob("tput_*.sqlite")) + [p for p in files if big_json(p) or p.name == "h3_traces.json"]:
        if p.exists():
            z.write(p)
print(up, cz)
EOF
) || log "FINAL: zip step failed"
  cache=${up#* }; up=${up%% *}
  [ -f "$up" ] && (cd "$OUTDIR" && shasum -a 256 "$(basename "$up")" "$(basename "$cache")") >> "$OUTDIR/CHECKSUMS.txt"
  push_results "FINAL"
  local hyp="$ROOT/$R/P6/hypotheses/hypotheses.md" t0 hours cps calls
  t0=$(cat "$L/started_at"); hours=$("$PY" -c "print(round(($(date -u +%s) - $t0) / 3600, 1))")
  calls=$( [ -f "$V2_CACHE" ] && calls_in "$V2_CACHE" || echo 0)
  cps=$("$PY" -c "print(round($calls / max(1, $(date -u +%s) - $t0), 3))")
  size() { [ -f "$1" ] && du -h "$1" | cut -f1 || echo "missing"; }
  {
    echo "# Upload to Claude: q4 results"; echo
    echo "Upload these files, in this order:"; echo
    echo "1. \`$up\` ($(size "$up"))"
    echo "2. \`$hyp\` ($(size "$hyp"))"
    echo "3. \`$ROOT/$R/STATUS.md\` ($(size "$ROOT/$R/STATUS.md"))"
    [ -f "$R/FAILURES.md" ] && echo "4. \`$ROOT/$R/FAILURES.md\` ($(size "$ROOT/$R/FAILURES.md"))"
    echo
    echo "Keep on the Mac: \`$cache\` (SQLite cache and per-substitution JSON). Checksums: \`$OUTDIR/CHECKSUMS.txt\`."
    echo
    echo "What ran: $(grep -c ' DONE' "$R/STATUS.md" 2>/dev/null || echo 0) of 5 steps finished" \
         "($(grep -o 'GATE Q4-[0-9] DONE' "$R/STATUS.md" 2>/dev/null | cut -d' ' -f2 | paste -sd, - || true))." \
         "Failed: $(grep -o 'GATE Q4-[0-9] FAILED' "$R/STATUS.md" 2>/dev/null | cut -d' ' -f2 | paste -sd, - | sed 's/^$/none/')." \
         "$(grep -q 'PAUSED for lease' "$R/STATUS.md" 2>/dev/null && echo 'Paused at the 2026-11-15 23:00 UTC deadline; re-run the script to resume.' || echo 'Not paused.')" \
         "Total wall time since the first start: $hours h. Ollama setting: OLLAMA_NUM_PARALLEL=$PAR, V2_WORKERS=$PAR" \
         "(throughput test: $CPS calls/s); overall $cps calls/s ($calls cached calls over the whole run, including waits and analysis)."
  } > "$OUTDIR/UPLOAD_TO_CLAUDE.md"
  log "FINAL done: $OUTDIR/UPLOAD_TO_CLAUDE.md"
}

# ---- Main ---------------------------------------------------------------
if [ $DRY = 1 ]; then
  echo "q4 plan: throughput test (2/2 vs 1/1), then Q4-1..Q4-5, then FINAL into $OUTDIR"
  echo "results $R, logs $L, cache $V2_CACHE, branch $BRANCH, deadline 2026-11-15 23:00 UTC"
  for p in P1 P2; do V2_DRY=1 V2_PUSH=0 V2_RESULTS="$L/dry" V2_LOGS="$L/dry" scripts/v2/run_phase.sh $p; done
  exit 0
fi

log "=== run_q4_all start, commit $(git rev-parse HEAD), branch $(git rev-parse --abbrev-ref HEAD)"
[ "$(git rev-parse --abbrev-ref HEAD)" = "$BRANCH" ] || { log "not on $BRANCH: stopping"; exit 1; }
[ -z "$(git status --porcelain --untracked-files=no)" ] || log "warning: tracked changes in the working tree"
PAR=1 CPS=0
trap 'log "signal: stopping"; final; exit 1' INT TERM HUP
throughput_test
export V2_WORKERS=$PAR
ollama_up "$PAR"  # serve with the chosen OLLAMA_NUM_PARALLEL
for n in 1 2 3 4 5; do
  do_step "$n"
  if [ $? = 2 ] || past_deadline; then
    status "PAUSED for lease"
    break
  fi
done
final
log "=== run_q4_all end"
