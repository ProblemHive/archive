# Runs heil_scip2.py for several n at once, one SCIP process each, and prints the RESULT lines.
# usage: python run_all.py timelimit
import subprocess, sys
tl = sys.argv[1]
D8 = (13 ** 0.5 - 1) / 36
D9 = -11 / 64 + 9 * 65 ** 0.5 / 320
jobs = [  # n, tmin, tmax
    (7, 0.0, 0.125),
    (8, 0.0, 0.0838591),
    (9, 0.0, D8 + 1e-7),
    (9, 0.0548, D8 + 1e-7),
    (10, 0.0, D9 + 1e-7),
    (10, 0.0465, D9 + 1e-7),
]
procs = []
for idx, (n, tmin, tmax) in enumerate(jobs):
    out = open("rpo3b/scip_n%d_job%d.log" % (n, idx), "w")
    procs.append((subprocess.Popen([sys.executable, "rpo3b/heil_scip2.py", str(n), tl, repr(tmin), repr(tmax)],
                                   stdout=out, stderr=subprocess.STDOUT), out, n, idx))
for p, out, n, idx in procs:
    p.wait(); out.close()
    for line in open("rpo3b/scip_n%d_job%d.log" % (n, idx)):
        if line.startswith("RESULT") or line.startswith("points"):
            print(line.rstrip(), flush=True)
