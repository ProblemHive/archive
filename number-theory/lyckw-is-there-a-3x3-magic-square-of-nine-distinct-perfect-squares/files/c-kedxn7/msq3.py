# 3x3 magic squares with many square entries, found from lists of three-square progressions.
# Every 3x3 magic square with centre e is fixed by two numbers p > q > 0: its eight outer entries are
# e+-p, e+-q, e+-(p+q), e+-(p-q)  (four opposite pairs).
# D(e) = {d > 0 : e-d and e+d are both squares}. With at least 7 square entries, at least two of the
# four pairs are entirely square (see the comment text), so two of p, q, p+q, p-q lie in D(e).
# For every e, every two members x < y of D(e) and every way to give them two of the four roles,
# the script counts the squares among the other four entries.
#
#   python msq3.py sq  N   square centres e = c^2, c <= N   (D from right triangles with hypotenuse c)
#   python msq3.py any M   all centres e <= M               (D from 2e = x^2 + z^2)
import sys, time
from math import gcd, isqrt
import numpy as np

mode, LIM = sys.argv[1], int(sys.argv[2])
t0 = time.time()

def is_sq(v):
    s = np.sqrt(np.maximum(v, 0).astype(np.float64)).astype(np.int64)
    return (v > 0) & ((s * s == v) | ((s + 1) * (s + 1) == v) | ((s - 1) * (s - 1) == v))

if mode == "sq":
    # primitive right triangles u^2 + v^2 = h^2, h <= N; then d = 2uv, and multiples k: c = kh, d = 2uv k^2
    H, D0 = [], []
    for m in range(2, isqrt(LIM) + 1):
        n = np.arange(1 + (m % 2), m, 2, dtype=np.int64)        # opposite parity
        n = n[np.gcd(n, m) == 1]
        h = m * m + n * n
        ok = h <= LIM
        n, h = n[ok], h[ok]
        H.append(h); D0.append(4 * m * n * (m * m - n * n))
    H = np.concatenate(H); D0 = np.concatenate(D0)
    reps = LIM // H
    idx = np.repeat(np.arange(len(H)), reps)
    k = np.arange(len(idx), dtype=np.int64) - np.repeat(np.cumsum(reps) - reps, reps) + 1
    C = H[idx] * k
    Dv = D0[idx] * k * k
    E = C * C
    del idx, k, C
    print(f"square centres c^2, c <= {LIM}: {len(H)} primitive right triangles, {len(E)} progressions of three squares")
else:
    # all x < z of equal parity with (x^2 + z^2)/2 <= M: e = (x^2+z^2)/2, d = (z^2-x^2)/2
    El, Dl = [], []
    for x in range(1, isqrt(LIM) + 1):
        zmax = isqrt(2 * LIM - x * x)
        z = np.arange(x + 2, zmax + 1, 2, dtype=np.int64)
        El.append((x * x + z * z) // 2); Dl.append((z * z - x * x) // 2)
    E = np.concatenate(El); Dv = np.concatenate(Dl)
    del El, Dl
    print(f"all centres e <= {LIM}: {len(E)} progressions of three squares")

order = np.lexsort((Dv, E))
E = E[order]; Dv = Dv[order]
del order
ue, starts, counts = np.unique(E, return_index=True, return_counts=True)
print(f"centres with at least one progression: {len(ue)}; with at least two: {int((counts >= 2).sum())}; most for one centre: {int(counts.max())}")

found = {}
pairs_tested = 0
for s in np.unique(counts):
    s = int(s)
    if s < 2:
        continue
    g = np.nonzero(counts == s)[0]
    ii, jj = np.triu_indices(s, 1)
    step = max(1, 2_000_000 // len(ii))
    for off in range(0, len(g), step):
        gg = g[off:off + step]
        Dm = Dv[starts[gg][:, None] + np.arange(s)[None, :]]        # rows sorted ascending
        e = ue[gg][:, None]
        x = Dm[:, ii]; y = Dm[:, jj]
        pairs_tested += x.size
        csq = is_sq(e)
        even = (x + y) % 2 == 0
        roles = [  # (p, q, valid) with x, y two of p, q, p+q, p-q
            (y, x, np.ones(x.shape, bool)),                 # p = y, q = x
            (x, y - x, y < 2 * x),                          # p = x, p+q = y
            (y, y - x, np.ones(x.shape, bool)),             # p = y, p-q = x
            (y - x, x, y > 2 * x),                          # q = x, p+q = y
            (x + y, x, np.ones(x.shape, bool)),             # q = x, p-q = y
            (x + y, y, np.ones(x.shape, bool)),             # q = y, p-q = x
            ((x + y) // 2, (y - x) // 2, even),             # p+q = y, p-q = x
        ]
        for p, q, valid in roles:
            valid = valid & (q > 0) & (p > q) & (p != 2 * q) & (e - p - q > 0)
            cnt = np.zeros(x.shape, np.int8)
            for f in (p, q, p + q, p - q):
                cnt += is_sq(e + f).astype(np.int8) + is_sq(e - f).astype(np.int8)
            tot = cnt + csq.astype(np.int8)
            for r, c in zip(*np.nonzero(valid & (tot >= 7))):
                ee, a, b = int(e[r, 0]), int(p[r, c]), int(q[r, c])
                ent = [ee + a, ee - a - b, ee + b, ee - a + b, ee, ee + a - b, ee - b, ee + a + b, ee - a]
                if len(set(ent)) == 9 and min(ent) > 0:
                    nsq = sum(1 for v in ent if isqrt(v) ** 2 == v)      # exact recount
                    if nsq >= 7:
                        found.setdefault(tuple(sorted(ent)), (nsq, ent))

print(f"pairs of progressions tested: {pairs_tested}; time {time.time() - t0:.0f}s")
prim = {k: v for k, v in found.items() if gcd(*k) == 1}
print(f"distinct magic squares with >= 7 square entries: {len(found)}; primitive: {len(prim)}; with 8 or 9: {sum(1 for v in found.values() if v[0] >= 8)}")
for k, (nsq, ent) in sorted(prim.items(), key=lambda kv: kv[1][1][4]):
    show = [f"{isqrt(v)}^2" if isqrt(v) ** 2 == v else str(v) for v in ent]
    print(f"centre={ent[4]} squares={nsq} magic sum={3 * ent[4]}: " + " | ".join(" ".join(show[3 * i:3 * i + 3]) for i in range(3)))
