"""Parse TOL_data.m (Duvelle & Grieves 2026 repository) into Python dicts: one per experiment row.
Only the statements of the form  dat.FIELD(idx...) = VALUE;  inside the data section are read.
Prints a summary of what could and could not be read."""
import re, sys, json
import numpy as np

SRC = "/data/tolman/TOL_data.m"
text = open(SRC, encoding="utf-8", errors="replace").read()
text = text.split("%% add chance shuffle info")[0]
lines = text.split("\n")

nan = float("nan")

def conv(v, ctx):
    v = v.strip()
    v = re.sub(r"\s*%.*$", "", v)           # trailing comment
    v = v.rstrip(";").strip()
    if v.startswith("{") and v.endswith("}"):
        v = v[1:-1].strip()
    if v.startswith("'"):
        return v.strip("'")
    # min/max of paths
    if re.match(r"\[min\(dat\.paths", v):
        p = np.array(ctx["paths"], float)
        return [float(np.nanmin(p)), float(np.nanmax(p))]
    if re.match(r"dat\.choice\{idx\}\./", v) or "dat.mean" in v and "./" in v:
        return None
    v = v.replace("NaN", "nan")
    if v.startswith("sum(dat.choice"):
        return "SUMCHOICE"
    if "fliplr" in v or ("+" in v and "[" in v):
        def arr(mm):
            return "np.array([" + ",".join(mm.group(1).replace(",", " ").split()) + "])"
        e = re.sub(r"\[([^\[\]]*)\]", arr, v).replace("fliplr", "np.flip")
        try:
            return [float(x) for x in np.atleast_1d(eval(e, {"np": np, "nan": nan}))]
        except Exception:
            return ("UNPARSED", v)
    if re.fullmatch(r"\[?[\d\s:\.,\-nae+]*\]?", v):
        pass
    m = re.fullmatch(r"\[?\s*(\d+)\s*:\s*(\d+)\s*\]?", v)
    if m:
        return list(range(int(m.group(1)), int(m.group(2)) + 1))
    try:
        if v.startswith("["):
            inner = v[1:-1].replace(",", " ").replace(";", " ")
            return [float(x) for x in inner.split()]
        return float(eval(v, {"nan": nan}))
    except Exception:
        return ("UNPARSED", v)

rows = []
cur = None
pat = re.compile(r"^\s*dat\.(\w+)\(idx[^)]*\)\s*=\s*(.*)$")
i = 0
while i < len(lines):
    ln = lines[i]
    if re.match(r"^\s*idx\s*=", ln):
        cur = {}
        rows.append(cur)
        i += 1
        continue
    m = pat.match(ln)
    if m and cur is not None:
        f, val = m.group(1), m.group(2)
        # join continuation lines (open bracket without close)
        while val.count("[") > val.count("]") or val.count("{") > val.count("}"):
            i += 1
            val += " " + lines[i].strip()
        cur[f] = conv(val, cur)
    i += 1

bad = {}
for r in rows:
    for k, v in r.items():
        if isinstance(v, tuple):
            bad.setdefault(k, []).append(v[1][:60])
print("rows:", len(rows), "main==1:", sum(1 for r in rows if r.get("main") == 1))
for k, v in bad.items():
    print("unparsed", k, len(v), v[:2])
json.dump(rows, open("rows.json", "w"))

