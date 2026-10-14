# small_cov.py - covering number C(v,k,t) by CP-SAT: fewest k-subsets of a v-set containing every t-subset.
# The first point's blocks are not fixed; one symmetry-breaking step only: the block 0..k-1 is chosen.
#   python small_cov.py SECONDS v k t [v k t ...]
import sys, time
from itertools import combinations
from ortools.sat.python import cp_model

def cov(v, k, t, secs):
    ks = list(combinations(range(v), k))
    idx = {b: j for j, b in enumerate(ks)}
    m = cp_model.CpModel()
    x = [m.NewBoolVar(f"b{j}") for j in range(len(ks))]
    for s in combinations(range(v), t):
        rest = [y for y in range(v) if y not in s]
        m.AddBoolOr([x[idx[tuple(sorted(s + e))]] for e in combinations(rest, k - t)])
    m.Add(x[0] == 1)
    m.Minimize(sum(x))
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = secs
    sv.parameters.num_workers = 8
    t0 = time.time()
    st = sv.Solve(m)
    print(f"C({v},{k},{t}): best found {sv.ObjectiveValue():.0f}, proved lower bound {sv.BestObjectiveBound():.0f}, "
          f"status {sv.StatusName(st)}, {time.time() - t0:.0f}s", flush=True)

a = sys.argv[2:]
for i in range(0, len(a), 3):
    cov(int(a[i]), int(a[i + 1]), int(a[i + 2]), float(sys.argv[1]))
