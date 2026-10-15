# Decode a kissat model for es_cnf.py and check by brute force that no K points are in convex position:
# a K-subset in x-order is convex iff its inner points split into a lower chain and an upper chain
# such that (first, lower..., last) is a cup and (first, upper..., last) is a cap, every consecutive triple checked.
# Also re-checks the signotope axiom on every 4-subset.
import sys, itertools
n, K, model = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
val = {}
for line in open(model):
    if line.startswith("v"):
        for x in line.split()[1:]:
            x = int(x)
            if x != 0:
                val[abs(x)] = x > 0
T = {}
v = 0
for t in itertools.combinations(range(n), 3):
    v += 1
    T[t] = val[v]
bad = 0
for i, j, k, l in itertools.combinations(range(n), 4):
    s = [T[(i, j, k)], T[(i, j, l)], T[(i, k, l)], T[(j, k, l)]]
    if sum(1 for x in range(3) if s[x] != s[x + 1]) > 1:
        bad += 1
print("signotope violations:", bad)
def chain_ok(ch, want):
    return all(T[(ch[m], ch[m + 1], ch[m + 2])] == want for m in range(len(ch) - 2))
found = 0
for S in itertools.combinations(range(n), K):
    inner = S[1:-1]
    for mask in range(1 << len(inner)):
        lo = [S[0]] + [inner[m] for m in range(len(inner)) if mask >> m & 1] + [S[-1]]
        up = [S[0]] + [inner[m] for m in range(len(inner)) if not mask >> m & 1] + [S[-1]]
        if chain_ok(lo, True) and chain_ok(up, False):
            found += 1
            break
print("convex %d-subsets found: %d (of %d subsets)" % (K, found, sum(1 for _ in itertools.combinations(range(n), K))))
