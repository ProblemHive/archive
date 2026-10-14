# Consequences of the formula for ML on U2 = (A, B, A+B, A+2B), using the formula only (no search over t),
# plus two sanity checks of steps of the proof.
# usage: python evawq/u2consequences.py K        (box: 1 <= A <= K, |B| <= K)
import sys
from fractions import Fraction
from math import gcd

import numpy as np

from u2formula import m_formula, ml

K = int(sys.argv[1])

# 1. step of the proof: on the four triangles that tile the torus, f = 1/4 - g_P exactly (grid 1/240)
D = 240
bad = 0
for i in range(D + 1):
    for j in range(D + 1):
        x, y = Fraction(i, D), Fraction(j, D)
        nrm = lambda z: abs(z - round(z))
        f = min(nrm(x), nrm(y), nrm(x + y), nrm(x + 2 * y))
        if x + y <= 1:
            loc = min(x, y, 1 - x - 2 * y) if x + 2 * y <= 1 else min(x, 1 - x - y, x + 2 * y - 1)
        else:                                   # the mirror images under (x, y) -> (1 - x, 1 - y)
            X, Y = 1 - x, 1 - y
            loc = min(X, Y, 1 - X - 2 * Y) if X + 2 * Y <= 1 else min(X, 1 - X - Y, X + 2 * Y - 1)
        bad += f != loc
print(f"grid 1/{D}: points where f differs from the local formula on its triangle: {bad} of {(D + 1) ** 2}")

# 2. U1: ML(1, 2, 3, 4s) = s/(4s+1), exact, s = 1..200
print("ML(1,2,3,4s) = s/(4s+1) for s = 1..200:", all(ml((1, 2, 3, 4 * s)) == Fraction(s, 4 * s + 1) for s in range(1, 201)))

# 3. the formula over a large box
seen = {}
small = []
notodd = 0
near = 0
worst = (Fraction(0), None)
for A in range(1, K + 1):
    for B in range(-K, K + 1):
        if B == 0 or gcd(A, abs(B)) != 1:
            continue
        v = sorted({abs(A + B), abs(B), A, abs(A + 2 * B)})
        if len(v) < 4 or v[0] == 0:
            continue                            # two equal speeds or a zero speed: not a quadruple
        m, _ = m_formula(A, B)
        if m is None:
            continue
        near += 1
        if m.denominator != 1 or m.numerator % 2 == 0:
            notodd += 1
            continue
        m = int(m)
        seen.setdefault(m, (A, B, tuple(v)))
        if m <= 9:
            small.append((m, A, B, tuple(v)))
        worst = max(worst, (Fraction(v[3], m), tuple(v), m))
print(f"box A <= {K}, |B| <= {K}: pairs with ML < 1/4: {near}; m not an odd integer: {notodd}")
print("all pairs with m <= 9 (m, A, B, speeds):")
for row in sorted(small):
    print("  ", row)
lim = K // 3
print(f"odd m from 3 to {lim} not attained (complete for m <= {lim}, since m >= max(|A-B|, |A+B|, |A+3B|)/3):",
      [m for m in range(3, lim + 1, 2) if m not in seen])
print("largest (largest speed)/m in the box:", worst[0], "=", round(float(worst[0]), 5), "speeds", worst[1], "m =", worst[2])

# 4. the two families that realise every m
print("m = b + 8 on (4, b, b+4, 2b+4), b = 1 mod 4, b = 1..2001:", all(m_formula(4, b)[0] == b + 8 for b in range(1, 2002, 4)))
print("m = a + 12 on (a, 8, a+8, a+16), a = 3 mod 4, a = -1..2003:", all(m_formula(a, 8)[0] == a + 12 for a in range(-1, 2004, 4)))
print("spot checks against the exact value:",
      [(b, str(ml((4, b, b + 4, 2 * b + 4)))) for b in (1, 5, 49)], [(a, str(ml(tuple(sorted((abs(a), 8, a + 8, a + 16)))))) for a in (-1, 3, 51)])
