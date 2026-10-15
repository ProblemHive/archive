# meanrec.py - the scalar version of accum.py's "fresh" scheme, simulated exactly through batch means.
# Estimate a mean mu = 0 (unit-variance noise). Generation n adds r*B real samples and B synthetic samples drawn from
# N(m_{n-1}, 1), where m_{n-1} is the previous generation's estimate; m_n is the mean of everything accumulated.
# Batch sums are drawn directly (sum of k unit normals = sqrt(k) * N(0,1)), so large n is cheap.
# Heuristic prediction (see the comment): E m_n^2 ~ n^(-1) if r > 1, (log n)/n if r = 1, n^(-2r/(1+r)) if r < 1.
# usage: python meanrec.py
import numpy as np

rng = np.random.default_rng(2026)
B, N, reps = 100, 20000, 2000
checkpoints = [100, 1000, 10000, 20000]
print(f"B={B} generations={N} reps={reps} seed=2026 numpy {np.__version__}")
for r in (0.25, 0.5, 1.0, 2.0):
    R = r * B
    m = rng.standard_normal(reps) / np.sqrt(R)          # generation 1: real data only
    tot_sum, tot_n = m * R, R
    out = {}
    for n in range(2, N + 1):
        real = rng.standard_normal(reps) * np.sqrt(R)
        syn = m * B + rng.standard_normal(reps) * np.sqrt(B)
        tot_sum = tot_sum + real + syn; tot_n += R + B
        m = tot_sum / tot_n
        if n in checkpoints:
            out[n] = np.mean(m ** 2)
    pred = -1.0 if r > 1 else (-1.0 if r == 1 else -2 * r / (1 + r))
    line = "  ".join(f"n={n}: {out[n]:.3e} (x real-only {out[n] * n * R:.2f})" for n in checkpoints)
    slope = np.polyfit(np.log(checkpoints[1:]), np.log([out[n] for n in checkpoints[1:]]), 1)[0]
    print(f"r={r:4.2f}  {line}\n          fitted exponent n=1000..20000: {slope:.3f}   predicted {pred:.3f}{' (with a log factor)' if r == 1 else ''}")
