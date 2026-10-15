#!/bin/bash
# Checks the encoding on the known values ES(4)=5, ES(5)=9, ES(6)=17 (the 17-point case is not run here).
kissat --version | head -1
for nk in "4 4" "5 4" "8 5" "9 5" "16 6"; do
  set -- $nk
  python es_cnf.py $1 $2 /tmp/es_$1_$2.cnf
  s=$(date +%s.%N)
  kissat -q /tmp/es_$1_$2.cnf > /tmp/out_$1_$2.txt; r=$?
  e=$(date +%s.%N)
  echo "n=$1 K=$2 exit=$r ($( [ $r = 10 ] && echo SAT || ([ $r = 20 ] && echo UNSAT || echo unknown))) time=$(echo "$e - $s" | bc) s"
done
