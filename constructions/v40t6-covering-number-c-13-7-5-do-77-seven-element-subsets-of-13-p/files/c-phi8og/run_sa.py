# Runs cover_sa.py for several block counts and seeds in parallel; writes one output file per run.
import subprocess, sys
moves = sys.argv[1]
procs = []
for b in (78, 77):
    for seed in range(1, 11):
        f = open(f"sa_{b}_{seed}.txt", "w")
        procs.append(subprocess.Popen([sys.executable, "cover_sa.py", "13", "7", "5", str(b), str(seed), moves], stdout=f))
for p in procs:
    p.wait()
for b in (78, 77):
    for seed in range(1, 11):
        print(open(f"sa_{b}_{seed}.txt").readline().strip())
