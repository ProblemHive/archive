# Exact maximum loneliness ML(v) = max_t min_i ||t v_i|| for every primitive quadruple of distinct
# positive integers up to N, and the form of every value below 1/4.
# usage: python evawq/spectrum4.py N
# A local maximum of t -> min_i ||t v_i|| is a time where two runners are at equal distance from
# the start, so t (v_i - v_j) or t (v_i + v_j) is an integer. All such t = m/d are scanned, in integers.
import sys
import time
from fractions import Fraction
from itertools import combinations
from math import gcd
from multiprocessing import Pool

import numpy as np

N = int(sys.argv[1])
QUARTER = Fraction(1, 4)
MS = np.arange(0, 2 * N + 1, dtype=np.int64)


def ml(v):
    best = Fraction(0)
    arr = np.array(v, dtype=np.int64)
    for d in {x for a, b in combinations(v, 2) for x in (b - a, a + b)}:
        m = MS[: d // 2 + 1]                      # t and -t give the same distances
        r = (m[:, None] * arr[None, :]) % d
        num = int(np.minimum(r, d - r).min(axis=1).max())
        f = Fraction(num, d)
        if f > best:
            best = f
    return best


def work(a):
    out = []
    count = 0
    for b in range(a + 1, N - 1):
        g2 = gcd(a, b)
        for c in range(b + 1, N):
            g3 = gcd(g2, c)
            for d in range(c + 1, N + 1):
                if gcd(g3, d) != 1:
                    continue
                count += 1
                f = ml((a, b, c, d))
                if f < QUARTER:
                    out.append(((a, b, c, d), f))
    return count, out


if __name__ == "__main__":
    t0 = time.time()
    # self-test on values stated in the literature
    assert ml((1, 2, 3, 4)) == Fraction(1, 5) and ml((1, 3, 4, 7)) == Fraction(1, 5)
    assert ml((3, 8, 11, 19)) == Fraction(7, 30)          # Fan and Sun, arXiv:2306.10417
    assert ml((1, 2, 3, 8)) == Fraction(2, 9)             # 1, 2, 3, 4s with s = 2 (Kravitz)
    assert ml((1, 2, 3)) == Fraction(1, 4) and ml((1, 2)) == Fraction(1, 3)
    with Pool(8) as p:
        res = p.map(work, range(1, N - 2), chunksize=1)
    total = sum(r[0] for r in res)
    near = [x for r in res for x in r[1]]
    print(f"N = {N}: primitive quadruples a<b<c<d<=N: {total}; with ML < 1/4: {len(near)}")
    print("smallest ML:", min(f for _, f in near), " attained by:", [v for v, f in near if f == min(g for _, g in near)])
    byk, bym, bad = {}, {}, []
    for v, f in near:
        k = f.denominator - 4 * f.numerator
        byk[k] = byk.get(k, 0) + 1
        x = 1 / (QUARTER - f)                      # predicted: 4m with m odd, i.e. ML = (m-1)/(4m)
        if x.denominator == 1 and x.numerator % 8 == 4:
            m = x.numerator // 4
            bym.setdefault(m, []).append(v)
        else:
            bad.append((v, f))
    print("count by k = q - 4p (ML = p/q in lowest terms):", dict(sorted(byk.items())))
    print("values not of the form (m-1)/(4m) with m odd:", len(bad), bad[:20])
    ms = sorted(bym)
    print("odd m that occur:", ms[:40], "..." if len(ms) > 40 else "", " largest:", ms[-1])
    print("odd m from 5 to 41 that do not occur:", [m for m in range(5, 42, 2) if m not in bym])
    for m in ms[:12]:
        f = Fraction(m - 1, 4 * m)
        print(f"  m = {m:3d}  ML = {f}  k = {f.denominator - 4 * f.numerator}  tuples: {len(bym[m])}  first: {bym[m][:3]}")
    with open(f"evawq/near{N}.txt", "w") as fh:          # every quadruple below 1/4, for later scripts
        for v, f in sorted(near):
            fh.write(" ".join(map(str, v)) + f" {f.numerator} {f.denominator}\n")
    print(f"wall time {time.time() - t0:.0f} s")
