#!/bin/bash
cd ~/AgentQO && source ~/env.sh; set -o pipefail
LOG=logs/h4_p3_prefix.txt; A="--small-share 0.5 --max-tokens 16 --concurrency 1,4,16,32 --requests 64 --prefix-metrics"
gpu_check() { local n=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l); echo "$(date -u +%H:%M:%S) GPU check: $n process(es), expected $1"; nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader; [ "$n" = "$1" ]; }
fail() { echo "$1"; echo "H4_P3_EXIT=1"; exit 1; }
{
{ echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) (UTC) ==="; cat /tmp/pre_p3.txt; echo; } >> logs/h4_preregistration.txt
t0=$(date +%s)
grep -o "enable_prefix_caching=[A-Za-z]*" ~/vllm_8001_h4.log | head -1 | sed 's/^/8001 (restarted after P2): /'
bash /tmp/serve.sh stop8003 >/dev/null 2>&1; gpu_check 1 || fail "gpu check failed"
for r in 0 1 2; do for P in 0 2000; do bash /tmp/pt.sh separate http://localhost:8001 http://$VMB:8002 $r data/h4/p3 /dev/null $A --prefix-tokens $P || fail "separate p$P r$r failed"; sleep 10; done; done
bash /tmp/serve.sh start8003 && gpu_check 2 || fail "start8003 failed"
grep -o "enable_prefix_caching=[A-Za-z]*" ~/vllm_8003_h4.log | head -1 | sed 's/^/8003: /'
for r in 0 1 2; do for P in 0 2000; do bash /tmp/pt.sh shared http://localhost:8001 http://localhost:8003 $r data/h4/p3 /dev/null $A --prefix-tokens $P || fail "shared p$P r$r failed"; sleep 10; done; done
echo "wall_s=$(( $(date +%s) - t0 ))"
echo "H4_P3_EXIT=0"
} 2>&1 | tee $LOG
