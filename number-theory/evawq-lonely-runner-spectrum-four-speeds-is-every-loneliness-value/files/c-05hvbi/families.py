# Which quadruples with ML < 1/4 lie on the two subtori of Jain and Kravitz (arXiv:2411.12684, Section 4)?
#   U1: speeds (B, A, 2A, 3A)          U2: speeds (A+B, B, A, A+2B)       up to order and signs.
# usage: python evawq/families.py N      (reads evawq/nearN.txt written by spectrum4.py)
import sys
from fractions import Fraction
from itertools import permutations

N = int(sys.argv[1])
rows = [tuple(map(int, l.split())) for l in open(f"evawq/near{N}.txt")]


def on_u1(v):
    s = set(v)
    return any(2 * a in s and 3 * a in s for a in v)


def on_u2(v):
    target = sorted(v)
    for p, q in permutations(v, 2):
        for b in (p, -p):                         # A = q > 0 without loss; B = +-p
            if sorted((abs(q + b), abs(b), q, abs(q + 2 * b))) == target:
                return True
    return False


stats = {}
for *v, p, q in rows:
    v = tuple(v)
    f = Fraction(p, q)
    k = f.denominator - 4 * f.numerator
    key = ("U1" if on_u1(v) else "") + ("U2" if on_u2(v) else "") or "neither"
    stats.setdefault(key, {}).setdefault(k, []).append((v, f))
print(f"N = {N}: quadruples with ML < 1/4: {len(rows)}")
for key in sorted(stats):
    for k in sorted(stats[key]):
        items = stats[key][k]
        print(f"  on {key:8s} k = {k}: {len(items):5d}   smallest speeds: {[x[0] for x in sorted(items, key=lambda x: max(x[0]))[:4]]}")
spor = sorted((x for k in stats.get("neither", {}) for x in stats["neither"][k]), key=lambda x: max(x[0]))
print("on neither subtorus:", len(spor))
for v, f in spor:
    m = 1 / (Fraction(1, 4) - f) / 4
    print(f"   {v}  ML = {f}  m = {m}")
if spor:
    print("largest speed among them:", max(max(v) for v, _ in spor))
