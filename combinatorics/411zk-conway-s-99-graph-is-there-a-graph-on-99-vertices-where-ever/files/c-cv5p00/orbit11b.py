# Orbit matrices for an automorphism of order 11 on a putative srg(99,14,1,2).
# 99 = 9 * 11 and an element of order 11 fixes no vertex, so there are 9 orbits of size 11.
# b[i][j] = number of neighbours in orbit j of a vertex of orbit i; symmetric (equal orbit sizes),
# b[i][i] even (the graph on an orbit is a circulant on Z_11).
# From A^2 = 12 I - A + 2 J summed over orbits:
#   sum_j b[i][j] = 14
#   sum_s b[i][s] b[s][j] = 12 [i=j] - b[i][j] + 22
# Symmetry: any permutation of the 9 orbits. Symmetry breaking used (mode "strong"): orbit 0 has the largest
# diagonal entry, and the off-diagonal entries of row 0 are non-increasing. Mode "weak": only the second rule.
# Mode "none": no symmetry breaking.
# Backtracking, row by row, exhaustive.
# usage: python c99/orbit11b.py strong|weak|none
import sys
import time

T = 9
MODE = sys.argv[1]
b = [[0] * T for _ in range(T)]
t0 = time.time()
nodes = 0
sols = []


def full_check(M):
    for i in range(T):
        if sum(M[i]) != 14 or M[i][i] % 2:
            return False
        for j in range(T):
            if sum(M[i][s] * M[s][j] for s in range(T)) != (12 if i == j else 0) - M[i][j] + 22:
                return False
    return True


def place_row(i):
    if i == T:
        M = [r[:] for r in b]
        assert full_check(M)
        sols.append(M)
        return
    S = 14 - sum(b[i][:i])
    Q = 34 - sum(v * v for v in b[i][:i])          # squares of entries from column i on, plus the diagonal, must equal Q
    R = [22 - b[i][r] - sum(b[i][s] * b[s][r] for s in range(i)) for r in range(i)]

    def rec(j, s_left, q_left, R):
        global nodes
        nodes += 1
        if j == T:
            if s_left == 0 and q_left == 0 and not any(R):
                place_row(i + 1)
            return
        if s_left < 0 or q_left < s_left:
            return
        for v in ((0, 2, 4) if j == i else (0, 1, 2, 3, 4, 5)):
            if v > s_left:
                break
            if MODE == "strong" and j == i and i > 0 and v > b[0][0]:
                break
            if MODE in ("strong", "weak") and i == 0 and j >= 2 and v > b[0][j - 1]:
                break
            ql = q_left - v * v - (v if j == i else 0)
            if ql < 0:
                break
            if v:
                R2 = [R[r] - v * b[j][r] for r in range(i)]
                if R2 and min(R2) < 0:
                    continue
            else:
                R2 = R
            b[i][j] = b[j][i] = v
            rec(j + 1, s_left - v, ql, R2)
        b[i][j] = b[j][i] = 0

    rec(i, S, Q, R)


place_row(0)
print("python", sys.version.split()[0], "mode", MODE)
print("search complete: True")
print("nodes:", nodes)
print("orbit matrices found:", len(sols))
print(f"time {time.time() - t0:.1f} s")
for M in sols[:3]:
    print("matrix")
    for r in M:
        print("  ", " ".join(map(str, r)))
