"""Re-run the classification of Sunburst-maze experiments from rows.json (made by parse.py from TOL_data.m).
V0 mimics TOL_fig_stats1.m: z of each category's mean % relative to the SINGLE-path null (mean m, sd s of one path's % under
uniform random choice), threshold z>=1.96, the category with the largest z wins.
V1: same but strict priority shortcut > adjacent > outer > cued > other (what the Methods text says).
V2: V0 with a one-sided 1.65 threshold.
V3: each category compared with its own null (same category, same N and number of paths, simulated), and 'other'
    compared with the null of the maximum over the remaining paths; threshold z>=1.96 against that null; max z wins.
usage: python classify.py [seed] [sims]"""
import json, sys
import numpy as np

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
SIMS = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
rng = np.random.default_rng(seed)
rows = [r for r in json.load(open("rows.json")) if r.get("main") == 1]
CATS = ["short", "adj", "outer", "cued", "other"]

def vec(x):
    return np.array([np.nan if v is None else v for v in x], float)

out = []
for r in rows:
    ch = r.get("choice")
    mean = r.get("mean")
    have_counts = ch is not None and isinstance(ch, list) and len(ch) > 0
    if have_counts:
        counts = vec(ch)
        n = int(np.nansum(counts))
        c = counts / n * 100
        pct = True
    else:
        c = vec(mean)
        n = int(round(np.nansum(c)))
        pct = False
    k = int((~np.isnan(c)).sum())
    avail = np.where(~np.isnan(c))[0]          # zero-based positions with data
    def idxs(f):
        v = r.get(f)
        if v is None or isinstance(v, (str, tuple)):
            return []
        v = [x for x in (v if isinstance(v, list) else [v]) if not np.isnan(x)]
        return [int(x) - 1 for x in v]
    s_i, a_i, o_i = idxs("short"), idxs("adjacent"), idxs("outer")
    light = r.get("light")
    light = [x for x in (light if isinstance(light, list) else [light]) if x is not None and not np.isnan(x)]
    paths = np.atleast_1d(np.array(r.get("paths") if r.get("paths") is not None else [], float))
    okp = (~np.isnan(paths) & ~np.isnan(c[:len(paths)])) if 0 < len(paths) <= len(c) else None
    def cat_stats(cv):
        """category statistics for a vector cv of the same layout as c"""
        st = [np.nan] * 5
        if s_i: st[0] = np.nanmean(cv[s_i])
        if a_i: st[1] = np.nanmean(cv[a_i])
        if o_i: st[2] = np.nanmean(cv[o_i])
        if light and okp is not None and okp.sum() > 1:
            st[3] = np.nanmean(np.interp(light, paths[okp], cv[:len(paths)][okp]))
        rest = np.ones(len(cv), bool)
        rest[s_i + a_i + o_i] = False
        rest &= ~np.isnan(cv)
        if rest.any(): st[4] = np.nanmax(cv[rest])
        return np.array(st)
    obs = cat_stats(c)
    # single-path null as in TOL_data.m
    sims = np.zeros((SIMS, len(c)))
    p = np.full(k, 1.0 / k)
    cnt = rng.multinomial(n, p, size=SIMS)
    sims[:, avail] = cnt / n * 100 if pct else cnt
    sims[:, np.isnan(c)] = np.nan
    m = np.nanmean(sims); s = np.nanstd(sims)
    z0 = (obs - m) / s
    # per-category nulls
    nulls = np.array([cat_stats(sims[i]) for i in range(SIMS)])
    z3 = (obs - np.nanmean(nulls, 0)) / np.nanstd(nulls, 0)
    out.append(dict(name=f"{r.get('experiment')}|{r.get('group')}|{r.get('test')}", sp=r.get("species"), n=n, k=k,
                    obs=obs, z0=z0, z3=z3))

def classify(z, thr, priority=False):
    z = np.where(z >= thr, z, np.nan)
    if np.all(np.isnan(z)): return 5
    if priority: return int(np.nanargmax(~np.isnan(z)))
    return int(np.nanargmax(z))

names = CATS + ["nopref"]
def tally(f):
    t = np.zeros(6, int)
    for o in out: t[f(o)] += 1
    return dict(zip(names, t.tolist()))

print("experiments:", len(out), "seed", seed, "sims", SIMS)
print("V0 as coded (z>=1.96, max z)      ", tally(lambda o: classify(o["z0"], 1.96)))
print("V1 strict priority                ", tally(lambda o: classify(o["z0"], 1.96, True)))
print("V2 one-sided 1.65                 ", tally(lambda o: classify(o["z0"], 1.65)))
print("V3 per-category null (z>=1.96)    ", tally(lambda o: classify(o["z3"], 1.96)))
print("V3 per-category null, priority    ", tally(lambda o: classify(o["z3"], 1.96, True)))
print()
print("per experiment: name, species, N, paths | V0 | V3")
for o in out:
    print(f"{o['name'][:58]:58s} {str(o['sp'])[:6]:6s} N={o['n']:4d} k={o['k']:2d} | {names[classify(o['z0'],1.96)]:7s} | {names[classify(o['z3'],1.96)]}")

