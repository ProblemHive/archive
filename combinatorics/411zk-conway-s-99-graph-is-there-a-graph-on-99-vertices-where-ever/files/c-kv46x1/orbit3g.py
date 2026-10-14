"""srg(99,14,1,2), automorphism of order 3 with a fixed triangle: second encoding of one case.

Same equations as orbit3f3.py, written so that most of them are linear.
The 20 outer orbits are the orbits of g on the 60 non-matched pairs of the 12 other neighbours of a
(an outer vertex has exactly 2 neighbours there, and each non-matched pair has exactly one common
neighbour besides a, so outer vertices and such pairs correspond one to one).  Hence the A part of every
outer column is known: 4 columns '2 on one A orbit', 2 columns each on the matched pairs {A0,A1}, {A2,A3},
3 columns on each of the other four pairs.  Unknown: the B type and C type of each outer orbit (10 types each,
same multiplicities) and the 20 x 20 outer block Y (entries 0..2, diagonal 0 or 2).

usage: python orbit3g.py case K SECONDS
"""
import itertools
import sys
import time

import ortools
from ortools.sat.python import cp_model

from orbit3f3 import case_list
from stage1 import inner_block, gram

TYPES = []
for i in range(4):
    v = [0] * 4
    v[i] = 2
    TYPES.append(tuple(v))
PAIRS = list(itertools.combinations(range(4), 2))
for i, j in PAIRS:
    v = [0] * 4
    v[i] = v[j] = 1
    TYPES.append(tuple(v))
MULT = [1, 1, 1, 1] + [2 if p in ((0, 1), (2, 3)) else 3 for p in PAIRS]
ACOL = [t for t in range(10) for _ in range(MULT[t])]
NO = 20


def model(K):
    (ab, ac, bc), _ = case_list()[K - 1]
    Cin = inner_block(ab, ac, bc)
    G = gram(Cin)
    m = cp_model.CpModel()
    A = [TYPES[ACOL[o]] for o in range(NO)]
    for i in range(4):
        for j in range(4):
            assert sum(A[o][i] * A[o][j] for o in range(NO)) == G[i][j]
    jb = [[m.NewBoolVar(f"jb{o}_{t}") for t in range(10)] for o in range(NO)]
    jc = [[m.NewBoolVar(f"jc{o}_{t}") for t in range(10)] for o in range(NO)]
    for o in range(NO):
        m.AddExactlyOne(jb[o])
        m.AddExactlyOne(jc[o])
    for t in range(10):
        m.Add(sum(jb[o][t] for o in range(NO)) == MULT[t])
        m.Add(sum(jc[o][t] for o in range(NO)) == MULT[t])
    xb = [[m.NewIntVar(0, 2, f"xb{o}_{j}") for j in range(4)] for o in range(NO)]
    xc = [[m.NewIntVar(0, 2, f"xc{o}_{j}") for j in range(4)] for o in range(NO)]
    for o in range(NO):
        for j in range(4):
            m.Add(xb[o][j] == sum(TYPES[t][j] * jb[o][t] for t in range(10)))
            m.Add(xc[o][j] == sum(TYPES[t][j] * jc[o][t] for t in range(10)))
    # X[i][o] for inner orbit i = 0..11 (A, B, C) as constant or variable
    X = [[A[o][i] for o in range(NO)] for i in range(4)] + [[xb[o][i] for o in range(NO)] for i in range(4)] \
        + [[xc[o][i] for o in range(NO)] for i in range(4)]

    def mul(u, v, hi):
        if isinstance(u, int):
            return u * v
        if isinstance(v, int):
            return v * u
        z = m.NewIntVar(0, hi, "")
        m.AddMultiplicationEquality(z, [u, v])
        return z

    # X X^T = G (the A-A block holds by construction)
    for i in range(12):
        for j in range(max(i, 4), 12):
            if i // 4 == j // 4 and i >= 4:
                # same group B or C: forced by the multiplicities of the types
                continue
            m.Add(sum(mul(X[i][o], X[j][o], 4) for o in range(NO)) == G[i][j])
    # outer block
    d = [m.NewBoolVar(f"d{o}") for o in range(NO)]
    Y = [[None] * NO for _ in range(NO)]
    for o in range(NO):
        for p in range(o + 1, NO):
            Y[o][p] = Y[p][o] = m.NewIntVar(0, 2, f"y{o}_{p}")
    Yd = [[(2 * d[o] if o == p else Y[o][p]) for p in range(NO)] for o in range(NO)]
    for o in range(NO):
        m.Add(sum(Yd[o]) == 8)
    m.Add(sum(d) == 2)          # exactly two triangle orbits (trace argument, see c/ybzyc5)
    # inner row i against outer column o:  sum_m X[i][m] Y[m][o] = 6 - X[i][o] - sum_j Cin[i][j] X[j][o]
    for i in range(12):
        for o in range(NO):
            terms = []
            for mm in range(NO):
                if mm == o:
                    terms.append(2 * mul(X[i][mm], d[o], 2))
                else:
                    terms.append(mul(X[i][mm], Y[mm][o], 4))
            m.Add(sum(terms) == 6 - X[i][o] - sum(X[j][o] for j in range(12) if Cin[i][j]))
    # outer rows o, p:  sum_m Y[o][m] Y[m][p] + Y[o][p] + x_o . x_p = 6 + 12 [o=p]
    for o in range(NO):
        for p in range(o, NO):
            if o == p:
                sq = sum((4 * d[o] if mm == o else mul(Y[o][mm], Y[o][mm], 4)) for mm in range(NO))
                dot = sum(v * v for v in A[o]) + sum((4 if t < 4 else 2) * (jb[o][t] + jc[o][t]) for t in range(10))
                m.Add(sq + 2 * d[o] + dot == 18)
            else:
                terms = []
                for mm in range(NO):
                    if mm == o:
                        terms.append(2 * mul(Y[mm][p], d[o], 2))
                    elif mm == p:
                        terms.append(2 * mul(Y[o][mm], d[p], 2))
                    else:
                        terms.append(mul(Y[o][mm], Y[mm][p], 4))
                dot = sum(A[o][j] * A[p][j] for j in range(4)) + sum(mul(xb[o][j], xb[p][j], 4) for j in range(4)) \
                    + sum(mul(xc[o][j], xc[p][j], 4) for j in range(4))
                m.Add(sum(terms) + Y[o][p] + dot == 6)
    # outer orbits with the same A type are interchangeable: order them by (B type, C type)
    key = [sum((10 * t) * jb[o][t] + t * jc[o][t] for t in range(10)) for o in range(NO)]
    for o in range(NO - 1):
        if ACOL[o] == ACOL[o + 1]:
            m.Add(key[o] <= key[o + 1])
    return m, (ab, ac, bc), jb, jc, Yd, d


if __name__ == "__main__":
    K, secs = int(sys.argv[2]), float(sys.argv[3])
    m, case, jb, jc, Yd, d = model(K)
    s = cp_model.CpSolver()
    s.parameters.num_workers = 8
    s.parameters.max_time_in_seconds = secs
    t0 = time.time()
    r = s.Solve(m)
    print(f"ortools {ortools.__version__} orbit3g case {K} {case} limit {secs:.0f} s status={s.StatusName(r)} "
          f"conflicts={s.NumConflicts()} branches={s.NumBranches()} wall={time.time()-t0:.0f} s")
    if r in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for o in range(NO):
            tb = [t for t in range(10) if s.Value(jb[o][t])][0]
            tc = [t for t in range(10) if s.Value(jc[o][t])][0]
            print(TYPES[ACOL[o]], TYPES[tb], TYPES[tc], "|", " ".join(str(s.Value(v)) if not isinstance(v, int) else str(v) for v in Yd[o]))
