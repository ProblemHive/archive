"""Block-circulant (3,t)-graphs by SAT with lazily added independence clauses.

A graph on N = m*n vertices (i, a), i in 0..m-1 (orbit), a in Z_n, invariant under the
semiregular cyclic automorphism (i, a) -> (i, a+1). Whether (i,a) ~ (j,b) depends only on
(i, j, b - a mod n); within one orbit on +-(b - a). One SAT variable per such edge class.

Constraints: no triangle (all triangle classes, written down at the start), and no independent
t-set (added lazily: each time the solver returns a graph with an independent t-set I, add the
clause "some pair in I is an edge"; since variables depend only on differences, that one clause
also covers every translate of I). Ends with SAT (a graph is found and checked) or UNSAT
(no (3,t)-graph with this symmetry exists).

Usage: python3 -u blockcirc.py m n t [max_iterations] [K = independent sets added per call]
"""
import sys, time, itertools
from pysat.solvers import Cadical153

m, n, t = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
maxit = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
K = int(sys.argv[5]) if len(sys.argv) > 5 else 1   # independent t-sets added per solver call
import random
rng = random.Random(12345)
N = m * n

var = {}
def v(i, j, d):
    d %= n
    if i > j:
        i, j, d = j, i, (-d) % n
    if i == j:
        d = min(d, n - d)
        if d == 0:
            return None
    key = (i, j, d)
    if key not in var:
        var[key] = len(var) + 1
    return var[key]

def ev(x, y):  # edge variable between vertex indices x, y
    i, a = divmod(x, n); j, b = divmod(y, n)
    return v(i, j, b - a)

for i in range(m):
    for j in range(i, m):
        for d in range(n):
            v(i, j, d)
nv = len(var)

s = Cadical153()
clauses = set()
# triangles: translate so that the first vertex has position 0
for i in range(m):
    u = i * n
    for y in range(N):
        if y == u: continue
        for z in range(y + 1, N):
            if z == u: continue
            lits = {ev(u, y), ev(u, z), ev(y, z)}
            if None in lits: continue
            c = tuple(sorted(-l for l in lits))
            if c not in clauses:
                clauses.add(c); s.add_clause(list(c))
ntri = len(clauses)

def find_indep(adj, need):
    """an independent set of size need, as a list, or None (plain branch and bound on bitsets)"""
    full = (1 << N) - 1
    def rec(cand, need, chosen):
        if need == 0:
            return chosen
        while cand:
            if bin(cand).count("1") < need:
                return None
            x = (cand & -cand).bit_length() - 1
            cand &= cand - 1
            r = rec(cand & ~adj[x], need - 1, chosen + [x])
            if r is not None:
                return r
        return None
    return rec(full, need, [])

t0 = time.time()
it = 0
while True:
    it += 1
    if not s.solve():
        print(f"m={m} n={n} N={N} t={t}: UNSAT after {it} solver calls, {len(clauses) - ntri} independence clauses "
              f"({nv} edge classes, {ntri} triangle clauses), {time.time() - t0:.1f} s")
        break
    model = set(l for l in s.get_model() if l > 0)
    adj = [0] * N
    for x in range(N):
        for y in range(N):
            if x != y and ev(x, y) in model:
                adj[x] |= 1 << y
    I = find_indep(adj, t)
    if I is not None and K > 1:
        # more independent t-sets from the same graph, found with shuffled vertex orders (fixed seed)
        for _ in range(K - 1):
            perm = list(range(N)); rng.shuffle(perm)
            inv = [0] * N
            for a, x in enumerate(perm): inv[x] = a
            padj = [0] * N
            for x in range(N):
                b = 0
                for y in range(N):
                    if adj[x] >> y & 1: b |= 1 << inv[y]
                padj[inv[x]] = b
            J = find_indep(padj, t)
            if J is not None:
                J = [perm[a] for a in J]
                c = tuple(sorted(set(ev(J[a], J[b]) for a in range(t) for b in range(a + 1, t))))
                if c not in clauses:
                    clauses.add(c); s.add_clause(list(c))
    if I is None:
        # double-check triangle-freeness directly
        tri = any(adj[x] >> y & 1 and adj[x] & adj[y] for x in range(N) for y in range(N))
        degs = sorted(set(bin(a).count("1") for a in adj))
        print(f"m={m} n={n} N={N} t={t}: FOUND after {it} solver calls, {time.time() - t0:.1f} s; triangle={tri}; degrees {degs}")
        for (i, j, d), k in sorted(var.items()):
            if k in model:
                print(f"  edge class orbit {i} -> orbit {j}, difference {d}")
        break
    c = tuple(sorted(ev(I[a], I[b]) for a in range(t) for b in range(a + 1, t) if ev(I[a], I[b]) is not None))
    c = tuple(sorted(set(c)))
    clauses.add(c); s.add_clause(list(c))
    if it % 2000 == 0:
        print(f"  ... {it} calls, {time.time() - t0:.0f} s", flush=True)
    if it >= maxit:
        print(f"m={m} n={n} N={N} t={t}: UNDECIDED, stopped at {it} solver calls, {time.time() - t0:.1f} s")
        break
