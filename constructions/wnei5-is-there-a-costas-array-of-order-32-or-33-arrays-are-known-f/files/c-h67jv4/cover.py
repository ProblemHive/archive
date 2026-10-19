"""Orders n <= NMAX for which a Costas array is produced by the Welch or Lempel-Golomb
construction followed by adding/removing corner dots. Every array is checked directly."""
import sys, itertools
from math import gcd

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 60

def is_costas(p):
    n = len(p)
    for d in range(1, n):
        seen = set()
        for i in range(n - d):
            v = p[i + d] - p[i]
            if v in seen:
                return False
            seen.add(v)
    return True

def is_prime(n):
    return n > 1 and all(n % k for k in range(2, int(n ** 0.5) + 1))

def prime_powers(limit):
    out = []
    for q in range(3, limit + 1):
        p = next(r for r in range(2, q + 1) if q % r == 0)   # smallest prime factor
        k, x = 0, q
        while x % p == 0:
            x //= p; k += 1
        if x == 1:
            out.append((q, p, k))
    return out

def poly_mulmod(a, b, mod, p):
    k = len(mod) - 1
    res = [0] * (2 * k - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            res[i + j] = (res[i + j] + x * y) % p
    for d in range(len(res) - 1, k - 1, -1):
        c = res[d]
        if c:
            for t in range(k + 1):
                res[d - k + t] = (res[d - k + t] - c * mod[t]) % p
    return tuple(res[:k])

def build_field(q, p, k):
    """pw[i] = g^i (i < q-1) for a fixed primitive element g, as coordinate tuples over GF(p)."""
    if k == 1:
        def add(u, v): return ((u[0] + v[0]) % p,)
        for g in range(2, q):
            x, pw = 1, []
            for _ in range(q - 1):
                pw.append((x,)); x = x * g % q
            if len(set(pw)) == q - 1:
                return pw, add, (1,)
    for coeffs in itertools.product(range(p), repeat=k):
        mod = list(coeffs) + [1]
        if mod[0] == 0:
            continue
        g = tuple([0, 1] + [0] * (k - 2))
        x = tuple([1] + [0] * (k - 1)); pw = []
        for _ in range(q - 1):
            pw.append(x); x = poly_mulmod(x, g, mod, p)
        if len(set(pw)) == q - 1 and x == tuple([1] + [0] * (k - 1)):
            def add(u, v): return tuple((a + b) % p for a, b in zip(u, v))
            return pw, add, tuple([1] + [0] * (k - 1))
    raise RuntimeError("no primitive polynomial found")

found = {}   # n -> (source, perm)
seen_arrays = set()

def explore(src, t, depth=3):
    """t: 0-indexed permutation that is Costas. Add or remove corner dots, up to `depth` steps."""
    t = tuple(t)
    if (t, depth) in seen_arrays:
        return
    seen_arrays.add((t, depth))
    n = len(t)
    if n <= NMAX and n not in found:
        found[n] = (src, t)
    if depth == 0:
        return
    if n > 1:
        if t[0] in (0, n - 1):
            r = t[0]
            explore(src + "-c", [v - (1 if v > r else 0) for v in t[1:]], depth - 1)
        if t[-1] in (0, n - 1):
            r = t[-1]
            explore(src + "-c", [v - (1 if v > r else 0) for v in t[:-1]], depth - 1)
    if n + 1 <= NMAX:
        for c in ([0] + [v + 1 for v in t], [n] + list(t), [v + 1 for v in t] + [0], list(t) + [n]):
            if is_costas(c):
                explore(src + "+c", c, depth - 1)

# Welch: perm[i] = g^(i+c) mod p - 1, i = 0..p-2, order p-1
for p in range(3, NMAX + 3):
    if not is_prime(p):
        continue
    for g in range(2, p):
        x, pw = 1, []
        for _ in range(p - 1):
            pw.append(x); x = x * g % p
        if len(set(pw)) != p - 1:
            continue
        for c in range(p - 1):
            perm = [pw[(i + c) % (p - 1)] - 1 for i in range(p - 1)]
            assert is_costas(perm)
            explore("Welch p=%d" % p, perm)

# Lempel-Golomb: dot (i,j), 1<=i,j<=q-2 with a^i + b^j = 1; order q-2
for q, p, k in prime_powers(NMAX + 4):
    pw, add, one = build_field(q, p, k)
    idx = {e: i for i, e in enumerate(pw)}
    units = [e for e in range(1, q - 1) if gcd(e, q - 1) == 1]
    for ea in units:
        for eb in units:
            perm = [None] * (q - 2)
            for i in range(1, q - 1):
                ai = pw[(ea * i) % (q - 1)]
                tgt = add(one, tuple((-a) % p for a in ai))   # 1 - alpha^i = beta^j
                lg = idx[tgt]
                j = next(j for j in range(1, q - 1) if (eb * j) % (q - 1) == lg)
                perm[i - 1] = j - 1
            assert sorted(perm) == list(range(q - 2)) and is_costas(perm), (q, ea, eb)
            explore("Golomb q=%d" % q, perm)

print("orders 1..%d with a Costas array from Welch / Lempel-Golomb, plus or minus corner dots (depth 3):" % NMAX)
print("covered:", [n for n in range(1, NMAX + 1) if n in found])
print("NOT covered:", [n for n in range(1, NMAX + 1) if n not in found])

