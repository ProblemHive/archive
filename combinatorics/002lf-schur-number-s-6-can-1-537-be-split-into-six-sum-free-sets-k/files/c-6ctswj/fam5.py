# fam5.py - sum-free colourings mod m that have a multiplier of order 5, as SAT problems for Kissat.
#
# Family: colour the nonzero residues mod m with k colours so that no colour holds x, y, z with
# x + y = z mod m (x = y allowed), and so that colour(u * x) = pi(colour(x)) for a unit u of
# multiplicative order 5 mod m, where pi is either the identity ("fixed": u keeps every colour class)
# or the 5-cycle (0 1 2 3 4) ("cycle": u rotates five classes; with six colours the sixth is kept).
# Any such colouring, read on 1..m-1, is a sum-free colouring of the integers 1..m-1.
# One u per subgroup of order 5 is enough: another generator u^j gives the same colourings (fixed),
# or the same after renaming colours (cycle).
#
# Limits are in solver conflicts, not seconds, so that a rerun gives the same answers.
# Part 0 looks at the published 536 colouring: is it sum-free mod 537, and which multipliers map its
# colour classes onto colour classes?
#
# Usage: python fam5.py CONFLICTS WORKERS OUTFILE
import subprocess, sys, os
from math import gcd
from multiprocessing import Pool

FS536 = ("ABCDAEFAECABDAFCEFBDECCABBADCADEABCAFDEABCAEFAFCADEAFEECBBFCDCBDAEC"
         "CCEABDCCFAFBCAEDABBCCEADEACBBFDACCBAEFCCDADEACCAFDBCDCFBBACEAEEADCA"
         "DFAFCBBDDABBAFEACCADBBFCCADBACCAEDAFCABFEFDCDFAFBCAFDAEEACBADFCCFBA"
         "ECACBAFDCBDADBBCFDADBADEAEFAFDABFADCABFCACBADEACCAEBACCFDFBBEEADBAF"
         "FABDAEEBBFDFCCABEACCAEDABCACFBACDAFBADFAFEAEDABDADFCBBDADBCDFABCACE"
         "ABFCCFDABCAEEADFACBFAFACDFEFBACFADEACCABDACCFBBDACCAEFABBADDBBCFAFD"
         "ACDAEEAECABBFCDCBDFACCAEDADCCFEABCCADFBBCAEDAECCBBADEACBFAFCCDBAECC"
         "CEADBCDCFBBCEEFAEDACFAFEACBAEDFACBAEDACDABBACCEDBFECFADBACEAFEADCBA")

def int_violations(col, n):
    """monochromatic x + y = z over the integers 1..n; col[1..n]"""
    return sum(1 for x in range(1, n + 1) for y in range(x, n + 1 - x) if col[x] == col[y] == col[x + y])

def mod_violations(col, m):
    """monochromatic x + y = z mod m with x <= y, over the nonzero residues"""
    return [(x, y, (x + y) % m) for x in range(1, m) for y in range(x, m)
            if (x + y) % m and col[x] == col[y] == col[(x + y) % m]]

def order5_units(m):
    """the smallest generator of each subgroup of order 5 of the units mod m"""
    seen, out = set(), []
    for u in range(2, m):
        if gcd(u, m) == 1 and pow(u, 5, m) == 1:
            H = frozenset(pow(u, e, m) for e in range(5))
            if H not in seen:
                seen.add(H)
                out.append(min(H - {1}))
    return out

def build(k, m, u, pi):
    """clauses for the family; variables: one per (orbit of x -> u*x, colour of its first element)"""
    inv = [0] * k
    for a, b in enumerate(pi):
        inv[b] = a
    first, steps, firsts, stuck = [0] * m, [0] * m, [], {}
    for x in range(1, m):
        if first[x] == 0:
            firsts.append(x)
            y, j = x, 0
            while first[y] == 0:
                first[y], steps[y] = x, j
                y, j = y * u % m, j + 1
            stuck[x] = (j == 1)            # u * x = x: x can only have a colour that pi keeps
    index = {x: i for i, x in enumerate(firsts)}
    def lit(y, c):
        """the variable 'y has colour c', or None when that is impossible"""
        for _ in range(steps[y]):
            c = inv[c]
        r = first[y]
        if stuck[r] and pi[c] != c:
            return None
        return index[r] * k + c + 1
    clauses = set()
    for r in firsts:
        clauses.add(tuple(v for v in (lit(r, c) for c in range(k)) if v))
    for x in firsts:                       # every sum has a multiple u^j * (x + y = z) with x a first element
        for y in range(1, m):
            z = (x + y) % m
            if z:
                for c in range(k):
                    ls = [lit(x, c), lit(y, c), lit(z, c)]
                    if None not in ls:
                        clauses.add(tuple(sorted({-v for v in ls})))
    def decode(model):
        col = [None] * m
        for x in range(1, m):
            c = next(c for c in range(k) if lit(first[x], c) in model)
            for _ in range(steps[x]):
                c = pi[c]
            col[x] = c
        return col
    return len(firsts), sorted(clauses), decode

def case(args):
    k, m, u, name, pi, conflicts = args
    norb, cl, decode = build(k, m, u, pi)
    fn = f"/tmp/fam5_{k}_{m}_{u}_{name}.cnf"
    with open(fn, "w") as f:
        f.write(f"p cnf {norb * k} {len(cl)}\n")
        for c in cl:
            f.write(" ".join(map(str, c)) + " 0\n")
    out = subprocess.run(["kissat", "-q", f"--conflicts={conflicts}", fn], capture_output=True, text=True).stdout
    os.remove(fn)
    res, colouring = "UNKNOWN", ""
    if "s UNSATISFIABLE" in out:
        res = "UNSAT"
    elif "s SATISFIABLE" in out:
        model = {int(t) for line in out.splitlines() if line.startswith("v ") for t in line[2:].split() if int(t) > 0}
        col = decode(model)
        ok = (int_violations(col, m - 1) == 0 and not mod_violations(col, m)
              and all(col[x * u % m] == pi[col[x]] for x in range(1, m)))
        res = "SAT" if ok else "SAT-BUT-RECHECK-FAILED"
        colouring = "".join("ABCDEF"[c] for c in col[1:])
    return k, m, u, name, norb, len(cl), res, colouring

def part0(out):
    m = 537
    col = [None] + ["ABCDEF".index(ch) for ch in FS536]
    out.append("PART 0: the published colouring of 1..536 (Fredricksen and Sweet 2000), read mod 537")
    out.append(f"  violations over the integers: {int_violations(col, 536)}")
    mv = mod_violations(col, m)
    out.append(f"  violations mod 537 (x <= y): {len(mv)} {mv[:6]}")
    good = []
    for u in range(1, m):
        if gcd(u, m) != 1:
            continue
        image = {}
        if all(image.setdefault(col[x], col[x * u % m]) == col[x * u % m] for x in range(1, m)):
            good.append(u)
    out.append(f"  units u mod 537 ({sum(1 for u in range(1, m) if gcd(u, m) == 1)} in all) for which x -> u*x maps every colour class into one colour class: {good}")
    # the same test leaving out 179 and 358, the one pair where the colouring is not symmetric
    good2 = []
    for u in range(1, m):
        if gcd(u, m) != 1:
            continue
        image = {}
        if all(image.setdefault(col[x], col[x * u % m]) == col[x * u % m]
               for x in range(1, m) if x not in (179, 358) and x * u % m not in (179, 358)):
            good2.append(u)
    out.append(f"  the same, ignoring the residues 179 and 358: {good2}")
    out.append(f"  units of order 5 mod 537: {order5_units(m)} (537 = 3 * 179, and 5 does not divide 2 * 178)")

if __name__ == "__main__":
    conflicts, workers, outfile = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    out = []
    ver = subprocess.run(["kissat", "--version"], capture_output=True, text=True).stdout.strip()
    out.append(f"kissat {ver}, at most {conflicts} conflicts per case")
    part0(out)
    cyc5 = lambda k: tuple([1, 2, 3, 4, 0] + list(range(5, k)))
    ident = lambda k: tuple(range(k))
    for k, lo, hi in ((5, 31, 161), (6, 151, 700)):
        jobs = [(k, m, u, name, f(k), conflicts) for m in range(lo, hi + 1) for u in order5_units(m)
                for name, f in (("fixed", ident), ("cycle", cyc5))]
        out.append(f"PART {k - 4}: {k} colours, m = {lo}..{hi}: {len(jobs)} cases (m, a subgroup of order 5, fixed or cycle)")
        tally = {}
        with Pool(workers) as pool:
            for k_, m, u, name, norb, ncl, res, colouring in pool.imap(case, jobs, chunksize=1):
                if res != "UNSAT":
                    out.append(f"  k={k} m={m} n={m - 1} u={u} {name}: {norb} orbits, {ncl} clauses: {res}")
                if colouring:
                    out.append("    " + colouring)
                tally.setdefault(name, {}).setdefault(res, []).append(m - 1)
                print(k, m, u, name, res, flush=True)
        for name in ("fixed", "cycle"):
            t = tally.get(name, {})
            out.append(f"  SUMMARY k={k} {name}: UNSAT {len(t.get('UNSAT', []))}, UNKNOWN {len(t.get('UNKNOWN', []))}, "
                       f"SAT {len(t.get('SAT', []))}; n with SAT: {sorted(set(t.get('SAT', [])))}; "
                       f"n with UNKNOWN: {sorted(set(t.get('UNKNOWN', [])))}")
    with open(outfile, "w") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(l for l in out if not l.startswith("    ")))
