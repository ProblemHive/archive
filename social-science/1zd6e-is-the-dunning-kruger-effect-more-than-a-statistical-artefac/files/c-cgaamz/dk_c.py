import numpy as np
from math import erf, sqrt

def norm_sf(z):
    return 0.5 * (1 - erf(z / sqrt(2)))

def glejser(score, est):
    sl, ic = np.polyfit(score, est, 1)
    resid = est - (ic + sl * score)
    ar = np.abs(resid)
    g_r = np.corrcoef(ar, score)[0, 1]
    n = len(score); t = g_r * sqrt((n - 2) / max(1e-30, 1 - g_r**2))
    return g_r, 2 * norm_sf(abs(t))

# Find the deficit size (model C coefficient c) that reproduces the Add Health Glejser r = -0.07
N, REPS = 3500, 100
rng = np.random.default_rng(42)
for c in [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4]:
    grs, gps = [], []
    for _ in range(REPS):
        theta = rng.normal(0, 1, N)
        score = theta + rng.normal(0, 1, N)
        sd = np.clip(1 - c * theta, 0.4, 2.2) * 6.0
        est = 50.0 + 8.0 * theta + rng.normal(0, 1, N) * sd
        est = np.clip(est, 0, 100)
        gr, gp = glejser(score, est)
        grs.append(gr); gps.append(gp)
    print(f'c={c:.2f}: mean Glejser r={np.mean(grs):+.4f}  share p<.05={np.mean(np.array(gps)<.05):.3f}')
