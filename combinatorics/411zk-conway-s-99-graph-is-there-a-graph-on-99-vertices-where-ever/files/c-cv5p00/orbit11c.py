# Order 11 on a putative srg(99,14,1,2): the equations of orbit11b.py in CP-SAT, as a second method.
# 9 orbits of size 11; b symmetric, b[i][i] even, row sums 14,
# sum_s b[i][s] b[s][j] = 12 [i=j] - b[i][j] + 22.
# Symmetry breaking: orbit 0 has the largest diagonal entry; off-diagonal entries of row 0 non-increasing.
# usage: python c99/orbit11c.py
import time
import ortools
from ortools.sat.python import cp_model

T = 9
m = cp_model.CpModel()
b = [[None] * T for _ in range(T)]
for i in range(T):
    for j in range(i, T):
        if i == j:
            h = m.NewIntVar(0, 5, f"h{i}")
            v = m.NewIntVar(0, 10, f"b{i}_{i}")
            m.Add(v == 2 * h)
        else:
            v = m.NewIntVar(0, 11, f"b{i}_{j}")
        b[i][j] = b[j][i] = v
for i in range(T):
    m.Add(sum(b[i]) == 14)
for i in range(T):
    for j in range(i, T):
        terms = []
        for s in range(T):
            p = m.NewIntVar(0, 121, f"m{i}_{s}_{j}")
            m.AddMultiplicationEquality(p, [b[i][s], b[s][j]])
            terms.append(p)
        m.Add(sum(terms) + b[i][j] == (12 if i == j else 0) + 22)
for i in range(1, T):
    m.Add(b[0][0] >= b[i][i])
for j in range(1, T - 1):
    m.Add(b[0][j] >= b[0][j + 1])
s = cp_model.CpSolver()
s.parameters.num_workers = 8
s.parameters.max_time_in_seconds = 600
t0 = time.time()
st = s.Solve(m)
print("OR-Tools", ortools.__version__)
print("status:", s.StatusName(st), "(INFEASIBLE = no orbit matrix exists)")
print(f"time {time.time() - t0:.1f} s, conflicts {s.NumConflicts()}, branches {s.NumBranches()}")
if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    for r in b:
        print("  ", " ".join(str(s.Value(x)) for x in r))
