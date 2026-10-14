# Exhaustive search for (13,7,5) coverings invariant under a permutation of prime order P of the 13 points:
# P = 13: x -> x+1 mod 13.  P = 11: x -> x+1 mod 11 on points 0..10, points 11 and 12 fixed.
# Such a covering is a union of orbits of 7-subsets (all of size P); it must cover every orbit of 5-subsets. Depth-first search: take the uncovered 5-orbit with the fewest block orbits
# containing it, branch on those. Prints the number of solutions with n orbits and the first one found.
#   python sym_cover.py P n
import sys, time
from itertools import combinations
V, K, T = 13, 7, 5
P, n = int(sys.argv[1]), int(sys.argv[2])

def canon(s):
    return min(tuple(sorted((x + i) % P if x < P else x for x in s)) for i in range(P))

t_orb = {}
for c in combinations(range(V), T):
    t_orb.setdefault(canon(c), len(t_orb))
k_reps = sorted({canon(c) for c in combinations(range(V), K)})
cov = []
for rep in k_reps:
    m = 0
    for c in combinations(rep, T):
        m |= 1 << t_orb[canon(c)]
    cov.append(m)
NT = len(t_orb)
FULL = (1 << NT) - 1
by_t = [[j for j, m in enumerate(cov) if m >> i & 1] for i in range(NT)]
maxc = max(bin(m).count("1") for m in cov)
print(f"{NT} orbits of 5-subsets, {len(k_reps)} orbits of 7-subsets, a block orbit covers at most {maxc} of them")

sols = set(); nodes = 0
def dfs(covered, chosen):
    global nodes
    nodes += 1
    if covered == FULL:
        sols.add(frozenset(chosen)); return
    left = n - len(chosen)
    if left == 0 or NT - bin(covered).count("1") > left * maxc:
        return
    unc = [i for i in range(NT) if not covered >> i & 1]
    i = min(unc, key=lambda i: len(by_t[i]))
    for j in by_t[i]:
        dfs(covered | cov[j], chosen + [j])
t0 = time.time()
dfs(0, [])
print(f"n = {n} orbits ({P * n} blocks): {len(sols)} coverings (as sets of orbits), {nodes} search nodes, {time.time() - t0:.0f}s")
if sols:
    s = sorted(min(sols, key=sorted))
    print("first: base blocks (apply the permutation P times):")
    for j in s:
        print(" ".join(map(str, k_reps[j])))
