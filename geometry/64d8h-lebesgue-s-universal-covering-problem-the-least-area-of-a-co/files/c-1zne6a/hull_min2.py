# Numerical (not certified) minimum of the convex-hull area of a disk of diameter 1
# and further test sets of diameter 1, each placed by its own rigid motion.
# The true minimum is a lower bound for Lebesgue's constant (any convex cover contains
# a congruent copy of each set, hence the hull of some placement); a numerical minimum
# found here is an upper estimate of what that family of test sets can prove.
# Usage: python3 hull_min2.py SETS NSTARTS SEED
#   SETS: comma list from T (triangle), P (pentagon), R3, R5, R7, R9 (Reuleaux polygons)
import sys
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import differential_evolution, minimize

names, nstarts, seed = sys.argv[1].split(','), int(sys.argv[2]), int(sys.argv[3])
NS = 4000

def regular(n, R):
    a = np.pi / 2 + 2 * np.pi * np.arange(n) / n
    return np.c_[R * np.cos(a), R * np.sin(a)]

def reuleaux(n):
    R = 0.5 / np.sin(np.pi * (n - 1) / (2 * n))      # longest diagonal 1
    V = regular(n, R)
    pts = []
    for i in range(n):
        c = V[(i + (n + 1) // 2) % n]
        p, q = V[i], V[(i + 1) % n]
        a0, a1 = np.arctan2(*(p - c)[::-1]), np.arctan2(*(q - c)[::-1])
        if a1 < a0: a1 += 2 * np.pi
        if a1 - a0 > np.pi: a0, a1 = a1, a0 + 2 * np.pi
        pts.append(c + np.c_[np.cos(np.linspace(a0, a1, NS // n + 2)), np.sin(np.linspace(a0, a1, NS // n + 2))])
    return np.vstack(pts)

def make(name):
    if name == 'T': return regular(3, 1 / np.sqrt(3)), 2 * np.pi / 3
    if name == 'P': return regular(5, 0.5 / np.sin(2 * np.pi / 5)), 2 * np.pi / 5
    n = int(name[1:]); return reuleaux(n), 2 * np.pi / n

t = np.linspace(0, 2 * np.pi, NS, endpoint=False)
DISK = 0.5 * np.c_[np.cos(t), np.sin(t)]
sets = [make(n) for n in names]

def rot(P, th):
    c, s = np.cos(th), np.sin(th)
    return P @ np.array([[c, s], [-s, c]])

def diam(P):
    h = P[ConvexHull(P).vertices]
    return np.linalg.norm(h[:, None] - h[None], axis=2).max()

# the disk is rotation invariant, so the first set keeps angle 0: 2 + 3(k-1) parameters
def area(p):
    pts = [DISK, sets[0][0] + p[0:2]]
    for j, (S, _) in enumerate(sets[1:]):
        th, x, y = p[2 + 3 * j: 5 + 3 * j]
        pts.append(rot(S, th) + [x, y])
    return ConvexHull(np.vstack(pts)).volume

print('sets', names, 'diameters', ['%.6f' % diam(S) for S, _ in sets], 'areas', ['%.6f' % ConvexHull(S).volume for S, _ in sets])
bounds = [(-0.6, 0.6)] * 2
for S, period in sets[1:]:
    bounds += [(0, period), (-0.6, 0.6), (-0.6, 0.6)]
rng = np.random.default_rng(seed)
best = []
for s in range(nstarts):
    r = differential_evolution(area, bounds, seed=int(rng.integers(1 << 30)), tol=1e-10, maxiter=3000,
                               popsize=30, polish=False)
    r2 = minimize(area, r.x, method='Nelder-Mead', options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': 40000})
    best.append((r2.fun, r2.x))
    print('start %d: area %.7f at %s' % (s, r2.fun, np.array2string(r2.x, precision=6)))
    sys.stdout.flush()
best.sort(key=lambda z: z[0])
print('BEST %s %.7f' % (','.join(names), best[0][0]))
