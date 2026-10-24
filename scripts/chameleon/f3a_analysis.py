import csv, json, statistics, sys
from collections import defaultdict
sys.path.insert(0, ".")
from scripts.run_real_h3 import load_qplus
d = "data/vllm/f3_granite512_h1_n100/h1/math_reasoning_s3_ver"
s = json.load(open(f"{d}/h1_summary.json"))
print(f"baseline accuracy {s['baseline_accuracy']:.3f}  holds={s['h1_holds']} range={s['range']:.3f} cv={s['cv']:.3f}")
ab = defaultdict(list)
for r in csv.DictReader(open(f"{d}/absorption.csv")):
    ab[r["node_id"]].append(r["absorbed"] == "True")
q = load_qplus(d)
print(f"{'node':<12}{'consequence [95% CI]':>28}{'p_err':>7}{'EC':>8}{'absorbed':>10}{'Q+':>7}{'Q-':>7}{'Q+-base':>9}")
for n, v in s["by_node"].items():
    a = sum(ab[n]) / len(ab[n]) if ab[n] else float("nan")
    qq = q.get(n, {"q_plus": float("nan"), "q_minus": float("nan"), "q_plus_minus_baseline": float("nan")})
    print(f"{n:<12}{v['consequence']:+9.3f} [{v['ci'][0]:+.3f},{v['ci'][1]:+.3f}]{v['p_err']:7.2f}{v['ec']:+8.3f}"
          f"{a:10.3f}{qq['q_plus']:7.3f}{qq['q_minus']:7.3f}{qq['q_plus_minus_baseline']:+9.3f}")
cons = [v["consequence"] for v in s["by_node"].values()]
mx, med = max(cons), statistics.median(cons)
held = (mx >= 3 * med) if med > 0 else (mx > 0)
print(f"\nPrediction 1: max consequence {mx:+.3f}, median {med:+.3f}, ratio {mx / med if med else float('nan'):.2f} -> {'HELD' if held else 'FAILED'}")
