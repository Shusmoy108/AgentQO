"""L2-X7 (MBPP+ code chain) on branch v2-lease2-x: sandbox isolation, loader, scoring, workflow, prompts.

The sandbox tests need Linux (util-linux unshare); they are skipped elsewhere and are run on the lease VMs
before any X7 data (a failure stops X7)."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from agentqo.tasks import mbppplus, sandbox
from agentqo.tasks.mbppplus import extract_code, load_mbppplus
from agentqo.tasks.real_task_model import RealTaskModel
from agentqo.workflows.library import create_code_workflow

linux = pytest.mark.skipif(not sandbox.available(), reason="the X7 sandbox needs Linux with util-linux unshare")


# ---------------------------------------------------------------- sandbox isolation (Linux)
@linux
def test_sandbox_runs_code_in_fresh_dir():
    r = sandbox.run_python("import os\nprint('hi', os.getcwd(), sorted(os.listdir('.')))\nopen('out.txt','w').write('x')")
    assert r.ok and "hi /mnt ['prog.py']" in r.stdout


@linux
def test_sandbox_blocks_network():
    code = ("import socket\n"
            "for host, port in [('1.1.1.1', 53), ('10.56.2.39', 8002), ('huggingface.co', 443)]:\n"
            "    try:\n"
            "        socket.create_connection((host, port), timeout=2); print('CONNECTED', host)\n"
            "    except OSError as e:\n"
            "        print('BLOCKED', host)\n")
    r = sandbox.run_python(code)
    assert r.ok and "CONNECTED" not in r.stdout and r.stdout.count("BLOCKED") == 3


@linux
def test_sandbox_blocks_writes_outside_temp_dir(tmp_path):
    home = Path(os.path.expanduser("~"))
    targets = [tmp_path / "x7_canary", home / "x7_canary", Path("/mnt/data/x7_canary"), Path("/etc/x7_canary"),
               Path("/usr/x7_canary"), Path("/tmp/x7_canary"), Path("/var/tmp/x7_canary"), Path("/dev/shm/x7_canary"),
               Path(__file__).resolve().parent / "x7_canary"]
    code = "for p in %r:\n    try:\n        open(p, 'w').write('x'); print('WROTE', p)\n    except OSError:\n        print('DENIED', p)\n" % [str(t) for t in targets]
    r = sandbox.run_python(code)
    assert r.ok and "WROTE" not in r.stdout and r.stdout.count("DENIED") == len(targets)
    assert not any(t.exists() for t in targets)            # nothing landed on the host


@linux
def test_sandbox_hides_repo_caches_and_mnt_data(tmp_path):
    canary = tmp_path / "secret.txt"
    canary.write_text("secret")
    repo_file = str(Path(__file__).resolve())
    code = ("import os\n"
            f"for p in [{str(canary)!r}, {repo_file!r}, '/mnt/data', os.path.expanduser('~/.ssh'), '/proc/1/environ']:\n"
            "    try:\n"
            "        print('SEE', p, (os.listdir(p) if os.path.isdir(p) else open(p).read(30))[:3])\n"
            "    except OSError:\n"
            "        print('HIDDEN', p)\n")
    r = sandbox.run_python(code)
    assert r.ok and "secret" not in r.stdout
    assert f"HIDDEN {canary}" in r.stdout and f"HIDDEN {repo_file}" in r.stdout and "HIDDEN /mnt/data" in r.stdout


@linux
def test_sandbox_kills_infinite_loop():
    t0 = time.time()
    r = sandbox.run_python("while True:\n    pass\n", timeout_s=2)
    assert r.timed_out and not r.ok and time.time() - t0 < 8


@linux
def test_sandbox_limits_memory_and_processes():
    mem = sandbox.run_python("try:\n    b = bytearray(3 * 1024 ** 3); print('ALLOCATED')\nexcept MemoryError:\n    print('MEMERR')\n")
    assert "ALLOCATED" not in mem.stdout
    procs = sandbox.run_python(
        "import subprocess\nn = 0\ntry:\n    ps = []\n    for i in range(200):\n"
        "        ps.append(subprocess.Popen(['/bin/sleep', '5'])); n += 1\nexcept OSError:\n    pass\nprint('SPAWNED', n)\n",
        timeout_s=8)
    assert "SPAWNED" in procs.stdout and int(procs.stdout.split("SPAWNED")[1].split()[0]) < 64


@linux
def test_sandbox_empty_env_and_cannot_undo_mounts():
    r = sandbox.run_python("import os, subprocess\nprint(sorted(os.environ))\n"
                           "print('UMOUNT', subprocess.run(['umount', '/home'], capture_output=True).returncode)\n")
    assert r.ok
    assert set(eval(r.stdout.splitlines()[0])) <= {"PATH", "HOME", "PWD", "LC_CTYPE"}  # noqa: S307 (our own output)
    assert "UMOUNT 0" not in r.stdout


# ---------------------------------------------------------------- data and scoring
def _write_rows(d: Path, n: int = 378):
    rows = [{"task_id": i + 2, "prompt": f"Write a function f{i} that returns its input plus {i}.", "code": "",
             "test_imports": [], "test_list": [f"assert f{i}(1) == {1 + i}"],
             "test": f"for x in range(5):\n    assert f{i}(x) == x + {i}\n"} for i in range(n)]
    (d / "mbppplus.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    mbppplus._rows.cache_clear()


def test_load_mbppplus_split(tmp_path):
    _write_rows(tmp_path)
    lab, ev = load_mbppplus("label", tmp_path), load_mbppplus("eval", tmp_path)
    assert len(lab) == 200 and len(ev) == 178 and not {p["qid"] for p in lab} & {p["qid"] for p in ev}
    assert lab == load_mbppplus("label", tmp_path)
    p = lab[0]
    assert p["gold"] == "mbppplus:" + p["qid"].removeprefix("mbppplus-") and "Your code should pass this test:" in p["question"]


def test_extract_code_and_asserts():
    t = "PLAN\n```python\ndef f(x):\n    return x\n```\nthen\n```python\ndef f(x):\n    return x + 1\n```"
    assert extract_code(t) == "def f(x):\n    return x + 1"
    assert extract_code("no code") is None
    assert mbppplus.tester_asserts("```python\nassert f(1) == 2\nprint(1)\nassert f(0) == 1\n```") == ["assert f(1) == 2", "assert f(0) == 1"]


@linux
def test_passes_runs_hidden_tests_in_sandbox(tmp_path):
    _write_rows(tmp_path, 3)
    assert mbppplus.passes("def f0(x):\n    return x", "mbppplus:2", cache_dir=tmp_path)
    assert not mbppplus.passes("def f0(x):\n    return x + 1", "mbppplus:2", cache_dir=tmp_path)
    assert not mbppplus.passes("def f0(x):\n    while True:\n        pass", "mbppplus:2", timeout_s=2, cache_dir=tmp_path)
    assert not mbppplus.passes(None, "mbppplus:2", cache_dir=tmp_path)


def test_task_model_extracts_code():
    tm = RealTaskModel([{"qid": "mbppplus-2", "question": "q", "gold": "mbppplus:2"}], dataset="mbppplus")
    assert tm.extract("PICK: B\n```python\ndef f(): pass\n```") == "def f(): pass"


# ---------------------------------------------------------------- workflow and prompts
def test_code_workflow_has_32_plans():
    from scripts.run_real_h3 import all_subset_plans
    wf = create_code_workflow()
    assert list(wf.topological_order) == ["planner", "coder", "tester", "fixer", "verifier"]
    assert len(all_subset_plans(wf)) == 32


def test_code_prompts(monkeypatch):
    from agentqo.tasks import prompts
    monkeypatch.setattr(mbppplus, "example_tests", lambda qid, cache_dir=None: ["assert f(1) == 1"])
    monkeypatch.setattr(mbppplus, "assert_report", lambda code, tests, timeout_s=10.0: f"REPORT[{code}|{len(tests)}]")
    wf = create_code_workflow()
    res = {n: SimpleNamespace(output={"text": t}) for n, t in {
        "planner": "PLAN: 1. return x", "coder": "```python\ndef f(x):\n    return x\n```",
        "tester": "```python\nassert f(2) == 2\n```", "fixer": "```python\ndef f(x):\n    return int(x)\n```"}.items()}
    task = SimpleNamespace(metadata={"dataset": "mbppplus", "qid": "mbppplus-2", "problem": "Write f."}, task_id="mbppplus-2")
    ctx = {"workflow": wf, "results": res, "task": task, "problem": "Write f."}
    p = {n: prompts.build_prompt(wf.nodes[n], {}, ctx) for n in wf.topological_order}
    assert "Do not write code" in p["planner"] and "PLAN: 1. return x" in p["coder"]
    assert "def f(x):\n    return x" in p["tester"] and "assert statements" in p["tester"]
    assert "REPORT[def f(x):\n    return x|2]" in p["fixer"]                    # example test + tester assert
    assert "Candidate A" in p["verifier"] and "return int(x)" in p["verifier"] and "PICK: A" in p["verifier"]
    assert all("#### <number>" not in v for v in p.values())
