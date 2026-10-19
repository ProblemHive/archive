"""How much late rise in hazard do the colony records hide? (Ruby et al. 2024 Supplementary Data File 1.)
Model: hazard h(a) = m for a <= T and m*exp(r*(a-T)) for a > T (a in years; constant, then exponential rise).
For each T, the profile likelihood in r is closed form (m has an exact maximiser), so a grid is exact.
Delayed entry at 2008-01-30 (Dammann et al. 2019) as an option. Reports the one-sided 95% upper bound on r
(2*(maxLL - LL(r)) <= 2.706) and what it means as a hazard ratio at ages 25 and 30 relative to the constant level."""
import numpy as np
from xlsx_min import sheets

MAT = 183.0
EXCEL_2008_01_30 = 39477.0
rows = None
for name, r in sheets("sup/11357_2024_1201_MOESM4_ESM.xlsx"):
    rows = r
rec = [(r['C'], r['D'], r['E'], r['F'], r['G']) for n, r in rows[1:] if 'G' in r]
brd = np.array([x[0] for x in rec]); birth = np.array([x[1] for x in rec], float)
cens = np.array([x[3] == 'Y' for x in rec]); obs = np.array([x[4] for x in rec], float)
mature = obs >= MAT

def sample(sel, delayed):
    a1 = obs[sel] / 365.25
    ent = np.full(sel.sum(), MAT)
    if delayed:
        ent = np.maximum(MAT, EXCEL_2008_01_30 - birth[sel])
        keep = ent < obs[sel]
    else:
        keep = np.ones(sel.sum(), bool)
    return ent[keep] / 365.25, a1[keep], (~cens[sel])[keep].astype(float)

def F(a, T, r):                       # integral of f from 0 to a, f = 1 up to T, exp(r(a-T)) after
    a = np.asarray(a)
    base = np.minimum(a, T)
    tail = np.where(a > T, (np.expm1(r * (a - T)) / r) if r != 0 else (a - T), 0.0)
    return base + tail

def prof(T, r, A0, A1, D):
    FF = F(A1, T, r) - F(A0, T, r)
    m = D.sum() / FF.sum()
    return D.sum() * np.log(m) - D.sum() + (D * r * np.maximum(A1 - T, 0)).sum()

def report(label, sel, delayed):
    A0, A1, D = sample(sel, delayed)
    print("\n%s | delayed entry %s | animals %d, deaths %d, oldest %.1f y, animals observed past 18 y: %d (deaths %d), past 25 y: %d (deaths %d)" % (
        label, delayed, len(A1), D.sum(), A1.max(), (A1 > 18).sum(), D[A1 > 18].sum(), (A1 > 25).sum(), D[A1 > 25].sum()))
    print("   T(y)  r_hat(/y)  LRstat(r_hat vs 0)  r_upper95(/y)  doubling_time_at_bound(y)  HR(25y)  HR(30y) at bound")
    rs = np.arange(0.0, 3.0001, 0.005)
    for T in (10, 12, 15, 18, 20, 25):
        ll = np.array([prof(T, r, A0, A1, D) for r in rs])
        i = int(np.argmax(ll))
        ok = rs[2 * (ll[i] - ll) <= 2.706]
        ub = ok.max()
        print("  %4d  %8.3f  %18.3f  %13.3f  %24.1f  %8.1f %8.1f" % (
            T, rs[i], 2 * (ll[i] - ll[0]), ub, np.log(2) / ub if ub > 0 else float('inf'),
            np.exp(ub * max(25 - T, 0)), np.exp(ub * max(30 - T, 0))))

report("all past maturity", mature, True)
report("all past maturity", mature, False)
report("non-breeders", mature & (brd == 'N'), True)

