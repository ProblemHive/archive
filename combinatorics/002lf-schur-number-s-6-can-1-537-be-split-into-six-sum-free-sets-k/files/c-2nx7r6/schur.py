# Schur numbers by exhaustive backtracking.
# S(k) = largest n such that 1..n can be coloured with k colours with no x + y = z in one colour
# (x = y allowed). Colours are introduced in order (symmetry breaking).
import sys, time
sys.setrecursionlimit(10000)

def search(k, target):
    """Return a colouring of 1..target, or None. Counts nodes."""
    col = [0] * (target + 1)
    sets = [set() for _ in range(k)]
    nodes = 0
    def ok(n, c):
        s = sets[c]
        if n % 2 == 0 and n // 2 in s:
            return False
        return not any(n - x in s for x in s if 2 * x < n)
    def rec(n, used):
        nonlocal nodes
        if n > target:
            return True
        for c in range(min(used + 1, k)):
            if ok(n, c):
                nodes += 1
                sets[c].add(n); col[n] = c
                if rec(n + 1, max(used, c + 1)):
                    return True
                sets[c].discard(n)
        return False
    found = rec(1, 0)
    return (col[1:] if found else None), nodes

for k, s in ((1, 1), (2, 4), (3, 13), (4, 44)):
    t0 = time.time()
    good, n1 = search(k, s)
    bad, n2 = search(k, s + 1)
    print(f"k={k}: colouring of 1..{s} found: {good is not None} ({n1} nodes); "
          f"colouring of 1..{s + 1} exists: {bad is not None} ({n2} nodes, exhaustive); {time.time() - t0:.1f}s")
    if k == 4:
        print("a 4-colouring of 1..44:", "".join("ABCD"[c] for c in good))
