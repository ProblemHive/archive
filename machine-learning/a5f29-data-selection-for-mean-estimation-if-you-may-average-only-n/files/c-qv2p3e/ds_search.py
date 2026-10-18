"""Lower bounds for F(d, n) = sup_D L*_D(n) / L*_D in data selection for mean estimation
(Hanneke, Moran, Shlimovich, Yehudayoff, arXiv:2504.14572, Section 5; COLT 2025 open problem).

D is a finitely supported distribution on R^d: points z_1..z_k with weights w_i > 0 (a multiset with
rational weights is the same up to density). The learner averages n points of the support, repetitions
allowed (as in the paper's proof of Theorem 1). By L_D(h) = L*_D + |h - mu|^2,
    F(d, n) = 1 + sup_D  min_{S}  |avg(S) - mu|^2 / V,   V = sum w_i |z_i - mu|^2,
over multisets S of size n from {1..k}. We maximise R = min_S |avg(S) - mu|^2 / V numerically
(SLSQP on the epigraph form, many random starts), then round the best configuration to rationals and
evaluate R exactly with fractions, which gives a rigorous lower bound F >= 1 + R_exact.

Usage: python3 -u ds_search.py d n kmin kmax starts seed
"""
import sys, itertools, numpy as np
from fractions import Fraction
from scipy.optimize import minimize

d, n, kmin, kmax, starts, seed = map(int, sys.argv[1:7])
rng = np.random.default_rng(seed)

def unpack(x, k):
    z = x[:k * d].reshape(k, d)
    a = x[k * d:k * d + k]
    w = np.exp(a - a.max()); w /= w.sum()
    return z, w, x[-1]

def solve(k):
    S = np.array([np.bincount(c, minlength=k) for c in itertools.combinations_with_replacement(range(k), n)]) / n
    def parts(x):
        z, w, t = unpack(x, k)
        mu = w @ z
        V = w @ ((z - mu) ** 2).sum(1)
        g = ((S @ z - mu) ** 2).sum(1)
        return g, V, t
    cons = [{"type": "ineq", "fun": lambda x: (lambda g, V, t: g - t * V)(*parts(x))},
            {"type": "eq", "fun": lambda x: parts(x)[1] - 1.0}]
    best = (-1, None)
    for _ in range(starts):
        z0 = rng.normal(size=(k, d)); a0 = rng.normal(size=k)
        x0 = np.concatenate([z0.ravel(), a0, [0.0]])
        z, w, _t = unpack(x0, k); mu = w @ z; V = w @ ((z - mu) ** 2).sum(1)
        x0[:k * d] = ((z - mu) / np.sqrt(V)).ravel()
        r = minimize(lambda x: -x[-1], x0, constraints=cons, method="SLSQP",
                     options={"maxiter": 2000, "ftol": 1e-12})
        g, V, t = parts(r.x)
        R = g.min() / V
        if R > best[0]:
            best = (R, r.x.copy())
    return best, S

def exact(z, w):
    """R for the rounded configuration, in exact rational arithmetic"""
    k = len(w)
    zq = [[Fraction(float(v)).limit_denominator(10**6) for v in row] for row in z]
    wq = [Fraction(float(v)).limit_denominator(10**6) for v in w]
    tot = sum(wq); wq = [v / tot for v in wq]
    mu = [sum(wq[i] * zq[i][j] for i in range(k)) for j in range(d)]
    V = sum(wq[i] * sum((zq[i][j] - mu[j]) ** 2 for j in range(d)) for i in range(k))
    m = None
    for c in itertools.combinations_with_replacement(range(k), n):
        avg = [sum(zq[i][j] for i in c) / n for j in range(d)]
        g = sum((avg[j] - mu[j]) ** 2 for j in range(d))
        m = g if m is None or g < m else m
    return m / V

overall = (-1, None, None)
for k in range(kmin, kmax + 1):
    (R, x), S = solve(k)
    print(f"d={d} n={n} k={k}: best R = {R:.8f}  (F >= {1 + R:.8f})", flush=True)
    if R > overall[0]:
        overall = (R, k, x)
R, k, x = overall
z, w, _ = unpack(x, k)
mu = w @ z
print(f"best over k: k={k}, R = {R:.10f}, F >= {1 + R:.10f}")
print("support points (centred, V = 1) and weights:")
for i in np.argsort(-w):
    print("  z =", np.round(z[i] - mu, 6), " w =", round(float(w[i]), 6))
Rq = exact(z, w)
print(f"exact R of the configuration rounded to rationals: {Rq} = {float(Rq):.10f}; certified F({d},{n}) >= {float(1 + Rq):.10f}")
