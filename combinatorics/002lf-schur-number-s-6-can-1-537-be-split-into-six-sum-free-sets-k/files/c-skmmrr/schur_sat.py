# schur_sat.py - symmetric sum-free colourings of 1..n with k colours, as a SAT problem for Kissat.
# Symmetric: i and n + 1 - i share a colour; when 3 divides n + 1, the numbers (n+1)/3 and 2(n+1)/3
# are coloured separately (the exception Fredricksen and Sweet allow).
# Variables: one per (class, colour). Clauses: each class has a colour; for every x <= y with
# x + y <= n and every colour c, not all of x, y, x + y in c. Colour of 1 is fixed to the first colour.
# Usage: python schur_sat.py K N SECONDS SEEDS [plain]
#   runs SEEDS copies of kissat in parallel with different seeds, each for at most SECONDS.
#   "plain" drops the symmetry (one class per number).
import subprocess, sys, time, os

def build(k, n, sym=True):
    m = n + 1
    free = {m // 3, 2 * m // 3} if (sym and m % 3 == 0) else set()
    rep = {}
    for i in range(1, n + 1):
        rep[i] = i if (not sym or i in free) else min(i, m - i)
    ids = {r: j for j, r in enumerate(sorted(set(rep.values())))}
    var = lambda i, c: ids[rep[i]] * k + c + 1
    clauses = set()
    for r in ids:
        clauses.add(tuple(var(r, c) for c in range(k)))
    for x in range(1, n + 1):
        for y in range(x, n + 1 - x):
            for c in range(k):
                clauses.add(tuple(sorted({-var(x, c), -var(y, c), -var(x + y, c)})))
    clauses.add((var(1, 0),))
    return len(ids) * k, sorted(clauses), var

def check(col, n):
    return sum(1 for x in range(1, n + 1) for y in range(x, n + 1 - x) if col[x] == col[y] == col[x + y])

def run(k, n, secs, seeds, sym=True):
    nv, cl, var = build(k, n, sym)
    name = f"schur_{k}_{n}_{'sym' if sym else 'plain'}.cnf"
    with open(name, "w") as f:
        f.write(f"p cnf {nv} {len(cl)}\n")
        for c in cl:
            f.write(" ".join(map(str, c)) + " 0\n")
    t0 = time.time()
    procs = [subprocess.Popen(["kissat", "-q", f"--seed={s}", f"--time={secs}", name],
                              stdout=subprocess.PIPE, text=True) for s in range(seeds)]
    result, model = "UNKNOWN (time limit)", None
    done = set()
    while len(done) < len(procs) and model is None and not result.startswith("UNSAT"):
        time.sleep(0.5)
        for j, p in enumerate(procs):
            if j in done or p.poll() is None:
                continue
            done.add(j)
            out = p.stdout.read()
            if "s SATISFIABLE" in out:
                lits = [int(t) for line in out.splitlines() if line.startswith("v ") for t in line[2:].split()]
                model = {l for l in lits if l > 0}
                result = f"SAT (seed {j})"
            elif "s UNSATISFIABLE" in out:
                result = f"UNSAT (seed {j})"
    for p in procs:
        if p.poll() is None:
            p.kill()
    line = f"k={k} n={n} {'symmetric' if sym else 'plain'}: {nv} variables, {len(cl)} clauses, {seeds} seeds x {secs}s: {result}, {time.time() - t0:.0f}s"
    if model:
        col = [None] + [next(c for c in range(k) if var(i, c) in model) for i in range(1, n + 1)]
        line += f"; re-check over the integers: {check(col, n)} monochromatic x + y = z"
        print(line, flush=True)
        print("  " + "".join("ABCDEFG"[c] for c in col[1:]), flush=True)
    else:
        print(line, flush=True)
    os.remove(name)

if __name__ == "__main__":
    k, n, secs, seeds = map(int, sys.argv[1:5])
    run(k, n, secs, seeds, sym=(len(sys.argv) < 6))
