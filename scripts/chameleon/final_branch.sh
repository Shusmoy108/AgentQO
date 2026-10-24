#!/bin/bash
# Final step B.4: session1-results branch in a separate worktree (main checkout never switches branches).
cd ~/AgentQO && set -o pipefail
fail() { echo "$1"; echo "FINAL_BRANCH_EXIT=1"; exit 1; }
W=/tmp/s1r; rm -rf $W; git worktree prune
git worktree add -q -b session1-results $W followup-e || fail "worktree failed"
{ find logs -type f; find data/vllm data/placement data/h4 -type f \( -name '*.csv' -o -name '*.json' -o -name '*.png' \) -size -20M; echo MANIFEST.txt; } | sort -u > /tmp/s1r_files.txt
skipped=$(find data/vllm data/placement data/h4 -type f \( -name '*.csv' -o -name '*.json' -o -name '*.png' \) -size +20M -o -type f \( -name '*.csv' -o -name '*.json' -o -name '*.png' \) -size 20M)
echo "files to commit: $(wc -l < /tmp/s1r_files.txt); excluded (>= 20 MB): ${skipped:-none}"
rsync -a --files-from=/tmp/s1r_files.txt ./ $W/ || fail "copy failed"
cd $W && git add -f $(cat /tmp/s1r_files.txt) && git commit -q -m "session1 results: logs, small CSV/JSON/PNG results (C1-C14, H4, E1, E2) and MANIFEST.txt" -m "Files under 20 MB from data/vllm, data/placement, data/h4, plus all of logs/. The generation cache, zips and larger files are only in session1_ALL_results.zip (see MANIFEST.txt)." -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>" || fail "commit failed"
git log --oneline -1
cd ~/AgentQO
git ls-tree -r --name-only session1-results | sort > /tmp/branch_files.txt
{ grep -v '^#' MANIFEST.txt | awk '{print $3}'; echo MANIFEST.txt; } | sort > /tmp/manifest_files.txt
echo "branch files: $(wc -l < /tmp/branch_files.txt); MANIFEST files (+ MANIFEST.txt itself): $(wc -l < /tmp/manifest_files.txt)"
comm -23 /tmp/branch_files.txt /tmp/manifest_files.txt > /tmp/missing.txt
echo "branch files missing from the zip: $(wc -l < /tmp/missing.txt)"; cat /tmp/missing.txt
echo "FINAL_BRANCH_EXIT=0"
