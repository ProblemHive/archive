"""Truth-probe transfer, affirmative <-> negated, at every layer of Qwen2.5-0.5B (base).
Data: Marks and Tegmark's datasets (github.com/saprmarks/geometry-of-truth/datasets):
cities, neg_cities, sp_en_trans, neg_sp_en_trans, larger_than, smaller_than.
Activations: residual stream (hidden_states[l], l = 0 embeddings .. 24) at the last token
of each statement, fp32 forward pass, no prompt around the statement.
Probes, per layer:
  MM  mass-mean (difference of class means), threshold at the midpoint of the training class means
  LR  logistic regression on standardised activations (sklearn, C = 0.1)
Reported: accuracy and AUROC (AUROC ignores the threshold, so it measures the direction alone).
In-domain: 80/20 split, seed 0. Cross-dataset: trained on all of A, tested on all of B.
"""
import sys, json, numpy as np, pandas as pd, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

M = "/data/wdqsj/qwen2.5-0.5b"
D = "/data/wdqsj/got"
names = ["cities", "neg_cities", "sp_en_trans", "neg_sp_en_trans", "larger_than", "smaller_than"]
dev = "cuda" if torch.cuda.is_available() else "cpu"
print("device", dev, torch.cuda.get_device_name(0) if dev == "cuda" else "")
tok = AutoTokenizer.from_pretrained(M)
tok.padding_side = "right"
model = AutoModelForCausalLM.from_pretrained(M, torch_dtype=torch.float32).to(dev).eval()

acts, labels = {}, {}
for n in names:
    df = pd.read_csv(f"{D}/{n}.csv")
    st = df["statement"].tolist(); y = df["label"].astype(int).to_numpy()
    out = []
    with torch.no_grad():
        for i in range(0, len(st), 64):
            b = tok(st[i:i + 64], return_tensors="pt", padding=True).to(dev)
            hs = model(**b, output_hidden_states=True).hidden_states  # tuple of (B, T, H)
            last = b["attention_mask"].sum(1) - 1  # right padding: index of last real token
            H = torch.stack(hs, 1)  # (B, L+1, T, H)
            out.append(H[torch.arange(H.shape[0]), :, last].float().cpu().numpy())
    acts[n] = np.concatenate(out); labels[n] = y
    print("%-16s n=%5d  true share %.3f" % (n, len(y), y.mean()))
L = acts[names[0]].shape[1]

def fit(X, y):
    mu1, mu0 = X[y == 1].mean(0), X[y == 0].mean(0)
    d = mu1 - mu0; thr = 0.5 * (mu1 + mu0) @ d
    m, s = X.mean(0), X.std(0) + 1e-6
    lr = LogisticRegression(C=0.1, max_iter=3000).fit((X - m) / s, y)
    return d, thr, lr, m, s

def score(p, X, y):
    d, thr, lr, m, s = p
    z = X @ d; pz = lr.decision_function((X - m) / s)
    return ((z > thr) == y).mean(), roc_auc_score(y, z), ((pz > 0) == y).mean(), roc_auc_score(y, pz)

rng = np.random.default_rng(0)
pairs = [("cities", "cities"), ("cities", "neg_cities"), ("neg_cities", "cities"),
         ("sp_en_trans", "sp_en_trans"), ("sp_en_trans", "neg_sp_en_trans"), ("neg_sp_en_trans", "sp_en_trans"),
         ("larger_than", "larger_than"), ("larger_than", "smaller_than"), ("smaller_than", "larger_than"),
         ("cities+neg_cities", "sp_en_trans"), ("cities+neg_cities", "neg_sp_en_trans"),
         ("cities", "sp_en_trans"), ("cities", "neg_sp_en_trans")]
res = {}
for a, b in pairs:
    rows = []
    for l in range(L):
        if a == b:
            X, y = acts[a][:, l], labels[a]
            idx = rng.permutation(len(y)) if l == 0 else idx
            k = int(0.8 * len(y)); tr, te = idx[:k], idx[k:]
            p = fit(X[tr], y[tr]); r = score(p, X[te], y[te])
        else:
            parts = a.split("+")
            Xa = np.concatenate([acts[n][:, l] for n in parts]); ya = np.concatenate([labels[n] for n in parts])
            p = fit(Xa, ya); r = score(p, acts[b][:, l], labels[b])
        rows.append([round(float(v), 3) for v in r])
    res[a + " -> " + b] = rows
    if a == b:
        del idx

print("\nper layer: MM accuracy / MM AUROC / LR accuracy / LR AUROC")
for key, rows in res.items():
    print("\n" + key)
    for l, r in enumerate(rows):
        print("  layer %2d  MM %.3f %.3f  LR %.3f %.3f" % (l, *r))
print("\nbest layer per pair (by MM AUROC; by LR accuracy):")
for key, rows in res.items():
    a = np.array(rows)
    i, j = int(a[:, 1].argmax()), int(a[:, 2].argmax())
    print("  %-38s MM-AUROC max %.3f at layer %2d | LR-acc max %.3f at layer %2d | MM-AUROC at 6/12/18/24: %s"
          % (key, a[i, 1], i, a[j, 2], j, " ".join("%.2f" % a[x, 1] for x in (6, 12, 18, 24))))
json.dump(res, open("negation_transfer.json", "w"))
