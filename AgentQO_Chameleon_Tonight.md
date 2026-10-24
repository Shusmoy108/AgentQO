# AgentQO on Chameleon: Tonight's Session

**KVM@TACC, 2 × H100, lease "AGENTQO"**
Friday Oct 23, 6:00 PM to Saturday Oct 24, 3:00 PM (Chicago time)

This guide covers tonight's session from start to finish: preparing on your Mac, launching two H100 virtual machines, connecting them as a two-GPU setup, running the experiments overnight, and shutting everything down cleanly. Work through it in order. Every command is copy-paste ready; replace anything in `<ANGLE BRACKETS>` with your own value.

---

## Contents

1. [Your lease and tonight's plan](#0-your-lease-and-tonights-plan)
2. [Before 6 PM: prepare on your Mac](#1-before-6-pm-prepare-on-your-mac)
3. [6:00 PM: launch both VMs](#2-600-pm-launch-both-vms)
4. [Floating IP and SSH](#3-floating-ip-and-ssh)
5. [First checks on both VMs](#4-first-checks-on-both-vms)
6. [Install the software](#5-install-the-software)
7. [Start the model servers](#6-start-the-model-servers)
8. [Smoke test and timing](#7-smoke-test-and-timing)
9. [The multi-GPU placement test (H4)](#8-the-multi-gpu-placement-test-h4)
10. [The overnight chain (H1, repair test, H3)](#9-the-overnight-chain-h1-repair-test-h3)
11. [Saturday morning: check and analyze](#10-saturday-morning-check-and-analyze)
12. [Copy results home and shut down](#11-copy-results-home-and-shut-down)
13. [Troubleshooting](#12-troubleshooting)
14. [Quick reference](#13-quick-reference)

---



## 0. Your lease and tonight's plan



### 0.1 The lease


|                |                                                                                       |
| -------------- | ------------------------------------------------------------------------------------- |
| Site           | **KVM@TACC** (virtual machines, not bare metal)                                       |
| Lease name     | **AGENTQO**                                                                           |
| Flavor         | `g1.h100.pci.1`: one NVIDIA H100 (94 GB) per VM, 48 vCPUs, 250 GB RAM, **40 GB disk** |
| Amount         | **2** (two VMs, one GPU each)                                                         |
| Reservation ID | `dfa3f9ae-9968-4e9c-9fd6-d7bd7f9760ad`                                                |
| Starts         | **Fri Oct 23, 6:00 PM Chicago** (23:00 UTC)                                           |
| Ends           | **Sat Oct 24, 3:00 PM Chicago** (20:00 UTC)                                           |
| Floating IPs   | None reserved; you take **one** ad hoc in Section 3                                   |


Chameleon shows times in **UTC**. Chicago is UTC−5 right now, so add 5 hours to Chicago time to get UTC.

### 0.2 The setup

```
  Your Mac
     │  SSH via floating IP
     ▼
┌──────────────────────────────┐   private network (sharednet1)   ┌──────────────────────────────┐
│ VM-A  "agentqo-1"   H100 #1  │ ───────────────────────────────▶ │ VM-B  "agentqo-2"   H100 #2  │
│  • AgentQO code, experiments │                                  │  • vLLM: Qwen2.5-7B   :8002  │
│  • vLLM: Qwen2.5-1.5B  :8001 │                                  │  • no public IP              │
└──────────────────────────────┘                                  └──────────────────────────────┘
```

The small model runs on GPU 1 and the large model on GPU 2. AgentQO runs on VM-A and sends large-model requests to VM-B over the private network. This is a real two-GPU deployment, which tonight's placement test (H4) needs.

### 0.3 What tonight should produce


| ID       | Experiment                                                          | Hypothesis      | Main question                                                            |
| -------- | ------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------------ |
| C1       | Smoke test                                                          | (setup)         | Does the vLLM pipeline work end to end?                                  |
| C2       | Timed 10-problem run                                                | (planning)      | How long do runs take on an H100?                                        |
| C3 to C6 | Placement test: split vs. colocated, with and without shared prefix | **H4**          | Do agent calls slow each other down more when they share a GPU?          |
| C7       | H1, math + self-consistency, 100 dev problems                       | **H1**          | Do the laptop criticality profiles replicate with full-precision models? |
| C8       | H1 with the passthrough verifier                                    | **H1 (repair)** | Does "repair inverts criticality" hold at scale?                         |
| C9       | H3, all plans, 200 unseen problems                                  | **H3**          | Does the criticality pair still beat the structural pair?                |
| C10, C11 | Verifier analysis, criticality vs. structure comparison             | H1, H3          | Summary numbers                                                          |


H2 waits for a later session, because it needs about four labeled workflows and a hidden-state probe.

### 0.4 Timeline


| Chicago time       | What                                              | Section |
| ------------------ | ------------------------------------------------- | ------- |
| **Before 6 PM**    | Push code, create key pair, check security groups | 1       |
| 6:00 to 6:20 PM    | Launch both VMs, floating IP, SSH                 | 2, 3, 4 |
| 6:20 to 7:00 PM    | Install software, start model servers             | 5, 6    |
| 7:00 to 7:30 PM    | Smoke test, timed run                             | 7       |
| 7:30 to 8:30 PM    | Placement test (needs idle GPUs)                  | 8       |
| ~8:30 PM           | Start the overnight chain, then sleep             | 9       |
| Sat morning        | Check progress, run analyses                      | 10      |
| **By 2:00 PM Sat** | Copy everything home, shut down                   | 11      |
| 3:00 PM Sat        | Lease ends automatically                          |         |


---



## 1. Before 6 PM: prepare on your Mac



### 1.1 Push all code to GitHub ✅ DONE

The VMs get your code by cloning the repository, so anything that exists only on your laptop will be missing. Tonight relies on several local changes:


| File                           | What it must contain                                                                        |
| ------------------------------ | ------------------------------------------------------------------------------------------- |
| `agentqo/tasks/prompts.py`     | hash-based tie-break in the vote; `import os`; the `judge` and `passthrough` verifier modes |
| `scripts/run_real_h3.py`       | the latest version (with `struct_top2` and trace saving)                                    |
| `scripts/verifier_analysis.py` | the verifier change analysis                                                                |
| `scripts/placement_test.py`    | **new**: the multi-GPU placement test                                                       |


```bash
cd ~/AgentQO
cp ~/Downloads/placement_test.py scripts/      # if not already there
python3 -m pytest tests/ -q                    # everything should pass
git status                                     # see what will be committed
git add -A
git commit -m "Tie-break fix, verifier modes, H3, verifier analysis, placement test"
git push
```

Then open your repository on github.com and check that the four files above are there and up to date. Make sure you don't commit the `data/` folder if it's large (it's normally excluded by `.gitignore`).

### 1.2 Create the key pair at KVM@TACC ✅ DONE (key pair: `agentqo-user`)

Key pairs are stored **per site**, so you need one at KVM@TACC even if you have one elsewhere.

1. In the KVM@TACC dashboard: **Compute → Key Pairs → Create Key Pair**.
2. Name: `agentqo-user`, Key Type: SSH Key. Click **Create Key Pair**. (Done.)
3. Your browser downloads `agentqo-user.pem`.

On your Mac:

```bash
mv ~/Downloads/agentqo-user.pem ~/.ssh/
chmod 600 ~/.ssh/agentqo-user.pem
ls -l ~/.ssh/agentqo-user.pem          # should show -rw-------
```

> Chameleon does not keep a copy of the private key. If you lose this file, you cannot log in to these VMs. Back it up somewhere safe.



### 1.3 Check the security groups

Security groups are firewalls for your VMs. Go to **Network → Security Groups** and click **Manage Rules** on `default`.

**You need two kinds of rules:**

1. **SSH from the internet to VM-A.** Look for an ingress rule on port 22. If none exists, create a separate group:
  - **Create Security Group** → name `agentqo-ssh` → **Add Rule**
  - Rule: **SSH**, Remote: **CIDR**, CIDR: `0.0.0.0/0` → **Add**
2. **Traffic between your two VMs.** The `default` group usually has an ingress rule whose remote is the `default` group itself, which allows all traffic between VMs in it. If you see such a rule, you're set. If not, add one now:
  - **Add Rule** → Rule: **Custom TCP Rule**, Port: **8002**, Remote: **Security Group**, Security Group: **default** → **Add**

You'll confirm both work in Section 6.

### 1.4 Optional: decide on a backup password

Public IPs at this site are scarce. If you can't get a floating IP at 6 PM, the backup is to log in through the browser console, which needs a password set at launch time. Pick one now (Section 2 shows where to enter it).

### 1.5 Checklist

- [x] Code pushed to GitHub
- [x] Key pair `agentqo-user` created
- [x] `agentqo-user.pem` moved to `~/.ssh/` with permissions `-rw-------` (commands in 1.2)
- [x] Verified on github.com that the four files in 1.1 are there
- [x] Security groups checked (SSH rule, VM-to-VM rule)
- [ ] Backup password chosen
- [ ] Laptop charged, stable Wi-Fi

---



## 2. 6:00 PM: launch both VMs



### 2.1 Confirm the lease is active

**Reservations → Leases**. `AGENTQO` should show **ACTIVE**. If it still says PENDING, wait a minute and refresh.

### 2.2 Launch the instances

**Compute → Instances → Launch Instance.** Fill in each tab:

**Details**

- Instance Name: `agentqo`
- Count: **2**
- If a **Reservation** field appears, select **AGENTQO**.

**Source**

- Select Boot Source: **Image**
- Find `CC-Ubuntu24.04-CUDA` and click its **↑** arrow so it moves to "Allocated".
- If asked about a volume, choose **No** for "Create New Volume" (the flavor's 40 GB disk is used).

**Flavor**

- Choose the flavor **tied to your reservation**. Its name contains your reservation ID, `dfa3f9ae` (it may look like `reservation:dfa3f9ae-...`).
- Do **not** pick the plain `g1.h100.pci.1`; that one is not linked to your lease and will fail.

**Networks**

- Allocate `sharednet1`.

**Security Groups**

- Keep `default`. Add `agentqo-ssh` if you created it.

**Key Pair**

- Select `agentqo-user`.

**Configuration (backup login, recommended)**
In "Customization Script", paste, using your own password:

```
#cloud-config
chpasswd:
  expire: false
  list: |
    cc:<YOUR-BACKUP-PASSWORD>
```

Click **Launch Instance**. VMs usually reach **Active** within a few minutes.

### 2.3 Identify the two VMs

With Count 2, the instances are named something like `agentqo-1` and `agentqo-2`.

- **VM-A =** `agentqo-1`: runs AgentQO and the small model, gets the floating IP.
- **VM-B =** `agentqo-2`: runs the large model, private network only.

Write down **VM-B's private IP** from the IP Address column (it usually starts with `10.`):

```
VM-B PRIVATE IP = ______________________
```

---



## 3. Floating IP and SSH



### 3.1 Get a floating IP for VM-A

1. **Network → Floating IPs → Allocate IP to Project** → Pool: the default public pool → **Allocate IP**.
2. In the new row, click **Associate** → Port: `agentqo-1` → **Associate**.

```
VM-A FLOATING IP = ______________________
```

**If allocation fails** (no IPs available): open **Compute → Instances →** `agentqo-1` **→ Console**, log in as `cc` with your backup password, and work from there. Retry "Allocate IP to Project" every 15 minutes; switch to SSH once it succeeds. Everything below also works in the console, just less comfortably.

### 3.2 Set up SSH shortcuts on your Mac

Open `~/.ssh/config` in a text editor (create it if it doesn't exist) and add:

```
Host agentqo-a
    HostName <VM-A FLOATING IP>
    User cc
    IdentityFile ~/.ssh/agentqo-user.pem
    ServerAliveInterval 60

Host agentqo-b
    HostName <VM-B PRIVATE IP>
    User cc
    IdentityFile ~/.ssh/agentqo-user.pem
    ProxyJump agentqo-a
    ServerAliveInterval 60
```

Now you can connect with:

```bash
ssh agentqo-a          # VM-A directly
ssh agentqo-b          # VM-B, hopping through VM-A automatically
```

Type `yes` the first time each one asks about a host fingerprint. `ServerAliveInterval` keeps the connection from dropping when idle.

### 3.3 Working with two terminals

Open **two Terminal windows** on your Mac: one connected to `agentqo-a`, one to `agentqo-b`. Label them mentally; most mistakes tonight would come from typing a command into the wrong VM.

### 3.4 One command to copy results to your Mac

Results only exist on VM-A until you copy them, and if the lease ends or the VM dies, they're gone. Set up `agentqo-sync` once now, then run it **after every test** (each test section below has a **📥 Copy home** step).

On your **Mac**, in a normal Terminal (not an SSH session), paste this once:

```bash
cat >> ~/.zshrc <<'EOF'
agentqo-sync() {
  local D=~/AgentQO   # results land in the repo's data/ and logs/, same layout as on VM-A
  mkdir -p "$D/logs" "$D/data/vllm" "$D/data/placement" "$D/data/cache" || return 1
  # snapshot the cache with SQLite's backup API: a plain copy of a file mid-write can be corrupt
  ssh agentqo-a 'cd ~/AgentQO || exit 1
    mkdir -p logs data/vllm data/placement
    rm -f /tmp/vllm_snapshot.sqlite
    if [ -f data/cache/vllm.sqlite ]; then
      python3 -c "import sqlite3; sqlite3.connect(\"data/cache/vllm.sqlite\").backup(sqlite3.connect(\"/tmp/vllm_snapshot.sqlite\"))" || exit 1
    fi' || { echo "agentqo-sync: FAILED (VM-A unreachable or ~/AgentQO missing)"; return 1; }
  rsync -az agentqo-a:AgentQO/logs/           "$D/logs/"           &&
  rsync -az agentqo-a:AgentQO/data/vllm/      "$D/data/vllm/"      &&
  rsync -az agentqo-a:AgentQO/data/placement/ "$D/data/placement/" || { echo "agentqo-sync: FAILED during rsync"; return 1; }
  if ssh agentqo-a 'test -f /tmp/vllm_snapshot.sqlite'; then
    rsync -az agentqo-a:/tmp/vllm_snapshot.sqlite "$D/data/cache/vllm.sqlite" || { echo "agentqo-sync: FAILED copying cache"; return 1; }
  fi
  echo "agentqo-sync $(date +%H:%M): $(ls "$D"/logs/c[0-9]*.txt | wc -l | tr -d ' ') Chameleon logs in $D/logs, cache $(du -h "$D/data/cache/vllm.sqlite" 2>/dev/null | cut -f1)"
}
EOF
source ~/.zshrc
```

What it does:

- Copies `logs/`, `data/vllm/`, `data/placement/` and a safe snapshot of `vllm.sqlite` from VM-A into the same places in your Mac's repo: `~/AgentQO/logs/`, `~/AgentQO/data/vllm/`, `~/AgentQO/data/placement/` and `~/AgentQO/data/cache/vllm.sqlite`. Your existing laptop logs and data there are left alone; tonight's logs are the `c01`–`c11` files.
- Only adds and updates files. It never deletes anything on your Mac, so re-running it is always safe.
- Prints `FAILED` and stops if anything goes wrong. A good run ends with a line like `agentqo-sync 21:05: 4 logs, 12M total in ...`.

It only works after Section 5.4 has created `~/AgentQO` on VM-A; before that it prints `FAILED`.

> Every test section below ends with **📥 Copy home**: switch to your Mac terminal and run `agentqo-sync`. Do it before you look at the results, so that whatever happens next, they're already safe.

---



## 4. First checks on both VMs

Run these on **both** VMs:

```bash
nvidia-smi                       # 1 x H100, about 94 GB memory
df -h / /dev/shm                 # / is about 40 GB; /dev/shm is a large RAM disk
free -h                          # about 250 GB RAM
python3 --version
curl -sI https://pypi.org | head -1      # internet access: should print HTTP/2 200 or similar
```


| Check           | Expected                   | If not                                     |
| --------------- | -------------------------- | ------------------------------------------ |
| `nvidia-smi`    | One H100, ~94 GB           | Wrong image or flavor; see Troubleshooting |
| `/dev/shm` size | Large (tens of GB or more) | Tell me; we'll put models elsewhere        |
| `curl pypi.org` | An HTTP status line        | VM has no internet; see Troubleshooting    |


**Why** `/dev/shm` **matters.** The disk is only 40 GB. The CUDA image, vLLM and PyTorch take about 20 GB, and the two models about 18 GB more, which is too tight. `/dev/shm` is a RAM disk backed by the VM's 250 GB of memory, so the models will be stored there. It's wiped when the VM is deleted, which is fine.

---



## 5. Install the software

Do Sections 5.1 and 5.2 on **both** VMs at the same time, then 5.3 or 5.4 on the matching VM.

### 5.1 tmux, so work survives disconnects

```bash
sudo apt-get update && sudo apt-get install -y tmux git python3-venv
tmux new -s agentqo
```

Everything from here on runs **inside tmux**. If your Mac sleeps or Wi-Fi drops, the work keeps running.


| Action                    | Keys                                        |
| ------------------------- | ------------------------------------------- |
| Detach (leave it running) | `Ctrl+b`, then `d`                          |
| Reattach                  | `tmux attach -t agentqo`                    |
| New window                | `Ctrl+b`, then `c`                          |
| Next / previous window    | `Ctrl+b`, then `n` / `p`                    |
| Go to window 0, 1, 2…     | `Ctrl+b`, then the number                   |
| Scroll up through output  | `Ctrl+b`, then `[`; arrow keys; `q` to exit |




### 5.2 Python environment (both VMs)

```bash
cat > ~/env.sh <<'EOF'
export HF_HOME=/dev/shm/hf
export PIP_NO_CACHE_DIR=1
source ~/venv/bin/activate
EOF

python3 -m venv ~/venv
source ~/env.sh
pip install --upgrade pip
```

> Every new tmux window starts **without** this environment. Always begin a new window with `source ~/env.sh`.



> **Don't run plain `pip install vllm`.** The default PyPI wheel (vLLM 0.32.0) pulls `torch 2.13.0+cu130`, which needs a CUDA 13 driver. The `CC-Ubuntu24.04-CUDA` image ships driver 560.35.05 (CUDA 12.6). `torch.cuda.is_available()` still prints `True`, but every GPU operation fails with `The NVIDIA driver on your system is too old (found version 12060)`. Use the CUDA 12.9 build below instead; it runs on the 12.6 driver. It was verified on these VMs on Oct 23.
>
> **Then remove `torchcodec`.** The cu129 vLLM wheel still pulls `torchcodec 0.17.0` from PyPI, which is CUDA 13 only (no cu129 build of 0.17 exists). `vllm serve` crashes at startup with `OSError: Could not load this library: .../libtorchcodec_image.so` (`libnvrtc.so.13` missing). torchcodec is only used for audio and video input. Once it's uninstalled, vLLM skips it cleanly, and both text models serve normally (verified Oct 23).

### 5.3 VM-B: vLLM only

```bash
pip install https://wheels.vllm.ai/5df63a7203cdb9328d824a27b682e77c7b9928be/vllm-0.32.0%2Bcu129-cp38-abi3-manylinux_2_28_x86_64.whl \
  --extra-index-url https://download.pytorch.org/whl/cu129
pip uninstall -y torchcodec           # its PyPI build is CUDA 13 only and crashes `vllm serve`; not needed for text models
python -c "import vllm, torch; print('vllm', vllm.__version__, 'torch', torch.__version__)"
python -c "import torch; x=torch.randn(4096,4096,device='cuda',dtype=torch.bfloat16); print('GPU matmul ok:', (x@x).float().sum().isfinite().item())"
```

The output should show `torch 2.13.0+cu129` and `GPU matmul ok: True`. Don't rely on `torch.cuda.is_available()`: it says `True` even when the GPU is unusable.

### 5.4 VM-A: AgentQO code and vLLM

```bash
git clone https://github.com/Shusmoy108/AgentQO.git ~/AgentQO
cd ~/AgentQO
git log --oneline | head -3           # should show your latest commit from Section 1.1
pip install https://wheels.vllm.ai/5df63a7203cdb9328d824a27b682e77c7b9928be/vllm-0.32.0%2Bcu129-cp38-abi3-manylinux_2_28_x86_64.whl \
  --extra-index-url https://download.pytorch.org/whl/cu129     # CUDA 12.9 build; see the note above 5.3
pip uninstall -y torchcodec           # see the note above 5.3
pip install -e ".[dev,viz]"
python -c "import vllm, torch; print('vllm', vllm.__version__, 'torch', torch.__version__)"
python -c "import torch; x=torch.randn(4096,4096,device='cuda',dtype=torch.bfloat16); print('GPU matmul ok:', (x@x).float().sum().isfinite().item())"
python -m pytest tests/ -q
ls scripts/placement_test.py scripts/run_real_h3.py scripts/verifier_analysis.py
grep -n "passthrough" agentqo/tasks/prompts.py | head -3
```

The last two lines confirm that tonight's scripts and the passthrough verifier mode are present. If either is missing, the push in Section 1.1 didn't go through.

Installing vLLM downloads several gigabytes and takes 5 to 15 minutes. That's normal.

---



## 6. Start the model servers

Each server runs in its own tmux window and keeps running all night. The first start of each model downloads it (about 3 GB for the 1.5B model, 15 GB for the 7B), so allow 5 to 10 minutes.

### 6.1 VM-B, window 0: the large model

```bash
source ~/env.sh
vllm serve Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 8002 \
  --max-model-len 4096 --gpu-memory-utilization 0.85
```

`--host 0.0.0.0` makes it reachable from VM-A over the private network. VM-B has no public IP, so it isn't exposed to the internet.

### 6.2 VM-A, window 0: the small model

```bash
source ~/env.sh
vllm serve Qwen/Qwen2.5-1.5B-Instruct --host 127.0.0.1 --port 8001 \
  --max-model-len 4096 --gpu-memory-utilization 0.25
```

`--host 127.0.0.1` keeps it local to VM-A, which does have a public IP. The memory cap of 0.25 leaves room on this GPU for a second copy of the large model during the placement test (Section 8).

A server is ready when its log shows it is running, typically a line like `Uvicorn running on http://...:8001`.

### 6.3 Check both servers from VM-A

On VM-A, open a new window (`Ctrl+b c`):

```bash
source ~/env.sh && cd ~/AgentQO
VMB=<VM-B PRIVATE IP>

curl -s http://localhost:8001/v1/models | head -c 200; echo
curl -s http://$VMB:8002/v1/models | head -c 200; echo
curl -s http://$VMB:8002/v1/completions -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen2.5-7B-Instruct","prompt":"2+2=","max_tokens":5,"logprobs":1}' | head -c 400; echo
```

**Expected:** both model names appear, and the last response contains a `logprobs` field (needed for the confidence measurements).

**If the VM-B lines hang or say "connection refused":**

1. Check VM-B's server window: is it still loading, or did it crash?
2. If it's running, the security group is blocking port 8002. Go to **Network → Security Groups → default → Manage Rules → Add Rule**: Custom TCP, Port **8002**, Remote **Security Group** = **default**. Retry.



### 6.4 Point AgentQO at both GPUs

On VM-A, replacing `<VM-B PRIVATE IP>`:

```bash
cat >> ~/env.sh <<'EOF'
cd ~/AgentQO
export VMB=<VM-B PRIVATE IP>
export VLLM_ENDPOINTS="{\"small\":\"http://localhost:8001\",\"large\":\"http://$VMB:8002\"}"
export VLLM_SMALL_MODEL="Qwen/Qwen2.5-1.5B-Instruct"
export VLLM_LARGE_MODEL="Qwen/Qwen2.5-7B-Instruct"
mkdir -p logs
EOF

source ~/env.sh
echo $VLLM_ENDPOINTS
```

The `echo` should print something like `{"small":"http://localhost:8001","large":"http://10.x.x.x:8002"}`.

---



## 7. Smoke test and timing

On VM-A, in a free tmux window, after `source ~/env.sh`.

### 7.1 C1: smoke test

```bash
python scripts/run_real_pipeline.py --backend vllm --stage smoke --n-tasks 3 \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/smoke 2>&1 | tee logs/c01_smoke.txt
```

**📥 Copy home** (Mac terminal): `agentqo-sync`

**Check, as you did on the laptop:**

- every output text starts with `PLAN:`
- `conf_src=logprobs`
- `cache_hit_on_rerun=True` and `same_text=True`
- latencies are far lower than on the laptop (expect well under a second for small)

If anything differs, stop and send me the log before going further.

### 7.2 C2: timed run

```bash
( time python scripts/run_real_pipeline.py --backend vllm --stage h1 --n-tasks 10 --workflows math \
  --workers 16 --max-tokens 256 --k 3 --corruptions 2 \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/h1_math_n10 ) 2>&1 | tee logs/c02_h1_n10.txt
```

The `( ... ) 2>&1` around `time` matters: without it, the `real`/`user`/`sys` lines print only to the terminal and never reach the log.

**📥 Copy home** (Mac terminal): `agentqo-sync`

**Write down the** `real` **time** at the end:

```
C2 time for 10 problems (math) = __________
```

**Estimate:** the overnight H1 run (C7) labels 100 problems on two workflows, so roughly **20 times** this number. If that's more than about 6 hours, tell me and we'll trim the overnight plan.

Also look at the result itself: `baseline_acc` should be between 0.2 and 0.8. Full-precision models may be more accurate than the 4-bit ones on your laptop; if baseline accuracy is above 0.85, say so, since very high accuracy weakens the criticality measurements.

---



## 8. The multi-GPU placement test (H4)



### 8.1 What it measures

**H4** claims that calls sharing a GPU slow each other down, and that a model of this interference helps scheduling. The placement test is the first real-hardware measurement of it. It sends a mix of small-model and large-model requests at increasing concurrency (1, 4, 16 and 32 at a time) and records each request's latency, under two placements:


| Placement     | Small model  | Large model                   |
| ------------- | ------------ | ----------------------------- |
| **split**     | GPU 1 (VM-A) | GPU 2 (VM-B)                  |
| **colocated** | GPU 1 (VM-A) | GPU 1 (VM-A), a second server |


Each placement runs twice: with ordinary prompts, and with `--shared-prefix`, where all prompts share a long common beginning. That tests whether shared prefixes soften the interference.

**Run this before the overnight chain,** because it needs the GPUs otherwise idle. Each run takes a few minutes.

### 8.2 C3 and C4: split placement

On VM-A:

```bash
source ~/env.sh

python scripts/placement_test.py --config split \
  --small-url http://localhost:8001 --large-url http://$VMB:8002 \
  2>&1 | tee logs/c03_place_split.txt

python scripts/placement_test.py --config split --shared-prefix \
  --small-url http://localhost:8001 --large-url http://$VMB:8002 \
  2>&1 | tee logs/c04_place_split_prefix.txt
```

**📥 Copy home** (Mac terminal): `agentqo-sync`. This copies C3, C4 and their CSVs in `data/placement/`.



### 8.3 C5 and C6: colocated placement

Start a **second copy of the large model on VM-A** in a new window (`Ctrl+b c`):

```bash
source ~/env.sh
vllm serve Qwen/Qwen2.5-7B-Instruct --host 127.0.0.1 --port 8003 \
  --max-model-len 4096 --gpu-memory-utilization 0.55
```

Wait until it's running (it reuses the downloaded model from `/dev/shm`, so it starts faster), then in your experiment window:

```bash
curl -s http://localhost:8003/v1/models | head -c 200; echo

python scripts/placement_test.py --config colocated \
  --small-url http://localhost:8001 --large-url http://localhost:8003 \
  2>&1 | tee logs/c05_place_coloc.txt

python scripts/placement_test.py --config colocated --shared-prefix \
  --small-url http://localhost:8001 --large-url http://localhost:8003 \
  2>&1 | tee logs/c06_place_coloc_prefix.txt
```

**📥 Copy home** (Mac terminal): `agentqo-sync`. This copies C5, C6 and their CSVs.



### 8.4 Stop the extra server

Go to the port-8003 window and press `Ctrl+c`. This frees GPU 1's memory so the overnight runs aren't slowed down. Check with `nvidia-smi` that only the small model's memory is in use on VM-A.

### 8.5 What to look at

Each run prints a table like:

```
 conc  model    n    p50 s    p95 s   mean s    tok/s
    1  small   32     0.40     0.45     0.41    ...
   32  small   32     1.90     2.60     2.00    ...
```

- **p50 / p95:** median and 95th-percentile latency of each request, in seconds.
- **tok/s:** generated tokens per second for that model, a throughput measure.

Compare **split vs. colocated** for the **small** model at concurrency 16 and 32. If colocated small-model latency is clearly higher, the large model's calls are imposing a cost on their GPU neighbors, which is the effect H4 is about. Compare the `prefix` runs with the plain ones to see whether shared prefixes reduce the effect. Results are also saved as CSV files in `data/placement/`.

---



## 9. The overnight chain (H1, repair test, H3)



### 9.1 Start it (around 8:30 PM)

On VM-A, in a fresh tmux window:

```bash
source ~/env.sh
set -o pipefail     # without this, `cmd | tee log && next` ignores cmd failing (it checks tee's exit code)

python scripts/run_real_pipeline.py --backend vllm --stage h1 --n-tasks 100 --workflows math,sc \
  --workers 16 --max-tokens 256 --k 3 --corruptions 2 \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/h1_n100 2>&1 | tee logs/c07_h1_n100.txt && \
AGENTQO_VERIFIER=passthrough python scripts/run_real_pipeline.py --backend vllm --stage h1 --n-tasks 100 \
  --workflows math --workers 16 --max-tokens 256 --k 3 --corruptions 2 \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/h1_math_passthrough_n100 2>&1 | tee logs/c08_h1_passthrough.txt && \
AGENTQO_VERIFIER=passthrough python scripts/run_real_h3.py --backend vllm --split eval --n-tasks 200 \
  --h1-summary data/vllm/h1_math_passthrough_n100/h1/math_reasoning_s3_ver/h1_summary.json \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/h3_eval_n200 2>&1 | tee logs/c09_h3_eval200.txt
```

The `&&` between steps means each one starts only if the previous one finished without error. That only works with `set -o pipefail`; otherwise `&&` checks `tee`'s exit code, which is always 0.

### 9.2 What each step does


| Step | Log                      | Experiment                                                           | What it answers                                                                                                            |
| ---- | ------------------------ | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| C7   | `c07_h1_n100.txt`        | H1 on math and self-consistency, 100 dev problems, original verifier | Do the laptop criticality profiles (verifier dominates in math; fair samplers in SC) replicate with full-precision models? |
| C8   | `c08_h1_passthrough.txt` | Same math workflow, verifier replaced by code                        | Does removing the repair step restore the structural ordering at scale? Mostly cached, so fast                             |
| C9   | `c09_h3_eval200.txt`     | H3 on 200 eval problems: all plans incl. `ec_top2` and `struct_top2` | Does the criticality-chosen pair still beat the structural pair at equal cost?                                             |




### 9.3 Leave it running

1. Watch the first few minutes to make sure C7 starts properly (you should see a progress bar for `math_reasoning_s3_ver`).
2. Detach with `Ctrl+b d`.
3. **📥 Auto copy home overnight.** C7 to C9 run for hours, so let your Mac copy results every 15 minutes. In a **new Mac Terminal tab** (leave it open):

   ```bash
   caffeinate -i zsh -ic 'while true; do agentqo-sync; sleep 900; done'
   ```

   `caffeinate -i` stops the Mac from sleeping while it's idle. Leave the laptop **open and plugged in**: closing the lid still puts most Macs to sleep, and a sleeping Mac copies nothing. (VM-A can't push to your Mac, because the Mac has no public address, so the Mac has to pull.) If the Mac does sleep, nothing is lost: the results stay on VM-A, and the loop catches up when the Mac wakes. Stop the loop with `Ctrl+c` in that tab.
4. The chain keeps running on VM-A, and the model servers keep running on both VMs.



### 9.4 Checking on it (from anywhere)

```bash
ssh agentqo-a
tail -n 15 ~/AgentQO/logs/c07_h1_n100.txt        # or c08 / c09
tmux attach -t agentqo                            # to see the live windows; Ctrl+b d to leave
watch -n 5 nvidia-smi                             # GPU busy? Ctrl+c to stop watching
```

If the auto-copy loop from 9.3 isn't running, run `agentqo-sync` on your Mac whenever you check in.

---



## 10. Saturday morning: check and analyze



### 10.1 Where is the chain?

```bash
ssh agentqo-a
cd ~/AgentQO && ls logs/
tail -n 25 logs/c07_h1_n100.txt
tail -n 25 logs/c08_h1_passthrough.txt
tail -n 30 logs/c09_h3_eval200.txt
```

**📥 Copy home first** (Mac terminal): `agentqo-sync`. This saves whatever the chain produced overnight before you do anything else.

- **C7 and C8 finished, C9 finished:** go to 10.2.
- **C9 still running:** that's expected; the H3 script runs one problem at a time. Let it continue until about **1:30 PM**. If it hasn't finished by then, stop it (`Ctrl+c` in its window). The finished plans' results are still in the log, and every generation is in the cache for next time.
- **A step failed:** the chain stops there. Copy the error and send it to me.



### 10.2 C10 and C11: the analyses (after C8 and C9)

```bash
source ~/env.sh

python scripts/verifier_analysis.py data/vllm/h1_n100 data/vllm/h1_math_passthrough_n100 \
  | tee logs/c10_verifier.txt

python -c "
import json, numpy as np
t = json.load(open('data/vllm/h3_eval_n200/h3_traces.json'))
a = np.array([x['correct'] for x in t['ec_top2']]); b = np.array([x['correct'] for x in t['struct_top2']])
d = a - b; rng = np.random.default_rng(0)
m = d[rng.integers(0, len(d), (5000, len(d)))].mean(1)
print(f'ec_top2 - struct_top2 = {d.mean():+.3f}  95% CI [{np.percentile(m,2.5):+.3f}, {np.percentile(m,97.5):+.3f}]  ({int((d>0).sum())} wins, {int((d<0).sum())} losses)')
" | tee logs/c11_ec_vs_struct.txt
```

(C11 needs C9 to have finished. If you stopped C9 early, skip C11.)

**📥 Copy home** (Mac terminal): `agentqo-sync`. This copies C10 and C11.

### 10.3 What to look for


| Log        | Key question                                                     | Laptop result to compare against          |
| ---------- | ---------------------------------------------------------------- | ----------------------------------------- |
| c07 (math) | Is the verifier still the most critical node?                    | verifier +0.35, planner and steps about 0 |
| c07 (SC)   | Are the three samplers roughly equal (fair tie-break)?           | each about 0.30 to 0.43                   |
| c08        | Do upstream nodes become critical without repair?                | planner +0.33, step 1 +0.28, …            |
| c09        | Share of gain and cost for `ec_top2`; how `struct_top2` compares | 52% of gain for 40% of cost               |
| c11        | Is `ec_top2 − struct_top2` positive with an interval above 0?    | +0.26 [+0.14, +0.38]                      |
| c03 to c06 | Does colocation slow the small model at high concurrency?        | (first real measurement)                  |


---



## 11. Copy results home and shut down

**Start this by 2:00 PM Saturday.** The lease ends at 3:00 PM, and when it ends, the VMs and everything on them are gone.

### 11.1 Copy everything to your Mac

Most results are already home from the 📥 steps. Do one final copy after the last run has stopped. On your **Mac** (a normal Terminal, not an SSH session), stop the overnight loop tab with `Ctrl+c` if it's still running, then:

```bash
agentqo-sync
cd ~/AgentQO
ls logs/c* data/vllm/ data/placement/
ls -lh data/cache/vllm.sqlite
sqlite3 data/cache/vllm.sqlite 'PRAGMA integrity_check;'     # must print: ok
```

Compare `ls logs/c*` with the log table in Section 13. Every log that exists on VM-A should be here.

**Keep** `vllm.sqlite` **safe.** It holds every generation from tonight. Next session, copy it back to the new VM before running anything, and none of tonight's generations will be paid for again:

```bash
# next session, after cloning the repo on the new VM:
ssh <NEW-VM> "mkdir -p ~/AgentQO/data/cache"
rsync -avz ~/AgentQO/data/cache/vllm.sqlite <NEW-VM>:~/AgentQO/data/cache/
```

If you changed any code on VM-A, commit and push it from there before shutting down, or it's lost.

### 11.2 Shut down, in this order

1. **Stop the servers:** in each server window on both VMs, press `Ctrl+c`. Then `exit` the tmux sessions and SSH connections.
2. **Delete both instances:** **Compute → Instances** → tick `agentqo-1` and `agentqo-2` → **Delete Instances** → confirm.
3. **Release the floating IP:** **Network → Floating IPs** → **Disassociate** (if still associated) → then **Release Floating IP**.
4. **End the lease early (if you're done before 3 PM):** **Reservations → Leases** → `AGENTQO` → **Delete Lease**.

> Deleting the instances alone doesn't end the lease. The lease is what holds the GPUs, so delete it too once your results are safely home.



### 11.3 Record what you used

After the session, check your project's SU usage on the Chameleon dashboard and add a line to `RESULTS.md`:


| Date       | Site / flavor               | Hours | SU used | Cumulative | What ran  |
| ---------- | --------------------------- | ----- | ------- | ---------- | --------- |
| 2026-10-23 | KVM@TACC / 2× g1.h100.pci.1 |       |         |            | C1 to C11 |


This tells us the real cost per hour, for planning the next sessions within your 1,000 SU budget.

### 11.4 Send me

The `logs/` folder, at least: `c01`, `c02`, `c03` to `c06`, `c07`, `c08`, `c09`, `c10`, `c11`. I'll analyze them and update the report.

---



## 12. Troubleshooting


| Problem                                            | Likely cause                                   | Fix                                                                               |
| -------------------------------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------- |
| Lease still PENDING after 6 PM                     | Page not refreshed                             | Refresh; times are UTC (23:00 = 6 PM Chicago)                                     |
| No flavor containing `dfa3f9ae` in Launch Instance | Lease not active yet, or wrong site            | Wait for ACTIVE; make sure you're in **KVM@TACC**                                 |
| "No valid host was found"                          | Plain `g1.h100.pci.1` chosen, or count above 2 | Use the reservation's flavor; Count ≤ 2                                           |
| Instance in **Error**                              | Launch problem                                 | Delete it and launch again with the same settings                                 |
| Can't allocate a floating IP                       | Site out of public IPs                         | Use the Console with your backup password; retry periodically                     |
| `ssh: Connection timed out`                        | No SSH rule, or IP not associated              | Add the SSH security group (1.3); check the association                           |
| `Permission denied (publickey)`                    | Wrong user or key                              | User is `cc`; check the `.pem` path and `chmod 600`                               |
| `REMOTE HOST IDENTIFICATION HAS CHANGED`           | IP reused from another VM                      | `ssh-keygen -R <IP>` on your Mac, then retry                                      |
| `ssh agentqo-b` fails                              | VM-A unreachable, or wrong private IP          | Check `ssh agentqo-a` first; recheck VM-B's IP on the Instances page              |
| `nvidia-smi` not found                             | Wrong image                                    | Relaunch with `CC-Ubuntu24.04-CUDA`                                               |
| VM-B can't reach the internet                      | No outbound route on that VM                   | Tell me; we'll copy what's needed through VM-A                                    |
| `pip install vllm` fails                           | Version mismatch                               | Copy the error to me; usually fixed by pinning a version                          |
| Disk full                                          | Models or caches on `/`                        | `echo $HF_HOME` must show `/dev/shm/hf`; `pip cache purge`; `du -sh ~/* ~/.cache` |
| vLLM: CUDA out of memory                           | Too much memory requested on VM-A              | Stop the port-8003 server; or lower `--gpu-memory-utilization`                    |
| VM-A can't reach `VMB:8002`                        | Security group                                 | Add rule: TCP 8002 from security group `default`                                  |
| Pipeline error about logprobs                      | Server not returning them                      | Recheck the logprobs `curl` in 6.3                                                |
| Chain stopped partway                              | A step errored (because of `&&`)               | `tail -n 40` that step's log; send me the error                                   |
| `agentqo-sync: command not found`                  | Function not loaded in this terminal           | `source ~/.zshrc` (or redo 3.4)                                                   |
| `agentqo-sync: FAILED (... ~/AgentQO missing)`     | Before 5.4, or VM-A unreachable                | Check `ssh agentqo-a` works and `~/AgentQO` exists on VM-A                         |
| Run much slower than expected                      | GPU idle or a server down                      | `watch nvidia-smi`; check both server windows                                     |
| Running out of time Saturday                       | H3 is slow                                     | Stop at 1:30 PM; copy results; everything is cached for next time                 |


If something isn't in this table, copy the **exact error text** and send it to me.

---



## 13. Quick reference



### Addresses

```
VM-A floating IP : ______________________   (ssh agentqo-a)
VM-B private IP  : ______________________   (ssh agentqo-b)
```



### Ports


| Port | VM   | Model                            | Reachable from                  |
| ---- | ---- | -------------------------------- | ------------------------------- |
| 8001 | VM-A | Qwen2.5-1.5B (small)             | VM-A only                       |
| 8002 | VM-B | Qwen2.5-7B (large)               | VM-A over the private network   |
| 8003 | VM-A | Qwen2.5-7B (colocated test only) | VM-A only; stop after Section 8 |




### Time conversion (Chicago → UTC, add 5 hours)


| Chicago     | UTC                    |
| ----------- | ---------------------- |
| Fri 6:00 PM | Fri 23:00              |
| Fri 8:30 PM | Sat 01:30              |
| Sat 9:00 AM | Sat 14:00              |
| Sat 2:00 PM | Sat 19:00              |
| Sat 3:00 PM | Sat 20:00 (lease ends) |




### Every new tmux window on VM-A

```bash
source ~/env.sh
```



### Log files tonight


| Log                          | Experiment                           |
| ---------------------------- | ------------------------------------ |
| `c01_smoke.txt`              | Smoke test                           |
| `c02_h1_n10.txt`             | Timed 10-problem run                 |
| `c03_place_split.txt`        | Placement: split                     |
| `c04_place_split_prefix.txt` | Placement: split, shared prefix      |
| `c05_place_coloc.txt`        | Placement: colocated                 |
| `c06_place_coloc_prefix.txt` | Placement: colocated, shared prefix  |
| `c07_h1_n100.txt`            | H1, 100 dev problems                 |
| `c08_h1_passthrough.txt`     | H1, passthrough verifier             |
| `c09_h3_eval200.txt`         | H3, 200 eval problems                |
| `c10_verifier.txt`           | Verifier change analysis             |
| `c11_ec_vs_struct.txt`       | Criticality pair vs. structural pair |




### Before you leave on Saturday

- [ ] Final `agentqo-sync` done; all logs, `data/vllm/`, `data/placement/` and `vllm.sqlite` on your Mac; `integrity_check` says `ok`
- [ ] Any code changes pushed
- [ ] Servers stopped
- [ ] Both instances deleted
- [ ] Floating IP released
- [ ] Lease deleted (or let it end at 3 PM)
- [ ] SU usage recorded

---

**About cost:** the lease holds two H100 GPUs for 21 hours, about 42 GPU-hours. Keeping the overnight chain running makes good use of them. Delete the lease as soon as your results are home if you finish before 3 PM.