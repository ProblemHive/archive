# usage: python -I biotime/variants.py MODE     the script richness.py with one filter added before anything else
# Unit: one study at one location. Richness per year = number of distinct taxa (newID), after
# sample-based rarefaction to the smallest number of sample events in any year of that series.
# Trend: least-squares slope of ln(richness) on year, for series with >= 5 sampled years spanning >= 10 years.
import sys
import time

import numpy as np
import pandas as pd
from scipy import stats

CELL = 0.0
MODE = sys.argv[1]            # species | notreat | protected | unprotected
DRAWS = 30
MIN_YEARS, MIN_SPAN = 5, 10
rng = np.random.default_rng(20261011)
t0 = time.time()

q = np.load("biotime/query.npz", allow_pickle=True)
df = pd.DataFrame({
    "study": q["STUDY_ID"], "year": q["YEAR"], "sample": q["SAMPLE_DESC__codes"], "sp": q["newID"],
    "lat": q["LATITUDE"], "lon": q["LONGITUDE"],
})
meta0 = pd.read_csv("downloads/biotime/metadata.csv", encoding="latin-1", low_memory=False)
print("PROTECTED_AREA:", meta0["PROTECTED_AREA"].astype(str).str.upper().value_counts(dropna=False).to_dict())
print("TREATMENT given:", int(meta0["TREATMENT"].notna().sum()), "GENERAL_TREAT given:", int(meta0["GENERAL_TREAT"].notna().sum()), "of", len(meta0))
if MODE == "species":
    lv = list(q["resolution__levels"])
    print("resolution levels:", lv)
    df = df[q["resolution__codes"] == lv.index("species")]
elif MODE == "notreat":
    ok = meta0.loc[meta0["TREATMENT"].isna() & meta0["GENERAL_TREAT"].isna(), "STUDY_ID"]
    df = df[df["study"].isin(ok)]
elif MODE in ("protected", "unprotected"):
    flag = meta0["PROTECTED_AREA"].astype(str).str.upper() == "TRUE"
    df = df[df["study"].isin(meta0.loc[flag if MODE == "protected" else ~flag, "STUDY_ID"])]
print("MODE:", MODE)
print(f"records: {len(df)}; studies: {df['study'].nunique()}; taxa (newID): {df['sp'].nunique()}; sample events: {df['sample'].nunique()}")
if CELL > 0:
    df["lat"] = np.floor(df["lat"] / CELL)
    df["lon"] = np.floor(df["lon"] / CELL)
df["loc"] = df.groupby(["study", "lat", "lon"], sort=False).ngroup()
df = df[["study", "loc", "year", "sample", "sp"]].drop_duplicates()
print(f"location unit: {'exact coordinates' if CELL == 0 else f'{CELL} degree cells'}; study-locations: {df['loc'].nunique()}; distinct (location, year, sample, taxon) rows: {len(df)}")

yrs = df.groupby("loc")["year"].agg(["nunique", "min", "max"])
keep = yrs[(yrs["nunique"] >= MIN_YEARS) & (yrs["max"] - yrs["min"] >= MIN_SPAN)].index
df = df[df["loc"].isin(keep)]
print(f"series with >= {MIN_YEARS} sampled years spanning >= {MIN_SPAN} years: {len(keep)}, from {df['study'].nunique()} studies; rows kept: {len(df)}")

eff = df.groupby(["loc", "year"])["sample"].nunique().rename("ns").reset_index()
m = eff.groupby("loc")["ns"].agg(["min", "max"])
equal = m[m["min"] == m["max"]].index
print(f"series with the same number of sample events every year: {len(equal)}; needing rarefaction: {len(m) - len(equal)}")

raw = df.groupby(["loc", "year"])["sp"].nunique().rename("S_raw").reset_index()
out = raw.merge(eff, on=["loc", "year"])
out["S"] = out["S_raw"].astype(float)

un = df[~df["loc"].isin(equal)].sort_values(["loc", "year"])
mmin = m["min"].to_dict()
rare = {}
for (loc, year), g in un.groupby(["loc", "year"], sort=False):
    k = mmin[loc]
    s_codes, s_idx = np.unique(g["sample"].to_numpy(), return_inverse=True)
    ns = len(s_codes)
    if ns == k:
        continue
    p_codes, p_idx = np.unique(g["sp"].to_numpy(), return_inverse=True)
    if ns * len(p_codes) <= 20_000_000:
        inc = np.zeros((ns, len(p_codes)), dtype=bool)
        inc[s_idx, p_idx] = True
        tot = 0
        for _ in range(DRAWS):
            tot += inc[rng.choice(ns, k, replace=False)].any(axis=0).sum()
    else:
        order = np.argsort(s_idx, kind="stable")
        bounds = np.searchsorted(s_idx[order], np.arange(ns + 1))
        tot = 0
        for _ in range(DRAWS):
            ch = rng.choice(ns, k, replace=False)
            tot += len(np.unique(np.concatenate([p_idx[order[bounds[c]:bounds[c + 1]]] for c in ch])))
    rare[(loc, year)] = tot / DRAWS
if rare:
    r = pd.Series(rare).rename("S_rare").rename_axis(["loc", "year"]).reset_index()
    out = out.merge(r, on=["loc", "year"], how="left")
    out["S"] = out["S_rare"].fillna(out["S"])
print(f"rarefaction done at {time.time() - t0:.0f} s; location-years rarefied: {len(rare)} of {len(out)}")

study_of = df.groupby("loc")["study"].first()


def slopes(table, col, shuffle=False):
    rows = []
    for loc, g in table.groupby("loc", sort=False):
        x = g["year"].to_numpy(dtype=float)
        y = np.log(g[col].to_numpy(dtype=float))
        if shuffle:
            y = rng.permutation(y)
        x = x - x.mean()
        sxx = (x * x).sum()
        b = (x * y).sum() / sxx
        res = y - y.mean() - b * x
        n = len(x)
        se = np.sqrt((res * res).sum() / (n - 2) / sxx) if n > 2 else np.nan
        p = 2 * stats.t.sf(abs(b / se), n - 2) if se > 0 else (1.0 if b == 0 else 0.0)
        rows.append((loc, b, p, n, g["year"].max() - g["year"].min(), g["year"].min(), g[col].mean()))
    return pd.DataFrame(rows, columns=["loc", "slope", "p", "nyears", "span", "start", "meanS"])


sl = slopes(out, "S")
sl["study"] = sl["loc"].map(study_of)
meta = pd.read_csv("downloads/biotime/metadata.csv", encoding="latin-1", low_memory=False)[["STUDY_ID", "REALM", "TAXA", "CLIMATE"]]
sl = sl.merge(meta, left_on="study", right_on="STUDY_ID", how="left")
sl["pct"] = 100 * (np.exp(10 * sl["slope"]) - 1)             # per cent change of richness per decade



def boot(tab, col="slope", n=4000):
    """Mean of study means, with a 95% interval from resampling studies."""
    sm = tab.groupby("study")[col].mean().to_numpy()
    if len(sm) < 3:
        return np.nan, np.nan, np.nan, len(sm)
    idx = rng.integers(0, len(sm), size=(n, len(sm)))
    bm = sm[idx].mean(axis=1)
    return sm.mean(), np.quantile(bm, 0.025), np.quantile(bm, 0.975), len(sm)


def pct(b):
    return 100 * (np.exp(10 * b) - 1)


def line(label, tab):
    mean, lo, hi, ns = boot(tab)
    sm = tab.groupby("study")["slope"].mean()
    print(f"  {label:30s} studies {ns:4d}  series {len(tab):6d}  mean of study means {pct(mean):+6.2f}% per decade [{pct(lo):+6.2f}, {pct(hi):+6.2f}]"
          f"  median study {pct(sm.median()):+6.2f}%  studies up/down {(sm > 0).sum()}/{(sm < 0).sum()}")


print("\nA. Series taken one by one")
print(f"  series {len(sl)}; median span {sl['span'].median():.0f} years; median sampled years {sl['nyears'].median():.0f}; median mean richness {sl['meanS'].median():.1f}")
print(f"  slope of ln S: mean {pct(sl['slope'].mean()):+.2f}% per decade, median {pct(sl['slope'].median()):+.2f}%; rising {(sl['slope'] > 0).mean():.3f}, falling {(sl['slope'] < 0).mean():.3f}, flat {(sl['slope'] == 0).mean():.3f}")
print(f"  individually significant at 5%: rising {((sl['p'] < 0.05) & (sl['slope'] > 0)).mean():.3f}, falling {((sl['p'] < 0.05) & (sl['slope'] < 0)).mean():.3f}")
top = sl["study"].value_counts()
print(f"  series per study: median {top.median():.0f}, largest {top.iloc[0]} (study {top.index[0]}), the five largest studies hold {top.iloc[:5].sum() / len(sl):.2f} of all series")

print("\nB. Each study counted once (mean slope of its series), interval from resampling studies")
line("all", sl)
for col in ("REALM", "TAXA", "CLIMATE"):
    for key, tab in sl.groupby(col):
        if tab["study"].nunique() >= 10:
            line(f"{col.lower()}: {key}", tab)

print("\nC. By length of the series (Gonzalez et al. 2016: is loss clearer in longer series?)")
for lo_, hi_ in ((10, 19), (20, 39), (40, 500)):
    line(f"span {lo_} to {hi_} years", sl[(sl["span"] >= lo_) & (sl["span"] <= hi_)])
rho, prho = stats.spearmanr(sl.groupby("study")["span"].mean(), sl.groupby("study")["slope"].mean())
print(f"  rank correlation of study mean slope with study mean span: {rho:+.3f} (p = {prho:.2g})")

print("\nD. By first year of the series")
for lo_, hi_ in ((1800, 1969), (1970, 1989), (1990, 2030)):
    line(f"start {lo_} to {hi_}", sl[(sl["start"] >= lo_) & (sl["start"] <= hi_)])

print("\nE. Controls")
rawsl = slopes(out, "S_raw")
rawsl["study"] = rawsl["loc"].map(study_of)
line("no rarefaction (raw counts)", rawsl)
sh = slopes(out, "S", shuffle=True)
sh["study"] = sh["loc"].map(study_of)
line("years shuffled within series", sh)
only = sl[sl["loc"].isin(equal)]
line("equal-effort series only", only)
line("mean richness 10 or more", sl[sl["meanS"] >= 10])
line("at least 10 sampled years", sl[sl["nyears"] >= 10])
print(f"\ndone in {time.time() - t0:.0f} s")
