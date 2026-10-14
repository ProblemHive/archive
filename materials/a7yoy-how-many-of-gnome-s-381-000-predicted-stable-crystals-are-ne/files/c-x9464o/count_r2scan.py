# Counts from the two public GNoME tables: how many released structures have an r2SCAN
# re-check, and how many of those are on or below the hull in the r2SCAN table's own columns.
import ast
import pandas as pd

S = pd.read_csv("a7yoy/data/stable_materials_summary.csv", index_col=0, low_memory=False)
R = pd.read_csv("a7yoy/data/stable_materials_r2scan.csv", index_col=0, low_memory=False)
TOL = 5e-5  # eV per atom, the on-hull threshold stated in DATASET.md
D, D_ALL, D_MP, D_MPO = ("Decomposition Energy Per Atom", "Decomposition Energy Per Atom All",
                         "Decomposition Energy Per Atom MP", "Decomposition Energy Per Atom MP OQMD")
for T in (S, R):
    T["nel"] = T["Elements"].map(lambda s: len(ast.literal_eval(s)))


def pct(k, n):
    return f"{k:>7} of {n:>7} = {100 * k / n:5.1f}%"


print("ROWS")
print(" summary table:", len(S), "rows, all MaterialIds and reduced formulas distinct:",
      S["MaterialId"].is_unique and S["Reduced Formula"].is_unique)
print(" r2SCAN table: ", len(R), "rows, all distinct:", R["MaterialId"].is_unique and R["Reduced Formula"].is_unique)
in_s = R["MaterialId"].isin(S["MaterialId"])
print(" r2SCAN rows whose MaterialId is in the summary table:", pct(in_s.sum(), len(R)))
print(" summary rows that have an r2SCAN row:               ", pct(S["MaterialId"].isin(R["MaterialId"]).sum(), len(S)))

print("\nSUMMARY TABLE (PBE), sanity")
print(" on the hull of all entries (All <= 5e-5):", pct((S[D_ALL] <= TOL).sum(), len(S)))
print(" All <= 0.001:                            ", pct((S[D_ALL] <= 0.001).sum(), len(S)))
print(" formation energy below -5 eV/atom (implausible values):", int((S["Formation Energy Per Atom"] < -5).sum()))
print(" Is Train:", S["Is Train"].value_counts(dropna=False).to_dict())

print("\nCOVERAGE OF THE r2SCAN RE-CHECK BY NUMBER OF ELEMENTS (summary rows with an r2SCAN row)")
has = S["MaterialId"].isin(R["MaterialId"])
for n, g in S.groupby("nel"):
    print(f" {n} elements:", pct(has[g.index].sum(), len(g)))

print("\nr2SCAN TABLE: DISTANCE TO THE HULL OF ALL ENTRIES ('... All', never negative)")
for name, T in (("all r2SCAN rows", R), ("rows also in the summary table", R[in_s]), ("rows not in the summary table", R[~in_s])):
    print(" " + name)
    for lab, thr in (("on hull, <= 5e-5", TOL), ("<= 0.001 (1 meV)", 0.001), ("<= 0.010", 0.010), ("<= 0.025", 0.025), ("<= 0.050", 0.050), ("<= 0.100", 0.100)):
        print(f"   {lab:<18}", pct((T[D_ALL] <= thr).sum(), len(T)))
    q = T[D_ALL].quantile([0.5, 0.75, 0.9, 0.99])
    print("   quantiles 50/75/90/99%:", " ".join(f"{v:.4f}" for v in q), " max", f"{T[D_ALL].max():.3f}")

print("\nr2SCAN TABLE: AT OR BELOW THE EARLIER HULLS (rows also in the summary table)")
T = R[in_s]
for c in (D, D_MP, D_MPO):
    print(f" {c:<40} <= 5e-5:", pct((T[c] <= TOL).sum(), len(T)))

print("\nBY NUMBER OF ELEMENTS (rows also in the summary table): on r2SCAN hull of all entries")
for n, g in T.groupby("nel"):
    print(f" {n} elements:", pct((g[D_ALL] <= TOL).sum(), len(g)), "  within 25 meV:", f"{100 * (g[D_ALL] <= 0.025).mean():5.1f}%")

print("\nPBE VALUE AGAINST r2SCAN OUTCOME (merged on MaterialId)")
M = R.merge(S, on="MaterialId", suffixes=("_r2", "_pbe"))
M["on_r2"] = M[D_ALL + "_r2"] <= TOL
bins = [-100, -0.1, -0.05, -0.025, -0.01, -0.005, -0.001, 0.0011]
M["pbe_bin"] = pd.cut(M[D_MPO + "_pbe"], bins)
print(" PBE energy below the Materials Project + OQMD hull (eV/atom)   rows   on r2SCAN hull")
for b, g in M.groupby("pbe_bin", observed=True):
    print(f"   {str(b):<22} {len(g):>7}   {100 * g['on_r2'].mean():5.1f}%")
print(" PBE summary rows on the PBE hull of all entries among merged:", pct((M[D_ALL + "_pbe"] <= TOL).sum(), len(M)))

print("\nELEMENTS WITH NO STABLE ISOTOPE (summary table)")
RADIO = {"Tc", "Pm", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es"}
els = S["Elements"].map(ast.literal_eval)
any_r = els.map(lambda e: bool(RADIO & set(e)))
print(" rows containing Tc, Pm or any element from Po upward:", pct(any_r.sum(), len(S)))
cnt = {}
for e in els[any_r]:
    for x in RADIO & set(e):
        cnt[x] = cnt.get(x, 0) + 1
print(" by element:", dict(sorted(cnt.items(), key=lambda kv: -kv[1])))
print(" same, among rows with an r2SCAN row:", pct((any_r & has).sum(), has.sum()))
