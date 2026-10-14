# A family of Casas-Alvero polynomials in characteristic p with two free parameters:
#     f = x^(p^2) * (x + s)^p * (x + b),   degree p^2 + p + 1.
# Part 1: for p = 2, 3, 5 check directly that every Hasse derivative H_i f, 1 <= i <= deg f - 1, is either the zero
#         polynomial or vanishes identically (in b, s) at one of the roots 0, -s, -b of f.
# Part 2 (p = 2, degree 7): in the notation of arXiv:2402.18717v3 (n = 7) and arXiv:2501.09272v2 (n = 6 variables),
#         F(i, j) = Phi_j(e_(7-i)(x1..x6)). Check that the six forms F(1,7), F(2,7), F(3,7), F(4,4), F(5,5), F(6,4)
#         vanish mod 2 on the whole plane (0, 0, 0, b, s, s), and write a Singular file that computes the dimension
#         of their zero set, with and without the deformation parameter T of Proposition 5.3 of 2402.18717v3:
#         Phi[T]_j : x_l -> x_l - T x_j (l != j), x_j -> (1 - 2T) x_j;  Phi[T]_7 = identity;  T = 1 gives Phi_j.
# usage: python family.py
from math import comb
from sympy import symbols, expand, Poly
from sympy.polys.polyfuncs import symmetric_poly

x, b, s, T = symbols('x b s T')

def hasse(f, i, p):
    P = Poly(f, x)
    out = 0
    for (k,), c in P.terms():
        if k >= i:
            out += (comb(k, i) % p) * c * x**(k - i)
    return expand(out)

def is_zero_mod(e, p, gens):
    e = expand(e)
    if e == 0:
        return True
    return all(c % p == 0 for c in Poly(e, *gens).coeffs())

print('PART 1')
for p in (2, 3, 5):
    f = expand(x**(p*p) * (x + s)**p * (x + b))
    d = p*p + p + 1
    report = []
    ok = True
    for i in range(1, d):
        h = hasse(f, i, p)
        if is_zero_mod(h, p, (x, b, s)):
            report.append((i, 'zero polynomial'))
            continue
        at = [name for name, r in (('0', 0), ('-s', -s), ('-b', -b)) if is_zero_mod(h.subs(x, r), p, (b, s))]
        if not at:
            ok = False
        report.append((i, 'vanishes at ' + ','.join(at) if at else 'NO SHARED ROOT'))
    nz = [(i, r) for i, r in report if r != 'zero polynomial']
    print('p = %d, degree %d: all %d Hasse derivatives share a root with f (or are zero): %s' % (p, d, d - 1, ok))
    print('   nonzero ones:', nz)

print('PART 2')
m = 6
X = symbols('x1:7')
def Phi(j, t):
    if j == m + 1:
        return list(X)
    return [((1 - 2*t) * X[l] if l == j - 1 else X[l] - t * X[j - 1]) for l in range(m)]
def F(i, j, t=1):
    return expand(symmetric_poly(m + 1 - i, *Phi(j, t)))
tup = (7, 7, 7, 4, 5, 4)
pt = dict(zip(X, (0, 0, 0, b, s, s)))
for i, j in enumerate(tup, start=1):
    val = expand(F(i, j).subs(pt))
    print('F(%d,%d) on the plane (0,0,0,b,s,s) is zero mod 2: %s' % (i, j, is_zero_mod(val, 2, (b, s))))

def sing(e):
    return str(e).replace('**', '^')
for p in (2, 3, 0):
    lines = ['ring r = %d,(x1,x2,x3,x4,x5,x6,T),dp;' % p]
    gens = [sing(F(i, j, T)) for i, j in enumerate(tup, start=1)]
    lines.append('ideal I = ' + ',\n  '.join(gens) + ';')
    lines.append('ideal G = std(I);')
    lines.append('print("characteristic %d, tuple (7,7,7,4,5,4)");' % p)
    lines.append('print("dimension of V(H_1..H_6) in the 7 variables x1..x6,T (a regular sequence needs 1):"); dim(G);')
    lines.append('ideal G1 = std(I + ideal(T-1));')
    lines.append('print("dimension of the fibre T = 1 in x1..x6 (Theorem 5.6 says at most 1):"); dim(G1);')
    lines.append('ideal G0 = std(I + ideal(T));')
    lines.append('print("dimension of the fibre T = 0 (elementary symmetric polynomials; expect 0):"); dim(G0);')
    if p == 2:
        lines.append('LIB "primdec.lib";')
        lines.append('print("minimal primes of the fibre T = 1:"); minAssGTZ(I + ideal(T-1));')
    lines.append('quit;')
    open('3bijk/tuple_p%d.sing' % p, 'w').write('\n'.join(lines) + '\n')
print('wrote 3bijk/tuple_p2.sing, tuple_p3.sing, tuple_p0.sing')
