# accum.py - self-consuming linear regression, Monte Carlo, numpy only.
# Setting (Gerstgrasser et al. 2024, arXiv:2404.01413, Theorem 2): d features, isotropic Gaussian X, y = X w* + N(0, s^2).
# Generation 1 fits OLS on T real samples. Generation n >= 2 labels new inputs with the previous model plus fresh noise
# and refits OLS on everything accumulated. Test error = |w_hat - w*|^2 (isotropic features).
# Scheme "fixed": the real set stays the same T samples; each generation adds T synthetic samples on the SAME inputs X
#   (as in the theorem). Prediction: s^2 d/(T-d-1) * sum_{i<=n} 1/i^2.
# Scheme "fresh": each generation adds T new real samples AND T synthetic samples on new inputs.
#   Compared with OLS on the n*T real samples alone. The question: does the ratio stay bounded, and at what value?
# Scheme "fresh-r": as "fresh" but only T*r new real samples per generation (r < 1) and T synthetic.
# usage: python accum.py
import numpy as np

rng = np.random.default_rng(12345)
d, T, s, N, reps = 20, 60, 1.0, 40, 400


def ols(X, y):
    return np.linalg.lstsq(X, y, rcond=None)[0]


def run_fixed():
    err = np.zeros(N)
    for _ in range(reps):
        w = rng.standard_normal(d)
        X = rng.standard_normal((T, d))
        Xs, ys = [X], [X @ w + s * rng.standard_normal(T)]
        wh = ols(X, ys[0]); err[0] += np.sum((wh - w) ** 2)
        for n in range(1, N):
            Xs.append(X); ys.append(X @ wh + s * rng.standard_normal(T))
            wh = ols(np.vstack(Xs), np.concatenate(ys)); err[n] += np.sum((wh - w) ** 2)
    return err / reps


def run_fresh(r):
    err, ref = np.zeros(N), np.zeros(N)
    Tr = int(round(T * r))
    for _ in range(reps):
        w = rng.standard_normal(d)
        X = rng.standard_normal((T, d)); y = X @ w + s * rng.standard_normal(T)
        RX, Ry = [X], [y]
        wh = ols(X, y); err[0] += np.sum((wh - w) ** 2); ref[0] += np.sum((wh - w) ** 2)
        SX, Sy = [], []
        for n in range(1, N):
            Xr = rng.standard_normal((Tr, d)); RX.append(Xr); Ry.append(Xr @ w + s * rng.standard_normal(Tr))
            Xn = rng.standard_normal((T, d)); SX.append(Xn); Sy.append(Xn @ wh + s * rng.standard_normal(T))
            wr = ols(np.vstack(RX), np.concatenate(Ry)); ref[n] += np.sum((wr - w) ** 2)
            wh = ols(np.vstack(RX + SX), np.concatenate(Ry + Sy)); err[n] += np.sum((wh - w) ** 2)
    return err / reps, ref / reps


base = s ** 2 * d / (T - d - 1)
ef = run_fixed()
print(f"d={d} T={T} sigma={s} generations={N} reps={reps} seed=12345 numpy {np.__version__}")
print("scheme fixed: error / (s^2 d/(T-d-1)) against the formula sum 1/i^2")
for n in (1, 2, 3, 5, 10, 20, 40):
    print(f"  n={n:2d}  simulated {ef[n-1]/base:.3f}   formula {sum(1/i**2 for i in range(1, n+1)):.3f}")
for r in (1.0, 0.25):
    e, ref = run_fresh(r)
    print(f"scheme fresh, real per generation = {r:g} T, synthetic per generation = T: error ratio self-consuming / real-only")
    for n in (1, 2, 3, 5, 10, 20, 40):
        print(f"  n={n:2d}  self-consuming {e[n-1]:.4f}  real-only {ref[n-1]:.4f}  ratio {e[n-1]/ref[n-1]:.3f}")
