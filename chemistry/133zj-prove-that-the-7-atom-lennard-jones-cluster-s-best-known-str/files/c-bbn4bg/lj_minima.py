# Local minima of small Lennard-Jones clusters, E = sum_{i<j} 4 (r^-12 - r^-6).
# Random starts -> L-BFGS -> keep only bound clusters (contact graph connected) that pass a
# stationarity test (gradient norm < 1e-6) and a minimum test (numerical Hessian: 6 zero modes, rest > 0).
# Needs numpy and scipy. A search: it can miss minima, and it proves nothing about the global minimum.
import sys
import numpy as np
from scipy.optimize import minimize

def energy_grad(x):
    p = x.reshape(-1, 3)
    d = p[:, None, :] - p[None, :, :]
    r2 = (d ** 2).sum(-1)
    np.fill_diagonal(r2, 1.0)
    i6 = r2 ** -3
    np.fill_diagonal(i6, 0.0)
    e = 2.0 * (i6 * i6 - i6).sum()
    g = (-24.0 * (2.0 * i6 * i6 - i6) / r2)[:, :, None] * d
    return e, g.sum(1).ravel()

def connected(p, cut=1.6):
    n = len(p)
    d = np.sqrt(((p[:, None] - p[None]) ** 2).sum(-1))
    seen, todo = {0}, [0]
    while todo:
        i = todo.pop()
        for j in range(n):
            if j not in seen and d[i, j] < cut:
                seen.add(j); todo.append(j)
    return len(seen) == n

def hessian(x, h=1e-5):
    m = len(x); H = np.zeros((m, m))
    for k in range(m):
        e = np.zeros(m); e[k] = h
        H[k] = (energy_grad(x + e)[1] - energy_grad(x - e)[1]) / (2 * h)
    return (H + H.T) / 2

def search(n, starts, rng):
    found = {}
    for _ in range(starts):
        x0 = rng.uniform(-1, 1, 3 * n) * (0.55 * n ** (1 / 3) + 0.4)
        res = minimize(energy_grad, x0, jac=True, method='L-BFGS-B', options={'maxiter': 20000, 'gtol': 1e-10, 'ftol': 1e-15})
        p = res.x.reshape(-1, 3)
        if np.linalg.norm(res.jac) > 1e-6 or not connected(p):
            continue
        key = round(res.fun, 5)
        if key not in found:
            w = np.linalg.eigvalsh(hessian(res.x))
            if not (np.abs(w[:6]).max() < 1e-3 and w[6] > 1e-3):
                continue
            d = np.sqrt(((p[:, None] - p[None]) ** 2).sum(-1))[np.triu_indices(n, 1)]
            found[key] = [0, res.fun, int((d < 1.3).sum()), d.min(), w[6]]
        found[key][0] += 1
    return found

starts = int(sys.argv[1])
rng = np.random.default_rng(20261006)
for n in (6, 7, 8):
    found = search(n, starts, rng)
    total = sum(v[0] for v in found.values())
    print(f'N = {n}: {len(found)} minima from {starts} starts ({total} starts ended in a bound minimum)')
    print('   energy        hits   pairs with r < 1.3   r_min     lowest nonzero Hessian eigenvalue')
    for key in sorted(found):
        c, e, nn, rmin, w = found[key]
        print(f'  {e:11.6f}  {c:6d}   {nn:10d}         {rmin:.5f}   {w:8.3f}')
