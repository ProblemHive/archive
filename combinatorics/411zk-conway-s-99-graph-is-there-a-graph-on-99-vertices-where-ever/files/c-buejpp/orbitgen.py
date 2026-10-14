# Orbit matrices of a strongly regular graph srg(n,k,lam,mu) under a group whose orbits have given sizes,
# written from the general identity, as a cross-check of orbit7b.py and orbit7d.py.
#   c[i][j] = number of neighbours in orbit j of a vertex in orbit i
#   n_i c[i][j] = n_j c[j][i];   sum_j c[i][j] = k
#   sum_s c[i][s] c[s][j] = (k - mu) [i=j] + (lam - mu) c[i][j] + mu n_j
# usage: python c99/orbitgen.py control      the 3x3 rook's graph srg(9,4,1,2) with the map (i,j) -> (-i,-j)
#        python c99/orbitgen.py seven        srg(99,14,1,2), order 7, one fixed vertex
import itertools
import sys
import time
import ortools
from ortools.sat.python import cp_model


def model(sizes, k, lam, mu, diag_even):
    t = len(sizes)
    m = cp_model.CpModel()
    c = [[m.NewIntVar(0, sizes[j] - (1 if i == j else 0), f"c{i}_{j}") for j in range(t)] for i in range(t)]
    for i in range(t):
        m.Add(sum(c[i]) == k)
        if diag_even and sizes[i] > 1:
            h = m.NewIntVar(0, sizes[i], f"h{i}")
            m.Add(c[i][i] == 2 * h)
        for j in range(i + 1, t):
            m.Add(sizes[i] * c[i][j] == sizes[j] * c[j][i])
    for i in range(t):
        for j in range(t):
            terms = []
            for s in range(t):
                p = m.NewIntVar(0, sizes[s] * sizes[j], f"p{i}_{s}_{j}")
                m.AddMultiplicationEquality(p, [c[i][s], c[s][j]])
                terms.append(p)
            m.Add(sum(terms) == ((k - mu) if i == j else 0) + (lam - mu) * c[i][j] + mu * sizes[j])
    return m, c


def holds(C, sizes, k, lam, mu):
    t = len(sizes)
    return all(sum(C[i]) == k for i in range(t)) and all(
        sum(C[i][s] * C[s][j] for s in range(t)) == ((k - mu) if i == j else 0) + (lam - mu) * C[i][j] + mu * sizes[j]
        for i in range(t) for j in range(t)) and all(sizes[i] * C[i][j] == sizes[j] * C[j][i] for i in range(t) for j in range(t))


print("OR-Tools", ortools.__version__)
if sys.argv[1] == "control":
    V = list(itertools.product(range(3), range(3)))
    adj = lambda u, v: u != v and (u[0] == v[0] or u[1] == v[1])
    g = lambda v: ((-v[0]) % 3, (-v[1]) % 3)
    orbits = []
    for v in V:
        o = sorted({v, g(v)})
        if o not in orbits:
            orbits.append(o)
    sizes = [len(o) for o in orbits]
    C = [[sum(adj(oi[0], w) for w in oj) for oj in orbits] for oi in orbits]
    print("orbit sizes:", sizes)
    print("orbit matrix of the real graph:", C)
    print("it satisfies the equations:", holds(C, sizes, 4, 1, 2))
    m, c = model(sizes, 4, 1, 2, diag_even=False)
    sols = []

    class CB(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self):
            sols.append([[self.Value(c[i][j]) for j in range(len(sizes))] for i in range(len(sizes))])

    s = cp_model.CpSolver()
    s.parameters.enumerate_all_solutions = True
    s.parameters.num_workers = 1
    st = s.Solve(m, CB())
    print("status:", s.StatusName(st), " solutions of the model:", len(sols), " real matrix among them:", C in sols)
else:
    # orbit 0 = the fixed vertex x; orbits 1 and 2 = the two orbits in its neighbourhood; then 12 more
    sizes = [1] + [7] * 14
    m, c = model(sizes, 14, 1, 2, diag_even=True)
    m.Add(c[0][1] == 7)
    m.Add(c[0][2] == 7)
    # normalisation and symmetry breaking, as in orbit7b.py with every index shifted by one
    ROW = [1, 0, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0]
    for j in range(15):
        m.Add(c[1][j] == ROW[j])
    m.Add(c[3][3] >= c[4][4])
    m.Add(c[3][3] >= c[5][5])
    m.Add(c[3][4] >= c[3][5])
    for lo, hi in ((6, 12), (12, 15)):
        for j in range(lo, hi - 1):
            m.Add(c[3][j] >= c[3][j + 1])
            t2 = m.NewBoolVar(f"t2_{j}")
            m.Add(c[3][j] == c[3][j + 1]).OnlyEnforceIf(t2)
            m.Add(c[3][j] != c[3][j + 1]).OnlyEnforceIf(t2.Not())
            m.Add(c[4][j] >= c[4][j + 1]).OnlyEnforceIf(t2)
            e3 = m.NewBoolVar(f"e3_{j}")
            m.Add(c[4][j] == c[4][j + 1]).OnlyEnforceIf(e3)
            m.Add(c[4][j] != c[4][j + 1]).OnlyEnforceIf(e3.Not())
            m.Add(c[5][j] >= c[5][j + 1]).OnlyEnforceIf([t2, e3])
    s = cp_model.CpSolver()
    s.parameters.num_workers = 8
    s.parameters.max_time_in_seconds = 1500
    t0 = time.time()
    st = s.Solve(m)
    print("status:", s.StatusName(st), "(INFEASIBLE = no orbit matrix)")
    print(f"time {time.time() - t0:.0f} s, conflicts {s.NumConflicts()}")
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        C = [[s.Value(c[i][j]) for j in range(15)] for i in range(15)]
        print("re-checked:", holds(C, sizes, 14, 1, 2))
        for r in C:
            print("  ", " ".join(map(str, r)))
