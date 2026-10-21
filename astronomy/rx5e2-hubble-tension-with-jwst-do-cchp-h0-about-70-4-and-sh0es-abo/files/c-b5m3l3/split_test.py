import re, random
from math import sqrt

# Table 3 of Li et al. (arXiv:2504.08921), as extracted by pdftotext into li.txt
pat = re.compile(r'^\s+(\d+)\s+(\S+)\s+.*?(\S+)\s+(\d+\.\d+)\s+(\d\.\d+)\s+(-\d+\.?\d*)\s+(\d\.\d+)\s+(\d+\.\d)\s+(?:\d+\.\d+\s+\d\.\d+|–\s+–)\s*$')
rows = []
for line in open('li.txt', encoding='utf-8'):
    m = pat.match(line)
    if m and 1 <= int(m.group(1)) <= 35:
        rows.append(dict(n=int(m.group(1)), host=m.group(2), sn=m.group(3), mb=float(m.group(6)),
                         smb=float(m.group(7)), h0=float(m.group(8))))
print('rows parsed:', len(rows), [r['n'] for r in rows] == list(range(1, 36)))

def wmean(rs):
    w = [1 / r['smb'] ** 2 for r in rs]
    return sum(wi * r['mb'] for wi, r in zip(w, rs)) / sum(w), 1 / sqrt(sum(w))

H0_BASE, MB_BASE = 72.1, -19.303   # Li et al. Table 2 baseline row (N = 35)
to_h0 = lambda mb: H0_BASE * 10 ** ((mb - MB_BASE) / 5)

mb_all, e_all = wmean(rows)
print(f'weighted mean MB, all 35: {mb_all:.3f} +- {e_all:.3f} -> H0 = {to_h0(mb_all):.2f}  (Li Table 2: -19.303, 72.1, 1.1)')
chi2 = sum(((r['mb'] - mb_all) / r['smb']) ** 2 for r in rows)
print(f'chi2 of the 35 MB values about their weighted mean: {chi2:.1f} for 34 d.o.f.')

# check the conversion on Li's two subsets: MB = -19.242 -> 74.1 and MB = -19.344 -> 70.7
print('conversion check: MB -19.242 ->', round(to_h0(-19.242), 2), ' MB -19.344 ->', round(to_h0(-19.344), 2))

# Permutation test: split the 35 calibrators at random into 11 and 24 and take the difference
# of the two weighted-mean H0 values (11-subset minus 24-subset). Observed in Li et al.: 74.1 - 70.7 = 3.4
random.seed(20261020)
obs = 74.1 - 70.7
N = 200000
diffs = []
for _ in range(N):
    idx = random.sample(range(35), 11)
    s11 = [rows[i] for i in idx]
    s24 = [rows[i] for i in range(35) if i not in set(idx)]
    diffs.append(to_h0(wmean(s11)[0]) - to_h0(wmean(s24)[0]))
mean = sum(diffs) / N
sd = sqrt(sum((d - mean) ** 2 for d in diffs) / N)
p_two = sum(1 for d in diffs if abs(d) >= obs) / N
p_one = sum(1 for d in diffs if d >= obs) / N
print(f'random 11/24 splits: N = {N}, mean diff {mean:.2f}, sd {sd:.2f}')
print(f'P(|diff| >= {obs:.1f}) = {p_two:.4f}   P(diff >= {obs:.1f}) = {p_one:.4f}')
