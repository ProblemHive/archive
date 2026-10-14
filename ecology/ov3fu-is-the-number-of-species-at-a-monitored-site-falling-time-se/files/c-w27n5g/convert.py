# Read the BioTIME 2.0 query file once and store its columns as NumPy arrays for the analysis script.
# usage: python -I biotime/convert.py     (the folder of this script is added to the path by hand, see below)
import sys
import time

import numpy as np

sys.path.insert(0, "/work/biotime")
from rds import read_frame

t0 = time.time()
fr = read_frame("downloads/biotime/query.rds")
print(f"read in {time.time() - t0:.0f} s")
save = {}
for nm, col in fr.items():
    if isinstance(col, dict):
        codes, levels = col["codes"], col["levels"]
        print(f"{nm:24s} text    n = {len(codes):9d}  distinct = {len(levels):7d}  missing = {(codes < 0).sum():8d}  e.g. {levels[:3]}")
        save[nm + "__codes"] = codes
        save[nm + "__levels"] = np.array(levels, dtype=object)
    else:
        col = np.asarray(col)
        miss = int(np.isnan(col).sum()) if col.dtype.kind == "f" else int((col == -2147483648).sum())
        print(f"{nm:24s} {str(col.dtype):7s} n = {len(col):9d}  missing = {miss:8d}  first = {col[:4].tolist()}  min = {np.nanmin(col)}  max = {np.nanmax(col)}")
        save[nm] = col
np.savez("biotime/query.npz", **save, allow_pickle=True)
print(f"saved in {time.time() - t0:.0f} s")
