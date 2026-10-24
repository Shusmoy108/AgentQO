#!/bin/bash
# one placement_test run: pt.sh <config> <small_url> <large_url> <repeat> <out> <log> [extra args...]
CFG=$1; SU=$2; LU=$3; REP=$4; OUT=$5; LOG=$6; shift 6
cd ~/AgentQO && source ~/env.sh; export PYTHONUNBUFFERED=1; set -o pipefail
python3 -u scripts/placement_test.py --config $CFG --small-url $SU --large-url $LU --repeat-id $REP --seed $REP --out $OUT "$@" 2>&1 | tee -a $LOG
