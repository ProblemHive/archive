# hazard2.py - robustness checks for hazard.py (same models A and B, pooled k, per-model levels).
# (1) tasks with measured human times only; (2) task effect with a discrete 4-point distribution instead of a
# normal one (support and weights fitted); (3) bootstrap over task families (40 resamples, seed 7) for k in A and B.
# usage: python hazard2.py /data/agenthaz/runs.jsonl
import sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp, softmax

raw = pd.read_json(sys.argv[1], lines=True)
raw = raw[(raw["alias"] != "human") & raw["human_minutes"].notna()].copy()
gh_x, gh_w = np.polynomial.hermite_e.hermegauss(40)
gh_lw = np.log(gh_w / np.sqrt(2 * np.pi))


def prep(df):
    cnt = df.groupby("alias")["score_binarized"].agg(["sum", "count"])
    keep = cnt[(cnt["sum"] >= 20) & (cnt["count"] - cnt["sum"] >= 20)].index
    df = df[df["alias"].isin(keep)]
    m = df["alias"].map({a: i for i, a in enumerate(sorted(keep))}).to_numpy()
    tk = sorted(df["task_id"].unique())
    t = df["task_id"].map({a: i for i, a in enumerate(tk)}).to_numpy()
    x = np.log(df["human_minutes"].to_numpy()); x = x - x.mean()
    y = df["score_binarized"].to_numpy(float)
    return dict(m=m, t=t, x=x, y=y, M=len(keep), T=len(tk), fam=df["task_family"].to_numpy(), tid=df["task_id"].to_numpy())


def ll_runs(eta, y):
    eta = np.clip(eta, -30, 6)
    return np.where(y == 1, -np.exp(eta), np.log(-np.expm1(-np.exp(eta))))


def fitA(d, w=None):
    w = np.ones_like(d["y"]) if w is None else w
    M = d["M"]
    f = lambda p: -(w * ll_runs(p[d["m"]] + p[M] * d["x"], d["y"])).sum()
    return minimize(f, np.r_[np.zeros(M), 0.7], method="L-BFGS-B")


def fitB(d, start, w=None):
    # w: integer copies per task (bootstrap); task log-likelihoods are multiplied by them
    M, T = d["M"], d["T"]
    wt = np.ones(T) if w is None else w

    def f(p):
        s = np.exp(p[M + 1]); eta0 = p[d["m"]] + p[M] * d["x"]
        L = np.stack([np.bincount(d["t"], weights=ll_runs(eta0 + s * z, d["y"]), minlength=T) for z in gh_x], 1)
        return -(wt * logsumexp(L + gh_lw, axis=1)).sum()
    return minimize(f, start, method="L-BFGS-B")


def fitD(d, start):
    # discrete task effect: K support points (first fixed at 0 for identification via intercepts) and weights
    M, T, K = d["M"], d["T"], 4

    def f(p):
        k = p[M]; sup = np.r_[0.0, p[M + 1:M + K]]; lw = np.log(softmax(np.r_[0.0, p[M + K:M + 2 * K - 1]]))
        eta0 = p[d["m"]] + k * d["x"]
        L = np.stack([np.bincount(d["t"], weights=ll_runs(eta0 + a, d["y"]), minlength=T) for a in sup], 1)
        return -logsumexp(L + lw, axis=1).sum()
    best = None
    for init in ([-2.0, 1.5, 3.0], [-1.0, 1.0, 2.0], [-3.0, -1.5, 1.5]):
        r = minimize(f, np.r_[start, init, np.zeros(K - 1)], method="L-BFGS-B")
        if best is None or r.fun < best.fun:
            best = r
    return best


full = prep(raw)
base = prep(raw[raw["human_source"] == "baseline"])
for name, d in (("all tasks", full), ("measured human times only", base)):
    a = fitA(d); b = fitB(d, np.r_[a.x, 0.0])
    print(f"{name}: runs {len(d['y'])}, tasks {d['T']}, models {d['M']}")
    print(f"  A (no task effect) k = {a.x[d['M']]:.3f}   B (normal task effect) k = {b.x[d['M']]:.3f}, s = {np.exp(b.x[d['M']+1]):.2f}, 2*dlogL = {2*(a.fun-b.fun):.1f}")
    if name == "all tasks":
        dd = fitD(d, a.x)
        print(f"  D (4-point task effect) k = {dd.x[d['M']]:.3f}, -logL = {dd.fun:.1f} (B: {b.fun:.1f}); support {np.round(np.r_[0, dd.x[d['M']+1:d['M']+4]], 2)}, weights {np.round(softmax(np.r_[0, dd.x[d['M']+4:]]), 3)}")
        startB = b.x

# bootstrap over task families (all tasks)
d = full
fams = np.unique(d["fam"])
task_fam = pd.Series(d["fam"]).groupby(d["t"]).first().to_numpy()
rng = np.random.default_rng(7)
kA, kB = [], []
for r in range(40):
    draw = np.bincount(rng.integers(0, len(fams), len(fams)), minlength=len(fams))
    fam_w = dict(zip(fams, draw))
    wt = np.array([fam_w[f] for f in task_fam], float)
    a = fitA(d, w=wt[d["t"]])
    b = fitB(d, startB, w=wt)
    kA.append(a.x[d["M"]]); kB.append(b.x[d["M"]])
kA, kB = np.array(kA), np.array(kB)
print(f"family bootstrap ({len(fams)} families, 40 resamples): A k 95% range {np.percentile(kA, 2.5):.3f} to {np.percentile(kA, 97.5):.3f}; "
      f"B k {np.percentile(kB, 2.5):.3f} to {np.percentile(kB, 97.5):.3f}; B k below 1 in {int((kB < 1).sum())} of 40")
