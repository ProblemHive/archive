# Electric field in a four-shell concentric-sphere head model (brain, CSF, skull, scalp)
# for two circular scalp electrodes with uniform current density, by the Legendre series
# solution of Laplace's equation in each shell (quasi-static, isotropic conductivities).
# Prints |E| per 1 mA (amplitude of the current, same convention as the input) at
# several depths below the brain surface, under one electrode and midway between them.
# Usage: python3 sphere_field.py           (prints a table; no arguments)
import numpy as np

NMAX = 400

def legendre_all(nmax, x):
    """P_0..P_nmax at points x (array), by the three-term recurrence."""
    x = np.asarray(x, float)
    P = np.zeros((nmax + 2,) + x.shape)
    P[0] = 1.0
    P[1] = x
    for n in range(1, nmax + 1):
        P[n + 1] = ((2 * n + 1) * x * P[n] - n * P[n - 1]) / (n + 1)
    return P

def basis(k, n, r, radii):
    """Scaled radial functions in shell k: a = (r/rout)^n, b = (rin/r)^(n+1), and their r-derivatives.
    Both are at most 1 inside the shell, so nothing over- or underflows."""
    rout = radii[k]; rin = radii[k - 1] if k > 0 else 0.0
    a = (r / rout) ** n; da = n / r * a
    if k == 0:
        return a, da, 0.0, 0.0
    b = (rin / r) ** (n + 1); db = -(n + 1) / r * b
    return a, da, b, db

def shell_coeffs(radii, sig, n):
    """Coefficients (A_k, B_k) of the scaled functions in each shell for degree n, normalised so
    that sigma_scalp dV/dr = 1 at the outer surface (inward current density 1)."""
    K = len(radii)
    cols = {0: (0, None)}
    for k in range(1, K):
        cols[k] = (2 * k - 1, 2 * k)
    M = np.zeros((2 * K - 1, 2 * K - 1)); rhs = np.zeros(2 * K - 1)
    row = 0
    for k in range(K - 1):
        r = radii[k]
        ai, dai, bi, dbi = basis(k, n, r, radii)
        ao, dao, bo, dbo = basis(k + 1, n, r, radii)
        (ca, cb), (oa, ob) = cols[k], cols[k + 1]
        M[row, ca] += ai
        if cb is not None: M[row, cb] += bi
        M[row, oa] -= ao; M[row, ob] -= bo
        row += 1
        M[row, ca] += sig[k] * dai
        if cb is not None: M[row, cb] += sig[k] * dbi
        M[row, oa] -= sig[k + 1] * dao; M[row, ob] -= sig[k + 1] * dbo
        row += 1
    a, da, b, db = basis(K - 1, n, radii[-1], radii)
    oa, ob = cols[K - 1]
    M[row, oa] = sig[-1] * da; M[row, ob] = sig[-1] * db; rhs[row] = 1.0
    x = np.linalg.solve(M, rhs)
    return [(x[0], 0.0)] + [(x[2 * k - 1], x[2 * k]) for k in range(1, K)]

_cache = {}
def coeffs(radii, sig, n):
    key = (tuple(radii), tuple(sig), n)
    if key not in _cache:
        _cache[key] = shell_coeffs(radii, sig, n)
    return _cache[key]

def potential_one(radii, sig, I, alpha, r, cos_gamma):
    """Potential at radius r and angle gamma from the centre of a cap electrode of half-angle
    alpha carrying current I into the head with uniform density. Degree 0 is left out: it
    cancels between the two electrodes."""
    R = radii[-1]
    J0 = I / (2 * np.pi * R ** 2 * (1 - np.cos(alpha)))
    Pc = legendre_all(NMAX + 1, np.array(np.cos(alpha)))
    Pg = legendre_all(NMAX, cos_gamma)
    k = int(np.searchsorted(radii, r))
    V = np.zeros_like(np.asarray(cos_gamma, float))
    for n in range(1, NMAX + 1):
        cn = J0 * (Pc[n - 1] - Pc[n + 1]) / 2.0
        A, B = coeffs(radii, sig, n)[k]
        a, _, b, _ = basis(k, n, r, radii)
        V = V + cn * (A * a + B * b) * Pg[n]
    return V

def field(radii, sig, I, alpha, e1, e2, pts):
    """|E| (V/m) at points pts (N x 3, metres) for +I at electrode centre e1 and -I at e2."""
    h = 1e-5
    def V(p):
        out = np.zeros(len(p))
        for i, q in enumerate(p):
            r = np.linalg.norm(q); u = q / r
            out[i] = (potential_one(radii, sig, I, alpha, r, u @ e1)
                      - potential_one(radii, sig, I, alpha, r, u @ e2))
        return out
    E = np.zeros_like(pts)
    for d in range(3):
        dp = np.zeros(3); dp[d] = h
        E[:, d] = -(V(pts + dp) - V(pts - dp)) / (2 * h)
    return np.linalg.norm(E, axis=1)

if __name__ == '__main__':
    radii = np.array([0.080, 0.082, 0.087, 0.092])        # outer radii of brain, CSF, skull, scalp (m)
    I = 1e-3                                               # 1 mA
    area = 35e-4                                           # 5 x 7 cm electrode, as a disk of equal area
    alpha = np.sqrt(area / np.pi) / radii[-1]
    print('radii (cm)', radii * 100, ' electrode cap radius %.2f cm, half-angle %.3f rad' % (np.sqrt(area / np.pi) * 100, alpha))
    # check: homogeneous sphere, total current through the plane midway between opposite electrodes
    # must equal I (current conservation)
    e1 = np.array([0, 0, 1.0])
    for sep_deg in (90, 180):
        s = np.radians(sep_deg)
        e2 = np.array([np.sin(s), 0, np.cos(s)])
        mid = e1 + e2
        mid = mid / np.linalg.norm(mid) if np.linalg.norm(mid) > 1e-9 else np.array([1.0, 0, 0])
        for sig_skull in (0.0042, 0.01, 0.02):
            sig = np.array([0.33, 1.65, sig_skull, 0.43])
            depths = np.array([0.001, 0.005, 0.010, 0.020])
            rs = radii[0] - depths
            under = field(radii, sig, I, alpha, e1, e2, np.outer(rs, e1))
            between = field(radii, sig, I, alpha, e1, e2, np.outer(rs, mid))
            print('sep %3d deg  skull %.4f S/m  |E| per mA (V/m) at depth 1/5/10/20 mm: under electrode %s  midway %s'
                  % (sep_deg, sig_skull, np.array2string(under, precision=3), np.array2string(between, precision=3)))
    # check against the closed form for a homogeneous sphere is not available for caps; instead
    # check current conservation: flux of sigma*E through the equatorial plane for opposite electrodes
    sig = np.array([0.33, 0.33, 0.33, 0.33])
    e2 = np.array([0, 0, -1.0])
    rr = np.linspace(0.0005, radii[-1] - 0.0005, 60)
    pts = np.c_[rr, np.zeros_like(rr), np.zeros_like(rr)]
    h = 1e-5
    def Vz(p):
        return np.array([potential_one(radii, sig, I, alpha, np.linalg.norm(q), (q / np.linalg.norm(q)) @ e1)
                         - potential_one(radii, sig, I, alpha, np.linalg.norm(q), (q / np.linalg.norm(q)) @ e2) for q in p])
    Ez = -(Vz(pts + [0, 0, h]) - Vz(pts - [0, 0, h])) / (2 * h)
    flux = np.trapezoid(sig[0] * Ez * 2 * np.pi * rr, rr)
    print('check, homogeneous sphere: current through the midplane %.4f mA (should be about 1, magnitude)' % (abs(flux) * 1e3))
