# sae_seeds.py - toy test of seed dependence in sparse autoencoders (SAEs) when the true features are known.
# Data: x = sum of a few of n_true fixed random unit directions in R^d (each active with probability p,
# coefficient uniform in [0.5, 1.5]). SAE: f = relu(W_enc (x - b_dec) + b_enc), xhat = W_dec f + b_dec,
# loss = mean |x - xhat|^2 + lam * mean sum_i f_i * |W_dec[:, i]|  (L1 penalty weighted by decoder norm).
# Two SAEs are trained on the same data stream and differ only in the seed of their initial weights.
# "Shared" follows Paulo & Belrose (arXiv:2501.16615): one-to-one matching (Hungarian algorithm) on decoder
# directions and, separately, on encoder directions; a latent is shared if it has the same partner in both
# matchings and cosine similarity >= 0.7 in both. Dead latents (never active on the test batch) are excluded
# from the percentages but reported. Needs numpy and scipy.
import sys, time
import numpy as np
from scipy.optimize import linear_sum_assignment

D, N_TRUE, P = 64, 256, 0.02          # 256 features in 64 dimensions; about 5 active per sample
STEPS, BATCH, LR, LAM = 8000, 512, 2e-3, 0.3

def unit_cols(M):
    return M / np.linalg.norm(M, axis=0, keepdims=True)

def sample(rng, F, n):
    act = (rng.random((n, N_TRUE)) < P) * rng.uniform(0.5, 1.5, (n, N_TRUE))
    return act @ F.T

def train(F, m, init_seed, data_seed):
    rng_i = np.random.default_rng(init_seed)
    rng_d = np.random.default_rng(data_seed)
    Wd = unit_cols(rng_i.standard_normal((D, m))) * 0.3
    We = Wd.T.copy()
    be = np.zeros(m); bd = np.zeros(D)
    params = [We, be, Wd, bd]
    mom = [np.zeros_like(q) for q in params]; var = [np.zeros_like(q) for q in params]
    for t in range(1, STEPS + 1):
        x = sample(rng_d, F, BATCH)
        pre = (x - bd) @ We.T + be
        f = np.maximum(pre, 0)
        err = f @ Wd.T + bd - x
        norms = np.linalg.norm(Wd, axis=0)
        g_xhat = 2 * err / BATCH
        g_Wd = g_xhat.T @ f + LAM * (f.sum(0) / BATCH) * Wd / norms
        g_f = g_xhat @ Wd + LAM * norms / BATCH
        g_pre = g_f * (pre > 0)
        g_We = g_pre.T @ (x - bd)
        g_be = g_pre.sum(0)
        g_bd = g_xhat.sum(0) - g_pre.sum(0) @ We
        for q, g, m1, v1 in zip(params, [g_We, g_be, g_Wd, g_bd], mom, var):
            m1 *= 0.9; m1 += 0.1 * g
            v1 *= 0.999; v1 += 0.001 * g * g
            q -= LR * (m1 / (1 - 0.9 ** t)) / (np.sqrt(v1 / (1 - 0.999 ** t)) + 1e-8)
    return We, be, Wd, bd

def evaluate(F, sae, x):
    We, be, Wd, bd = sae
    f = np.maximum((x - bd) @ We.T + be, 0)
    err = f @ Wd.T + bd - x
    fvu = (err ** 2).sum() / ((x - x.mean(0)) ** 2).sum()
    alive = (f > 0).any(0)
    l0 = (f > 0).sum(1).mean()
    return fvu, l0, alive

def shared_mask(a, b, alive_a, alive_b):
    # a, b: (We, Wd) of two SAEs; returns mask over a's latents
    Da, Db = unit_cols(a[1]), unit_cols(b[1])
    Ea, Eb = unit_cols(a[0].T), unit_cols(b[0].T)
    cd = Da.T @ Db; ce = Ea.T @ Eb
    rd, cdm = linear_sum_assignment(-cd); re, cem = linear_sum_assignment(-ce)
    pd = np.empty(len(rd), int); pd[rd] = cdm
    pe = np.empty(len(re), int); pe[re] = cem
    idx = np.arange(len(pd))
    ok = (pd == pe) & (cd[idx, pd] >= 0.7) & (ce[idx, pe] >= 0.7) & alive_a & alive_b[pd]
    return ok

if __name__ == '__main__':
    sizes = [int(s) for s in sys.argv[1:]]
    F = unit_cols(np.random.default_rng(0).standard_normal((D, N_TRUE)))
    xt = sample(np.random.default_rng(999), F, 20000)
    print(f'd={D}, true features={N_TRUE}, P(active)={P}, steps={STEPS}, batch={BATCH}, lr={LR}, lam={LAM}')
    print('  m   FVU(A)  FVU(B)   L0   alive(A)  shared%  true feats found A / B / by both (cos>=0.9)  shared latents on a true feat%  unshared on a true feat%   time')
    for m in sizes:
        t0 = time.time()
        A = train(F, m, 1, 100); B = train(F, m, 2, 100)
        fa, l0, alA = evaluate(F, A, xt); fb, _, alB = evaluate(F, B, xt)
        sh = shared_mask((A[0], A[2]), (B[0], B[2]), alA, alB)
        cA = np.abs(F.T @ unit_cols(A[2])); cB = np.abs(F.T @ unit_cols(B[2]))
        cA[:, ~alA] = 0; cB[:, ~alB] = 0
        foundA = cA.max(1) >= 0.9; foundB = cB.max(1) >= 0.9
        on_true = cA.max(0) >= 0.9                        # latent of A aligned with some true feature
        un = alA & ~sh
        print(f'{m:4d}  {fa:.4f}  {fb:.4f}  {l0:5.1f}  {alA.sum():5d}    {100*sh.sum()/alA.sum():5.1f}   '
              f'{foundA.sum():4d} / {foundB.sum():4d} / {(foundA & foundB).sum():4d}                 '
              f'{100*on_true[sh].mean() if sh.any() else float("nan"):5.1f}                        '
              f'{100*on_true[un].mean() if un.any() else float("nan"):5.1f}            {time.time()-t0:4.0f}s', flush=True)
