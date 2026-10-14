# baseline_refit.py - refit 50% time horizons from METR TH1.1 public runs, all tasks vs tasks with measured (baseline) human times only
import json, sys, datetime, collections
import numpy as np
rng = np.random.default_rng(1)
dates = {}
for line in open(sys.argv[2], encoding='utf8'):
    if ':' in line and line.startswith('  '):
        k, v = line.rsplit(':', 1); dates[k.strip()] = datetime.date.fromisoformat(v.strip())
rows = []
for l in open(sys.argv[1], encoding='utf8'):
    r = json.loads(l)
    if r['alias'] == 'human' or r['human_minutes'] is None: continue
    rows.append(r)
fams = sorted({r['task_family'] for r in rows}); fi = {f: i for i, f in enumerate(fams)}
models = sorted({r['alias'] for r in rows}, key=lambda m: dates[m])
def build(sel):
    d = {}
    for m in models:
        rr = [r for r in rows if r['alias'] == m and sel(r)]
        d[m] = (np.array([fi[r['task_family']] for r in rr]), np.log2([r['human_minutes'] for r in rr]),
                np.array([r['score_binarized'] for r in rr], float), np.array([r['invsqrt_task_weight'] for r in rr]))
    return d
def horizon(x, y, w):
    w = w / w.sum() * len(w); X = np.column_stack([np.ones(len(x)), x]); b = np.zeros(2)
    for _ in range(50):
        p = 1 / (1 + np.exp(-X @ b)); g = X.T @ (w * (y - p)) - 0.01 * b
        H = (X * (w * p * (1 - p))[:, None]).T @ X + 0.01 * np.eye(2)
        s = np.linalg.solve(H, g); b += s
        if np.abs(s).max() < 1e-10: break
    return -b[0] / b[1]
t = np.array([(dates[m] - datetime.date(2023, 1, 1)).days for m in models], float)
def hs(d, c=None):
    out = []
    for m in models:
        f, x, y, w = d[m]; ww = w if c is None else w * c[f]; k = ww > 0
        out.append(horizon(x[k], y[k], ww[k]))
    return np.array(out)
def dbl(h, mask): return 1 / np.polyfit(t[mask], h[mask], 1)[0]
wins = {'all models': np.ones(len(models), bool), '2024+': t >= 365, '2025+': t >= 731}
for name, sel in [('all 228 tasks', lambda r: True), ('measured human time only', lambda r: r['human_source'] == 'baseline'),
                  ('estimated human time only', lambda r: r['human_source'] == 'estimate')]:
    d = build(sel); h0 = hs(d)
    nt = len({(r['task_id']) for r in rows if sel(r)})
    boot = []
    for _ in range(500):
        c = np.bincount(rng.integers(0, len(fams), len(fams)), minlength=len(fams)).astype(float)
        try: boot.append(hs(d, c))
        except np.linalg.LinAlgError: pass
    boot = np.array(boot); boot = boot[np.isfinite(boot).all(1)]
    print(f'\n== {name}: {nt} tasks, {len(boot)} bootstrap fits')
    for n, mk in wins.items():
        lo, hi = np.percentile([dbl(b, mk) for b in boot], [2.5, 97.5])
        print(f'  {n:11s} n={mk.sum():2d} doubling {dbl(h0, mk):7.1f} days [{lo:7.1f}, {hi:7.1f}]')
    if 'measured' in name or 'all' in name:
        for i in range(-4, 0):
            lo, hi = np.percentile(boot[:, i], [2.5, 97.5]); print(f'  {models[i]:30s} {2**h0[i]:8.1f} min [{2**lo:7.1f}, {2**hi:9.1f}]')

