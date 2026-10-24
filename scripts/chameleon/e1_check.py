import json
c14s = json.load(open("data/vllm/c14_h3_cautious_eval200/h3_summary.json"))
e1s = json.load(open("data/vllm/e1_output_cautious/h3_summary.json"))
print("qids identical to C14c:", c14s["qids"] == e1s["qids"], "n =", len(e1s["qids"]))
c14 = json.load(open("data/vllm/c14_h3_cautious_eval200/h3_traces.json"))
e1 = json.load(open("data/vllm/e1_output_cautious/h3_traces.json"))
for p in ("all_small", "ec_top2", "all_large"):
    print(f"{p:<10} per-problem identical to C14c (correct and node answers): {c14[p] == e1[p]}")
