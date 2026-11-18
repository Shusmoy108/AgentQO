# Lease 2 queue helpers (sourced). Not repo code: lives in /mnt/data, outside the tree.
set -uo pipefail
source /mnt/data/env_lease.sh
cd /mnt/data/AgentQO
export V2_WORKERS=${V2_WORKERS:-32} V2_PUSH=0 PYTHON=/mnt/data/venv/bin/python
export V2_LEASE_END=${V2_LEASE_END:-2026-11-19T16:00Z} V2_RESERVE_HOURS=${V2_RESERVE_HOURS:-2}   # PI schedule 2026-11-18: FINAL 16:00Z, new GPU work until 14:00Z
[ -f /mnt/data/hours.env ] && source /mnt/data/hours.env   # V2_HOURS_<setting> overrides from measured rates
VM=${VM:?set VM=A or B}
L=logs/v2; G=results/v2/GATES; mkdir -p $L $G results/v2
SRV=()   # current server spec list: model|port|mem|maxlen|extra
qlog() { echo "[$(date -u +%FT%TZ)] VM-$VM $*" | tee -a $L/queue_$VM.log; }

srv_stop() { local s
  for s in $(tmux ls -F '#S' 2>/dev/null | grep '^srv'); do tmux kill-session -t "$s"; done
  for i in $(seq 1 60); do
    pgrep -f 'vllm serve' >/dev/null || break; sleep 5
  done
  pkill -9 -f 'vllm serve' 2>/dev/null; sleep 5
  SRV=()
}
srv_up() { curl -sf -m 10 "localhost:$1/v1/models" >/dev/null; }
srv_launch() {  # model port mem maxlen [extra]
  local m=$1 p=$2 mem=$3 len=$4 extra=${5:-}
  tmux kill-session -t srv$p 2>/dev/null
  tmux new -d -s srv$p "source /mnt/data/env_lease.sh; ${MPS_ENV:-} vllm serve $m --host 0.0.0.0 --port $p --gpu-memory-utilization $mem --max-model-len $len $extra >> $L/server_$p.log 2>&1"
  for i in $(seq 1 240); do srv_up $p && { qlog "server $m :$p up (mem $mem, len $len)"; return 0; }; sleep 5; done
  qlog "server $m :$p FAILED to start"; tail -20 $L/server_$p.log; return 1
}
srv_start() {  # specs "model|port|mem|maxlen|extra" ..., largest first
  srv_stop
  local s ok=0
  for s in "$@"; do IFS='|' read -r m p mem len extra <<<"$s"; srv_launch "$m" "$p" "$mem" "$len" "$extra" || ok=1; done
  SRV=("$@"); endpoints; return $ok
}
srv_ensure() {  # restart dead servers of the current spec
  local s
  for s in "${SRV[@]}"; do IFS='|' read -r m p mem len extra <<<"$s"; srv_up $p || { qlog "server :$p down, restarting"; srv_launch "$m" "$p" "$mem" "$len" "$extra"; }; done
}
endpoints() {
  local s j=""
  for s in "${SRV[@]}"; do IFS='|' read -r m p _ <<<"$s"; j="$j${j:+,}\"$m\":\"http://localhost:$p\""; done
  export VLLM_ENDPOINTS="{$j}"
}
fail_note() {  # phase reason logfile
  { echo; echo "## $1 on VM-$VM, $(date -u +%FT%TZ)"; echo "$2"; echo '```'; tail -50 "$3"; echo '```'; } >> results/v2/FAILURES.md
}
past() { /mnt/data/venv/bin/python -c 'import sys,datetime as d; sys.exit(not d.datetime.now(d.timezone.utc) >= d.datetime.fromisoformat(sys.argv[1].replace("Z","+00:00")))' "$1"; }
step() {  # gate_name phase [VAR=val ...]; retries 2/5/15 min; skips if gated
  local gate=$1 ph=$2; shift 2
  [ -f $G/$gate.$VM ] && { qlog "$gate already gated, skip"; return 0; }
  [ -f /mnt/data/PAUSE ] && { qlog "PAUSE set, stopping before $gate"; exit 0; }
  past 2026-11-19T14:00Z && { qlog "GPU cutoff (new work until 14:00Z) passed, not starting $gate"; return 1; }
  local w
  for w in 0 120 300 900; do
    [ $w -gt 0 ] && { qlog "$gate retry after ${w}s"; sleep $w; srv_ensure; }
    qlog "start $gate ($ph $*)"
    if env "$@" scripts/v2/run_phase.sh "$ph"; then qlog "done $gate"; return 0; fi
    qlog "$gate failed (exit $?)"
  done
  fail_note "$gate ($ph $*)" "failed 4 times (retries 2/5/15 min)" "$L/$ph.log"
  return 1
}
gate() { echo "$(date -u +%FT%TZ) ${2:-}" > $G/$1.$VM; qlog "GATE $1"; }
