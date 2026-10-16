# check.py - independent checks for erdos3.c, in plain Python big integers.
# 1) brute force: every n <= N, full ternary expansion of 2^n; list n with no digit 2,
#    and the smallest n >= 1 with 2^n >= 3^(m-1) and no 2 in the last m digits (A351928) for m <= M.
# 2) fallback: for each n in a file, find a digit 2 by computing 2^n mod 3^L for growing L.
# Usage: python3 check.py brute N M  |  python3 check.py fallback FILE
import sys

def tern_digits_low(x, count):
    d = []
    for _ in range(count):
        x, r = divmod(x, 3)
        d.append(r)
    return d

if sys.argv[1] == "brute":
    N, M = int(sys.argv[2]), int(sys.argv[3])
    clean, best = [], {}
    x = 1
    for n in range(N + 1):
        y, low, has2, pos = x, [], False, 0
        while y:
            y, r = divmod(y, 3)
            if r == 2:
                has2 = True
                break
            pos += 1
        if not has2:
            clean.append(n)
        # pos = number of trailing non-2 digits (whole length if none)
        for m in range(1, M + 1):
            if m in best or n == 0:
                continue
            if pos >= m and x >= 3 ** (m - 1):
                best[m] = n
        x *= 2
    print("brute force n <= %d: no digit 2 for n in %s" % (N, clean))
    for m in range(1, M + 1):
        print("A351928(%d) = %s" % (m, best.get(m)))
else:
    bad = 0
    cnt = 0
    for line in open(sys.argv[2]):
        n = int(line)
        cnt += 1
        L = 160
        while True:
            d = tern_digits_low(pow(2, n, 3 ** L), L)
            if 2 in d:
                break
            if 3 ** L > 2 ** n:   # whole number seen, no 2: counterexample
                bad += 1
                print("COUNTEREXAMPLE", n)
                break
            L *= 2
    print("fallback cases checked: %d, counterexamples: %d" % (cnt, bad))
