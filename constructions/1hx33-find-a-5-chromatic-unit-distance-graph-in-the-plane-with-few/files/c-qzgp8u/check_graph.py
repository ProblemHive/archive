# Exact check of a unit-distance graph given as Mathematica-style coordinates.
# usage: python 1hx33/check_graph.py 510
# Reads 1hx33/data/N.vtx and N.edge, checks every pair of points in exact arithmetic in
# Q(sqrt3, sqrt5, sqrt11), compares the unit pairs with the edge file, writes a 4-colouring CNF.
import ast
import sys
from fractions import Fraction
from itertools import combinations

PRIMES = (3, 5, 11)


class K:
    """Element of Q(sqrt3, sqrt5, sqrt11): {d: coefficient of sqrt(d)}, d a divisor of 165."""
    __slots__ = ("c",)

    def __init__(self, c=None):
        self.c = {d: v for d, v in (c or {}).items() if v != 0}

    @staticmethod
    def of(x):
        return x if isinstance(x, K) else K({1: Fraction(x)})

    def __add__(self, o):
        o = K.of(o)
        r = dict(self.c)
        for d, v in o.c.items():
            r[d] = r.get(d, 0) + v
        return K(r)
    __radd__ = __add__

    def __neg__(self):
        return K({d: -v for d, v in self.c.items()})

    def __sub__(self, o):
        return self + (-K.of(o))

    def __rsub__(self, o):
        return K.of(o) - self

    def __mul__(self, o):
        o = K.of(o)
        r = {}
        for d1, v1 in self.c.items():
            for d2, v2 in o.c.items():
                d, f = 1, 1
                for p in PRIMES:
                    e = (d1 % p == 0) + (d2 % p == 0)
                    if e == 1:
                        d *= p
                    elif e == 2:
                        f *= p
                r[d] = r.get(d, 0) + v1 * v2 * f
        return K(r)
    __rmul__ = __mul__

    def __truediv__(self, o):
        num, den = self, K.of(o)
        for p in PRIMES:                      # multiply by conjugates until the divisor is rational
            cj = K({d: (-v if d % p == 0 else v) for d, v in den.c.items()})
            num, den = num * cj, den * cj
        if set(den.c) != {1}:
            raise ZeroDivisionError("division by zero")
        return K({d: v / den.c[1] for d, v in num.c.items()})

    def is_one(self):
        return self.c == {1: Fraction(1)}

    def approx(self):
        return sum(float(v) * d ** 0.5 for d, v in self.c.items())


def sqrt_rational(q):
    """sqrt of a positive rational as rational * sqrt(squarefree divisor of 165)."""
    q = Fraction(q)
    n = q.numerator * q.denominator          # sqrt(a/b) = sqrt(ab)/b
    d = 1
    for p in PRIMES:
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        if e % 2:
            d *= p
        n *= p ** (e - e % 2)
    r = int(round(n ** 0.5))
    if r * r != n:
        raise ValueError(f"sqrt({q}) is outside the field")
    return K({d: Fraction(r, q.denominator)})


def ev(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return K.of(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -ev(node.operand)
    if isinstance(node, ast.BinOp):
        a, b = ev(node.left), ev(node.right)
        if isinstance(node.op, ast.Add):
            return a + b
        if isinstance(node.op, ast.Sub):
            return a - b
        if isinstance(node.op, ast.Mult):
            return a * b
        if isinstance(node.op, ast.Div):
            return a / b
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Sqrt" and len(node.args) == 1:
        a = ev(node.args[0])
        if set(a.c) - {1}:
            raise ValueError("nested square root")
        return sqrt_rational(a.c.get(1, 0))
    raise ValueError("unexpected syntax: " + ast.dump(node)[:80])


def parse_point(line):
    s = line.strip()
    assert s.startswith("{") and s.endswith("}"), s
    s = "(" + s[1:-1].replace("[", "(").replace("]", ")") + ")"
    t = ast.parse(s, mode="eval").body
    assert isinstance(t, ast.Tuple) and len(t.elts) == 2
    return ev(t.elts[0]), ev(t.elts[1])


name = sys.argv[1]
pts = [parse_point(l) for l in open(f"1hx33/data/{name}.vtx") if l.strip()]
n = len(pts)
print("vertices read:", n)
keys = [tuple(sorted((d, v) for d, v in x.c.items())) + ("|",) + tuple(sorted((d, v) for d, v in y.c.items())) for x, y in pts]
print("distinct points:", len(set(keys)))
used = sorted({d for x, y in pts for d in list(x.c) + list(y.c)})
print("square roots occurring in coordinates (as sqrt(d)):", used)

fl = [(x.approx(), y.approx()) for x, y in pts]
unit = set()
near = 0
for i, j in combinations(range(n), 2):
    dx, dy = fl[i][0] - fl[j][0], fl[i][1] - fl[j][1]
    if abs(dx * dx + dy * dy - 1.0) < 1e-6:          # float prefilter, then exact test
        near += 1
        ex, ey = pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]
        if (ex * ex + ey * ey).is_one():
            unit.add((i + 1, j + 1))
print("pairs within 1e-6 of unit distance (float):", near)
print("pairs at distance exactly 1 (exact):", len(unit))
# the prefilter is safe only if no exact unit pair is missed; test all pairs exactly on a sample of rows
miss = 0
for i in range(0, n, 17):
    for j in range(n):
        if i != j:
            ex, ey = pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]
            if (ex * ex + ey * ey).is_one() and (min(i, j) + 1, max(i, j) + 1) not in unit:
                miss += 1
print("exact unit pairs missed by the prefilter on every 17th row:", miss)

edges = set()
header = None
for l in open(f"1hx33/data/{name}.edge"):
    p = l.split()
    if p and p[0] == "p":
        header = (int(p[2]), int(p[3]))
    elif p and p[0] == "e":
        a, b = int(p[1]), int(p[2])
        edges.add((min(a, b), max(a, b)))
print("edge file header (vertices, edges):", header, " distinct edges listed:", len(edges))
print("edges in file that are not unit pairs:", len(edges - unit))
print("unit pairs missing from the edge file:", len(unit - edges))

deg = [0] * (n + 1)
adj = {v: set() for v in range(1, n + 1)}
for a, b in unit:
    deg[a] += 1
    deg[b] += 1
    adj[a].add(b)
    adj[b].add(a)
print("degree min/max/mean:", min(deg[1:]), max(deg[1:]), round(2 * len(unit) / n, 3))
tri = next(((a, b, c) for a, b in sorted(unit) for c in sorted(adj[a] & adj[b]) if c > b), None)
print("first triangle (used to fix three colours):", tri)

K4 = 4
var = lambda v, c: (v - 1) * K4 + c + 1
for tag, fix in (("", False), ("-sym", True)):
    cl = []
    for v in range(1, n + 1):
        cl.append([var(v, c) for c in range(K4)])
    for a, b in sorted(unit):
        for c in range(K4):
            cl.append([-var(a, c), -var(b, c)])
    if fix:
        for k, v in enumerate(tri):
            cl.append([var(v, k)])
    with open(f"1hx33/{name}-4col{tag}.cnf", "w") as f:
        f.write(f"p cnf {n * K4} {len(cl)}\n")
        for c in cl:
            f.write(" ".join(map(str, c)) + " 0\n")
    print(f"wrote 1hx33/{name}-4col{tag}.cnf: {n * K4} variables, {len(cl)} clauses")
with open(f"1hx33/{name}.unit", "w") as f:
    for a, b in sorted(unit):
        f.write(f"{a} {b}\n")
