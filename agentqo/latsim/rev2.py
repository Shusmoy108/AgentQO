"""latsim rev2: rev1 with measured instead of borrowed interference factors (X1c data only).

    python3 -m agentqo.latsim.rev2 --out results/latsim/rev2/params.json

Registered in docs/latsim_prereg.md (PI decision 3). Everything is rev1's (results/latsim/rev1/params.json)
except the interference factors latsim had to borrow:
  * Phi-3.5-mini / Phi-4 (borrowed from Qwen 3B/14B): the X1c Phi grid's own h4_fit
    (results/v2/X1c/phi/fit/{fit_results,mps_fit}.json), at rev1's quantile (p50), for shared and shared_mps.
  * Qwen 1.5B/7B/14B on one GPU (pairs with the 14B borrowed: 7B/14B from Qwen 3B/14B, 1.5B/14B from
    Qwen 1.5B/7B, a log-size tie that nearest_pair resolves to the first pair): the four directed factors
    14B->1.5B, 1.5B->14B, 14B->7B, 7B->14B for shared placement, fitted by closed-loop re-simulation of the X1c
    A16 three-model runs (results/v2/X1c/a16_three_model/shared, K=16, cold runs left out as in rev1): least
    squares on log(predicted / measured) per call, model parameters fixed at rev1's, starting from the borrowed
    values. The 1.5B/7B pair keeps its own (measured) h4grid factor. MPS with three models has no X1c data and
    stays borrowed.
Nothing from X1 or X1b is read.
"""

from __future__ import annotations

import argparse
import json
import os
from multiprocessing import Pool

import numpy as np
from scipy.optimize import least_squares

from agentqo.latsim.fit import betas_for, folder_runs
from agentqo.latsim.sim import simulate

Q15, Q7, Q14 = (f"Qwen/Qwen2.5-{s}-Instruct" for s in ("1.5B", "7B", "14B"))
FITTED = [(Q14, Q15), (Q15, Q14), (Q14, Q7), (Q7, Q14)]  # (other, model): other slows model
LOG_LO, LOG_HI = np.log(1e-3), np.log(20.0)

_RUNS, _MODELS = None, None


def _init(runs, models):
    global _RUNS, _MODELS
    _RUNS, _MODELS = runs, models


def _run_resid(args):
    i, betas = args
    _, k, problems, _ = _RUNS[i]
    lat = []
    simulate(problems, _MODELS, k, betas, call_latency=lat)
    pred = np.array([x for p in lat for x in p])
    meas = np.array([c[3] for p in problems for c in p])
    return np.log(np.maximum(pred, 1e-6)) - np.log(meas)


def a16_betas(runs: list, params: dict, pool) -> dict:
    base = betas_for([Q15, Q7, Q14], "shared", params)

    def resid(z):
        b = {**base, **{p: float(np.exp(v)) for p, v in zip(FITTED, z)}}
        return np.concatenate(pool.map(_run_resid, [(i, b) for i in range(len(runs))]))

    x0 = np.log([base[p] for p in FITTED])
    r0 = resid(x0)
    sol = least_squares(resid, x0, diff_step=1e-2, max_nfev=40, bounds=(LOG_LO, LOG_HI))
    r = resid(sol.x)
    return {"pair_betas": {f"{o}->{m}": float(np.exp(v)) for (o, m), v in zip(FITTED, sol.x)},
            "borrowed": {f"{o}->{m}": float(base[(o, m)]) for o, m in FITTED},
            "n_runs": len(runs), "n_calls": int(len(r)),
            "rmse_log_borrowed": float(np.sqrt(np.mean(r0 ** 2))), "rmse_log_fitted": float(np.sqrt(np.mean(r ** 2))),
            "mean_log_residual_borrowed": float(np.mean(r0)), "mean_log_residual_fitted": float(np.mean(r)),
            "nfev": int(sol.nfev)}


def phi_betas(results: str, q: str) -> dict:
    names = ("large_to_small", "small_to_large")
    fr = json.load(open(f"{results}/X1c/phi/fit/fit_results.json"))["full_fit"]
    mp = json.load(open(f"{results}/X1c/phi/fit/mps_fit.json"))["shared_mps"]
    return {"shared": dict(zip(names, fr[f"AgentIconq_{q}"]["params"])),
            "shared_mps": dict(zip(names, mp[f"AgentIconq_{q}"]["params"]))}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", default="results/v2")
    ap.add_argument("--base", default="results/latsim/rev1/params.json")
    ap.add_argument("--out", default="results/latsim/rev2/params.json")
    args = ap.parse_args()
    params = json.load(open(args.base))
    q = params["beta_quantile"]
    params["betas"]["phi"] = phi_betas(args.results, q)
    runs = list(folder_runs(f"{args.results}/X1c/a16_three_model/shared"))
    with Pool(initializer=_init, initargs=(runs, params["models"])) as pool:
        a16 = a16_betas(runs, params, pool)
    params["pair_betas"] = {"shared": a16.pop("pair_betas")}
    params["rev2"] = {"base": args.base, "phi_quantile": q, "a16_fit": a16,
                      "data": ["results/v2/X1c/phi/fit", "results/v2/X1c/a16_three_model/shared"]}
    print(json.dumps({"phi": params["betas"]["phi"], "pair_betas": params["pair_betas"], **a16}, indent=1))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(params, open(args.out, "w"), indent=1)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
