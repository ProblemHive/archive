import numpy as np, random, sys
# Three-layer construction in F_3^7 = F_3^6 x F_3: A0 x {0}, A1 x {1}, A2 x {2} is a cap iff each layer is a cap
# and no x in A0, y in A1, z in A2 has x + y + z = 0.  Take A0 = a 112-cap C found by local search, A1 = g(C) for a
# random affine map g of F_3^6; the points available for A2 are those z with z != -(x+y) for all x in A0, y in A1.
n = 6
C = [int(l) for l in open('cap112.txt')]
def dig(x):
    return np.array([(x // 3 ** i) % 3 for i in range(n)])
D = np.array([dig(x) for x in range(3 ** n)])           # 729 x 6
pw = 3 ** np.arange(n)
Cv = D[C]                                               # 112 x 6
# check C is a cap
S = set(C)
bad = 0
for i in range(len(C)):
    for j in range(i + 1, len(C)):
        z = (-(Cv[i] + Cv[j])) % 3
        if int(z @ pw) in S:
            bad += 1
print('cap check, collinear triples found:', bad, 'size', len(C))

def rand_inv():
    while True:
        M = np.random.randint(0, 3, (n, n))
        # determinant mod 3 via rank over GF(3)
        A = M.copy() % 3
        r = 0
        for c in range(n):
            p = None
            for i in range(r, n):
                if A[i, c] % 3:
                    p = i; break
            if p is None: continue
            A[[r, p]] = A[[p, r]]
            inv = 1 if A[r, c] == 1 else 2
            A[r] = (A[r] * inv) % 3
            for i in range(n):
                if i != r and A[i, c]:
                    A[i] = (A[i] - A[i, c] * A[r]) % 3
            r += 1
        if r == n: return M

np.random.seed(1)
best = []
trials = int(sys.argv[1])
for t in range(trials):
    M = rand_inv(); b = np.random.randint(0, 3, n)
    A1 = (Cv @ M.T + b) % 3
    sums = (Cv[:, None, :] + A1[None, :, :]) % 3        # 112 x 112 x 6
    forb = set((((-sums) % 3).reshape(-1, n) @ pw).tolist())
    avail = 3 ** n - len(forb)
    best.append(avail)
best = np.array(best)
print('trials', trials, 'available points for the third layer: max', best.max(), 'mean', round(best.mean(), 2), 'min', best.min())
print('histogram of availability:', dict(zip(*np.unique(best, return_counts=True))))

