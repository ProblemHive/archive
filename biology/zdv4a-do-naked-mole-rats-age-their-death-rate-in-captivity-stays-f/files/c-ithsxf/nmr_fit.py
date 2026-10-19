"""Naked mole-rat colony records (Ruby et al. 2024, Supplementary Data File 1 = MOESM4, 6957 animals).
1. Rebuild the paper's life table (deaths, censored, exposure days per age bin) and compare with its
   Figure 1 sheet (MOESM3).
2. Gompertz-Makeham fit h(a) = m + b*exp(g*(a-1)), a in years, by maximum likelihood with and without
   delayed entry at 2008-01-30 (Dammann et al. 2019: only animals alive then were included), and a
   profile-likelihood upper bound on the Gompertz rate g (per year).
"""
import sys
import numpy as np
from scipy.optimize import minimize
from xlsx_min import sheets

SUP = "sup/11357_2024_1201_MOESM"
MAT = 183.0                       # age at sexual maturity used by the paper, days
EXCEL_2008_01_30 = 39477.0        # Excel serial date of 2008-01-30 (1900 date system)

def load():
    rows = None
    for name, r in sheets(SUP + "4_ESM.xlsx"):
        rows = r
    recs = []
    for n, r in rows[1:]:
        try:
            recs.append((r['A'], r['B'], r['C'], r['D'], r['E'], r['F'], r['G']))
        except KeyError:
            continue
    return recs

recs = load()
print("rows read:", len(recs))
ids = [x[0] for x in recs]
sex = np.array([x[1] for x in recs]); brd = np.array([x[2] for x in recs])
birth = np.array([x[3] for x in recs], float); end = np.array([x[4] for x in recs], float)
cens = np.array([x[5] == 'Y' for x in recs]); obs = np.array([x[6] for x in recs], float)
print("check end-birth == Obs.life:", np.all(end - birth == obs), " censored:", cens.sum(), " deaths:", (~cens).sum())
print("obs.life: max %.0f days (%.1f y); animals with obs.life < %d: %d" % (obs.max(), obs.max() / 365.25, MAT, (obs < MAT).sum()))

# ---- life table
mature = obs >= MAT
print("past maturity:", mature.sum(), "deaths among them:", (mature & ~cens).sum(), "censored:", (mature & cens).sum())
edges = [183, 400, 700, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6529, 13000]
print("\nlife table, no delayed entry (exposure from age 183 days):")
print("bin            deaths  cens  exposure_days  hazard/day")
for lo, hi in zip(edges[:-1], edges[1:]):
    sel = mature & (obs > lo)
    t0 = np.maximum(lo, MAT)
    t1 = np.minimum(obs, hi)
    ex = (t1 - t0)[sel].sum()
    d = (sel & ~cens & (obs <= hi)).sum()
    c = (sel & cens & (obs <= hi)).sum()
    print("%5d-%5d  %6d %5d %14.0f  %.3e" % (lo, hi, d, c, ex, d / ex if ex else float('nan')))

# ---- Gompertz-Makeham with optional delayed entry
def prep(delayed, sel):
    a1 = obs[sel] / 365.25
    a0 = np.full(sel.sum(), MAT / 365.25)
    if delayed:
        entry = np.maximum(MAT, EXCEL_2008_01_30 - birth[sel])
        keep = entry < obs[sel]      # animals that died or were censored before 2008-01-30 cannot be in the sample
        return a0[keep] * 0 + entry[keep] / 365.25, a1[keep], (~cens[sel])[keep].astype(float)
    return a0, a1, (~cens[sel]).astype(float)

def negll(theta, g, A0, A1, D):
    m = np.exp(theta[0]); b = np.exp(theta[1])
    if abs(g) < 1e-9:
        H = (m + b) * (A1 - A0); h = (m + b) * np.ones_like(A1)
    else:
        H = m * (A1 - A0) + b * (np.exp(g * (A1 - 1)) - np.exp(g * (A0 - 1))) / g
        h = m + b * np.exp(g * (A1 - 1))
    return -(D * np.log(h)).sum() + H.sum()

def fit_g(g, data, start):
    best = None
    for s in start:
        r = minimize(negll, s, args=(g,) + data, method='Nelder-Mead', options=dict(xatol=1e-8, fatol=1e-10, maxiter=4000))
        if best is None or r.fun < best.fun:
            best = r
    return best

def run(label, sel, delayed):
    data = prep(delayed, sel)
    A0, A1, D = data
    print("\n%s | delayed entry: %s | animals %d, deaths %d, max age %.1f y" % (label, delayed, len(A1), D.sum(), A1.max()))
    base = np.log(max(D.sum(), 1) / (A1 - A0).sum())
    starts = [[base, base - 3], [base - 1, base], [base - 2, base + 1]]
    gs = np.concatenate([[0.0], np.arange(0.01, 1.0, 0.01)])
    ll = []
    for g in gs:
        ll.append(-fit_g(g, data, starts).fun)
    ll = np.array(ll)
    imax = int(np.argmax(ll))
    print("  g = 0 (constant hazard, b absorbed in m): logL %.3f; best g on grid %.2f /yr: logL %.3f" % (ll[0], gs[imax], ll[imax]))
    # one-sided 95% upper bound: largest g with 2*(maxLL - LL(g)) <= 2.706
    ok = [g for g, l in zip(gs, ll) if 2 * (ll[imax] - l) <= 2.706]
    print("  upper 95%% bound on g (profile, one-sided, grid 0.01): %.2f /yr  -> hazard doubling time >= %.1f y" % (max(ok), np.log(2) / max(ok)) if max(ok) > 0 else "  bound 0")
    print("  LR test vs constant hazard: 2*(max - LL0) = %.3f" % (2 * (ll[imax] - ll[0])))

allm = mature.copy()
run("all past maturity", allm, False)
run("all past maturity", allm, True)
run("non-breeders", mature & (brd == 'N'), True)
run("breeders", mature & (brd == 'Y'), True)

