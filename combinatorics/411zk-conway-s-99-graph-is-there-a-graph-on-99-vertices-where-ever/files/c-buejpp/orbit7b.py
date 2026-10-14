# Orbit matrices for an automorphism of order 7 with exactly one fixed vertex x acting on a
# putative srg(99,14,1,2): backtracking search, row by row.
# Orbits: x and 14 orbits of size 7; orbits 0 and 1 lie in the neighbourhood of x.
# b[i][j] = number of neighbours in orbit j of a vertex of orbit i (symmetric).
# From A^2 = 12 I - A + 2 J, summed over orbits:
#   [i<2] + sum_j b[i][j] = 14
#   sum_s b[i][s] b[s][j] = 12 [i=j] - b[i][j] + 14 - 7 [i<2 and j<2]
#   b[i][i] even.
# Row 0 is fixed without loss of generality (see the comment in the post): 0 1 | 2 2 2 | 1 1 1 1 1 1 | 0 0 0.
# Symmetry breaking (permutations of orbits inside the three groups 2-4, 5-10, 11-13): orbit 2 has the largest
# diagonal of its group, b[2][3] >= b[2][4], and inside the groups 5-10 and 11-13 the columns, read down rows 2,3,4,
# are in non-increasing lexicographic order.
# usage: python c99/orbit7b.py [seconds]
import json
import sys
import time
import pynauty

T = 14
LIMIT = float(sys.argv[1]) if len(sys.argv) > 1 else 1500
ROW0 = [0, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0]
GROUP = [None, None, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2]
b = [[0] * T for _ in range(T)]
b[0] = ROW0[:]
for j in range(T):
    b[j][0] = ROW0[j]
b[1][1] = 0
for j in range(2, T):
    b[1][j] = b[j][1] = 2 - ROW0[j]
# check rows 0 and 1 against the equations
for i in (0, 1):
    assert 1 + sum(b[i]) == 14
    assert sum(v * v for v in b[i]) == 12 - b[i][i] + 14 - 7
assert sum(b[0][s] * b[s][1] for s in range(T)) == 14 - b[0][1] - 7

t0 = time.time()
nodes = 0
found = 0
classes = {}
timed_out = False


def canon(M):
    n = T
    adj = {v: [] for v in range(T)}
    cols = {}
    for i in range(T):
        cols.setdefault(("o", i < 2, M[i][i]), set()).add(i)
    for i in range(T):
        for j in range(i + 1, T):
            if M[i][j]:
                adj[n] = [i, j]
                cols.setdefault(("e", M[i][j]), set()).add(n)
                n += 1
    keys = sorted(cols, key=str)
    g = pynauty.Graph(n, directed=False, adjacency_dict=adj, vertex_coloring=[cols[k] for k in keys])
    return (tuple(str(k) + ":" + str(len(cols[k])) for k in keys), pynauty.certificate(g))


def full_check(M):
    for i in range(T):
        if (1 if i < 2 else 0) + sum(M[i]) != 14:
            return False
        for j in range(T):
            rhs = (12 if i == j else 0) - M[i][j] + 14 - (7 if (i < 2 and j < 2) else 0)
            if sum(M[i][s] * M[s][j] for s in range(T)) != rhs:
                return False
    return True


def place_row(i):
    """choose b[i][i..13]; rows < i are complete"""
    global nodes, found, timed_out
    if i == T:
        found += 1
        M = [r[:] for r in b]
        assert full_check(M)
        c = canon(M)
        if c not in classes:
            classes[c] = M
            print(f"  new class {len(classes)} after {found} matrices, {time.time() - t0:.0f} s", flush=True)
        return
    S = 14 - sum(b[i][:i])                       # what the entries from column i on must add up to
    sq0 = sum(v * v for v in b[i][:i])
    # residuals of the inner products with the earlier rows r (all entries of row r are known)
    R = [14 - b[i][r] - sum(b[i][s] * b[s][r] for s in range(i)) for r in range(i)]
    coef = [[b[j][r] for r in range(i)] for j in range(T)]      # coef[j][r] = b[j][r]
    dmax = b[2][2] if i in (3, 4) else 2

    def rec(j, s_left, q_left, R):
        global nodes, timed_out
        nodes += 1
        if nodes % 200000 == 0 and time.time() - t0 > LIMIT:
            timed_out = True
        if timed_out:
            return
        if j == T:
            if s_left == 0 and q_left == 0 and not any(R):
                place_row(i + 1)
            return
        rem = T - j
        if s_left < 0 or q_left < s_left or s_left > 4 * rem:
            return
        for v in ((0, 2) if j == i else (0, 1, 2, 3, 4)):
            if j == i and v > dmax:
                continue
            if v > s_left:
                break
            if i <= 4 and j > i:
                if i == 2 and j == 4 and v > b[2][3]:
                    break
                if j >= 6 and GROUP[j] == GROUP[j - 1] and v > b[i][j - 1] and all(b[r][j] == b[r][j - 1] for r in range(2, i)):
                    break
            # q_left is defined so that the diagonal equation reads: sum of squares of the entries = 26 - d
            ql = q_left - v * v - (v if j == i else 0)
            if ql < 0:
                break
            if v:
                c = coef[j]
                R2 = [R[r] - v * c[r] for r in range(i)]
                if min(R2, default=0) < 0:
                    continue
            else:
                R2 = R
            b[i][j] = b[j][i] = v
            rec(j + 1, s_left - v, ql, R2)
        b[i][j] = b[j][i] = 0

    rec(i, S, 26 - sq0, R)


place_row(2)
print("pynauty", pynauty.__version__, "python", sys.version.split()[0])
print("search complete:", not timed_out)
print("nodes:", nodes)
print("orbit matrices found (with partial symmetry breaking):", found)
print("classes up to relabelling of orbits:", len(classes))
print(f"time {time.time() - t0:.0f} s")
json.dump(list(classes.values()), open("c99/orbit7_classes.json", "w"))
for k, M in enumerate(list(classes.values())[:2]):
    print("class", k + 1)
    for r in M:
        print("  ", " ".join(map(str, r)))
