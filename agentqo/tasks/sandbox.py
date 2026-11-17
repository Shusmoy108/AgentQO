"""L2-X7: run untrusted model code in an isolated subprocess (Linux only).

Model code is never exec'd or eval'd in the agent process. Each run gets a fresh temp dir and a new
user, network, mount and PID namespace (util-linux ``unshare``):
  - no network: a new network namespace with no interfaces up;
  - filesystem: the temp dir is bind-mounted over /mnt (which also hides /mnt/data: the repo, caches,
    results, the venv); /tmp, /var/tmp, /dev/shm, /home, /root, /run, /srv, /opt and /media are covered
    by empty read-only tmpfs; everything else is owned by the real root and not writable;
  - privileges: the process runs as the invoking non-root user (mapped to uid 0 in the namespace) with
    every capability dropped and no_new_privs, so it cannot undo the mounts;
  - limits: empty environment, address space 2 GB, 64 processes, 64 MB files, 64 open files, and a
    wall-clock timeout after which the whole process group is killed;
  - interpreter: the system /usr/bin/python3 in isolated mode (-I).
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import tempfile
from dataclasses import dataclass

PYTHON = "/usr/bin/python3"
HIDE = ("/tmp", "/var/tmp", "/dev/shm", "/home", "/root", "/run", "/srv", "/opt", "/media")
_SETUP = r"""
set -e
mount --bind "$1" /mnt
for d in {hide}; do [ -d "$d" ] && mount -t tmpfs -o ro,size=1m,mode=555 tmpfs "$d"; done
cd /mnt
exec setpriv --no-new-privs --inh-caps=-all --bounding-set=-all \
  prlimit --as={mem} --nproc={nproc} --fsize={fsize} --nofile=64 -- \
  env -i PATH=/usr/bin:/bin HOME=/mnt {python} -I prog.py
"""


@dataclass
class SandboxResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out


def available() -> bool:
    return sys.platform.startswith("linux") and shutil.which("unshare") is not None and os.path.exists(PYTHON)


def run_python(code: str, timeout_s: float = 10.0, mem_bytes: int = 2 * 1024 ** 3, nproc: int = 64,
               base_dir: str | None = None) -> SandboxResult:
    """Run ``code`` as prog.py in a fresh sandbox; returns exit code, output and whether it timed out."""
    if not available():
        raise RuntimeError("the X7 sandbox needs Linux with util-linux unshare and /usr/bin/python3")
    work = tempfile.mkdtemp(prefix="x7sbx_", dir=base_dir)
    try:
        with open(os.path.join(work, "prog.py"), "w") as fh:
            fh.write(code)
        setup = _SETUP.format(hide=" ".join(HIDE), mem=mem_bytes, nproc=nproc, fsize=64 * 1024 ** 2, python=PYTHON)
        cmd = ["unshare", "--user", "--map-root-user", "--net", "--mount", "--pid", "--fork", "--kill-child",
               "--mount-proc", "--propagation", "private", "sh", "-c", setup, "sh", work]
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, errors="replace", start_new_session=True, env={"PATH": "/usr/bin:/bin"})
        try:
            out, err = proc.communicate(timeout=timeout_s)
            return SandboxResult(proc.returncode, out[-20000:], err[-20000:], False)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            out, err = proc.communicate()
            return SandboxResult(-9, out[-20000:], err[-20000:], True)
    finally:
        shutil.rmtree(work, ignore_errors=True)
