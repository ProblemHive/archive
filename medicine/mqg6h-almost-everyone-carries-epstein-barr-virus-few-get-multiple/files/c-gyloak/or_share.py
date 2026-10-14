# What a 261-fold odds ratio measured INSIDE EBV-positive people implies.
# Case-control design: 270 EBV-positive MS patients, 270 EBV-positive controls (as described in
# Xie, Sun, Zeng 2024, doi:10.1038/s41392-024-01774-8, for Vietzen et al. 2023).
OR, RR_EBV, N = 261.0, 32.0, 270

print("A) share of MS cases that carry the combination, by its frequency f among EBV-positive controls")
print("   (MS is rare, so the odds ratio is close to the risk ratio against EBV-positive non-carriers)")
for f in [0.0005, 0.001, 0.0037, 0.01, 0.02, 0.05, 0.10, 0.1197]:
    share = OR * f / (1 + (OR - 1) * f)
    # risk of an EBV-positive NON-carrier relative to an EBV-negative person, given 32-fold overall
    r0 = RR_EBV / (1 + (OR - 1) * f)
    print(f"   f={f:.4f}: carriers are {100*share:5.1f}% of cases; EBV+ non-carriers have {r0:5.1f}x the EBV-negative risk")

print("B) what OR=261 looks like in a 270 v 270 table, by number of carrier controls k")
for k in [1, 2, 3, 5]:
    odds_cases = OR * k / (N - k)
    a = N * odds_cases / (1 + odds_cases)
    print(f"   k={k} of {N} controls ({100*k/N:.2f}%): about {a:5.1f} of {N} patients carry it ({100*a/N:.0f}%)")

print("C) the comment's model: non-carriers at the EBV-negative risk (r0 = 1) forces f =", round((RR_EBV-1)/(OR-1), 4))
