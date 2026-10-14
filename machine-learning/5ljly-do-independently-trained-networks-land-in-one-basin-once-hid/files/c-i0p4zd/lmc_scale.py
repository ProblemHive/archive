# lmc_scale.py - follow-up to lmc_depth.py: is the matched loss barrier at depth 3 a loss of scale?
# For each pair (same seeds and training as lmc_depth.py), after weight matching, at the midpoint
# t = 0.5 of the straight path: (1) the standard deviation of each hidden layer's activations and of
# the logits over the training set, relative to the mean of the two end points; (2) the training loss
# when the midpoint's logits are multiplied by the single best number s (grid 1..40), which changes
# confidence and nothing else; (3) the training error, which no such s can change.
# Usage: python lmc_scale.py TARGET PAIRS DEPTH WIDTHS
import sys
import numpy as np
import torch
import lmc_depth as L

def acts(P):
    with torch.no_grad():
        x, out = L.X, []
        for i in range(0, len(P) - 2, 2):
            x = torch.relu(x @ P[i].T + P[i + 1])
            out.append(float(x.std()))
        z = x @ P[-2].T + P[-1]
        out.append(float(z.std()))
        return out, z

def best_scale(z):
    best = (1e9, 1.0)
    for s in np.concatenate([np.arange(1, 10, 0.25), np.arange(10, 41, 1.0)]):
        l = float(torch.nn.functional.cross_entropy(z * s, L.y))
        best = min(best, (l, float(s)))
    return best

if __name__ == "__main__":
    target, pairs, depth = float(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    widths = [int(s) for s in sys.argv[4].split(",")]
    print(f"depth {depth}, target {target}, {pairs} pairs; all values are means over pairs, after weight matching")
    print("width  end_loss  mid_loss  mid_loss_best_s  (s)   mid_err  end_err   activation sd at midpoint / mean of end points, per hidden layer, then logits")
    for width in widths:
        rows = []
        for k in range(pairs):
            A, _ = L.train(depth, width, 100 + 2 * k, target, 3000)
            B, _ = L.train(depth, width, 101 + 2 * k, target, 3000)
            M, _ = L.match(A, B, k)
            tA, tM = [torch.tensor(p) for p in A], [torch.tensor(p) for p in M]
            mid = [torch.tensor(0.5 * a + 0.5 * m) for a, m in zip(A, M)]
            sa, _ = acts(tA); sm, _ = acts(tM); sd, z = acts(mid)
            la, ea = L.loss_err(tA); lm, em = L.loss_err(tM); ld, ed = L.loss_err(mid)
            lb, s = best_scale(z)
            rows.append([(la + lm) / 2, ld, lb, s, ed, (ea + em) / 2] + [d / ((a + m) / 2) for d, a, m in zip(sd, sa, sm)])
        r = np.mean(rows, axis=0)
        print(f"{width:5d}  {r[0]:.4f}    {r[1]:.4f}    {r[2]:.4f}        {r[3]:5.1f}   {r[4]:.4f}   {r[5]:.4f}    " + "  ".join(f"{v:.2f}" for v in r[6:]), flush=True)
