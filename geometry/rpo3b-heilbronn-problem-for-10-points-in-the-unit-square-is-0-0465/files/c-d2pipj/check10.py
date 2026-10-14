# The best known 10-point Heilbronn configuration (Comellas and Yebra 2002), as tabulated in Appendix A of
# arXiv:2603.11107v2: points (x,0),(1-y,0),(0,x),(1,y),(1-z,z),(z,1-z),(0,1-y),(1,1-x),(y,1),(1-x,1)
# with x = z/2, y = 1 - 3z + 2z^2 and z near 0.3156.
# 1. Find z by maximising the smallest triangle area, and identify its minimal polynomial.
# 2. Check exactly (sympy, in Q(z)) which triangles have the minimum area and that it equals 5z^2/8 - z^3/2.
# 3. First-order test of local optimality: a linear program over all small moves of the 10 points that keep
#    them in the square; value 0 means no move increases all the smallest triangles to first order.
import itertools
import mpmath as mp
import numpy as np
import sympy as sp
from scipy.optimize import linprog

def pts(z):
    x = z / 2; y = 1 - 3*z + 2*z**2
    return [(x, 0), (1 - y, 0), (0, x), (1, y), (1 - z, z), (z, 1 - z), (0, 1 - y), (1, 1 - x), (y, 1), (1 - x, 1)]

def det2(P, i, j, k):
    (a, b), (c, d), (e, f) = P[i], P[j], P[k]
    return (c - a)*(f - b) - (e - a)*(d - b)

T = list(itertools.combinations(range(10), 3))
mp.mp.dps = 40
def minarea(z):
    P = pts(z)
    return min(abs(det2(P, *t)) for t in T) / 2

# 1. golden-section search on [0.30, 0.33]
a, b = mp.mpf('0.30'), mp.mpf('0.33')
g = (mp.sqrt(5) - 1) / 2
for _ in range(200):
    c, d = b - g*(b - a), a + g*(b - a)
    if minarea(c) > minarea(d): b = d
    else: a = c
z0 = (a + b) / 2
print('z maximising the smallest area: %s' % mp.nstr(z0, 20), ' smallest area: %s' % mp.nstr(minarea(z0), 20))
print('minimal polynomial found by mpmath.findpoly (degree <= 4):', mp.findpoly(z0, 4, maxcoeff=200, tol=1e-15))

# 2. exact check
zs = sp.symbols('z')
P = pts(zs)
areas = {t: sp.expand(det2(P, *t)) / 2 for t in T}
z0f = float(z0)
target = sp.Rational(5, 8)*zs**2 - sp.Rational(1, 2)*zs**3
num = {t: abs(float(areas[t].subs(zs, z0f))) for t in T}
m = min(num.values())
crit = [t for t in T if num[t] < m + 1e-9]
print('number of triangles with the minimum area (numerically):', len(crit), ' next smallest area: %.6f' % min(v for v in num.values() if v > m + 1e-9))
coef = mp.findpoly(z0, 4, maxcoeff=200, tol=1e-15)
minpoly = sp.Poly(sum(c*zs**(len(coef) - 1 - i) for i, c in enumerate(coef)), zs)
print('minimal polynomial irreducible over Q:', minpoly.is_irreducible)
ident, vanish = [], []
for t in crit:
    for sign in (1, -1):
        diff = sp.Poly(sp.expand(sign*areas[t] - target), zs)
        if diff.is_zero:
            ident.append(t); break
        if sp.rem(diff, minpoly).is_zero:
            vanish.append(t); break
print('critical triangles whose area equals 5z^2/8 - z^3/2 identically in z:', len(ident))
print('critical triangles whose area equals it only at the root (difference divisible by the minimal polynomial):', len(vanish))
print('critical triangles (0-based point numbers):', crit)
print('value 5z^2/8 - z^3/2 = %s' % mp.nstr(mp.mpf(5)/8*z0**2 - z0**3/2, 20))

# 3. first-order test
Pn = np.array([[float(v) if not hasattr(v, 'subs') else float(v.subs(zs, z0f)) for v in p] for p in pts(zs)])
def grad(i, j, k):
    g = np.zeros(20)
    (a_, b_), (c_, d_), (e_, f_) = Pn[i], Pn[j], Pn[k]
    s = np.sign((c_ - a_)*(f_ - b_) - (e_ - a_)*(d_ - b_))
    g[2*i] = -(f_ - b_) + (d_ - b_); g[2*i+1] = -(c_ - a_) + (e_ - a_)
    g[2*j] = (f_ - b_);             g[2*j+1] = -(e_ - a_)
    g[2*k] = -(d_ - b_);            g[2*k+1] = (c_ - a_)
    return s * g / 2
A_ub, b_ub = [], []
for t in crit:                       # eps - grad.d <= 0
    A_ub.append(np.concatenate([-grad(*t), [1.0]])); b_ub.append(0.0)
bounds = []
for i in range(10):
    for c in range(2):
        v = Pn[i, c]
        lo, hi = -1.0, 1.0
        if abs(v) < 1e-12: lo = 0.0
        if abs(v - 1) < 1e-12: hi = 0.0
        bounds.append((lo, hi))
bounds.append((None, None))
res = linprog(c=np.concatenate([np.zeros(20), [-1.0]]), A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=bounds, method='highs')
print('LP: largest first-order gain of the smallest area per unit move (0 = stationary): %.3e' % (-res.fun))
