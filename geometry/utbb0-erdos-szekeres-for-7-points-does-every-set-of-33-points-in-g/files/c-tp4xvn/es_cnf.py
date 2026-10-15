# CNF: n points in x-order with no K points in convex position, in the signotope model.
# Usage: python es_cnf.py n K out.cnf
# Variables T(i,j,k), i<j<k: true = positive orientation, so (i,j,k) is a 'cup' (j below segment ik); false = 'cap'.
# Signotope axioms: for i<j<k<l the four triples ijk, ijl, ikl, jkl (lex order) change sign at most once.
# A convex polygon in x-order = a cup and a cap with the same two endpoints p<q; a points + b points give a+b-2 vertices.
# U[p,a,j,k] (cup) / V[p,a,j,k] (cap): there is an a-point chain starting at p whose last two points are j<k.
# Only implications from structure to variable are needed: an UNSAT answer is then a proof (for this model).
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
# signotope axioms
for i, j, k, l in itertools.combinations(range(n), 4):
    s = [T[(i, j, k)], T[(i, j, l)], T[(i, k, l)], T[(j, k, l)]]
    for x, y, z in itertools.combinations(range(4), 3):
        cls.append([-s[x], s[y], -s[z]])   # forbid + - +
        cls.append([s[x], -s[y], s[z]])    # forbid - + -
# chains
U, V, EU, EV = {}, {}, {}, {}
def get(d, key):
    if key not in d:
        d[key] = new()
    return d[key]
for p in range(n):
    # 3-point chains starting at p
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
    # chain of a points from p to q
    for (pp, a, j, q), v in list(U.items()):
        if pp == p:
            cls.append([-v, get(EU, (p, a, q))])
    for (pp, a, j, q), v in list(V.items()):
        if pp == p:
            cls.append([-v, get(EV, (p, a, q))])
# forbid a-cup and b-cap from p to q with a + b - 2 >= K (a, b >= 2; a 2-chain is the edge pq, always present)
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
# symmetry: reflecting in the x-axis swaps cups and caps, so fix the first triple
cls.append([T[(0, 1, 2)]])
with open(out, "w") as f:
    f.write("p cnf %d %d\n" % (nv, len(cls)))
    for c in cls:
        f.write(" ".join(map(str, c)) + " 0\n")
print("n=%d K=%d vars=%d clauses=%d" % (n, K, nv, len(cls)))
