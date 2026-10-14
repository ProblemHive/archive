# horizon_refit.py - refit METR's 50% time horizons and the doubling time from the public run data.
# Input (not redistributed here; the repository has no licence file):
#   https://github.com/METR/eval-analysis-public  reports/time-horizon-1-1/data/raw/runs.jsonl  -> th11_runs.jsonl
#   and data/external/release_dates.yaml -> release_dates.yaml
# Needs numpy only. Method: per model, weighted logistic regression of success on log2(human minutes)
# (weights: invsqrt_task_weight, as in METR's pipeline; a small ridge penalty 0.01 on both coefficients for stability, my choice);
# horizon = task length at which the fitted success probability is 50%. Then ordinary least squares of
# log2(horizon) on release date. Confidence intervals: bootstrap over task families (500 resamples).
import json, datetime, collections
import numpy as np

rng = np.random.default_rng(1)
dates = {}
for line in open('release_dates.yaml', encoding='utf8'):
    if ':' in line and line.startswith('  '):
        k, v = line.rsplit(':', 1); dates[k.strip()] = datetime.date.fromisoformat(v.strip())

runs = collections.defaultdict(list)
for l in open('th11_runs.jsonl', encoding='utf8'):
    r = json.loads(l)
    if r['alias'] == 'human' or r['human_minutes'] is None: continue
    runs[r['alias']].append((r['task_family'], np.log2(r['human_minutes']), r['score_binarized'], r['invsqrt_task_weight']))
families = sorted({f for v in runs.values() for f, *_ in v})
print('models:', len(runs), ' task families:', len(families), ' tasks:', len({json.loads(l)['task_id'] for l in open('th11_runs.jsonl', encoding='utf8')}))

def horizon(x, y, w):
    """minutes at which P(success) = 0.5; weighted logistic fit by Newton steps"""
    w = w / w.sum() * len(w)
    X = np.column_stack([np.ones(len(x)), x]); b = np.zeros(2)
    for _ in range(50):
        p = 1 / (1 + np.exp(-X @ b))
        g = X.T @ (w * (y - p)) - 0.01 * b
        H = (X * (w * p * (1 - p))[:, None]).T @ X + 0.01 * np.eye(2)
        step = np.linalg.solve(H, g); b += step
        if np.abs(step).max() < 1e-10: break
    return -b[0] / b[1], b[1]            # log2(minutes) at 50%, slope

arr = {m: (np.array([families.index(f) for f, *_ in v]), np.array([t[1] for t in v]), np.array([t[2] for t in v], float), np.array([t[3] for t in v])) for m, v in runs.items()}
order = sorted(arr, key=lambda m: dates[m])
t = np.array([(dates[m] - datetime.date(2023, 1, 1)).days for m in order], float)

def all_horizons(fam_counts=None):
    out = []
    for m in order:
        f, x, y, w = arr[m]
        ww = w if fam_counts is None else w * fam_counts[f]
        keep = ww > 0
        out.append(horizon(x[keep], y[keep], ww[keep])[0])
    return np.array(out)

def doubling(h, mask):
    slope = np.polyfit(t[mask], h[mask], 1)[0]     # doublings per day
    return 1 / slope

h0 = all_horizons()
record = np.array([h0[i] > h0[:i].max() if i else True for i in range(len(order))])   # set a new record when released
windows = {
    'all 20 models, 2023-03 to 2026-02': np.ones(len(order), bool),
    'released 2024 or later': t >= 365,
    'released 2025 or later': t >= 731,
    'record-setting models only': record,
    'record-setting, 2024 or later': record & (t >= 365),
    'released before 2026 (as available at TH1.1 post)': t < 1096,
    '2024 or later, released before 2026': (t >= 365) & (t < 1096),
}
boot = []
for _ in range(500):
    c = np.bincount(rng.integers(0, len(families), len(families)), minlength=len(families)).astype(float)
    try: boot.append(all_horizons(c))
    except np.linalg.LinAlgError: pass
boot = np.array(boot); boot = boot[np.isfinite(boot).all(axis=1)]
print('bootstrap resamples used:', len(boot))
print()
print(f"{'model':36s} {'released':10s} {'runs':>5s} {'50% horizon':>12s}  95% interval (minutes)   record")
for i, m in enumerate(order):
    lo, hi = np.percentile(boot[:, i], [2.5, 97.5])
    print(f'{m:36s} {dates[m].isoformat():10s} {len(arr[m][1]):5d} {2**h0[i]:9.1f} min  [{2**lo:7.1f}, {2**hi:8.1f}]   {"yes" if record[i] else ""}')
print()
print(f"{'window':52s} {'n':>2s}  doubling time, days [95% interval]")
for name, mask in windows.items():
    d = doubling(h0, mask); bs = np.array([doubling(b, mask) for b in boot]); lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f'{name:52s} {mask.sum():2d}  {d:6.1f}  [{lo:6.1f}, {hi:6.1f}]')
print()
print('leave one model out, window "released 2024 or later":')
m24 = t >= 365
for i in np.where(m24)[0]:
    mk = m24.copy(); mk[i] = False
    print(f'  without {order[i]:36s} {doubling(h0, mk):6.1f} days')
print()
print('share of runs on tasks longer than a model\'s own 50% horizon, three newest record models:')
for i in np.where(record)[0][-3:]:
    f, x, y, w = arr[order[i]]
    print(f'  {order[i]:32s} horizon {2**h0[i]:7.1f} min; runs above it: {int((x > h0[i]).sum())} of {len(x)} ({len(set(zip(f[x > h0[i]], x[x > h0[i]])))} distinct task lengths); success there {y[x > h0[i]].mean():.2f}')
