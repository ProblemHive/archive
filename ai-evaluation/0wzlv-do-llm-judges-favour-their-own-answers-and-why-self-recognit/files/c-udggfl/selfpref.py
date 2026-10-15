"""Self-preference of the GPT-4 judge on MT-Bench, measured against expert/author human votes
on the same (question, turn, model pair). Data: lmsys/mt_bench_human_judgments (CC BY 4.0).

Score of model X in one comparison: win 1, tie 0.5, loss 0 (GPT-4 'tie (inconsistent)',
i.e. the verdict flipped when the order was swapped, counts as a tie).
Human score of a pair = mean over all human votes on that pair (several judges per pair).
delta(X vs Y) = judge score of X - human score of X, on pairs judged by both.
Self-preference of GPT-4 = how much larger delta is for X = gpt-4 than for other strong
models X' facing the same opponents Y (the matched null).
Bootstrap: resample the 80 questions with replacement, 2000 times, seed 1.
"""
import sys
import numpy as np, pandas as pd

H = pd.read_parquet("/data/0wzlv/mtbench_human.parquet")
G = pd.read_parquet("/data/0wzlv/mtbench_gpt4_pair.parquet")

def tidy(d):
    rows = []
    for r in d.itertuples():
        a, b = r.model_a, r.model_b
        w = r.winner
        sa = 1.0 if w == "model_a" else 0.0 if w == "model_b" else 0.5
        # store with the two models in alphabetical order
        if a > b:
            a, b, sa = b, a, 1 - sa
        rows.append((r.question_id, r.turn, a, b, sa))
    return pd.DataFrame(rows, columns=["q", "turn", "a", "b", "sa"])

h = tidy(H).groupby(["q", "turn", "a", "b"], as_index=False).agg(h_sa=("sa", "mean"), n_h=("sa", "size"))
g = tidy(G).groupby(["q", "turn", "a", "b"], as_index=False).agg(g_sa=("sa", "mean"))
m = h.merge(g, on=["q", "turn", "a", "b"])
print("human votes", len(H), "| gpt4 verdicts", len(G), "| pairs judged by both:", len(m),
      "| mean human votes per pair %.2f" % m.n_h.mean())

# long form: one row per (pair, focal model X, opponent Y)
L = pd.concat([
    pd.DataFrame({"q": m.q, "turn": m.turn, "X": m.a, "Y": m.b, "hs": m.h_sa, "gs": m.g_sa}),
    pd.DataFrame({"q": m.q, "turn": m.turn, "X": m.b, "Y": m.a, "hs": 1 - m.h_sa, "gs": 1 - m.g_sa}),
])
L["d"] = L.gs - L.hs
cat = {81: "writing", 91: "roleplay", 101: "reasoning", 111: "math", 121: "coding",
       131: "extraction", 141: "stem", 151: "humanities"}
L["cat"] = L.q.map(lambda q: cat[81 + 10 * ((q - 81) // 10)])
L["ref"] = L.cat.isin(["reasoning", "math", "coding"])  # graded with a reference answer by the GPT-4 judge

models = ["gpt-4", "claude-v1", "gpt-3.5-turbo", "vicuna-13b-v1.2", "alpaca-13b", "llama-13b"]
print("\nPer focal model, all opponents: n, human score, GPT-4-judge score, delta")
for X in models:
    s = L[L.X == X]
    print("  %-16s n=%4d  human %.3f  judge %.3f  delta %+.3f" % (X, len(s), s.hs.mean(), s.gs.mean(), s.d.mean()))

qs = np.array(sorted(L.q.unique()))
rng = np.random.default_rng(1)
B = 2000
boot_idx = [rng.choice(qs, size=len(qs), replace=True) for _ in range(B)]

def contrast(sub, X, Xs):
    """mean over opponents Y (not X, not in Xs) of [delta(X vs Y) - delta(X' vs Y)], X' in Xs pooled."""
    opp = [y for y in models if y != X and y not in Xs]
    a = sub[(sub.X == X) & sub.Y.isin(opp)]
    b = sub[sub.X.isin(Xs) & sub.Y.isin(opp)]
    da = a.groupby("Y").d.mean(); db = b.groupby("Y").d.mean()
    return float((da - db).mean())

def with_ci(sub, X, Xs):
    est = contrast(sub, X, Xs)
    per_q = {q: sub[sub.q == q] for q in qs}
    vals = []
    for idx in boot_idx:
        bs = pd.concat([per_q[q] for q in idx])
        vals.append(contrast(bs, X, Xs))
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return est, lo, hi

print("\nMatched contrast: delta(gpt-4 vs Y) - delta(other vs Y), same opponents Y; 95% bootstrap CI over questions")
for label, sub in [("all categories", L), ("open-ended (no reference)", L[~L.ref]), ("reference-graded (reasoning, math, coding)", L[L.ref])]:
    for Xs in (["claude-v1"], ["gpt-3.5-turbo"], ["claude-v1", "gpt-3.5-turbo"]):
        est, lo, hi = with_ci(sub, "gpt-4", Xs)
        print("  %-42s vs %-26s %+.3f  [%+.3f, %+.3f]" % (label, "+".join(Xs), est, lo, hi))

# Zheng et al. style: win rate excluding ties, gpt-4 against each opponent, judge vs humans
print("\nWin rate of gpt-4 excluding ties (pairs judged by both), per opponent: humans (vote-level) vs GPT-4 judge")
Hv = tidy(H); Gv = tidy(G)
key = set(map(tuple, m[["q", "turn", "a", "b"]].values))
for Y in models[1:]:
    def wr(v):
        v = v[[(r.q, r.turn, r.a, r.b) in key for r in v.itertuples()]]
        s = v[((v.a == "gpt-4") & (v.b == Y)) | ((v.b == "gpt-4") & (v.a == Y))]
        x = np.where(s.a == "gpt-4", s.sa, 1 - s.sa)
        x = x[x != 0.5]
        return x.mean(), len(x)
    (hw, hn), (gw, gn) = wr(Hv), wr(Gv)
    print("  vs %-16s humans %.3f (n=%d)  judge %.3f (n=%d)  diff %+.3f" % (Y, hw, hn, gw, gn, gw - hw))
