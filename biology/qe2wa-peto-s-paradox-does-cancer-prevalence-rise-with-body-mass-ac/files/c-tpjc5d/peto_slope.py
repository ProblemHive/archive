"""How steeply does neoplasia prevalence rise with body mass, compared with Peto's
naive expectation? Compton et al. 2024 species table (via Dujon et al. 2025 repository).

If each of N cells independently becomes cancerous with small probability, the
lifetime probability is P = 1 - exp(-c N), so cloglog(P) = log c + log N. With N
proportional to adult mass M, the slope of cloglog(P) on ln(M) is 1 (more if larger
species also live longer). A slope well below 1 is Peto's paradox in his sense; a
slope of 0 is the stronger 'no relation' version.

Not phylogenetic: species are treated as independent, with overdispersion handled
by a quasi-binomial scale (Pearson chi2 / df). Usage: python3 peto_slope.py [min_records]
"""
import sys, csv, math
import numpy as np
import statsmodels.api as sm

MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 20
CLASS_INTERCEPTS = len(sys.argv) > 2 and sys.argv[2] == 'by-class'
rows = list(csv.DictReader(open('/data/peto/compton_vertebrates.csv', encoding='utf-8')))

def fit(sel, outcome, link):
    n = np.array([float(r['RecordsWithDenominators']) for r in sel])
    if outcome == 'neoplasia':
        y = np.array([float(r['NeoplasiaWithDenominators']) for r in sel])
    else:  # malignancy prevalence: malignant cases over all records (as MalignancyPrevalence in the table)
        y = np.array([float(r['Malignant']) for r in sel])
    x = np.log(np.array([float(r['adult_weight(g)']) for r in sel]))
    keep = n > 0
    y, n, x = y[keep], n[keep], x[keep]
    sel = [r for r, k in zip(sel, keep) if k]
    X = sm.add_constant(x)
    classes = sorted(set(r['Class'] for r in sel))
    if CLASS_INTERCEPTS and len(classes) > 1:  # one intercept per class, one shared slope
        X = np.column_stack([X] + [np.array([r['Class'] == c for r in sel], float) for c in classes[1:]])
    fam = sm.families.Binomial(link=link)
    # proportions with binomial weights n: Pearson chi2 / df is the usual quasi-binomial scale
    m = sm.GLM(y / n, X, family=fam, var_weights=n).fit(scale='X2')
    b, se = m.params[1], m.bse[1]
    return len(sel), y.sum(), n.sum(), b, b - 1.96 * se, b + 1.96 * se, m.scale

ok = [r for r in rows if r['adult_weight(g)'] not in ('', '-1') and float(r['adult_weight(g)']) > 0
      and float(r['RecordsWithDenominators']) >= MIN]
print(f"species with adult mass and >= {MIN} records: {len(ok)}")
groups = {'Mammalia': [r for r in ok if r['Class'] == 'Mammalia'],
          'Aves': [r for r in ok if r['Class'] == 'Aves'],
          'Mammalia+Aves': [r for r in ok if r['Class'] in ('Mammalia', 'Aves')],
          'Reptilia': [r for r in ok if r['Class'] == 'Reptilia'],
          'Amphibia': [r for r in ok if r['Class'] == 'Amphibia']}
links = {'cloglog': sm.families.links.CLogLog(), 'logit': sm.families.links.Logit()}
print("group          outcome    link     species  events/records   slope per ln(mass)  95% CI (quasi)   dispersion")
for g, sel in groups.items():
    if len(sel) < 10:
        print(f"{g:14s} only {len(sel)} species, skipped"); continue
    for out in ('neoplasia', 'malignancy'):
        for ln, lk in links.items():
            k, ys, ns, b, lo, hi, sc = fit(sel, out, lk)
            print(f"{g:14s} {out:10s} {ln:8s} {k:7d}  {int(ys):6d}/{int(ns):6d}   {b:8.3f}        [{lo:6.3f}, {hi:6.3f}]   {sc:6.2f}")
# What the naive model predicts across the mammal mass range, and what the fit gives
mam = groups['Mammalia']
masses = sorted(float(r['adult_weight(g)']) for r in mam)
lo_m, hi_m = masses[0], masses[-1]
k, ys, ns, b, lo, hi, sc = fit(mam, 'neoplasia', links['cloglog'])
print(f"mammal mass range {lo_m:g} g to {hi_m:g} g: ratio {hi_m/lo_m:.3g}")
print(f"hazard ratio largest/smallest: naive (slope 1) {hi_m/lo_m:.3g}; fitted (slope {b:.3f}) {(hi_m/lo_m)**b:.3g}")
