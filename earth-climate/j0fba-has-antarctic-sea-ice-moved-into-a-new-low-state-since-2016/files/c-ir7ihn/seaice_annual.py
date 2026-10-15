"""Stricter nulls for the post-2016 low, on annual means (complete years 1979..2025) of NSIDC
G02135 v4 monthly extent anomalies (relative to the 1979-2006 monthly climatology).
A monthly AR(1) has an e-folding time of a few months and cannot make multi-year swings like
the 2007-2015 high, so it overstates how unusual a ten-year low is. Here the noise is fitted on
annual means, (a) to 1979-2006 and (b) to 1979-2015 (all years before the drop, high period
included), with trend + AR(1) and, as a heavier tail, trend + AR(2).
Statistic: mean anomaly of 2017..2025 (9 complete years after the drop of late 2016).
1987/88: the two missing months are left out of those years' means.
"""
import numpy as np, csv, glob
ext = {}
for f in sorted(glob.glob("/data/j0fba/S_*_extent_v4.0.csv")):
    with open(f) as fh:
        r = csv.reader(fh); next(r)
        for x in r:
            v = float(x[4])
            if v > 0: ext[(int(x[0]), int(x[1]))] = v
clim = {m: np.mean([v for (y, mo), v in ext.items() if mo == m and 1979 <= y <= 2006]) for m in range(1, 13)}
years = np.arange(1979, 2026)
ann = np.array([np.mean([ext[(y, m)] - clim[m] for m in range(1, 13) if (y, m) in ext]) for y in years])
obs = ann[(years >= 2017) & (years <= 2025)].mean()
print("observed mean annual anomaly 2017-2025: %+.3f million km2" % obs)

def fit(Y, A, p):
    # OLS of A_t on 1, (Y_t-1979), A_{t-1..t-p} residual structure: two-step (trend, then AR(p) on residuals)
    X = np.column_stack([np.ones(len(Y)), Y - 1979]); b = np.linalg.lstsq(X, A, rcond=None)[0]
    e = A - X @ b
    Z = np.column_stack([e[p - k - 1:len(e) - k - 1] for k in range(p)])
    ph = np.linalg.lstsq(Z, e[p:], rcond=None)[0]
    inn = e[p:] - Z @ ph
    return b, ph, inn.std(ddof=p), e.std(ddof=1)

rng = np.random.default_rng(11); N = 50000
for lastfit in (2006, 2015):
    sel = years <= lastfit
    for p in (1, 2):
        b, ph, s, sd = fit(years[sel], ann[sel], p)
        for name, slope in (("trend continued", b[1]), ("no trend", 0.0)):
            n = len(years); e = np.zeros((N, n + 50))
            z = rng.normal(0, s, (N, n + 50))
            for i in range(p, n + 50):
                e[:, i] = sum(ph[k] * e[:, i - k - 1] for k in range(p)) + z[:, i]
            e = e[:, 50:]  # burn-in
            sim = b[0] + slope * (years - 1979) + e
            sm = sim[:, (years >= 2017) & (years <= 2025)].mean(1)
            pv = (sm <= obs).mean()
            print("fit 1979-%d, AR(%d) phi=%s innov sd %.3f, %-15s: null mean %+.3f sd %.3f, P(<= obs) = %s"
                  % (lastfit, p, np.round(ph, 3).tolist(), s, name, sm.mean(), sm.std(),
                     ("< 1/%d" % N) if pv == 0 else "%.5f" % pv))
print("annual anomalies:", " ".join("%d:%+.2f" % (y, a) for y, a in zip(years, ann)))
