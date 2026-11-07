#!/usr/bin/env bash
# M10: summarize, zip, and commit one phase's text results to branch v2-lease1.
#   scripts/v2/package_phase.sh <phase>
# The checked-out branch is never touched: the commit happens in a temporary worktree.
# V2_PUSH=0 stops before git. V2_RESULTS, V2_ZIP_DIR and V2_CACHE move the inputs and outputs.
set -euo pipefail

phase=${1:?usage: package_phase.sh <phase>}
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cd "$ROOT"
RESULTS=${V2_RESULTS:-results/v2}
ZIP_DIR=${V2_ZIP_DIR:-.}
BRANCH=v2-lease1
PY=${PYTHON:-python3}
dir="$RESULTS/$phase"
[ -d "$dir" ] || { echo "no results at $dir" >&2; exit 1; }

"$PY" scripts/v2/summarize_phase.py report "$dir"
extra=()
if [ "$phase" = final ] && [ -n "${V2_CACHE:-}" ]; then
  extra=(--extra "$V2_CACHE")  # the SQLite cache ships only in the final zip
fi
"$PY" scripts/v2/summarize_phase.py zip "$dir" --name "$phase" --where "$ZIP_DIR" ${extra[@]+"${extra[@]}"}

# final repeats the phases already committed, so it only makes the zip.
if [ "${V2_PUSH:-1}" = 0 ] || [ "$phase" = final ]; then
  echo "not committing $phase to $BRANCH (V2_PUSH=${V2_PUSH:-1})"
  exit 0
fi

wt=$(mktemp -d)
trap 'git worktree remove --force "$wt" >/dev/null 2>&1 || true; rm -rf "$wt"' EXIT
git fetch origin "$BRANCH" 2>/dev/null || true
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git worktree add "$wt" "$BRANCH"
  if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
    git -C "$wt" merge --ff-only "origin/$BRANCH"
  fi
elif git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
  git worktree add -b "$BRANCH" "$wt" "origin/$BRANCH"
else
  git worktree add -b "$BRANCH" "$wt" HEAD
fi
"$PY" scripts/v2/summarize_phase.py copy "$dir" "$wt/results/v2/$phase"
git -C "$wt" add -f "results/v2/$phase"
if git -C "$wt" diff --cached --quiet; then
  echo "nothing new to commit for $phase"
else
  git -C "$wt" commit -q -m "Results for phase $phase"
fi
git -C "$wt" push origin "$BRANCH"
echo "pushed $phase results to $BRANCH"
