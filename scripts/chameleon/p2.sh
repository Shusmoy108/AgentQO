#!/bin/bash
cd ~/AgentQO && source ~/env.sh; set -o pipefail
LOG=logs/h4_p2_mps.txt; A="--small-share 0.5 --max-tokens 128 --concurrency 1,4,16,32 --requests 64"
gpu_check() { local n=$(nvidia-smi --query-compute-apps=process_name --format=csv,noheader | grep -c "VLLM"); echo "$(date -u +%H:%M:%S) GPU check: $n process(es), expected $1"; nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader; nvidia-smi | grep -E "MiB \|" | grep -E " C | M\+C " ; [ "$n" = "$1" ]; }
fail() { echo "$1"; echo "H4_P2_EXIT=1"; exit 1; }
{
{ echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) (UTC) ==="; cat /tmp/pre_p2.txt; echo; } >> logs/h4_preregistration.txt
t0=$(date +%s)
bash /tmp/serve.sh stop8003 && gpu_check 1 || fail "setup failed"
for r in 0 1 2; do bash /tmp/pt.sh separate http://localhost:8001 http://$VMB:8002 $r data/h4/p2 /dev/null $A || fail "separate r$r failed"; sleep 10; done
bash /tmp/serve.sh start8003 && gpu_check 2 || fail "start8003 failed"
for r in 0 1 2; do bash /tmp/pt.sh shared_nomps http://localhost:8001 http://localhost:8003 $r data/h4/p2 /dev/null $A || fail "nomps r$r failed"; sleep 10; done
echo "--- switching to MPS"
bash /tmp/serve.sh stop8003 && bash /tmp/serve.sh stop8001 && gpu_check 0 || fail "stopping servers failed"
bash /tmp/serve.sh mps_on || fail "MPS daemon failed to start"
MPS_OK=0
if bash /tmp/serve.sh start8001 mps && bash /tmp/serve.sh start8003 mps; then MPS_OK=1; else
  echo "vLLM failed under MPS with 0.25/0.55; errors:"; tail -n 30 ~/vllm_8001_h4.log ~/vllm_8003_h4.log
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) P2: vLLM failed to start under MPS at 0.25/0.55. Log tails:" >> logs/h4_changes.txt
  tail -n 30 ~/vllm_8001_h4.log ~/vllm_8003_h4.log >> logs/h4_changes.txt
  bash /tmp/serve.sh stop8003; bash /tmp/serve.sh stop8001
  echo "retrying once with 0.2/0.5" | tee -a logs/h4_changes.txt
  sed -i 's/1.5B-Instruct 0.25 5/1.5B-Instruct 0.2 5/; s/7B-Instruct 0.55 6/7B-Instruct 0.5 6/' /tmp/serve.sh
  if bash /tmp/serve.sh start8001 mps && bash /tmp/serve.sh start8003 mps; then MPS_OK=1; else
    tail -n 30 ~/vllm_8001_h4.log ~/vllm_8003_h4.log >> logs/h4_changes.txt; echo "P2 MPS runs SKIPPED: vLLM did not start under MPS" | tee -a logs/h4_changes.txt; fi
fi
if [ $MPS_OK = 1 ]; then
  gpu_check 2 || fail "MPS gpu check failed"
  [ "$(nvidia-smi | grep -c "M+C")" -ge 2 ] && echo "MPS confirmed: processes shown as M+C" || fail "processes not shown as M+C"
  ls /tmp/mps_log; tail -5 /tmp/mps_log/control.log
  for r in 0 1 2; do bash /tmp/pt.sh shared_mps http://localhost:8001 http://localhost:8003 $r data/h4/p2 /dev/null $A || fail "mps r$r failed"; sleep 10; done
fi
echo "--- MPS off"
bash /tmp/serve.sh stop8003; bash /tmp/serve.sh stop8001; gpu_check 0 || fail "servers did not stop"
bash /tmp/serve.sh mps_off || fail "MPS did not stop"
sed -i 's/1.5B-Instruct 0.2 5/1.5B-Instruct 0.25 5/; s/7B-Instruct 0.5 6/7B-Instruct 0.55 6/' /tmp/serve.sh
bash /tmp/serve.sh start8001 && gpu_check 1 && [ "$(nvidia-smi | grep -c "M+C")" = 0 ] || fail "restart without MPS failed"
echo "wall_s=$(( $(date +%s) - t0 )) MPS_OK=$MPS_OK"
echo "H4_P2_EXIT=0"
} 2>&1 | tee $LOG
