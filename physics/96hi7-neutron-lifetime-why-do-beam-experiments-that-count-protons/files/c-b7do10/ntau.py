# Standard Model neutron lifetime from lambda = g_A/g_V, two routes.
# Route A: tau * (1 + 3 lambda^2) = 5172.0(1.1) s   (Czarnecki, Marciano, Sirlin 2018).
#          Uses the superallowed nuclear decays for the vector strength; V_ud and the
#          inner radiative correction drop out.
# Route B: tau * Vud^2 * (1 + 3 lambda^2) * (1 + D_R) * (1 + 0.02704(7)) = 5263.284(17) s
#          (Vander Griend, Cao, Hill, Plestid 2025), with D_R = 0.04537(27) and V_ud from PDG.
from math import sqrt

def route_a(lam, dlam):
    K, dK = 5172.0, 1.1
    f = 1 + 3 * lam * lam
    tau = K / f
    e_lam = tau * 6 * abs(lam) * dlam / f
    e_th = tau * dK / K
    return tau, e_lam, e_th

def route_b(lam, dlam, vud=0.97367, dvud=0.00032):
    K = 5263.284 / ((1 + 0.02704) * (1 + 0.04537))
    relK = sqrt((0.017 / 5263.284) ** 2 + (0.00007 / 1.02704) ** 2 + (0.00027 / 1.04537) ** 2)
    f = 1 + 3 * lam * lam
    tau = K / (vud * vud * f)
    return K, tau, tau * 6 * abs(lam) * dlam / f, tau * 2 * dvud / vud, tau * relK

lams = [("PDG 2025 average (scale factor 2.7)", 1.2753, 0.0013),
        ("PERKEO III 2019, beta asymmetry A", 1.27641, 0.00056),
        ("UCNA 2018, beta asymmetry A", 1.2772, 0.0020),
        ("PERKEO II 2013, beta asymmetry A", 1.2748, 0.0014),
        ("aSPECT 2020, electron-neutrino correlation a", 1.2677, 0.0028),
        ("pre-2002 average quoted by Czarnecki et al.", 1.2637, 0.0021)]
meas = [("UCNtau 2021 (trap)", 877.75, 0.34), ("PDG 2025 trap average", 878.4, 0.5),
        ("Yue et al. 2013 (beam, protons)", 887.7, 2.2), ("J-PARC 2024 (beam, electrons)", 877.2, 4.0)]

print("Route A: tau = 5172.0(1.1) s / (1 + 3 lambda^2)")
for name, lam, dlam in lams:
    tau, e1, e2 = route_a(lam, dlam)
    tot = sqrt(e1 * e1 + e2 * e2)
    pulls = "  ".join(f"{(m - tau) / sqrt(tot * tot + dm * dm):+.1f}" for _, m, dm in meas)
    print(f"  |lambda| = {lam:.5f}({dlam:.5f})  tau = {tau:7.2f} +- {tot:.2f} s (lambda {e1:.2f}, theory {e2:.2f})  pulls: {pulls}   [{name}]")
print("  pulls = (measured - predicted) / combined error, for:", ", ".join(n for n, _, _ in meas))

print("Route B, cross-check with V_ud = 0.97367(32):")
for name, lam, dlam in lams[:2]:
    K, tau, e1, e2, e3 = route_b(lam, dlam)
    print(f"  K = {K:.2f} s; |lambda| = {lam:.5f}: tau = {tau:.2f} s (lambda {e1:.2f}, V_ud {e2:.2f}, theory {e3:.2f})   [{name}]")
K = 5263.284 / (1.02704 * 1.04537)
print(f"  check of the formula against the paper: V_ud from tau = 877.82, |lambda| = 1.27641: {sqrt(K / (877.82 * (1 + 3 * 1.27641 ** 2))):.5f} (paper: 0.97393)")

print("lambda needed by Route A for a given lifetime:")
for name, m, dm in meas[:3]:
    print(f"  {name}: tau = {m} -> |lambda| = {sqrt((5172.0 / m - 1) / 3):.5f}")
