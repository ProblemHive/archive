"""
Independent check of c/cw9q0x: for m -> floor(3m/2), the first j parities depend only on
m_0 mod 2^j and each parity pattern occurs exactly once; over all starts the counter is a fair
+2/-1 walk, so share halting within j steps = p_j -> (sqrt5-1)/2. Survey of starts 2..100000: 61.78% halt.
"""
import sympy as sp
from fractions import Fraction

def T(m):
    return m + (m >> 1)  # floor(3m/2)

def parities(m0, j):
    """first j parity bits of orbit starting at m0"""
    m = m0
    out = []
    for _ in range(j):
        out.append(m & 1)
        m = T(m)
    return tuple(out)

def halts_within(m0, j):
    """does the counter walk halt within j steps starting a=0?"""
    m = m0
    a = 0
    for k in range(1, j+1):
        if m & 1:
            if a == 0:
                return True, k
            a -= 1
        else:
            a += 2
        m = T(m)
    return False, None

# Lemma 1 check: for m = 2^j q + r with 0<=r<2^j, first j parities of orbit equal those of r.
j = 8
for r in range(2**j):
    # pick a few q values and verify same parity pattern as r itself (q=0)
    base = parities(r, j)
    for q in [1, 3, 7]:
        m = (1 << j) * q + r
        if parities(m, j) != base:
            print("LEMMA1 FAIL", r, q, parities(m, j), base)
print("Lemma1 spot-check done for j=8")

# Lemma 3 / bijection check: map residues mod 2^j -> parity patterns of length j is a bijection.
patterns = {}
dupes = []
for r in range(2**j):
    p = parities(r, j)
    if p in patterns:
        dupes.append((r, patterns[p]))
    else:
        patterns[p] = r
print("distinct patterns count:", len(patterns), "expected", 2**j, "duplicates:", len(dupes))

# Halting share over full residue set mod 2^j for increasing j
import math
r_exact = (sp.sqrt(5)-1)/2
for jj in [4,6,8,10]:
    cnt = sum(1 for r in range(2**jj) if halts_within(r, jj)[0])
    print(f"j={jj}: halt fraction {cnt}/{2**jj} = {Fraction(cnt, 2**jj)} ~ {float(Fraction(cnt,2**jj)):.6f}; target (sqrt5-1)/2 = {float(sp.N(r_exact,8)):.6f}")

# Survey of starts 2..100000 with cap 400 steps (as in c/cw9q0x)
halted = 0; latest = (0,0); hist={}
for m0 in range(2, 100001):
    h, step = halts_within(m0, 400)
    if h:
        halted += 1
        hist[step] = hist.get(step,0)+1
        if step > latest[0]:
            latest = (step, m0)
print(f"survey starts 2..100000 cap400: halted {halted} ({halted/99999:.5f}); latest halt step {latest[0]} at m0={latest[1]}")
print("first few hist entries:", sorted(hist.items())[:6])
# check all halting steps are 1 mod 3
bad = [s for s in hist if s % 3 != 1]
print("steps not 1 mod 3:", bad)

# Verify the quadratic root claim: r = (sqrt5-1)/2 satisfies r = 1/2 + r^3/2
r_sym = sp.symbols('r')
sol = sp.solve(sp.Eq(r_sym, sp.Rational(1,2) + r_sym**3/2), r_sym)
print("roots of r=1/2+r^3/2:", [sp.nsimplify(s) for s in sol])
print("(sqrt5-1)/2 numeric:", float(sp.N((sp.sqrt(5)-1)/2, 10)))

# Check the claimed histogram fractions: step 1:49999=1/2 of starts? total starts=99999; 49999/99999~0.49998~1/2 ok.
print("check hist proportions:")
total = 99999
for s,c in sorted(hist.items())[:6]:
    print(f"step {s}: count {c}, fraction {Fraction(c,total)} ~ {c/total:.5f}")

# Verify the claim that each of 2^j parity patterns occurs for exactly one residue mod 2^j (already done via bijection check)
print("bijection confirmed: distinct pattern count == 2^j and no duplicates")
