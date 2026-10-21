from math import sqrt, erfc

planck = (67.4, 0.5)  # Planck 2018 VI, base-LCDM, as quoted in the arXiv abstract
rows = [
    # name, H0, list of independent error terms (added in quadrature)
    ("CCHP TRGB, HST+JWST, 24 SN Ia (Freedman+ 2408.06153)", 70.39, [1.22, 1.33, 0.70]),
    ("CCHP TRGB, JWST only (same paper)", 68.81, [1.79, 1.32]),
    ("CCHP JAGB, JWST only (same paper)", 67.80, [2.17, 1.64]),
    ("SH0ES JWST three methods (Riess+ 2408.11770)", 72.6, [2.0]),
    ("SH0ES full HST sample, 42 SN Ia (same paper)", 73.2, [0.9]),
    ("SBF, JWST-TRGB zero point (Jensen+ 2502.15935)", 73.8, [0.7, 2.3]),
]
print(f"Planck 2018: {planck[0]} +- {planck[1]}")
print(f"{'measurement':58s} {'H0':>6s} {'sigma':>6s} {'diff':>6s} {'n_sigma':>7s} {'p(2-sided)':>10s}")
for name, h, errs in rows:
    s = sqrt(sum(e * e for e in errs))
    d = h - planck[0]
    z = d / sqrt(s * s + planck[1] ** 2)
    p = erfc(abs(z) / sqrt(2))
    print(f"{name:58s} {h:6.2f} {s:6.2f} {d:6.2f} {z:7.2f} {p:10.2g}")

# CCHP headline against SH0ES JWST combined: difference and its naive uncertainty
# (the two samples share most galaxies, so the naive z overstates the disagreement)
a, sa = 70.39, sqrt(1.22**2 + 1.33**2 + 0.70**2)
b, sb = 72.6, 2.0
print(f"\nCCHP 70.39 +- {sa:.2f} vs SH0ES-JWST 72.6 +- {sb:.1f}: diff {b-a:.2f}, naive z = {(b-a)/sqrt(sa*sa+sb*sb):.2f} (errors treated as independent; they are not)")
a2, sa2 = 70.39, sa
b2, sb2 = 73.2, 0.9
print(f"CCHP 70.39 vs SH0ES full HST 73.2 +- 0.9: diff {b2-a2:.2f}, naive z = {(b2-a2)/sqrt(sa2*sa2+sb2*sb2):.2f}")
