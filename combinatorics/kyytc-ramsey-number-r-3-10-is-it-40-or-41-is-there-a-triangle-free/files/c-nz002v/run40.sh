#!/bin/bash
# Block-circulant (3,10)-graphs on 39 and 40 vertices: a semiregular cyclic automorphism with m orbits of size n.
# Controls first (solved cases: FOUND at R(3,t)-1 vertices, UNSAT at R(3,t)), then the open cases.
# Each case is cut off after 300 s (timeout); a case cut off is undecided, not UNSAT.
python3 -c "import pysat; print('python-sat', pysat.__version__)"
for a in "1 13 5" "1 14 5" "2 8 6" "2 9 6" "3 6 6" "2 13 8" "2 14 8" "5 7 9" "1 38 10" "1 39 10" "1 40 10"; do
  timeout 300 python3 -u blockcirc.py $a 1000000000 20 | grep -v -E "^  (edge class|\.\.\.)"
done
for a in "2 20 10" "3 13 10" "4 10 10" "5 8 10" "8 5 10"; do
  s=$(date +%s)
  timeout 300 python3 -u blockcirc.py $a 1000000000 20 | grep -v -E "^  (edge class|\.\.\.)"
  echo "  (m n t = $a: $(( $(date +%s) - s )) s wall; no result line means cut off at 300 s)"
done
