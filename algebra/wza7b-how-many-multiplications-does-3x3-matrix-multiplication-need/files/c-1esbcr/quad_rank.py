# Toy example: multiplying two quadratics (a0 + a1 x + a2 x^2)(b0 + b1 x + b2 x^2) = c0 + ... + c4 x^4.
# Its rank is 5 over the rationals and 6 over the two-element field.
from fractions import Fraction as Fr
from itertools import product
import random

# 1) Over Q with 5 products: evaluate at 0, 1, -1, 2 and infinity, then interpolate.
def mul5(a, b):
    ev = lambda p, t: p[0] + p[1] * t + p[2] * t * t
    m0, m1, m2, m3, m4 = (ev(a, 0) * ev(b, 0), ev(a, 1) * ev(b, 1), ev(a, -1) * ev(b, -1),
                          ev(a, 2) * ev(b, 2), a[2] * b[2])
    c0, c4 = m0, m4
    c2 = Fr(m1 + m2, 2) - c0 - c4
    s = Fr(m1 - m2, 2)                              # c1 + c3
    c3 = Fr(Fr(m3 - c0 - 4 * c2 - 16 * c4, 2) - s, 3)
    c1 = s - c3
    return [c0, c1, c2, c3, c4]

def schoolbook(a, b):
    c = [0] * 5
    for i in range(3):
        for j in range(3):
            c[i + j] += a[i] * b[j]
    return c

random.seed(1)
ok = all(mul5(a, b) == schoolbook(a, b)
         for a, b in ((([random.randint(-9, 9) for _ in range(3)]), [random.randint(-9, 9) for _ in range(3)])
                      for _ in range(1000)))
print("5 products over Q (divisions by 2 and 3) correct on 1000 random integer inputs:", ok)

# 2) Over F_2: a decomposition with 5 products would need 5 rank-one 3x3 matrices u v^T
#    spanning the 5-dimensional space T of matrices whose (i, j) entry depends only on i + j.
#    So each of the 5 would lie in T. Count the rank-one matrices in T.
vecs = [v for v in product((0, 1), repeat=3) if any(v)]
inT = []
for u in vecs:
    for v in vecs:
        M = [[u[i] * v[j] for j in range(3)] for i in range(3)]
        if M[0][1] == M[1][0] and M[0][2] == M[1][1] == M[2][0] and M[1][2] == M[2][1]:
            inT.append((u, v))
print("rank-one matrices over F_2:", len(vecs) ** 2, "; of these in T:", len(inT), inT)

# 3) Six products that work over any ring (so the rank over F_2 is exactly 6).
def mul6(a, b):
    p0, p1, p2 = a[0] * b[0], a[1] * b[1], a[2] * b[2]
    q01, q12, q02 = (a[0] + a[1]) * (b[0] + b[1]), (a[1] + a[2]) * (b[1] + b[2]), (a[0] + a[2]) * (b[0] + b[2])
    return [p0, q01 - p0 - p1, q02 - p0 - p2 + p1, q12 - p1 - p2, p2]
ok6 = all([x % 2 for x in mul6(a, b)] == [x % 2 for x in schoolbook(a, b)]
          for a in product((0, 1), repeat=3) for b in product((0, 1), repeat=3))
print("6 products, no divisions, correct on all 64 inputs over F_2:", ok6)
