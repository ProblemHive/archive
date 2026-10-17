# Number-count dipole of the Secrest et al. (2021) CatWISE2020 quasar sample.
# Own reimplementation (not the authors' code): masks, ecliptic-latitude correction,
# least-squares dipole (healpy.fit_dipole) and a Poisson maximum-likelihood fit.
# Usage: python3 dipole.py            (baseline + table of variants)
import sys
import numpy as np
import healpy as hp
from astropy.io import fits
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy.optimize import minimize

CAT = '/data/dipole/catwise_agns_masked_final_w1lt16p5_alpha.fits'
MASKS = '/data/dipole/MASKS_exclude_master_final.fits'
NHI, NLO = 1024, 64
C_KMS = 299792.458
V_CMB, L_CMB, B_CMB = 369.82, 264.021, 48.253   # Planck 2018 solar velocity and apex

d = fits.open(CAT, memmap=True)[1].data
l_all = np.asarray(d['l'], float); b_all = np.asarray(d['b'], float)
w1_all = np.asarray(d['w1'], float)
elat_all = np.asarray(d['elat'], float)
flux_all = np.asarray(d['k'], float) * np.asarray(d['nu_W1_iso'], float) ** np.asarray(d['alpha_W1'], float)
alpha_all = -np.asarray(d['alpha_W1'], float)          # S ~ nu^-alpha
pm = fits.open(MASKS)[1].data

def ps_mask(nside):
    """Point-source masks in Galactic coordinates, masked on one side only.
    Circles (pa <= 2, radius < 15 deg) as given; ellipses (pa > 2) approximated
    by a circle of their semi-major radius, which masks slightly more."""
    m = np.ones(hp.nside2npix(nside))
    sel = ((pm['pa'] <= 2) & (pm['radius'] < 15)) | (pm['pa'] > 2)
    c = SkyCoord(pm['ra'][sel] * u.deg, pm['dec'][sel] * u.deg, frame='icrs').galactic
    for lo, la, r in zip(c.l.deg, c.b.deg, pm['radius'][sel]):
        v = hp.ang2vec(lo, la, lonlat=True)
        m[hp.query_disc(nside, v, np.deg2rad(r))] = 0
    return m

PSHI = ps_mask(NHI)
_, BHI = hp.pix2ang(NHI, np.arange(hp.nside2npix(NHI)), lonlat=True)
plon, plat = hp.pix2ang(NLO, np.arange(hp.nside2npix(NLO)), lonlat=True)
ELAT_LO = SkyCoord(plon * u.deg, plat * u.deg, frame='galactic').barycentricmeanecliptic.lat.deg
PIXVEC = np.array(hp.pix2vec(NLO, np.arange(hp.nside2npix(NLO)))).T

def lo_mask(galcut):
    hi = PSHI * (np.abs(BHI) > galcut)
    lo = hp.ud_grade(hi, NLO)
    return (lo == 1).astype(float)

def vec2lb(v):
    lo, la = hp.vec2dir(v, lonlat=True)
    return lo % 360, la

def angsep(v, l, b):
    w = hp.ang2vec(l, b, lonlat=True)
    return np.degrees(np.arccos(np.clip(np.dot(v / np.linalg.norm(v), w), -1, 1)))

def measure(sel, galcut=30, eclcor=True, estimator='lsq'):
    l, b, el = l_all[sel], b_all[sel], elat_all[sel]
    mask = lo_mask(galcut)
    counts = np.bincount(hp.ang2pix(NLO, l, b, lonlat=True), minlength=hp.nside2npix(NLO)).astype(float)
    good = mask == 1
    slope = 0.0
    if eclcor:   # linear fit of counts per pixel against |ecliptic latitude|
        A = np.vstack([np.ones(good.sum()), np.abs(ELAT_LO[good])]).T
        coef = np.linalg.lstsq(A, counts[good], rcond=None)[0]
        slope = coef[1]
    if estimator == 'lsq':
        m = counts - slope * np.abs(ELAT_LO)
        m[~good] = hp.UNSEEN
        mono, dip = hp.fit_dipole(m)
        D = np.linalg.norm(dip) / mono; v = dip
    else:        # Poisson likelihood: mean = N0 (1 + e*|elat|) (1 + d.n)
        n = counts[good]; x = PIXVEC[good]; e = np.abs(ELAT_LO[good])
        def nll(p):
            mu = p[0] * (1 + p[1] * e) * (1 + x @ p[2:5])
            if np.any(mu <= 0): return 1e30
            return np.sum(mu - n * np.log(mu))
        p0 = np.array([n.mean(), 0.0 if not eclcor else slope / n.mean(), 0, 0, 0])
        if not eclcor:
            f = lambda q: nll(np.r_[q[0], 0.0, q[1:]])
            r = minimize(f, np.r_[p0[0], p0[2:]], method='Nelder-Mead',
                         options={'xatol': 1e-7, 'fatol': 1e-6, 'maxiter': 20000, 'maxfev': 20000})
            v = r.x[1:4]
        else:
            r = minimize(nll, p0, method='Nelder-Mead',
                         options={'xatol': 1e-7, 'fatol': 1e-6, 'maxiter': 40000, 'maxfev': 40000})
            v = r.x[2:5]
        D = np.linalg.norm(v)
    lo, la = vec2lb(v)
    return dict(N=int(sel.sum()), npix=int(good.sum()), D=D, l=lo, b=la, sep=angsep(v, L_CMB, B_CMB))

def kinematic(sel, w1cut):
    """Ellis-Baldwin expectation D = [2 + x(1+alpha)] v/c, with x the slope of
    the integral counts N(>S) ~ S^-x measured just above the cut (0.1 mag)."""
    S = flux_all[sel]
    s0 = S.min()
    n0 = len(S); n1 = np.sum(S > s0 * 10 ** (0.4 * 0.1))
    x = np.log(n0 / n1) / (0.4 * 0.1 * np.log(10))
    a = alpha_all[sel].mean()
    return x, a, (2 + x * (1 + a)) * V_CMB / C_KMS

if __name__ == '__main__':
    CUT164 = 8.52707e-28        # the authors' flux cut, W1 < 16.4
    base = flux_all > CUT164
    print('catalogue rows', len(l_all), '; with flux > W1=16.4 cut:', base.sum(), '; max w1 there %.4f' % w1_all[base].max())
    x, a, Dk = kinematic(base, 16.4)
    print('kinematic expectation: x = %.3f, mean alpha = %.3f, D_kin = %.5f' % (x, a, Dk))
    r = measure(base)
    print('BASELINE lsq, |b|>30, ecl. corr.: N=%d pix=%d D=%.5f (l,b)=(%.1f,%.1f) sep CMB %.1f deg  D/D_kin=%.2f'
          % (r['N'], r['npix'], r['D'], r['l'], r['b'], r['sep'], r['D'] / Dk))
    print()
    print('%-6s %-5s %-4s %-7s %8s %7s %8s %6s %6s %6s %6s' % ('w1<', 'gal', 'ecl', 'est', 'N', 'D', 'D_kin', 'ratio', 'l', 'b', 'sep'))
    for w1cut in [16.0, 16.2, 16.4, 16.5]:
        sel = (w1_all < w1cut) if w1cut != 16.4 else base
        x, a, Dk = kinematic(sel, w1cut)
        for gal in [20, 30, 40]:
            for ecl in [True, False]:
                for est in (['lsq', 'poisson'] if gal == 30 else ['lsq']):
                    if est == 'poisson' and not ecl and w1cut != 16.4: continue
                    r = measure(sel, gal, ecl, est)
                    print('%-6.1f %-5d %-4s %-7s %8d %7.5f %8.5f %6.2f %6.1f %6.1f %6.1f' %
                          (w1cut, gal, 'y' if ecl else 'n', est, r['N'], r['D'], Dk, r['D'] / Dk, r['l'], r['b'], r['sep']))
        sys.stdout.flush()
