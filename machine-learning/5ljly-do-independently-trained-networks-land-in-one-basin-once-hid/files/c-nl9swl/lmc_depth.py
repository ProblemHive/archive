# lmc_depth.py - loss barrier between two independently trained ReLU networks with 1, 2 or 3 hidden
# layers, before and after permuting the hidden units of one of them (weight matching), every network
# trained to the same training loss. Extends c/m2b609 (one hidden layer) of p/5ljly to deeper networks.
#
# Data: scikit-learn 8x8 digits scaled by 1/16, split as in the thread (default_rng(0) permutation,
# first 1,200 images for training). Model: fully connected, ReLU, Glorot-uniform weights, zero biases.
# Training: Adam, learning rate 1e-3, batch 64, reshuffled every epoch, no weight decay; stopped at the
# first epoch whose mean training cross-entropy (full training set) is at or below TARGET.
# Matching: for one hidden layer, one assignment problem on incoming weights, bias and outgoing weights
# (as in the thread). For more layers the same cost is minimised layer by layer with the other layers'
# permutations held fixed, sweeping until nothing improves (the weight-matching method of Ainsworth,
# Hayase and Srinivasa, "Git Re-Basin", arXiv:2209.04836). It finds a local optimum, not the best one.
# Barrier: max over t = 0, 0.05, ..., 1 of loss((1-t)A + tB) - ((1-t) loss(A) + t loss(B)), training set.
#
# Usage: python lmc_depth.py TARGET PAIRS MAX_EPOCHS DEPTHS WIDTHS   e.g. 0.02 5 3000 1,2,3 32,64,128
import sys, time
import numpy as np
import torch
from scipy.optimize import linear_sum_assignment
from sklearn.datasets import load_digits

torch.set_num_threads(2)
Xn, yn = load_digits(return_X_y=True)
Xn = Xn / 16.0
idx = np.random.default_rng(0).permutation(len(Xn))
tr = idx[:1200]
X = torch.tensor(Xn[tr], dtype=torch.float64)
y = torch.tensor(yn[tr])

def init(depth, width, seed):
    g = torch.Generator().manual_seed(seed)
    sizes = [64] + [width] * depth + [10]
    P = []
    for a, b in zip(sizes[:-1], sizes[1:]):
        lim = (6.0 / (a + b)) ** 0.5
        P.append(((torch.rand(b, a, generator=g, dtype=torch.float64) * 2 - 1) * lim).requires_grad_())
        P.append(torch.zeros(b, dtype=torch.float64, requires_grad=True))
    return P, g

def forward(P, x):
    for i in range(0, len(P) - 2, 2):
        x = torch.relu(x @ P[i].T + P[i + 1])
    return x @ P[-2].T + P[-1]

def loss_err(P):
    with torch.no_grad():
        z = forward(P, X)
        return float(torch.nn.functional.cross_entropy(z, y)), float((z.argmax(1) != y).double().mean())

def train(depth, width, seed, target, max_epochs):
    P, g = init(depth, width, seed)
    opt = torch.optim.Adam(P, lr=1e-3)
    for ep in range(1, max_epochs + 1):
        perm = torch.randperm(len(X), generator=g)
        for s in range(0, len(X), 64):
            b = perm[s:s + 64]
            opt.zero_grad()
            torch.nn.functional.cross_entropy(forward(P, X[b]), y[b]).backward()
            opt.step()
        if loss_err(P)[0] <= target:
            return [p.detach().numpy().copy() for p in P], ep
    return [p.detach().numpy().copy() for p in P], -1

def permute(B, perms):
    """apply one permutation per hidden layer to network B (a list W0, b0, W1, b1, ...)"""
    out = [p.copy() for p in B]
    for l, p in enumerate(perms):
        out[2 * l] = out[2 * l][p]
        out[2 * l + 1] = out[2 * l + 1][p]
        out[2 * l + 2] = out[2 * l + 2][:, p]
    return out

def match(A, B, seed):
    depth = len(A) // 2 - 1
    width = A[0].shape[0]
    perms = [np.arange(width) for _ in range(depth)]
    rng = np.random.default_rng(seed)
    sweeps = 0
    while True:
        sweeps += 1
        changed = False
        for l in rng.permutation(depth):
            Win = B[2 * l] if l == 0 else B[2 * l][:, perms[l - 1]]          # columns follow the layer below
            Wout = B[2 * l + 2] if l == depth - 1 else B[2 * l + 2][perms[l + 1]]   # rows follow the layer above
            sim = A[2 * l] @ Win.T + np.outer(A[2 * l + 1], B[2 * l + 1]) + A[2 * l + 2].T @ Wout
            r, c = linear_sum_assignment(-sim)
            old = sim[np.arange(width), perms[l]].sum()
            if sim[r, c].sum() > old + 1e-12:
                perms[l] = c
                changed = True
        if not changed or sweeps >= 100:
            break
    return permute(B, perms), sweeps

def barriers(A, B):
    ts = np.linspace(0, 1, 21)
    R = np.array([loss_err([torch.tensor((1 - t) * a + t * b) for a, b in zip(A, B)]) for t in ts])
    L, E = R[:, 0], R[:, 1]
    return (L - ((1 - ts) * L[0] + ts * L[-1])).max(), (E - ((1 - ts) * E[0] + ts * E[-1])).max()

def selftest():
    """a network and a randomly permuted copy of itself must match back exactly (barrier 0)"""
    for depth in (1, 2, 3):
        A, _ = train(depth, 16, 7, 0.5, 50)
        rng = np.random.default_rng(depth)
        B = permute(A, [rng.permutation(16) for _ in range(depth)])
        plain = barriers(A, B)[0]
        M, sweeps = match(A, B, 0)
        gap = max(float(np.abs(a - m).max()) for a, m in zip(A, M))
        print(f"self-test depth {depth}: barrier to a shuffled copy {plain:.3f}; after matching, largest weight difference {gap:.1e} ({sweeps} sweeps)")
        fa = float(np.abs(forward([torch.tensor(p) for p in A], X).detach().numpy() - forward([torch.tensor(p) for p in B], X).detach().numpy()).max())
        assert fa < 1e-9, "permuting hidden units changed the function"

if __name__ == "__main__":
    target, pairs, max_epochs = float(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    depths = [int(s) for s in sys.argv[4].split(",")]
    widths = [int(s) for s in sys.argv[5].split(",")]
    print(f"torch {torch.__version__}, numpy {np.__version__}; target training loss {target}; {pairs} pairs; at most {max_epochs} epochs", flush=True)
    selftest()
    table = {}
    print("depth width  epochs  end_loss   loss barrier: plain (sd)   matched (sd)   ratio   error barrier: plain  matched  sweeps  seconds", flush=True)
    for depth in depths:
        for width in widths:
            t0 = time.time()
            lp, lm, ep_, em_, eps, el, sw = [], [], [], [], [], [], []
            for k in range(pairs):
                (A, ea), (B, eb) = train(depth, width, 100 + 2 * k, target, max_epochs), train(depth, width, 101 + 2 * k, target, max_epochs)
                if ea < 0 or eb < 0:
                    continue
                eps += [ea, eb]
                el.append(loss_err([torch.tensor(p) for p in A])[0])
                a, b = barriers(A, B); lp.append(a); ep_.append(b)
                M, s = match(A, B, k); sw.append(s)
                a, b = barriers(A, M); lm.append(a); em_.append(b)
            if len(lp) < pairs:
                print(f"{depth:5d} {width:5d}  target not reached in {pairs - len(lp)} of {pairs} pairs; row left out", flush=True)
                continue
            lp, lm = np.array(lp), np.array(lm)
            table[(depth, width)] = (lp.mean(), lm.mean())
            print(f"{depth:5d} {width:5d}  {np.mean(eps):6.0f}  {np.mean(el):.5f}     {lp.mean():.4f} ({lp.std(ddof=1):.4f})   {lm.mean():.5f} ({lm.std(ddof=1):.5f})  {lm.mean() / lp.mean():.3f}"
                  f"        {np.mean(ep_):.4f}   {np.mean(em_):.4f}   {np.mean(sw):5.1f}   {time.time() - t0:5.0f}", flush=True)
    print("log-log slope of the mean loss barrier against width")
    for depth in depths:
        for lo in (32, 64):
            ws = [w for w in widths if w >= lo and (depth, w) in table]
            if len(ws) >= 3:
                sp = np.polyfit(np.log(ws), np.log([table[(depth, w)][0] for w in ws]), 1)[0]
                sm = np.polyfit(np.log(ws), np.log([table[(depth, w)][1] for w in ws]), 1)[0]
                print(f"  depth {depth}, widths {ws[0]}-{ws[-1]}: plain {sp:+.2f}, matched {sm:+.2f}")
