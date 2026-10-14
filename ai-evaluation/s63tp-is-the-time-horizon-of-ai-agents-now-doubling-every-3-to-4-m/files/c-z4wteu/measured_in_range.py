# measured_in_range.py - follow-up to c/8it475: with measured-human-time tasks only, does the doubling time
# change when the trend is fitted only through models whose 50% horizon lies inside the range the measured
# tasks cover? Cut-offs on the measured-only point horizon: none, 1112 min (longest measured task),
# 480 min (8 hours; only 5 measured tasks are longer), 240 min. Windows: all models, and released 2024 or later.
# Same fit as s63tp/rerun_measured.py (scipy BFGS, ridge 0.01, bootstrap of task families, seed 2026, 500 resamples).
# The set of models is fixed from the point estimates, then kept in every resample.
# usage: python -I s63tp/measured_in_range.py downloads/s63tp/runs.jsonl downloads/s63tp/release_dates.yaml
import datetime
import sys
import numpy as np
import pandas as pd
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
df["fam"] = df["task_family"].map({f: i for i, f in enumerate(families)})


def log2_horizon(x, y, w):
    w = w / w.sum() * len(w)
    f = lambda b: -(w * (y * (b[0] + b[1] * x) - np.logaddexp(0, b[0] + b[1] * x))).sum() + 0.005 * (b @ b)

    def g(b):
        r = w * (y - expit(b[0] + b[1] * x))
        return -np.array([r.sum(), (r * x).sum()]) + 0.01 * b

    res = minimize(f, np.zeros(2), jac=g, method="BFGS", options={"gtol": 1e-9, "maxiter": 500})
    return -res.x[0] / res.x[1]


def horizons(parts, counts=None):
    out = []
    for f, x, y, w in parts:
        ww = w if counts is None else w * counts[f]
        k = ww > 0
        out.append(log2_horizon(x[k], y[k], ww[k]))
    return np.array(out)


sub = df[df["human_source"] == "baseline"]
parts = []
for m in models:
    gm = sub[sub["alias"] == m]
    parts.append((gm["fam"].to_numpy(), gm["x"].to_numpy(), gm["score_binarized"].to_numpy(float), gm["invsqrt_task_weight"].to_numpy(float)))
h0 = horizons(parts)
rng = np.random.default_rng(2026)
boot = np.array([horizons(parts, np.bincount(rng.integers(0, len(families), len(families)), minlength=len(families)).astype(float)) for _ in range(500)])
print("measured-only 50% horizons (minutes), by release date:")
for m, h in zip(models, h0):
    print(f"  {release[m]}  {m:36s} {2 ** h:8.1f}")
print()
print(f"{'models kept (measured-only horizon)':38s} {'window':10s} {'n':>2s}  {'last release':12s} doubling, days [95%]   slope<=0")
for cut in (None, 1112, 480, 240):
    keep = np.ones(len(models), bool) if cut is None else (2 ** h0 <= cut)
    for wname, wmask in (("all", np.ones(len(models), bool)), ("2024+", days >= 365)):
        mask = keep & wmask
        slope0 = np.polyfit(days[mask], h0[mask], 1)[0]
        sl = np.array([np.polyfit(days[mask], b[mask], 1)[0] for b in boot])
        lo, hi = np.percentile(sl, [2.5, 97.5])           # interval taken on the slope, then inverted
        last = max(release[m] for m, k in zip(models, mask) if k)
        label = "all models" if cut is None else f"horizon <= {cut} min"
        print(f"{label:38s} {wname:10s} {int(mask.sum()):2d}  {str(last):12s} {1 / slope0:6.1f} [{1 / hi:6.1f}, {1 / lo:6.1f}]      {int((sl <= 0).sum())}")
