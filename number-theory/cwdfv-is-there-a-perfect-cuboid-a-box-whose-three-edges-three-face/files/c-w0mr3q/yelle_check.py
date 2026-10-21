"""Tests of the 'triangular remainder' set-up of Yelle, arXiv:2602.00239v2, on real Euler bricks.
A face (a, b, c) with a^2 + b^2 = c^2 is written (r+x, r+y, r+x+y) with r^2 = 2xy.
"""
import sys
from math import isqrt, gcd
from itertools import permutations

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200000

# all Pythagorean triples with both legs <= N
legs = {}
for m in range(2, isqrt(N * 13 // 10) + 3):   # both legs <= N forces m^2 <= N (1 + sqrt 2)/2
    for n in range(1, m):
        if (m - n) % 2 == 0 or gcd(m, n) != 1:
            continue
        p, q = m * m - n * n, 2 * m * n
        k = 1
        while k * p <= N and k * q <= N:
            legs.setdefault(k * p, set()).add(k * q)
            legs.setdefault(k * q, set()).add(k * p)
            k += 1

bricks = set()
for a, s in legs.items():
    for b in s:
        if b > a:
            for c in s:
                if c > b and c in legs.get(b, ()):
                    bricks.add((a, b, c))
bricks = sorted(bricks)
print('edge bound', N, 'Euler bricks', len(bricks))

def remainder(u, v):
    w = isqrt(u * u + v * v)
    assert w * w == u * u + v * v
    r = u + v - w
    x, y = w - v, w - u        # u = r + x, v = r + y, w = r + x + y
    assert (u, v, w) == (r + x, r + y, r + x + y) and r * r == 2 * x * y and min(r, x, y) > 0
    return r, x, y

n_ok_param = 0
n_cyclic = 0      # bricks for which SOME labelling satisfies the three 'rigid cyclic gluing' relations of Section 6
n_closure = 0     # bricks that also satisfy the 'symmetric closure' r1 + x1 = r2 + x2 (Lemma 1)
example = None
for (a, b, c) in bricks:
    faces = [(a, b), (a, c), (b, c)]
    found_cyc = False
    for order in permutations(range(3)):
        for swap in range(8):
            rxy = []
            for i, f in enumerate(order):
                u, v = faces[f]
                if (swap >> i) & 1:
                    u, v = v, u
                rxy.append(remainder(u, v))
            (r1, x1, y1), (r2, x2, y2), (r3, x3, y3) = rxy
            if r1 + x1 == r3 + y3 and r2 + x2 == r3 + x3 and r1 + y1 == r2 + y2:
                found_cyc = True
                if r1 + x1 == r2 + x2:
                    n_closure += 1
                if example is None:
                    example = ((a, b, c), rxy)
    n_ok_param += 1
    n_cyclic += found_cyc
print('all faces satisfy r^2 = 2xy and (r+x, r+y, r+x+y):', n_ok_param == len(bricks))
print('bricks with a labelling satisfying the three cyclic gluing relations:', n_cyclic)
print('(brick, labelling) pairs that also satisfy the symmetric closure r1+x1 = r2+x2:', n_closure)
print('example:', example)
