# Lennard-Jones clusters, E = sum_{i<j} 4 (r^-12 - r^-6): random-restart local minimisation.
# For each N: best energy found, how many distinct local minima were seen, how often the best was hit,
# the gap to the second-lowest minimum, and the smallest pair distance in the best structure.
# Needs numpy and scipy. This is a search, not a proof: it gives upper bounds on the minimum energy.
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
    e = 2.0 * (i6 * i6 - i6).sum()                    # 4 * sum over i<j
    g = (-24.0 * (2.0 * i6 * i6 - i6) / r2)[:, :, None] * d
    return e, g.sum(1).ravel()

def run(n, starts, rng):
    found = {}
    for _ in range(starts):
        x0 = rng.uniform(-1, 1, 3 * n) * (0.55 * n ** (1 / 3) + 0.4)
        res = minimize(energy_grad, x0, jac=True, method='L-BFGS-B', options={'maxiter': 5000, 'gtol': 1e-9})
        if not res.success or res.fun > -1e-6:
            continue
        key = round(res.fun, 5)
        if key not in found:
            found[key] = [0, res.x.copy(), res.fun]
        found[key][0] += 1
    keys = sorted(found)
    best = found[keys[0]]
    p = best[1].reshape(-1, 3)
    d = np.sqrt(((p[:, None] - p[None]) ** 2).sum(-1))
    rmin = d[np.triu_indices(n, 1)].min()
    gap = keys[1] - keys[0] if len(keys) > 1 else float('nan')
    return best[2], len(keys), best[0], gap, rmin

CCD = {2: -1.0, 3: -3.0, 4: -6.0, 5: -9.103852, 6: -12.712062, 7: -16.505384, 8: -19.821489,
       9: -24.113360, 10: -28.422532, 11: -32.765970, 12: -37.967600, 13: -44.326801}

starts = int(sys.argv[1])
rng = np.random.default_rng(20261006)
print(f'{starts} random starts per N, seed 20261006; pair minimum is at r = 2^(1/6) = {2 ** (1 / 6):.6f}')
print(' N   best found     database     diff     minima seen  hits of best  gap to 2nd   r_min')
for n in range(2, 14):
    e, k, hits, gap, rmin = run(n, starts, rng)
    print(f'{n:2d}  {e:12.6f}  {CCD[n]:11.6f}  {e - CCD[n]:+.1e}  {k:11d}  {hits:12d}  {gap:10.5f}  {rmin:.6f}')
