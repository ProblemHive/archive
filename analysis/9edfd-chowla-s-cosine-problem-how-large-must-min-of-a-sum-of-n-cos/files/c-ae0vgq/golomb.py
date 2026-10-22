"""K(A) for A = set of positive differences of a Golomb ruler (a Sidon set), as in the sqrt(n) upper-bound construction.
Each ruler is first checked: all pairwise differences must be distinct.  K(A) = -min_x sum cos(a x), found on a fine
grid of [0, pi] and refined at every grid local minimum (bounded scalar minimisation)."""
import itertools
import numpy as np
from scipy.optimize import minimize_scalar

rulers = {
    3: [0, 1, 3],
    4: [0, 1, 4, 6],
    5: [0, 1, 4, 9, 11],
    6: [0, 1, 4, 10, 12, 17],
    7: [0, 1, 4, 10, 18, 23, 25],
    8: [0, 1, 4, 9, 15, 22, 32, 34],
    9: [0, 1, 5, 12, 25, 27, 35, 41, 44],
    10: [0, 1, 6, 10, 23, 26, 34, 41, 53, 55],
}

def K(A):
    A = np.array(sorted(A), float)
    G = 200 * int(A.max())
    xs = (np.arange(G) + 0.5) * np.pi / G
    v = np.zeros(G)
    for a in A:
        v += np.cos(a * xs)
    f = lambda t: np.cos(A * t).sum()
    best = v.min()
    for i in range(G):
        if v[i] <= v[max(i - 1, 0)] and v[i] <= v[min(i + 1, G - 1)] and v[i] < 0:
            lo = 0.0 if i == 0 else xs[i - 1]
            hi = np.pi if i == G - 1 else xs[i + 1]
            r = minimize_scalar(f, bounds=(lo, hi), method="bounded", options={"xatol": 1e-13})
            best = min(best, r.fun)
    return -best

print("marks  n=|A|  max(A)   K(A)    K/sqrt(n)")
for m, R in rulers.items():
    D = [b - a for a, b in itertools.combinations(R, 2)]
    assert len(set(D)) == len(D), f"not a Golomb ruler: {R}"
    A = sorted(D)
    n = len(A)
    k = K(A)
    print(f"{m:5d} {n:6d} {max(A):7d} {k:9.6f} {k / n ** 0.5:8.4f}")

