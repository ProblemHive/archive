# Does the curvature survive when each mammal order gets its own level, or its own level and slope?
# usage: python kleiber/orders.py
import io
import zipfile

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

z = zipfile.ZipFile("downloads/kleiber/anage.zip")
df = pd.read_csv(io.BytesIO(z.read("anage_data.txt")), sep="\t", encoding="latin-1")
df = df.dropna(subset=["Metabolic rate (W)", "Body mass (g)"])
mam = df[df["Class"] == "Mammalia"].copy()
mam["x"] = np.log10(mam["Body mass (g)"])
mam["y"] = np.log10(mam["Metabolic rate (W)"])
mam["x2"] = mam["x"] ** 2
big = mam["Order"].value_counts()
mam["grp"] = mam["Order"].where(mam["Order"].map(big) >= 5, "other")       # orders with fewer than 5 species pooled
print("species:", len(mam), " groups:", mam["grp"].nunique())

models = {
    "one line": "y ~ x",
    "one curve": "y ~ x + x2",
    "own level per order, common slope": "y ~ x + C(grp)",
    "own level per order, common curve": "y ~ x + x2 + C(grp)",
    "own level and slope per order": "y ~ x * C(grp)",
    "own level and slope per order, common x2": "y ~ x * C(grp) + x2",
}
fits = {}
for name, f in models.items():
    r = smf.ols(f, mam).fit()
    fits[name] = r
    b2 = f"b2 = {r.params['x2']:.4f} (se {r.bse['x2']:.4f}, p = {r.pvalues['x2']:.2g})" if "x2" in r.params else ""
    print(f"  {name:42s} params {int(r.df_model) + 1:2d}  R2 {r.rsquared:.4f}  AIC {r.aic:8.1f}  BIC {r.bic:8.1f}  {b2}")
r = fits["own level per order, common slope"]
lo, hi = r.conf_int().loc["x"]
print(f"common slope with a level per order: {r.params['x']:.3f} CI95 [{lo:.3f}, {hi:.3f}]")

# within-order curvature, orders with at least 20 species
print("quadratic term fitted inside single orders:")
for o in big[big >= 20].index:
    d = mam[mam["Order"] == o]
    q = smf.ols("y ~ x + x2", d).fit()
    print(f"  {o:16s} n = {len(d):3d}  mass 10^{d['x'].min():.1f} to 10^{d['x'].max():.1f} g  b2 = {q.params['x2']:+.4f} (se {q.bse['x2']:.4f}, p = {q.pvalues['x2']:.2g})")
