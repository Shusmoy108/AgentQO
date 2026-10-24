#!/bin/bash
# usage: grid.sh <separate|shared> <repeat_id> <max_tokens list, e.g. "32 128 512">
PL=$1; REP=$2; MTS=$3
cd ~/AgentQO && source ~/env.sh
export PYTHONUNBUFFERED=1
set -o pipefail
NAME=H4_P1A_${PL^^}_R${REP}
LOG=logs/h4_p1a_${PL}_r${REP}.txt
if [ "$PL" = separate ]; then SU=http://localhost:8001; LU=http://$VMB:8002; else SU=http://localhost:8001; LU=http://localhost:8003; fi
{ echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) $NAME  max_tokens: $MTS"; nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader; } | tee $LOG
t0=$(date +%s)
for MT in $MTS; do for SH in 0.25 0.5 0.75; do
  python3 -u scripts/placement_test.py --config $PL --small-url $SU --large-url $LU --small-share $SH --max-tokens $MT \
    --concurrency 1,4,16 --requests 64 --repeat-id $REP --seed $REP --out data/h4/grid 2>&1 | tee -a $LOG || { echo "${NAME}_EXIT=1" | tee -a $LOG; exit 1; }
  sleep 10
  python3 -u scripts/placement_test.py --config $PL --small-url $SU --large-url $LU --small-share $SH --max-tokens $MT \
    --concurrency 64 --requests 128 --repeat-id $REP --seed $REP --out data/h4/grid 2>&1 | tee -a $LOG || { echo "${NAME}_EXIT=1" | tee -a $LOG; exit 1; }
  sleep 10
done; done
echo "wall_s=$(( $(date +%s) - t0 ))" | tee -a $LOG
echo "${NAME}_EXIT=0" | tee -a $LOG
