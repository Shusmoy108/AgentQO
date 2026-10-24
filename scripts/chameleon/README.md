# Chameleon session scripts (lease AGENTQO, 2026-10-23/24)

Shell and helper scripts that drove the runs on VM-A (they lived in /tmp during the session).
They call the repo scripts (run_real_pipeline.py, run_real_h3.py, placement_test.py, h4_fit.py,
h4_workflow_load.py, verifier_analysis.py) and write logs/ and data/ as recorded in logs/changes.txt
and logs/h4_changes.txt.

- run_c12.sh, run_c13.sh, run_c14a.sh, run_c14b.sh, run_c14c.sh, check_c13.py: follow-up C12-C14
- grid.sh, chain_p1a.sh, pt.sh, serve.sh, p2.sh, p3.sh, master.sh: H4 (P1-P4); serve.sh starts/stops vLLM and MPS
- e_chain.sh, e1_check.py, e2a_analysis.py, e2b_check.py: follow-up E (E1, E2a, E2b)
- final_A.sh, final_branch.sh: bundles and the session1-results branch
- f1_chain.sh, f2_chain.sh, f2_extract_check.py, ids_check.py: last run (F1, F2 smoke)
- f3_chain.sh, f3_smoke_check.py, f3_calls.py, f3a_analysis.py: F3 (Granite, max_tokens 512)
