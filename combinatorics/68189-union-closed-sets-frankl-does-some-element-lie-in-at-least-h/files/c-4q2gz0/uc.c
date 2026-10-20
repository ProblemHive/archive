// Enumerate every union-closed family F of subsets of [n] (labelled), n <= 5,
// and record the largest element frequency. Sets are bitmasks 0..2^n-1.
// Sets are decided in increasing numeric order; s is forced into F iff s = a|b
// for two members a,b already decided (all proper subsets of s are < s).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int n, N;
static unsigned long long total, withnonempty, hit_half, below_half;
static int in[64];
static int cnt[64][1]; // unused
// best[k] = minimum over families of size k (with a nonempty set) of max frequency
static int best[65];
static unsigned long long nbest[65];   // how many families of size k attain best[k]

static void leaf(void) {
    total++;
    int size = 0, freq[8] = {0};
    int nonempty = 0;
    for (int s = 0; s < N; s++) if (in[s]) {
        size++;
        if (s) nonempty = 1;
        for (int i = 0; i < n; i++) if (s >> i & 1) freq[i]++;
    }
    if (!nonempty) return;
    withnonempty++;
    int mx = 0;
    for (int i = 0; i < n; i++) if (freq[i] > mx) mx = freq[i];
    if (2 * mx == size) hit_half++;
    if (2 * mx < size) below_half++;
    if (best[size] < 0 || mx < best[size]) { best[size] = mx; nbest[size] = 1; }
    else if (mx == best[size]) nbest[size]++;
}

static void dfs(int s) {
    if (s == N) { leaf(); return; }
    int forced = 0;
    for (int a = 0; a < s && !forced; a++) {
        if (!in[a] || (a & ~s)) continue;
        for (int b = a; b < s; b++) {
            if (in[b] && !(b & ~s) && (a | b) == s) { forced = 1; break; }
        }
    }
    in[s] = 1; dfs(s + 1);
    if (!forced) { in[s] = 0; dfs(s + 1); }
    in[s] = 0;
}

int main(int argc, char **argv) {
    n = atoi(argv[1]); N = 1 << n;
    memset(best, -1, sizeof best);
    dfs(0);
    printf("n=%d union-closed families (incl. empty family and {{}}): %llu\n", n, total);
    printf("  with a nonempty set: %llu\n", withnonempty);
    printf("  max element frequency < 1/2 (counterexamples): %llu\n", below_half);
    printf("  max element frequency exactly 1/2: %llu\n", hit_half);
    printf("  size k: min over families of (max freq)/k, and how many families attain it\n");
    for (int k = 1; k <= N; k++) if (best[k] >= 0)
        printf("   k=%2d min maxfreq=%2d  ratio=%.4f  attained by %llu\n", k, best[k], (double)best[k] / k, nbest[k]);
    return 0;
}

