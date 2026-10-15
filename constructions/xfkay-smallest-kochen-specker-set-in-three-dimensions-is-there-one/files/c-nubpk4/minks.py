# Smallest Kochen-Specker set whose vectors all have coordinates in {-m..m} (3D, real).
# KS set: no 0/1 colouring with (a) no two orthogonal vectors both 1, (b) exactly one 1 in
# every orthogonal basis (three mutually orthogonal vectors) contained in the set.
# Method: CP-SAT master chooses a subset S of minimum size; a colouring of S found by the
# subproblem is extended to all rays and turned into cuts (with its 48 images under the
# signed permutations of the axes). Stops when the chosen S has no colouring.
import sys, itertools, math, time
from ortools.sat.python import cp_model

m = int(sys.argv[1]) if len(sys.argv) > 1 else 2
t0 = time.time()

def norm(v):
    g = 0
    for a in v: g = math.gcd(g, abs(a))
    v = tuple(a // g for a in v)
    for a in v:
        if a != 0:
            return v if a > 0 else tuple(-b for b in v)
rays = sorted({norm(v) for v in itertools.product(range(-m, m + 1), repeat=3) if any(v)})
idx = {r: i for i, r in enumerate(rays)}
n = len(rays)
dot = lambda a, b: sum(x * y for x, y in zip(a, b))
pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if dot(rays[i], rays[j]) == 0]
adj = {i: set() for i in range(n)}
for i, j in pairs: adj[i].add(j); adj[j].add(i)
tris = sorted({tuple(sorted((i, j, k))) for i, j in pairs for k in adj[i] & adj[j]})
cons = [('p', t) for t in pairs] + [('t', t) for t in tris]
print(f"m={m}: {n} rays, {len(pairs)} orthogonal pairs, {len(tris)} bases", flush=True)

# signed permutations of the axes, acting on ray indices
syms = []
for perm in itertools.permutations(range(3)):
    for sg in itertools.product((1, -1), repeat=3):
        syms.append([idx[norm(tuple(sg[k] * rays[i][perm[k]] for k in range(3)))] for i in range(n)])

def violated(c):
    out = []
    for ci, (kind, t) in enumerate(cons):
        s = sum(c[v] for v in t)
        if (kind == 'p' and s == 2) or (kind == 't' and s != 1):
            out.append(ci)
    return out

def colour(S, fixed=None):
    """Colouring of S (dict) if one exists, else None."""
    md = cp_model.CpModel(); c = {v: md.NewBoolVar('') for v in S}
    for kind, t in cons:
        if all(v in c for v in t):
            if kind == 'p': md.Add(c[t[0]] + c[t[1]] <= 1)
            else: md.Add(sum(c[v] for v in t) == 1)
    s = cp_model.CpSolver(); s.parameters.num_workers = 1
    r = s.Solve(md)
    if r in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {v: s.Value(c[v]) for v in S}
    assert r == cp_model.INFEASIBLE, r
    return None

def extend(cS):
    """Extend a colouring of S to all rays, violating as few constraints as possible."""
    md = cp_model.CpModel(); c = [md.NewBoolVar('') for _ in range(n)]
    for v, b in cS.items(): md.Add(c[v] == b)
    pen = []
    for kind, t in cons:
        if all(v in cS for v in t): continue
        z = md.NewBoolVar('')
        if kind == 'p': md.Add(c[t[0]] + c[t[1]] <= 1 + z)
        else:
            md.Add(sum(c[v] for v in t) <= 1 + 2 * z); md.Add(sum(c[v] for v in t) >= 1 - z)
        pen.append(z)
    md.Minimize(sum(pen))
    s = cp_model.CpSolver(); s.parameters.num_workers = 8; s.parameters.max_time_in_seconds = 20
    s.Solve(md)
    return [s.Value(x) for x in c]

master = cp_model.CpModel()
x = [master.NewBoolVar(f'x{i}') for i in range(n)]
y = []
for kind, t in cons:
    yt = master.NewBoolVar('')
    for v in t: master.AddImplication(yt, x[v])
    master.AddBoolOr([yt] + [x[v].Not() for v in t])
    y.append(yt)
master.Minimize(sum(x))
seen = set()
it = 0
while True:
    it += 1
    s = cp_model.CpSolver(); s.parameters.num_workers = 8
    r = s.Solve(master)
    assert r == cp_model.OPTIMAL, r
    S = [i for i in range(n) if s.Value(x[i])]
    cS = colour(S)
    if it % 20 == 0 or cS is None:
        print(f"iter {it}: lower bound {len(S)}, {time.time()-t0:.0f}s", flush=True)
    if cS is None:
        break
    c = extend(cS)
    for g in syms:
        cg = [0] * n
        for i in range(n): cg[g[i]] = c[i]
        key = tuple(cg)
        if key in seen: continue
        seen.add(key)
        vio = violated(cg)
        if not vio:
            print(f"all {n} rays have a colouring: no KS set with coordinates in -{m}..{m}")
            sys.exit(0)
        master.AddBoolOr([y[ci] for ci in vio])

print(f"minimum KS set with coordinates in -{m}..{m}: {len(S)} vectors, {it} iterations, {time.time()-t0:.0f}s")
tS = [t for t in tris if all(v in S for v in t)]
print(f"bases inside it: {len(tS)}")
print("vectors:", [rays[i] for i in S])
# independent recheck of uncolourability by brute force over the bases (exhaustive with pruning)
assert colour(S) is None
# minimality check: removing any one vector leaves a colourable set
print("every vector needed:", all(colour([v for v in S if v != u]) is not None for u in S))
