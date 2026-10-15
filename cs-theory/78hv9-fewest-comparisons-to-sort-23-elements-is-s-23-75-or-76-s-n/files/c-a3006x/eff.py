# For n = 12..60: C(n) = ceil(log2 n!), F(n) = Ford-Johnson count, and the efficiency
# e(n) = n!/2^C(n) used by Stober and Weiss (arXiv:2206.05597, Table 2) as a predictor of search cost.
# A proof that n elements cannot be sorted in C(n) comparisons gives S(n) >= C(n)+1, which settles
# S(n) = F(n) whenever F(n) = C(n)+1.
from fractions import Fraction
from math import factorial

def clog2(num, den=1):
    c = 0
    while (1 << c) * den < num:
        c += 1
    return c

def C(n):
    return clog2(factorial(n))

def F(n):
    return sum(clog2(3 * k, 4) for k in range(1, n + 1))

print(" n  C(n) F(n) F-C  e(n)=n!/2^C")
rows = []
for n in range(12, 61):
    e = float(Fraction(factorial(n), 2 ** C(n)))
    rows.append((n, C(n), F(n), F(n) - C(n), e))
    print(f"{n:2d}  {C(n):4d} {F(n):4d} {F(n)-C(n):3d}  {e:.4f}")
print()
print("open n <= 60 with F-C = 1 (a proof of 'not sortable in C(n)' settles S(n) = F(n)):")
for r in rows:
    if r[0] >= 23 and r[3] == 1:
        print(f"  n={r[0]}: C={r[1]}, F={r[2]}, e={r[4]:.4f}")
print("open n <= 60 with e(n) >= 0.9 (the regime where n = 19, 22 and 28 were cheap):")
print("  ", [(r[0], round(r[4], 3), r[3]) for r in rows if r[0] >= 23 and r[4] >= 0.9])
