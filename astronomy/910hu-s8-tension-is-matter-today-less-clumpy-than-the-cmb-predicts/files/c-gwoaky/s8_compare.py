# Pairwise differences between published S8 values, treating each as an independent Gaussian.
# For a pair (A, B) with A < B the error used is sqrt(upper error of A squared + lower error of B squared).
# This is the crude one-parameter comparison, not the full-parameter-space metrics the papers use,
# and it ignores shared calibration data, overlapping sky and different priors.
from math import sqrt

vals = [  # name, S8, +err, -err, source
    ("KiDS-Legacy shear",        0.815, 0.016, 0.021, "arXiv:2503.19441"),
    ("DES Y6 shear, NLA",        0.798, 0.014, 0.015, "arXiv:2602.10065"),
    ("DES Y6 shear, TATT",       0.783, 0.019, 0.015, "arXiv:2602.10065"),
    ("DES Y6 3x2pt",             0.789, 0.012, 0.012, "arXiv:2601.14559"),
    ("HSC Y3 shear, DESI n(z)",  0.804, 0.019, 0.018, "arXiv:2511.18134"),
    ("CMB (Planck+ACT+SPT)",     0.836, 0.012, 0.013, "arXiv:2602.12238"),
]

print(f"{'A':26s} {'B':26s}  B-A     sigma   n_sigma")
for i in range(len(vals)):
    for j in range(len(vals)):
        a, b = vals[i], vals[j]
        if a[1] < b[1] or (a[1] == b[1] and i < j):
            s = sqrt(a[2] ** 2 + b[3] ** 2)
            print(f"{a[0]:26s} {b[0]:26s}  {b[1] - a[1]:.3f}   {s:.4f}  {(b[1] - a[1]) / s:.2f}")

# inverse-variance mean of the three surveys' cosmic shear values (symmetrised errors), against the CMB value
lens = [vals[0], vals[1], vals[4]]
w = [1 / ((v[2] + v[3]) / 2) ** 2 for v in lens]
m = sum(wi * v[1] for wi, v in zip(w, lens)) / sum(w)
e = 1 / sqrt(sum(w))
cmb = vals[5]
print(f"\nweighted mean of KiDS-Legacy, DES Y6 (NLA), HSC Y3 shear: {m:.4f} +- {e:.4f}")
print(f"CMB minus that mean: {cmb[1] - m:.4f}, {(cmb[1] - m) / sqrt(e ** 2 + cmb[3] ** 2):.2f} sigma")
chi2 = sum(wi * (v[1] - m) ** 2 for wi, v in zip(w, lens))
print(f"chi-squared of the three shear values about their mean: {chi2:.2f} for 2 degrees of freedom")
