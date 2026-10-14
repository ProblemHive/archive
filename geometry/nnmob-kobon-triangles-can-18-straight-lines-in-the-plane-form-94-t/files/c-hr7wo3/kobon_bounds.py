# kobon_bounds.py - the three upper bounds for Kobon triangles side by side, even n.
# tamura: floor(n(n-2)/3), all arrangements.
# cb:     Clement-Bader (unpublished draft, 2007): tamura - 1 when n mod 6 is 0 or 2, all arrangements.
# bbl:    Bartholdi-Blanc-Loisel Theorem 1.1: floor(n(n-7/3)/3), proved for SIMPLE arrangements, n even.
# simple: best simple pseudoline arrangement, from the table in their Theorem 1.4 ("x-y" = found x, bound y).
# oeis:   value or lower bound in OEIS A006066 (read 2026-10-07).
simple = {4: '2', 6: '7', 8: '14', 10: '25', 12: '37', 14: '53', 16: '72', 18: '93-94', 20: '116-117', 22: '143-144', 24: '172-173'}
oeis = {4: '2', 6: '7', 8: '15', 10: '25', 12: '38', 14: '54', 16: '72', 18: '>=93', 20: '117', 22: '>=143', 24: '>=172'}
print(' n  tamura  cb  bbl  simple   oeis')
for n in range(4, 26, 2):
    tamura = n * (n - 2) // 3
    cb = tamura - (1 if n % 6 in (0, 2) else 0)
    bbl = (3 * n * n - 7 * n) // 9          # floor(n(n-7/3)/3) in integers
    print(f'{n:2d}  {tamura:6d} {cb:3d} {bbl:4d}  {simple[n]:>7s}  {oeis[n]:>5s}')
