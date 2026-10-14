# Does the Glejser test keep its false-positive rate when the answer scale's bounds actually bind?
# No-deficit model throughout: every person's self-estimate has the same noise sd.
#   theta ~ N(0,1) latent ability; score = theta + N(0, s_e) (test reliability = 1/(1+s_e^2))
#   est   = MEAN + SLOPE*theta + N(0, NOISE), then clipped to 0..100
# Part 1 varies MEAN and NOISE so that a growing share of estimates hits a bound.
# Part 2: with a real deficit sd = NOISE*clip(1 - c*theta, 0.4, 2.2) and no binding bounds,
#         which c gives Glejser r = -0.07, as a function of test reliability and of SLOPE?
# Needs numpy and scipy.
import numpy as np
from scipy import stats

N, REPS = 3500, 400

def glejser(score, est):
    sl, ic, *_ = stats.linregress(score, est)
    return stats.pearsonr(np.abs(est - (ic + sl * score)), score)

def run(mean, slope, noise, s_e, c, rng, clip=True):
    rs, ps, hit = [], [], []
    for _ in range(REPS):
        theta = rng.normal(0, 1, N)
        score = theta + rng.normal(0, s_e, N)
        sd = noise * np.clip(1 - c * theta, 0.4, 2.2)
        raw = mean + slope * theta + rng.normal(0, 1, N) * sd
        est = np.clip(raw, 0, 100) if clip else raw
        hit.append(np.mean((raw <= 0) | (raw >= 100)))
        r, p = glejser(score, est)
        rs.append(r); ps.append(p)
    rs, ps = np.array(rs), np.array(ps)
    return rs.mean(), np.mean(ps < .05), np.mean((ps < .05) & (rs < 0)), np.mean(hit)

rng = np.random.default_rng(20261006)
print(f'N={N}, REPS={REPS}')
print('PART 1: no deficit (c=0), slope 8, test reliability 0.5; estimates clipped to 0..100')
print(' mean  noise  share at a bound   mean Glejser r   share p<.05   share p<.05 with r<0')
for mean, noise in [(50, 6), (50, 20), (65, 15), (70, 15), (75, 15), (80, 15), (85, 15), (75, 25), (30, 15)]:
    r, p, pn, h = run(mean, 8, noise, 1.0, 0.0, rng)
    print(f'  {mean:3d}   {noise:3d}      {h:6.3f}          {r:+.4f}         {p:.3f}         {pn:.3f}')

print('PART 2: real deficit, bounds not binding (mean 50, noise 6): mean Glejser r by c')
print(' reliability  slope   ' + '   '.join(f'c={c:.2f}' for c in [0.05, 0.10, 0.15, 0.20, 0.30]))
for s_e, slope in [(1.0, 8), (0.5, 8), (0.0, 8), (1.5, 8), (1.0, 2), (1.0, 16)]:
    row = [run(50, slope, 6, s_e, c, rng, clip=False)[0] for c in [0.05, 0.10, 0.15, 0.20, 0.30]]
    print(f'    {1/(1+s_e**2):.2f}      {slope:3d}    ' + '  '.join(f'{x:+.4f}' for x in row))

