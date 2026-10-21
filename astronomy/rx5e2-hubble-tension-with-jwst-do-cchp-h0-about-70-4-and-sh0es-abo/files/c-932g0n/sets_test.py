import re, random
from math import sqrt

# Table 3 of Li et al. (arXiv:2504.08921), as extracted by pdftotext into li.txt (same parser as split_test.py)
pat = re.compile(r'^\s+(\d+)\s+(\S+)\s+.*?(\S+)\s+(\d+\.\d+)\s+(\d\.\d+)\s+(-\d+\.?\d*)\s+(\d\.\d+)\s+(\d+\.\d)\s+(?:\d+\.\d+\s+\d\.\d+|–\s+–)\s*$')
rows = {}
for line in open('li.txt', encoding='utf-8'):
    m = pat.match(line)
    if m and 1 <= int(m.group(1)) <= 35:
        rows[int(m.group(1))] = dict(host=m.group(2), mb=float(m.group(6)), smb=float(m.group(7)))
assert sorted(rows) == list(range(1, 36)), 'parse failed'

# Membership, from the CCHP paper's Table 1 (arXiv:2408.06153, 10 hosts, 11 SNe) and the host columns of
# Li et al. Table 3 (JWST distances labelled L24 = SH0ES JWST). Row numbers are Li Table 3 rows.
CCHP_JWST = [1, 8, 15, 20, 22, 24, 27, 28, 31, 32, 34]        # 11 SNe: 2011fe 2012fr 2015F 2011by 2007sr 2012cg 1981B 1990N 2013aa 2017cbv 2013dy
SH0ES_JWST = [12, 13, 14, 16, 18, 19, 30, 31, 32, 33]         # 10 SNe: 2001el 2021pit 2005df 2018gv 1994ae 2012ht 2007af 2013aa 2017cbv 2017erp
shared = sorted(set(CCHP_JWST) & set(SH0ES_JWST))

def wm(ids):
    w = [1 / rows[i]['smb'] ** 2 for i in ids]
    mb = sum(wi * rows[i]['mb'] for wi, i in zip(w, ids)) / sum(w)
    return mb, 1 / sqrt(sum(w))

def h0(mb):  # Li et al. eq. 1: 5 log10(H0/72.5) = MB + 19.29
    return 72.5 * 10 ** ((mb + 19.29) / 5)

def chi2(ids):
    mb, _ = wm(ids)
    return sum(((rows[i]['mb'] - mb) / rows[i]['smb']) ** 2 for i in ids)

for name, ids in [('CCHP JWST (11)', CCHP_JWST), ('SH0ES JWST (10)', SH0ES_JWST), ('all 35', list(range(1, 36)))]:
    mb, e = wm(ids)
    print(f'{name:18s} MB = {mb:.3f} +- {e:.3f}  H0 = {h0(mb):.1f}  chi2 = {chi2(ids):.1f} for {len(ids)-1} dof')
print('shared SNe (rows):', shared)

# Disjoint comparison: drop the 2 shared SNe from both lists
a = [i for i in CCHP_JWST if i not in shared]     # 9
b = [i for i in SH0ES_JWST if i not in shared]    # 8
(mba, ea), (mbb, eb) = wm(a), wm(b)
d_obs = h0(mbb) - h0(mba)
se = sqrt((0.4605 * h0(mba) * ea) ** 2 + (0.4605 * h0(mbb) * eb) ** 2)   # 0.4605 = ln(10)/5
print(f'disjoint: CCHP-only {len(a)} SNe H0 = {h0(mba):.2f}; SH0ES-only {len(b)} SNe H0 = {h0(mbb):.2f}; '
      f'diff {d_obs:.2f} +- {se:.2f} (z = {d_obs / se:.2f})')

# Permutation: a random disjoint pair of subsets of sizes 9 and 8 drawn from all 35 SNe
random.seed(20261020)
N = 200000
cnt = 0
ds = []
for _ in range(N):
    s = random.sample(range(1, 36), len(a) + len(b))
    x, y = s[:len(a)], s[len(a):]
    d = h0(wm(y)[0]) - h0(wm(x)[0])
    ds.append(d)
    if abs(d) >= abs(d_obs):
        cnt += 1
mean = sum(ds) / N
sd = sqrt(sum((d - mean) ** 2 for d in ds) / N)
print(f'random disjoint 9/8 subsets, {N} draws: sd of the H0 difference = {sd:.2f}; P(|diff| >= {abs(d_obs):.2f}) = {cnt / N:.4f}')

