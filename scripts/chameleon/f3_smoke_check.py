import glob, json, subprocess, sys
sys.path.insert(0, ".")
from agentqo.tasks.answers import extract_gsm8k_number
d, since = sys.argv[1], sys.argv[2]
ok = True
for f in sorted(glob.glob(f"{d}/h1/math_reasoning_s3_ver/traces/*.json")):
    t = json.load(open(f)); a = t["nodes"]["aggregator"]
    key = extract_gsm8k_number(a["output"])
    print(f"{t['task_id']:<18} aggregator key={key!s:<8} gold={t['gold']:<6} '####' present={'####' in a['output']} tokens={a['completion_tokens']} tail={a['output'][-70:]!r}")
    ok &= key is not None
out = subprocess.run([sys.executable, "/tmp/f3_calls.py", "data/cache/vllm_granite.sqlite", since, "512"], capture_output=True, text=True).stdout
print(out, end="")
rate = float(out.split("TRUNC_RATE=")[1].split()[0]); lp = "LOGPROBS_ALL=True" in out
print(f"criteria: every aggregator yields a number={ok}; truncation {rate:.1%} < 10%={rate < 0.10}; logprobs on every call={lp}")
print("SMOKE_PASS" if ok and rate < 0.10 and lp else "SMOKE_FAIL")
sys.exit(0 if ok and rate < 0.10 and lp else 1)
