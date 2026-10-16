# CNF for the reduced ES question: N = n - 1 points in x-order, no K points in convex position
# and no (K-1)-point cap, in the signotope model.
# Why: take a vertex p0 of the convex hull of n points and a line through p0 missing the other points.
# A projective map sending that line to infinity sends p0 to the point at infinity in the downward
# vertical direction and keeps every other subset's convex position. A convex K-gon through p0 then
# becomes a (K-1)-point cap among the other points. So: n points without a convex K-gon exist
# => N = n - 1 points (signotope) with no convex K-gon and no (K-1)-cap exist. UNSAT here proves ES(K) <= n.
# Same encoding as es_cnf.py (c/tp4xvn) with two changes: caps of K-1 points are forbidden, and the
# x-axis reflection is no longer a symmetry (it swaps cups and caps), so the first triple is not fixed.
# Usage: python es_hull.py N K out.cnf
import sys, itertools
n, K, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
nv = 0
def new():
    global nv
    nv += 1
    return nv
T = {}
for t in itertools.combinations(range(n), 3):
    T[t] = new()
cls = []
for i, j, k, l in itertools.combinations(range(n), 4):
    s = [T[(i, j, k)], T[(i, j, l)], T[(i, k, l)], T[(j, k, l)]]
    for x, y, z in itertools.combinations(range(4), 3):
        cls.append([-s[x], s[y], -s[z]])
        cls.append([s[x], -s[y], s[z]])
U, V, EU, EV = {}, {}, {}, {}
def get(d, key):
    if key not in d:
        d[key] = new()
    return d[key]
for p in range(n):
    for j in range(p + 1, n):
        for k in range(j + 1, n):
            cls.append([-T[(p, j, k)], get(U, (p, 3, j, k))])
            cls.append([T[(p, j, k)], get(V, (p, 3, j, k))])
    for a in range(3, K):
        for i in range(p + 1, n):
            for j in range(i + 1, n):
                if (p, a, i, j) in U:
                    for k in range(j + 1, n):
                        cls.append([-U[(p, a, i, j)], -T[(i, j, k)], get(U, (p, a + 1, j, k))])
                if (p, a, i, j) in V:
                    for k in range(j + 1, n):
                        cls.append([-V[(p, a, i, j)], T[(i, j, k)], get(V, (p, a + 1, j, k))])
    for (pp, a, j, q), v in list(U.items()):
        if pp == p:
            cls.append([-v, get(EU, (p, a, q))])
    for (pp, a, j, q), v in list(V.items()):
        if pp == p:
            cls.append([-v, get(EV, (p, a, q))])
for p in range(n):
    for q in range(p + 1, n):
        for a in range(2, K + 1):
            for b in range(2, K + 1):
                if a + b - 2 < K:
                    continue
                c = []
                if a > 2:
                    if (p, a, q) not in EU: continue
                    c.append(-EU[(p, a, q)])
                if b > 2:
                    if (p, b, q) not in EV: continue
                    c.append(-EV[(p, b, q)])
                if c:
                    cls.append(c)
# no cap of K-1 points
ncap = 0
for (p, a, j, k), v in V.items():
    if a == K - 1:
        cls.append([-v])
        ncap += 1
with open(out, "w") as f:
    f.write("p cnf %d %d\n" % (nv, len(cls)))
    for c in cls:
        f.write(" ".join(map(str, c)) + " 0\n")
print("N=%d K=%d vars=%d clauses=%d (cap clauses %d)" % (n, K, nv, len(cls), ncap))
