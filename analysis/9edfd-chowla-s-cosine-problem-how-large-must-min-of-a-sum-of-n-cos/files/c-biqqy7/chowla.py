"""Chowla cosine problem, small cases.
K(A) = -min_x sum_{a in A} cos(a x).  For each n and bound N: the minimum of K(A) over n-subsets A of {1..N}.
Exhaustive search with a grid prefilter (grid value <= true value, error <= n*N^2*h^2/8), then exact refinement
of every set whose grid value is within that error of the best.
usage: python chowla.py n N
"""
import sys, itertools
import numpy as np
from scipy.optimize import minimize_scalar

n = int(sys.argv[1]); N = int(sys.argv[2])
G = 24 * N
x = (np.arange(G) + 0.5) * np.pi / G          # f is even and 2pi-periodic: [0, pi] suffices
h = np.pi / G
T = np.cos(np.outer(np.arange(1, N + 1), x))  # N x G
tol = n * N * N * h * h / 8 + 1e-12

def exact_K(A):
    A = np.array(A)
    f = lambda t: np.cos(A * t).sum()
    xs = (np.arange(G) + 0.5) * np.pi / G
    v = np.cos(np.outer(xs, A)).sum(1)
    best = v.min()
    idx = [i for i in range(G) if v[i] <= v[max(i - 1, 0)] and v[i] <= v[min(i + 1, G - 1)] and v[i] <= best + 0.5]
    for i in idx:
        lo = 0.0 if i == 0 else xs[i - 1]
        hi = np.pi if i == G - 1 else xs[i + 1]
        r = minimize_scalar(f, bounds=(lo, hi), method='bounded', options={'xatol': 1e-13})
        best = min(best, r.fun)
    return -best

combos = itertools.combinations(range(N), n)
CH = 20000
cands = []   # (grid value, set)
gbest = 1e9
while True:
    chunk = list(itertools.islice(combos, CH))
    if not chunk: break
    idx = np.array(chunk)
    F = T[idx[:, 0]].copy()
    for j in range(1, n): F += T[idx[:, j]]
    g = -F.min(1)
    gbest = min(gbest, g.min())
    keep = np.nonzero(g <= gbest + tol)[0]
    for k in keep: cands.append((g[k], tuple(int(v) + 1 for v in idx[k])))
    if len(cands) > 200000: cands = [c for c in cands if c[0] <= gbest + tol]
cands = [c for c in cands if c[0] <= gbest + tol]
res = sorted((exact_K(A), A) for _, A in cands)
print(f"n={n} N={N} sets within grid tolerance: {len(cands)} grid-best {gbest:.6f}")
for v, A in res[:5]: print(f"  K={v:.9f}  A={A}")

