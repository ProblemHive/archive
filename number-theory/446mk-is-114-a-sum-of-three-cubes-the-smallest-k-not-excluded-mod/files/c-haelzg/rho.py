"""Heath-Brown density rho_sol(k) = sigma_inf/6 * prod_p sigma_p, computed two ways for the local factors:
 (a) by counting solutions of x^3+y^3+z^3 = k modulo p^e (small p; this is the definition of sigma_p);
 (b) by the closed formulas of Booker-Sutherland (arXiv:2007.01209, section 2.1), for all primes up to X.
Only (a) is used to check (b) for p <= 60, and for p = 2, 3. Then the product is truncated at X.
usage: python3 rho.py X k1 k2 ...
"""
import sys, math
from math import gamma, isqrt

def primes_upto(n):
    s = bytearray([1]) * (n + 1); s[0:2] = b"\x00\x00"
    for i in range(2, isqrt(n) + 1):
        if s[i]: s[i*i::i] = bytearray(len(s[i*i::i]))
    return [i for i in range(n + 1) if s[i]]

def sigma_count(p, k, e):
    """#{(x,y,z) mod p^e : x^3+y^3+z^3 = k mod p^e} / p^(2e)"""
    q = p ** e
    hist = {}
    for x in range(q):
        c = pow(x, 3, q); hist[c] = hist.get(c, 0) + 1
    h2 = {}
    items = list(hist.items())
    for a, ca in items:
        for b, cb in items:
            s = (a + b) % q; h2[s] = h2.get(s, 0) + ca * cb
    tot = 0
    for a, ca in items:
        tot += ca * h2.get((k - a) % q, 0)
    return tot / q ** 2

def a_p(p):
    """the integer a with a = 1 mod 3 and 4p = a^2 + 27 b^2 (p = 1 mod 3), else 0"""
    if p % 3 != 1: return 0
    b = 1
    while 27 * b * b <= 4 * p:
        r = 4 * p - 27 * b * b; a = isqrt(r)
        if a * a == r:
            return a if a % 3 == 1 else -a
        b += 1
    raise ValueError(p)

def c_p(p, k):
    if p % 3 != 1 or k % p == 0: return 0
    return 2 if pow(k, (p - 1) // 3, p) == 1 else -1

def sigma_formula(p, k):
    ap = a_p(p)
    if k % p != 0:
        return 1 + 3 * c_p(p, k) / p - ap / p ** 2
    return sigma_count(p, k, 3)   # p | k: counting mod p^3 (the formula I read from the PDF text did not match counting)

def sigma_inf():
    # 4 * int_1^inf (t^3+1)^(-2/3) dt = (2/3) Gamma(1/3)^2 / Gamma(2/3)   (closed form quoted in the paper)
    closed = (2.0 / 3.0) * gamma(1 / 3) ** 2 / gamma(2 / 3)
    # numeric check: substitute t = 1/u, dt = du/u^2: int_0^1 (1+u^3)^(-2/3) du, composite Simpson
    n = 200000; h = 1.0 / n
    f = lambda u: (1 + u ** 3) ** (-2 / 3)
    s = f(0) + f(1) + sum((4 if i % 2 else 2) * f(i * h) for i in range(1, n))
    return closed, 4 * s * h / 3

if __name__ == "__main__":
    X = int(sys.argv[1]); ks = [int(a) for a in sys.argv[2:]]
    ci, ni = sigma_inf()
    print("sigma_inf closed form %.10f  numeric integral %.10f" % (ci, ni))
    # check (b) against (a)
    bad = 0
    for p in primes_upto(60):
        if p in (2, 3): continue
        for k in ks + [1, 2, 5, 7]:
            e = 1 if k % p else 2
            if k % p == 0: e = 2
            if k % p == 0: continue   # p | k is taken from counting itself
            a = sigma_count(p, k, e); b = sigma_formula(p, k)
            if abs(a - b) > 1e-12: bad += 1; print("MISMATCH p=%d k=%d count=%.8f formula=%.8f (e=%d)" % (p, k, a, b, e))
    print("formula vs counting, p<=60 (p!=2,3): mismatches =", bad)
    print('stability of sigma_5 for k=975 (25 | k), e=2,3,4:', [round(sigma_count(5, 975, e), 6) for e in (2, 3, 4)])
    print('stability of sigma_19 for k=114, e=2,3:', [round(sigma_count(19, 114, e), 6) for e in (2, 3)])
    for k in ks:
        # sigma_2 and sigma_3 by counting at increasing e to see stabilisation
        s2 = [sigma_count(2, k, e) for e in (3, 4, 5, 6)]
        s3 = [sigma_count(3, k, e) for e in (2, 3, 4)]
        print("k=%d sigma_2 (e=3..6): %s  sigma_3 (e=2..4): %s" % (k, ["%.6f" % v for v in s2], ["%.6f" % v for v in s3]))
    ps = [p for p in primes_upto(X) if p > 3]
    for k in ks:
        s2 = sigma_count(2, k, 6); s3 = sigma_count(3, k, 4)
        prod = s2 * s3
        marks = {}
        for p in ps:
            prod *= sigma_formula(p, k)
            if p in (1000, 10000, 100000, 1000000): marks[p] = ci / 6 * prod
        print("k=%d rho_sol truncated at X: %s  final(X=%d) %.6f  e(1e15)=%.4f" % (k, {a: round(b, 6) for a, b in marks.items()}, ps[-1], ci / 6 * prod, ci / 6 * prod * math.log(1e15)))
