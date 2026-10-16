#!/bin/bash
# Build erdos3.c; control against brute force (n <= u_9 = 13122); verify to depth K = $1;
# then the record sequence A351928 exactly up to m = $2 among n < N = $3.
set -e
gcc --version | head -1
gcc -O2 -fopenmp -o /tmp/erdos3 erdos3.c
export OMP_NUM_THREADS=$PHS_CPUS
echo "== control: brute force, then the program, n <= 13122"
python3 check.py brute 13122 9
/tmp/erdos3 verify 9 4 /tmp/fb9.txt
/tmp/erdos3 rho 9 13122 4 | tail -8
echo "== verify K = $1"
/tmp/erdos3 verify $1 12 /tmp/fb.txt
python3 check.py fallback /tmp/fb.txt
echo "== rho M = $2, N = $3"
/tmp/erdos3 rho $2 $3 12
