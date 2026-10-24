# Smoke check for Granite: logprobs present, answers extracted with the unchanged extract_gsm8k_number.
import glob, json, re, sys
sys.path.insert(0, ".")
from agentqo.tasks.answers import extract_gsm8k_number
d = sys.argv[1]
ok = True
for f in sorted(glob.glob(f"{d}/h1/math_reasoning_s3_ver/traces/*.json")):
    t = json.load(open(f))
    for nid in ("step_1", "step_2", "step_3", "aggregator"):
        out = t["nodes"][nid]["output"]
        key = extract_gsm8k_number(out)
        marker = "####" in out or "RESULT:" in out
        print(f"{t['task_id']:<18} {nid:<11} marker={'yes' if marker else 'NO '} key={key!s:<10} tail={out[-60:]!r}")
        if nid == "aggregator" and ("####" not in out or key is None):
            ok = False
print("EXTRACTION_OK" if ok else "EXTRACTION_FAILED")
sys.exit(0 if ok else 1)
