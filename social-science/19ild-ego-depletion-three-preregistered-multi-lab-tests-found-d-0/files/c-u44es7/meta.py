# Random-effects (DerSimonian-Laird) meta-analysis of the per-sample effects
# deposited by Dang et al. 2025 (osf.io/j56xz, file ES_Nogo_error.csv).
# d1 = depletion vs long control, d2 = depletion vs short control,
# d3 = long control vs short control; v = sampling variance of d.
import csv, math, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PREREG = {"Lihua Mao (China)", "Anna Baumert (Germany)", "Lile Jia (Singapore)",
          "Oulmann Zerhouni (France)", "Timur Sevincer (Germany)"}
ONLINE = {"Online sample (International)", "Online sample (US)"}


def dl(rows):
    k = len(rows)
    w = [1 / v for _, v in rows]
    fe = sum(wi * d for wi, (d, _) in zip(w, rows)) / sum(w)
    q = sum(wi * (d - fe) ** 2 for wi, (d, _) in zip(w, rows))
    c = sum(w) - sum(wi * wi for wi in w) / sum(w)
    tau2 = max(0.0, (q - (k - 1)) / c) if k > 1 else 0.0
    ws = [1 / (v + tau2) for _, v in rows]
    est = sum(wi * d for wi, (d, _) in zip(ws, rows)) / sum(ws)
    se = math.sqrt(1 / sum(ws))
    i2 = max(0.0, (q - (k - 1)) / q) * 100 if q > 0 else 0.0
    return k, est, est - 1.96 * se, est + 1.96 * se, est / se, q, i2, tau2


def show(label, rows):
    if not rows:
        return
    k, est, lo, hi, z, q, i2, tau2 = dl(rows)
    print(f"{label:<46} k={k:2d} d={est:6.3f} CI95=[{lo:6.3f},{hi:6.3f}] Z={z:5.2f} Q={q:5.2f} I2={i2:4.1f}% tau2={tau2:.4f}")


data = list(csv.DictReader(open("osf/ES_Nogo_error.csv", encoding="utf-8-sig")))
for col, name in (("1", "depletion vs long control"), ("2", "depletion vs short control"), ("3", "long vs short control")):
    rows = [(r["Author"], float(r["d" + col]), float(r["v" + col])) for r in data if r["d" + col]]
    print("==", name)
    show("all samples", [(d, v) for _, d, v in rows])
    show("preregistered (steps 1 and 2)", [(d, v) for a, d, v in rows if a in PREREG])
    show("not preregistered (steps 3 and 4)", [(d, v) for a, d, v in rows if a not in PREREG])
    show("preregistered replications only (step 2)", [(d, v) for a, d, v in rows if a in PREREG and "Mao" not in a])
    show("all except the initial experiment", [(d, v) for a, d, v in rows if "Mao" not in a])
    show("laboratory", [(d, v) for a, d, v in rows if a not in ONLINE])
    show("online", [(d, v) for a, d, v in rows if a in ONLINE])
    if col == "1":
        sig = [(a, d / math.sqrt(v)) for a, d, v in rows]
        print("samples with |z| > 1.96:", sum(1 for _, z in sig if abs(z) > 1.96), "of", len(sig))
        for a, z in sig:
            print(f"   {a:<32} z={z:5.2f}")

print("== manipulation checks, depletion vs long control (tiredness)")
mc = list(csv.DictReader(open("osf/mc_dep_long.csv", encoding="utf-8-sig")))
show("tiredness, all", [(float(r["d_tiredness"]), float(r["v_tiredness"])) for r in mc])
show("difficulty, all", [(float(r["d_difficulty"]), float(r["v_difficulty"])) for r in mc])
print("== manipulation checks, long vs short control (tiredness)")
mc = [r for r in csv.DictReader(open("osf/mc_long_short.csv", encoding="utf-8-sig")) if r["d_tiredness"]]
show("tiredness, all", [(float(r["d_tiredness"]), float(r["v_tiredness"])) for r in mc])

# Same paradigm, short against long first task: the pilot in the supplement
# (10 minutes, 240 trials, d = 0.09, CI95 [-0.22, 0.39]) against the main result.
print("== pilot (10 min) vs main study (30-40 min), depletion vs long control")
se_p = (0.39 - (-0.22)) / 3.92
k, est, lo, hi, z, q, i2, tau2 = dl([(float(r["d1"]), float(r["v1"])) for r in data])
se_m = (hi - lo) / 3.92
diff = est - 0.09
se_d = math.sqrt(se_p ** 2 + se_m ** 2)
zz = diff / se_d
p = math.erfc(abs(zz) / math.sqrt(2))
print(f"difference={diff:.3f} SE={se_d:.3f} z={zz:.2f} two-sided p={p:.3f}")
