"""Numerical search for the largest S(P) in Smale's mean value conjecture.

Normalisation: P(0) = 0, P'(0) = 1, so P'(t) = prod_i (1 - t/b_i) with
critical points b_1..b_{d-1} (all nonzero). S(P) = min_i |P(b_i) / b_i|.
Conjecture: S(P) <= (d-1)/d, equality for P(z) = z - z^d/d (b_i = roots of unity).
S is invariant under b -> lambda*b (complex lambda), so b_1 = 1 is fixed and the
search runs over b_2..b_{d-1} (2(d-2) real parameters), in log-polar coordinates.

Method: for each random start (fixed seed), a short Nelder-Mead on -S, then
SLSQP on the smooth epigraph form: maximise t subject to |P(b_i)/b_i|^2 >= t^2
for every i. The best value is re-evaluated with mpmath at 50 digits.
Usage: python smvc_search.py d starts seed
"""
import sys
import numpy as np
from scipy.optimize import minimize
import mpmath as mp
import warnings

warnings.filterwarnings("ignore")
LOGR = 6.0   # critical points kept within a factor e^6 (about 400) of b_1 = 1


def ratios(b):
    # P'(t) = prod (1 - t/b_i); returns the list |P(b_i)/b_i|
    c = np.array([1.0 + 0j])
    for bi in b:
        c = np.convolve(c, np.array([1.0, -1.0 / bi]))
    q = c / np.arange(1, len(c) + 1)          # P(z)/z = sum q_k z^k
    return np.array([abs(np.polyval(q[::-1], bi)) for bi in b])


def params_to_b(x, d):
    m = d - 2
    r = np.exp(np.clip(x[:m], -LOGR, LOGR))
    th = x[m:]
    return np.concatenate([[1.0 + 0j], r * np.exp(1j * th)])


def S_mp(b):
    mp.mp.dps = 50
    bb = [mp.mpc(complex(z).real, complex(z).imag) for z in b]
    c = [mp.mpc(1)]
    for bi in bb:
        n = [mp.mpc(0)] * (len(c) + 1)
        for k, ck in enumerate(c):
            n[k] += ck
            n[k + 1] -= ck / bi
        c = n
    out = []
    for bi in bb:
        s = mp.mpc(0)
        for k, ck in enumerate(c):
            s += ck * bi ** k / (k + 1)
        out.append(abs(s))
    return min(out)


def polish(x, d):
    y0 = np.concatenate([x, [ratios(params_to_b(x, d)).min()]])
    cons = {"type": "ineq",
            "fun": lambda y: ratios(params_to_b(y[:-1], d)) ** 2 - y[-1] ** 2}
    m = d - 2
    bounds = [(-LOGR, LOGR)] * m + [(None, None)] * m + [(0, None)]
    r = minimize(lambda y: -y[-1], y0, method="SLSQP", constraints=[cons],
                 bounds=bounds, options={"maxiter": 500, "ftol": 1e-14})
    xs = r.x[:-1]
    return ratios(params_to_b(xs, d)).min(), xs


def main():
    d = int(sys.argv[1]); starts = int(sys.argv[2]); seed = int(sys.argv[3])
    rng = np.random.default_rng(seed)
    m = d - 2
    f = lambda x: -ratios(params_to_b(x, d)).min()
    results = []
    for s in range(starts):
        x0 = np.concatenate([rng.normal(0, 0.7, m), rng.uniform(-np.pi, np.pi, m)])
        r = minimize(f, x0, method="Nelder-Mead", options={"maxiter": 300 * m})
        v, x = polish(r.x, d)
        if not np.isfinite(v):
            continue
        results.append((v, x))
    results.sort(key=lambda t: -t[0])
    vals = np.array([v for v, _ in results])
    target = (d - 1) / d
    print(f"d={d} starts={starts} seed={seed} conjectured max (d-1)/d = {target:.12f}")
    print(f"best S found (double) = {vals[0]:.12f}; starts ending within 1e-6 of (d-1)/d: {(np.abs(vals - target) < 1e-6).sum()} of {len(vals)}")
    print(f"starts with S > (d-1)/d + 1e-9: {(vals > target + 1e-9).sum()}")
    uniq = []
    for v in vals:
        if all(abs(v - u) > 1e-6 for u in uniq):
            uniq.append(v)
    print("largest distinct local values:", ", ".join(f"{u:.8f}" for u in uniq[:8]))
    v, x = results[0]
    b = params_to_b(x, d)
    print(f"best S at 50 digits: {mp.nstr(S_mp(b), 20)}")
    print("|b_i| of best:", ", ".join(f"{abs(z):.6f}" for z in b))
    print("arg(b_i) in units of 2pi/(d-1):", ", ".join(f"{(np.angle(z) / (2 * np.pi / (d - 1))) % (d - 1):.6f}" for z in b))
    # the best configuration that is not the conjectured extremal one
    for v2, x2 in results:
        b2 = params_to_b(x2, d)
        if abs(v2 - target) > 1e-6:
            print(f"best non-extremal local value: {v2:.10f}; |b_i|:",
                  ", ".join(f"{abs(z):.4f}" for z in b2), "; args/(2pi/(d-1)):",
                  ", ".join(f"{(np.angle(z) / (2 * np.pi / (d - 1))) % (d - 1):.4f}" for z in b2))
            break


if __name__ == "__main__":
    main()
