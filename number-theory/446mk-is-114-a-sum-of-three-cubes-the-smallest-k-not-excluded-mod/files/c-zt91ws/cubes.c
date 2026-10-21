// For every n in 1..NMAX with n mod 9 not in {4,5}: the smallest H = max(|x|,|y|,|z|) <= B
// such that x^3+y^3+z^3 = n has a solution. Exact 64-bit integer arithmetic (B <= 2000: |x^3+y^3| <= 1.6e10).
// Method: sort all sums x^3+y^3 (x<=y, |x|,|y|<=B), then for each n and each z look up n - z^3.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef struct { int64_t s; int16_t x, y; } P;
static int cmp(const void *a, const void *b) {
    int64_t u = ((const P*)a)->s, v = ((const P*)b)->s;
    return (u > v) - (u < v);
}
int main(int argc, char **argv) {
    int B = atoi(argv[1]), NMAX = atoi(argv[2]);
    size_t cnt = 0, cap = (size_t)(2*B+1)*(2*B+2)/2;
    P *p = malloc(cap * sizeof(P));
    for (int x = -B; x <= B; x++) for (int y = x; y <= B; y++) {
        p[cnt].s = (int64_t)x*x*x + (int64_t)y*y*y; p[cnt].x = x; p[cnt].y = y; cnt++;
    }
    qsort(p, cnt, sizeof(P), cmp);
    int *best = calloc(NMAX+1, sizeof(int));  // smallest height found, 0 = none
    int bx[2000+1][1]; (void)bx;
    long nsol = 0;
    for (int n = 1; n <= NMAX; n++) {
        int r = ((n % 9) + 9) % 9;
        if (r == 4 || r == 5) continue;
        for (int z = -B; z <= B; z++) {
            int64_t t = (int64_t)n - (int64_t)z*z*z;
            size_t lo = 0, hi = cnt;
            while (lo < hi) { size_t m = (lo+hi)/2; if (p[m].s < t) lo = m+1; else hi = m; }
            for (size_t i = lo; i < cnt && p[i].s == t; i++) {
                int h = abs(p[i].x); if (abs(p[i].y) > h) h = abs(p[i].y); if (abs(z) > h) h = abs(z);
                if (best[n] == 0 || h < best[n]) best[n] = h;
                nsol++;
                // verify independently
                __int128 chk = (__int128)p[i].x*p[i].x*p[i].x + (__int128)p[i].y*p[i].y*p[i].y + (__int128)z*z*z;
                if (chk != n) { printf("BAD n=%d\n", n); return 1; }
            }
        }
    }
    for (int n = 1; n <= NMAX; n++) {
        int r = ((n % 9) + 9) % 9;
        if (r == 4 || r == 5) continue;
        printf("%d %d\n", n, best[n]);
    }
    fprintf(stderr, "ordered-by-z solution count (each unordered triple counted by its z): %ld\n", nsol);
    return 0;
}
