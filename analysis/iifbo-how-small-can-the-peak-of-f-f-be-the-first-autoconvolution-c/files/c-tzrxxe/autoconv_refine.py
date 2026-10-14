# autoconv_refine.py - step-function upper bounds for the first autoconvolution constant,
# by refinement: optimise at N pieces, split every piece in two (same function, 2N pieces), optimise again.
#   ratio(a) = 2N * max_k (a*a)_k / (sum a)^2   (exact for the step function with heights a)
# Optimiser: the same LP iteration as autoconv.py in c/x8dgiz. Needs numpy and scipy.
import sys, time
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog

STEPS = (0.5, 0.25, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 0.0005, 0.0002, 0.0001, 0.00005, 0.00002)

def ratio(a):
    return 2 * len(a) * np.convolve(a, a).max() / a.sum() ** 2

def exact_ratio(a, digits=6):
    # round heights to rationals with the given number of decimals, then evaluate exactly
    q = [Fraction(round(float(x) * 10 ** digits), 10 ** digits) for x in a]
    N = len(q)
    conv = [Fraction(0)] * (2 * N - 1)
    for i, x in enumerate(q):
        if x:
            for j, y in enumerate(q):
                conv[i + j] += x * y
    return 2 * N * max(conv) / sum(q) ** 2

def improve(a, iters, budget):
    N = len(a); a = a / a.sum(); best = ratio(a); t0 = time.time(); it = 0
    for it in range(iters):
        if time.time() - t0 > budget:
            break
        A = np.zeros((2 * N - 1, N + 1))
        for j in range(N):
            A[j:j + N, j] = a
        A[:, N] = -1
        c = np.zeros(N + 1); c[N] = 1
        Aeq = np.ones((1, N + 1)); Aeq[0, N] = 0
        r = linprog(c, A_ub=A, b_ub=np.zeros(2 * N - 1), A_eq=Aeq, b_eq=[1],
                    bounds=[(0, None)] * N + [(None, None)], method='highs')
        if r.status != 0:
            break
        b = r.x[:N]
        val, e = min((ratio((1 - e) * a + e * b), e) for e in STEPS)
        if val >= best - 1e-11:
            break
        a = (1 - e) * a + e * b; a /= a.sum(); best = val
    return a, best, it

if __name__ == '__main__':
    N0, levels, budget = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    rng = np.random.default_rng(1)
    # best of 6 starts at N0, as in autoconv.py
    res = []
    for s in range(6):
        a0 = rng.random(N0) + 0.1 if s else np.ones(N0)
        a, v, _ = improve(a0, 400, budget)
        res.append((v, a))
    res.sort(key=lambda z: z[0])
    v, a = res[0]
    print(f'N={N0:5d}  best of 6 starts          {v:.6f}')
    for lev in range(levels):
        a = np.repeat(a, 2)                      # same step function on 2N pieces
        before = ratio(a)
        t0 = time.time()
        a, v, it = improve(a, 2000, budget)
        print(f'N={len(a):5d}  after split {before:.6f}  re-optimised {v:.6f}   {it} LP steps, {time.time()-t0:.0f}s')
    a = a * 2 * len(a)                           # heights of the function with integral 1
    ex = exact_ratio(a)
    print(f'final N={len(a)}: float ratio {ratio(a):.9f}; exact ratio of heights rounded to 6 decimals = {float(ex):.9f}')
    print('  as a fraction: numerator has', len(str(ex.numerator)), 'digits; value > 1.5 ?', ex > Fraction(3, 2))
    np.savetxt('heights_final.txt', a, fmt='%.6f')
    print('heights (6 decimals, integral 1), left to right:')
    print(' '.join(f'{x:.6f}' for x in a))
