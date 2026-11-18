#!/usr/bin/env bash
# FINAL-early archive builder (PI NEXT 2026-11-18): run after the pulls into $A/vm-{A,B} and the VM cache compression.
# Builds in $A only (a new folder; nothing overwritten, nothing deleted anywhere). usage: final_early.sh ARCHIVE_DIR
set -uo pipefail
A=${1:?archive dir}; R=~/AgentQO_results/v2; WT=~/AgentQO_lease
log() { echo "$(date -u +%FT%TZ) FINAL-early $*" | tee -a $A/BUILD_LOG.txt; }
# 1) compressed caches (built and verified on the VMs from the idle live files): copy, verify sha256 on the Mac
for v in A B; do
  mkdir -p $A/cache/vm-$v
  for i in 1 2 3 4 5 6 7 8; do rsync -a --partial --timeout=120 agentqo-$v:/mnt/data/final_early/ $A/cache/vm-$v/ && break; sleep 20; done
  grep -q DONE $A/cache/vm-$v/CACHE_SHA256.txt || log "WARN VM-$v cache list incomplete"
  grep -E 'verify=(MISMATCH)|WARN' $A/cache/vm-$v/CACHE_SHA256.txt && log "WARN VM-$v cache verification problem"
  while read -r h f rest; do
    [ "$h" = DONE ] && continue
    [ "$(shasum -a 256 $A/cache/vm-$v/$f | cut -c1-64)" = "$h" ] && log "cache VM-$v $f sha256 OK on the Mac ($(du -h $A/cache/vm-$v/$f | cut -f1); $rest)" || log "WARN cache VM-$v $f sha256 MISMATCH on the Mac"
  done < <(grep -v '^WARN' $A/cache/vm-$v/CACHE_SHA256.txt)
done
# 2) Mac-side material: derived analyses, STATUS, events, CHANGELOG, prereg, tools
mkdir -p $A/mac
rsync -a $R/derived $R/tools $A/mac/; cp $R/STATUS.md $R/events.log $A/mac/
rsync -a $WT/prereg $WT/tools_lease $A/mac/; cp $WT/CHANGELOG_v2.md $WT/PLAN_v2_times.md $A/mac/ 2>/dev/null
# 3) data check on the archive copy (same checks as final_check.py)
FINALCHECK_ROOT=$A python3 $R/tools/final_check.py $A/data_check.md > /dev/null
miss=$(grep -o 'Summary: [0-9]* MISSING' $A/data_check.md | grep -o '[0-9]*'); log "data check: ${miss:-?} MISSING"
# 4) zips: UPLOAD = results + logs + scripts + Mac material (no caches, no bundles); CACHE = the per-VM .zst caches + their sha lists
(cd $A && zip -q -r -9 results_v2_UPLOAD.zip vm-A vm-B mac data_check.md -x '*.bundle' -x '*/.*') || log "WARN UPLOAD zip failed"
(cd $A && zip -q -r -0 results_v2_CACHE.zip cache) || log "WARN CACHE zip failed"
for z in results_v2_UPLOAD.zip results_v2_CACHE.zip; do
  unzip -tq $A/$z > /dev/null && log "$z $(du -h $A/$z | cut -f1) ($(stat -f%z $A/$z) bytes): unzip -t OK" || log "WARN $z unzip -t FAILED"
done
# 5) SHA256SUMS.txt for every file in the archive, verified with shasum -c; MANIFEST (file list + sizes)
(cd $A && find . -type f ! -name SHA256SUMS.txt ! -name MANIFEST.txt ! -name BUILD_LOG.txt | sed 's|^\./||' | sort > /private/tmp/claude-501/-Users-shusmoychowdhury-AgentQO/52abffdc-7b07-4777-b603-7894c255f4d2/scratchpad/fe_files.txt \
  && tr '\n' '\0' < /private/tmp/claude-501/-Users-shusmoychowdhury-AgentQO/52abffdc-7b07-4777-b603-7894c255f4d2/scratchpad/fe_files.txt | xargs -0 shasum -a 256 > SHA256SUMS.txt && shasum -a 256 -c SHA256SUMS.txt > /dev/null) \
  && log "SHA256SUMS.txt: $(wc -l < $A/SHA256SUMS.txt | tr -d ' ') files, shasum -c OK" || log "WARN SHA256SUMS verification failed"
(cd $A && { echo "# FINAL-early archive manifest ($(basename $A)); path<TAB>bytes"; while IFS= read -r f; do printf '%s\t%s\n' "$f" "$(stat -f%z "$f")"; done < /private/tmp/claude-501/-Users-shusmoychowdhury-AgentQO/52abffdc-7b07-4777-b603-7894c255f4d2/scratchpad/fe_files.txt; } > MANIFEST.txt)
log "zip sha256: $(cd $A && shasum -a 256 results_v2_UPLOAD.zip results_v2_CACHE.zip | tr '\n' ' ')"
log "BUILD DONE"
