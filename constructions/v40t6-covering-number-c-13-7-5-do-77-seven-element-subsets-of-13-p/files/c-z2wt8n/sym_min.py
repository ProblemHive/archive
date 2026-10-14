# sym_min.py - control for sym_ilp.py: the smallest (13,7,5) covering invariant under one permutation of prime
# order p with c cycles, by minimising the number of blocks (same model as sym_ilp.py, objective instead of bound).
#   python sym_min.py SECONDS p c [p c ...]
import sys, time
from itertools import combinations
from ortools.sat.python import cp_model
from sym_ilp import perm, orbits, V, K, T

def minimise(p, c, secs):
    g = perm(p, c)
    tidx, treps, _ = orbits(g, p, T)
    kidx, kreps, ksize = orbits(g, p, K)
    m = cp_model.CpModel()
    x = [m.NewBoolVar(f"b{j}") for j in range(len(kreps))]
    through = [set() for _ in treps]
    for j, rep in enumerate(kreps):
        for t in combinations(rep, T):
            through[tidx[t]].add(j)
    for s in through:
        m.AddBoolOr([x[j] for j in s])
    m.Minimize(sum(ksize[j] * x[j] for j in range(len(kreps))))
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = secs
    sv.parameters.num_workers = 8
    t0 = time.time()
    st = sv.Solve(m)
    blocks = set()
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for j, rep in enumerate(kreps):
            if sv.Value(x[j]):
                cur = rep
                for _ in range(p):
                    blocks.add(cur); cur = tuple(sorted(g[y] for y in cur))
    covered = {t for b in blocks for t in combinations(b, T)}
    print(f"order {p}, {c} cycle(s): best covering found {len(blocks)} blocks (direct count: {len(covered)} of 1287 covered), "
          f"proved lower bound {sv.BestObjectiveBound():.0f}, status {sv.StatusName(st)}, {time.time() - t0:.0f}s", flush=True)

if __name__ == "__main__":
    a = sys.argv[2:]
    for i in range(0, len(a), 2):
        minimise(int(a[i]), int(a[i + 1]), float(sys.argv[1]))
