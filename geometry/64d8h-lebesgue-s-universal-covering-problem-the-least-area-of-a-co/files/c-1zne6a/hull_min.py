# Numerical (not certified) minimum of the convex-hull area of three test sets of
# diameter 1 placed independently by rigid motions: a disk, and two more sets.
# Any convex universal cover contains a congruent copy of each, hence the hull of
# some placement, so the true minimum is a lower bound for Lebesgue's constant;
# a numerical minimum found here is an upper estimate of what that test set can prove.
# Usage: python3 hull_min.py FAMILY NSTARTS SEED     FAMILY = polygons | reuleaux
import sys
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import differential_evolution, minimize

fam, nstarts, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
NS = 4000  # boundary samples per curved piece

def regular(n, R):
    a = np.pi / 2 + 2 * np.pi * np.arange(n) / n
    return np.c_[R * np.cos(a), R * np.sin(a)]

def reuleaux(n):
    # regular n-gon (n odd) whose longest diagonal is 1; each arc has radius 1 and is
    # centred at the vertex opposite it
    R = 0.5 / np.sin(np.pi * (n - 1) / (2 * n))
    V = regular(n, R)
    pts = []
    for i in range(n):
        c = V[(i + (n + 1) // 2) % n]          # opposite vertex
        p, q = V[i], V[(i + 1) % n]
        a0, a1 = np.arctan2(*(p - c)[::-1]), np.arctan2(*(q - c)[::-1])
        if a1 < a0: a1 += 2 * np.pi
        if a1 - a0 > np.pi: a0, a1 = a1, a0 + 2 * np.pi
        t = np.linspace(a0, a1, NS // n + 2)
        pts.append(c + np.c_[np.cos(t), np.sin(t)])
    P = np.vstack(pts)
    return P - P.mean(0) * 0  # keep the polygon's centre at the origin

t = np.linspace(0, 2 * np.pi, NS, endpoint=False)
DISK = 0.5 * np.c_[np.cos(t), np.sin(t)]
if fam == 'polygons':
    A = regular(3, 1 / np.sqrt(3))                     # equilateral triangle, side 1
    B = regular(5, 0.5 / np.sin(2 * np.pi / 5))        # regular pentagon, diagonal 1
    rotA, rotB = 2 * np.pi / 3, 2 * np.pi / 5
elif fam == 'reuleaux':
    A, B = reuleaux(3), reuleaux(5)
    rotA, rotB = 2 * np.pi / 3, 2 * np.pi / 5
else:
    raise SystemExit('family?')

def diam(P):
    h = P[ConvexHull(P).vertices]
    return max(np.linalg.norm(h[:, None] - h[None], axis=2).max(), 0)

def rot(P, th):
    c, s = np.cos(th), np.sin(th)
    return P @ np.array([[c, s], [-s, c]])

# the disk is rotation invariant about its centre, so the whole picture may be turned
# until set A has angle 0: parameters are A's offset and B's angle and offset
def area(p):
    xa, ya, thb, xb, yb = p
    pts = np.vstack([DISK, A + [xa, ya], rot(B, thb) + [xb, yb]])
    return ConvexHull(pts).volume

print('family', fam, 'diameters: disk %.6f A %.6f B %.6f' % (diam(DISK), diam(A), diam(B)))
print('areas of the sets: disk %.6f A %.6f B %.6f' % (ConvexHull(DISK).volume, ConvexHull(A).volume, ConvexHull(B).volume))
bounds = [(-0.6, 0.6), (-0.6, 0.6), (0, rotB), (-0.6, 0.6), (-0.6, 0.6)]
best = []
rng = np.random.default_rng(seed)
for s in range(nstarts):
    r = differential_evolution(area, bounds, seed=int(rng.integers(1 << 30)), tol=1e-10, maxiter=3000,
                               popsize=30, polish=False)
    r2 = minimize(area, r.x, method='Nelder-Mead', options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': 20000})
    best.append((r2.fun, r2.x))
    print('start %d: area %.7f at %s' % (s, r2.fun, np.array2string(r2.x, precision=6)))
    sys.stdout.flush()
best.sort(key=lambda z: z[0])
print('BEST %.7f at %s' % (best[0][0], np.array2string(best[0][1], precision=8)))
