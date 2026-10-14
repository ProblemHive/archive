# Complement to msq.py: the one case its corner scan cannot see.
# Square centre e = c^2, the two non-square entries are opposite corners e+a and e-a,
# and the other six outer entries are squares: e+-b, e+-(a+b), e+-(a-b).
# Let D = {d > 0 : e-d and e+d are both squares}. Needed: b, |a+b|, |a-b| in D with a != 0,
# Taking a, b > 0 (allowed by symmetry) and d2 = b, d1 = a+b, d3 = |a-b|:
# d1 - d3 = 2*d2 (if a > b) or d1 + d3 = 2*d2 (if a < b), with d1 > d3.
import sys
from math import isqrt
import numpy as np

N = int(sys.argv[1])
hits = []; maxD = 0; total = 0
for c in range(2, N + 1):
    e = c * c
    x = np.arange(1, c, dtype=np.int64)
    z2 = 2 * e - x * x
    z = np.sqrt(z2.astype(np.float64)).astype(np.int64)
    z += (z + 1) * (z + 1) == z2
    Dl = sorted(int(e - v * v) for v in x[z * z == z2])
    D = set(Dl); maxD = max(maxD, len(D)); total += len(D)
    for d2 in Dl:                      # d2 = b
        for d1 in Dl:                  # d1 = |a+b|, d3 = |a-b|
            for d3 in (d1 - 2 * d2, 2 * d2 - d1):
                if d3 in D and d1 > d3:
                    hits.append((c, d2, d1, d3))
print(f"c = 2..{N}: progressions of three squares with middle c^2: {total} in all, at most {maxD} for one c")
print(f"squares with centre c^2, six square outer entries and two opposite corners free: {len(hits)}")
for h in hits[:10]:
    print(h)
