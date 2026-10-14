# Bläser's bound, quoted in Landsberg arXiv:1206.1530 (fetched this visit): "the previous lower
# bound, due to Blaser, was 5n^2/2 - 3n"; Wikipedia Machtey Award page (fetched this visit) titles it
# "A 5/2 n^2-Lower Bound for the Rank of n x n Matrix Multiplication over Arbitrary Fields".
import math
for n in [2, 3]:
    v = 5*n*n/2 - 3*n
    print(f"n={n}: 5n^2/2 - 3n = {v}; floor = {math.floor(v)}")

import numpy as np
# Correct flattening of the MM tensor c_ij = sum_k a_ik b_kj, viewed as map U x V -> W:
# rows = output (i,j), cols = A-entry index (k,l) with l==? Build M[(i,j),(k,l)] = delta_{l==j}delta_{k==k}? 
# The tensor is sum e_i^* otimes e_k^* ... simplest: as element of U*xV*xW, flatten along W:
M = np.zeros((9, 9))
for i in range(3):
    for j in range(3):
        for k in range(3):
            M[3*i + j, 3*k + (i if False else j)] += 0
# Direct correct build: term a_{ik} b_{kj}: first factor index (i,k), second (k,j). Flatten along FIRST factor:
F = np.zeros((9, 9))
for i in range(3):
    for j in range(3):
        for k in range(3):
            F[3*i + k, 3*k + j] = 1   # rows=(i,k) cols=(k,j): this is the map V* -> U* x W*
r = np.linalg.matrix_rank(F)
print("rank of flattening (rows=(i,k), cols=(k,j)) over Q:", r, "(0/1 matrix: same rank over any field)")

from fractions import Fraction as Fr
import random
random.seed(7)
def mul5(a, b):
    ev = lambda p, t: p[0] + p[1]*t + p[2]*t*t
    m0, m1, m2, m3, m4 = (ev(a,0)*ev(b,0), ev(a,1)*ev(b,1), ev(a,-1)*ev(b,-1), ev(a,2)*ev(b,2), a[2]*b[2])
    c0, c4 = m0, m4
    c2 = Fr(m1+m2, 2) - c0 - c4
    s = Fr(m1-m2, 2)
    c3 = Fr(Fr(m3-c0-4*c2-16*c4, 2) - s, 3); c1 = s - c3
    return [c0, c1, c2, c3, c4]
def schoolbook(a, b):
    c = [0]*5
    for i in range(3):
        for j in range(3):
            c[i+j] += a[i]*b[j]
    return c
ok = all(mul5(a,b)==schoolbook(a,b) for a,b in (([random.randint(-9,9) for _ in range(3)], [random.randint(-9,9) for _ in range(3)]) for _ in range(1000)))
print("quadratic-product tensor: 5 products over Q correct on 1000 random integer inputs:", ok)
