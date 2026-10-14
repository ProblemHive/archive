# Dunning-Kruger: do the classical quartile plot, the Glejser test and the quadratic term
# tell a model with a real skill-dependent deficit apart from models with none?
# Simulated people take a 20-item test and estimate their own score (0..20).
#   A  no deficit, no bounds : estimate = prior + k*(score + noise - prior), same noise for everyone
#   B  no deficit, bounded   : as A, then rounded and clipped to 0..20 (what a real answer scale does)
#   C  real deficit, bounded : as B, but the noise is larger for people of lower skill
# Needs numpy and scipy.
import numpy as np
from scipy import stats

N, ITEMS, REPS = 3500, 20, 300
PRIOR, K, SD = 13.0, 0.45, 5.0
diff = np.linspace(-2.0, 2.0, ITEMS)

def sample(model, rng):
    theta = rng.normal(0, 1, N)
    p = 1 / (1 + np.exp(-1.3 * (theta[:, None] - diff[None, :])))
    score = (rng.random((N, ITEMS)) < p).sum(1).astype(float)
    sd = np.full(N, SD)
    if model == 'C':
        sd = SD * np.clip(1 - 0.4 * theta, 0.4, 2.2)       # low skill -> noisier impression of own score
    est = PRIOR + K * (score + rng.normal(0, 1, N) * sd - PRIOR)
    if model in 'BC':
        est = np.clip(np.round(est), 0, ITEMS)
    return score, est

def tests(score, est):
    sl, ic, r, _, _ = stats.linregress(score, est)
    resid = est - (ic + sl * score)
    g_r, g_p = stats.pearsonr(np.abs(resid), score)          # Glejser: |residual| against ability
    X1 = np.column_stack([np.ones(N), score])
    X2 = np.column_stack([np.ones(N), score, score ** 2])
    rss1 = ((est - X1 @ np.linalg.lstsq(X1, est, rcond=None)[0]) ** 2).sum()
    b2 = np.linalg.lstsq(X2, est, rcond=None)[0]
    rss2 = ((est - X2 @ b2) ** 2).sum()
    tss = ((est - est.mean()) ** 2).sum()
    F = (rss1 - rss2) / (rss2 / (N - 3))
    q_p = stats.f.sf(F, 1, N - 3)
    order = np.argsort(score, kind='stable')
    q = np.array_split(order, 4)
    gaps = [est[i].mean() - score[i].mean() for i in q]      # classical plot: over-estimate by quartile
    return r, g_r, g_p, (rss1 - rss2) / tss, b2[2], q_p, gaps

rng = np.random.default_rng(20261006)
print(f'n = {N} per sample, {REPS} samples per model, {ITEMS} items; prior {PRIOR}, weight on evidence {K}, noise sd {SD}')
print('model  r(score,est)  over-estimate by score quartile (Q1 lowest .. Q4)   Glejser r   share p<.05   quad dR2   quad coef   share p<.05')
for model in 'ABC':
    out = [tests(*sample(model, rng)) for _ in range(REPS)]
    r = np.mean([o[0] for o in out]); gr = np.mean([o[1] for o in out]); gp = np.mean([o[2] < .05 for o in out])
    dr = np.mean([o[3] for o in out]); qc = np.mean([o[4] for o in out]); qp = np.mean([o[5] < .05 for o in out])
    gaps = np.mean([o[6] for o in out], axis=0)
    print(f'  {model}       {r:.3f}      ' + '  '.join(f'{g:+6.2f}' for g in gaps) + f'              {gr:+.3f}      {gp:.2f}       {dr:.4f}    {qc:+.4f}      {qp:.2f}')
