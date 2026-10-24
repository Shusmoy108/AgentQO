#!/bin/bash
# Deliverable 1 (session1_final.zip) and Final step A (session1_ALL_results.zip + MANIFEST.txt). Run on VM-A.
cd ~/AgentQO && set -o pipefail
fail() { echo "$1"; echo "FINAL_A_EXIT=1"; exit 1; }
date -u
[ "$(git branch --show-current)" = followup-e ] || fail "not on followup-e"
git status --porcelain --untracked-files=no | grep -q . && fail "uncommitted tracked changes on followup-e"
# ---- deliverable 1
sqlite3 data/cache/vllm.sqlite "PRAGMA integrity_check;" | tee logs/cache_integrity_final.txt
grep -qx ok logs/cache_integrity_final.txt || fail "cache integrity check failed"
git diff followup-c12...followup-e > followup_e.patch
rm -f session1_final.zip
zip -qr session1_final.zip logs data/vllm/e1_* data/vllm/e2_* data/cache/vllm.sqlite followup_e.patch || fail "zip final failed"
unzip -tq session1_final.zip || fail "session1_final.zip test failed"
echo "session1_final.zip $(du -h session1_final.zip | cut -f1) $(sha256sum session1_final.zip | cut -d' ' -f1)"
# ---- Final step A: stage VM-A home logs, then everything into one archive
mkdir -p vmA_home && cp -p ~/vllm_*.log ~/install_54.log ~/env.sh vmA_home/ 2>/dev/null
{ git ls-files; find logs data vmB vmA_home -type f; ls *.patch *.zip | grep -v '^session1_ALL_results.zip$'; } | sort -u > /tmp/all_files.txt
wc -l < /tmp/all_files.txt
{ echo "# MANIFEST of session1_ALL_results.zip, built $(date -u +%Y-%m-%dT%H:%M:%SZ) on VM-A (agentqo-1)"
  echo "# size_bytes  sha256  path   (MANIFEST.txt itself is also in the zip)"
  while read -r f; do printf "%s  %s  %s\n" "$(stat -c %s "$f")" "$(sha256sum "$f" | cut -d' ' -f1)" "$f"; done < /tmp/all_files.txt; } > MANIFEST.txt
rm -f session1_ALL_results.zip
{ cat /tmp/all_files.txt; echo MANIFEST.txt; } | zip -q session1_ALL_results.zip -@ || fail "zip ALL failed"
unzip -tq session1_ALL_results.zip || fail "ALL zip test failed"
echo "files in ALL zip: $(unzip -Z1 session1_ALL_results.zip | wc -l); manifest entries: $(grep -vc '^#' MANIFEST.txt)"
echo "size: $(du -h session1_ALL_results.zip | cut -f1)  sha256: $(sha256sum session1_ALL_results.zip | cut -d' ' -f1)"
df -h ~ | tail -1
echo "FINAL_A_EXIT=0"
