# West-minus-east equatorial Pacific SST gradient: linear trend against start year.
# Input: two NetCDF-3 subsets (5S-5N, 110E-80W, monthly, 1940 onward) from NOAA ERDDAP.
import numpy as np
from scipy.io import netcdf_file

FILES = [("ERSSTv5", "3vhhr/ersstv5_eqpac.nc"), ("HadISST1", "3vhhr/hadisst_eqpac.nc")]
WEST = (110.0, 180.0)   # 5S-5N, 110E-180
EAST = (180.0, 280.0)   # 5S-5N, 180-80W
END_YEARS = (2024, 2025)
STARTS = range(1950, 1991)


def load(path):
    f = netcdf_file(path, "r", mmap=False)
    t = np.array(f.variables["time"].data, dtype="int64").astype("datetime64[s]")
    lat = np.array(f.variables["latitude"].data, dtype=float)
    lon = np.array(f.variables["longitude"].data, dtype=float)
    s = np.array(f.variables["sst"].data, dtype=float)
    s = s.reshape(len(t), len(lat), len(lon))      # drops the depth axis of ERSST
    s[(s < -100) | ~np.isfinite(s)] = np.nan        # land and missing
    years = t.astype("datetime64[Y]").astype(int) + 1970
    return years, lat, lon, s


def box_mean(s, lat, lon, lo, hi):
    sel = (lon >= lo) & (lon < hi)
    w = np.cos(np.deg2rad(lat))[None, :, None] * np.ones((1, 1, sel.sum()))
    x = s[:, :, sel]
    ok = np.isfinite(x)
    return np.nansum(np.where(ok, x, 0) * w, axis=(1, 2)) / np.sum(ok * w, axis=(1, 2)), int(ok[0].sum())


def annual(years, m):
    ys = np.unique(years)
    ys = np.array([y for y in ys if (years == y).sum() == 12])
    return ys, np.array([m[years == y].mean() for y in ys])


def trend(ys, v, y0, y1):
    k = (ys >= y0) & (ys <= y1)
    x, y = ys[k].astype(float), v[k]
    n = len(x)
    A = np.vstack([x - x.mean(), np.ones(n)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    res = y - A @ coef
    r1 = np.corrcoef(res[:-1], res[1:])[0, 1]
    neff = n * (1 - r1) / (1 + r1) if r1 > 0 else n   # AR(1) effective sample size
    neff = max(min(neff, n), 3.0)
    se = np.sqrt(res @ res / (neff - 2) / ((x - x.mean()) ** 2).sum())
    return coef[0] * 10, se * 10, r1                    # per decade


series = {}
for name, path in FILES:
    years, lat, lon, s = load(path)
    w, nw = box_mean(s, lat, lon, *WEST)
    e, ne = box_mean(s, lat, lon, *EAST)
    ys, wa = annual(years, w)
    _, ea = annual(years, e)
    series[name] = (ys, wa, ea, wa - ea)
    print(f"{name}: lat centres {lat.min():+.1f}..{lat.max():+.1f}, ocean cells west {nw}, east {ne}, "
          f"complete years {ys[0]}-{ys[-1]}")
    print(f"  1991-2020 mean: west {wa[(ys>=1991)&(ys<=2020)].mean():.2f} C, east {ea[(ys>=1991)&(ys<=2020)].mean():.2f} C, "
          f"west-east {(wa-ea)[(ys>=1991)&(ys<=2020)].mean():.2f} C")

ya, _, _, ga = series["ERSSTv5"]
yb, _, _, gb = series["HadISST1"]
common = np.intersect1d(ya, yb)
ca = ga[np.isin(ya, common)]
cb = gb[np.isin(yb, common)]
print(f"\nCorrelation of the two annual gradient series, {common[0]}-{common[-1]}: {np.corrcoef(ca, cb)[0,1]:.3f}")
print(f"Mean difference ERSSTv5 - HadISST1: 1940-1979 {np.mean((ca-cb)[common<1980]):+.3f} C, 1980-2025 {np.mean((ca-cb)[common>=1980]):+.3f} C")

for end in END_YEARS:
    print(f"\nTrend of west-minus-east SST, start year to {end}, C per decade (+- 1 s.e., AR(1)-adjusted); positive = gradient strengthens")
    print("start |      ERSSTv5       |      HadISST1      | differ")
    for y0 in STARTS:
        row = [f"{y0}  "]
        vals = []
        for name in ("ERSSTv5", "HadISST1"):
            ys, _, _, g = series[name]
            b, se, r1 = trend(ys, g, y0, end)
            vals.append(b)
            row.append(f"{b:+.3f} +- {se:.3f} ({abs(b)/se:4.1f}) ")
        row.append(f"{vals[0]-vals[1]:+.3f}")
        print(" | ".join(row))

print("\nBox trends separately, C per decade, to 2024")
print("start | ERSSTv5 west  east | HadISST1 west  east")
for y0 in (1950, 1960, 1970, 1979, 1982, 1990):
    out = [f"{y0}  "]
    for name in ("ERSSTv5", "HadISST1"):
        ys, wa, ea, _ = series[name]
        out.append(f"{trend(ys, wa, y0, 2024)[0]:+.3f}  {trend(ys, ea, y0, 2024)[0]:+.3f}")
    print(" |     ".join(out))

print("\nAnnual west-minus-east gradient, C (ERSSTv5, HadISST1), last 12 complete years")
for y in common[-12:]:
    print(y, f"{ga[ya==y][0]:.2f}", f"{gb[yb==y][0]:.2f}")
