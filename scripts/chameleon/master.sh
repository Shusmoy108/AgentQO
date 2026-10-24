#!/bin/bash
# Runs after P2: P3, P4 (predictions first, then measurements), reports, bundle. Stops on failure.
cd ~/AgentQO && source ~/env.sh; set -o pipefail; export PYTHONUNBUFFERED=1
gpu_check() { local n=$(nvidia-smi --query-compute-apps=process_name --format=csv,noheader | grep -c "VLLM"); echo "$(date -u +%H:%M:%S) GPU check VM-A: $n process(es), expected $1"; nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader; [ "$n" = "$1" ]; }
step() { local NAME=$1 LOG=$2; shift 2; date -u | tee $LOG; "$@" 2>&1 | tee -a $LOG; local rc=$?; echo "${NAME}_EXIT=$rc" | tee -a $LOG; date -u | tee -a $LOG; return $rc; }
until grep -q "H4_P2_EXIT=" logs/h4_p2_mps.txt 2>/dev/null; do sleep 20; done
grep -q "H4_P2_EXIT=0" logs/h4_p2_mps.txt || { echo "P2 failed; stopping"; exit 1; }
MPS_OK=$(grep -o "MPS_OK=[01]" logs/h4_p2_mps.txt | tail -1 | cut -d= -f2)
step H4_P2_REPORT logs/h4_p2_report.txt python3 -u scripts/h4_fit.py p2-report || exit 1
bash /tmp/p3.sh; grep -q "H4_P3_EXIT=0" logs/h4_p3_prefix.txt || { echo "P3 failed; stopping"; exit 1; }
step H4_P3_REPORT logs/h4_p3_report.txt python3 -u scripts/h4_fit.py p3-report || exit 1
# ---- P4: pre-register goal + predictions text, then model predictions, then append them, then measure
{ echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) (UTC) ==="; cat /tmp/pre_p4.txt; echo; } >> logs/h4_preregistration.txt
if [ "$MPS_OK" = 1 ]; then step H4_P4_MPS_FIT logs/h4_p4_mps_fit.txt python3 -u scripts/h4_fit.py fit-mps || exit 1; MF=data/h4/fit/mps_fit.json; else MF=""; fi
step H4_P4_PREDICT logs/h4_p4_predict.txt python3 -u scripts/h4_fit.py predict-workflow --mps-fit "$MF" || exit 1
{ echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) (UTC) P4 model predictions, written before any P4 measurement ==="; cat data/h4/p4_predictions.json; echo; } >> logs/h4_preregistration.txt
run_p4() {  # placement endpoints_json
  for K in 4 16 32; do for R in 0 1; do
    VLLM_ENDPOINTS="$2" AGENTQO_VERIFIER=passthrough python3 -u scripts/h4_workflow_load.py --placement $1 --k $K --repeat-id $R --out data/h4/p4 || return 1
    sleep 10
  done; done
}
LOCAL_L='{"small":"http://localhost:8001","large":"http://localhost:8003"}'
SEP_L="{\"small\":\"http://localhost:8001\",\"large\":\"http://$VMB:8002\"}"
gpu_check 2 || { echo "expected 8001+8003 for C"; exit 1; }
step H4_P4_C logs/h4_p4_C.txt run_p4 C "$LOCAL_L" || exit 1
bash /tmp/serve.sh stop8003; gpu_check 1 || exit 1
step H4_P4_S logs/h4_p4_S.txt run_p4 S "$SEP_L" || exit 1
if [ "$MPS_OK" = 1 ]; then
  bash /tmp/serve.sh stop8001; gpu_check 0 || exit 1
  bash /tmp/serve.sh mps_on && bash /tmp/serve.sh start8001 mps && bash /tmp/serve.sh start8003 mps && gpu_check 2 && [ "$(nvidia-smi | grep -c "M+C")" -ge 2 ] || { echo "CM setup failed"; exit 1; }
  step H4_P4_CM logs/h4_p4_CM.txt run_p4 CM "$LOCAL_L"; RC=$?
  bash /tmp/serve.sh stop8003; bash /tmp/serve.sh stop8001; bash /tmp/serve.sh mps_off; bash /tmp/serve.sh start8001
  [ $RC = 0 ] || exit 1
fi
step H4_P4_REPORT logs/h4_p4_report.txt python3 -u scripts/h4_fit.py p4-report || exit 1
# ---- bundle
git diff main...h4-complete > h4.patch
rm -f h4_complete.zip
zip -qr h4_complete.zip data/h4 logs/h4_*.txt h4.patch && unzip -tq h4_complete.zip && sha256sum h4_complete.zip
echo "H4_MASTER_EXIT=0"
