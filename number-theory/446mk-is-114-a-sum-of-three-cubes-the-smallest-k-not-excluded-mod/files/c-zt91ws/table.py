import sys
rows = [tuple(map(int, l.split())) for l in open(sys.argv[1])]
tot = len(rows)
print("n in 1..999 with n mod 9 not 4,5:", tot)
for B in (10, 30, 100, 300, 1000, 2000):
    got = sum(1 for n, h in rows if 0 < h <= B)
    print(f"solved with max|coordinate| <= {B}: {got}  unsolved: {tot-got}")
miss = [n for n, h in rows if h == 0]
print("no solution with max|coordinate| <= 2000:", len(miss), miss)
big = sorted((h, n) for n, h in rows if h > 300)
print("largest first-solution heights (height, n):", big[-12:])
