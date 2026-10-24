# Every call written to a cache file since <epoch>: truncation (>= max_tokens or finish_reason length) and logprobs.
import json, sqlite3, sys
db, since, mt = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
rows = sqlite3.connect(db).execute("select response from gen where created >= ?", (since,)).fetchall()
n = trunc = lp = 0
for (resp,) in rows:
    d = json.loads(resp); c = d["choices"][0]
    n += 1
    trunc += int(c.get("finish_reason") == "length" or int(d.get("usage", {}).get("completion_tokens", 0)) >= mt)
    lp += int(c.get("logprobs") is not None)
print(f"calls since start: {n}; hit the {mt}-token limit: {trunc} ({trunc / n:.1%}); with logprobs: {lp}/{n}")
print(f"TRUNC_RATE={trunc / n:.4f} LOGPROBS_ALL={lp == n}")
