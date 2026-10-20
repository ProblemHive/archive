# recover.py - how many true features does a sparse autoencoder (SAE) recover on a toy with known features?
# Data: x = sum_i a_i F_i, F_i fixed random unit directions in R^D (N_TRUE of them), a_i = 0 with probability 1-P,
# else uniform in [0.5, 1.5]. SAE: one hidden layer of M latents, ReLU or TopK(K), trained with Adam on fresh samples.
# Recovered true feature = some alive latent whose decoder column has cosine >= 0.9 with it.
# Reported with fraction of variance unexplained (FVU) on 20000 held-out samples, so that "recovery at X% explained
# variance" can be read off. One seed per setting. Not a language model.
# usage: python recover.py N_TRUE P_TIMES_N M_FACTOR   (P = P_TIMES_N / N_TRUE, so P_TIMES_N is the mean number of active features)
import sys, time
import numpy as np, torch

D = 64
STEPS, BATCH, LR, LAM = 6000, 512, 2e-3, 0.3
dev = 'cuda' if torch.cuda.is_available() else 'cpu'

def unit_cols(M):
    return M / M.norm(dim=0, keepdim=True)

def sample(gen, F, n, P):
    N = F.shape[1]
    act = (torch.rand(n, N, generator=gen, device=dev) < P) * (0.5 + torch.rand(n, N, generator=gen, device=dev))
    return act @ F.T

def encode(arch, K, p, x):
    We, be, Wd, bd = p
    f = torch.relu((x - bd) @ We.T + be)
    if arch == 'topk':
        v, i = f.topk(K, dim=1)
        f = torch.zeros_like(f).scatter_(1, i, v)
    return f

def run(arch, N, mean_active, mfac, seed=1):
    P = mean_active / N
    M = int(mfac * N)
    K = max(1, int(round(mean_active)))
    F = unit_cols(torch.randn(D, N, generator=torch.Generator().manual_seed(0))).to(dev)
    g = torch.Generator(device='cpu').manual_seed(seed)
    Wd = (unit_cols(torch.randn(D, M, generator=g)) * (0.3 if arch == 'relu' else 1.0)).to(dev)
    p = [Wd.T.clone().requires_grad_(), torch.zeros(M, device=dev, requires_grad=True), Wd.requires_grad_(),
         torch.zeros(D, device=dev, requires_grad=True)]
    opt = torch.optim.Adam(p, lr=LR)
    gen = torch.Generator(device=dev).manual_seed(100)
    for _ in range(STEPS):
        x = sample(gen, F, BATCH, P)
        f = encode(arch, K, p, x)
        loss = ((f @ p[2].T + p[3] - x) ** 2).sum(1).mean()
        if arch == 'relu':
            loss = loss + LAM * (f * p[2].norm(dim=0)).sum(1).mean()
        opt.zero_grad(); loss.backward(); opt.step()
        if arch == 'topk':
            with torch.no_grad():
                p[2].copy_(unit_cols(p[2]))
    p = [q.detach() for q in p]
    xt = sample(torch.Generator(device=dev).manual_seed(999), F, 20000, P)
    f = encode(arch, K, p, xt)
    err = f @ p[2].T + p[3] - xt
    fvu = float((err ** 2).sum() / ((xt - xt.mean(0)) ** 2).sum())
    alive = (f > 0).any(0)
    c = (F.T @ unit_cols(p[2])) * alive[None, :]
    found = float((c.max(1).values >= 0.9).float().mean())
    return fvu, float((f > 0).sum(1).float().mean()), int(alive.sum()), found

if __name__ == '__main__':
    N = int(sys.argv[1]); act = float(sys.argv[2]); mfac = float(sys.argv[3])
    for arch in ('relu', 'topk'):
        t0 = time.time()
        fvu, l0, alive, found = run(arch, N, act, mfac)
        print(f'{arch:5s} true={N:5d} active/sample={act:4.1f} M={int(mfac*N):5d} FVU={fvu:.3f} explained={1-fvu:.3f} L0={l0:5.1f} alive={alive:5d} true features found={found:.3f}  {time.time()-t0:.0f}s', flush=True)

