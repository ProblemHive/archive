# Which vertices and edges of the graph are critical for non-4-colourability?
# usage: python 1hx33/critical.py 510
# Reads 1hx33/N.unit (pairs at exact unit distance, written by check_graph.py).
import sys
import time
from multiprocessing import Pool
from pysat.solvers import Cadical153

name = sys.argv[1]
E = [tuple(map(int, l.split())) for l in open(f"1hx33/{name}.unit")]
N = max(max(e) for e in E)
K4 = 4
var = lambda v, c: (v - 1) * K4 + c + 1


def colourable(job):
    kind, x = job
    edges = [e for e in E if not (kind == "v" and x in e) and not (kind == "e" and e == x)]
    verts = [v for v in range(1, N + 1) if not (kind == "v" and v == x)]
    adj = {v: set() for v in verts}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    tri = next(((a, b, c) for a, b in edges for c in adj[a] & adj[b]), None)
    s = Cadical153()
    for v in verts:
        s.add_clause([var(v, c) for c in range(K4)])
    for a, b in edges:
        for c in range(K4):
            s.add_clause([-var(a, c), -var(b, c)])
    for k, v in enumerate(tri or ()):
        s.add_clause([var(v, k)])
    t = time.time()
    sat = s.solve()
    if sat:                                  # check the colouring the solver returned
        m = set(l for l in s.get_model() if l > 0)
        col = {v: next(c for c in range(K4) if var(v, c) in m) for v in verts}
        assert all(col[a] != col[b] for a, b in edges)
    s.delete()
    return kind, x, sat, time.time() - t


if __name__ == "__main__":
    t0 = time.time()
    print("graph:", N, "vertices,", len(E), "edges")
    print("whole graph 4-colourable:", colourable(("none", None))[2])
    jobs = [("v", v) for v in range(1, N + 1)] + [("e", e) for e in E]
    with Pool(8) as p:
        res = p.map(colourable, jobs, chunksize=8)
    for kind, label in (("v", "vertex"), ("e", "edge")):
        r = [x for x in res if x[0] == kind]
        crit = [x for x in r if x[2]]
        non = [x[1] for x in r if not x[2]]
        print(f"{label} removals tested: {len(r)}; graph becomes 4-colourable (critical): {len(crit)}; stays non-4-colourable: {len(non)}")
        print(f"  solve time per removal: max {max(x[3] for x in r):.1f} s, total {sum(x[3] for x in r):.0f} s")
        if non:
            print("  not critical:", non[:60], "..." if len(non) > 60 else "")
    print(f"wall time {time.time() - t0:.0f} s")
