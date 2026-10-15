# Independent check, without OR-Tools: is this 31-vector set 010-colourable?
# Exhaustive backtracking in plain Python: assign 0/1 vector by vector, prune on
# (a) two orthogonal vectors both 1, (b) three mutually orthogonal vectors all 0.
import itertools
V = [(0, 0, 1), (0, 1, -1), (0, 1, 0), (0, 1, 1), (0, 1, 2), (0, 2, -1), (1, -2, 0), (1, -2, 1),
     (1, -1, -2), (1, -1, -1), (1, -1, 0), (1, -1, 1), (1, 0, -2), (1, 0, -1), (1, 0, 0), (1, 0, 1),
     (1, 0, 2), (1, 1, -1), (1, 1, 0), (1, 1, 1), (1, 1, 2), (1, 2, -1), (1, 2, 0), (2, -1, -1),
     (2, -1, 0), (2, -1, 1), (2, 0, -1), (2, 0, 1), (2, 1, -1), (2, 1, 0), (2, 1, 1)]
n = len(V)
assert len(set(V)) == n
dot = lambda a, b: sum(x * y for x, y in zip(a, b))
orth = [[dot(V[i], V[j]) == 0 for j in range(n)] for i in range(n)]
tri = [t for t in itertools.combinations(range(n), 3) if orth[t[0]][t[1]] and orth[t[0]][t[2]] and orth[t[1]][t[2]]]
print(n, "vectors,", sum(orth[i][j] for i in range(n) for j in range(i + 1, n)), "orthogonal pairs,", len(tri), "orthogonal triples")
nodes = 0
def ok(c, k):
    # constraints whose vectors are all among the first k+1 assigned, involving vector k
    for j in range(k):
        if orth[j][k] and c[j] == 1 and c[k] == 1: return False
    for t in tri:
        if t[2] == k and c[t[0]] == 0 and c[t[1]] == 0 and c[k] == 0: return False
    return True
def search(c, k):
    global nodes
    nodes += 1
    if k == n: return True
    for b in (0, 1):
        c.append(b)
        if ok(c, k) and search(c, k + 1): return True
        c.pop()
    return False
found = search([], 0)
print("010-colouring exists:", found, "| search nodes:", nodes)
# each vector needed: drop one, check colourable
def colourable(S):
    sub = [V[i] for i in S]
    global V, n, orth, tri
    keep = (V, n, orth, tri)
    V = sub; n = len(sub)
    orth = [[dot(V[i], V[j]) == 0 for j in range(n)] for i in range(n)]
    tri = [t for t in itertools.combinations(range(n), 3) if orth[t[0]][t[1]] and orth[t[0]][t[2]] and orth[t[1]][t[2]]]
    r = search([], 0)
    V, n, orth, tri = keep
    return r
print("colourable after removing any one vector:", all(colourable([i for i in range(n) if i != u]) for u in range(n)))
