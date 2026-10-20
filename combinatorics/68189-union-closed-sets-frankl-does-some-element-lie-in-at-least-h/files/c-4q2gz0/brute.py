# Brute-force cross-check of uc.c for n <= 4: test every family of subsets of [n].
import sys
n = int(sys.argv[1]); N = 1 << n
tot = ne = half = below = 0
for fam in range(1 << N):
    mem = [s for s in range(N) if fam >> s & 1]
    ok = all((fam >> (a | b)) & 1 for a in mem for b in mem)
    if not ok: continue
    tot += 1
    if not any(mem): continue
    ne += 1
    k = len(mem)
    mx = max(sum(1 for s in mem if s >> i & 1) for i in range(n))
    half += (2 * mx == k); below += (2 * mx < k)
print(n, tot, ne, below, half)

