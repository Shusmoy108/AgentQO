#!/usr/bin/env python3
"""How much does the verifier change the aggregator's answer, and is it right?

Reads H1 baseline traces (no model calls). For each run directory, reports
aggregator accuracy, verifier accuracy, how often the verifier changed the
answer, and whether those changes fixed or broke it.

    python3 scripts/verifier_analysis.py data/ollama/h1_n30 data/ollama/h1_math_judge

--details adds a verdict-vs-correctness cross-tab, a kept/changed cross-tab and
the median verifier output length in tokens.
"""

import json
import re
import statistics
import sys
from pathlib import Path

_VERDICT = re.compile(r"VERDICT:\s*(correct|incorrect)", re.IGNORECASE)


def same(a, b):
    if a is None or b is None:
        return False
    try:
        return abs(float(str(a).replace(",", "")) - float(str(b).replace(",", ""))) < 1e-6
    except ValueError:
        return str(a).strip() == str(b).strip()


def analyze(run_dir: Path, details: bool = False):
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
    if details:
        print_details(traces)


def print_details(traces):
    """Cross-tabs against aggregator correctness, and verifier output length."""
    verdict = {}
    action = {}
    tokens = []
    for t in traces:
        a_ok = same(t["nodes"].get("aggregator", {}).get("key"), t["gold"])
        ver = t["nodes"].get("verifier", {})
        m = _VERDICT.findall(ver.get("output") or "")
        v = f"VERDICT: {m[-1].lower()}" if m else "no VERDICT line"
        verdict[(v, a_ok)] = verdict.get((v, a_ok), 0) + 1
        kept = same(t["nodes"].get("aggregator", {}).get("key"), ver.get("key"))
        k = "kept answer" if kept else "changed answer"
        action[(k, a_ok)] = action.get((k, a_ok), 0) + 1
        if ver.get("completion_tokens") is not None:
            tokens.append(ver["completion_tokens"])
    for title, tab, rows in (("verdict", verdict, ["VERDICT: correct", "VERDICT: incorrect", "no VERDICT line"]),
                             ("action", action, ["kept answer", "changed answer"])):
        print(f"  {title} vs aggregator correctness:   agg right  agg wrong")
        for r in rows:
            print(f"    {r:<30}{tab.get((r, True), 0):>9}{tab.get((r, False), 0):>11}")
    med = statistics.median(tokens) if tokens else float("nan")
    print(f"  median verifier output tokens  {med:g}  (n = {len(tokens)})")


if __name__ == "__main__":
    args = sys.argv[1:]
    details = "--details" in args
    for d in [a for a in args if a != "--details"]:
        analyze(Path(d), details)
