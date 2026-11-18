#!/usr/bin/env bash
# Lease 2 stage 7 (Mac): L2-X11 on VM-A only (registered 6d853cdb), one block at a time: x11prep (no model calls) ->
# wait for the search session's tag search-prereg-s5d-* on origin -> x11a -> x11b. No block starts after 2026-11-19 14:00Z
# or while VM-A holds a TIMING_LOCK; final_guard stops anything still running at 15:30Z.
R=~/AgentQO_results/v2; EV=$R/events.log; ST=$R/STATUS.md
ts() { date -u +%FT%TZ; }
left() { python3 -c 'import datetime as d; e=d.datetime(2026,11,19,14,tzinfo=d.timezone.utc); print(round((e-d.datetime.now(d.timezone.utc)).total_seconds()/3600,1))'; }
run() {  # block
  python3 -c "import sys; sys.exit(not $(left) > 0)" || { echo "$(ts) X11 CUT: $1 not started, past 2026-11-19 14:00Z" | tee -a $ST >> $EV; return 1; }
  until ssh agentqo-A 'test ! -f /mnt/data/TIMING_LOCK'; do sleep 60; done
  ssh agentqo-A "tmux kill-session -t blk_$1 2>/dev/null; tmux new -d -s blk_$1 'VM=A bash /mnt/data/x11.sh $1'" && echo "$(ts) ORCH start $1 on VM-A" >> $EV
  local s
  while true; do
    sleep 60
    s=$(ssh -o ConnectTimeout=20 agentqo-A "if [ -f /mnt/data/blk/$1.done ]; then echo done; elif [ -f /mnt/data/blk/$1.fail ]; then echo fail; elif tmux has-session -t blk_$1 2>/dev/null; then echo run; else echo gone; fi" 2>/dev/null)
    case $s in done) echo "$(ts) ORCH done $1 on VM-A" >> $EV; return 0 ;; fail|gone) echo "$(ts) WARN ORCH block $1 on VM-A: $s" >> $EV; return 1 ;; esac
  done
}
[ -n "${SKIP_PREP:-}" ] || run x11prep || { echo "$(ts) X11 STOPPED at prep (see logs/v2/blk_x11prep.log)" | tee -a $ST >> $EV; exit 0; }
until git -C ~/AgentQO_lease ls-remote --tags origin 'search-prereg-s5d-*' 2>/dev/null | grep -q .; do sleep 120; done
echo "$(ts) X11 model calls may start: tag $(git -C ~/AgentQO_lease ls-remote --tags origin 'search-prereg-s5d-*' | grep -v '\^{}' | head -1 | sed 's|.*refs/tags/||') on origin" | tee -a $ST >> $EV
run x11a && echo "$(ts) TIME LEFT after X11a: $(left) h to 2026-11-19 14:00Z" | tee -a $ST >> $EV
run x11b && echo "$(ts) TIME LEFT after X11b: $(left) h to 2026-11-19 14:00Z" | tee -a $ST >> $EV
echo "$(ts) ORCH STAGE7 DONE (X11)" >> $EV
