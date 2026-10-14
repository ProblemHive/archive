import numpy as np
from math import erf, sqrt

N, REPS = 3500, 200
rng = np.random.default_rng(20261006)

def norm_sf(z):
    return 0.5 * (1 - erf(z / sqrt(2)))

def sample(model, rng):
    theta = rng.normal(0, 1, N)                      # latent ability
    score = theta + rng.normal(0, 1, N)               # observed test score (noisy measure of theta)
    est = 50.0 + 8.0 * theta                          # percentile estimate: no deficit, linear in true ability
    if model == 'C':                                  # real deficit: low skill -> noisier impression
        sd = np.clip(1 - 0.4 * theta, 0.4, 2.2) * 6.0
        est = est + rng.normal(0, 1, N) * sd
    else:
        est = est + rng.normal(0, 1, N) * 6.0
    if model in 'BC':                                 # bounded percentile scale: hard floor/ceiling at 0 and 100
        est = np.clip(est, 0, 100)
    return score, est

def glejser(score, est):
    sl, ic = np.polyfit(score, est, 1)
    resid = est - (ic + sl * score)
    ar = np.abs(resid)
    g_r = np.corrcoef(ar, score)[0, 1]
    n = len(score); t = g_r * sqrt((n - 2) / max(1e-30, 1 - g_r**2))
    g_p = 2 * norm_sf(abs(t))                          # two-sided p for Glejser corr
    return g_r, g_p

print(f'N={N} per sample, REPS={REPS}, percentile scale 0..100 with hard bounds in B,C')
for model in 'ABC':
    out = [glejser(*sample(model, rng)) for _ in range(REPS)]
    grs = np.array([o[0] for o in out]); gps = np.array([o[1] for o in out])
    print(f'model {model}: mean Glejser r={grs.mean():+.4f}  share p<.05={(gps<.05).mean():.3f}')
