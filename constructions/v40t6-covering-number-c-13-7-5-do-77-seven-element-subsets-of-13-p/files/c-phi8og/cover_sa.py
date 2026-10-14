# Simulated annealing for a (v,k,t) covering with b blocks: every t-subset of {0..v-1} inside some block.
# State: b blocks (k-subsets). Cost: number of t-subsets in no block. Move: in one block, swap one point
# for a point outside it. Accept if cost does not rise, else with probability exp(-rise/T).
# T falls geometrically from T0 to T1 over the allowed moves. Stops at cost 0 and prints the blocks.
#   python cover_sa.py v k t b seed moves [T0 T1]
import sys, random, math, time
from itertools import combinations

v, k, t, b, seed, moves = map(int, sys.argv[1:7])
T0, T1 = (float(sys.argv[7]), float(sys.argv[8])) if len(sys.argv) > 8 else (0.6, 0.15)
rng = random.Random(seed)
tidx = {sum(1 << i for i in c): n for n, c in enumerate(combinations(range(v), t))}
cache = {}
def tsets(mask):
    r = cache.get(mask)
    if r is None:
        pts = [i for i in range(v) if mask >> i & 1]
        r = cache[mask] = [tidx[sum(1 << i for i in c)] for c in combinations(pts, t)]
    return r

blocks = [sum(1 << i for i in rng.sample(range(v), k)) for _ in range(b)]
cnt = [0] * len(tidx)
for B in blocks:
    for j in tsets(B):
        cnt[j] += 1
cost = cnt.count(0)
best = cost
t0 = time.time()
ratio = (T1 / T0) ** (1.0 / moves)
T = T0
for step in range(moves):
    if cost == 0:
        break
    i = rng.randrange(b)
    B = blocks[i]
    while True:
        x = rng.randrange(v)
        if B >> x & 1:
            break
    while True:
        y = rng.randrange(v)
        if not B >> y & 1:
            break
    N = B ^ (1 << x) ^ (1 << y)
    d = 0
    for j in tsets(B):
        cnt[j] -= 1
        if cnt[j] == 0:
            d += 1
    for j in tsets(N):
        if cnt[j] == 0:
            d -= 1
        cnt[j] += 1
    if d <= 0 or rng.random() < math.exp(-d / T):
        blocks[i] = N
        cost += d
        if cost < best:
            best = cost
    else:
        for j in tsets(N):
            cnt[j] -= 1
        for j in tsets(B):
            cnt[j] += 1
    T *= ratio
print(f"({v},{k},{t}) b={b} seed={seed}: final cost {cost}, best cost {best}, moves {step + (cost != 0)}, {time.time() - t0:.0f}s")
if cost == 0:
    for B in sorted(blocks):
        print(" ".join(str(i + 1) for i in range(v) if B >> i & 1))
