"""M10: the phase driver on the fake backend, and packaging against a local bare remote."""

import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

from scripts.v2.summarize_phase import copy_for_git, free_zip_name, make_zip, manifest, report

ROOT = Path(__file__).resolve().parent.parent
GSM8K = (ROOT / "data/tasks/gsm8k_test.jsonl").exists() and (ROOT / "data/tasks/split.json").exists()
HOTPOT = (ROOT / "data/tasks/hotpot_dev_distractor.jsonl").exists()


def phase(tmp, name, **env):
    full = {**os.environ, "V2_BACKEND": "fake", "V2_N": "3", "V2_WORKERS": "2", "V2_PUSH": "0",
            "V2_RESULTS": str(tmp / "results"), "V2_LOGS": str(tmp / "logs"), "V2_CACHE": str(tmp / "c.sqlite"),
            "V2_ZIP_DIR": str(tmp), **env}
    return subprocess.run(["scripts/v2/run_phase.sh", name], cwd=ROOT, env=full, check=True,
                          capture_output=True, text=True).stdout


def test_step_tables_manifest_and_zip(tmp_path):
    root = tmp_path / "P9"
    step = root / "s" / "labels"
    step.mkdir(parents=True)
    (step / "run_config.v2.json").write_text('{"a": 1}')
    (step / "labels_v2.csv").write_text("agent,uv\nplanner,0.12345\n")
    (step / "c.sqlite").write_text("cache")
    (step / "traces.bin").write_text("x")
    summary = report(root)
    text = (root / "SUMMARY.md").read_text()
    assert "| s/labels | UNFINISHED |" in text and "| planner | 0.123 |" in text
    assert summary["steps"][0]["finished"] is False and json.loads((root / "summary.json").read_text())["phase"] == "P9"
    manifest(root)
    listed = (root / "MANIFEST.txt").read_text()
    assert "SUMMARY.md" in listed and "s/labels/labels_v2.csv" in listed and "MANIFEST.txt" not in listed
    zipped = make_zip(root, "P9", tmp_path)
    names = zipfile.ZipFile(zipped).namelist()
    assert "results/v2/P9/s/labels/labels_v2.csv" in names and not any(n.endswith(".sqlite") for n in names)
    assert free_zip_name("P9", tmp_path).name == "results_v2_P9_2.zip"
    assert make_zip(root, "P9", tmp_path).name == "results_v2_P9_2.zip"  # never overwrites
    with_cache = zipfile.ZipFile(make_zip(root, "final", tmp_path, extra=[step / "c.sqlite"])).namelist()
    assert "cache/c.sqlite" in with_cache
    dest = tmp_path / "copy"
    assert copy_for_git(root, dest) >= 4 and not (dest / "s/labels/c.sqlite").exists()
    assert not (dest / "s/labels/traces.bin").exists()


@pytest.mark.skipif(not GSM8K, reason="GSM8K working set not downloaded")
def test_math_phases_run_end_to_end_and_resume(tmp_path):
    results = tmp_path / "results"
    phase(tmp_path, "P1", V2_SETTINGS="math")
    p1 = results / "P1" / "math_q15_7"
    for f in ("labels/labels_v2.csv", "labels/labels_v2_per_problem.csv", "labels_disagree/labels_v2.csv"):
        assert (p1 / f).exists()
    assert (results / "P1/SUMMARY.md").read_text().count("labels_v2.csv") >= 2
    assert (tmp_path / "results_v2_P1.zip").exists() and (tmp_path / "logs/P1.log").exists()

    phase(tmp_path, "P2", V2_SETTINGS="math")
    assert len((results / "P2/math_q15_7/plans/h3_plans.csv").read_text().splitlines()) == 65
    phase(tmp_path, "P5", V2_PLACEMENT="separate")
    phase(tmp_path, "P5", V2_PLACEMENT="shared")
    assert (results / "P5/shared/placement_summary.csv").exists()

    out = phase(tmp_path, "P6")
    assert "skip hotpot_q15_7" in out and "skip math_q3_14" in out
    p6 = results / "P6" / "math_q15_7"
    for f in ("cost/plan_costs.csv", "rules/rule_plans.csv", "rules/estimator_errors.csv", "rules/h1c.json",
              "routing/routing.csv", "adaptive/adaptive_summary.json", "pareto/pareto_front.csv",
              "pareto/two_step_baseline.csv", "pareto/constrained_best.csv", "pareto/budget_best.csv",
              "pareto/latency_check.csv", "pareto_estimated/pareto_summary.json"):
        assert (p6 / f).exists(), f
    summary = json.loads((p6 / "pareto/pareto_summary.json").read_text())
    assert summary["hypervolume_joint"] >= summary["hypervolume_two_step"] > 0
    assert "regret_hypervolume" in json.loads((p6 / "pareto_estimated/pareto_summary.json").read_text())
    text = (results / "P6/SUMMARY.md").read_text()
    assert "### pareto_front.csv" in text and "UNFINISHED" not in text
    # A11: rates from the P5 runs, a basis flag on every GPU cost, and hypotheses.md says which.
    assert (p6 / "cost/token_rates.csv").read_text().count("\n") >= 3
    costs = (p6 / "cost/plan_costs.csv").read_text()
    assert "estimated_rates" in costs and "fallback_latency" in costs  # no P5 run under shared_mps
    hyp = (results / "P6/hypotheses/hypotheses.md").read_text()
    assert "## Cost basis" in hyp and "fallback_latency" in hyp and "## Hypotheses" in text

    # A repeat finds every step finished: no new directories, a new zip name.
    before = sorted(p.name for p in p6.iterdir())
    assert "already finished" in phase(tmp_path, "P6")
    assert sorted(p.name for p in p6.iterdir()) == before
    assert (tmp_path / "results_v2_P6_2.zip").exists()

    phase(tmp_path, "final")
    names = zipfile.ZipFile(tmp_path / "results_v2_final.zip").namelist()
    assert "cache/c.sqlite" in names and any("/P6/" in n for n in names)


def test_dry_run_writes_nothing(tmp_path):
    out = phase(tmp_path, "P2", V2_DRY="1", V2_SETTINGS="math")
    assert "would run 64 plans" in out and "dry run done" in out
    assert not (tmp_path / "results/P2/math_q15_7").exists()
    assert not list(tmp_path.glob("results_v2_*.zip"))


@pytest.mark.skipif(not HOTPOT, reason="HotpotQA not downloaded")
def test_hotpot_phases_run_end_to_end(tmp_path):
    phase(tmp_path, "P1", V2_SETTINGS="hotpot")
    phase(tmp_path, "P2", V2_SETTINGS="hotpot")
    results = tmp_path / "results"
    plans = (results / "P2/hotpot_q15_7/plans/h3_plans.csv").read_text().splitlines()
    assert len(plans) == 33 and "f1" in plans[0]
    assert "f1" in (results / "P2/hotpot_q15_7/plans/h3_per_problem.csv").read_text().splitlines()[0]
    phase(tmp_path, "P6")
    assert (results / "P6/hotpot_q15_7/pareto/pareto_front.csv").exists()


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
    return subprocess.run(["git", *args], cwd=cwd, env=env, check=True, capture_output=True, text=True).stdout.strip()


def test_package_commits_text_only_and_never_forces(tmp_path):
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "--bare", str(remote))
    repo = tmp_path / "repo"
    (repo / "scripts/v2").mkdir(parents=True)
    git(repo, "init", "-b", "work")
    for name in ("package_phase.sh", "summarize_phase.py"):
        shutil.copy2(ROOT / "scripts/v2" / name, repo / "scripts/v2" / name)
    (repo / ".gitignore").write_text("results/\nresults_v2_*.zip\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "base")
    git(repo, "remote", "add", "origin", str(remote))
    head = git(repo, "rev-parse", "HEAD")

    step = repo / "results/v2/P1/s"
    step.mkdir(parents=True)
    (step / "run_config.v2.json").write_text("{}")
    (step / "labels_v2.csv").write_text("agent,uv\na,1\n")
    (step / "cache.sqlite").write_text("no")
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
    run = lambda: subprocess.run(["scripts/v2/package_phase.sh", "P1"], cwd=repo, env=env, check=True,
                                 capture_output=True, text=True).stdout
    assert "pushed P1" in run()
    # The checked-out branch and its commit do not move.
    assert git(repo, "rev-parse", "--abbrev-ref", "HEAD") == "work" and git(repo, "rev-parse", "HEAD") == head
    files = git(remote, "ls-tree", "-r", "--name-only", "v2-lease1").splitlines()
    assert "results/v2/P1/s/labels_v2.csv" in files and "results/v2/P1/SUMMARY.md" in files
    assert "results/v2/P1/MANIFEST.txt" in files
    assert not any(f.endswith((".sqlite", ".zip")) for f in files)
    assert (repo / "results_v2_P1.zip").exists()

    (step / "labels_v2.csv").write_text("agent,uv\na,2\n")
    first = git(remote, "rev-parse", "v2-lease1")
    run()
    assert git(remote, "rev-parse", "v2-lease1~1") == first  # appended, not rewritten
    assert (repo / "results_v2_P1_2.zip").exists()
    assert not list(tmp_path.glob("tmp*")) and git(repo, "worktree", "list").count("\n") == 0


def test_provenance_records_commit_and_refuses_dirty_lease_runs(tmp_path):
    """FIX 3: the full HEAD of the code run, a dirty flag, and no lease phase from a dirty tree."""
    repo = tmp_path / "repo"
    (repo / "scripts/v2").mkdir(parents=True)
    git(repo, "init", "-b", "work")
    shutil.copy2(ROOT / "scripts/v2/summarize_phase.py", repo / "scripts/v2/summarize_phase.py")
    (repo / ".gitignore").write_text("results/\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "base")
    head = git(repo, "rev-parse", "HEAD")
    prov = lambda *a: subprocess.run(["python3", "scripts/v2/summarize_phase.py", "provenance", "results/v2/P1", *a],
                                     cwd=repo, capture_output=True, text=True)
    assert prov("--refuse-dirty").returncode == 0
    (repo / "scripts/v2/new_helper.py").write_text("x = 1\n")  # untracked code makes the tree dirty
    assert prov().returncode == 0
    refused = prov("--refuse-dirty")
    assert refused.returncode != 0 and "uncommitted" in refused.stderr
    runs = [json.loads(x) for x in (repo / "results/v2/P1/provenance.jsonl").read_text().splitlines()]
    assert [r["dirty"] for r in runs] == [False, True] and all(r["commit"] == head for r in runs)
    subprocess.run(["python3", "scripts/v2/summarize_phase.py", "report", "results/v2/P1"], cwd=repo, check=True)
    summary = json.loads((repo / "results/v2/P1/summary.json").read_text())
    assert summary["git_commit"] == head and summary["dirty"] is True and summary["packaged_at"]["dirty"] is True
    assert f"`{head}` **(dirty working tree)**" in (repo / "results/v2/P1/SUMMARY.md").read_text()


def test_lease_runs_need_the_tag_or_a_logged_deviation(tmp_path):
    repo = tmp_path / "repo"
    (repo / "scripts/v2").mkdir(parents=True)
    (repo / "prereg").mkdir()
    git(repo, "init", "-b", "work")
    shutil.copy2(ROOT / "scripts/v2/summarize_phase.py", repo / "scripts/v2/summarize_phase.py")
    (repo / "prereg/v2_amendments.md").write_text("D1 lease-time deviation: fix\n")
    (repo / ".gitignore").write_text("results/\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "base")
    prov = lambda **env: subprocess.run(["python3", "scripts/v2/summarize_phase.py", "provenance", "results/v2/P1",
                                         "--refuse-dirty", "--lease"], cwd=repo, capture_output=True, text=True,
                                        env={**os.environ, **env})
    assert "not found" in prov().stderr
    git(repo, "tag", "v2-lease1-start")
    assert prov().returncode == 0
    (repo / "x.txt").write_text("x")
    git(repo, "add", "x.txt")
    git(repo, "commit", "-m", "lease-time change")
    assert "is not v2-lease1-start" in prov().stderr
    assert prov(V2_DEVIATION="D9").returncode != 0  # not logged
    assert prov(V2_DEVIATION="D1").returncode == 0
    last = json.loads((repo / "results/v2/P1/provenance.jsonl").read_text().splitlines()[-1])
    assert last["deviation"] == "D1" and last["lease_tag_commit"] != last["commit"]
