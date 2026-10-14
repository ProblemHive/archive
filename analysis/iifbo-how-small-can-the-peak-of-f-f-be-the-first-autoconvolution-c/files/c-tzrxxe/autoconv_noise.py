# autoconv_noise.py - as autoconv_refine.py, but after each split the heights are multiplied by
# random factors in [1-s, 1+s] before re-optimising; best of 4 perturbations is kept at each level.
import sys, time
import numpy as np
from autoconv_refine import ratio, improve, exact_ratio

N0, levels, budget, s = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
rng = np.random.default_rng(1)
res = []
for k in range(6):
    a0 = rng.random(N0) + 0.1 if k else np.ones(N0)
    a, v, _ = improve(a0, 400, budget)
    res.append((v, a))
res.sort(key=lambda z: z[0]); v, a = res[0]
print(f'N={N0:5d}  best of 6 starts   {v:.6f}')
rng = np.random.default_rng(2)
for lev in range(levels):
    base = np.repeat(a, 2); t0 = time.time(); cands = []
    for k in range(4):
        p = base * (1 + s * (2 * rng.random(len(base)) - 1))
        b, v, it = improve(p, 2000, budget)
        cands.append((v, it, b))
    cands.sort(key=lambda z: z[0])
    v, it, a = cands[0]
    print(f'N={len(a):5d}  split, noise {s}: 4 tries ' + ' '.join(f'{c[0]:.6f}' for c in cands) + f'   best used {it} LP steps; {time.time()-t0:.0f}s')
a = a * 2 * len(a)
print(f'final N={len(a)}: float ratio {ratio(a):.9f}; exact ratio of heights rounded to 6 decimals = {float(exact_ratio(a)):.9f}')
