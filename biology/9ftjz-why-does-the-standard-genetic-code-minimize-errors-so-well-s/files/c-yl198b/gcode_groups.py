# Error minimization of the standard genetic code under restricted null models.
# MS = weighted mean squared change in polar requirement over single-base
# substitutions between sense codons (changes to/from stop codons are skipped).
# Null models (amino acids permuted among the 20 synonymous codon blocks):
#   free       : any permutation (sampled)
#   groups     : permute only within the four groups of Freeland & Hurst 1998b
#                (exact enumeration of all 120^4 = 207,360,000 codes)
#   groups+fix : as groups, with Phe, Tyr, Trp, His, Leu, Ile, Arg fixed
#                (Buhrman et al. 2013; exact enumeration of 11,520 codes)
import itertools
import sys
import numpy as np

B = "TCAG"
AAS = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
CODE = {a + b + c: AAS[16 * i + 4 * j + k] for i, a in enumerate(B) for j, b in enumerate(B) for k, c in enumerate(B)}

WOESE = dict(A=7.0, R=9.1, N=10.0, D=13.0, C=4.8, Q=8.6, E=12.5, G=7.9, H=8.4, I=4.9,
             L=4.9, K=10.1, M=5.3, F=5.0, P=6.6, S=7.5, T=6.6, W=5.2, Y=5.4, V=5.6)
UPDATED = dict(F=4.5, L=4.4, I=5.0, M=5.0, V=6.2, W=4.9, C=4.3, P=6.1, T=6.2, A=6.5,
               G=9.0, S=7.5, N=9.6, Q=8.9, Y=7.7, H=7.9, D=12.2, E=13.6, K=10.2, R=8.6)

GROUPS = ["GADEV", "IMTNK", "LPHQR", "FSYCW"]   # Freeland & Hurst 1998b, as listed in Buhrman et al. 2013
FIXED = "FYWHLIR"                                # Buhrman et al. 2013
ORDER = "".join(GROUPS)                          # block index 0..19, group g = blocks 5g..5g+4
idx = {a: i for i, a in enumerate(ORDER)}
PUR = "AG"

def weight(p, ts, scheme):
    if scheme == "equal":
        return 1.0
    # Freeland & Hurst 1998a weights, as given in Buhrman et al. 2013
    if (p == 0 and not ts) or (p == 1 and ts):
        return 0.5
    if p == 1 and not ts:
        return 0.1
    return 1.0

def count_matrix(scheme):
    N = np.zeros((20, 20)); total = 0.0; pairs = 0
    for c, x in CODE.items():
        if x == "*": continue
        for p in range(3):
            for b in B:
                if b == c[p]: continue
                y = CODE[c[:p] + b + c[p + 1:]]
                if y == "*": continue
                w = weight(p, (b in PUR) == (c[p] in PUR), scheme)
                N[idx[x], idx[y]] += w; total += w; pairs += 1
    return N, total, pairs

def ms_batch(V, N, total):
    d = N.sum(1)
    return 2 * ((V * V) @ d - np.einsum("bi,ij,bj->b", V, N, V)) / total

def free_sample(v, N, total, samples, seed):
    rng = np.random.default_rng(seed); nat = ms_batch(v[None, :], N, total)[0]
    better = 0; done = 0
    while done < samples:
        b = min(100000, samples - done)
        better += int((ms_batch(rng.permuted(np.tile(v, (b, 1)), axis=1), N, total) < nat - 1e-9).sum())
        done += b
    return better

def group_exact(v, N, total, fixed=""):
    """Enumerate every code that permutes values within each group (fixed amino acids stay)."""
    d = N.sum(1); nat = ms_batch(v[None, :], N, total)[0]
    perms = []   # per group: array (n_perms, 5) of values per block
    for g, grp in enumerate(GROUPS):
        free = [i for i, a in enumerate(grp) if a not in fixed]
        base = v[5 * g:5 * g + 5]
        rows = []
        for q in itertools.permutations(free):
            r = base.copy(); r[free] = base[list(q)]; rows.append(r)
        perms.append(np.array(rows))
    Nb = [[N[5 * g:5 * g + 5, 5 * h:5 * h + 5] for h in range(4)] for g in range(4)]
    # unary[g][p] = contribution of group g alone; pair[g][h][p,q] = cross term (both orders)
    unary = [(P * P) @ d[5 * g:5 * g + 5] - np.einsum("pi,ij,pj->p", P, Nb[g][g], P) for g, P in enumerate(perms)]
    pair = {(g, h): -(perms[g] @ Nb[g][h] @ perms[h].T) - (perms[h] @ Nb[h][g] @ perms[g].T).T
            for g in range(4) for h in range(g + 1, 4)}
    n = [len(P) for P in perms]
    # S01[p0,p1], S23[p2,p3] and the cross part pair02+pair03+pair12+pair13
    S01 = (unary[0][:, None] + unary[1][None, :] + pair[(0, 1)]).reshape(-1)
    S23 = (unary[2][:, None] + unary[3][None, :] + pair[(2, 3)]).reshape(-1)
    better = 0; ties = 0; best = np.inf; count = 0
    thr = nat * total / 2
    for p0 in range(n[0]):
        for p1 in range(n[1]):
            cross = (pair[(0, 2)][p0][:, None] + pair[(0, 3)][p0][None, :]
                     + pair[(1, 2)][p1][:, None] + pair[(1, 3)][p1][None, :]).reshape(-1)
            tot = S01[p0 * n[1] + p1] + S23 + cross
            better += int((tot < thr - 1e-7).sum()); ties += int((np.abs(tot - thr) <= 1e-7).sum())
            best = min(best, float(tot.min())); count += tot.size
    return nat, better, ties, 2 * best / total, count

if __name__ == "__main__":
    samples = int(sys.argv[1])
    for tname, table in (("Woese 1966", WOESE), ("updated 2008", UPDATED)):
        v = np.array([table[a] for a in ORDER])
        for scheme in ("equal", "FH"):
            N, total, pairs = count_matrix(scheme)
            fb = free_sample(v, N, total, samples, 1)
            nat, b, t, best, cnt = group_exact(v, N, total)
            nat2, b2, t2, best2, cnt2 = group_exact(v, N, total, FIXED)
            print(f"{tname} | weights {scheme} | pairs {pairs} | MS standard {nat:.4f}")
            print(f"  free (sampled): {fb} of {samples} better")
            print(f"  groups (exact): {b} of {cnt} better, {t} equal (incl. standard), best MS {best:.4f}")
            print(f"  groups+fixed (exact): {b2} of {cnt2} better, {t2} equal (incl. standard), best MS {best2:.4f}")
