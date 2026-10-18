#!/bin/bash
# Controls (known values), then the open cases of the COLT 2025 open problem table.
python3 -c "import numpy, scipy; print('numpy', numpy.__version__, 'scipy', scipy.__version__)"
for a in "1 2 2 4 30 1" "1 3 2 4 30 1" "2 2 2 6 40 1" \
         "2 3 2 8 60 1" "3 2 2 8 60 1" "2 4 2 7 60 1" "3 3 2 7 60 1" "4 2 2 8 60 1"; do
  python3 -u ds_search.py $a 2>/dev/null | grep -E "^d=|best over|certified|z ="
done
