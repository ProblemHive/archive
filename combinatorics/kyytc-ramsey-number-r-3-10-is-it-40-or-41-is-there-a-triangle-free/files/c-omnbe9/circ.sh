#!/bin/bash
# Controls on solved cases, then R(3,10) at 38, 39 and 40 vertices. Arguments of circ: n t R(3,t-1)-1
gcc --version | head -1
gcc -O2 -o /tmp/circ circ.c
# controls: R(3,4)=9 (R(3,3)-1=5), R(3,5)=14 (R(3,4)-1=8), R(3,6)=18 (R(3,5)-1=13), R(3,8)=28 (R(3,7)-1=22), R(3,9)=36 (R(3,8)-1=27)
for a in "8 4 5" "9 4 5" "13 5 8" "14 5 8" "16 6 13" "17 6 13" "26 8 22" "27 8 22" "35 9 27" "36 9 27"; do
  /tmp/circ $a | tail -3
done
for a in "38 10 35" "39 10 35" "40 10 35"; do
  s=$(date +%s); /tmp/circ $a | tail -5; e=$(date +%s); echo "time $((e-s)) s"
done
