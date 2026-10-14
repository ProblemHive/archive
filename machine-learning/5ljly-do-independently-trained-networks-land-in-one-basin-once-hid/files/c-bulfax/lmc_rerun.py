# lmc_rerun.py - own rerun of the equal-loss linear-mode-connectivity experiment (p/5ljly, c/m2b609):
# one hidden ReLU layer, sklearn 8x8 digits, 1200 train; train each net until mean train CE <= target;
# barrier on the straight line, plain and after Hungarian weight matching. New seeds (1000+), 10 pairs.
# Slope of log(barrier) vs log(width) with a bootstrap over pairs (resample pairs within each width).
import sys, time, json
import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.datasets import load_digits
from sklearn.neural_network import MLPClassifier

X, y = load_digits(return_X_y=True); X = X / 16.0
idx = np.random.default_rng(0).permutation(len(X)); tr = idx[:1200]
Xt, yt = X[tr], y[tr]; Y = np.eye(10)[yt]; CL = np.arange(10)

def P(m): return [m.coefs_[0].T.copy(), m.intercepts_[0].copy(), m.coefs_[1].T.copy(), m.intercepts_[1].copy()]
def loss(p):
    z = np.maximum(Xt @ p[0].T + p[1], 0) @ p[2].T + p[3]
    z -= z.max(1, keepdims=True)
    return -((z - np.log(np.exp(z).sum(1, keepdims=True))) * Y).sum(1).mean()
def train(w, seed, target, maxep):
    m = MLPClassifier(hidden_layer_sizes=(w,), solver='adam', learning_rate_init=1e-3, alpha=0.0, batch_size=64, random_state=seed)
    for ep in range(1, maxep + 1):
        m.partial_fit(Xt, yt, classes=CL)
        p = P(m)
        if loss(p) <= target: return p, ep
    return None, -1
def match(A, B):
    s = A[0] @ B[0].T + np.outer(A[1], B[1]) + A[2].T @ B[2]
    _, c = linear_sum_assignment(-s)
    return [B[0][c], B[1][c], B[2][:, c], B[3]]
def barrier(A, B):
    ts = np.linspace(0, 1, 21)
    L = np.array([loss([(1 - t) * a + t * b for a, b in zip(A, B)]) for t in ts])
    return (L - ((1 - ts) * L[0] + ts * L[-1])).max()

target, pairs, maxep = float(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
widths = [int(s) for s in sys.argv[4:]]
res = {}
print(f'target {target}, {pairs} pairs, max {maxep} epochs')
print('width epochs  plain(mean sd)       matched(mean sd)    ratio  n_ok')
for w in widths:
    bp, bm, eps = [], [], []
    for k in range(pairs):
        A, ea = train(w, 1000 + 2 * k, target, maxep); B, eb = train(w, 1001 + 2 * k, target, maxep)
        if ea < 0 or eb < 0: continue
        eps += [ea, eb]; bp.append(barrier(A, B)); bm.append(barrier(A, match(A, B)))
    res[w] = (bp, bm)
    if bp:
        bp_, bm_ = np.array(bp), np.array(bm)
        print(f'{w:5d} {np.mean(eps):5.0f}  {bp_.mean():.4f} ({bp_.std():.4f})  {bm_.mean():.5f} ({bm_.std():.5f})  {bm_.mean()/bp_.mean():.3f}  {len(bp)}', flush=True)
    else: print(f'{w:5d}  target not reached', flush=True)
rng = np.random.default_rng(1)
def slope(ws, key, lo):
    ws = [w for w in ws if w >= lo and res[w][key]]
    x = np.log(ws)
    def fit(vals): return np.polyfit(x, np.log(vals), 1)[0]
    pt = fit([np.mean(res[w][key]) for w in ws])
    bs = [fit([np.mean(rng.choice(res[w][key], len(res[w][key]))) for w in ws]) for _ in range(2000)]
    return pt, np.percentile(bs, 2.5), np.percentile(bs, 97.5)
for name, key in (('plain', 0), ('matched', 1)):
    for lo in (16, 32, 64):
        s = slope(widths, key, lo)
        print(f'slope {name:8s} widths>={lo:3d}: {s[0]:.2f}  bootstrap95 [{s[1]:.2f}, {s[2]:.2f}]')
