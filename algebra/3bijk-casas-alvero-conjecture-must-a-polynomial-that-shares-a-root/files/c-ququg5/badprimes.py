# Bad primes for the Casas-Alvero conjecture in degree d, by one Groebner basis per prime.
#
# Normal form: a Casas-Alvero polynomial f of degree d over an algebraically closed field of
# characteristic p (p not dividing d) shares a root with H_{d-1}(f) = d*x + a_1. Translate that
# root to 0: then a_1 = 0 and f(0) = 0, so
#     f = x^d + a_2 x^(d-2) + ... + a_(d-1) x.
# f must share a root with the Hasse derivative H_i(f) = sum_k C(k,i) a_k' x^(k-i), i = 1..d-2,
# i.e. Res(f, H_i f) = 0. These are d-2 equations in d-2 unknowns, weighted homogeneous
# (a_j has weight j), so a nonzero solution gives a whole curve of solutions. Hence:
#     p is bad for d  <=>  the ideal (R_1..R_(d-2)) mod p is not zero-dimensional.
# usage: python badprimes.py d pmin pmax nproc
import sys, time
from multiprocessing import Pool
from sympy import symbols, Poly, resultant, binomial, groebner, primerange, GF, ZZ

def system(d):
    x = symbols('x')
    a = symbols('a2:%d' % d)            # a2 .. a_(d-1)
    coeff = {d: 1}
    for j, s in zip(range(2, d), a):
        coeff[d - j] = s                # a_j multiplies x^(d-j)
    f = sum(c * x**k for k, c in coeff.items())
    R = []
    for i in range(1, d - 1):
        h = sum(binomial(k, i) * c * x**(k - i) for k, c in coeff.items() if k >= i)
        R.append(Poly(resultant(f, h, x), *a, domain=ZZ))
    return a, R

def test(args):
    d, p = args
    a, R = SYS
    polys = [r.set_modulus(p) for r in R]
    polys = [q for q in polys if not q.is_zero]
    if len(polys) < len(R):
        return p, True                  # an equation vanishes identically: not zero-dimensional
    G = groebner(polys, *a, modulus=p, order='grevlex')
    return p, not G.is_zero_dimensional

def init(d):
    global SYS
    SYS = system(d)

if __name__ == '__main__':
    d, pmin, pmax, nproc = map(int, sys.argv[1:5])
    t = time.time()
    init(d)
    a, R = SYS
    print('degree', d, 'unknowns', a, 'total degrees of the resultants', [r.total_degree() for r in R],
          'terms', [len(r.terms()) for r in R], flush=True)
    # With a 5th argument 'all', primes dividing d are tested too. The normal form still holds for
    # them: H_(d-1)(f) = d*x + a_1 = a_1 is then a constant, so a_1 = 0 is forced, translations keep
    # a_1 = 0, and one root can be moved to 0.
    incl = len(sys.argv) > 5 and sys.argv[5] == 'all'
    primes = [p for p in primerange(pmin, pmax + 1) if incl or d % p != 0]
    skipped = [p for p in primerange(pmin, pmax + 1) if not (incl or d % p != 0)]
    bad = []
    with Pool(nproc, initializer=init, initargs=(d,)) as pool:
        for p, isbad in pool.imap(test, [(d, p) for p in primes], chunksize=4):
            if isbad:
                bad.append(p)
                print('bad', p, flush=True)
    print('primes tested', len(primes), 'from', pmin, 'to', pmax, '; skipped (divide d):', skipped)
    print('bad primes found:', bad)
    print('seconds', round(time.time() - t, 1))
