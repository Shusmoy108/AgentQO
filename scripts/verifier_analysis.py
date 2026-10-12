#!/usr/bin/env python3
"""How much does the verifier change the aggregator's answer, and is it right?

Reads H1 baseline traces (no model calls). For each run directory, reports
aggregator accuracy, verifier accuracy, how often the verifier changed the
answer, and whether those changes fixed or broke it.

    python3 scripts/verifier_analysis.py data/ollama/h1_n30 data/ollama/h1_math_judge
"""

import json
import sys
from pathlib import Path


def same(a, b):
    if a is None or b is None:
        return False
    try:
        return abs(float(str(a).replace(",", "")) - float(str(b).replace(",", ""))) < 1e-6
    except ValueError:
        return str(a).strip() == str(b).strip()


def analyze(run_dir: Path):
    tdir = run_dir / "h1" / "math_reasoning_s3_ver" / "traces"
    traces = [json.loads(p.read_text()) for p in sorted(tdir.glob("*.json"))]
    n = len(traces)
    agg_ok = ver_ok = changed = fixed = broke = wrong_to_wrong = no_key = 0
    for t in traces:
        gold = t["gold"]
        a = t["nodes"].get("aggregator", {}).get("key")
        v = t["nodes"].get("verifier", {}).get("key")
        if v is None:
            no_key += 1
        a_ok, v_ok = same(a, gold), same(v, gold)
        agg_ok += a_ok
        ver_ok += v_ok
        if not same(a, v):
            changed += 1
            fixed += (not a_ok) and v_ok
            broke += a_ok and (not v_ok)
            wrong_to_wrong += (not a_ok) and (not v_ok)
    print(f"\n{run_dir}  (n = {n})")
    print(f"  aggregator accuracy        {agg_ok / n:.2f}")
    print(f"  verifier (final) accuracy  {ver_ok / n:.2f}")
    print(f"  verifier changed answer    {changed}/{n}")
    print(f"    wrong -> right (fixed)   {fixed}")
    print(f"    right -> wrong (broke)   {broke}")
    print(f"    wrong -> other wrong     {wrong_to_wrong}")
    print(f"  verifier gave no number    {no_key}/{n}")


if __name__ == "__main__":
    for d in sys.argv[1:]:
        analyze(Path(d))
