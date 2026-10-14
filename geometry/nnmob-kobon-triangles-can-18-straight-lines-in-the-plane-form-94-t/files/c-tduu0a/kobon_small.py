# kobon_small.py - maximum number of bounded triangular faces over all SIMPLE pseudoline
# arrangements of n pseudolines (every two cross exactly once, no three through a point, no parallels).
# An arrangement is a wiring diagram: a reduced word s_i1 s_i2 ... of length n(n-1)/2 for the reversing
# permutation, where s_i swaps the wires at heights i and i+1. Words that differ by swapping adjacent
# commuting letters (|i-j| > 1) are the same diagram; we keep one word per class: the one in which no
# letter is directly followed by a letter smaller by 2 or more.
# The bounded face between two consecutive crossings at height i has 2 + (number of crossings at
# heights i-1 and i+1 between them) sides, so it is a triangle when exactly one such crossing lies between.
import sys, time

def run(n):
    N = n * (n - 1) // 2
    perm = list(range(n))
    since = [None] * (n - 1)    # since[i]: neighbours' crossings since the last s_i, None if no s_i yet
    best = 0; count = 0; hist = {}; best_word = None
    word = []
    def rec(depth, last, tri):
        nonlocal best, count, best_word
        if depth == N:
            count += 1; hist[tri] = hist.get(tri, 0) + 1
            if tri > best: best, best_word = tri, word[:]
            return
        for i in range(max(0, last - 1), n - 1):
            if perm[i] < perm[i + 1]:
                perm[i], perm[i + 1] = perm[i + 1], perm[i]
                old = (since[i], since[i - 1] if i > 0 else None, since[i + 1] if i < n - 2 else None)
                t = tri + (1 if since[i] == 1 else 0)
                since[i] = 0
                if i > 0 and since[i - 1] is not None: since[i - 1] += 1
                if i < n - 2 and since[i + 1] is not None: since[i + 1] += 1
                word.append(i + 1)
                rec(depth + 1, i, t)
                word.pop()
                since[i] = old[0]
                if i > 0: since[i - 1] = old[1]
                if i < n - 2: since[i + 1] = old[2]
                perm[i], perm[i + 1] = perm[i + 1], perm[i]
    rec(0, 0, 0)
    return count, best, hist, best_word

for n in range(3, int(sys.argv[1]) + 1):
    t0 = time.time()
    count, best, hist, w = run(n)
    top = sorted(hist.items())[-3:]
    print(f'n={n}: {count} wiring diagrams, max triangles {best}, diagrams by triangle count (top 3): {top}, {time.time()-t0:.1f}s')
    print('   one best word:', ' '.join(map(str, w)))
