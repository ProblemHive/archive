#!/bin/bash
# n=4, m=10 (the first case not covered by arXiv:2608.08590): 8 independent searches of 420 s each
for s in 1 2 3 4; do ./efx 4 10 10 $s 420 > r10_V10_s$s.txt & done
for s in 5 6 7 8; do ./efx 4 10 4 $s 420 > r10_V4_s$s.txt & done
wait
cat r10_*.txt
