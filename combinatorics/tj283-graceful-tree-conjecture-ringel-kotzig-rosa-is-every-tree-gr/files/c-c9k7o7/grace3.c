// Graceful labelling search, version 3. The edge with difference n-1 must join labels 0 and n-1,
// so each restart picks a random edge (a,b), sets f(a)=0, f(b)=n-1, and extends by depth-first search
// in breadth-first order from that edge, trying differences in random order, with a node limit.
// A tree counts as labelled only if a labelling is found AND an independent check passes.
// usage: ./grace3 trees<n>.txt n [restart_node_limit] [max_restarts]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int n, par0[64], adj[64][64], deg[64];
int ord[64], par[64], lab[64], usedL[64], usedD[64];
long long nodes, limit;
unsigned long long rs = 88172645463325252ULL;
static unsigned rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (unsigned)(rs >> 11); }
int dfs(int k) {
    if (k == n) return 1;
    if (++nodes > limit) return -1;
    int v = ord[k], p = lab[par[v]];
    int dl[64], m = n - 1;
    for (int i = 0; i < m; i++) dl[i] = i + 1;
    for (int i = m - 1; i > 0; i--) { int j = rnd() % (i + 1); int t = dl[i]; dl[i] = dl[j]; dl[j] = t; }
    for (int q = 0; q < m; q++) {
        int d = dl[q];
        if (usedD[d]) continue;
        for (int s = -1; s <= 1; s += 2) {
            int l = p + s * d;
            if (l < 0 || l >= n || usedL[l]) continue;
            usedL[l] = 1; usedD[d] = 1; lab[v] = l;
            int r = dfs(k + 1);
            if (r == 1) return 1;
            usedL[l] = 0; usedD[d] = 0;
            if (r == -1) return -1;
        }
    }
    return 0;
}
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r");
    n = atoi(argv[2]);
    limit = argc > 3 ? atoll(argv[3]) : 2000;
    int maxr = argc > 4 ? atoi(argv[4]) : 20000;
    long long total = 0, ok = 0, unf = 0, maxrestarts = 0;
    int ea[64], eb[64];
    while (1) {
        int good = 1;
        for (int i = 1; i < n; i++) if (fscanf(f, "%d", &par0[i]) != 1) { good = 0; break; }
        if (!good) break;
        total++;
        memset(deg, 0, sizeof deg);
        for (int i = 1; i < n; i++) { ea[i-1] = par0[i]; eb[i-1] = i; adj[par0[i]][deg[par0[i]]++] = i; adj[i][deg[i]++] = par0[i]; }
        int found = 0, tries = 0;
        while (!found && tries < maxr) {
            tries++;
            int e = rnd() % (n - 1), a = ea[e], b = eb[e];
            if (rnd() & 1) { int t = a; a = b; b = t; }
            // BFS order from the edge (a,b)
            int seen[64] = {0}, qh = 0, qt = 0;
            ord[qt++] = a; seen[a] = 1; par[a] = -1;
            ord[qt++] = b; seen[b] = 1; par[b] = a;
            qh = 0;
            while (qh < qt) { int u = ord[qh++]; for (int i = 0; i < deg[u]; i++) { int w = adj[u][i]; if (!seen[w]) { seen[w] = 1; par[w] = u; ord[qt++] = w; } } }
            memset(usedL, 0, sizeof usedL); memset(usedD, 0, sizeof usedD);
            lab[a] = 0; lab[b] = n - 1; usedL[0] = usedL[n-1] = 1; usedD[n-1] = 1; nodes = 0;
            if (dfs(2) == 1) found = 1;
        }
        if (tries > maxrestarts) maxrestarts = tries;
        if (found) {
            int seenD[64] = {0}, seenL[64] = {0}, okk = 1;
            for (int i = 0; i < n; i++) { if (lab[i] < 0 || lab[i] >= n || seenL[lab[i]]) okk = 0; else seenL[lab[i]] = 1; }
            for (int i = 1; i < n; i++) { int d = abs(lab[i] - lab[par0[i]]); if (d < 1 || d > n - 1 || seenD[d]) okk = 0; else seenD[d] = 1; }
            if (!okk) { printf("CHECK FAILED tree %lld\n", total); return 1; }
            ok++;
        } else { unf++; printf("not found after %d restarts: tree %lld\n", maxr, total); }
    }
    printf("n=%d trees=%lld labelled=%lld unlabelled=%lld max_restarts_used=%lld\n", n, total, ok, unf, maxrestarts);
    return 0;
}
