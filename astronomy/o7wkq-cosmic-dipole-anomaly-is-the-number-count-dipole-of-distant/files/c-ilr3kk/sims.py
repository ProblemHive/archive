# Shot-noise-only simulations on the real masks: Poisson counts per pixel with the
# kinematic dipole (D_kin, CMB direction) and the measured ecliptic slope, fitted
# exactly as the data are by dipole.measure-like least squares at |b|>30 and |b|>40.
# No clustering dipole and no source-level selection: a lower bound on the scatter.
# Usage: python3 sims.py NSIM SEED
import sys
import numpy as np
import healpy as hp
import dipole as dp

nsim, seed = int(sys.argv[1]), int(sys.argv[2])
rng = np.random.default_rng(seed)
sel = dp.flux_all > 8.52707e-28
_, _, Dk = dp.kinematic(sel, 16.4)
counts = np.bincount(hp.ang2pix(dp.NLO, dp.l_all[sel], dp.b_all[sel], lonlat=True),
                     minlength=hp.nside2npix(dp.NLO)).astype(float)
masks = {g: dp.lo_mask(g) for g in (30, 40)}
good = masks[30] == 1
A = np.vstack([np.ones(good.sum()), np.abs(dp.ELAT_LO[good])]).T
c0, c1 = np.linalg.lstsq(A, counts[good], rcond=None)[0]
ecl = np.abs(dp.ELAT_LO)
nhat = hp.ang2vec(dp.L_CMB, dp.B_CMB, lonlat=True)
mu = (c0 + c1 * ecl) * (1 + Dk * dp.PIXVEC @ nhat)

def fit(m, mask):
    g = mask == 1
    A = np.vstack([np.ones(g.sum()), ecl[g]]).T
    s = np.linalg.lstsq(A, m[g], rcond=None)[0][1]
    x = m - s * ecl
    x[~g] = hp.UNSEEN
    mono, dip = hp.fit_dipole(x)
    return np.linalg.norm(dip) / mono

data = {g: fit(counts, masks[g]) for g in (30, 40)}
res = np.array([[fit(rng.poisson(mu).astype(float), masks[g]) for g in (30, 40)] for _ in range(nsim)])
print('D_kin %.5f; data D30 %.5f D40 %.5f diff %.5f' % (Dk, data[30], data[40], data[30] - data[40]))
for i, g in enumerate((30, 40)):
    r = res[:, i]
    print('|b|>%d: sims mean %.5f sd %.5f; sims with D >= data: %d of %d; (data-mean)/sd = %.1f'
          % (g, r.mean(), r.std(), (r >= data[g]).sum(), nsim, (data[g] - r.mean()) / r.std()))
dd = res[:, 0] - res[:, 1]
print('D30-D40 in sims: mean %.5f sd %.5f; data diff is %.1f sd from the mean'
      % (dd.mean(), dd.std(), (data[30] - data[40] - dd.mean()) / dd.std()))
