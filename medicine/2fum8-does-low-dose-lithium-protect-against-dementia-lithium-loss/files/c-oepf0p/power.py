# How large would a confirmatory trial of low-dose lithium in MCI have to be, judged from
# the pilot LATTICE trial (Gildengers et al., JAMA Neurol 2026, doi:10.1001/jamaneurol.2026.0072)?
# Inputs are the published numbers only: difference in annual decline of CVLT-II delayed
# recall 0.69 points/year, 95% CI 0.01 to 1.37, with 41 + 39 randomised; hippocampal volume
# 59 mm3/year, 95% CI -9 to 127; Hedges g in amyloid-positive completers 0.74.
# Normal approximation throughout; equal arms; two-sided tests.
from scipy.stats import norm

def se_from_ci(lo, hi):
    return (hi - lo) / (2 * norm.ppf(0.975))

def n_total(effect, se_pilot, n_pilot, alpha, power):
    # the SE scales as 1/sqrt(n): n = n_pilot * (z_total * se_pilot / effect)^2
    z = norm.ppf(1 - alpha / 2) + norm.ppf(power)
    return n_pilot * (z * se_pilot / effect) ** 2

n_pilot = 80  # started treatment (41 + 39)
for name, est, lo, hi in [("CVLT-II delayed recall, points/yr", 0.69, 0.01, 1.37),
                          ("hippocampal volume, mm3/yr", 59.0, -9.0, 127.0)]:
    se = se_from_ci(lo, hi)
    print(f"{name}: estimate {est}, SE {se:.3f}, z {est/se:.2f}, two-sided p {2*norm.sf(est/se):.3f}")
    for frac in (1.0, 0.75, 0.5):
        for alpha in (0.05, 0.01):
            n = n_total(frac * est, se, n_pilot, alpha, 0.8)
            print(f"  true effect {frac:.2f} x pilot, alpha {alpha}, power 0.8: about {n:.0f} randomised in total (completers)")

# amyloid-positive subgroup: standardized effect g, per-arm n for a two-sample comparison
for g in (0.74, 0.5, 0.37):
    for alpha in (0.05, 0.01):
        z = norm.ppf(1 - alpha / 2) + norm.ppf(0.8)
        print(f"Abeta+ subgroup, d = {g}, alpha {alpha}, power 0.8: {2*(z/g)**2:.0f} per arm")

# winner's curse: if the true effect equalled the pilot estimate, how often would a pilot of
# this size give p < 0.05 (its observed p was about 0.05)? -> power of the pilot itself
se = se_from_ci(0.01, 1.37)
for frac in (1.0, 0.5):
    zt = frac * 0.69 / se
    print(f"power of an 80-person pilot at alpha 0.05 if true effect = {frac} x 0.69: {norm.sf(1.96 - zt) + norm.cdf(-1.96 - zt):.2f}")
