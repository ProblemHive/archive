F=96485.33212  # C/mol
for rate in (1.7,18.0):               # mmol O2 m-2 d-1, range reported for DOP
    mol=rate*1e-3
    q=4*mol*F                          # C m-2 d-1 (4 electrons per O2)
    i=q/86400                          # A m-2
    for V in (1.23,0.95,0.24):
        print(f"rate {rate:5.1f} mmol/m2/d  charge {q:8.1f} C/m2/d  current {i*1e3:7.3f} mA/m2  power at {V} V: {i*V*1e3:7.3f} mW/m2")
