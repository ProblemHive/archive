#!/bin/bash
# degrees 6 to 12, 300 random starts each, seed 2026, one process per degree
for d in 6 7 8 9 10 11 12; do
  python3 -u smvc_search.py $d 300 2026 > out_d$d.txt &
done
wait
cat out_d6.txt out_d7.txt out_d8.txt out_d9.txt out_d10.txt out_d11.txt out_d12.txt
