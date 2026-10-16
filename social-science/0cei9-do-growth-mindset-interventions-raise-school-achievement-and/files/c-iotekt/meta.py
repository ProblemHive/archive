"""Rerun of Macnamara & Burgoyne (2023) from their open data (osf.io/ajhxv, sheet 'Main Analysis').

Random-effects meta-analysis (REML, tau^2 by Fisher scoring) on Cohen's d with the
sheet's 'Adjusted Variance' (variance corrected for clustering / dependence). Then
the subgroup the other side of the dispute points to (Burnette et al. 2023, Tipton
et al. 2023): students marked high risk status, against the rest, as a meta-regression.
Also PET (d regressed on its standard error) within each subset.
"""
import math
import numpy as np
from xlsx_min import sheets

rows = None
for name, rs in sheets('/data/mindset/macnamara_burgoyne_data.xlsx'):
    if name == 'Main Analysis':
        rows = rs
hdr = rows[0][1]
col = {h: c for c, h in hdr.items()}
data = []
for _, r in rows[1:]:
    d, v = r.get(col["Cohen's d"]), r.get(col['Adjusted Variance'])
    if isinstance(d, float) and isinstance(v, float) and v > 0:
        data.append(dict(ref=r.get(col['Reference']), d=d, v=v, N=r.get(col['N']),
                         risk=r.get(col['Risk status']), ses=r.get(col['SES']),
                         stake=r.get(col['Financial Stake']), m2=r.get(col['Model 2']), m3=r.get(col['Model 3'])))
print('effect sizes with d and adjusted variance:', len(data))

def reml(y, v, X=None, iters=200):
    y, v = np.asarray(y), np.asarray(v)
    X = np.ones((len(y), 1)) if X is None else X
    t2 = max(0.0, np.var(y) - v.mean())
    for _ in range(iters):
        W = np.diag(1 / (v + t2))
        XtWX = X.T @ W @ X
        P = W - W @ X @ np.linalg.solve(XtWX, X.T @ W)
        # REML score and information for tau^2
        score = -0.5 * np.trace(P) + 0.5 * y @ P @ P @ y
        info = 0.5 * np.trace(P @ P)
        new = max(0.0, t2 + score / info)
        if abs(new - t2) < 1e-10:
            t2 = new
            break
        t2 = new
    W = np.diag(1 / (v + t2))
    cov = np.linalg.inv(X.T @ W @ X)
    b = cov @ X.T @ W @ y
    return b, np.sqrt(np.diag(cov)), t2

def show(label, sub):
    if len(sub) < 3:
        print(f'{label:42s} k={len(sub)} too few'); return
    y = [s['d'] for s in sub]; v = [s['v'] for s in sub]
    b, se, t2 = reml(y, v)
    lo, hi = b[0] - 1.96 * se[0], b[0] + 1.96 * se[0]
    # PET: d = b0 + b1 * SE
    X = np.column_stack([np.ones(len(sub)), np.sqrt(v)])
    bp, sep, _ = reml(y, v, X)
    N = sum(s['N'] for s in sub if isinstance(s['N'], float))
    print(f'{label:42s} k={len(sub):3d} N={N:8.0f}  d={b[0]:6.3f} [{lo:6.3f},{hi:6.3f}]  tau={math.sqrt(t2):.3f}   PET intercept {bp[0]:6.3f} [{bp[0]-1.96*sep[0]:6.3f},{bp[0]+1.96*sep[0]:6.3f}]')

show('all effect sizes (their Model 1)', data)
show('Model 2 (intervention changed mindsets)', [s for s in data if s['m2'] == 'Yes'])
show('Model 3 (best available evidence)', [s for s in data if s['m3'] == 'Yes'])
show('risk status High', [s for s in data if s['risk'] == 'High'])
show('risk status Medium', [s for s in data if s['risk'] == 'Medium'])
show('risk status Low', [s for s in data if s['risk'] == 'Low'])
show('low SES', [s for s in data if s['ses'] == 'low SES'])
show('financial stake: yes', [s for s in data if s['stake'] == 'Yes'])
show('financial stake: no', [s for s in data if s['stake'] == 'No'])
show('High risk, no financial stake', [s for s in data if s['risk'] == 'High' and s['stake'] == 'No'])
show('Model 2 and High risk', [s for s in data if s['risk'] == 'High' and s['m2'] == 'Yes'])
# meta-regression: High vs other, one model
sub = [s for s in data if s['risk'] in ('High', 'Medium', 'Low')]
X = np.column_stack([np.ones(len(sub)), [1.0 if s['risk'] == 'High' else 0.0 for s in sub]])
b, se, t2 = reml([s['d'] for s in sub], [s['v'] for s in sub], X)
print(f'meta-regression, k={len(sub)}: d(other) = {b[0]:.3f}, High minus other = {b[1]:.3f} [{b[1]-1.96*se[1]:.3f},{b[1]+1.96*se[1]:.3f}], tau={math.sqrt(t2):.3f}')
X = np.column_stack([X, [1.0 if s['stake'] == 'Yes' else 0.0 for s in sub]])
b, se, t2 = reml([s['d'] for s in sub], [s['v'] for s in sub], X)
print(f'  adding financial stake: High minus other = {b[1]:.3f} [{b[1]-1.96*se[1]:.3f},{b[1]+1.96*se[1]:.3f}], stake = {b[2]:.3f} [{b[2]-1.96*se[2]:.3f},{b[2]+1.96*se[2]:.3f}]')
print('High-risk effect sizes (reference, d, SE, financial stake):')
for s in sorted([s for s in data if s['risk'] == 'High'], key=lambda s: -s['d']):
    print(f"  {str(s['ref'])[:60]:60s} {s['d']:6.3f} {math.sqrt(s['v']):6.3f} {s['stake']}")
