#!/usr/bin/env python3
"""H4 analysis: features from per-request placement logs, four latency models,
held-out tests (P1), and the workflow latency simulation (P4).

    python3 scripts/h4_fit.py fit --grid data/h4/grid --out data/h4/fit
    python3 scripts/h4_fit.py fit-mps --grid data/h4/grid --p2 data/h4/p2 --out data/h4/fit/mps_fit.json
    python3 scripts/h4_fit.py predict-workflow --profile data/h4/p4/token_profile.json

Models (predict p50 or p95 latency of model m in a shared-GPU cell):
  B0         L = L_iso(m)
  B1         L = L_iso(m) * (1 + a * concurrency)
  B2         L = L_iso(m) * (1 + s * overlap)
  AgentIconq L = L_iso(m) * (1 + beta_{n->m} * u_n * overlap),  n = the other model
L_iso = median over repeats of the separate-placement latency in the same
(model, small_share, max_tokens, concurrency) cell. Fits are least squares on
log latency with parameters >= 0; concurrency-1 cells are not fitted.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

MODELS = ("B0", "B1", "B2", "AgentIconq")
OTHER = {"small": "large", "large": "small"}


# ---------------------------------------------------------------- features
def merge(iv):
    out = []
    for s, e in sorted(iv):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def length(iv):
    return sum(e - s for s, e in iv)


def intersect(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        s, e = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        if s < e:
            out.append([s, e])
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return out


def pct(xs, q):
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round(q * (len(xs) - 1)))))
    return xs[k]


def load_cells(grid: str):
    """One dict per (placement, small_share, max_tokens, concurrency, repeat, model)."""
    levels = defaultdict(list)
    for path in sorted(glob.glob(f"{grid}/*_requests.csv")):
        for r in csv.DictReader(open(path)):
            key = (r["config"], float(r["small_share"]), int(r["max_tokens"]), int(r["concurrency"]),
                   int(r["repeat_id"]), int(r["prefix_tokens"]))
            levels[key].append(r)
    cells = []
    for (pl, sh, mt, conc, rep, pt), rs in sorted(levels.items()):
        wall = float(rs[0]["level_wall_s"])
        iv = {m: merge([(float(r["start_s"]), float(r["end_s"])) for r in rs if r["model"] == m])
              for m in ("small", "large")}
        u = {m: length(iv[m]) / wall for m in iv}
        overlap = length(intersect(iv["small"], iv["large"])) / wall
        for m in ("small", "large"):
            lats = [float(r["latency_s"]) for r in rs if r["model"] == m]
            if not lats:
                continue
            cells.append({"placement": pl, "small_share": sh, "max_tokens": mt, "concurrency": conc,
                          "repeat": rep, "prefix_tokens": pt, "model": m, "n": len(lats),
                          "p50": pct(lats, 0.5), "p95": pct(lats, 0.95), "u_self": u[m],
                          "u_other": u[OTHER[m]], "overlap": overlap, "wall_s": wall})
    return cells


def attach_iso(cells, target="shared"):
    sep = defaultdict(lambda: {"p50": [], "p95": []})
    for c in cells:
        if c["placement"] == "separate":
            k = (c["model"], c["small_share"], c["max_tokens"], c["concurrency"], c["prefix_tokens"])
            sep[k]["p50"].append(c["p50"])
            sep[k]["p95"].append(c["p95"])
    shared = []
    for c in cells:
        if c["placement"] != target:
            continue
        k = (c["model"], c["small_share"], c["max_tokens"], c["concurrency"], c["prefix_tokens"])
        if k not in sep:
            continue
        shared.append({**c, "iso50": float(np.median(sep[k]["p50"])), "iso95": float(np.median(sep[k]["p95"]))})
    return shared


# ---------------------------------------------------------------- models
def factor(name, p, c):
    if name == "B0":
        return 1.0
    if name == "B1":
        return 1.0 + p[0] * c["concurrency"]
    if name == "B2":
        return 1.0 + p[0] * c["overlap"]
    beta = p[0] if c["model"] == "small" else p[1]  # p[0] = large->small, p[1] = small->large
    return 1.0 + beta * c["u_other"] * c["overlap"]


N_PARAMS = {"B0": 0, "B1": 1, "B2": 1, "AgentIconq": 2}


def fit(name, cells, q):
    n = N_PARAMS[name]
    if n == 0 or not cells:
        return np.zeros(n)
    y = np.log([c[q] for c in cells])
    iso = np.log([c["iso" + q[1:]] for c in cells])

    def res(p):
        return iso + np.log([factor(name, p, c) for c in cells]) - y
    return least_squares(res, x0=np.full(n, 0.5), bounds=(0, np.inf)).x


def predict(name, p, c, q):
    return c["iso" + q[1:]] * factor(name, p, c)


def mape(name, p, cells, q):
    return float(np.mean([abs(predict(name, p, c, q) - c[q]) / c[q] for c in cells]))


def direction(name, p, cells, min_conc):
    """Share of (share, max_tokens, conc) conditions where the predicted larger slowdown is right."""
    cond = defaultdict(lambda: defaultdict(list))
    for c in cells:
        if c["concurrency"] >= min_conc:
            cond[(c["small_share"], c["max_tokens"], c["concurrency"])][c["model"]].append(c)
    hits = total = 0
    for by in cond.values():
        if set(by) != {"small", "large"}:
            continue
        meas = {m: np.mean([c["p50"] / c["iso50"] for c in by[m]]) for m in by}
        pred = {m: np.mean([factor(name, p, c) for c in by[m]]) for m in by}
        total += 1
        if pred["small"] != pred["large"] and (pred["small"] > pred["large"]) == (meas["small"] > meas["large"]):
            hits += 1
    return hits / total if total else float("nan"), total


def bootstrap(name, cells, q, n_boot=1000):
    rng = np.random.default_rng(0)
    ps = [fit(name, [cells[i] for i in rng.integers(0, len(cells), len(cells))], q) for _ in range(n_boot)]
    ps = np.array(ps)
    return np.percentile(ps, 2.5, axis=0).tolist(), np.percentile(ps, 97.5, axis=0).tolist()


TESTS = {
    "A": ("fit small_share 0.25,0.75 -> predict 0.50", lambda c: c["small_share"] in (0.25, 0.75), lambda c: c["small_share"] == 0.5),
    "B": ("fit max_tokens 32,128 -> predict 512", lambda c: c["max_tokens"] in (32, 128), lambda c: c["max_tokens"] == 512),
    "C": ("fit repeat 0 -> predict repeats 1,2", lambda c: c["repeat"] == 0, lambda c: c["repeat"] in (1, 2)),
}


def plot(test, preds, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 4, figsize=(16, 4), sharex=True, sharey=True)
    for ax, name in zip(axes, MODELS):
        for m, color in (("small", "tab:blue"), ("large", "tab:orange")):
            pts = [(meas, pr) for mm, meas, pr in preds[name] if mm == m]
            if pts:
                ax.scatter(*zip(*pts), s=10, color=color, label=m)
        lim = [min(x for _, a, b in preds[name] for x in (a, b)), max(x for _, a, b in preds[name] for x in (a, b))]
        ax.plot(lim, lim, "k--", lw=0.8)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(name)
        ax.set_xlabel("measured p50 (s)")
    axes[0].set_ylabel("predicted p50 (s)")
    axes[0].legend()
    fig.suptitle(f"Test {test}: {TESTS[test][0]} (held-out shared-GPU cells)")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)


def cmd_fit(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cells = load_cells(args.grid)
    with open(out / "cells.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cells[0]))
        w.writeheader()
        w.writerows(cells)
    shared = [c for c in attach_iso(cells) if c["prefix_tokens"] == 0]
    fitset = [c for c in shared if c["concurrency"] > 1]
    print(f"cells: {len(cells)} total, {len(shared)} shared-GPU cells with L_iso, {len(fitset)} used for fitting")

    # separate placement: p50 at concurrency 64 vs 1 (median over repeats)
    sep = defaultdict(list)
    for c in cells:
        if c["placement"] == "separate" and c["prefix_tokens"] == 0:
            sep[(c["model"], c["small_share"], c["max_tokens"], c["concurrency"])].append(c["p50"])
    print("\nseparate placement, p50 at concurrency 64 / p50 at concurrency 1 (median over repeats):")
    sep_rows = []
    for (m, sh, mt, conc) in sorted(k for k in sep if k[3] == 64):
        r = float(np.median(sep[(m, sh, mt, 64)]) / np.median(sep[(m, sh, mt, 1)]))
        sep_rows.append({"model": m, "small_share": sh, "max_tokens": mt, "ratio_c64_c1": r})
        print(f"  {m:<6} share={sh:<5} max_tokens={mt:<4} ratio={r:.3f}")

    params = {}
    print("\nfitted on all shared cells (concurrency > 1), 95% bootstrap CIs (1000 resamples of cells):")
    for q in ("p50", "p95"):
        for name in MODELS[1:]:
            p = fit(name, fitset, q)
            lo, hi = bootstrap(name, fitset, q)
            params[f"{name}_{q}"] = {"params": p.tolist(), "ci_low": lo, "ci_high": hi}
            label = {"B1": ["a"], "B2": ["s"], "AgentIconq": ["beta_large_to_small", "beta_small_to_large"]}[name]
            txt = "  ".join(f"{l}={v:.3f} [{a:.3f},{b:.3f}]" for l, v, a, b in zip(label, p, lo, hi))
            print(f"  {q} {name:<11} {txt}")

    rows = []
    for t, (desc, tr, te) in TESTS.items():
        train = [c for c in fitset if tr(c)]
        test = [c for c in shared if te(c)]
        preds = {}
        print(f"\nTest {t}: {desc}   train cells {len(train)}, held-out cells {len(test)}")
        print(f"  {'model':<11}{'MAPE p50':>10}{'MAPE p95':>10}{'dir acc (c>=4)':>16}{'dir acc (all)':>15}  params p50")
        for name in MODELS:
            p50, p95 = fit(name, train, "p50"), fit(name, train, "p95")
            d4, n4 = direction(name, p50, test, 4)
            da, na = direction(name, p50, test, 1)
            row = {"test": t, "model": name, "mape_p50": mape(name, p50, test, "p50"),
                   "mape_p95": mape(name, p95, test, "p95"), "dir_acc_c4plus": d4, "n_dir_c4plus": n4,
                   "dir_acc_all": da, "n_dir_all": na, "params_p50": p50.tolist(), "params_p95": p95.tolist()}
            rows.append(row)
            preds[name] = [(c["model"], c["p50"], predict(name, p50, c, "p50")) for c in test]
            print(f"  {name:<11}{row['mape_p50']:>10.3f}{row['mape_p95']:>10.3f}{d4:>12.2f} ({n4}){da:>11.2f} ({na})  "
                  + " ".join(f"{v:.3f}" for v in p50))
        if test:
            plot(t, preds, out / f"pred_vs_measured_test{t}.png")
    json.dump({"full_fit": params, "tests": rows, "separate_c64_vs_c1": sep_rows}, open(out / "fit_results.json", "w"), indent=1)
    with open(out / "tests.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[k for k in rows[0] if not k.startswith("params")])
        w.writeheader()
        w.writerows({k: v for k, v in r.items() if not k.startswith("params")} for r in rows)
    print(f"\nwrote {out}/cells.csv, fit_results.json, tests.csv, pred_vs_measured_test*.png")


def cmd_fit_mps(args):
    """AgentIconq and B2 refitted on P2's MPS cells (L_iso from the grid's separate placement)."""
    cells = load_cells(args.grid) + load_cells(args.p2)
    out = {}
    for target in ("shared_mps", "shared_nomps"):
        fitset = [c for c in attach_iso(cells, target) if c["concurrency"] > 1 and c["prefix_tokens"] == 0]
        out[target] = {"n_cells": len(fitset)}
        for q in ("p50", "p95"):
            for name in ("B2", "AgentIconq"):
                out[target][f"{name}_{q}"] = {"params": fit(name, fitset, q).tolist() if fitset else None}
        print(target, json.dumps(out[target]))
    json.dump(out, open(args.out, "w"), indent=1)


# ---------------------------------------------------------------- P4 simulation
class IsoTable:
    """Separate-placement latency vs (model, tokens, concurrency): linear in tokens
    at each measured concurrency, linear in log2(concurrency) between levels."""

    def __init__(self, cells, q):
        by = defaultdict(list)
        for c in cells:
            if c["placement"] == "separate" and c["prefix_tokens"] == 0:
                by[(c["model"], c["concurrency"])].append((c["max_tokens"], c[q]))
        self.coef = {}
        for k, pts in by.items():
            x, y = np.array(pts, dtype=float).T
            self.coef[k] = np.polyfit(x, y, 1)  # y = b*tokens + a
        self.concs = sorted({k[1] for k in self.coef})

    def __call__(self, model, tokens, conc):
        conc = min(max(conc, self.concs[0]), self.concs[-1])
        lo = max(c for c in self.concs if c <= conc)
        hi = min(c for c in self.concs if c >= conc)
        f = lambda c: max(1e-3, float(np.polyval(self.coef[(model, c)], tokens)))
        if lo == hi:
            return f(lo)
        w = (np.log2(conc) - np.log2(lo)) / (np.log2(hi) - np.log2(lo))
        return (1 - w) * f(lo) + w * f(hi)


def simulate(profile, iso, k, interference, iters=200):
    """Fixed point for per-model concurrency, busy fraction and overlap with K problems in flight.
    interference(model, u_other, overlap, conc_total) -> latency multiplier."""
    calls = [[(n["fidelity"], n["completion_tokens"]) for n in nodes.values()] for nodes in profile.values()]
    c = {"small": 1.0, "large": 1.0}
    u = {"small": 0.5, "large": 0.5}
    for _ in range(iters):
        ov = u["small"] * u["large"]
        per_problem, t_m = [], {"small": 0.0, "large": 0.0}
        for cl in calls:
            tot = 0.0
            for m, tok in cl:
                lat = iso(m, tok, c[m]) * interference(m, u[{"small": "large", "large": "small"}[m]], ov, c["small"] + c["large"])
                tot += lat
                t_m[m] += lat
            per_problem.append(tot)
        mean_t = float(np.mean(per_problem))
        new_c, new_u = {}, {}
        for m in c:
            share = t_m[m] / len(calls) / mean_t  # fraction of a problem's time spent in model m calls
            new_c[m] = max(1.0, k * share)
            new_u[m] = 1 - (1 - share) ** k
        c = {m: 0.5 * c[m] + 0.5 * new_c[m] for m in c}
        u = {m: 0.5 * u[m] + 0.5 * new_u[m] for m in u}
    return {"p50_e2e": pct(per_problem, 0.5), "p95_e2e": pct(per_problem, 0.95), "mean_e2e": mean_t,
            "conc": c, "busy": u, "overlap": u["small"] * u["large"]}


def cmd_predict_workflow(args):
    cells = load_cells(args.grid)
    fitres = json.load(open(args.fit))["full_fit"]
    mps = json.load(open(args.mps_fit)) if args.mps_fit and Path(args.mps_fit).exists() else None
    profile = json.load(open(args.profile))["per_problem"]
    iso = IsoTable(cells, "p50")
    ks = [int(x) for x in args.ks.split(",")]

    def factors(model_name, params):
        if model_name == "B0":
            return lambda m, uo, ov, ct: 1.0
        if model_name == "B2":
            return lambda m, uo, ov, ct: 1.0 + params[0] * ov
        return lambda m, uo, ov, ct: 1.0 + (params[0] if m == "small" else params[1]) * uo * ov

    out = {"method": ("per-call latency = separate-placement p50 table (linear in tokens, log2-interpolated in "
                      "concurrency) x the model's interference factor; per-model concurrency, busy fraction and "
                      "overlap from a fixed point with K problems in flight (overlap = u_small*u_large); "
                      "per-problem e2e = sum of its 5 calls with its own completion tokens (from the cache "
                      "profile of C9's ec_top2 run); predicted p50/p95 e2e = percentiles over the problems. "
                      "S: no interference term. C: P1 full-fit parameters. CM: parameters refitted on P2 MPS cells."),
           "goal": "Use the fewest GPUs such that p95 end-to-end latency per problem is at most 1.5 x the p95 of placement S, at K = 16 problems in flight.",
           "predictions": {}, "recommendation": {}}
    for name in ("B0", "B2", "AgentIconq"):
        par = {"C": fitres.get(f"{name}_p50", {}).get("params")}
        if mps and name != "B0":
            par["CM"] = mps["shared_mps"].get(f"{name}_p50", {}).get("params")
        elif mps:
            par["CM"] = None
        res = {}
        for pl in ["S", "C"] + (["CM"] if mps else []):
            res[pl] = {}
            for k in ks:
                f = factors("B0" if pl == "S" else name, par.get(pl))
                res[pl][str(k)] = simulate(profile, iso, k, f)
        out["predictions"][name] = res
        s95 = res["S"]["16"]["p95_e2e"]
        ok = [pl for pl in res if pl != "S" and res[pl]["16"]["p95_e2e"] <= 1.5 * s95]
        rec = min(ok, key=lambda pl: res[pl]["16"]["p95_e2e"]) if ok else "S"
        out["recommendation"][name] = rec
        print(f"\n{name}: recommends {rec}")
        for pl in res:
            print("  " + pl + "  " + "  ".join(f"K={k}: p50 {res[pl][str(k)]['p50_e2e']:.2f}s p95 {res[pl][str(k)]['p95_e2e']:.2f}s"
                                         for k in ks) + f"   (p95/S at K=16: {res[pl]['16']['p95_e2e'] / s95:.2f})")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=1)
    print(f"\nwrote {args.out}")


# ---------------------------------------------------------------- reports
def _mean_p50(cells, **kw):
    xs = [c["p50"] for c in cells if all(c[k] == v for k, v in kw.items())]
    return xs


def cmd_p2_report(args):
    cells = load_cells(args.p2)
    base = {}
    for m in ("small", "large"):
        for conc in (1, 4, 16, 32):
            xs = _mean_p50(cells, placement="separate", model=m, concurrency=conc)
            base[(m, conc)] = float(np.median(xs)) if xs else float("nan")
    rows, means = [], {}
    print(f"{'config':<14}{'model':<7}{'conc':>5}{'sep p50':>9}{'mean slowdown':>15}{'range':>18}")
    for cfg in ("shared_nomps", "shared_mps"):
        for m in ("small", "large"):
            for conc in (1, 4, 16, 32):
                sl = [x / base[(m, conc)] for x in _mean_p50(cells, placement=cfg, model=m, concurrency=conc)]
                if not sl:
                    continue
                means[(cfg, m, conc)] = float(np.mean(sl))
                rows.append({"config": cfg, "model": m, "concurrency": conc, "separate_p50": base[(m, conc)],
                             "slowdown_mean": float(np.mean(sl)), "slowdown_min": min(sl), "slowdown_max": max(sl),
                             "n_repeats": len(sl)})
                print(f"{cfg:<14}{m:<7}{conc:>5}{base[(m, conc)]:>9.3f}{np.mean(sl):>15.3f}   [{min(sl):.3f}, {max(sl):.3f}]")
    verdict = {}
    if all(("shared_mps", "small", c) in means for c in (4, 16, 32)):
        v = [means[("shared_mps", "small", c)] for c in (4, 16, 32)]
        verdict["mps_small_below_2"] = {"values_c4_16_32": v, "held": all(x < 2.0 for x in v)}
    if all(("shared_nomps", m, c) in means for m in ("small", "large") for c in (4, 16, 32)):
        sm = float(np.mean([means[("shared_nomps", "small", c)] for c in (4, 16, 32)]))
        lg = float(np.mean([means[("shared_nomps", "large", c)] for c in (4, 16, 32)]))
        verdict["nomps_reproduces_c5"] = {"small": sm, "large": lg, "small_rel_err": sm / 3.07 - 1,
                                          "large_rel_err": lg / 1.75 - 1,
                                          "held": abs(sm / 3.07 - 1) <= 0.10 and abs(lg / 1.75 - 1) <= 0.10}
    print(json.dumps(verdict, indent=1))
    json.dump({"rows": rows, "verdict": verdict}, open(Path(args.p2) / "p2_report.json", "w"), indent=1)


def cmd_p3_report(args):
    cells = load_cells(args.p3)
    pts = sorted({c["prefix_tokens"] for c in cells})
    long_p = max(pts)
    mean = lambda **kw: float(np.mean(_mean_p50(cells, **kw)))
    rows = []
    print(f"prefix settings (measured tokens): {pts}")
    print(f"{'placement':<10}{'model':<7}{'conc':>5}" + "".join(f"{'p50 pre=' + str(p):>14}" for p in pts))
    for pl in ("separate", "shared"):
        for m in ("small", "large"):
            for conc in (1, 4, 16, 32):
                v = [mean(placement=pl, model=m, concurrency=conc, prefix_tokens=p) for p in pts]
                rows.append({"placement": pl, "model": m, "concurrency": conc, **{f"p50_prefix{p}": x for p, x in zip(pts, v)}})
                print(f"{pl:<10}{m:<7}{conc:>5}" + "".join(f"{x:>14.3f}" for x in v))
    # hit rates
    hits = defaultdict(lambda: [0.0, 0.0])
    for path in glob.glob(f"{args.p3}/placement_separate_*_p{long_p}_*_prefix_cache.json"):
        for lv in json.load(open(path))["levels"]:
            if lv["concurrency"] in (16, 32):
                hits[lv["model"]][0] += lv["hit_tokens"]
                hits[lv["model"]][1] += lv["query_tokens"]
    all_hits = defaultdict(list)
    for path in sorted(glob.glob(f"{args.p3}/*_prefix_cache.json")):
        for lv in json.load(open(path))["levels"]:
            all_hits[(Path(path).name.split("_")[1], json.load(open(path))["prefix_tokens"], lv["concurrency"], lv["model"])].append(lv["hit_rate"])
    print("\nprefix cache hit rate per level (mean over repeats):")
    for k in sorted(all_hits):
        print(f"  {k[0]:<9} prefix={k[1]:<5} conc={k[2]:<3} {k[3]:<6} {np.mean(all_hits[k]):.3f}")
    hr = {m: h / q if q else float("nan") for m, (h, q) in hits.items()}
    ratios = {(m, c): mean(placement="separate", model=m, concurrency=c, prefix_tokens=long_p)
              / mean(placement="separate", model=m, concurrency=c, prefix_tokens=0) for m in ("small", "large") for c in (16, 32)}
    v1 = {"p50_ratio_prefix_vs_none": {f"{m}_c{c}": r for (m, c), r in ratios.items()},
          "hit_rate_c16_32": hr,
          "held": all(r <= 0.8 for r in ratios.values()) and all(h > 0.8 for h in hr.values())}
    slow = {p: float(np.mean([mean(placement="shared", model="small", concurrency=c, prefix_tokens=p)
                              / mean(placement="separate", model="small", concurrency=c, prefix_tokens=p) for c in (4, 16, 32)]))
            for p in (0, long_p)}
    v2 = {"small_slowdown_mean_c4_16_32": slow, "ratio": slow[long_p] / slow[0], "held": slow[long_p] <= 0.9 * slow[0]}
    print(json.dumps({"separate_prediction": v1, "shared_prediction": v2}, indent=1))
    json.dump({"rows": rows, "separate_prediction": v1, "shared_prediction": v2,
               "hit_rates": {"|".join(map(str, k)): float(np.mean(v)) for k, v in all_hits.items()}},
              open(Path(args.p3) / "p3_report.json", "w"), indent=1)


def cmd_p4_report(args):
    import csv as _csv
    runs = defaultdict(list)
    for path in sorted(glob.glob(f"{args.p4}/p4_*_k*_r*.csv")):
        rs = list(_csv.DictReader(open(path)))
        pl, k = rs[0]["placement"], int(rs[0]["k"])
        lat = [float(r["latency_s"]) for r in rs]
        wall = max(float(r["end_s"]) for r in rs) - min(float(r["start_s"]) for r in rs)
        gpus = {"S": 2, "C": 1, "CM": 1}[pl]
        runs[(pl, k)].append({"p50": pct(lat, 0.5), "p95": pct(lat, 0.95), "acc": np.mean([float(r["correct"]) for r in rs]),
                              "per_gpu_hour": len(rs) / (wall / 3600) / gpus,
                              "match_c9": np.mean([r["correct"] == r["c9_correct"] for r in rs])})
    pred = json.load(open(args.predictions))
    meas = {}
    print(f"{'placement':<10}{'K':>4}{'p50 e2e':>10}{'p95 e2e':>10}{'probs/GPU-h':>13}{'accuracy':>10}{'C9 match':>10}  (mean over repeats)")
    for (pl, k), rs in sorted(runs.items()):
        m = {key: float(np.mean([r[key] for r in rs])) for key in rs[0]}
        meas[(pl, k)] = m
        print(f"{pl:<10}{k:>4}{m['p50']:>10.2f}{m['p95']:>10.2f}{m['per_gpu_hour']:>13.0f}{m['acc']:>10.3f}{m['match_c9']:>10.3f}   n_repeats={len(rs)}")
    s95 = meas[("S", 16)]["p95"]
    meets = {pl: meas[(pl, 16)]["p95"] <= 1.5 * s95 for pl in ("S", "C", "CM") if (pl, 16) in meas}
    one_gpu = [pl for pl in ("C", "CM") if meets.get(pl)]
    best = min(one_gpu, key=lambda pl: meas[(pl, 16)]["p95"]) if one_gpu else "S"
    print(f"\ngoal at K=16: limit 1.5 x S p95 = {1.5 * s95:.2f} s; meets: {meets}; fewest-GPU placement meeting it: {best}")
    out = {"measured": {f"{pl}|{k}": v for (pl, k), v in meas.items()}, "goal_limit_s": 1.5 * s95,
           "meets_goal": meets, "actual_best": best, "models": {}}
    for name, rec in pred["recommendation"].items():
        err = {pl: pred["predictions"][name][pl]["16"]["p95_e2e"] / meas[(pl, 16)]["p95"] - 1
               for pl in pred["predictions"][name] if (pl, 16) in meas}
        out["models"][name] = {"recommended": rec, "recommendation_meets_goal": bool(meets.get(rec)),
                               "recommendation_is_best": rec == best, "p95_rel_error_k16": err}
        print(f"{name:<11} recommended {rec}: meets goal {meets.get(rec)}, is the fewest-GPU placement meeting it {rec == best}; "
              f"p95 error at K=16 " + ", ".join(f"{pl} {e:+.1%}" for pl, e in err.items()))
    json.dump(out, open(Path(args.p4) / "p4_report.json", "w"), indent=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fit")
    f.add_argument("--grid", default="data/h4/grid")
    f.add_argument("--out", default="data/h4/fit")
    f.set_defaults(func=cmd_fit)
    m = sub.add_parser("fit-mps")
    m.add_argument("--grid", default="data/h4/grid")
    m.add_argument("--p2", default="data/h4/p2")
    m.add_argument("--out", default="data/h4/fit/mps_fit.json")
    m.set_defaults(func=cmd_fit_mps)
    w = sub.add_parser("predict-workflow")
    w.add_argument("--grid", default="data/h4/grid")
    w.add_argument("--fit", default="data/h4/fit/fit_results.json")
    w.add_argument("--mps-fit", default="data/h4/fit/mps_fit.json")
    w.add_argument("--profile", default="data/h4/p4/token_profile.json")
    w.add_argument("--ks", default="4,16,32")
    w.add_argument("--out", default="data/h4/p4_predictions.json")
    w.set_defaults(func=cmd_predict_workflow)
    for name, fn, dflt in (("p2-report", cmd_p2_report, "data/h4/p2"), ("p3-report", cmd_p3_report, "data/h4/p3")):
        r = sub.add_parser(name)
        r.add_argument("--" + name[:2], default=dflt)
        r.set_defaults(func=fn)
    r = sub.add_parser("p4-report")
    r.add_argument("--p4", default="data/h4/p4")
    r.add_argument("--predictions", default="data/h4/p4_predictions.json")
    r.set_defaults(func=cmd_p4_report)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
