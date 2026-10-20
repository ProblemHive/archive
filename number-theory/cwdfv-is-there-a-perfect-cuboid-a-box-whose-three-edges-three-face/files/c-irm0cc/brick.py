import sys
from math import isqrt, gcd
from collections import defaultdict
N = int(sys.argv[1])
# all Pythagorean triples (x, y, z) with both legs <= N: legs[x] = set of partner legs y (x != y)
partners = defaultdict(set)
for m in range(2, isqrt(N) + 3):
    for n in range(1, m):
        if (m - n) % 2 == 0 or gcd(m, n) != 1:
            continue
        p, q = m * m - n * n, 2 * m * n
        if max(p, q) > N:
            continue
        k = 1
        while k * max(p, q) <= N:
            partners[k * p].add(k * q)
            partners[k * q].add(k * p)
            k += 1
bricks = set()
for a, ps in partners.items():
    L = sorted(ps)
    Ls = set(L)
    for i, b in enumerate(L):
        for c in L[i + 1:]:
            if a < b < c and c in partners[b]:
                bricks.add((a, b, c))
bricks = sorted(bricks, key=lambda t: (t[2], t[1], t[0]))
prim = [t for t in bricks if gcd(gcd(t[0], t[1]), t[2]) == 1]
def issq(n):
    r = isqrt(n)
    return r * r == n
perfect = [t for t in bricks if issq(t[0] ** 2 + t[1] ** 2 + t[2] ** 2)]
print("N =", N, "bricks (all):", len(bricks), "primitive:", len(prim), "perfect:", len(perfect))
print("first 12 primitive by largest edge:")
for t in prim[:12]:
    a, b, c = t
    print(t, "face diagonals", isqrt(a*a+b*b), isqrt(a*a+c*c), isqrt(b*b+c*c), "space diag^2 =", a*a+b*b+c*c)

