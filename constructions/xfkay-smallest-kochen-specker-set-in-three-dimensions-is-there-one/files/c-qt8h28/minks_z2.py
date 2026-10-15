# Smallest Kochen-Specker set whose vectors have coordinates a + b*sqrt(2) with (a, b) from a given
# list (3D, real). Same method as minks.py (p/xfkay, c/nubpk4), with exact arithmetic in Q(sqrt 2).
# KS set: no 0/1 colouring with no two orthogonal vectors both 1 and every orthogonal triple
# inside the set having exactly one 1.
# Usage: python minks_z2.py peres   -> coordinates in {0, +-1, +-sqrt2}
#        python minks_z2.py box1    -> coordinates a + b sqrt2 with a, b in {-1, 0, 1}
#        python minks_z2.py box21   -> coordinates a + b sqrt2 with a in -2..2, b in {-1, 0, 1}
import sys, itertools, time
from fractions import Fraction as F
from ortools.sat.python import cp_model

which = sys.argv[1] if len(sys.argv) > 1 else 'peres'
if which == 'peres':
    alphabet = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
elif which == 'box1':
    alphabet = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
elif which == 'box21':  # a in -2..2, b in -1..1: contains both the Peres and the Conway-Kochen alphabets
    alphabet = [(a, b) for a in range(-2, 3) for b in (-1, 0, 1)]
else:
    raise SystemExit('unknown alphabet')
t0 = time.time()

def mul(x, y): return (x[0] * y[0] + 2 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])
def add(x, y): return (x[0] + y[0], x[1] + y[1])
def div(x, y):  # x / y in Q(sqrt 2), y != 0
    c, d = y; nrm = F(c * c - 2 * d * d)
    num = mul(x, (c, -d))
    return (F(num[0]) / nrm, F(num[1]) / nrm)
def key(v):  # canonical representative of the line through v: divide by the first nonzero coordinate
    for a in v:
        if a != (0, 0):
            return tuple(div(b, a) for b in v)
def dot(u, v):
    s = (0, 0)
    for a, b in zip(u, v): s = add(s, mul(a, b))
    return s

lines = {}
for v in itertools.product(alphabet, repeat=3):
    if all(a == (0, 0) for a in v): continue
    lines.setdefault(key(v), v)
keys = sorted(lines)
rays = [lines[k] for k in keys]
idx = {k: i for i, k in enumerate(keys)}
n = len(rays)
pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if dot(rays[i], rays[j]) == (0, 0)]
adj = {i: set() for i in range(n)}
for i, j in pairs: adj[i].add(j); adj[j].add(i)
tris = sorted({tuple(sorted((i, j, k))) for i, j in pairs for k in adj[i] & adj[j]})
cons = [('p', t) for t in pairs] + [('t', t) for t in tris]
print(f"{which}: {n} rays, {len(pairs)} orthogonal pairs, {len(tris)} bases", flush=True)

# symmetries: signed permutations of the axes, and the conjugation sqrt2 -> -sqrt2
syms = []
for conj in (1, -1):
    for perm in itertools.permutations(range(3)):
        for sg in itertools.product((1, -1), repeat=3):
            g = []
            for r in rays:
                w = tuple((sg[k] * r[perm[k]][0], sg[k] * conj * r[perm[k]][1]) for k in range(3))
                g.append(idx[key(w)])
            syms.append(g)

def violated(c):
    out = []
    for ci, (kind, t) in enumerate(cons):
        s = sum(c[v] for v in t)
        if (kind == 'p' and s == 2) or (kind == 't' and s != 1):
            out.append(ci)
    return out

def colour(S):
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
seen = set(); it = 0
while True:
    it += 1
    s = cp_model.CpSolver(); s.parameters.num_workers = 8
    r = s.Solve(master)
    assert r == cp_model.OPTIMAL, r
    S = [i for i in range(n) if s.Value(x[i])]
    cS = colour(S)
    if it % 20 == 0 or cS is None:
        print(f"iter {it}: lower bound {len(S)}, {time.time()-t0:.0f}s", flush=True)
    if cS is None: break
    c = extend(cS)
    for g in syms:
        cg = [0] * n
        for i in range(n): cg[g[i]] = c[i]
        kk = tuple(cg)
        if kk in seen: continue
        seen.add(kk)
        vio = violated(cg)
        if not vio:
            print(f"all {n} rays have a colouring: no KS set in this class"); sys.exit(0)
        master.AddBoolOr([y[ci] for ci in vio])

fmt = lambda a: {(0, 0): '0', (1, 0): '1', (-1, 0): '-1', (0, 1): 'r', (0, -1): '-r'}.get(a, f"{a[0]}{a[1]:+d}r")
print(f"minimum KS set in class {which}: {len(S)} vectors, {it} iterations, {time.time()-t0:.0f}s  (r = sqrt 2)")
print("bases inside it:", sum(1 for t in tris if all(v in S for v in t)))
print("vectors:", ' '.join('(' + ','.join(fmt(a) for a in rays[i]) + ')' for i in S))
assert colour(S) is None
print("every vector needed:", all(colour([v for v in S if v != u]) is not None for u in S))
