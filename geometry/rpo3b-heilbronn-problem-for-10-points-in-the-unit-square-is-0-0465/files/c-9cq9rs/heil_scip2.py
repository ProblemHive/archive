# Heilbronn problem in the unit square, n >= 5 points, with SCIP through pyscipopt.
# Own code. The model follows the published formulation of Sudermann-Merx (arXiv:2603.11107v2, Section 3):
#   points 1..5 on the boundary, counterclockwise: p1 = (0, y1) left, p2 = (x2, 0) bottom, p3 = (1, y3) right,
#   p4 = (x4, 1) top, p5 = (0, y5) left, with y1 <= y5 and x2 <= x4; points 6..n sorted by x.
#   Triangles among points 1..5 are counterclockwise (sign fixed +); triangles (1, 5, k) have sign fixed -.
#   Upper bound t <= tmax (the optimum for n-1 points).
# Differences from the paper: big-M sign constraints instead of the product (2b-1)*A; one added cut
#   (three points in a vertical strip of width w span area <= w/2, so x_(i+2) - x_i >= 2t for the sorted points);
#   an optional lower cutoff t >= tmin; SCIP instead of Gurobi.
# usage: python heil_scip2.py n timelimit_seconds tmin tmax
import sys, time, itertools
from pyscipopt import Model

n = int(sys.argv[1]); tl = float(sys.argv[2]); tmin = float(sys.argv[3]); tmax = float(sys.argv[4])
m = Model("heilbronn%d" % n)
X = {}; Y = {}
fixed_x = {1: 0.0, 3: 1.0, 5: 0.0}; fixed_y = {2: 0.0, 4: 1.0}
for i in range(1, n + 1):
    X[i] = fixed_x[i] if i in fixed_x else m.addVar(lb=0, ub=1, name="x%d" % i)
    Y[i] = fixed_y[i] if i in fixed_y else m.addVar(lb=0, ub=1, name="y%d" % i)
t = m.addVar(lb=tmin, ub=tmax, name="t")
M = 1 + 2 * tmax
nb = 0
for i, j, k in itertools.combinations(range(1, n + 1), 3):
    D = X[i]*Y[j] + X[j]*Y[k] + X[k]*Y[i] - X[i]*Y[k] - X[j]*Y[i] - X[k]*Y[j]      # twice the signed area
    if k <= 5:
        m.addCons(D >= 2 * t)
    elif i == 1 and j == 5:
        m.addCons(-D >= 2 * t)
    else:
        b = m.addVar(vtype="B", name="b_%d_%d_%d" % (i, j, k)); nb += 1
        m.addCons(D >= 2 * t - M * (1 - b))
        m.addCons(-D >= 2 * t - M * b)
m.addCons(Y[1] <= Y[5])
m.addCons(X[2] <= X[4])
for i in range(6, n):
    m.addCons(X[i] <= X[i + 1])
for i in range(6, n - 1):
    m.addCons(X[i + 2] - X[i] >= 2 * t)
m.setObjective(t, "maximize")
m.setParam("limits/time", tl)
m.setParam("display/freq", 50000)
t0 = time.time()
m.optimize()
print("RESULT n=%d binaries=%d status=%s primal=%s dual=%.7f nodes=%d seconds=%.1f tmin=%g tmax=%g" % (
    n, nb, m.getStatus(), ("%.7f" % m.getObjVal()) if m.getNSols() > 0 else "none",
    m.getDualbound(), m.getNNodes(), time.time() - t0, tmin, tmax), flush=True)
if m.getNSols() > 0:
    val = lambda v: v if isinstance(v, float) else m.getVal(v)
    print("points", [(round(val(X[i]), 6), round(val(Y[i]), 6)) for i in range(1, n + 1)])
