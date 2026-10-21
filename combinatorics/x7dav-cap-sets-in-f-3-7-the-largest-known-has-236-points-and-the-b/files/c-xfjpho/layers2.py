import numpy as np
# Same construction as layers.py, but A1 = C + t (a translate) and A1 = -C + t, for all 729 translations t.
n = 6
C = [int(l) for l in open('cap112.txt')]
D = np.array([[(x // 3 ** i) % 3 for i in range(n)] for x in range(3 ** n)])
pw = 3 ** np.arange(n)
Cv = D[C]
def avail(A0, A1):
    sums = (A0[:, None, :] + A1[None, :, :]) % 3
    forb = set((((-sums) % 3).reshape(-1, n) @ pw).tolist())
    return 3 ** n - len(forb)
res = {}
for name, base in [('C+t', Cv), ('-C+t', (-Cv) % 3)]:
    vals = []
    for t in range(3 ** n):
        vals.append(avail(Cv, (base + D[t]) % 3))
    vals = np.array(vals)
    print(name, 'availability over 729 translations: max', vals.max(), 'values', dict(zip(*[a.tolist() for a in np.unique(vals, return_counts=True)])))
# sizes of sumsets for reference
print('|C+C| (all sums incl. x+x):', len(set((((Cv[:, None, :] + Cv[None, :, :]) % 3).reshape(-1, n) @ pw).tolist())))

