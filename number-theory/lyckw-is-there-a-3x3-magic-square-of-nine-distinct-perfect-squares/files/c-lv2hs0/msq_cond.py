# Numerical check of the lemmas behind the necessary conditions for a 3x3 magic square of squares.
# A "line" is a triple of positive integers x < c < z with x^2 + z^2 = 2 c^2
# (three squares in arithmetic progression, middle c^2).
import sys
from math import gcd, isqrt

N = int(sys.argv[1])

def factor(n):
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f

lines = 0; bad = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
count_ok = 0; count_checked = 0; first4 = None
for c in range(1, N + 1):
    fc = factor(c)
    here = 0
    for x in range(1, c):
        z2 = 2 * c * c - x * x
        z = isqrt(z2)
        if z * z != z2:
            continue
        lines += 1; here += 1
        g = gcd(x, gcd(c, z))
        # A: a prime q = 3 mod 4 dividing c divides x and z too
        for q in fc:
            if q % 4 == 3 and (x % q or z % q):
                bad["A"] += 1
        # B: c even => x and z even
        if c % 2 == 0 and (x % 2 or z % 2):
            bad["B"] += 1
        # C: 3 | c => 3 | x and 3 | z
        if c % 3 == 0 and (x % 3 or z % 3):
            bad["C"] += 1
        # D: if c is odd and prime to 3 and to x: x^2 and z^2 are 1 mod 24
        if c % 2 and c % 3 and g == 1 and ((x * x) % 24 != 1 or (z * z) % 24 != 1 or (c * c) % 24 != 1):
            bad["D"] += 1
        # E: an odd prime dividing x or z but not c is +-1 mod 8
        for w in (x, z):
            for q in factor(w):
                if q != 2 and c % q and q % 8 not in (1, 7):
                    bad["E"] += 1
    # F: number of lines with middle c^2 equals (prod(2a+1 over primes 1 mod 4) - 1) / 2
    pred = 1
    for q, a in fc.items():
        if q % 4 == 1:
            pred *= 2 * a + 1
    count_checked += 1
    count_ok += (here == (pred - 1) // 2)
    if here >= 4 and first4 is None:
        first4 = (c, here)
print(f"c = 1..{N}: {lines} lines x^2 + z^2 = 2c^2 with 0 < x < c")
print("violations of A (prime 3 mod 4 in c), B (c even), C (3 | c), D (1 mod 24), E (primes +-1 mod 8):", bad)
print(f"F: line count equals the formula for {count_ok} of {count_checked} values of c")
print("smallest c with at least 4 lines:", first4)
