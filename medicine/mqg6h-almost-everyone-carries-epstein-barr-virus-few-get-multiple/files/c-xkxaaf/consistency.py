# Consistency check for p/mqg6h: does a 260-fold subgroup risk (Vietzen 2023,
# Cell, doi:10.1016/j.cell.2023.11.015) fit a 32-fold overall EBV effect
# (Bjornevik 2022, Science, quoted in the post summary) and population MS rates?

RR_E = 32.0   # overall relative risk of MS after EBV infection (post summary)
RR_S = 260.0  # 'up to' subgroup risk from Vietzen abstract (read via Europe PMC today)

print("=== Part A: what the 32-fold overall figure implies ===")
for p_E in [0.90, 0.93, 0.95]:
    ratio = p_E*RR_E + (1-p_E)*1.0
    print(f"p_E={p_E:.2f}: population MS rate / EBV-negative baseline rate = {ratio:.1f}x")
print("(so the EBV-positive group carries ~97-98% of all incident MS cases)")
for p_E in [0.93]:
    share_pos = p_E*RR_E/(p_E*RR_E + (1-p_E))
    print(f"share of MS cases among EBV-positive at p_E={p_E}: {share_pos:.4f}")

print()
print("=== Part B: what subgroup frequency f_S a 260-fold effect needs ===")
f_S_needed = (RR_E - 1.0)/(RR_S - 1.0)
print(f"f_S needed if subgroup alone explains the 32-fold: {f_S_needed:.4f} "
      f"= {f_S_needed*100:.2f}% of EBV-positive people")

print()
print("=== Part C: grid over plausible frequencies ===")
for p_E in [0.90, 0.93, 0.95]:
    for f_S in [0.001, 0.002, 0.004, 0.01, 0.02, 0.05, 0.10, 0.20]:
        implied = p_E*(f_S*RR_S + (1-f_S)*1.0) + (1-p_E)*1.0
        flag = " <-- matches observed ~29-31x" if abs(implied - (p_E*RR_E+(1-p_E))) < 0.5 else ""
        print(f"p_E={p_E:.2f} f_S={f_S:.3f}: implied population rate ratio {implied:6.1f}x{flag}")
    print()

print("=== Part D: absolute numbers, sanity check ===")
N = 10_000_000; cases = 955; p_E = 0.93
neg_rate = cases / (N*(p_E*RR_E + (1-p_E)))
pos_rate = neg_rate*RR_E
print(f"implied EBV-negative baseline incidence: {neg_rate:.2e}/person-cohort")
print(f"implied EBV-positive incidence:          {pos_rate:.2e}")
sub_inc = pos_rate*f_S_needed
print(f"if the 260x subgroup were all of it, its incidence would be {sub_inc:.2e}, "
      f"i.e. {f_S_needed*100:.2f}% of EBV+ people carrying RR=260")

print()
print("=== Part E: the key consistency result ===")
# If the subgroup is a fraction f_S of EBV-positive people and has RR_S,
# what overall ratio does it produce?  Compare to observed ~30x.
for f_S in [0.01, 0.02, 0.05, 0.10, 0.1197, 0.20]:
    implied = p_E*(f_S*RR_S + (1-f_S)*1.0) + (1-p_E)*1.0
    print(f"f_S={f_S:.4f}: implied overall ratio {implied:6.1f}x  "
          f"(observed ~{p_E*RR_E+(1-p_E):.1f}x)")
