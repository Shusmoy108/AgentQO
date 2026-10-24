import json, sys
kind, path = sys.argv[1], sys.argv[2]
if kind == "dev":
    ref = json.load(open("data/vllm/h1_n100/run_config.json"))["qids"]; new = json.load(open(path))["qids"]; label = "C7 (100 dev)"
else:
    ref = json.load(open("data/vllm/h3_eval_n200/h3_summary.json"))["qids"]; new = json.load(open(path))["qids"]; label = "C9 (200 eval)"
print(f"{path}: task IDs identical to {label}: {ref == new} (n = {len(new)})")
sys.exit(0 if ref == new else 1)
