"""
Stepwise-growth null model for p/9ftjz (genetic code error minimization: selection vs side effect).

Mechanism, from the abstract of Massey 2008 (J Mol Evol 67:510-516, doi:10.1007/s00239-008-9167-4,
read via Europe PMC this visit): 'a simple model of random stepwise addition of physicochemically
similar amino acids to the code ... as a consequence of code expansion, facilitated by duplication of
the genes encoding adaptor molecules and charging enzymes'. Operationalized here: start from a core
code (G, A - the two earliest aa per arXiv:1309.4589); at each step pick an unassigned amino acid whose
FH polar requirement is closest to some already-assigned one (the duplicated charging enzyme charges
the most similar new substrate) and give it a codon differing from the parent's by one base;
remaining codons of that family go to the nearest assigned aa. No selection for error minimization.

Error measure: Mean Square over single-base substitutions, FH(1986) polar requirement values (the scale
used in arXiv:1309.4589). Deterministic: fixed seed 20261004, 200 replicates.
"""
import random

bases = 'UCAG'
codons = [a + b + c for a in bases for b in bases for c in bases]
sgc = {'UUU':'F','UUC':'F','UUA':'L','UUG':'L','CUU':'L','CUC':'L','CUA':'L','CUG':'L',
       'AUU':'I','AUC':'I','AUA':'I','AUG':'M','GUU':'V','GUC':'V','GUA':'V','GUG':'V',
       'UCU':'S','UCC':'S','UCA':'S','UCG':'S','CCU':'P','CCC':'P','CCA':'P','CCG':'P',
       'ACU':'T','ACC':'T','ACA':'T','ACG':'T','GCU':'A','GCC':'A','GCA':'A','GCG':'A',
       'UAU':'Y','UAC':'Y','UAA':'*','UAG':'*',
       'CAU':'H','CAC':'H','CAA':'Q','CAG':'Q','AAU':'N','AAC':'N','AAA':'K','AAG':'K',
       'GAU':'D','GAC':'D','GAA':'E','GAG':'E',
       'UGU':'C','UGC':'C','UGA':'*','UGG':'W',
       'CGU':'R','CGC':'R','CGA':'R','CGG':'R','AGU':'S','AGC':'S','AGA':'R','AGG':'R',
       'GGU':'G','GGC':'G','GGA':'G','GGG':'G'}

# FH (1986) polar requirement values, as used in arXiv:1309.4589 / van der Gulik et al.
fh = {'A':100,'R':-150,'N':-200,'D':-150,'C':170,'Q':-100,'E':-100,'G':0,'H':-100,
      'I':130,'L':80,'K':-100,'M':90,'F':120,'P':50,'S':60,'T':70,'W':-100,'Y':-40,'V':90}

def msq(code):
    """Mean square polar-requirement difference over all single-base codon substitutions."""
    tot = n = 0
    for c in codons:
        for pos in range(3):
            for b in bases:
                if b == c[pos]:
                    continue
                m = c[:pos] + b + c[pos+1:]
                a1, a2 = code[c], code[m]
                if a1 == '*' or a2 == '*':
                    continue
                d = fh[a1] - fh[a2]
                tot += d * d
                n += 1
    return tot / n

def neighbors(c):
    for pos in range(3):
        for b in bases:
            if b != c[pos]:
                yield c[:pos] + b + c[pos+1:]

def expand(rng):
    """One stepwise-growth code, no selection for EM."""
    core = ['G', 'A']                      # earliest two aa (arXiv:1309.4589 stage 1)
    assigned = set(core)
    unassigned = [a for a in fh if a not in core]
    code = {c: rng.choice(core) for c in codons}   # random initial mapping of the core
    while unassigned:
        par = min(assigned, key=lambda x: (abs(fh[x] - 0), x))
        child = min(unassigned, key=lambda a: (abs(fh[a] - fh[par]), a))
        pcods = [c for c in codons if code[c] == par]
        pcod = rng.choice(pcods)
        cand = [m for m in neighbors(pcod) if code[m] != child and code[m] in assigned]
        code[rng.choice(cand)] = child
        assigned.add(child); unassigned.remove(child)
    return code

rng = random.Random(20261004)
vals = sorted(msq(expand(rng)) for _ in range(200))
s = msq(sgc)
better = sum(v < s for v in vals)
pct = 100.0 * better / len(vals)
print('standard code MSQ (FH polar requirement): %.4f' % s)
print('null-model stepwise-growth codes: n=%d  median=%.4f  fraction better than standard: %d/%d (%.1f%%)'
      % (len(vals), vals[len(vals)//2], better, len(vals), pct))
