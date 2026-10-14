# Closed formula for the maximum loneliness on the subtorus U2 of Jain and Kravitz,
# speeds (A, B, A+B, A+2B) with gcd(A, B) = 1, tested against the exact value.
# usage: python evawq/u2formula.py AMAX BMAX
#
# Runner positions at time t are x, y, x+y, x+2y with (x, y) = t(A, B) mod 1, so (x, y) runs over
# the closed curve Bx - Ay = integer.  f(x, y) = min(||x||, ||y||, ||x+y||, ||x+2y||) equals 1/4
# only at +-P1 = +-(1/4, 1/4) and +-P2 = +-(1/4, 1/2) (checked on a grid below).  Near P1,
# f = 1/4 - max(-u, -v, u+2v); near P2, f = 1/4 - max(-u, u+v, -u-2v).  Minimising these over the
# nearest lines of the curve gives 1/4 - ML = 1/(4m) with m the largest of the candidates below.
import sys
from fractions import Fraction
from itertools import combinations
from math import gcd

import numpy as np

Q = Fraction(1, 4)


def ml(v):
    """Exact max_t min_i ||t v_i||: scan t = j/d for d = v_i - v_j and v_i + v_j."""
    best = Fraction(0)
    arr = np.array(v, dtype=np.int64)
    for d in {x for a, b in combinations(v, 2) for x in (abs(b - a), a + b)}:
        j = np.arange(0, d // 2 + 1, dtype=np.int64)
        r = (j[:, None] * arr[None, :]) % d
        best = max(best, Fraction(int(np.minimum(r, d - r).min(axis=1).max()), d))
    return best


def candidates(A, B):
    """(value, label) pairs; None as value means the curve passes through the point (ML = 1/4)."""
    out = []
    for name, rho, hp, hm in (
        ("P1", (A - B) % 4, max(A - B, -A - B, A + 3 * B), max(B - A, A + B, -A - 3 * B)),
        ("P2", (2 * A - B) % 4, max(-B - 2 * A, -B, 3 * B + 2 * A), max(B + 2 * A, B, -3 * B - 2 * A)),
    ):
        if rho == 0:
            out.append((None, name))
        elif rho == 1:
            out += [(Fraction(hp), name + " c=+1/4"), (Fraction(hm, 3), name + " c=-3/4")]
        elif rho == 3:
            out += [(Fraction(hm), name + " c=-1/4"), (Fraction(hp, 3), name + " c=+3/4")]
        else:
            out += [(Fraction(hp, 2), name + " c=+1/2"), (Fraction(hm, 2), name + " c=-1/2")]
    return out


def m_formula(A, B):
    c = candidates(A, B)
    if any(v is None for v, _ in c):
        return None, "tight"
    return max(c)


def main():
    AMAX, BMAX = int(sys.argv[1]), int(sys.argv[2])
    # 1. where does f reach 1/4 on the torus?  exact check on the grid of denominator 840
    D = 840
    g = np.arange(D, dtype=np.int64)
    X, Y = np.meshgrid(g, g, indexing="ij")
    f = np.minimum.reduce([np.minimum(z % D, D - z % D) for z in (X, Y, X + Y, X + 2 * Y)])
    top = np.argwhere(f * 4 >= D)
    print(f"grid 1/{D}: max of 4f = {Fraction(int(f.max()) * 4, D)}; points with f >= 1/4:",
          [(str(Fraction(int(a), D)), str(Fraction(int(b), D))) for a, b in top])

    # 2. formula against the exact value
    pairs = tight = near = agree = 0
    bad = []
    labels = {}
    worst = (Fraction(0), None)
    seen_m = {}
    for A in range(1, AMAX + 1):
        for B in range(-BMAX, BMAX + 1):
            if B == 0 or gcd(A, abs(B)) != 1:
                continue
            v = sorted({abs(A + B), abs(B), A, abs(A + 2 * B)})
            if len(v) < 4 or v[0] == 0:
                continue
            pairs += 1
            exact = ml(v)
            mf, lab = m_formula(A, B)
            if mf is None:
                tight += 1
                ok = exact == Q
            else:
                near += 1
                ok = exact == Q - Q / mf
                labels[lab] = labels.get(lab, 0) + 1
                if ok:
                    seen_m.setdefault(mf, tuple(v))
                    worst = max(worst, (Fraction(v[3]) / mf, tuple(v)))
            if ok:
                agree += 1
            else:
                bad.append((A, B, tuple(v), str(exact), str(mf)))
    print(f"A <= {AMAX}, |B| <= {BMAX}: pairs {pairs}; formula says ML = 1/4 for {tight}, below for {near}")
    print(f"formula equals exact value: {agree} of {pairs}; disagreements: {len(bad)}")
    for row in bad[:30]:
        print("   A, B, speeds, exact ML, m from formula:", row)
    print("which candidate gives the maximum:", dict(sorted(labels.items())))
    ms = sorted(seen_m)
    print("non-integer or even m:", [str(m) for m in ms if m.denominator != 1 or m.numerator % 2 == 0][:10])
    ints = [int(m) for m in ms]
    print("odd m from 5 to 201 not attained on U2 in this range:", [m for m in range(5, 202, 2) if m not in ints])
    print("largest (largest speed)/m:", worst[0], "=", float(worst[0]), "at", worst[1])
    for m in (5, 9, 11, 13, 15, 19, 23, 27, 31):
        print(f"   m = {m}: e.g. speeds {seen_m.get(Fraction(m))}")


if __name__ == "__main__":
    main()
