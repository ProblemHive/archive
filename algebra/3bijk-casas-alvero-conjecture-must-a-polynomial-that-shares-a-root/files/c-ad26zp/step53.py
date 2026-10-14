# Looking inside the proof of Proposition 5.3 of arXiv:2402.18717v3 for n = 7 and the tuple j = (7,7,7,4,5,4).
# Notation of the proof: R = K[x1..x6, T];  H_l = Phi[T]_(j_l)(e_(7-l)(x1..x6));  for a fixed i with j_i != 7,
#   G_l = (1-2T)^(7-l) * phi[T]_(j_i)^(-1)(H_l)   if j_l != j_i,      G_l = h_l = e_(7-l)   if j_l = j_i,
# and F_l is G_l with the powers of T reversed. The proof states: 'either F_l = h_l or deg_T(F_l) = 2(n-l)',
# and then orders the l with F_l != h_l by strictly decreasing T-degree.
# This script prints the actual T-degrees of G_l over the rationals and modulo 2, and writes a Singular file
# for the dimensions of V(H_1..H_k), k = 1..6, in characteristic 2 (a regular sequence needs dimension 7 - k).
from sympy import symbols, expand, Poly, together, cancel, fraction
from sympy.polys.polyfuncs import symmetric_poly

m = 6
X = symbols('x1:7'); T = symbols('T')
tup = (7, 7, 7, 4, 5, 4)

def Phi(j):                       # images of x1..x6 under Phi[T]_j
    if j == m + 1:
        return list(X)
    return [((1 - 2*T) * X[l] if l == j - 1 else X[l] - T * X[j - 1]) for l in range(m)]

def Phi_inv(j):                   # images of x1..x6 under the inverse of Phi[T]_j
    return [(X[l] / (1 - 2*T) if l == j - 1 else X[l] + T / (1 - 2*T) * X[j - 1]) for l in range(m)]

H = [expand(symmetric_poly(m + 1 - l, *Phi(tup[l - 1]))) for l in range(1, m + 1)]

def degT(e, p):
    P = Poly(e, T, *X)
    if p:
        terms = [(mon, c) for mon, c in P.terms() if c % p != 0]
    else:
        terms = P.terms()
    return max(mon[0] for mon, c in terms) if terms else None

for i in (4, 5, 6):
    ji = tup[i - 1]
    sub = dict(zip(X, Phi_inv(ji)))
    print('i = %d, j_i = %d' % (i, ji))
    for l in range(1, i):
        if tup[l - 1] == ji:
            print('   l = %d: j_l = j_i, so G_l = h_l (T-degree 0)' % l)
            continue
        G = cancel(together((1 - 2*T)**(m + 1 - l) * H[l - 1].subs(sub, simultaneous=True)))
        num, den = fraction(G)
        assert den == 1 or den == -1
        G = expand(G)
        print('   l = %d: j_l = %d, the proof says deg_T = 2(n-l) = %d; actual deg_T over Q: %s, modulo 2: %s'
              % (l, tup[l - 1], 2 * (m + 1 - l), degT(G, 0), degT(G, 2)))

lines = ['ring r = 2,(x1,x2,x3,x4,x5,x6,T),dp;', 'ideal I;']
for k in range(1, m + 1):
    lines.append('I = I, ' + str(H[k - 1]).replace('**', '^') + ';')
    lines.append('print("k = %d: dim V(H_1..H_k) =");  dim(std(I));' % k)
lines.append('quit;')
open('3bijk/partial_p2.sing', 'w').write('\n'.join(lines) + '\n')
