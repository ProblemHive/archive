# Independent check of a (13,7,5) covering given by base blocks developed mod 13 (x -> x+1).
# Reads base blocks from the command line, one per argument, points separated by commas.
# Prints: number of blocks, whether every 5-subset is covered, how often 5-subsets are covered,
# blocks per point, range of blocks per pair, and for each base block how many 5-subsets only it covers.
#   python check_cover.py 0,1,2,3,4,6,8 0,1,2,3,9,10,11 ...
import sys
from itertools import combinations
from collections import Counter
V = 13
base = [tuple(int(x) for x in a.split(",")) for a in sys.argv[1:]]
blocks = []
for b in base:
    for i in range(V):
        blocks.append(frozenset((x + i) % V for x in b))
assert all(len(b) == 7 for b in blocks)
print("blocks:", len(blocks), "distinct:", len(set(blocks)))
cnt = Counter()
for b in blocks:
    for c in combinations(sorted(b), 5):
        cnt[c] += 1
allt = list(combinations(range(V), 5))
print("5-subsets:", len(allt), "covered:", sum(1 for c in allt if cnt[c] > 0))
print("times covered -> number of 5-subsets:", dict(sorted(Counter(cnt[c] for c in allt).items())))
print("blocks per point:", sorted(Counter(x for b in blocks for x in b).values())[::12])
pc = Counter(p for b in blocks for p in combinations(sorted(b), 2))
print("blocks per pair: min", min(pc.values()), "max", max(pc.values()))
for b in base:
    print("base block", " ".join(map(str, b)), "- 5-subsets covered by it alone:", sum(1 for c in combinations(b, 5) if cnt[c] == 1))
