# rsi_model.py - when does the software feedback loop speed up, in the Jones idea-production model
# with research input made from cognitive labour L and experiment compute K?
#   d ln A / dt = A^(-beta) * E^lam,   E = CES(L, K) with elasticity of substitution sigma and labour share alpha
#   L = A (the automated research workforce grows in proportion to software level A),  K = 1 (compute fixed)
# r = lam / beta is the "returns to research" of the papers. Units: time 1 = the time software needs to grow
# by a factor e at the starting rate (A = 1, E = 1). Pure Python, no packages.
import math

ALPHA = 0.5      # labour share in the CES aggregate (assumption)
LAM = 1.0        # no penalty for doing research in parallel (assumption); beta = LAM / r

def E(A, sigma):
    if sigma == 0:                      # Leontief: fixed proportions
        return min(A, 1.0)
    if sigma == 1:                      # Cobb-Douglas
        return A ** ALPHA
    rho = (sigma - 1) / sigma
    return (ALPHA * A ** rho + (1 - ALPHA)) ** (1 / rho)

def rate(A, r, sigma):                  # d ln A / dt
    return A ** (-LAM / r) * E(A, sigma) ** LAM

def time_to(target, r, sigma, n=200000):
    """time for A to go from 1 to target: integral of d ln A / rate, midpoint rule"""
    h = math.log(target) / n
    return sum(h / rate(math.exp((i + 0.5) * h), r, sigma) for i in range(n))

rs = [0.8, 1.2, 2.0, 3.6]
sigmas = [(0, 'sigma = 0 (fixed proportions)'), (0.5, 'sigma = 0.5'), (1, 'sigma = 1 (Cobb-Douglas)'),
          (2.58, 'sigma = 2.58'), (None, 'no compute input (E = L)')]
print('time for software to improve 1000-fold, in units of the starting e-folding time')
print('(a constant growth rate would take ln 1000 = %.2f); in brackets: growth rate at 1000x / starting rate' % math.log(1000))
print('%-32s' % '' + ''.join('r = %-14s' % r for r in rs))
for s, name in sigmas:
    row = '%-32s' % name
    for r in rs:
        if s is None:
            t = sum((math.log(1000) / 200000) / math.exp((i + 0.5) * math.log(1000) / 200000) ** (LAM - LAM / r) for i in range(200000))
            g = 1000 ** (LAM - LAM / r)
        else:
            t = time_to(1000, r, s); g = rate(1000, r, s)
        row += '%-18s' % ('%.3g [%.3g]' % (t, g))
    print(row)
print()
print('exponent of A in the growth rate for large A (positive: speeds up without limit; negative: slows down):')
for s, name in sigmas:
    row = '%-32s' % name
    for r in rs:
        if s is None or (s and s > 1): e = LAM - LAM / r
        elif s == 1: e = ALPHA * LAM - LAM / r
        else: e = -LAM / r
        row += '%-18s' % ('%+.3f' % e)
    print(row)
