# 3x3 magic square of nine squares: centre c, entries c+-a, c+-b, c+-(a+b), c+-(a-b), all squares, row sum 3c.
# Work modulo q (a multiple of p^2). Count residue solutions (c, a, b) mod q with all nine entries squares mod q.
# An entry that is a square and divisible by p is divisible by p^2, so "divisible by p" is tested as == 0 mod p^2.
#   primitive at p: NOT all nine entries == 0 mod p^2.
# Report whether, under that, some entry (or the centre) can be == 0 mod p^2.
# A residue solution that exists does NOT mean a true solution exists; the absence of any residue solution
# with the property proves the congruence condition. Exact integer counting.
import numpy as np, sys

def run(p, q):
    p2 = p * p
    sq = np.zeros(q, dtype=bool)
    for t in range(q): sq[(t*t) % q] = True
    A, B = np.meshgrid(np.arange(q), np.arange(q), indexing="ij")
    ent_off = [A, -A, B, -B, A+B, -(A+B), A-B, -(A-B)]
    n_all = n_prim = n_some0 = n_centre0 = 0
    ex = None
    for c in range(q):
        if not sq[c]: continue
        ok = np.ones((q, q), dtype=bool)
        for off in ent_off:
            ok &= sq[(c + off) % q]
        n_all += int(ok.sum())
        zero_flags = [((c + off) % p2 == 0) for off in ent_off]
        allzero = np.full((q, q), c % p2 == 0)
        for z in zero_flags: allzero = allzero & z
        prim = ok & ~allzero
        n_prim += int(prim.sum())
        some0 = np.full((q, q), c % p2 == 0)
        for z in zero_flags: some0 = some0 | z
        s = prim & some0
        n_some0 += int(s.sum())
        if c % p2 == 0: n_centre0 += int(prim.sum())
        if ex is None and s.any():
            i, j = np.argwhere(s)[0]; ex = (c, int(i), int(j))
    return n_all, n_prim, n_some0, n_centre0, ex

for p, q in [(2, 64), (3, 81), (5, 25), (7, 49), (11, 121), (13, 169), (17, 289), (19, 361), (23, 529)]:
    na, npr, ns, nc, ex = run(p, q)
    print(f"p={p:2d} mod {q:3d}: residue solutions {na}, primitive at p {npr}, "
          f"with some entry divisible by p {ns}, with centre divisible by p {nc}, example (c,a,b)={ex}")
    sys.stdout.flush()
