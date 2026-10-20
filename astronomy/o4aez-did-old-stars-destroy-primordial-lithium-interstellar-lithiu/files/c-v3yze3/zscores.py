import math
chain = (3.27, -1.18, 0.07)       # Molaro et al. 2024 eq. 3: A(Li)sun, [K/H], [Li/K]
errs = (0.03, 0.09, 0.08)
a = sum(chain); s = math.sqrt(sum(e * e for e in errs))
print(f"eq.3 chain: {a:.2f} +- {s:.3f}  (paper: 2.16 +- 0.12)")
meas = [("Molaro 2024, gas K", 2.16, 0.12), ("De Cia metallicity route", 2.25, 0.25),
        ("Howk 2012", 2.68, 0.16), ("halo plateau, Matas Pinto 2021", 2.16, 0.07)]
bbn = [("Yeh 2021", 2.69, 0.14), ("Pitrou 2021", 2.74, 0.17)]
for n, x, sx in meas:
    row = ", ".join(f"{bn} {(b - x) / math.hypot(sx, sb):+.2f} sigma" for bn, b, sb in bbn)
    print(f"{n:34s} A(Li)={x:.2f}+-{sx:.2f}: BBN minus value in sigma: {row}")
for bn, b, sb in bbn:
    print(f"{bn}: needed [K/H] = {b - 3.27 - 0.07:+.2f}")
