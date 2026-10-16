#!/bin/bash
# Reduced formulas (hull vertex sent to infinity): controls, then the 17-point case of ES(6), with a DRAT proof checked by drat-trim.
# Argument 1: conflict limit for the 16-point (= 17-point original) case.
LIMIT=$1
kissat --version | head -1
for nk in "4 5" "8 5" "15 6"; do
  set -- $nk
  python es_hull.py $1 $2 /tmp/h_$1_$2.cnf
  kissat -q /tmp/h_$1_$2.cnf > /tmp/hm_$1_$2.txt; r=$?
  echo "N=$1 K=$2 (original n=$(($1+1))) exit=$r"
done
python es_hull.py 16 6 /tmp/h16.cnf
s=$(date +%s); kissat -q --conflicts=$LIMIT /tmp/h16.cnf /tmp/h16.drat --no-binary > /tmp/k16.txt; r=$?; e=$(date +%s)
echo "N=16 K=6 (original n=17) exit $r time $((e-s)) s (conflict limit $LIMIT)"
tail -1 /tmp/k16.txt
if [ $r = 20 ]; then
  ls -la /tmp/h16.drat | awk '{print "proof bytes", $5}'
  s=$(date +%s); drat-trim /tmp/h16.cnf /tmp/h16.drat | grep -E "^s |VERIFIED"; e=$(date +%s)
  echo "drat-trim time $((e-s)) s"
fi
