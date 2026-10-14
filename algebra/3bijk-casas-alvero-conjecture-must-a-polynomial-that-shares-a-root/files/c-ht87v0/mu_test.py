# Test of one intermediate statement of arXiv:2501.09272v2 (Ghosh), in characteristic p.
#
# Notation of the paper, Section 2: R_m = K[x_1..x_m]; for an index j in 1..m+1 the automorphism
# Phi_j sends x_l -> x_l - x_j (l != j), x_j -> -x_j, and Phi_(m+1) is the identity.
#   F(i, j) = Phi_j( e_(m+1-i)(x_1..x_m) ),  i = 1..m     (degree m+1-i)
# For indices j = (j_1..j_m), I_m(j) = (F(1,j_1), ..., F(m,j_m)).
#   - Proposition 1.4: the conjecture holds in degree m+1 over K iff F(1,j_1)..F(m,j_m) is a regular
#     sequence for every j, i.e. iff the ideal is zero-dimensional for every j.
#   - Theorem 3.6 / Corollary 3.9 need: the minimal number of generators of I_m(j) is m. As the
#     generators have distinct degrees m, m-1, ..., 1, that fails exactly when some
#     F(l, j_l) lies in the ideal (F(i, j_i) : i > l)   (equation (3.9) of the paper).
# For every j this script reports whether the sequence is regular and whether mu(I_m(j)) = m.
# usage: python mu_test.py m p nproc      (p = 0 for the rationals)
import sys, itertools, time
from multiprocessing import Pool
from sympy import symbols, Poly, groebner, QQ, GF
from sympy.polys.polyfuncs import symmetric_poly

def setup(m, p):
    global X, DOM, M, P
    M, P = m, p
    X = symbols('x1:%d' % (m + 1))
    DOM = QQ if p == 0 else GF(p)

def F(i, j):
    m = M
    if j == m + 1:
        z = list(X)
    else:
        z = [(-X[l] if l == j - 1 else X[l] - X[j - 1]) for l in range(m)]
    return Poly(symmetric_poly(m + 1 - i, *z), *X, domain=DOM)

def gb(polys):
    polys = [q for q in polys if not q.is_zero]
    kw = {} if P == 0 else {'modulus': P}
    return groebner([q.as_expr() for q in polys], *X, order='grevlex', **kw)

def test(j):
    m = M
    Fs = [F(i, j[i - 1]) for i in range(1, m + 1)]
    if any(f.is_zero for f in Fs):
        return j, None, 'zero generator'
    regular = gb(Fs).is_zero_dimensional
    dependent = []
    for l in range(1, m):                       # F(m, .) is a nonzero linear form: never dependent
        G = gb(Fs[l:])
        if G.contains(Fs[l - 1].as_expr()):
            dependent.append(l)
    return j, regular, dependent

if __name__ == '__main__':
    m, p, nproc = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    t = time.time()
    setup(m, p)
    tuples = list(itertools.product(range(1, m + 2), repeat=m))
    nonreg, short, both = [], [], []
    with Pool(nproc, initializer=setup, initargs=(m, p)) as pool:
        for j, regular, dep in pool.imap(test, tuples, chunksize=8):
            if regular is None:
                print('zero generator at', j); continue
            if not regular: nonreg.append(j)
            if dep: short.append((j, dep))
            if (not regular) and dep: both.append(j)
    print('m =', m, ' degree d = m+1 =', m + 1, ' characteristic', p, ' index tuples', len(tuples))
    print('tuples whose sequence is NOT regular (a Casas-Alvero polynomial of degree m+1 exists):', len(nonreg))
    print('  ', nonreg[:40], '...' if len(nonreg) > 40 else '')
    print('tuples with mu(I_m(j)) < m (some F(l,j_l) in the ideal of the later ones):', len(short))
    print('  ', short[:40], '...' if len(short) > 40 else '')
    print('tuples that are both:', len(both), both[:40])
    print('seconds', round(time.time() - t, 1))
