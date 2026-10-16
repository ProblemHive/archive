/* Exhaustive search over circulant graphs C_n(S): is there one with no triangle and no independent set of t vertices?
   S is a symmetric subset of Z_n \ {0} (S = -S). Triangle-free <=> no x, y in S (x = y allowed) with x + y in S (mod n).
   Circulants are vertex-transitive, so an independent t-set exists iff one exists containing vertex 0.
   Degree range used to prune: deg <= t - 1 (neighbourhood is independent) and n - 1 - deg <= R(3,t-1) - 1 (given as rmin1).
   Usage: ./circ n t rmin1     (rmin1 = R(3,t-1) - 1, e.g. 35 for t = 10)
   Prints every connection set found (one representative per set, no isomorphism reduction) and the counts. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static int n, t;
static uint64_t adj[64];

/* is there an independent set of size need inside cand (bitmask), all vertices > last? simple branch and bound */
static int indep(uint64_t cand, int need) {
    if (need == 0) return 1;
    if (__builtin_popcountll(cand) < need) return 0;
    while (cand) {
        if (__builtin_popcountll(cand) < need) return 0;
        int v = __builtin_ctzll(cand);
        cand &= cand - 1;
        if (indep(cand & ~adj[v], need - 1)) return 1;
    }
    return 0;
}

int main(int argc, char **argv) {
    n = atoi(argv[1]); t = atoi(argv[2]); int rmin1 = atoi(argv[3]);
    int half = n / 2;               /* distances 1..half; distance n/2 (n even) is its own negative */
    long tried = 0, trianglefree = 0, inrange = 0, found = 0;
    for (long mask = 1; mask < (1L << half); mask++) {
        int inS[64] = {0};
        int deg = 0;
        for (int d = 1; d <= half; d++) if (mask >> (d - 1) & 1) {
            inS[d] = 1; inS[n - d] = 1;
            deg += (2 * d == n) ? 1 : 2;
        }
        tried++;
        int ok = 1;
        for (int x = 1; x < n && ok; x++) if (inS[x])
            for (int y = x; y < n; y++) if (inS[y] && inS[(x + y) % n]) { ok = 0; break; }
        if (!ok) continue;
        trianglefree++;
        if (deg > t - 1 || n - 1 - deg > rmin1) continue;
        inrange++;
        for (int v = 0; v < n; v++) {
            adj[v] = 0;
            for (int w = 0; w < n; w++) if (w != v && inS[((w - v) % n + n) % n]) adj[v] |= 1ULL << w;
        }
        uint64_t cand = 0;
        for (int w = 1; w < n; w++) if (!inS[w]) cand |= 1ULL << w;
        if (!indep(cand, t - 1)) {
            found++;
            printf("FOUND n=%d degree %d S = {", n, deg);
            for (int d = 1; d <= half; d++) if (inS[d]) printf(" %d", d);
            printf(" } (and negatives)\n");
        }
    }
    printf("n=%d t=%d: %ld connection sets, %ld triangle-free, %ld with degree in range, %ld with no independent %d-set\n",
           n, t, tried, trianglefree, inrange, found, t);
    return 0;
}
