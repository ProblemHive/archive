"""Antarctic sea-ice extent, NSIDC Sea Ice Index G02135 v4, monthly files S_MM_extent_v4.0.csv.
1. Null model: linear trend + AR(1) noise fitted to monthly anomalies 1979-01..2006-12
   (anomaly = extent minus that month's 1979-2006 mean). Simulated forward to the end of the
   record; how often does it give a mean anomaly over Sep 2016 .. end as low as observed?
2. Variance and lag-1 autocorrelation of anomalies (detrended with the 1979-2006 trend) in
   three periods (the breaks of Purich and Doddridge 2023): 1979-01..2007-08, 2007-09..2016-08,
   2016-09..end; all months and February only.
3. Recovery: AR(1) with free mean fitted to anomalies 2016-09..end. Does the fitted mean sit at
   the old climatology (0) or below it?
Each test also with the record cut at 2024-12, since 2025 onward comes from a different
product (NSIDC-0803, AMSR2) than earlier years (NSIDC-0051).
Seeds fixed; numpy only.
"""
import numpy as np, csv, glob

rows = []
for f in sorted(glob.glob("/data/j0fba/S_*_extent_v4.0.csv")):
    with open(f) as fh:
        r = csv.reader(fh); next(r)
        for x in r:
            y, mo, src, reg, ext = int(x[0]), int(x[1]), x[2].strip(), x[3], float(x[4])
            rows.append((y, mo, src, ext))
rows.sort()
t = np.array([y + (mo - 0.5) / 12 for y, mo, s, e in rows])
yr = np.array([y for y, mo, s, e in rows]); mon = np.array([mo for y, mo, s, e in rows])
ext = np.array([e for y, mo, s, e in rows]); ext[ext < 0] = np.nan
src = [s for y, mo, s, e in rows]
print("months: %d, %d-%02d to %d-%02d; missing: %s" % (len(rows), yr[0], mon[0], yr[-1], mon[-1],
      [(int(a), int(b)) for a, b in zip(yr[np.isnan(ext)], mon[np.isnan(ext)])]))
print("sources by year range:", sorted({(s, int(yr[i])) for i, s in enumerate(src) if s != src[i-1] or i == 0}))
full = (yr >= 1979)
yr, mon, ext, t = yr[full], mon[full], ext[full], t[full]

base = yr <= 2006
clim = np.array([np.nanmean(ext[base & (mon == m)]) for m in range(1, 13)])
anom = ext - clim[mon - 1]
# fill the two missing months by linear interpolation (needed for AR fits only)
nan = np.isnan(anom); anom_f = anom.copy()
anom_f[nan] = np.interp(np.flatnonzero(nan), np.flatnonzero(~nan), anom[~nan])

def ols(x, y):
    X = np.column_stack([np.ones_like(x), x]); b = np.linalg.lstsq(X, y, rcond=None)[0]
    return b, y - X @ b

def ar1(e):
    return np.dot(e[1:], e[:-1]) / np.dot(e[:-1], e[:-1])

def run(end_year, label):
    keep = yr <= end_year
    A, T, Y, M = anom_f[keep], t[keep], yr[keep], mon[keep]
    b0 = Y <= 2006
    (c, s), res = ols(T[b0] - 1979, A[b0])
    phi = ar1(res); sig = np.std(res[1:] - phi * res[:-1], ddof=1)
    late = (T >= 2016 + 8.5 / 12)
    obs = A[late].mean()
    print("\n=== %s (record to %d-%02d) ===" % (label, Y[-1], M[-1]))
    print("1979-2006 fit: trend %+.4f million km2 per year, AR(1) phi %.3f, innovation sd %.3f, residual sd %.3f"
          % (s, phi, sig, res.std(ddof=1)))
    print("observed mean anomaly Sep 2016 .. end: %+.3f million km2 (%d months)" % (obs, late.sum()))
    rng = np.random.default_rng(2026)
    N = 20000; n = len(A)
    for name, slope in [("trend continued", s), ("no trend", 0.0)]:
        e = np.zeros((N, n)); e[:, 0] = rng.normal(0, res.std(ddof=1), N)
        z = rng.normal(0, sig, (N, n))
        for i in range(1, n):
            e[:, i] = phi * e[:, i - 1] + z[:, i]
        sim = c + slope * (T - 1979) + e
        sm = sim[:, late].mean(1)
        p = (sm <= obs).mean()
        print("  null '%s': simulated late-period mean %+.3f (sd %.3f); P(as low as observed) = %s; observed is %.1f sd below"
              % (name, sm.mean(), sm.std(), ("< 1/%d" % N) if p == 0 else "%.5f" % p, (sm.mean() - obs) / sm.std()))
    # 2. variance and autocorrelation by period, detrended with the 1979-2006 line
    d = A - (c + s * (T - 1979))
    periods = [("1979-01..2007-08", T < 2007 + 8 / 12), ("2007-09..2016-08", (T >= 2007 + 8 / 12) & (T < 2016 + 8 / 12)),
               ("2016-09..end", T >= 2016 + 8 / 12)]
    print("by period: n, mean, sd and lag-1 autocorrelation of anomalies about the 1979-2006 line (all months); Feb: n, sd about the period mean")
    for nm, sel in periods:
        x = d[sel]; xc = x - x.mean()
        f = d[sel & (M == 2)]
        print("  %-17s n=%3d mean %+.3f sd %.3f r1 %.3f | Feb n=%2d sd %.3f" % (nm, sel.sum(), x.mean(), x.std(ddof=1), ar1(xc), len(f), f.std(ddof=1)))
    # F-test style comparison of Feb sd, bootstrap-free: ratio of variances
    f1 = d[(T < 2007 + 8 / 12) & (M == 2)]; f3 = d[(T >= 2007 + 8 / 12) & (M == 2)]
    print("  Feb variance ratio (2008..end vs 1979..2007): %.2f (n=%d vs %d)" % (f3.var(ddof=1) / f1.var(ddof=1), len(f3), len(f1)))
    # 3. recovery: AR(1) with free mean on the late period, anomalies relative to old climatology
    x = A[late]
    X = np.column_stack([np.ones(len(x) - 1), x[:-1]]); (k, ph), *_ = np.linalg.lstsq(X, x[1:], rcond=None)
    mu = k / (1 - ph)
    # block bootstrap (12-month blocks) for the CI of mu
    rng = np.random.default_rng(7); mus = []
    nb = len(x) // 12
    for _ in range(4000):
        st = rng.integers(0, len(x) - 12, nb)
        xb = np.concatenate([x[s0:s0 + 12] for s0 in st])
        mus.append(xb.mean())
    lo, hi = np.percentile(mus, [2.5, 97.5])
    print("recovery: late-period AR(1) phi %.3f (e-folding %.1f months), fitted mean %+.3f; block-bootstrap 95%% CI of the mean %+.3f to %+.3f"
          % (ph, -1 / np.log(ph), mu, lo, hi))
    print("  for comparison 1979-2006 residual AR(1) phi %.3f (e-folding %.1f months)" % (phi, -1 / np.log(phi)))
    # yearly means of anomalies, last 12 years
    print("annual mean anomaly vs 1979-2006 climatology:", " ".join("%d:%+.2f" % (y, A[Y == y].mean()) for y in range(2013, Y[-1] + 1)))

run(2026, "full record")
run(2024, "cut at 2024 (one product, NSIDC-0051)")
