# desi_loo.py - DESI DR2 BAO + compressed CMB prior: LCDM vs w0waCDM, leaving out one tracer at a time.
# Needs numpy and scipy, and the two DESI DR2 files (see URLs in the comment) in the working directory.
import sys
import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize
from scipy.stats import chi2 as chi2dist, norm

C_KMS = 299792.458
TCMB = 2.7255
OMEGA_GAMMA = 2.4729e-5 * (TCMB / 2.7255) ** 4      # photon density, Omega_gamma h^2
NEFF = 3.044
MNU = 0.06                                           # eV, one massive neutrino
NU_PER_SPECIES = 0.22711 * OMEGA_GAMMA               # (7/8)(4/11)^(4/3) per species
THETA_SHIFT = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0   # fractional shift of model theta*, robustness test

# BAO data: desi_gaussian_bao_ALL_GCcomb_mean.txt / _cov.txt from
# https://github.com/CobayaSampler/bao_data/tree/master/desi_bao_dr2
rows = [l.split() for l in open('mean.txt') if not l.startswith('#')]
Z = np.array([float(r[0]) for r in rows]); D = np.array([float(r[1]) for r in rows]); KIND = [r[2] for r in rows]
COV = np.loadtxt('cov.txt')
TRACERS = {'BGS': [0], 'LRG1': [1, 2], 'LRG2': [3, 4], 'LRG3+ELG1': [5, 6], 'ELG2': [7, 8], 'QSO': [9, 10], 'Lya': [11, 12]}

# CMB prior on (theta*, omega_b, omega_bc): DESI DR2 paper arXiv:2503.14738, Appendix A, Eqs. 35-36
MU = np.array([0.01041, 0.02223, 0.14208])
CC = 1e-9 * np.array([[0.006621, 0.12444, -1.1929], [0.12444, 21.344, -94.001], [-1.1929, -94.001, 1488.4]])
CCINV = np.linalg.inv(CC)


def nu_density(z):
    """omega_nu(z)/ (1+z)^4-scaled: 2.044 massless species + one of mass MNU (interpolation between relativistic and matter-like)."""
    a = 1.0 / (1.0 + z)
    tnu = 1.6803e-4 * (TCMB / 2.7255)                # k T_nu today in eV
    x = MNU * a / (3.151 * tnu)                      # mass / mean momentum
    massive = NU_PER_SPECIES * (NEFF / 3.0) * np.sqrt(1.0 + x * x)
    massless = NU_PER_SPECIES * (NEFF / 3.0) * 2.0
    return (massless + massive) * (1.0 + z) ** 4


def E2h2(z, h, wb, wbc, w0, wa):
    """H(z)^2 in units of (100 km/s/Mpc)^2, flat universe."""
    rad = OMEGA_GAMMA * (1 + z) ** 4 + nu_density(z)
    mat = wbc * (1 + z) ** 3
    today = OMEGA_GAMMA + nu_density(0.0) + wbc
    wde = h * h - today
    a = 1.0 / (1.0 + z)
    de = wde * a ** (-3 * (1 + w0 + wa)) * np.exp(-3 * wa * (1 - a))
    return rad + mat + de


def DH(z, *p):
    return C_KMS / (100.0 * np.sqrt(E2h2(z, *p)))


def DM(z, *p):
    return quad(lambda x: DH(x, *p), 0, z, epsrel=1e-9, limit=200)[0]


def r_drag(wb, wbc):
    # DESI DR2 paper Eq. 2
    return 147.05 * (wb / 0.02236) ** -0.13 * (wbc / 0.1432) ** -0.23 * (NEFF / 3.04) ** -0.1


def z_star(wb, wm):
    # Hu & Sugiyama (1996) fitting formula for the redshift of last scattering
    g1 = 0.0783 * wb ** -0.238 / (1 + 39.5 * wb ** 0.763)
    g2 = 0.560 / (1 + 21.1 * wb ** 1.81)
    return 1048 * (1 + 0.00124 * wb ** -0.738) * (1 + g1 * wm ** g2)


def theta_star(h, wb, wbc, w0, wa):
    p = (h, wb, wbc, w0, wa)
    zs = z_star(wb, wbc)
    def integrand(a):
        z = 1 / a - 1
        R = 0.75 * wb / OMEGA_GAMMA * a
        cs = C_KMS / np.sqrt(3 * (1 + R))
        return cs / (a * a * 100.0 * np.sqrt(E2h2(z, *p)))
    rs = quad(integrand, 0, 1 / (1 + zs), epsrel=1e-10, limit=200)[0]
    dm = quad(lambda x: DH(x, *p), 0, 5, epsrel=1e-10, limit=200)[0] + quad(lambda x: DH(x, *p), 5, zs, epsrel=1e-10, limit=200)[0]
    return rs / dm * (1 + THETA_SHIFT)


def chi2(params, keep, model):
    if model == 'lcdm':
        h, wb, wbc = params; w0, wa = -1.0, 0.0
    else:
        h, wb, wbc, w0, wa = params
        if not (-3 <= w0 <= 1 and -3 <= wa <= 2 and w0 + wa < 0):   # DESI priors
            return 1e6
    if not (0.4 < h < 1.0 and 0.015 < wb < 0.03 and 0.08 < wbc < 0.2):
        return 1e6
    p = (h, wb, wbc, w0, wa)
    if h * h - (OMEGA_GAMMA + nu_density(0.0) + wbc) <= 0:
        return 1e6
    rd = r_drag(wb, wbc)
    pred = np.empty(len(Z))
    for i in keep:
        if KIND[i] == 'DM_over_rs':
            pred[i] = DM(Z[i], *p) / rd
        elif KIND[i] == 'DH_over_rs':
            pred[i] = DH(Z[i], *p) / rd
        else:
            pred[i] = (Z[i] * DM(Z[i], *p) ** 2 * DH(Z[i], *p)) ** (1 / 3) / rd
    r = (D - pred)[keep]
    cb = r @ np.linalg.inv(COV[np.ix_(keep, keep)]) @ r
    v = np.array([theta_star(*p), wb, wbc]) - MU
    return cb + v @ CCINV @ v


def fit(keep, model):
    best = None
    starts = [[0.68, 0.0222, 0.142]] if model == 'lcdm' else [[0.64, 0.0222, 0.142, -0.45, -1.7], [0.67, 0.0222, 0.142, -0.9, -0.3], [0.66, 0.0222, 0.142, -0.7, -1.0]]
    for s in starts:
        r = minimize(chi2, s, args=(keep, model), method='Nelder-Mead', options={'xatol': 1e-7, 'fatol': 1e-7, 'maxiter': 20000, 'maxfev': 20000})
        r = minimize(chi2, r.x, args=(keep, model), method='Nelder-Mead', options={'xatol': 1e-8, 'fatol': 1e-8, 'maxiter': 20000, 'maxfev': 20000})
        if best is None or r.fun < best.fun:
            best = r
    return best


def sigma(dchi2, dof=2):
    return norm.isf(chi2dist.sf(dchi2, dof) / 2)


print(f'theta* shift applied: {THETA_SHIFT:+.4%}')
print(f'check: theta* at h=0.6736, wb=0.02237, wbc=0.1424, LCDM = {theta_star(0.6736, 0.02237, 0.1424, -1, 0) / (1 + THETA_SHIFT):.6f}, z* = {z_star(0.02237, 0.1424):.2f}, r_d = {r_drag(0.02237, 0.1424):.2f} Mpc')
print(f"{'left out':10s} {'N':>2s} {'chi2 LCDM':>9s} {'Om':>6s} {'H0':>6s} | {'chi2 w0wa':>9s} {'Om':>6s} {'H0':>6s} {'w0':>6s} {'wa':>6s} | {'dchi2':>6s} {'sigma':>5s}")
cases = [('none', [])] + [(k, v) for k, v in TRACERS.items()]
for name, drop in cases:
    keep = [i for i in range(len(Z)) if i not in drop]
    a = fit(keep, 'lcdm'); b = fit(keep, 'w0wa')
    om_a = (a.x[2] + MNU / 93.14) / a.x[0] ** 2; om_b = (b.x[2] + MNU / 93.14) / b.x[0] ** 2
    d = a.fun - b.fun
    print(f'{name:10s} {len(keep):2d} {a.fun:9.2f} {om_a:6.4f} {100 * a.x[0]:6.2f} | {b.fun:9.2f} {om_b:6.4f} {100 * b.x[0]:6.2f} {b.x[3]:6.2f} {b.x[4]:6.2f} | {d:6.2f} {sigma(d):5.2f}')
