# Build the import closure of OAI.Geometry.PlaneColoring.Five (openai/math, result 158) with the
# sandbox's Lean and Mathlib. Files are compiled unchanged, each to an .olean under 1hx33/build.
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, FIRST_COMPLETED, wait

SRC = "/work/1hx33/oai"
OUT = "/work/1hx33/build"
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 26 * 60
WORKERS = 6
T0 = time.time()

mods = [l.strip() for l in open("/work/1hx33/order158.txt") if l.strip()]
path = lambda m, root, ext: os.path.join(root, *m.split(".")) + ext
deps = {}
flags = []
FLAG = re.compile(r"\bsorry\b|^\s*axiom\b|native_decide|\bunsafe\b|implemented_by|run_cmd|#eval|\bIO\.|^\s*initialize\b|^\s*(elab|macro|syntax)\b|open Lean\b|extern")
for m in mods:
    d = []
    for n, line in enumerate(open(path(m, SRC, ".lean"), encoding="utf-8"), 1):
        g = re.match(r"\s*(?:public\s+)?import\s+(\S+)", line)
        if g:
            if g.group(1) != "Mathlib":
                d.append(g.group(1))
        if FLAG.search(line):
            flags.append(f"{m}:{n}: {line.strip()[:120]}")
    deps[m] = d
print("modules:", len(mods), " lines:", sum(sum(1 for _ in open(path(m, SRC, '.lean'), encoding='utf-8')) for m in mods))
print("lines matching sorry/axiom/native_decide/unsafe/implemented_by/run_cmd/#eval/IO/initialize/elab/macro/syntax/extern:", len(flags))
for f in flags[:30]:
    print("  ", f)
sys.stdout.flush()


def build(m):
    o = path(m, OUT, ".olean")
    if os.path.exists(o):
        return m, 0, 0.0, "cached"
    os.makedirs(os.path.dirname(o), exist_ok=True)
    t = time.time()
    p = subprocess.run(["lean", "--root=" + SRC, "-o", o + ".tmp", path(m, SRC, ".lean")], capture_output=True, text=True)
    if p.returncode == 0:
        os.replace(o + ".tmp", o)
    elif os.path.exists(o + ".tmp"):
        os.remove(o + ".tmp")
    return m, p.returncode, time.time() - t, (p.stdout + p.stderr)


done, failed, running, log = set(), {}, {}, []
with ThreadPoolExecutor(WORKERS) as ex:
    while len(done) + len(failed) < len(mods):
        if time.time() - T0 < BUDGET and not failed:
            for m in mods:
                if m not in done and m not in failed and m not in running.values() and all(d in done for d in deps[m]) and len(running) < WORKERS:
                    running[ex.submit(build, m)] = m
        if not running:
            break
        fin, _ = wait(list(running), return_when=FIRST_COMPLETED)
        for f in fin:
            del running[f]
            m, rc, dt, out = f.result()
            warn = len(re.findall(r"warning:", out))
            if rc == 0:
                done.add(m)
                print(f"ok   {dt:7.1f}s  {m}" + (f"  ({warn} warnings)" if warn else "") + ("  [cached]" if out == "cached" else ""))
            else:
                failed[m] = out
                print(f"FAIL {dt:7.1f}s  {m}")
                print("\n".join(out.splitlines()[:25]))
            sys.stdout.flush()
print(f"built {len(done)} of {len(mods)}; failed {len(failed)}; not attempted {len(mods) - len(done) - len(failed)}; wall {time.time() - T0:.0f} s")
