import json
c9 = json.load(open("data/vllm/h3_eval_n200/h3_traces.json"))
c13 = json.load(open("data/vllm/c13_budget_curve/h3_traces.json"))
s9 = json.load(open("data/vllm/h3_eval_n200/h3_summary.json"))
s13 = json.load(open("data/vllm/c13_budget_curve/h3_summary.json"))
print("qids identical to C9:", s9["qids"] == s13["qids"])
pairs = [("ec_top1", "only_aggregator"), ("ec_top2", "ec_top2"), ("struct_top2", "struct_top2"),
         ("struct_top1", "only_planner"), ("all_small", "all_small"), ("all_large", "all_large")]
for new, old in pairs:
    same = ([a["correct"] for a in c13[new]] == [b["correct"] for b in c9[old]]
            and [a["keys"] for a in c13[new]] == [b["keys"] for b in c9[old]])
    print(f"C13 {new:<12} == C9 {old:<16} per task: {same}")
for r in s13["plans"]:
    print(f"{r['plan']:<12} upgraded={r['upgraded']:<34} cost={r['cost_units']:.0f} "
          f"acc={r['accuracy']:.3f} correct={round(r['accuracy'] * 200)}/200")
