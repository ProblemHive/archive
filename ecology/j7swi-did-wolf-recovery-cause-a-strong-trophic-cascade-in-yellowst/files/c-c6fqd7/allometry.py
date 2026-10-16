# allometry.py - what the Kauffman-Cummings willow data say about crown volume and height.
# Data: figshare 10.6084/m9.figshare.27905172 (v3), file 'Database for Figshare 2024.xlsx' (CC BY 4.0).
# Volume in the file is a half-ellipsoid: V = (4/3 * pi * W1/2 * W2/2 * H) / 2 = pi * W1 * W2 * H / 6,
# so ln V = ln(pi/6) + ln(W1*W2) + ln H. The only information on how crowns scale with height is in
# the regression of ln(W1*W2) on ln H; the regression of ln V on ln H contains ln H on both sides.
# Usage: python allometry.py /data/wolfwillow/kauffman_cummings_2024.xlsx
import sys, math, random
import numpy as np
from xlsx_min import sheets

rows = []
for name, rs in sheets(sys.argv[1]):
    for n, r in rs:
        if isinstance(r.get('A'), float) and isinstance(r.get('D'), float):
            rows.append(dict(plant=int(r['A']), site=r.get('B'), sp=r.get('C'), H=r['D'], W1=r['E'], W2=r['F'], V=r.get('H')))
    break
print("plants:", len(rows))
sp = {}
for r in rows:
    sp[r['sp']] = sp.get(r['sp'], 0) + 1
print("species codes:", sorted(sp.items(), key=lambda x: -x[1]))
st = {}
for r in rows:
    st[r['site']] = st.get(r['site'], 0) + 1
print("sites:", sorted(st.items(), key=lambda x: -x[1]))
# check the volume formula
err = max(abs(r['V'] - math.pi * r['W1'] * r['W2'] * r['H'] / 6) / r['V'] for r in rows)
print("max relative difference between file volume and pi*W1*W2*H/6: %.2e" % err)

def fit(x, y):
    x, y = np.asarray(x), np.asarray(y)
    A = np.vstack([np.ones_like(x), x]).T
    coef, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = A @ coef
    r2 = 1 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    s = math.sqrt(((y - yhat) ** 2).sum() / (len(x) - 2))
    se_b = s / math.sqrt(((x - x.mean()) ** 2).sum())
    return coef[0], coef[1], r2, se_b, s

def report(sub, label):
    lh = [math.log(r['H'] / 100) for r in sub]                       # height in m
    lv = [math.log(math.pi * r['W1'] * r['W2'] * r['H'] / 6 / 1e6) for r in sub]   # volume in m3
    la = [math.log(r['W1'] * r['W2'] / 1e4) for r in sub]            # W1*W2 in m2
    a, b, r2, se, s = fit(lh, lv)
    a2, b2, r22, se2, s2 = fit(lh, la)
    print("%-34s n=%2d  lnV = %.4f + %.4f lnH (R2 %.3f, se slope %.3f) | ln(W1W2) = %.3f + %.3f lnH (R2 %.3f, se %.3f, resid sd %.3f)"
          % (label, len(sub), a, b, r2, se, a2, b2, r22, se2, s2))
    return b, b2

print()
b_all, b2_all = report(rows, "all plants")
report([r for r in rows if r['sp'] != 'SALU'], "without SALU (S. lutea)")
report([r for r in rows if r['site'] != 'Madison'], "without Madison (outside N. range)")
report([r for r in rows if r['H'] <= 200], "height <= 2 m")
report([r for r in rows if r['H'] > 200], "height > 2 m")

# How much R2 would lnV ~ lnH have if crown widths had nothing to do with height?
# Shuffle the (W1, W2) pairs across plants, keep the heights, recompute V, refit.
random.seed(1)
H = [r['H'] for r in rows]
WW = [(r['W1'], r['W2']) for r in rows]
r2s = []
for it in range(2000):
    random.shuffle(WW)
    lh = [math.log(h / 100) for h in H]
    lv = [math.log(math.pi * w1 * w2 * h / 6 / 1e6) for h, (w1, w2) in zip(H, WW)]
    r2s.append(fit(lh, lv)[2])
r2s.sort()
print()
print("R2 of lnV ~ lnH with crown widths shuffled across plants (2000 shuffles, seed 1): median %.3f, 95%% range %.3f to %.3f"
      % (r2s[1000], r2s[50], r2s[1949]))

# What the exponent means for a log10 response ratio of mean volume, for a lognormal height
# distribution with fixed spread: log10(mean V2/mean V1) = b * log10(GM2/GM1) + (b^2/2)(s2^2 - s1^2)/ln10.
# Ripple et al. report mean heights 92 cm (2001) and 192 cm (2020), log10 ratio 0.32 for height and 1.21 for volume.
print()
lr_h = math.log10(192 / 92)
for b in (1.0, 2.0, b_all):
    print("exponent %.3f: log10 ratio from the means alone (same spread both years) = %.3f" % (b, b * lr_h))
