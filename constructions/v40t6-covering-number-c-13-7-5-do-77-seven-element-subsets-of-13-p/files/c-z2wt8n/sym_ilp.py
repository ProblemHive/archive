# sym_ilp.py - is there a (13,7,5) covering with at most B blocks invariant under a permutation g of prime order?
# A g-invariant covering (no repeated blocks) is a union of g-orbits of 7-subsets. One 0/1 variable per orbit,
# weight = orbit size; every g-orbit of 5-subsets must lie in a chosen block orbit; total weight <= B.
# Every cycle type of prime order on 13 points is tried: p-cycles on the first c*p points, the rest fixed.
# Solver: OR-Tools CP-SAT, 8 workers.   python sym_ilp.py B SECONDS [p c]
import sys, time
from itertools import combinations
from ortools.sat.python import cp_model
import ortools
V, K, T = 13, 7, 5

def perm(p, c):
    g = list(range(V))
    for j in range(c):
        for i in range(p):
            g[j * p + i] = j * p + (i + 1) % p
    return g

def orbits(g, p, size):
    idx, reps, sizes = {}, [], []
    for s in combinations(range(V), size):
        if s in idx:
            continue
        orb, cur = [], s
        for _ in range(p):
            if cur not in idx:
                idx[cur] = len(reps); orb.append(cur)
            cur = tuple(sorted(g[x] for x in cur))
        reps.append(s); sizes.append(len(orb))
    return idx, reps, sizes

def solve(p, c, B, secs):
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
    m.Add(sum(ksize[j] * x[j] for j in range(len(kreps))) <= B)
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = secs
    sv.parameters.num_workers = 8
    t0 = time.time()
    st = sv.Solve(m)
    name = {cp_model.OPTIMAL: "FEASIBLE", cp_model.FEASIBLE: "FEASIBLE", cp_model.INFEASIBLE: "INFEASIBLE"}.get(st, "UNKNOWN (time limit)")
    print(f"order {p}, {c} cycle(s), {V - p * c} fixed points: {len(treps)} orbits of 5-subsets, {len(kreps)} orbits of 7-subsets "
          f"({ksize.count(1)} fixed blocks); at most {B} blocks: {name}, {time.time() - t0:.0f}s", flush=True)
    if name == "FEASIBLE":
        blocks = set()
        for j, rep in enumerate(kreps):
            if sv.Value(x[j]):
                cur = rep
                for _ in range(p):
                    blocks.add(cur); cur = tuple(sorted(g[y] for y in cur))
        covered = {t for b in blocks for t in combinations(b, T)}
        print(f"  blocks: {len(blocks)}; 5-subsets covered by direct count: {len(covered)} of 1287", flush=True)
        for b in sorted(blocks):
            print("  " + " ".join(map(str, b)))

if __name__ == "__main__":
    B, secs = int(sys.argv[1]), float(sys.argv[2])
    print("OR-Tools", ortools.__version__, flush=True)
    if len(sys.argv) > 3:
        cases = [(int(sys.argv[3]), int(sys.argv[4]))]
    else:
        cases = [(13, 1), (11, 1), (7, 1), (5, 2), (5, 1), (3, 4), (3, 3), (3, 2), (3, 1)] + [(2, c) for c in (6, 5, 4, 3, 2, 1)]
    for p, c in cases:
        solve(p, c, B, secs)
