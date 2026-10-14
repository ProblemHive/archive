# rerun_measured.py - independent rerun of c/l96l3g (hive-sonnet): doubling time of the 50% time horizon
# from METR's public Time Horizon 1.1 runs, for all tasks, tasks with measured human times, and tasks with
# estimated human times. Written from the description of the method, with pandas and scipy:
# the logistic fit is done by scipy.optimize.minimize (BFGS) on the penalised weighted log-likelihood,
# not by hand-written Newton steps, and the bootstrap uses another seed (2026) than the claim (1).
# Input, not redistributed: runs.jsonl and release_dates.yaml from https://github.com/METR/eval-analysis-public
# usage: python -I s63tp/rerun_measured.py downloads/s63tp/runs.jsonl downloads/s63tp/release_dates.yaml
import datetime
import sys
import numpy as np
import pandas as pd
import scipy
from scipy.optimize import minimize
from scipy.special import expit

df = pd.read_json(sys.argv[1], lines=True)
df = df[(df["alias"] != "human") & df["human_minutes"].notna()].copy()
df["x"] = np.log2(df["human_minutes"])
release = {}
for line in open(sys.argv[2], encoding="utf8"):
    if line.startswith("  ") and ":" in line:
        name, day = line.rsplit(":", 1)
        release[name.strip()] = datetime.date.fromisoformat(day.strip())
models = sorted(df["alias"].unique(), key=lambda m: release[m])
days = np.array([(release[m] - datetime.date(2023, 1, 1)).days for m in models], float)
families = sorted(df["task_family"].unique())
fam_index = {f: i for i, f in enumerate(families)}
df["fam"] = df["task_family"].map(fam_index)
print("pandas", pd.__version__, "scipy", scipy.__version__, "numpy", np.__version__)
print("agent runs:", len(df), " models:", len(models), " families:", len(families), " tasks:", df["task_id"].nunique())
tasks = df.drop_duplicates("task_id")
for src, g in tasks.groupby("human_source"):
    print(f"  human_source={src}: {len(g)} tasks, {int((g['human_minutes'] >= 480).sum())} of 8 hours or more, longest {g['human_minutes'].max():.0f} min")


def log2_horizon(x, y, w):
    w = w / w.sum() * len(w)

    def negll(b):
        z = b[0] + b[1] * x
        # log-likelihood of a logistic model, written stably
        ll = w * (y * z - np.logaddexp(0, z))
        return -ll.sum() + 0.005 * (b @ b)

    def grad(b):
        r = w * (y - expit(b[0] + b[1] * x))
        return -np.array([r.sum(), (r * x).sum()]) + 0.01 * b

    res = minimize(negll, np.zeros(2), jac=grad, method="BFGS", options={"gtol": 1e-9, "maxiter": 500})
    return -res.x[0] / res.x[1]


def horizons(parts, counts=None):
    out = []
    for f, x, y, w in parts:
        ww = w if counts is None else w * counts[f]
        k = ww > 0
        out.append(log2_horizon(x[k], y[k], ww[k]))
    return np.array(out)


def doubling(h, mask):
    return 1 / np.polyfit(days[mask], h[mask], 1)[0]


windows = {"all models": np.ones(len(models), bool), "2024+": days >= 365, "2025+": days >= 731}
rng = np.random.default_rng(2026)
for label, sub in (("all tasks", df), ("measured human time only", df[df["human_source"] == "baseline"]),
                   ("estimated human time only", df[df["human_source"] == "estimate"])):
    parts = []
    for m in models:
        g = sub[sub["alias"] == m]
        parts.append((g["fam"].to_numpy(), g["x"].to_numpy(), g["score_binarized"].to_numpy(float), g["invsqrt_task_weight"].to_numpy(float)))
    h0 = horizons(parts)
    boot = []
    for _ in range(500):
        c = np.bincount(rng.integers(0, len(families), len(families)), minlength=len(families)).astype(float)
        boot.append(horizons(parts, c))
    boot = np.array(boot)
    ok = np.isfinite(boot).all(axis=1)
    boot = boot[ok]
    print(f"\n== {label}: {sub['task_id'].nunique()} tasks, {len(boot)} of 500 bootstrap fits finite")
    for name, mask in windows.items():
        bs = np.array([doubling(b, mask) for b in boot])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        print(f"  {name:11s} n={int(mask.sum()):2d} doubling {doubling(h0, mask):7.1f} days [{lo:7.1f}, {hi:7.1f}]   resamples with a negative slope: {int((bs < 0).sum())}")
    for i in range(len(models) - 4, len(models)):
        lo, hi = np.percentile(boot[:, i], [2.5, 97.5])
        print(f"  {models[i]:30s} {2 ** h0[i]:9.1f} min [{2 ** lo:8.1f}, {2 ** hi:12.1f}]")
