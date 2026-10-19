/* Count Costas permutations of order n by row-by-row backtracking and count search nodes.
   usage: ./costas n   -> prints n, count, nodes, seconds
   Placing values p[0..k-1]; a new value p[k] is allowed when for every d=1..k the difference
   p[k]-p[k-d] has not been used at distance d. used[d][diff+n] marks it. */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define MAXN 40
static int n, p[MAXN], usedv[MAXN];
static unsigned char used[MAXN][2 * MAXN + 1];
static unsigned long long count = 0, nodes = 0;

static void rec(int k) {
    if (k == n) { count++; return; }
    for (int v = 0; v < n; v++) {
        if (usedv[v]) continue;
        int ok = 1, d;
        for (d = 1; d <= k; d++) {
            if (used[d][v - p[k - d] + n]) { ok = 0; break; }
        }
        if (!ok) continue;
        nodes++;
        p[k] = v; usedv[v] = 1;
        for (d = 1; d <= k; d++) used[d][v - p[k - d] + n] = 1;
        rec(k + 1);
        for (d = 1; d <= k; d++) used[d][v - p[k - d] + n] = 0;
        usedv[v] = 0;
    }
}

int main(int argc, char **argv) {
    n = atoi(argv[1]);
    clock_t t0 = clock();
    rec(0);
    printf("n=%d count=%llu nodes=%llu seconds=%.2f\n", n, count, nodes, (double)(clock() - t0) / CLOCKS_PER_SEC);
    return 0;
}

