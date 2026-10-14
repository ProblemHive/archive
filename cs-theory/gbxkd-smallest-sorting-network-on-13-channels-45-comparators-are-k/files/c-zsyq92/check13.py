# Zero-one check of the two 13-channel networks listed on Dobbelaere's page (copied by hand from the
# page source, rows N13L45D10 and N13L46D9), plus two facts about the 45-comparator one:
# which single comparators can be dropped, and how many comparators the largest / smallest value meets
# from each input channel (the quantity in Van Voorhis's bound).
N45 = [
 [(0,12),(1,10),(2,9),(3,7),(5,11),(6,8)],
 [(1,6),(2,3),(4,11),(7,9),(8,10)],
 [(0,4),(1,2),(3,6),(7,8),(9,10),(11,12)],
 [(4,6),(5,9),(8,11),(10,12)],
 [(0,5),(3,8),(4,7),(6,11),(9,10)],
 [(0,1),(2,5),(6,9),(7,8),(10,11)],
 [(1,3),(2,4),(5,6),(9,10)],
 [(1,2),(3,4),(5,7),(6,8)],
 [(2,3),(4,5),(6,7),(8,9)],
 [(3,4),(5,6)],
]
N46 = [
 [(0,11),(1,7),(2,4),(3,5),(8,9),(10,12)],
 [(0,2),(3,6),(4,12),(5,7),(8,10)],
 [(0,8),(1,3),(2,5),(4,9),(6,11),(7,12)],
 [(0,1),(2,10),(3,8),(4,6),(9,11)],
 [(1,3),(2,4),(5,10),(6,8),(7,9),(11,12)],
 [(1,2),(3,4),(5,8),(6,9),(7,10)],
 [(2,3),(4,7),(5,6),(8,11),(9,10)],
 [(4,5),(6,7),(8,9),(10,11)],
 [(3,4),(5,6),(7,8),(9,10)],
]
n = 13

def flat(layers):
    return [c for layer in layers for c in layer]

def layers_ok(layers):
    return all(len({x for c in layer for x in c}) == 2 * len(layer) for layer in layers)

def unsorted_count(comps):
    # bit i of x is the value on channel i; sorted means zeros on low channels, ones on high channels
    bad = 0
    for x in range(1 << n):
        y = x
        for i, j in comps:
            if (y >> i) & 1 and not (y >> j) & 1:
                y ^= (1 << i) | (1 << j)
        k = bin(y).count("1")
        if y != ((1 << k) - 1) << (n - k):
            bad += 1
    return bad

for name, net in (("45 comparators, 10 layers", N45), ("46 comparators, 9 layers", N46)):
    comps = flat(net)
    print(f"{name}: {len(comps)} comparators in {len(net)} layers, layers disjoint: {layers_ok(net)}, "
          f"all i<j: {all(i < j for i, j in comps)}, unsorted 0-1 inputs: {unsorted_count(comps)} of {1 << n}")

comps = flat(N45)
droppable = [k for k in range(len(comps)) if unsorted_count(comps[:k] + comps[k + 1:]) == 0]
print("45-network: comparators that can be dropped singly without breaking it:", droppable)

def path_len(comps, start, largest):
    pos, cnt = start, 0
    for i, j in comps:
        if pos in (i, j):
            cnt += 1
            pos = j if largest else i
    return cnt, pos

dmax = [path_len(comps, s, True) for s in range(n)]
dmin = [path_len(comps, s, False) for s in range(n)]
print("45-network: comparators met by the largest value, by input channel:", [d for d, _ in dmax],
      "ends on", {p for _, p in dmax})
print("45-network: comparators met by the smallest value, by input channel:", [d for d, _ in dmin],
      "ends on", {p for _, p in dmin})

# Removing the path of the largest value from input channel s leaves a 12-channel sorting network
# (Van Voorhis's argument). Build it and check it, for every s.
def prune(comps, start):
    pos, out = start, []
    # channel labels of the remaining 12 values: follow the swap along the path
    lab = list(range(n))            # lab[c] = label of the wire now on channel c
    for i, j in comps:
        if pos in (i, j):
            # the largest value moves to j; the other value takes whichever channel is left
            if pos == i:
                lab[i], lab[j] = lab[j], lab[i]
            pos = j
        else:
            out.append((lab[i], lab[j]))
    return out, lab, pos

def sorts_generalised(comps, m_labels):
    # comparators here are (a, b) on wire labels with no orientation guarantee: put min on a, max on b.
    # A network of such comparators sorts iff the output is a fixed permutation of sorted order;
    # test: for every 0-1 input the output pattern depends only on the number of ones.
    seen = {}
    labs = sorted(m_labels)
    for x in range(1 << len(labs)):
        v = {l: (x >> t) & 1 for t, l in enumerate(labs)}
        for a, b in comps:
            if v[a] > v[b]:
                v[a], v[b] = v[b], v[a]
        k = sum(v.values())
        key = tuple(v[l] for l in labs)
        if seen.setdefault(k, key) != key:
            return False
    return True

sizes = []
for s in range(n):
    out, lab, pos = prune(comps, s)
    rest = [lab[c] for c in range(n) if c != pos]
    sizes.append((len(out), sorts_generalised(out, rest)))
print("45-network: size of the 12-channel network left after removing the largest value's path, and whether it sorts:")
print("  ", sizes)

