# Is there any orbit matrix for an automorphism of order 7 with exactly one fixed vertex x
# on a putative srg(99,14,1,2)?  Decision version with CP-SAT (8 workers).
# Orbits: x and 14 orbits of size 7; orbits 0 and 1 lie in the neighbourhood of x.
# b[i][j] = number of neighbours in orbit j of a vertex of orbit i (symmetric).
#   [i<2] + sum_j b[i][j] = 14
#   sum_s b[i][s] b[s][j] = 12 [i=j] - b[i][j] + 14 - 7 [i<2 and j<2]
#   b[0][j] + b[1][j] = 2 for j >= 2, b[0][0] = b[1][1] = 0, b[0][1] = 1   (the equations of the row of x)
#   b[i][i] even.
# Row 0 is fixed: 0 1 | 2 2 2 | 1 1 1 1 1 1 | 0 0 0 (forced up to order by its sum 13 and sum of squares 19).
# Symmetry breaking: inside each of the three column groups the diagonals are non-increasing.
# usage: python c99/orbit7c.py [seconds]
import sys
import time
import ortools
from ortools.sat.python import cp_model

T = 14
ROW0 = [0, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0]
GROUPS = [(2, 5), (5, 11), (11, 14)]
m = cp_model.CpModel()
b = [[None] * T for _ in range(T)]
for i in range(T):
    for j in range(i, T):
        if i == j:
            h = m.NewIntVar(0, 1, f"h{i}")
            v = m.NewIntVar(0, 2, f"b{i}_{i}")
            m.Add(v == 2 * h)          # diagonal 4 or 6 is impossible: the row would need sum of squares below its sum
        else:
            v = m.NewIntVar(0, 4, f"b{i}_{j}")   # an entry 5 has square 25, leaving at most 1 for entries that sum to 9
        b[i][j] = b[j][i] = v
for j in range(T):
    m.Add(b[0][j] == ROW0[j])
m.Add(b[1][1] == 0)
for j in range(2, T):
    m.Add(b[1][j] == 2 - ROW0[j])
for i in range(T):
    m.Add(sum(b[i]) == 14 - (1 if i < 2 else 0))
for i in range(T):
    for j in range(i, T):
        terms = []
        for s in range(T):
            p = m.NewIntVar(0, 16, f"m{i}_{s}_{j}")
            m.AddMultiplicationEquality(p, [b[i][s], b[s][j]])
            terms.append(p)
        rhs = (12 if i == j else 0) + 14 - (7 if (i < 2 and j < 2) else 0)
        m.Add(sum(terms) + b[i][j] == rhs)
# symmetry breaking, as in orbit7b.py: orbit 2 has the largest diagonal of its group, b[2][3] >= b[2][4],
# and inside the groups 5-10 and 11-13 the columns, read down rows 2,3,4, are lexicographically non-increasing
m.Add(b[2][2] >= b[3][3])
m.Add(b[2][2] >= b[4][4])
m.Add(b[2][3] >= b[2][4])
for lo, hi in GROUPS[1:]:
    for j in range(lo, hi - 1):
        m.Add(b[2][j] >= b[2][j + 1])
        t2 = m.NewBoolVar(f"t2_{j}")
        m.Add(b[2][j] == b[2][j + 1]).OnlyEnforceIf(t2)
        m.Add(b[2][j] != b[2][j + 1]).OnlyEnforceIf(t2.Not())
        m.Add(b[3][j] >= b[3][j + 1]).OnlyEnforceIf(t2)
        e3 = m.NewBoolVar(f"e3_{j}")
        m.Add(b[3][j] == b[3][j + 1]).OnlyEnforceIf(e3)
        m.Add(b[3][j] != b[3][j + 1]).OnlyEnforceIf(e3.Not())
        m.Add(b[4][j] >= b[4][j + 1]).OnlyEnforceIf([t2, e3])

s = cp_model.CpSolver()
s.parameters.num_workers = 8
s.parameters.max_time_in_seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 1500
t0 = time.time()
st = s.Solve(m)
print("OR-Tools", ortools.__version__)
print("status:", s.StatusName(st), "(INFEASIBLE = no orbit matrix exists; OPTIMAL or FEASIBLE = one was found; UNKNOWN = time ran out)")
print(f"time {time.time() - t0:.0f} s, conflicts {s.NumConflicts()}, branches {s.NumBranches()}")
if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    M = [[s.Value(b[i][j]) for j in range(T)] for i in range(T)]
    ok = all((1 if i < 2 else 0) + sum(M[i]) == 14 for i in range(T)) and all(
        sum(M[i][k] * M[k][j] for k in range(T)) == (12 if i == j else 0) - M[i][j] + 14 - (7 if (i < 2 and j < 2) else 0)
        for i in range(T) for j in range(T))
    print("re-checked against the equations in plain Python:", ok)
    for r in M:
        print("  ", " ".join(map(str, r)))
