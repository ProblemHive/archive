#!/bin/bash
# The open case ES(7) <= 33 in reduced form: 32 points, no convex 7-gon, no 6-cap.
# Control: 31 points (32 original points, ES(7) >= 33 so it must be SAT). Argument 1: conflict limit for N = 32.
LIMIT=$1
kissat --version | head -1
python es_hull.py 31 7 /tmp/h31.cnf
s=$(date +%s); kissat -q --conflicts=$LIMIT /tmp/h31.cnf > /tmp/m31.txt; r=$?; e=$(date +%s)
echo "N=31 K=7 (original n=32) exit $r time $((e-s)) s"
python es_hull.py 32 7 /tmp/h32.cnf
s=$(date +%s); kissat --conflicts=$LIMIT /tmp/h32.cnf > /tmp/k32.txt; r=$?; e=$(date +%s)
echo "N=32 K=7 (original n=33) exit $r time $((e-s)) s (conflict limit $LIMIT)"
grep -E "^c (conflicts|decisions|process-time)" /tmp/k32.txt | head -3
tail -1 /tmp/k32.txt
