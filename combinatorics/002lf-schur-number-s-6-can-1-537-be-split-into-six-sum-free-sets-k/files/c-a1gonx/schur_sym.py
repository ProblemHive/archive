# schur_sym.py - tabu search for SYMMETRIC sum-free colourings of 1..n with k colours.
# Symmetric: i and n + 1 - i share a colour. With m = n + 1 this is the same as colouring the nonzero
# residues mod m so that no colour holds x, y, z with x + y = z (mod m). When 3 divides m the two
# numbers m/3 and 2m/3 are left free to take different colours (the exception Fredricksen and Sweet
# allow), since m/3 + m/3 = 2m/3.
# Cost = number of ordered triples (x, y, z), x + y = z mod m, in one colour. Cost 0 = valid colouring;
# every reported colouring is re-checked over the integers 1..n. A move recolours one class {i, m - i}.
# A search: failing to reach 0 proves nothing. Needs numpy.
import sys, time
import numpy as np

def classes(m):
    free = {m // 3, 2 * m // 3} if m % 3 == 0 else set()
    cl = []
    for i in range(1, m):
        if i in free: cl.append((i,))
        elif i <= m - i: cl.append((i, m - i) if i != m - i else (i,))
    return cl

def int_violations(col, n):          # col[1..n], direct count over the integers
    return sum(1 for x in range(1, n + 1) for y in range(x, n + 1 - x) if col[x] == col[y] == col[x + y])

def mod_cost(col, m):                # ordered triples mod m, direct count
    return sum(1 for x in range(1, m) for y in range(1, m) if (x + y) % m and col[x] == col[y] == col[(x + y) % m])

class State:
    def __init__(self, m, k, rng):
        self.m, self.k = m, k
        self.cl = classes(m); J = len(self.cl)
        self.p = np.array([c[0] for c in self.cl]); self.q = np.array([c[-1] for c in self.cl])
        self.two = np.array([len(c) == 2 for c in self.cl])
        # ordered pairs (a, b) of members, for the terms with two members of the class in one triple
        A, B, W = [], [], []
        for c in self.cl:
            prs = [(a, b) for a in c for b in c]
            prs += [(c[0], c[0])] * (4 - len(prs))
            A.append([a for a, b in prs]); B.append([b for a, b in prs]); W.append([1] * len(c) ** 2 + [0] * (4 - len(c) ** 2))
        A, B, self.W = np.array(A), np.array(B), np.array(W)
        self.sum_idx, self.dif_idx = (A + B) % m, (B - A) % m
        self.S3 = np.array([sum(1 for a in c for b in c if (a + b) % m in c) for c in self.cl])
        self.ccol = rng.integers(0, k, J)
        self.v = np.zeros((k, m))
        for j in range(J): self.v[self.ccol[j], list(self.cl[j])] = 1
        self.T = np.zeros((k, m)); self.R = np.zeros((k, m))
        for c in range(k): self.refresh(c)
    def refresh(self, c):
        F = np.fft.fft(self.v[c])
        self.T[c] = np.rint(np.fft.ifft(F * F).real)             # T[z] = pairs (x, y) in c with x + y = z
        self.R[c] = np.rint(np.fft.ifft(F * np.conj(F)).real)    # R[p] = y in c with y + p in c
    def tables(self):
        """add[j, c]: triples created if class j joined colour c; own[j]: triples class j is in now"""
        S1 = (2 * self.R[:, self.p] + self.T[:, self.p]) + np.where(self.two, 2 * self.R[:, self.q] + self.T[:, self.q], 0)
        S2 = ((self.v[:, self.sum_idx] + 2 * self.v[:, self.dif_idx]) * self.W).sum(axis=2)
        J = np.arange(len(self.cl))
        own = S1[self.ccol, J] - S2[self.ccol, J] + self.S3
        return (S1 + S2 + self.S3).T, own
    def move(self, j, b):
        a = self.ccol[j]; mem = list(self.cl[j])
        self.v[a, mem] = 0; self.v[b, mem] = 1; self.ccol[j] = b
        self.refresh(a); self.refresh(b)
    def colouring(self):
        col = np.zeros(self.m, dtype=int)
        for j, c in enumerate(self.cl): col[list(c)] = self.ccol[j]
        return col

def tabu(m, k, iters, rng, tenure=10):
    s = State(m, k, rng); J = len(s.cl); rows = np.arange(J)
    cost = mod_cost(s.colouring(), m); best, best_col = cost, s.colouring()
    tab = np.zeros((J, k), dtype=np.int64)
    for it in range(1, iters + 1):
        if cost == 0: break
        add, own = s.tables()
        D = add - own[:, None]
        D = np.where((tab > it) & (cost + D >= best), 1e9, D)
        D[rows, s.ccol] = 1e9; D[own == 0] = 1e9
        mn = D.min()
        if mn >= 1e9: tab[:] = 0; continue
        cand = np.flatnonzero(D.ravel() == mn); j, b = divmod(int(cand[rng.integers(len(cand))]), k)
        a = int(s.ccol[j]); s.move(j, b); cost += int(mn)
        tab[j, a] = it + tenure + int(rng.integers(0, 6))
        if cost < best: best, best_col = cost, s.colouring()
    return best, best_col, it

def selftest(rng):
    for m in (45, 46, 61):
        s = State(m, 4, rng); cost = mod_cost(s.colouring(), m)
        for _ in range(200):
            add, own = s.tables(); j, b = int(rng.integers(len(s.cl))), int(rng.integers(4))
            if b == s.ccol[j]: continue
            cost += int(add[j, b] - own[j]); s.move(j, b)
            assert cost == mod_cost(s.colouring(), m), m
    print('self-test passed: running cost equals a direct count after 200 random moves, m = 45, 46, 61')

if __name__ == '__main__':
    iters, runs = int(sys.argv[1]), int(sys.argv[2])
    rng = np.random.default_rng(20261007)
    selftest(rng)
    print(f'symmetric tabu search, up to {iters} moves per run, {runs} runs per line, seed 20261007')
    print('best = fewest ordered monochromatic triples mod n + 1 (0 = valid colouring of 1..n)')
    for k, n in [(3, 13), (4, 44), (5, 150), (5, 160)] + [(6, n) for n in (450, 500, 520, 530, 536, 537, 538, 540, 542, 546)]:
        t0 = time.time(); res = []; found = None
        for _ in range(runs):
            best, col, it = tabu(n + 1, k, iters, rng)
            res.append((best, it))
            if best == 0:
                assert int_violations(col, n) == 0
                found = found or ''.join('ABCDEF'[c] for c in col[1:])
        print(f'  k={k} n={n:3d}: best per run {[b for b, _ in res]}, moves to success {[i for b, i in res if b == 0]}, {time.time() - t0:.0f}s')
        if found and (n >= 160): print('    colouring:', found)
