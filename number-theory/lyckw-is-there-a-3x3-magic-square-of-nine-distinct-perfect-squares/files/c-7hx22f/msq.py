# 3x3 magic squares with a square centre c^2 and many square entries.
# Every 3x3 magic square with centre e has the form
#     e+a    e-a-b   e+b
#     e-a+b  e       e+a-b
#     e-b    e+a+b   e-a
# For each c <= N, e = c^2: try every pair of squares (p, q) below 2e for the two
# top corners (a = p - e, b = q - e) and count how many of the other six entries are squares.
# Reports squares with 9 distinct positive entries and at least 7 squares among them.
import sys, time
from math import gcd, isqrt
import numpy as np

N = int(sys.argv[1])
t0 = time.time()
found = {}
best_count = {}
for c in range(2, N + 1):
    e = c * c
    r = np.arange(1, isqrt(2 * e - 1) + 1, dtype=np.int64)
    S = r * r
    P, Q = S[:, None], S[None, :]
    a, b = P - e, Q - e
    others = [e - a - b, e - a + b, e + a - b, e - b, e + a + b, e - a]
    cnt = np.zeros(P.shape[0:1] + Q.shape[1:2], dtype=np.int8) + 3   # centre and two corners are squares
    ok = np.ones(cnt.shape, dtype=bool)
    for x in others:
        ok &= x > 0
        s = np.sqrt(np.maximum(x, 0).astype(np.float64)).astype(np.int64)
        cnt += ((s * s == x) | ((s + 1) * (s + 1) == x)).astype(np.int8)
    ok &= (a != 0) & (b != 0) & (a != b) & (a != -b) & (a != 2 * b) & (b != 2 * a)
    cnt[~ok] = 0
    for i, j in zip(*np.nonzero(cnt >= 7)):
        aa, bb = int(S[i]) - e, int(S[j]) - e
        ent = [e + aa, e - aa - bb, e + bb, e - aa + bb, e, e + aa - bb, e - bb, e + aa + bb, e - aa]
        if len(set(ent)) < 9:
            continue
        key = tuple(sorted(ent))
        if key not in found:
            found[key] = (int(cnt[i, j]), c, ent)
print(f"centres c^2 for c = 2..{N}; time {time.time() - t0:.0f}s")
prim = [(k, v) for k, v in found.items() if gcd(*k) == 1]
print(f"distinct magic squares with >= 7 square entries: {len(found)}; primitive (gcd of entries 1): {len(prim)}")
print("with 8 or 9 square entries:", sum(1 for v in found.values() if v[0] >= 8))
for k, (n, c, ent) in sorted(prim, key=lambda kv: kv[1][1]):
    show = [f"{isqrt(x)}^2" if isqrt(x) ** 2 == x else str(x) for x in ent]
    print(f"c={c} squares={n} magic sum={3 * c * c}: " + " | ".join(" ".join(show[3 * i:3 * i + 3]) for i in range(3)))
