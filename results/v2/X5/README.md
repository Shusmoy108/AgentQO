# X5: MATH-500 (L2-X5/X6, exploratory)

Data: HuggingFaceH4/MATH-500, file test.jsonl (500 problems), pinned to Hugging Face commit
6e4ed1a2a79af7d8630a6b768ec859cb5af4d3be (the "main" revision on 2026-11-17T01:57:03Z). sha256 of the file used:
35dc41080a3680858b27fa7e0533d2d547825316fc5dafe5d316f4ccc5a06132. The file was fetched at that commit
(resolve/6e4ed1a2.../test.jsonl), checked to be byte-identical to main, and placed at
/mnt/data/AgentQO-x/data/tasks/math500_test.jsonl on both VMs before any X5 run, so the loader never
downloads it again. Split: seed-0 permutation of the 500 rows sorted by unique_id; label = first 200,
eval = other 300 (ids in data/tasks/math500_split.json, copied here when written).
Code: branch v2-lease2-x commit c1bb8338 (agentqo/tasks/math500.py, answers.extract_boxed/math_equal).
Scorer: last balanced \boxed{} after normalize_math; correct if normalized strings match or numeric
values match (rel. tol. 1e-6); no \boxed{} = unscorable. Not changed during the lease.
Safeguards: (1) prompt check before the smoke run (every agent's prompt for the 5 smoke problems, built
with the run's code) and on every prompt actually sent in the label traces: no prompt contains
"#### <number>" or "<number>"; every agent except the planner (which only plans and has no answer
format) contains "\boxed" or "RESULT: <expression>"; a violation fails X5. (2) this data record.
(3) scorer_audit.csv (40 random label problems scored wrong with a prediction, seed 0: gold, pred, raw
final text, empty hand_check_equivalent column) and unscorable_by_agent.csv, written after labels, for a
manual false-negative check later.
