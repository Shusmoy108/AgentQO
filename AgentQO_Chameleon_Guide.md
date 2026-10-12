# Running AgentQO on Chameleon Cloud: A Beginner's Guide

**For:** Shusmoy Chowdhury, first time on Chameleon
**Goal:** run the AgentQO real-model experiments (H1 and H3) on a GPU node with vLLM, copy the results home, and stop paying for the node as soon as you are done.

Read Part 1 once before you start. It explains the handful of ideas that the rest of the guide assumes. Then work through Parts 2 to 9 in order the first time. After that, Part 10 is a one-page checklist for every later session.

> Chameleon's web interface changes from time to time. If a button or menu name below does not match exactly, look for the closest equivalent. The official getting-started guide is linked at the end.

---

## Part 0: Before you touch Chameleon

Do these on your laptop first. Skipping them is the most common way to waste GPU hours.

### 0.1 Get the go-ahead

The allocation belongs to Dr. Liu's project (**CHI-251518**). Send him the update and agree on the plan before reserving anything.

### 0.2 Push all your code changes to GitHub

Chameleon gets your code by cloning the repository, so anything that exists only on your laptop will be missing. Several important changes from the laptop work were made locally:

| File | Change |
|---|---|
| `agentqo/tasks/prompts.py` | hash-based tie-break in the vote, `import os`, the `judge` and `passthrough` verifier modes |
| `scripts/run_real_h3.py` | the H3 script (latest version, with `struct_top2`) |
| `scripts/verifier_analysis.py` | the verifier change analysis |

On your laptop:

```bash
cd ~/AgentQO
git status                      # see what's changed
python3 -m pytest tests/ -q     # make sure everything passes first
git add -A
git commit -m "Laptop results: tie-break fix, verifier modes, H3 and verifier scripts"
git push
```

Then check on github.com that the files are there. Do not commit the `data/` folder if it is large; it is normally ignored by `.gitignore` already.

### 0.3 Decide what this first session will do

For the first session, keep the goal small: **get vLLM running, pass the smoke test, and run one real experiment.** Do not try to run everything on day one.

### 0.4 Set a budget

You planned to use at most **1,000 SU** for the prototype phase. Keep a log from the very first lease (Part 9 shows a template). The most expensive mistake on Chameleon is not a slow experiment; it is a lease you forgot to end.

---

## Part 1: Chameleon in plain English

| Term | What it means for you |
|---|---|
| **Portal** | The website at chameleoncloud.org where you log in. |
| **Project** | The account that pays. You use Dr. Liu's project, CHI-251518. |
| **SU (service unit)** | The currency. Using a node costs SUs per hour. |
| **Site** | A physical data center. Bare-metal sites include **CHI@UC** (Chicago), **CHI@TACC** (Austin) and **CHI@NCAR** (Boulder). Each site has different hardware, and each has its own dashboard. |
| **Bare metal** | You get a whole physical machine, not a virtual one. Good for GPU work. |
| **Node type** | The kind of machine (for example a GPU node with A100s). You pick it when reserving. |
| **Lease (reservation)** | Your booking of a machine for a time window. **You must have a lease before you can start a machine.** Bare-metal leases can last up to 7 days. |
| **Instance** | The running machine itself, started inside your lease, from an operating system image. |
| **Image** | The operating system the machine boots. You want one with NVIDIA drivers already installed (the **CUDA** images). |
| **Key pair** | Your SSH key. Chameleon puts the public half on the machine so you can log in with the private half. |
| **Floating IP** | A public internet address you attach to your instance so you can SSH to it from your laptop. |
| **sharednet1** | The default network that gives your instance internet access. |
| **cc** | The username you log in with on Chameleon images. |

The life cycle of one session is always the same:

```
reserve (lease)  ->  start machine (instance)  ->  attach address (floating IP)
    ->  SSH in  ->  set up and run  ->  copy results home  ->  delete instance  ->  end lease
```

**The key cost rule:** a lease holds the machine for you whether or not you are using it. Plan your session, keep leases short, and end them as soon as you finish. (Confirm the exact charging rules for your project in the Chameleon FAQ or with the help desk; the safe habit is the same either way.)

---

## Part 2: Log in and check your project

1. Go to **chameleoncloud.org** and click **Log In**. Chameleon uses federated login, so you can sign in with your institution or another supported identity.
2. Open your **Dashboard** and check that project **CHI-251518** appears, with its allocation (you saw 8,000 SU allocated).
3. Click the **Experiment** tab in the top menu. It shows the sites. Picking a site opens that site's own dashboard.

The project and site appear in a dropdown at the top left, next to the Chameleon logo. If the project is missing there, it usually means you have not been added to it or it has no active allocation. Ask Dr. Liu to check your membership.

---

## Part 3: Create your SSH key (once)

You need this only the first time.

**Option A (recommended): use your laptop's existing key.**

On your Mac, check whether you already have one:

```bash
ls ~/.ssh/id_ed25519.pub ~/.ssh/id_rsa.pub 2>/dev/null
```

If neither exists, create one:

```bash
ssh-keygen -t ed25519 -C "shusmoy-chameleon"
```

Press Enter to accept the default location. Set a passphrase if you like. Then print the public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

In the site dashboard (for example CHI@UC), go to **Compute → Key Pairs → Import Public Key**, give it a name like `shusmoy-mac`, paste the line you just printed, and save.

> **Key pairs are stored per site.** If you later use a different site (say CHI@TACC), import the same public key there too.

**Option B: let Chameleon create the key.** In **Compute → Key Pairs → Create Key Pair**, it downloads a `.pem` file. Move it somewhere safe and lock its permissions:

```bash
mv ~/Downloads/your-key.pem ~/.ssh/
chmod 600 ~/.ssh/your-key.pem
```

You would then log in with `ssh -i ~/.ssh/your-key.pem ...`.

---

## Part 4: Choose a site and a GPU node type

### 4.1 What you need

The experiments serve two models: **Qwen2.5-1.5B-Instruct** (small) and **Qwen2.5-7B-Instruct** (large), unquantized through vLLM. The 7B model needs about 15 GB of GPU memory for its weights plus room for its cache.

- **Ideal:** a node with **two or more GPUs of 40 GB or more** (for example A100 40 GB or 80 GB). Each model then gets its own GPU, which is the simplest setup.
- **Fine:** a single GPU with **40 GB or more**. Both models share it (Part 6 shows how).
- **Workable but tight:** a single 24 GB GPU. Both models fit, but you must cap memory carefully.
- **Avoid for now:** fractional or virtual GPU flavors, and non-NVIDIA accelerators. They need different images and drivers.

Later, for larger models (for example a 70B-class model), you will need several large GPUs on one node. Do not start there.

### 4.2 Find what is available

1. Open the site dashboard (try **CHI@UC** first, then **CHI@TACC**).
2. Go to **Reservations → Leases → Host Calendar**.
3. Use the **Node Type** filter. GPU node types usually have names starting with `gpu_` (names you may see include ones with `a100`, `v100` or `rtx_6000` in them, but the list changes, so trust what the calendar shows).
4. The calendar shows which nodes are free and when.

If you are unsure what a node type contains, the **Hardware Discovery** tool on the Chameleon site lists each type's GPUs and memory.

GPU nodes are popular. If nothing suitable is free now, book ahead (Part 5 explains how) rather than settling for a GPU that is too small.

---

## Part 5: Make a lease

1. In the site dashboard: **Reservations → Leases → Host Calendar**.
2. Filter by your chosen GPU node type and click a free node's name. This opens **Create Lease** with that node selected.
3. Fill in the form:
   - **General tab:** a name such as `agentqo-h1-oct14`. For the start time, either *now* or a future slot. For the **first session, choose about 6 hours**. That is enough to set up, test and run one experiment. You can extend later.
   - **Hosts tab:** one host, already set by the calendar.
   - **Networks tab:** tick **Floating IP**. You need it to SSH in. Leave *Reserve Network* unticked.
4. Click **Create**.
5. The lease shows **PENDING**, then **ACTIVE** once its start time arrives. You can only start a machine when it is ACTIVE.

**If you need more time later:** in the Leases list, use **Update Lease** in the Actions column and add hours (within the 7-day limit). Do not create back-to-back leases to get around the limit; Chameleon discourages "lease stacking."

---

## Part 6: Start the machine and connect

### 6.1 Launch the instance

1. In the site dashboard: **Compute → Instances → Launch Instance**.
2. **Details:** name it (for example `agentqo-gpu`), and under **Reservation** pick your active lease. Count: 1.
3. **Source:** find the image **`CC-Ubuntu24.04-CUDA`** and click its up-arrow to select it. This image comes with NVIDIA drivers set up for GPU nodes. (`CC-Ubuntu22.04-CUDA` is the fallback if you hit trouble.)
4. **Networks:** select **sharednet1**.
5. **Key Pair:** select the key you imported in Part 3.
6. Click **Launch Instance**.

**Bare-metal machines take a while to start, often 10 to 20 minutes.** The status goes from *Build* to *Active*. This is normal. Do not launch a second one while you wait.

### 6.2 Attach the floating IP

1. **Network → Floating IPs.**
2. If there is a free IP, click **Associate** next to it, choose your instance, and confirm.
3. If there is none, click **Allocate IP to Project → Allocate IP**, then associate it.

Write down the IP address.

### 6.3 SSH in

From your Mac:

```bash
ssh cc@<FLOATING_IP>
```

(or `ssh -i ~/.ssh/your-key.pem cc@<FLOATING_IP>` if you used Option B in Part 3).

The first time, type `yes` to accept the host fingerprint. If it says *Connection refused* or times out, the machine may still be booting. Wait two or three minutes and try again.

### 6.4 First checks on the machine

```bash
nvidia-smi                     # should list your GPU(s) and memory
df -h ~                        # free disk space in your home directory
free -h                        # system memory
python3 --version
```

If `nvidia-smi` fails, stop here and see Troubleshooting (Part 11). Nothing else will work without it.

---

## Part 7: Set up the software (first time on each new machine)

> **A new instance starts clean every time.** Anything you install is lost when you delete the instance. That is why Part 8 saves results back to your laptop, and why this part is written as copy-paste blocks you can rerun.

### 7.1 Use tmux so work survives disconnects

If your Wi-Fi drops or you close the laptop, a normal SSH session dies and takes your running job with it. `tmux` keeps it alive on the server.

```bash
sudo apt-get update && sudo apt-get install -y tmux git python3-venv
tmux new -s agentqo
```

Inside tmux, the essentials:

| Action | Keys |
|---|---|
| Detach (leave it running, go back to plain SSH) | `Ctrl+b` then `d` |
| Reattach later | `tmux attach -t agentqo` |
| New window | `Ctrl+b` then `c` |
| Next / previous window | `Ctrl+b` then `n` / `p` |
| Go to window 0, 1, 2 | `Ctrl+b` then `0`, `1`, `2` |

You will use three windows: **0** for the small model server, **1** for the large model server, **2** for running experiments.

### 7.2 Get the code and a Python environment

In tmux window 0:

```bash
cd ~
git clone https://github.com/Shusmoy108/AgentQO.git
cd AgentQO
python3 -m venv ~/venv
source ~/venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev,viz]"
pip install vllm
python -m pytest tests/ -q          # should pass, same as on your laptop
```

Installing vLLM downloads several gigabytes and can take 5 to 15 minutes. That is normal.

> Every new tmux window starts without the environment. Run `source ~/venv/bin/activate && cd ~/AgentQO` at the top of each one.

### 7.3 Start the two model servers

The first start of each server downloads the model from Hugging Face (about 3 GB for 1.5B, about 15 GB for 7B), so allow 5 to 10 minutes.

**If the node has two or more GPUs (simplest):** put one model on each GPU.

Window 0 (small model):

```bash
source ~/venv/bin/activate
CUDA_VISIBLE_DEVICES=0 vllm serve Qwen/Qwen2.5-1.5B-Instruct --port 8001 --max-model-len 4096
```

Window 1 (`Ctrl+b c`, large model):

```bash
source ~/venv/bin/activate
CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen2.5-7B-Instruct --port 8002 --max-model-len 4096
```

**If the node has a single GPU:** both servers share it, so each must be told how much GPU memory it may take. vLLM grabs memory up front, so start the large model first.

Window 1 (large model, first):

```bash
source ~/venv/bin/activate
vllm serve Qwen/Qwen2.5-7B-Instruct --port 8002 --max-model-len 4096 --gpu-memory-utilization 0.55
```

Wait until it says the server is running, then in window 0:

```bash
source ~/venv/bin/activate
vllm serve Qwen/Qwen2.5-1.5B-Instruct --port 8001 --max-model-len 4096 --gpu-memory-utilization 0.25
```

On a 24 GB GPU, use about `0.65` and `0.25`. If a server fails with an out-of-memory error, lower its number slightly.

Each server is ready when its log shows that it is listening (something like `Uvicorn running on http://0.0.0.0:8002`).

### 7.4 Check that the servers answer, with logprobs

Open window 2 (`Ctrl+b c`):

```bash
source ~/venv/bin/activate && cd ~/AgentQO

curl -s http://localhost:8001/v1/models | head -c 300; echo
curl -s http://localhost:8002/v1/models | head -c 300; echo

curl -s http://localhost:8002/v1/completions -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen2.5-7B-Instruct","prompt":"2+2=","max_tokens":5,"logprobs":1}' | head -c 600; echo
```

You should see each model's name, and a short completion whose response includes a `logprobs` field. If the logprobs field is there, the confidence baseline will work exactly as it did with Ollama.

### 7.5 Point AgentQO at the servers

The pipeline reads these settings from the environment. In window 2:

```bash
export VLLM_ENDPOINTS='{"small":"http://localhost:8001","large":"http://localhost:8002"}'
export VLLM_SMALL_MODEL="Qwen/Qwen2.5-1.5B-Instruct"
export VLLM_LARGE_MODEL="Qwen/Qwen2.5-7B-Instruct"
mkdir -p logs
```

You can put these lines in a file to save typing later:

```bash
cat > ~/agentqo_env.sh <<'EOF'
source ~/venv/bin/activate
cd ~/AgentQO
export VLLM_ENDPOINTS='{"small":"http://localhost:8001","large":"http://localhost:8002"}'
export VLLM_SMALL_MODEL="Qwen/Qwen2.5-1.5B-Instruct"
export VLLM_LARGE_MODEL="Qwen/Qwen2.5-7B-Instruct"
mkdir -p logs
EOF
source ~/agentqo_env.sh
```

### 7.6 Smoke test

```bash
python scripts/run_real_pipeline.py --backend vllm --stage smoke --n-tasks 3 \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/smoke 2>&1 | tee logs/c01_smoke.txt
```

**What to check** (the same as your Ollama smoke test):

- Every line shows text that starts with `PLAN:`.
- `conf_src=logprobs` (real logprobs, not a fallback).
- `cache_hit_on_rerun=True` and `same_text=True`.
- Latency is much lower than on the laptop.

If all four look right, the setup works. **Write down the time** since the lease started; you now know your setup cost per session.

---

## Part 8: Run the experiments

Use a **new cache file** (`data/cache/vllm.sqlite`). The Ollama cache cannot be reused, because vLLM serves the full-precision models rather than Ollama's 4-bit versions, so every answer is generated fresh once.

vLLM handles many requests at once, so use more workers than on the laptop. Start with `--workers 16`.

The problem sets are fixed by the code: the **dev** split has 100 problems (used to measure criticality), the **eval** split has 200 (used for H3 on unseen problems).

### Before the long runs: time one small run

Run H1 on 10 problems first and note how long it takes. Multiply to estimate the bigger runs, and check that the estimate fits inside your lease. This is the single best habit for not running out of lease time mid-experiment.

```bash
time python scripts/run_real_pipeline.py --backend vllm --stage h1 --n-tasks 10 --workflows math \
  --workers 16 --max-tokens 256 --k 3 --corruptions 2 \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/h1_math_n10 2>&1 | tee logs/c02_h1_n10.txt
```

### Experiment C1: H1 on math with the repairing verifier (100 dev problems)

```bash
python scripts/run_real_pipeline.py --backend vllm --stage h1 --n-tasks 100 --workflows math,sc \
  --workers 16 --max-tokens 256 --k 3 --corruptions 2 \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/h1_n100 2>&1 | tee logs/c03_h1_n100.txt
```

### Experiment C2: H1 with the verifier as a passthrough (100 dev problems)

Almost free after C1, because upstream generations are cached and the passthrough is code.

```bash
AGENTQO_VERIFIER=passthrough python scripts/run_real_pipeline.py --backend vllm --stage h1 --n-tasks 100 \
  --workflows math --workers 16 --max-tokens 256 --k 3 --corruptions 2 \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/h1_math_passthrough_n100 2>&1 | tee logs/c04_h1_passthrough.txt

python scripts/verifier_analysis.py data/vllm/h1_n100 data/vllm/h1_math_passthrough_n100
```

### Experiment C3: H3 on 200 unseen problems (verifier passthrough)

Uses the criticality measured in C2 to choose `ec_top2`, then tests every plan, including `struct_top2`, on the eval split.

```bash
AGENTQO_VERIFIER=passthrough python scripts/run_real_h3.py --backend vllm --split eval --n-tasks 200 \
  --h1-summary data/vllm/h1_math_passthrough_n100/h1/math_reasoning_s3_ver/h1_summary.json \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/h3_eval_n200 2>&1 | tee logs/c05_h3_eval200.txt
```

Then the paired comparison:

```bash
python -c "
import json, numpy as np
t = json.load(open('data/vllm/h3_eval_n200/h3_traces.json'))
a = np.array([x['correct'] for x in t['ec_top2']]); b = np.array([x['correct'] for x in t['struct_top2']])
d = a - b; rng = np.random.default_rng(0)
m = d[rng.integers(0, len(d), (5000, len(d)))].mean(1)
print(f'ec_top2 - struct_top2 = {d.mean():+.3f}  95% CI [{np.percentile(m,2.5):+.3f}, {np.percentile(m,97.5):+.3f}]  ({int((d>0).sum())} wins, {int((d<0).sum())} losses)')
" | tee logs/c06_ec_vs_struct.txt
```

> Note: `run_real_h3.py` runs one problem at a time, so it does not benefit from many workers the way labeling does. If C3 is slow, tell me and I will add parallel execution.

### Experiment C4 (later session): more workflows for H2

```bash
python scripts/run_real_pipeline.py --backend vllm --stage h1 --n-tasks 100 --workflows complex \
  --workers 16 --max-tokens 256 --k 3 --corruptions 2 \
  --cache data/cache/vllm.sqlite --output-dir data/vllm/h1_complex_n100 2>&1 | tee logs/c07_h1_complex.txt
```

### While a run is going

- **Detach** with `Ctrl+b d`. You can close the laptop. The run continues.
- **Check on it later:** `ssh cc@<FLOATING_IP>` then `tmux attach -t agentqo`.
- **Watch the GPU:** `watch -n 2 nvidia-smi` (press `Ctrl+c` to stop watching).
- **Check the end of a log without attaching:** `tail -n 30 ~/AgentQO/logs/c03_h1_n100.txt`.

---

## Part 9: Save your results, then shut everything down

### 9.1 Copy results to your laptop

**Do this before deleting anything.** Everything on the instance disappears when it is deleted.

From your **Mac** (a new Terminal window, not the SSH session):

```bash
mkdir -p ~/AgentQO/chameleon_runs
rsync -avz cc@<FLOATING_IP>:~/AgentQO/logs/ ~/AgentQO/chameleon_runs/logs/
rsync -avz cc@<FLOATING_IP>:~/AgentQO/data/vllm/ ~/AgentQO/chameleon_runs/data_vllm/
rsync -avz cc@<FLOATING_IP>:~/AgentQO/data/cache/vllm.sqlite ~/AgentQO/chameleon_runs/
```

**Keep the cache file (`vllm.sqlite`).** Next session, copy it back to the new instance before running anything, and every generation you already paid for is reused:

```bash
# next session, from your Mac, after cloning the repo on the new instance:
ssh cc@<NEW_IP> "mkdir -p ~/AgentQO/data/cache"
rsync -avz ~/AgentQO/chameleon_runs/vllm.sqlite cc@<NEW_IP>:~/AgentQO/data/cache/
```

If you changed any code on the instance, commit and push it from there, or copy the changed files back. Otherwise those changes are lost too.

### 9.2 Shut down in this order

1. **Stop the servers.** In tmux windows 0 and 1, press `Ctrl+c`. Type `exit` to leave tmux and the SSH session.
2. **Delete the instance.** Site dashboard → **Compute → Instances** → select it → **Delete Instance**.
3. **Release the floating IP** if you allocated one yourself. **Network → Floating IPs → Release** (or Disassociate, then Release).
4. **End the lease.** **Reservations → Leases** → select your lease → **Delete Lease**. Check that it no longer shows as ACTIVE.

> Deleting the instance alone is not enough. The **lease** is what holds the node, so end it too.

### 9.3 Log what you used

Keep a ledger in `RESULTS.md` (it already has a table for this):

| Date | Site / node type | Lease hours | SU used | Cumulative | What ran |
|---|---|---|---|---|---|
| 2026-10-14 | CHI@UC / (node type) | 6 | (from portal) | | setup, smoke, H1 n=10 |

After your first lease, check how many SUs it actually used on your dashboard, so you know the real cost per hour for that node type. Use that number to plan every later session.

---

## Part 10: Checklist for every session

**Before**
- [ ] Code changes pushed to GitHub
- [ ] Plan for this session written down (which experiments, estimated hours)
- [ ] Lease created for the planned hours plus some margin, with Floating IP ticked

**Start**
- [ ] Lease is ACTIVE
- [ ] Instance launched: `CC-Ubuntu24.04-CUDA`, sharednet1, your key pair
- [ ] Floating IP associated
- [ ] `ssh cc@<IP>` works, `nvidia-smi` shows the GPU(s)
- [ ] `tmux new -s agentqo`
- [ ] Clone repo, venv, `pip install -e ".[dev,viz]" vllm`, tests pass
- [ ] Copy the cache file back (if not the first session)
- [ ] Both vLLM servers running; `curl` checks pass with logprobs
- [ ] `source ~/agentqo_env.sh`; smoke test passes

**Run**
- [ ] Small timed run first, check it fits in the lease
- [ ] Long runs inside tmux, logs saved with `tee`

**Finish**
- [ ] `rsync` logs, `data/vllm/`, and `vllm.sqlite` to the laptop
- [ ] Code changes pushed or copied back
- [ ] Servers stopped, instance deleted, floating IP released, **lease deleted**
- [ ] SU ledger updated

---

## Part 11: Troubleshooting

| Problem | Likely cause | What to do |
|---|---|---|
| Project not in the dropdown | Not a member, or no active allocation | Ask Dr. Liu to check your membership in CHI-251518 |
| No GPU nodes free in the calendar | High demand | Try the other site, or reserve a future slot |
| Cannot select the lease when launching | Lease still PENDING, or wrong site | Wait for ACTIVE; make sure you are in the same site's dashboard |
| Instance stuck in *Build* | Bare metal boots slowly | Wait 20 minutes. If it ends in *Error*, delete it and launch again |
| `ssh: Connection timed out` | Still booting, or no floating IP | Wait a few minutes; check the IP is associated to this instance |
| `Permission denied (publickey)` | Wrong key, or wrong username | Use `cc@`; check the key pair chosen at launch matches your key; use `-i` for a `.pem` file |
| `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED` | Same IP reused by a new instance | `ssh-keygen -R <IP>` on your Mac, then SSH again |
| `nvidia-smi: command not found` or no devices | Not a CUDA image, or not a GPU node | Relaunch with `CC-Ubuntu24.04-CUDA` (or `CC-Ubuntu22.04-CUDA`); check the lease's node type |
| `pip install vllm` fails | Python or CUDA mismatch | Send me the error; usually fixed by a specific vLLM version or the 22.04 image |
| vLLM out of memory at start | Two servers on one GPU asking for too much | Lower `--gpu-memory-utilization`; start the large model first |
| `curl` to a port is refused | Server still loading, or crashed | Look at that server's tmux window for the error |
| Pipeline errors about logprobs | Server not returning them | Check the `curl` logprobs test; as a last resort add `--allow-missing-logprobs` |
| Run is much slower than expected | Too few workers, or GPU idle | Watch `nvidia-smi`; raise `--workers` for labeling runs |
| Lease about to run out | Underestimated time | **Update Lease** to add hours; if not possible, copy results home immediately |
| Disk full | Model downloads plus outputs | `df -h`; remove unused models from `~/.cache/huggingface` |

If you get stuck, copy the exact error message and send it to me. Chameleon also has a help desk and a user forum for platform problems.

---

## Part 12: A plan for the first three sessions

**Session 1 (about 6 hours): setup and first result**
Lease, instance, setup (Parts 5 to 7), smoke test, timed 10-problem run, then C1 if time allows. Copy everything home. End the lease. Record SUs and how long each step took.

**Session 2: the core replication**
Copy the cache back, run C1 (if not finished), C2 and C3. This replicates the H1 repair finding and the H3 criticality-versus-structure result at 100 and 200 problems with full-precision models.

**Session 3: broaden**
C4 and the multi-hop QA workflow, which gives enough labeled workflows for H2. Then plan the multi-GPU scheduling experiments with Dr. Liu.

After each session, send me the logs and I will help you read them before the next one, so no session's results go unchecked.

---

## Sources

- Chameleon getting started guide: https://chameleoncloud.readthedocs.io/en/latest/getting-started
- Supported images (including `CC-Ubuntu24.04-CUDA`): https://chameleoncloud.readthedocs.io/en/latest/technical/images/supported_images.html
- Reservations (GUI), including lease updates and the 7-day limit: https://chameleoncloud.readthedocs.io/en/latest/technical/reservations/gui_reservations.html
- Recent platform changes (May 2026 newsletter): https://blog.chameleoncloud.org/posts/chameleon-newsletter-changelog-may-2026/
