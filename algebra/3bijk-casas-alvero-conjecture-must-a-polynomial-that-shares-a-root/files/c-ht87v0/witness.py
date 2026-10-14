# Proposition 3.3 of arXiv:2501.09272v2 for n = 3 over GF(p): explicit data.
# R_3 = GF(p)[x1,x2,x3];  F(i,j) = e_(4-i)(z), z = images of x1,x2,x3 under Phi_j (Section 2 of the paper).
# For every index tuple j in {1..4}^3 with a common zero a != 0 in GF(p)^3 of F(1,j1),F(2,j2),F(3,j3):
#   - global mu: F2 not a multiple of F3, and F1 not in (F2,F3)   (generators of degrees 3,2,1)
#   - the quartic X(X-a1)(X-a2)(X-a3) and a direct check that it shares a root with each Hasse derivative
#   - rank of the Jacobian matrix of (F1,F2,F3) at a: rank 2 means the three forms cut out the line
#     through a with multiplicity one, so the ideal needs only 2 generators locally at that line.
# usage: python witness.py p
import sys, itertools
from math import comb
from sympy import symbols, Poly, groebner, expand, diff, Matrix
from sympy.polys.polyfuncs import symmetric_poly

p = int(sys.argv[1])
X = symbols('x1 x2 x3')

def F(i, j):
    z = list(X) if j == 4 else [(-X[l] if l == j - 1 else X[l] - X[j - 1]) for l in range(3)]
    return expand(symmetric_poly(4 - i, *z))

def hasse(c, i):          # c[k] = coefficient of X^k ; i-th Hasse derivative
    return [comb(k, i) * c[k] % p for k in range(i, len(c))]

def ev(c, a):
    return sum(ck * pow(a, k, p) for k, ck in enumerate(c)) % p

def polymul(c, d):
    r = [0] * (len(c) + len(d) - 1)
    for i, ci in enumerate(c):
        for k, dk in enumerate(d):
            r[i + k] = (r[i + k] + ci * dk) % p
    return r

count = 0
for j in itertools.product(range(1, 5), repeat=3):
    Fs = [F(i, j[i - 1]) for i in (1, 2, 3)]
    sols = [a for a in itertools.product(range(p), repeat=3) if any(a)
            and all(Poly(f, *X, modulus=p).eval(a) % p == 0 for f in Fs)]
    if not sols:
        continue
    G23 = groebner(Fs[1:], *X, modulus=p, order='grevlex')
    G3 = groebner(Fs[2:], *X, modulus=p, order='grevlex')
    mu3 = (not G23.contains(Fs[0])) and (not G3.contains(Fs[1]))
    a = min(sols)
    roots = [0, a[0], a[1], a[2]]
    c = [1]
    for r in roots:
        c = polymul(c, [(-r) % p, 1])
    shared = [[r for r in sorted(set(roots)) if ev(hasse(c, i), r) == 0] for i in (1, 2, 3)]
    J = Matrix([[diff(f, v).subs(dict(zip(X, a))) % p for v in X] for f in Fs])
    # rank over GF(p) by hand (3x3): rank 2 iff some 2x2 minor is nonzero mod p and det = 0 mod p
    Jm = [[int(J[r_, c_]) % p for c_ in range(3)] for r_ in range(3)]
    det = (Jm[0][0]*(Jm[1][1]*Jm[2][2]-Jm[1][2]*Jm[2][1]) - Jm[0][1]*(Jm[1][0]*Jm[2][2]-Jm[1][2]*Jm[2][0])
           + Jm[0][2]*(Jm[1][0]*Jm[2][1]-Jm[1][1]*Jm[2][0])) % p
    minors = [(Jm[r1][c1]*Jm[r2][c2]-Jm[r1][c2]*Jm[r2][c1]) % p
              for r1, r2 in ((0, 1), (0, 2), (1, 2)) for c1, c2 in ((0, 1), (0, 2), (1, 2))]
    rk = 3 if det else (2 if any(minors) else (1 if any(any(row) for row in Jm) else 0))
    count += 1
    if count <= 6:
        print('j =', j, ' mu(I_3(j)) = 3:', mu3, ' zero a =', a,
              ' quartic coefficients (X^0..X^4) mod', p, '=', c,
              ' roots shared with Hasse derivatives 1,2,3:', shared, ' Jacobian rank at a:', rk)
print('p =', p, ': index tuples with a nonzero common zero over GF(p):', count)
