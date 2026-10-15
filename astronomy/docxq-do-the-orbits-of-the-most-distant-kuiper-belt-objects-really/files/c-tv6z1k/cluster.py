# Rayleigh and Kuiper-style tests on the angles of distant TNOs, from MPC's Distant.txt (MPCORB format).
# Unweighted: no selection-bias model. Columns per the MPCORB format description.
import math, sys
from scipy import stats
import numpy as np

F = "/data/docxq/Distant.txt"

def fl(s):
    s = s.strip()
    return float(s) if s else float("nan")

objs = []
for line in open(F, encoding="latin-1"):
    if len(line) < 160 or line[0] == "-" or not line[0:7].strip():
        continue
    try:
        w = fl(line[37:46]); O = fl(line[48:57]); i = fl(line[59:68])
        e = fl(line[70:79]); a = fl(line[92:103])
    except ValueError:
        continue
    U = line[105:106].strip()
    nopp = line[123:126].strip()
    arc = line[127:136].strip()
    name = line[166:194].strip()
    if not (a > 0 and e < 1):
        continue
    objs.append(dict(name=name, a=a, e=e, i=i, w=w, O=O, q=a * (1 - e), U=U, opp=nopp, arc=arc))

print("objects read:", len(objs))

def rayleigh(angles_deg):
    th = np.radians(angles_deg)
    n = len(th)
    C, S = np.cos(th).sum(), np.sin(th).sum()
    R = math.hypot(C, S) / n
    Z = n * R * R
    # Rayleigh p-value with the usual small-n correction (Zar)
    p = math.exp(math.sqrt(1 + 4 * n + 4 * (n * n - n * n * R * R)) - (1 + 2 * n))
    mean = math.degrees(math.atan2(S, C)) % 360
    return n, R, p, mean

def pole_rayleigh(sel):
    # 3-D Rayleigh test on orbit poles (uniform on sphere null): 3 n Rbar^2 ~ chi2(3)
    v = []
    for o in sel:
        i, O = math.radians(o["i"]), math.radians(o["O"])
        v.append((math.sin(i) * math.sin(O), -math.sin(i) * math.cos(O), math.cos(i)))
    v = np.array(v); n = len(v)
    m = v.sum(0) / n
    return None  # poles are concentrated near the ecliptic pole by inclination alone; not a fair null, so not used

def good(o, strict):
    # 'strict': orbit quality code U <= 5 and at least 2 oppositions (drops poorly determined orbits)
    if not strict:
        return True
    try:
        return int(o["U"]) <= 5 and int(o["opp"]) >= 2
    except ValueError:
        return False

print()
print("Unweighted Rayleigh tests (no survey bias model). p is the chance of R this large from uniform angles.")
print("%-6s %-5s %-6s | %3s  %-22s | %-22s" % ("a>", "q>", "orbits", "n", "varpi: R  p  mean", "node: R  p  mean"))
for strict in (False, True):
    for amin in (150, 200, 250):
        for qmin in (30, 37, 42):
            sel = [o for o in objs if o["a"] > amin and o["q"] > qmin and good(o, strict)]
            if len(sel) < 3:
                continue
            vp = [(o["w"] + o["O"]) % 360 for o in sel]
            n, R, p, m = rayleigh(vp)
            n2, R2, p2, m2 = rayleigh([o["O"] for o in sel])
            print("%-6d %-5d %-6s | %3d  %.2f %.4f %5.0f      | %.2f %.4f %5.0f" %
                  (amin, qmin, "U<=5" if strict else "all", n, R, p, m, R2, p2, m2))

if len(sys.argv) > 1:
    amin, qmin = float(sys.argv[1]), float(sys.argv[2])
    sel = sorted([o for o in objs if o["a"] > amin and o["q"] > qmin], key=lambda o: -o["a"])
    print()
    print("Objects with a > %g, q > %g:" % (amin, qmin))
    for o in sel:
        print("%-14s a=%7.1f q=%5.1f i=%5.1f varpi=%5.1f node=%5.1f U=%s opp=%s arc=%s" %
              (o["name"], o["a"], o["q"], o["i"], (o["w"] + o["O"]) % 360, o["O"], o["U"], o["opp"], o["arc"]))
    vp = [(o["w"] + o["O"]) % 360 for o in sel]
    base = rayleigh(vp)
    print()
    print("Leave-one-out on varpi (p with that object removed), largest changes first:")
    rows = []
    for k, o in enumerate(sel):
        rest = vp[:k] + vp[k + 1:]
        rows.append((rayleigh(rest)[2], o["name"]))
    rows.sort(key=lambda r: abs(math.log(r[0]) - math.log(base[2])), reverse=True)
    print("all: n=%d p=%.4f" % (base[0], base[2]))
    for p, nm in rows[:6]:
        print("  without %-14s p=%.4f" % (nm, p))
