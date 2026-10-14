"""srg(99,14,1,2), automorphism of order 3 with 3 fixed vertices: stage 1.

For one case (ab, ac, bc) of orbit3f3.py the 15 x 15 block of the orbit matrix
on a, b, c and the 12 inner orbits is known.  Let X be the 12 x 20 block
inner orbit against outer orbit.  The equations for two inner orbits i, j,
  sum_m C[i][m] C[m][j] = 12 [i=j] - C[i][j] + 6,
contain the outer orbits only through (X X^T)[i][j], so
  X X^T = G,   G = 12 I - Cin + 6 - 3 [i, j next to the same fixed vertex] - Cin^2,
with Cin the known 12 x 12 inner block.  A column of X (one outer orbit) has
sum 2 on the A orbits, 2 on B, 2 on C: (2) or (1,1) on each, 10^3 = 1000
possible columns.  So: non-negative integers n_p, one per possible column p,
with sum_p n_p p p^T = G.  That is a linear problem in 1000 unknowns, and the
order of the outer orbits no longer matters.

usage: python stage1.py K [MAXSOL]     K = case number, or 'all'
Prints for each case whether such a block X exists and, up to MAXSOL
(default 2000), how many there are up to the order of the columns.
One worker, no time limit: the output is the same on every run.
"""
import itertools
import sys

import ortools
from ortools.sat.python import cp_model

from orbit3f3 import case_list


def inner_block(ab, ac, bc):
    Cin = [[0] * 12 for _ in range(12)]
    for g in range(3):
        for a, b in ((0, 1), (2, 3)):
            Cin[4 * g + a][4 * g + b] = Cin[4 * g + b][4 * g + a] = 1
    for g1, g2, perm in ((0, 1, ab), (0, 2, ac), (1, 2, bc)):
        for i in range(4):
            Cin[4 * g1 + i][4 * g2 + perm[i]] = Cin[4 * g2 + perm[i]][4 * g1 + i] = 1
    return Cin


def gram(Cin):
    G = [[0] * 12 for _ in range(12)]
    for i in range(12):
        for j in range(12):
            sq = sum(Cin[i][m] * Cin[m][j] for m in range(12))
            G[i][j] = 12 * (i == j) - Cin[i][j] + 6 - 3 * (i // 4 == j // 4) - sq
    return G


def columns():
    part = []
    for i in range(4):
        v = [0] * 4
        v[i] = 2
        part.append(tuple(v))
    for i, j in itertools.combinations(range(4), 2):
        v = [0] * 4
        v[i] = v[j] = 1
        part.append(tuple(v))
    return [x + y + z for x in part for y in part for z in part]


COLS = columns()


def stage1(K, maxsol):
    (ab, ac, bc), _ = case_list()[K - 1]
    G = gram(inner_block(ab, ac, bc))
    m = cp_model.CpModel()
    n = [m.NewIntVar(0, 20, f"n{p}") for p in range(len(COLS))]
    m.Add(sum(n) == 20)
    for i in range(12):
        for j in range(i, 12):
            m.Add(sum(n[p] * (c[i] * c[j]) for p, c in enumerate(COLS) if c[i] * c[j]) == G[i][j])
    sols = []

    class CB(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self):
            sols.append({p: self.Value(n[p]) for p in range(len(COLS)) if self.Value(n[p])})
            if len(sols) >= maxsol:
                self.StopSearch()

    s = cp_model.CpSolver()
    s.parameters.num_workers = 1
    s.parameters.enumerate_all_solutions = True
    r = s.Solve(m, CB())
    complete = r in (cp_model.OPTIMAL, cp_model.INFEASIBLE) and len(sols) < maxsol
    print(f"case {K:2d} ab={ab} ac={ac} bc={bc}: blocks X up to column order: {len(sols)}"
          f"{'' if complete else ' or more (stopped at the cap)'}; status {s.StatusName(r)}, conflicts {s.NumConflicts()}")
    return G, sols


if __name__ == "__main__":
    print("ortools", ortools.__version__)
    maxsol = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    ks = range(1, len(case_list()) + 1) if sys.argv[1] == "all" else [int(sys.argv[1])]
    for K in ks:
        stage1(K, maxsol)
