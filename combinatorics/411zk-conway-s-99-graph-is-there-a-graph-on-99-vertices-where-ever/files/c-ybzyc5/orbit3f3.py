"""srg(99,14,1,2): an automorphism g of order 3 with exactly 3 fixed vertices.
Is there an orbit matrix?  Split into cases by the part of the matrix that
is forced up to a few choices, one CP-SAT run per case.

Orbits: the fixed vertices a, b, c (indices 0, 1, 2) and 32 orbits of size 3.
C[i][j] = number of neighbours in orbit j of a vertex of orbit i.
Conditions on any orbit matrix (function build, the same for every graph):
  n_i C[i][j] = n_j C[j][i];  sum_j C[i][j] = k
  sum_m C[i][m] C[m][j] = (k-mu)[i=j] + (lam-mu) C[i][j] + mu n_j
  C[i][i] = 0 on a fixed vertex, 0 or 2 on an orbit of size 3.

Forced structure for (99,14,1,2), proved in the comment this file is posted in:
  a, b, c form a triangle.  The other 12 neighbours of a are 4 orbits
  A0..A3 (indices 3..6), with A0-A1 and A2-A3 joined by a matching (entry 1)
  and no other edges among them; the same for b (B0..B3, 7..10) and c
  (C0..C3, 11..14).  Every vertex of an A orbit has exactly one neighbour in
  the B orbits and one in the C orbits, so the blocks A-B, A-C and B-C are
  permutation matrices ab, ac, bc.  The other 20 orbits (15..34, 'outer')
  have 2 neighbours in the A orbits, 2 in B, 2 in C and 8 among themselves.
A case is a triple (ab, ac, bc) up to renaming: the 8 renamings of A0..A3
that keep the pairs {A0,A1},{A2,A3}, the same for B and C, and the 6
permutations of a, b, c.

usage: python orbit3f3.py control
       python orbit3f3.py list
       python orbit3f3.py case K DET [plain]
  K    case number from the list (1-based)
  DET  limit in CP-SAT's deterministic time units, not seconds, so a rerun
       stops at the same place
  plain  leave out the derived row sums and the fixed first column; only the
       case's 15 x 15 block and the ordering of the outer orbits are imposed
"""
import itertools
import sys
import time

import ortools
from ortools.sat.python import cp_model


def build(v, k, lam, mu, p, f, extra=None):
    q = (v - f) // p
    assert f + p * q == v
    n = [1] * f + [p] * q
    N = f + q
    m = cp_model.CpModel()
    C = [[None] * N for _ in range(N)]
    for i in range(N):
        for j in range(i, N):
            if i == j:
                if n[i] == 1:
                    C[i][i] = m.NewConstant(0)
                else:
                    assert p == 3
                    C[i][i] = m.NewIntVarFromDomain(cp_model.Domain.FromValues([0, 2]), f"d{i}")
            elif n[i] == n[j]:
                C[i][j] = m.NewIntVar(0, n[j], f"c{i}_{j}")
                C[j][i] = C[i][j]
            else:  # i fixed, j an orbit: all of it or none
                y = m.NewBoolVar(f"y{i}_{j}")
                C[j][i] = y
                C[i][j] = m.NewIntVar(0, p, f"c{i}_{j}")
                m.Add(C[i][j] == p * y)
    for i in range(N):
        m.Add(sum(C[i]) == k)
    prod = {}

    def P(a, b, c, d):  # C[a][b]*C[c][d]
        key = (a, b, c, d)
        if key not in prod:
            z = m.NewIntVar(0, 9 * p * p, "")
            m.AddMultiplicationEquality(z, [C[a][b], C[c][d]])
            prod[key] = z
        return prod[key]

    for i in range(N):
        for j in range(N):
            rhs = (k - mu) * (i == j) + mu * n[j]
            m.Add(sum(P(i, t, t, j) for t in range(N)) == rhs + (lam - mu) * C[i][j])
    if extra:
        extra(m, C, n, f)
    return m, C, n


# ---------------------------------------------------------------- the cases
PERMS = list(itertools.permutations(range(4)))
D4GEN = [(1, 0, 2, 3), (2, 3, 0, 1)]          # generate the 8 renamings keeping {0,1},{2,3}


def inv(p):
    r = [0] * 4
    for i, x in enumerate(p):
        r[x] = i
    return tuple(r)


def moves(t):
    ab, ac, bc = t
    for s in D4GEN:
        # rename the A orbits: new index s[i]
        yield (tuple(ab[inv(s)[i]] for i in range(4)), tuple(ac[inv(s)[i]] for i in range(4)), bc)
        # rename the B orbits
        yield (tuple(s[ab[i]] for i in range(4)), ac, tuple(bc[inv(s)[j]] for j in range(4)))
        # rename the C orbits
        yield (ab, tuple(s[ac[i]] for i in range(4)), tuple(s[bc[j]] for j in range(4)))
    yield (inv(ab), bc, ac)                    # swap a and b
    yield (ac, ab, inv(bc))                    # swap b and c


def case_list():
    seen = set()
    reps = []
    for t in itertools.product(PERMS, repeat=3):
        if t in seen:
            continue
        orbit = {t}
        stack = [t]
        while stack:
            x = stack.pop()
            for y in moves(x):
                if y not in orbit:
                    orbit.add(y)
                    stack.append(y)
        seen |= orbit
        reps.append((min(orbit), len(orbit)))
    reps.sort()
    assert sum(sz for _, sz in reps) == 24 ** 3
    return reps


def make_extra(ab, ac, bc, plain):
    A, B, Cc, OUT = range(3, 7), range(7, 11), range(11, 15), range(15, 35)

    def extra(m, C, n, f):
        for x, y in ((0, 1), (0, 2), (1, 2)):
            m.Add(C[x][y] == 1)
        for fx, grp in enumerate((A, B, Cc)):
            for o in range(3, 35):
                m.Add(C[o][fx] == (1 if o in grp else 0))
            for i in grp:
                for j in grp:
                    if i <= j:
                        partner = (i - grp[0]) // 2 == (j - grp[0]) // 2 and i != j
                        m.Add(C[i][j] == (1 if partner else 0))
        for g1, g2, perm in ((A, B, ab), (A, Cc, ac), (B, Cc, bc)):
            for i in range(4):
                for j in range(4):
                    m.Add(C[g1[i]][g2[j]] == (1 if perm[i] == j else 0))
        # the outer orbits are interchangeable: order them by their entries against orbits 3..14,
        # orbit 3 (A0) weighing most
        keys = [sum(C[o][j] * 4 ** (14 - j) for j in range(3, 15)) for o in OUT]
        for x, y in zip(keys, keys[1:]):
            m.Add(x >= y)
        if not plain:
            for o in OUT:
                for grp in (A, B, Cc):
                    m.Add(sum(C[o][j] for j in grp) == 2)
                m.Add(sum(C[o][j] for j in OUT) == 8)
            # column A0 holds one 2, eight 1s and eleven 0s (row sum 10, sum of squares 12);
            # with the ordering above that fixes it
            col = [2] + [1] * 8 + [0] * 11
            for o, val in zip(OUT, col):
                m.Add(C[o][3] == val)
            # exactly 2 orbits are triangles (diagonal 2).  The trace of A g is 3t for t such orbits, and the
            # multiplicities 1, 54, 44 of the eigenvalues 14, 3, -4 with 3 fixed vertices give t = 7m + 2;
            # g permutes the 231 triangles and fixes abc and those t, so t = 2 mod 3.  Hence t = 2.
            m.Add(sum(C[o][o] for o in OUT) == 4)
            # no entry 3 between orbits of size 3: two vertices of an orbit would get 3 common neighbours
            for i in range(3, 35):
                for j in range(i + 1, 35):
                    m.Add(C[i][j] <= 2)
            # entries 2: an inner orbit has exactly one (row sum and sum of squares), an outer orbit
            # has two if it is not a triangle and none if it is
            two = {}
            for i in range(3, 35):
                for j in OUT:
                    if i < j:
                        z = m.NewBoolVar(f"z{i}_{j}")
                        m.Add(C[i][j] == 2).OnlyEnforceIf(z)
                        m.Add(C[i][j] <= 1).OnlyEnforceIf(z.Not())
                        two[i, j] = two[j, i] = z
            for i in range(3, 15):
                m.Add(sum(two[i, j] for j in OUT) == 1)
            for o in OUT:
                m.Add(2 * sum(two[o, j] for j in range(3, 35) if j != o) + C[o][o] == 4)

    return extra


def solve(m, det=None, seconds=None):
    s = cp_model.CpSolver()
    s.parameters.num_workers = 8
    if det is not None:
        s.parameters.interleave_search = True      # makes the 8 workers reproducible
        s.parameters.max_deterministic_time = det
    if seconds is not None:
        s.parameters.max_time_in_seconds = seconds
    t = time.time()
    r = s.Solve(m)
    return s, r, time.time() - t


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "control":
        # the general equations on graphs where the answer is known
        want = {"rook9 f=0": ((9, 4, 1, 2, 3, 0), True), "petersen f=1": ((10, 3, 0, 1, 3, 1), True),
                "petersen f=4": ((10, 3, 0, 1, 3, 4), False), "clebsch f=1": ((16, 5, 0, 2, 3, 1), False),
                "clebsch f=4": ((16, 5, 0, 2, 3, 4), True)}
        ok = True
        for name, (par, exists) in want.items():
            m, C, n = build(*par)
            s, r, _ = solve(m, seconds=60)
            got = {cp_model.OPTIMAL: True, cp_model.FEASIBLE: True, cp_model.INFEASIBLE: False}.get(r)
            print(f"  {name}: matrix exists = {got}, expected {exists}")
            ok = ok and got == exists
        reps = case_list()
        print(f"  cases: {len(reps)}, orbit sizes {[sz for _, sz in reps]}")
        print("control ok" if ok else "control FAILED")
    elif mode == "list":
        for i, (t, sz) in enumerate(case_list(), 1):
            print(f"case {i:2d}  ab={t[0]} ac={t[1]} bc={t[2]}  triples in this class: {sz}")
    else:
        K, lim = int(sys.argv[2]), sys.argv[3]
        plain = len(sys.argv) > 4 and sys.argv[4] == "plain"
        (ab, ac, bc), sz = case_list()[K - 1]
        m, C, n = build(99, 14, 1, 2, 3, 3, make_extra(ab, ac, bc, plain))
        if lim.startswith("sec"):      # ordinary parallel search with a limit in seconds: not reproducible when it stops
            s, r, secs = solve(m, seconds=float(lim[3:]))
        else:
            s, r, secs = solve(m, det=float(lim))
        print(f"ortools {ortools.__version__} case {K} ab={ab} ac={ac} bc={bc} {'plain' if plain else 'full'} "
              f"limit={lim} status={s.StatusName(r)} conflicts={s.NumConflicts()} branches={s.NumBranches()}")
        print(f"(wall time {secs:.1f} s; INFEASIBLE = no orbit matrix in this case, UNKNOWN = limit reached)",
              file=sys.stderr)
        if r in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for row in C:
                print(" ".join(str(s.Value(x)) for x in row))
