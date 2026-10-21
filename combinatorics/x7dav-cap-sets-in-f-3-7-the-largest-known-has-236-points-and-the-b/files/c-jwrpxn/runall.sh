#!/bin/bash
# 8 seeds per dimension, run in parallel; prints the best size per seed
for spec in "5 2000000" "6 4000000" "7 3000000"; do
  set -- $spec
  echo "== n=$1 iterations=$2"
  seq 1 8 | xargs -P 8 -I{} sh -c "./capls $1 {} $2 | head -1"
done

