import json
c9 = json.load(open("data/vllm/h3_eval_n200/h3_summary.json"))["qids"]
e2 = json.load(open("data/vllm/e2_complex_h3_eval200/h3_summary.json"))["qids"]
print("E2b qids identical to C9:", c9 == e2, "n =", len(e2))
