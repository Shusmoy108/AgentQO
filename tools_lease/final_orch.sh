#!/usr/bin/env bash
# Lease 2 FINAL (PI FINAL spec 2026-11-16, cache part per the PI NEXT of 2026-11-17 04:10Z: compressed per-VM caches built
# and verified on the VMs, only the compressed files copied to the Mac, no uncompressed cache copy on the Mac, no deletions
# on the Mac). Waits for 2026-11-19T06:00Z (FINAL_NOW=1 starts at once). FINAL_DRY=1: build into $R/FINAL_dryrun without
# touching the VM caches, git, or mac_sync (for testing the zip build).
set -uo pipefail
R=~/AgentQO_results/v2; WT=~/AgentQO_lease; EV=$R/events.log; ST=$R/STATUS.md; T=$R/tools; REPO=/mnt/data/AgentQO
DRY=${FINAL_DRY:-0}; OUT=$R/FINAL; [ $DRY = 1 ] && OUT=$R/FINAL_dryrun
ts() { date -u +%FT%TZ; }
log() { echo "$(ts) FINAL $*" | tee -a $ST >> $EV; }
warn() { echo "$(ts) WARN FINAL $*" | tee -a $ST >> $EV; }
macfree() { echo $(( $(df -k ~ | tail -1 | awk '{print $4}') / 1024 / 1024 )); }
floor() { [ "$(macfree)" -ge 10 ] || { echo "$(ts) ACTION NEEDED: Mac disk ($(macfree) GB free) during FINAL $1" | tee -a $ST >> $EV; echo "ACTION NEEDED: Mac disk"; exit 2; }; }

if [ "${FINAL_NOW:-0}" != 1 ] && [ $DRY != 1 ]; then
  until python3 -c 'import datetime as d,sys; sys.exit(d.datetime.now(d.timezone.utc) < d.datetime(2026,11,19,6,tzinfo=d.timezone.utc))'; do sleep 30; done
fi
log "START (dry=$DRY); Mac free $(macfree) GB"
mkdir -p $OUT; floor start

# 0) No GPU work after the 06:00Z cutoff: report any block still running (never killed here; final_guard stops X work)
if [ $DRY != 1 ]; then
  for v in A B; do
    r=$(ssh -o ConnectTimeout=30 agentqo-$v 'tmux ls 2>/dev/null | grep -o "^blk_[^:]*" | tr "\n" " "')
    [ -n "$r" ] && warn "VM-$v still has blocks at FINAL start: $r"
  done
  # mac_sync would race FINAL's pulls, backups and pushes: stop it (logged); FINAL does its own pulls and push
  if kill -0 "$(cat $R/mac_sync.pid 2>/dev/null)" 2>/dev/null; then kill "$(cat $R/mac_sync.pid)"; log "mac_sync stopped for FINAL (pid $(cat $R/mac_sync.pid))"; fi
fi

# 1) Pull everything from both VMs (results, logs incl. power logs, amendments, zips); retried until a pass changes nothing
pull_full() {  # v
  local v=$1 h=agentqo-$1 i
  for i in $(seq 1 12); do
    rsync -az --partial --timeout=120 --exclude '*.sqlite*' $h:$REPO/results/v2/ $R/vm-$v/results/v2/ &&
    rsync -az --partial --timeout=120 $h:$REPO/logs/ $R/vm-$v/logs/ &&
    rsync -az $h:$REPO/prereg/v2_amendments.md $R/vm-$v/lease_logs/ &&
    { rsync -az --include '*.zip' --exclude '*' $h:$REPO/ $R/zips/vm-$v/ 2>/dev/null; true; } &&
    [ -z "$(rsync -az --dry-run --itemize-changes --timeout=60 --exclude '*.sqlite*' $h:$REPO/results/v2/ $R/vm-$v/results/v2/ | grep -v '^\.d')" ] && return 0
    sleep 20
  done
  return 1
}
if [ $DRY != 1 ]; then
  for v in A B; do pull_full $v && log "pulled VM-$v completely" || warn "VM-$v pull incomplete after 12 tries"; done
fi

# 2) Data completeness check, then search ground truth (front/hypervolume, usable-for-search flags)
mkdir -p $OUT/results/v2/FINAL
python3 $T/final_check.py $OUT/results/v2/FINAL/data_check.md > /dev/null || warn "final_check.py failed"
nmiss=$(grep -o 'Summary: [0-9]* MISSING' $OUT/results/v2/FINAL/data_check.md | grep -o '[0-9]*')
log "data check: ${nmiss:-?} MISSING item(s) (results/v2/FINAL/data_check.md)"
[ "${nmiss:-1}" = 0 ] || warn "data check lists MISSING items; regenerate from the cache before 09:00Z if possible, otherwise they stay listed with the reason"

# 3) Staging tree with the git layout: VM-A phases as is; VM-B phases P3/P4/P4b from VM-B (VM-A only holds copies; its P3
#    copy has 2 truncated files), VM-B's P0/P5/X* as <phase>_vmB. No caches, no per-substitution JSON, no rsync partials.
S=$OUT/stage; rm -rf $S; mkdir -p $S/results/v2
X="--exclude=*.sqlite* --exclude=.* --exclude=substitutions/"
for p in $(ls $R/vm-A/results/v2); do
  case $p in P3|P4|P4b) continue ;; esac
  rsync -a $X $R/vm-A/results/v2/$p $S/results/v2/
done
for p in $(ls $R/vm-B/results/v2); do
  case $p in P3|P4|P4b) d=$p ;; GATES) d=GATES_vmB ;; *) d=${p}_vmB ;; esac
  mkdir -p $S/results/v2/$d; rsync -a $X $R/vm-B/results/v2/$p/ $S/results/v2/$d/
done
mkdir -p $S/results/v2/P6_X $S/logs; rsync -a $WT/results/v2/P6_X/ $S/results/v2/P6_X/
python3 $T/search_gt.py $S/results/v2/P6/search_ground_truth.md > /dev/null || warn "search_gt.py failed"
cp $OUT/results/v2/FINAL/data_check.md $S/results/v2/FINAL/ 2>/dev/null || { mkdir -p $S/results/v2/FINAL; cp $OUT/results/v2/FINAL/data_check.md $S/results/v2/FINAL/; }
for v in A B; do rsync -a --exclude='.*' $R/vm-$v/logs/ $S/logs/vm$v/; done
cp $ST $EV $S/; cp -r $WT/prereg $S/; cp $WT/CHANGELOG_v2.md $WT/PLAN_v2_times.md $S/ 2>/dev/null
mkdir -p $S/orchestration; cp $T/*.sh $T/*.py $S/orchestration/ 2>/dev/null
[ -f $R/vm-A/results/v2/FAILURES.md ] && cp $R/vm-A/results/v2/FAILURES.md $S/results/v2/FAILURES_vmA.md
[ -f $R/vm-B/results/v2/FAILURES.md ] && cp $R/vm-B/results/v2/FAILURES.md $S/results/v2/FAILURES_vmB.md
# every h3_per_problem.csv and h3_calls.csv must be in the zip
n_src=$(cd $R && { find vm-A/results/v2 -not -path 'vm-A/results/v2/P3/*' -not -path 'vm-A/results/v2/P4/*' -not -path 'vm-A/results/v2/P4b/*' \( -name h3_per_problem.csv -o -name h3_calls.csv \); find vm-B/results/v2 \( -name h3_per_problem.csv -o -name h3_calls.csv \); } | wc -l)
n_stg=$(find $S/results/v2 \( -name h3_per_problem.csv -o -name h3_calls.csv \) | wc -l)
[ "$n_src" -eq "$n_stg" ] && log "staging: $n_stg per-problem/per-call CSVs (all of them)" || warn "staging has $n_stg per-problem/per-call CSVs, sources have $n_src"
floor staging

# 4) results_v2_UPLOAD.zip (<= 300 MB; if larger, drop h3_traces.json first, never the per-problem or per-call CSVs)
Z=$OUT/results_v2_UPLOAD.zip; rm -f $Z
(cd $S && zip -q -r -9 $Z .) || warn "zip failed"
if [ "$(stat -f%z $Z)" -gt 300000000 ]; then
  log "UPLOAD zip $(( $(stat -f%z $Z) / 1000000 )) MB > 300 MB: rebuilding without h3_traces.json"
  printf 'results_v2_UPLOAD.zip\n\nh3_traces.json files were left out: with them the zip was over 300 MB (PI FINAL rule: drop h3_traces.json first,\nnever the per-problem or per-call CSVs). They are in results_v2_CACHE/excluded_json.zip.\n' > $S/README.txt
  rm -f $Z; (cd $S && zip -q -r -9 $Z . -x '*/h3_traces.json') || warn "zip failed"
  DROPPED_TRACES=1
fi
unzip -tq $Z > /dev/null && log "UPLOAD zip $(( $(stat -f%z $Z) / 1000000 )) MB, unzip -t OK" || warn "UPLOAD zip failed unzip -t"
floor upload-zip

# 5) results_v2_CACHE: per-VM compressed caches built and verified on the VMs (sqlite backup + integrity_check + zstd,
#    decompressed sha256 = backup sha256), only the .zst copied, sha256 verified on the Mac; plus the excluded JSON
C=$OUT/results_v2_CACHE; mkdir -p $C
J=$C/excluded_json.zip; rm -f $J
(cd $R && { find vm-A/results/v2 vm-B/results/v2 -path '*/substitutions/*' -not -name '.*'; [ "${DROPPED_TRACES:-0}" = 1 ] && find vm-A/results/v2 vm-B/results/v2 -name h3_traces.json; } | zip -q -9 $J -@) && unzip -tq $J > /dev/null && log "excluded JSON zip $(du -h $J | cut -f1), unzip -t OK" || warn "excluded JSON zip failed"
if [ $DRY != 1 ]; then
  for v in A B; do
    mkdir -p $C/vm-$v
    for f in $(ssh agentqo-$v "ls $REPO/data/cache/*.sqlite"); do
      b=$(basename $f .sqlite)
      out=$(ssh agentqo-$v "bash /mnt/data/zbackup.sh $f && /mnt/data/venv/bin/python -c 'import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); r=c.execute(\"pragma integrity_check\").fetchone()[0]; n=c.execute(\"select count(*) from sqlite_master\").fetchone()[0]; print(\"INTEGRITY\", r, n)' /mnt/data/backup_$b.sqlite") \
        || { warn "CACHE VM-$v $b: build/verify failed on the VM"; continue; }
      read -r z hraw hz size <<< "$(echo "$out" | head -1)"; integ=$(echo "$out" | grep INTEGRITY)
      cp_ok=0; for try in 1 2 3 4 5 6 7 8; do rsync -a --partial --timeout=120 agentqo-$v:/mnt/data/backup_$b.sqlite.$z $C/vm-$v/ && { cp_ok=1; break; }; sleep 15; done
      [ $cp_ok = 1 ] || { warn "CACHE VM-$v $b: copy failed after 8 tries"; continue; }
      [ "$(shasum -a 256 $C/vm-$v/backup_$b.sqlite.$z | cut -c1-64)" = "$hz" ] || { warn "CACHE VM-$v $b: sha256 mismatch on the Mac"; continue; }
      echo "$hz  vm-$v/backup_$b.sqlite.$z  (uncompressed sha256 $hraw, $size bytes; on the VM: $integ)" >> $C/SHA256SUMS.txt
      ssh agentqo-$v "rm -f /mnt/data/backup_$b.sqlite"
      log "CACHE VM-$v $b: $(du -h $C/vm-$v/backup_$b.sqlite.$z | cut -f1) compressed, $integ, sha256 verified on VM and Mac"
      floor cache
    done
  done
fi

# 6) CHECKSUMS.txt (sha256 of the UPLOAD zip and every CACHE file), verified with shasum -c on the Mac
(cd $OUT && shasum -a 256 results_v2_UPLOAD.zip $(cd $OUT && find results_v2_CACHE -type f ! -name SHA256SUMS.txt | sort) > CHECKSUMS.txt && shasum -a 256 -c CHECKSUMS.txt > /dev/null) \
  && log "CHECKSUMS.txt written and verified ($(wc -l < $OUT/CHECKSUMS.txt) files)" || warn "CHECKSUMS verification failed"

# 7) Push all CSV/JSON/MD to v2-lease1 (gates already pushed every phase; this adds FINAL/, the final ground truth, logs)
if [ $DRY != 1 ]; then
  git -C $WT fetch -q origin v2-lease1 && git -C $WT merge -q --ff-only origin/v2-lease1
  mkdir -p $WT/results/v2/FINAL; cp $S/results/v2/FINAL/data_check.md $WT/results/v2/FINAL/
  cp $S/results/v2/P6/search_ground_truth.md $WT/results/v2/P6/; cp $OUT/CHECKSUMS.txt $WT/results/v2/FINAL/
  cp $ST $WT/results/v2/STATUS.md; cp $EV $WT/results/v2/FINAL/events.log
  git -C $WT add -f results/v2/FINAL results/v2/P6/search_ground_truth.md results/v2/STATUS.md CHANGELOG_v2.md
  git -C $WT commit -q -m "Lease 2: FINAL (data check, search ground truth, checksums)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SskgYqCUR4kz4DJuBUgcVJ" && git -C $WT push -q origin v2-lease1 2>&1 | tail -2
  log "pushed to v2-lease1 ($(git -C $WT log origin/v2-lease1 -1 --format=%h))"
  cp $Z $R/; cp -r $C $R/ 2>/dev/null; cp $OUT/CHECKSUMS.txt $R/
fi

# 8) UPLOAD_TO_CLAUDE.md
U=$OUT/UPLOAD_TO_CLAUDE.md; [ $DRY != 1 ] && U=$R/UPLOAD_TO_CLAUDE.md
sz() { [ -f "$1" ] && echo "$(du -h "$1" | cut -f1) ($(stat -f%z "$1") bytes)" || echo "MISSING"; }
UZ=$Z; [ $DRY != 1 ] && UZ=$R/results_v2_UPLOAD.zip
{
  echo "# Upload to Claude (AgentQO v2 Lease 2 FINAL, $(ts))"; echo
  echo "Upload these, in this order:"; echo
  echo "1. $UZ — $(sz $UZ)"
  echo "2. $S/results/v2/P6/hypotheses/hypotheses.md — $(sz $S/results/v2/P6/hypotheses/hypotheses.md)"
  echo "3. $S/results/v2/FINAL/data_check.md — $(sz $S/results/v2/FINAL/data_check.md)"
  echo "4. $ST — $(sz $ST)"
  for f in $S/results/v2/FAILURES_vmA.md $S/results/v2/FAILURES_vmB.md; do [ -f $f ] && echo "5. $f — $(sz $f)"; done
  echo; echo "Stays on the Mac (not for upload): $C (per-VM compressed SQLite caches and the excluded JSON; sha256 in $OUT/CHECKSUMS.txt)."
  echo; echo "## What ran"; echo
  echo "Registered: P0-P4b quality phases on both VMs (11 settings with exhaustive plans, incl. A16 math_tiers 729 plans and A17"
  echo "complex_q15_7 1,024 plans), P5 placement and calibration on both VMs, the D-L2-h4grid refit, E1 (full precision vs AWQ),"
  echo "and P6 (costs, Pareto fronts, rules, routing, adaptive check, hypotheses, search ground truth). Exploratory (L2-X, own"
  echo "folders, never change a registered verdict): X1 latency ground truth for every plan, X1b load sweep, X1c Phi grid and A16"
  echo "three-model runs, X2 held-out problems, X3 cross-family model choice (729 plans), X4 run-to-run replicate (redefined: greedy"
  echo "decoding makes a seed replicate meaningless), X5 MATH-500, X6 Qwen 7B/32B (separate placement only: the pair does not fit"
  echo "usefully on one 94 GB H100), X7 MBPP+ code chain with a sandbox, X8 held-out problems for complex_q15_7. Data check:"
  echo "${nmiss:-?} missing item(s). Deviations, reruns and every cut are logged with reasons in STATUS.md and CHANGELOG_v2.md."
  [ "${DROPPED_TRACES:-0}" = 1 ] && echo "h3_traces.json files were left out of the UPLOAD zip to stay under 300 MB (they are in the CACHE excluded_json.zip)."
} > $U
[ $DRY = 1 ] && log "DRY RUN DONE: $OUT" || { echo "$(ts) GATE FINAL DONE" | tee -a $ST >> $EV; }
echo "GATE FINAL DONE"; cat $U
