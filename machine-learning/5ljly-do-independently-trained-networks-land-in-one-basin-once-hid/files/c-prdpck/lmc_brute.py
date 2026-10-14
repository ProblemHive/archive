# lmc_brute.py - is weight matching the best permutation? For small widths, try ALL permutations of the
# hidden units of network B and compare the smallest barrier with the barrier after weight matching.
# Same data, training and barrier definition as lmc_digits.py (imported).
# Screening: barrier on the grid t = 0.25, 0.5, 0.75 for every permutation; the 50 best by that score are
# then re-evaluated on the full grid t = 0, 0.05, ..., 1, and the smallest full-grid barrier is reported.
import sys, time, itertools
import numpy as np
from lmc_digits import X, Y, y, tr, train, match, barrier

Xt, Yt = X[tr], Y[tr]
def loss(W1, b1, W2, b2):
    z = np.maximum(Xt @ W1.T + b1, 0) @ W2.T + b2
    z -= z.max(1, keepdims=True)
    return -((z - np.log(np.exp(z).sum(1, keepdims=True))) * Yt).sum(1).mean()

width, pairs = int(sys.argv[1]), int(sys.argv[2])
print(f'width {width}: {len(list(itertools.permutations(range(width))))} permutations per pair')
print('pair  plain    matched  best_of_all  rank_of_matched(screen)  identity_is_best?')
for k in range(pairs):
    t0 = time.time()
    A, B = train(width, 100 + 2 * k), train(width, 101 + 2 * k)
    LA, LB = loss(*A), loss(*B)
    scores = []
    for perm in itertools.permutations(range(width)):
        c = list(perm); s = -1e9
        for t in (0.25, 0.5, 0.75):
            L = loss((1 - t) * A[0] + t * B[0][c], (1 - t) * A[1] + t * B[1][c], (1 - t) * A[2] + t * B[2][:, c], (1 - t) * A[3] + t * B[3])
            s = max(s, L - ((1 - t) * LA + t * LB))
        scores.append((s, perm))
    scores.sort()
    full = min((barrier(A, [B[0][list(p)], B[1][list(p)], B[2][:, list(p)], B[3]], tr), p) for s, p in scores[:50])
    Bm = match(A, B)
    # which permutation did weight matching choose, and where does it rank in the screen?
    mperm = tuple(int(np.argmin(np.abs(B[0] - Bm[0][i]).sum(1))) for i in range(width))
    rank = [p for s, p in scores].index(mperm) + 1
    print(f'{k:4d}  {barrier(A, B, tr):7.4f}  {barrier(A, Bm, tr):7.4f}  {full[0]:10.4f}   {rank:8d} of {len(scores)}        {full[1] == tuple(range(width))}   {time.time()-t0:.0f}s', flush=True)
