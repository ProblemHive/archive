"""Exact diagonalisation of the S=1/2 nearest-neighbour kagome Heisenberg
antiferromagnet, H = J sum_<ij> S_i . S_j with J = 1, on L1 x L2 periodic tori.

Lattice: a1 = (2,0), a2 = (1,sqrt3); sublattices A at 0, B at a1/2, C at a2/2.
Bonds per unit cell R: up triangle A(R)-B(R), A(R)-C(R), B(R)-C(R);
down triangle A(R)-B(R-a1), A(R)-C(R-a2), B(R-a1)-C(R-a2).
Each site has 4 neighbours; N = 3 L1 L2 sites, 2N bonds (checked below).

Usage: python kagome_ed.py L1 L2      prints E0, E0/N, lowest Sz=1 energy and the
                                       triplet gap (even N), using scipy eigsh.
"""
import sys
import itertools
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
from math import comb


def bonds(L1, L2):
    idx = lambda x, y, s: 3 * ((x % L1) * L2 + (y % L2)) + s
    B = []
    for x in range(L1):
        for y in range(L2):
            a, b, c = idx(x, y, 0), idx(x, y, 1), idx(x, y, 2)
            bm, cm = idx(x - 1, y, 1), idx(x, y - 1, 2)
            B += [(a, b), (a, c), (b, c), (a, bm), (a, cm), (bm, cm)]
    B = [tuple(sorted(e)) for e in B]
    assert len(set(B)) == len(B), "duplicate bond: cluster too small"
    N = 3 * L1 * L2
    deg = np.bincount(np.array(B).ravel(), minlength=N)
    assert (deg == 4).all() and len(B) == 2 * N
    return N, B


def sector_states(N, nup):
    # all N-bit integers with nup bits set, sorted
    st = np.fromiter((sum(1 << i for i in c) for c in itertools.combinations(range(N), nup)),
                     dtype=np.int64, count=comb(N, nup))
    st.sort()
    return st


def hamiltonian(N, B, states):
    D = len(states)
    diag = np.zeros(D)
    rows, cols, vals = [], [], []
    ar = np.arange(D)
    for (i, j) in B:
        bi = (states >> i) & 1
        bj = (states >> j) & 1
        same = bi == bj
        diag += np.where(same, 0.25, -0.25)
        flip = ~same
        new = states[flip] ^ ((1 << i) | (1 << j))
        k = np.searchsorted(states, new)
        rows.append(ar[flip]); cols.append(k); vals.append(np.full(k.size, 0.5))
    rows.append(ar); cols.append(ar); vals.append(diag)
    H = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(D, D))
    return H


def lowest(N, B, nup, k=1):
    st = sector_states(N, nup)
    H = hamiltonian(N, B, st)
    w, v = eigsh(H, k=k, which="SA", tol=1e-12)
    o = np.argsort(w)
    return w[o], v[:, o], st, H


if __name__ == "__main__":
    L1, L2 = int(sys.argv[1]), int(sys.argv[2])
    N, B = bonds(L1, L2)
    nup0 = N // 2
    w0, _, st0, _ = lowest(N, B, nup0, k=2)
    print(f"cluster {L1}x{L2} torus: N = {N}, bonds = {len(B)}, sector dim = {len(st0)}")
    print(f"E0 = {w0[0]:.10f}   E0/N = {w0[0] / N:.10f}   (2nd level in Sz={'0' if N % 2 == 0 else '1/2'}: {w0[1]:.10f})")
    w1, _, st1, _ = lowest(N, B, nup0 + 1, k=1)
    print(f"lowest Sz={'1' if N % 2 == 0 else '3/2'} energy = {w1[0]:.10f}   gap to it = {w1[0] - w0[0]:.10f}")
