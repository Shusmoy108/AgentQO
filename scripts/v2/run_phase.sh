#!/usr/bin/env bash
# M10: one driver for the lease. Re-running a phase resumes it.
#   scripts/v2/run_phase.sh P1|P2|P3|P4|P5|P6|final
#
#   P1  Qwen 1.5B/7B labels: math (label 200 = Session 1 dev 100 + 100), HotpotQA (label 200), full and --disagree-only,
#       then HotpotQA isolated (A13, label 200)
#   P2  Qwen 1.5B/7B plans:  math all_subsets (eval_ext 400), HotpotQA all_subsets (eval 400), then HotpotQA isolated (A13)
#   P3  Qwen 3B/14B math:    labels (label 200) + all_subsets (eval_ext 400)
#   P4  Granite 2B/8B:       math labels (label 200, inside the Session 1 LABEL 500) + all_subsets, then (A14)
#       HotpotQA and HotpotQA isolated: labels 200 + all_subsets (eval 400), max_tokens 512
#   P5  Placement timing under V2_PLACEMENT (separate|shared|shared_mps), one run per placement;
#       with V2_P5_CAL=qwen_hotpot|qwen3_14_math|granite_math, a calibration set (A11) instead
#   P6  Offline analysis of every setting that has data (M1, M4, M5, M7, H5a)
#   final  Zip everything, with the SQLite cache
#
# Environment: V2_BACKEND (vllm|ollama|fake), V2_N (cap on problems, for test runs),
# V2_RESULTS, V2_LOGS, V2_CACHE, V2_WORKERS, V2_PUSH=0 (no git), V2_DRY=1 (print each
# command's --dry-run), V2_SETTINGS (limit P1/P2/P4 to e.g. "math"; default "math hotpot hotpot_iso"), V2_PLACEMENT,
# V2_P5_PLANS, V2_P5_CAL, V2_VMS ("gpu_a=local gpu_b=cc@host"), V2_DEVIATION (id of a lease-time
# deviation logged in prereg/v2_amendments.md, needed to run vllm phases off the v2-lease1-start tag).
set -euo pipefail

phase=${1:?usage: run_phase.sh P1|P2|P3|P4|P5|P6|final}
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cd "$ROOT"
BACKEND=${V2_BACKEND:-vllm}
RESULTS=${V2_RESULTS:-results/v2}
LOGS=${V2_LOGS:-logs/v2}
WORKERS=${V2_WORKERS:-32}
PY=${PYTHON:-python3}
DRY=()
[ "${V2_DRY:-0}" = 1 ] && DRY=(--dry-run)
case "$BACKEND" in
  ollama) CACHE=${V2_CACHE:-data/cache/v2_ollama.sqlite}; EXTRA=(--allow-missing-logprobs) ;;
  fake)   CACHE=${V2_CACHE:-data/cache/v2_fake.sqlite};   EXTRA=() ;;
  *)      CACHE=${V2_CACHE:-data/cache/vllm.sqlite};      EXTRA=() ;;
esac
export V2_BACKEND=$BACKEND V2_CACHE=$CACHE
export AGENTQO_VERIFIER=cautious  # the Session 1 math verifier that helps; HotpotQA is always cautious

mkdir -p "$LOGS" "$RESULTS/$phase"
exec > >(tee -a "$LOGS/$phase.log") 2>&1
echo "=== $phase start $(date -u +%FT%TZ) commit $(git rev-parse HEAD) backend $BACKEND"
# Provenance: the commit of the code actually run. A lease phase (vllm, not a dry run)
# refuses a dirty tree; test runs record the dirty flag instead.
if [ "${V2_DRY:-0}" != 1 ]; then
  refuse=()
  [ "$BACKEND" = vllm ] && refuse=(--refuse-dirty --lease)  # lease: the v2-lease1-start commit, or V2_DEVIATION
  "$PY" scripts/v2/summarize_phase.py provenance "$RESULTS/$phase" ${refuse[@]+"${refuse[@]}"}
fi

cap() { echo "${V2_N:-$1}"; }
OUT="$RESULTS/$phase"

use_models() {  # small large
  eval "$("$PY" scripts/v2/model_env.py "$1" "$2")"
  if [ "$BACKEND" = vllm ] && [ ${#DRY[@]} -eq 0 ]; then
    "$PY" scripts/v2/model_env.py --check-servers "$1" "$2"
  fi
}

labels() {  # setting workflow dataset split n max_tokens
  local common=(--backend "$BACKEND" --cache "$CACHE" --workflows "$2" --dataset "$3" --split "$4"
                --n-tasks "$5" --max-tokens "$6" --workers "$WORKERS" --stage h1 --k 5
                ${EXTRA[@]+"${EXTRA[@]}"} ${DRY[@]+"${DRY[@]}"})
  "$PY" scripts/run_real_pipeline.py "${common[@]}" --realistic --output-dir "$OUT/$1/labels"
  "$PY" scripts/run_real_pipeline.py "${common[@]}" --disagree-only --output-dir "$OUT/$1/labels_disagree"
}

plans() {  # setting workflow dataset split n max_tokens
  "$PY" scripts/run_real_h3.py --backend "$BACKEND" --cache "$CACHE" --workflow "$2" --dataset "$3" --split "$4" \
    --n-tasks "$5" --max-tokens "$6" --workers "$WORKERS" --plans all_subsets --output-dir "$OUT/$1/plans" \
    ${EXTRA[@]+"${EXTRA[@]}"} ${DRY[@]+"${DRY[@]}"}
}

wants() { case " ${V2_SETTINGS:-math hotpot hotpot_iso} " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }

analyze() {  # setting workflow labels_phase plans_phase
  local s=$1 wf=$2 lab="$RESULTS/$3/$1/labels" fast="$RESULTS/$3/$1/labels_disagree" pl="$RESULTS/$4/$1/plans"
  if [ ! -f "$pl/DONE" ] || [ ! -f "$lab/DONE" ]; then
    echo "skip $s: labels or plans not finished"
    return 0
  fi
  local d=${DRY[@]+"${DRY[@]}"}
  # A7/A11: every P5 run (main sweep and calibration sets) feeds the per-model
  # prefill/decode rates; rates are keyed by model, so other models' runs are ignored.
  local p5="" f
  for f in "$RESULTS"/P5/*/placement_summary.csv; do
    [ -f "$f" ] && p5="${p5:+$p5,}$(dirname "$f")"
  done
  "$PY" scripts/v2/cost_report.py --calls "$pl/h3_calls.csv" --output-dir "$OUT/$s/cost" ${p5:+--placement "$p5"} $d
  "$PY" scripts/v2/rules_report.py --workflow "$wf" --labels "$lab/labels_v2.csv" --plans "$pl/h3_plans.csv" \
    --labels-disagree "$fast/labels_v2.csv" --output-dir "$OUT/$s/rules" $d
  "$PY" scripts/v2/routing_offline.py --labels-per-problem "$lab/labels_v2_per_problem.csv" \
    --labels "$lab/labels_v2.csv" --workflow "$wf" --output-dir "$OUT/$s/routing" $d
  "$PY" scripts/v2/adaptive_check.py --per-problem "$pl/h3_per_problem.csv" --output-dir "$OUT/$s/adaptive" $d
  [ -n "$d" ] && return 0
  # Measured placement runs feed H3c, and their separate-placement calls set the latency base.
  local calls="$pl/h3_calls.csv" measured=""
  if [ "$s" = math_q15_7 ]; then
    for p in separate shared shared_mps; do
      local f="$RESULTS/P5/$p/placement_summary.csv"
      [ -f "$f" ] && measured="${measured:+$measured,}$f"
    done
    [ -f "$RESULTS/P5/separate/placement_calls.csv" ] && calls="$RESULTS/P5/separate/placement_calls.csv"
  fi
  local joint=(--workflow "$wf" --costs "$OUT/$s/cost/plan_costs.csv" --calls "$calls")
  [ -n "$measured" ] && joint+=(--measured "$measured")
  "$PY" scripts/v2/pareto.py "${joint[@]}" --plans "$pl/h3_plans.csv" --output-dir "$OUT/$s/pareto"
  "$PY" scripts/v2/pareto.py "${joint[@]}" --cost-metric api_usd --plans "$pl/h3_plans.csv" --output-dir "$OUT/$s/pareto_api"
  "$PY" scripts/v2/pareto.py "${joint[@]}" --plans "$OUT/$s/rules/plan_estimates.csv" --estimator pairwise_corrected \
    --true-plans "$pl/h3_plans.csv" --output-dir "$OUT/$s/pareto_estimated"
}

case "$phase" in
  P1)
    use_models qwen_small qwen_large
    wants math && labels math_q15_7 math gsm8k label "$(cap 200)" 256
    wants hotpot && labels hotpot_q15_7 hotpot hotpotqa label "$(cap 200)" 384
    wants hotpot_iso && labels hotpot_iso_q15_7 hotpot_iso hotpotqa label "$(cap 200)" 384
    ;;
  P2)
    use_models qwen_small qwen_large
    wants math && plans math_q15_7 math gsm8k eval_ext "$(cap 400)" 256
    wants hotpot && plans hotpot_q15_7 hotpot hotpotqa eval "$(cap 400)" 384
    wants hotpot_iso && plans hotpot_iso_q15_7 hotpot_iso hotpotqa eval "$(cap 400)" 384
    ;;
  P3)
    use_models qwen3b qwen14b
    labels math_q3_14 math gsm8k label "$(cap 200)" 256
    plans math_q3_14 math gsm8k eval_ext "$(cap 400)" 256
    ;;
  P4)
    use_models granite_small granite_large
    if wants math; then
      labels math_granite math gsm8k label "$(cap 200)" 512
      plans math_granite math gsm8k eval_ext "$(cap 400)" 512
    fi
    export AGENTQO_HOTPOT_SPAN=1  # A14: Granite-only short-span line in the HotpotQA aggregator/verifier
    for wf in hotpot hotpot_iso; do  # A14: Granite on both HotpotQA workflows, after math
      if wants $wf; then
        labels ${wf}_granite $wf hotpotqa label "$(cap 200)" 512
        plans ${wf}_granite $wf hotpotqa eval "$(cap 400)" 512
      fi
    done
    unset AGENTQO_HOTPOT_SPAN
    ;;
  P5)
    placement=${V2_PLACEMENT:?set V2_PLACEMENT to separate, shared or shared_mps to match the running servers}
    vms=()
    for vm in ${V2_VMS:-}; do vms+=(--vm "$vm"); done
    # V2_P5_CAL (A11) runs a calibration set instead of the main sweep: all_small and
    # all_large, K = 16, 64 problems, under the placement the servers are in (separate, shared).
    case "${V2_P5_CAL:-}" in
      "")           models=(qwen_small qwen_large); task=(--workflow math); tok=256; out="$OUT/$placement"
                    plans=${V2_P5_PLANS:-all_small,only_planner,only_aggregator,only_verifier,planner+verifier,aggregator+verifier,all_large} ;;
      qwen_hotpot)  models=(qwen_small qwen_large); task=(--workflow hotpot --dataset hotpotqa --split eval); tok=384 ;;
      qwen3_14_math) models=(qwen3b qwen14b); task=(--workflow math); tok=256 ;;
      granite_math) models=(granite_small granite_large); task=(--workflow math); tok=512 ;;
      *) echo "unknown V2_P5_CAL ${V2_P5_CAL}" >&2; exit 2 ;;
    esac
    if [ -n "${V2_P5_CAL:-}" ]; then
      plans=all_small,all_large
      out="$OUT/cal_${V2_P5_CAL}_$placement"
    fi
    use_models "${models[@]}"
    "$PY" scripts/v2/run_placement.py --backend "$BACKEND" --placement "$placement" "${task[@]}" \
      --plans "$plans" --max-tokens "$tok" --n-tasks "$(cap 64)" --k 16 --repeats 3 --output-dir "$out" \
      ${vms[@]+"${vms[@]}"} ${EXTRA[@]+"${EXTRA[@]}"} ${DRY[@]+"${DRY[@]}"}
    ;;
  P6)
    analyze math_q15_7 math P1 P2
    analyze hotpot_q15_7 hotpot P1 P2
    analyze math_q3_14 math P3 P3
    analyze math_granite math P4 P4
    analyze hotpot_iso_q15_7 hotpot_iso P1 P2
    analyze hotpot_granite hotpot P4 P4
    analyze hotpot_iso_granite hotpot_iso P4 P4
    "$PY" scripts/v2/hypotheses_report.py --p6 "$OUT" --output-dir "$OUT/hypotheses" ${DRY[@]+"${DRY[@]}"}
    ;;
  final)
    ;;
  *)
    echo "unknown phase $phase" >&2
    exit 2
    ;;
esac

if [ ${#DRY[@]} -gt 0 ]; then
  echo "=== $phase dry run done"
  exit 0
fi
cp "$LOGS/$phase.log" "$OUT/run.log.txt"
if [ "$phase" = final ]; then
  for p in P1 P2 P3 P4 P5 P6; do
    [ -d "$RESULTS/$p" ] && cp -R "$RESULTS/$p" "$OUT/"
  done
fi
scripts/v2/package_phase.sh "$phase"
echo "=== $phase done $(date -u +%FT%TZ)"
