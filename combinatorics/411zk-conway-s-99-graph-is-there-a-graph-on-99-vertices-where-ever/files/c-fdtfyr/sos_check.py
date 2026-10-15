# Check of the bound T(99) <= 55 stated in arXiv:2610.16266v1 (Conjecture 5, section 3.2):
# "the maximum number of triangles in a graph on 99 vertices containing no diamond and no K_{2,3}
#  (as subgraphs) is at most 55".
# Counterexample candidate: 11 disjoint copies of the 3x3 rook's graph K3 x K3 = srg(9,4,1,2).
# Checks, by brute force on the 99-vertex graph:
#  - diamond (K4 minus an edge) as a subgraph  <=> some edge lies in two or more triangles;
#  - K_{2,3} as a subgraph                     <=> some pair of distinct vertices has >= 3 common neighbours;
#  - the number of triangles.
# Also builds the same check for one copy (n = 9) and confirms it is srg(9,4,1,2).
from itertools import combinations

def rook(offset):
    cells = [(i, j) for i in range(3) for j in range(3)]
    idx = {c: offset + k for k, c in enumerate(cells)}
    edges = set()
    for a, b in combinations(cells, 2):
        if a[0] == b[0] or a[1] == b[1]:
            edges.add(frozenset((idx[a], idx[b])))
    return edges

def analyse(n, edges):
    adj = [set() for _ in range(n)]
    for e in edges:
        u, v = tuple(e)
        adj[u].add(v); adj[v].add(u)
    tri = sum(1 for u, v, w in combinations(range(n), 3) if v in adj[u] and w in adj[u] and w in adj[v])
    max_tri_per_edge = max(len(adj[u] & adj[v]) for u, v in (tuple(e) for e in edges))
    max_common = max(len(adj[u] & adj[v]) for u, v in combinations(range(n), 2))
    degs = sorted(set(len(a) for a in adj))
    return tri, max_tri_per_edge, max_common, degs, adj

# one copy: srg(9,4,1,2)?
tri, mte, mc, degs, adj = analyse(9, rook(0))
lam = {len(adj[u] & adj[v]) for u, v in combinations(range(9), 2) if v in adj[u]}
mu = {len(adj[u] & adj[v]) for u, v in combinations(range(9), 2) if v not in adj[u]}
print(f"n=9 rook graph: degrees {degs}, lambda values {lam}, mu values {mu}, triangles {tri}")

# 11 disjoint copies on 99 vertices
edges = set()
for c in range(11):
    edges |= rook(9 * c)
tri, mte, mc, degs, adj = analyse(99, edges)
print(f"n=99, 11 copies: edges {len(edges)}, triangles {tri}")
print(f"  max triangles through one edge = {mte}  (diamond-free as a subgraph iff <= 1)")
print(f"  max common neighbours of two vertices = {mc}  (K_(2,3)-free as a subgraph iff <= 2)")
print("  diamond-free:", mte <= 1, " K23-free:", mc <= 2, " exceeds 55:", tri > 55)
# monotonicity: adding isolated vertices keeps both properties, so T(n) is non-decreasing in n
print("T(n) >= 6*floor(n/9) for every n; e.g. T(99) >= 66, T(243) >= 162")
