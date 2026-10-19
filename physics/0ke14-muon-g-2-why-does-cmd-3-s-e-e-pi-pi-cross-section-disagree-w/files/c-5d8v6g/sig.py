from math import sqrt, erfc
cmd3,s3=5260,42      # a_mu(2pi) CMD-3, units 1e-11 (arXiv:2309.12910)
old,so=5060,34       # average of all previous measurements, error inflated (same paper)
d=cmd3-old; e=sqrt(s3**2+so**2); z=d/e
print("difference %d (x1e-11), combined error %.1f, %.2f sigma, two-sided p=%.1e"%(d,e,z,erfc(z/sqrt(2))))
print("difference in relative terms: %.2f%% of the older average"%(100*d/old))
# if CMD-3 replaced the old 2pi value in the total: shift of a_mu SM prediction
print("shift of a_mu^SM if 2pi swapped: +%d x1e-11 ; white paper exp-SM = 38(63) x1e-11 (lattice-based)"%d)

