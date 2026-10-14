# calib.py - calibration of schur_sat.py where the answer is known, then the six-colour record size.
from schur_sat import run
import subprocess
print(subprocess.run(["kissat", "--version"], capture_output=True, text=True).stdout.strip(), flush=True)
run(3, 13, 60, 1); run(3, 14, 60, 1)
run(4, 44, 60, 1); run(4, 45, 60, 1)
run(4, 44, 60, 1, sym=False); run(4, 45, 300, 1, sym=False)
for n in (150, 155, 158, 159, 160, 161, 162):
    run(5, n, 200, 8)
