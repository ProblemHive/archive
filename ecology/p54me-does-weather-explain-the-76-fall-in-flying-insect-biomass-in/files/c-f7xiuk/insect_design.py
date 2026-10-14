# insect_design.py - Hallmann et al. 2017 (PLoS ONE e0185809) open data: sampling design and
# how the linear time trend in log daily biomass depends on how location enters the model.
# Needs numpy only. Input: S1 Dataset (journal.pone.0185809.s004) and S2 Dataset (.s005) saved as CSV.
import csv, collections, copy
import numpy as np

S1 = list(csv.DictReader(open('S1_Dataset.csv', encoding='utf8')))
wx = collections.defaultdict(list)
for r in csv.DictReader(open('S2_Dataset.csv', encoding='utf8')):
    wx[r['potID']].append(r)

rows = []
for r in S1:
    days = float(r['to.daynr']) - float(r['from.daynr']) + 1
    b = float(r['biomass']) if r['biomass'] != 'NA' else 0.0
    w = wx[r['potID']]
    if b <= 0 or not w:
        continue
    f = lambda k: float(np.mean([float(x[k]) for x in w]))
    rows.append(dict(plot=r['plot'], year=int(r['year']), day=float(r['mean.daynr']), y=np.log(b / days),
                     temp=f('temperature'), prec=f('precipitation'), wind=f('wind.speed'),
                     frost=f('frostdays'), precw=f('sum.precW')))
print('samples in S1:', len(S1), ' used (biomass > 0 and weather rows present):', len(rows))

# ---- design
years_by_plot = collections.defaultdict(set)
for r in rows: years_by_plot[r['plot']].add(r['year'])
ny = collections.Counter(len(v) for v in years_by_plot.values())
print('locations:', len(years_by_plot), ' location-years:', sum(len(v) for v in years_by_plot.values()))
print('locations by number of years sampled:', dict(sorted(ny.items())))
multi = {p for p, v in years_by_plot.items() if len(v) > 1}
spans = sorted(max(v) - min(v) for p, v in years_by_plot.items() if p in multi)
print('resampled locations:', len(multi), ' span between first and last year: min', spans[0], 'median', spans[len(spans)//2], 'max', spans[-1])
first = collections.Counter((min(v) - 1989) // 7 for v in years_by_plot.values())
print('locations by year first sampled: 1989-95:', first[0], ' 1996-2002:', first[1], ' 2003-09:', first[2], ' 2010-16:', first[3])
per = collections.Counter()
for p, v in years_by_plot.items():
    for y in v: per[(y - 1989) // 7] += 1
print('location-years per period:   1989-95:', per[0], ' 1996-2002:', per[1], ' 2003-09:', per[2], ' 2010-16:', per[3])
single = [min(v) for p, v in years_by_plot.items() if p not in multi]
print('single-year locations: n =', len(single), ' mean year', round(float(np.mean(single)), 1))

# ---- models
def fit(data, weather, fe, label):
    plots = sorted({r['plot'] for r in data})
    idx = {p: i for i, p in enumerate(plots)}
    y = np.array([r['y'] for r in data])
    d = np.array([(r['day'] - 200) / 50 for r in data])
    cols = [np.array([r['year'] - 2000 for r in data], float), d, d ** 2, d ** 3]
    if weather:
        for k in ('temp', 'prec', 'wind', 'frost', 'precw'):
            v = np.array([r[k] for r in data]); cols.append((v - v.mean()) / v.std())
    X = np.column_stack(cols)
    g = np.array([idx[r['plot']] for r in data])
    if fe:   # location fixed effects: subtract location means (within estimator)
        for M in (X, y.reshape(-1, 1)):
            for i in range(len(plots)):
                m = g == i; M[m] -= M[m].mean(axis=0)
    else:
        X = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    XtXi = np.linalg.inv(X.T @ X)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for i in range(len(plots)):                      # cluster-robust by location
        m = g == i; s = X[m].T @ res[m]; meat += np.outer(s, s)
    G = len(plots); V = XtXi @ meat @ XtXi * G / (G - 1)
    j = 0 if fe else 1
    b, se = beta[j], np.sqrt(V[j, j])
    print(f'{label:58s} n={len(y):4d} loc={G:2d}  year coef {b:+.4f} +- {se:.4f}  = {100*(np.exp(b)-1):+.1f}%/yr [{100*(np.exp(b-1.96*se)-1):+.1f}, {100*(np.exp(b+1.96*se)-1):+.1f}]  27-yr change {100*(np.exp(27*b)-1):+.0f}%')

print()
print('log(daily biomass) ~ year + cubic in day of year [+ weather] [+ location]; standard errors clustered by location')
for weather in (False, True):
    wl = 'with weather' if weather else 'no weather  '
    fit(copy.deepcopy(rows), weather, False, f'A pooled, no location term, {wl}')
    fit(copy.deepcopy(rows), weather, True,  f'B location fixed effects, {wl}')
    fit(copy.deepcopy([r for r in rows if r["plot"] in multi]), weather, False, f'C resampled locations only, pooled, {wl}')
    fit(copy.deepcopy([r for r in rows if r["plot"] not in multi]), weather, False, f'D single-year locations only, pooled, {wl}')
