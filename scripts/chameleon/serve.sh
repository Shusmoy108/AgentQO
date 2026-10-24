#!/bin/bash
# usage: serve.sh start8001|start8003|stop8001|stop8003|mps_on|mps_off|status   [mps]
cd ~/AgentQO && source ~/env.sh
MPSENV="CUDA_MPS_PIPE_DIRECTORY=/tmp/mps_pipe CUDA_MPS_LOG_DIRECTORY=/tmp/mps_log"
INFO=logs/h4_system_info.txt
wait_health() { for i in $(seq 1 90); do [ "$(curl -s -o /dev/null -w '%{http_code}' localhost:$1/health)" = 200 ] && { echo "port $1 healthy"; return 0; }; sleep 5; done; echo "port $1 NOT healthy after 450 s"; return 1; }
stop_port() { pkill -INT -f "vllm serve .*--port $1( |$)"; for i in $(seq 1 60); do pgrep -f "vllm serve .*--port $1( |$)" >/dev/null || { sleep 5; echo "port $1 stopped"; return 0; }; sleep 2; done; echo "port $1 still running"; return 1; }
start_port() {  # port model util window [mps]
  local P=$1 M=$2 U=$3 W=$4 E=""
  [ "$5" = mps ] && E="$MPSENV "
  local CMD="${E}vllm serve $M --host 127.0.0.1 --port $P --max-model-len 4096 --gpu-memory-utilization $U"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VM-A started: HF_HOME=$HF_HOME $CMD" >> $INFO
  tmux kill-window -t agentqo:$W 2>/dev/null; tmux new-window -d -t agentqo:$W
  tmux send-keys -t agentqo:$W "source ~/env.sh && env $CMD 2>&1 | tee ~/vllm_${P}_h4.log" Enter
  wait_health $P
}
case $1 in
  start8001) start_port 8001 Qwen/Qwen2.5-1.5B-Instruct 0.25 5 $2 ;;
  start8003) start_port 8003 Qwen/Qwen2.5-7B-Instruct 0.55 6 $2 ;;
  stop8001) stop_port 8001 ;;
  stop8003) stop_port 8003 ;;
  mps_on) mkdir -p /tmp/mps_pipe /tmp/mps_log; env $MPSENV nvidia-cuda-mps-control -d && sleep 2; pgrep -a nvidia-cuda-mps && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VM-A MPS daemon started ($MPSENV)" >> $INFO ;;
  mps_off) pgrep -f "^nvidia-cuda-mps-control" >/dev/null && { echo quit | env $MPSENV nvidia-cuda-mps-control; }
    for i in $(seq 1 30); do pgrep -f "^nvidia-cuda-mps-control" >/dev/null || pgrep -f "^nvidia-cuda-mps-server" >/dev/null || { echo "MPS off"; echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VM-A MPS daemon stopped" >> $INFO; exit 0; }; sleep 1; done
    echo "MPS STILL RUNNING"; pgrep -a nvidia-cuda-mps; exit 1 ;;
  status) nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader; nvidia-smi | grep -E "MiB \||C |M\+C"; pgrep -a nvidia-cuda-mps || echo "no MPS daemon"; for p in 8001 8003; do echo "$p $(curl -s -o /dev/null -w '%{http_code}' localhost:$p/health)"; done ;;
esac
