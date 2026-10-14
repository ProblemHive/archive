# Tabu search for sum-free colourings of 1..n with k colours (Schur colourings).
# Cost = number of monochromatic triples (x, y, x + y) with x <= y. Cost 0 = valid colouring.
# A move recolours one number that is in at least one monochromatic triple.
# M[j][c] = number of triples containing j whose other members all have colour c,
# kept up to date in O(n) per move. Needs numpy. A search: failing to reach 0 proves nothing.
import sys, time
import numpy as np

FS536 = ("ABCDAEFAECABDAFCEFBDECCABBADCADEABCAFDEABCAEFAFCADEAFEECBBFCDCBDAEC"
         "CCEABDCCFAFBCAEDABBCCEADEACBBFDACCBAEFCCDADEACCAFDBCDCFBBACEAEEADCA"
         "DFAFCBBDDABBAFEACCADBBFCCADBACCAEDAFCABFEFDCDFAFBCAFDAEEACBADFCCFBA"
         "ECACBAFDCBDADBBCFDADBADEAEFAFDABFADCABFCACBADEACCAEBACCFDFBBEEADBAF"
         "FABDAEEBBFDFCCABEACCAEDABCACFBACDAFBADFAFEAEDABDADFCBBDADBCDFABCACE"
         "ABFCCFDABCAEEADFACBFAFACDFEFBACFADEACCABDACCFBBDACCAEFABBADDBBCFAFD"
         "ACDAEEAECABBFCDCBDFACCAEDADCCFEABCCADFBBCAEDAECCBBADEACBFAFCCDBAECC"
         "CEADBCDCFBBCEEFAEDACFAFEACBAEDFACBAEDACDABBACCEDBFECFADBACEAFEADCBA")

def brute_cost(col, n):
    return sum(1 for x in range(1, n + 1) for y in range(x, n + 1 - x) if col[x] == col[y] == col[x + y])

def build(col, n, k):
    ind = np.zeros((k, n + 1), dtype=np.int64)
    ind[col[1:], np.arange(1, n + 1)] = 1
    M = np.zeros((n + 1, k), dtype=np.int64)
    for j in range(1, n + 1):
        for c in range(k):
            v = ind[c]
            a = int(v[1:j] @ v[j - 1:0:-1]) if j > 1 else 0      # ordered pairs x + (j - x) = j
            if j % 2 == 0:
                h = j // 2
                a = (a + int(v[h])) // 2                         # unordered pairs; (h, h, j) counted once
            else:
                a //= 2
            m = n - j
            b = 0
            if m >= 1:
                w = v[1:m + 1] * v[j + 1:n + 1]                  # x and x + j both in c, x != j
                b = int(w.sum())
                if j <= m:
                    b -= int(w[j - 1])                           # remove x = j, handled next
                    b += int(v[2 * j])                           # (j, j, 2j): other member 2j
            M[j, c] = a + b
    return ind, M

def apply(ind, M, n, i, c, s):
    """Number i joins (s = +1) or leaves (s = -1) colour c: update M[:, c] for all j != i."""
    v = ind[c]
    keep = M[i, c]
    if n - i >= 1:
        M[1:n - i + 1, c] += s * v[i + 1:n + 1]                  # triple (i, j, i + j)
    if n > i:
        M[i + 1:n + 1, c] += s * v[1:n - i + 1]                  # triple (i, j - i, j), j > i
        if 2 * i <= n:
            M[2 * i, c] += s * (1 - v[i])                        # j = 2i: (i, i, 2i) has no other member
    if i > 1:
        M[1:i, c] += s * v[i - 1:0:-1]                           # triple (j, i - j, i), j < i
        if i % 2 == 0:
            M[i // 2, c] += s * (1 - v[i // 2])                  # j = i/2: (j, j, i) has no other member
    M[i, c] = keep

def tabu(col, n, k, iters, rng, tenure=12):
    col = col.copy()
    ind, M = build(col, n, k)
    for c in range(k):
        ind[c, 0] = 0
    rows = np.arange(n + 1)
    cost = brute_cost(col, n)
    best, best_col = cost, col.copy()
    tab = np.zeros((n + 1, k), dtype=np.int64)
    for it in range(1, iters + 1):
        if cost == 0:
            break
        cur = M[rows, col]
        D = M - cur[:, None]
        bad = (tab > it) & (cost + D >= best)                    # tabu unless it gives a new best
        D = np.where(bad, 10 ** 6, D)
        D[rows, col] = 10 ** 6
        D[cur == 0] = 10 ** 6
        D[0] = 10 ** 6
        m = D.min()
        if m >= 10 ** 6:
            tab[:] = 0
            continue
        cand = np.flatnonzero(D.ravel() == m)
        p = int(cand[rng.integers(len(cand))])
        i, b = divmod(p, k)
        a = int(col[i])
        ind[a, i] = 0
        apply(ind, M, n, i, a, -1)
        apply(ind, M, n, i, b, +1)
        ind[b, i] = 1
        col[i] = b
        cost += int(m)
        tab[i, a] = it + tenure + int(rng.integers(0, 6))
        if cost < best:
            best, best_col = cost, col.copy()
    return best, best_col, it

def selftest(rng):
    n, k = 60, 4
    col = np.concatenate(([0], rng.integers(0, k, n)))
    ind, M = build(col, n, k)
    cost = brute_cost(col, n)
    for _ in range(300):
        i, b = int(rng.integers(1, n + 1)), int(rng.integers(0, k))
        a = int(col[i])
        if a == b:
            continue
        d = int(M[i, b] - M[i, a])
        ind[a, i] = 0; apply(ind, M, n, i, a, -1); apply(ind, M, n, i, b, +1); ind[b, i] = 1; col[i] = b
        cost += d
        assert cost == brute_cost(col, n)
    ind2, M2 = build(col, n, k)
    assert (M2[1:] == M[1:]).all()
    print("self-test passed: incremental cost and table agree with brute force after 300 random moves")

if __name__ == "__main__":
    iters = int(sys.argv[1])
    rng = np.random.default_rng(20261007)
    selftest(rng)
    print(f"tabu search, {iters} moves per run, seed 20261007")
    print("A. random start; best = fewest monochromatic triples reached (0 = valid colouring)")
    for k, n in ((3, 13), (4, 40), (4, 44), (5, 120), (5, 140), (5, 150), (5, 160), (6, 300), (6, 400), (6, 450), (6, 500), (6, 536), (6, 537)):
        t0 = time.time()
        col = np.concatenate(([0], rng.integers(0, k, n)))
        best, bc, it = tabu(col, n, k, iters, rng)
        assert brute_cost(bc, n) == best
        print(f"  k={k} n={n:3d}: best {best:3d} after {it} moves, {time.time() - t0:.0f}s")
    print("B. start from the Fredricksen-Sweet colouring of 1..536, with 537.. added in the least-conflict colour")
    base = np.array([0] + ["ABCDEF".index(ch) for ch in FS536])
    assert brute_cost(base, 536) == 0
    for n in (537, 538, 540):
        t0 = time.time()
        col = base.copy()
        for j in range(537, n + 1):
            cnt = [sum(1 for x in range(1, j // 2 + 1) if col[x] == c and col[j - x] == c) for c in range(6)]
            col = np.append(col, int(np.argmin(cnt)))
        start = brute_cost(col, n)
        best, bc, it = tabu(col, n, 6, iters, rng)
        assert brute_cost(bc, n) == best
        changed = int((bc[1:537] != base[1:537]).sum())
        print(f"  n={n}: start {start} triples, best {best} after {it} moves, {changed} of the first 536 colours differ at the best point, {time.time() - t0:.0f}s")
