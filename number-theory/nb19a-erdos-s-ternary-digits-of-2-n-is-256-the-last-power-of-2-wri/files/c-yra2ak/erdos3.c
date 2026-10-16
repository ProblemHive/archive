// erdos3.c - Saye's recursion (arXiv:2202.13256, Algorithm 1 with chi = 2) for Erdos's conjecture
// that 2^n has a ternary digit 2 for every n > 8.
// Arithmetic: 2^n mod 3^120, 6 limbs in base 3^20 (reducing mod 3^120 is truncation).
// Node (k, j): 0 <= j < u_k = 2*3^(k-1) with no 2 in the last k ternary digits of 2^j. Its children
// are j, j + u_k, j + 2u_k at depth k+1 (Saye, Lemma 3.1); the one whose digit k+1 is 2 is cut.
//
// Mode 'verify K D file': every node down to depth K, so every n <= u_K is covered. At depth K a node
//   whose 120 trailing digits avoid 2 is a candidate: if 2^j < 3^120 the whole number is known and
//   it is printed as CLEAN; otherwise j goes to 'file' for an exact check (check.py fallback).
//   Splits the tree at depth D for the threads.
// Mode 'rho M N D': every node down to depth M with j < N. For each m <= M, prints the smallest
//   j >= 1 with 2^j >= 3^(m-1) and no 2 in the last m digits (OEIS A351928), among j < N. Since the
//   search sees every such j below N, the value is exact whenever it is printed (it is < N).
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>
#define NL 6
#define B 3486784401ULL   /* 3^20 */
#define KAPPA (20 * NL)
typedef struct { uint64_t l[NL]; } num;
static uint64_t P3[20];
static num PU[KAPPA + 2], PU2[KAPPA + 2];
static uint64_t U[KAPPA + 2];
static int K, MODE; static uint64_t NB;
static const double LOG2_3 = 1.5849625007211562; /* log2(3): 2^j >= 3^(m-1) iff j >= (m-1)*log2(3) */

static num mul(const num *a, const num *b) {
    unsigned __int128 acc[NL] = {0};
    for (int i = 0; i < NL; i++)
        for (int j = 0; i + j < NL; j++)
            acc[i + j] += (unsigned __int128)a->l[i] * b->l[j];
    num r; unsigned __int128 carry = 0;
    for (int i = 0; i < NL; i++) { unsigned __int128 t = acc[i] + carry; r.l[i] = (uint64_t)(t % B); carry = t / B; }
    return r;
}
static inline int digit(const num *v, int i) { return (int)((v->l[(i - 1) / 20] / P3[(i - 1) % 20]) % 3); }

typedef struct { uint64_t best[KAPPA + 2]; uint64_t nodes, nfall; FILE *ff; } stats;

static void visit(int k, uint64_t j, const num *v, stats *s) {   /* node already known admissible */
    s->nodes++;
    if (j > 0 && (double)j >= (k - 1) * LOG2_3 && j < s->best[k]) s->best[k] = j;
    if (MODE == 0 && k == K) {
        int L = k;
        while (L < KAPPA && digit(v, L + 1) != 2) L++;
        if (L == KAPPA) {
            if ((double)j < KAPPA * LOG2_3) {
                #pragma omp critical
                printf("CLEAN n=%llu\n", (unsigned long long)j);
            } else {
                #pragma omp critical
                fprintf(s->ff, "%llu\n", (unsigned long long)j);
                s->nfall++;
            }
        }
    }
}
static void rec(int k, uint64_t j, num v, stats *s) {
    if (digit(&v, k) == 2) return;
    if (MODE == 1 && j >= NB) return;
    visit(k, j, &v, s);
    if (k >= K) return;
    rec(k + 1, j, v, s);
    if (MODE == 1 && !(U[k] < NB && j < NB - U[k])) return;      /* child j + u_k would be >= N */
    num c1 = mul(&v, &PU[k]);
    rec(k + 1, j + U[k], c1, s);
    if (MODE == 1 && !(U[k] < NB / 2 && j < NB - 2 * U[k])) return;
    num c2 = mul(&v, &PU2[k]);
    rec(k + 1, j + 2 * U[k], c2, s);
}
typedef struct { int k; uint64_t j; num v; } item;
static item *fr; static int nfr, cap;
static void collect(int k, uint64_t j, num v, int D, stats *s) {
    if (digit(&v, k) == 2) return;
    if (MODE == 1 && j >= NB) return;
    if (k == D) { if (nfr == cap) { cap = cap ? 2 * cap : 1024; fr = realloc(fr, cap * sizeof(item)); } fr[nfr++] = (item){k, j, v}; return; }
    visit(k, j, &v, s);
    collect(k + 1, j, v, D, s);
    if (MODE == 1 && !(U[k] < NB && j < NB - U[k])) return;
    num c1 = mul(&v, &PU[k]);
    collect(k + 1, j + U[k], c1, D, s);
    if (MODE == 1 && !(U[k] < NB / 2 && j < NB - 2 * U[k])) return;
    num c2 = mul(&v, &PU2[k]);
    collect(k + 1, j + 2 * U[k], c2, D, s);
}

int main(int argc, char **argv) {
    FILE *ff = NULL; int D;
    if (!strcmp(argv[1], "verify")) { MODE = 0; K = atoi(argv[2]); D = atoi(argv[3]); ff = fopen(argv[4], "w"); }
    else { MODE = 1; K = atoi(argv[2]); NB = strtoull(argv[3], 0, 10); D = atoi(argv[4]); }
    if (K > KAPPA - 1 || D >= K || (MODE == 0 && K > 40)) { fprintf(stderr, "bad arguments\n"); return 1; }
    P3[0] = 1; for (int i = 1; i < 20; i++) P3[i] = P3[i - 1] * 3;
    num four = {{4}}; U[1] = 2; PU[1] = four;          /* 2^{u_1} = 4, 2^{u_{k+1}} = (2^{u_k})^3 */
    for (int k = 1; k <= KAPPA; k++) {
        PU2[k] = mul(&PU[k], &PU[k]);
        if (k < KAPPA) { PU[k + 1] = mul(&PU2[k], &PU[k]); U[k + 1] = (k < 40) ? 3 * U[k] : UINT64_MAX; }
    }
    stats s0; memset(&s0, 0, sizeof s0); for (int m = 0; m <= KAPPA + 1; m++) s0.best[m] = UINT64_MAX; s0.ff = ff;
    double t0 = omp_get_wtime();
    num one = {{1}};
    collect(1, 0, one, D, &s0);
    uint64_t nodes = s0.nodes, nfall = s0.nfall, best[KAPPA + 2];
    for (int m = 0; m <= KAPPA + 1; m++) best[m] = s0.best[m];
    #pragma omp parallel
    {
        stats s; memset(&s, 0, sizeof s); for (int m = 0; m <= KAPPA + 1; m++) s.best[m] = UINT64_MAX; s.ff = ff;
        #pragma omp for schedule(dynamic, 1)
        for (int i = 0; i < nfr; i++) rec(fr[i].k, fr[i].j, fr[i].v, &s);
        #pragma omp critical
        { nodes += s.nodes; nfall += s.nfall; for (int m = 0; m <= KAPPA + 1; m++) if (s.best[m] < best[m]) best[m] = s.best[m]; }
    }
    if (ff) fclose(ff);
    if (MODE == 0) printf("verify K=%d: every n <= u_K = 2*3^%d = %llu checked\n", K, K - 1, (unsigned long long)U[K]);
    else printf("rho M=%d: every admissible j < N = %llu down to depth %d\n", K, (unsigned long long)NB, K);
    printf("threads=%d frontier=%d nodes=%llu fallback=%llu time=%.1f s\n", omp_get_max_threads(), nfr,
           (unsigned long long)nodes, (unsigned long long)nfall, omp_get_wtime() - t0);
    if (MODE == 1)
        for (int m = 2; m <= K; m++)
            if (best[m] != UINT64_MAX) printf("A351928(%d) = %llu\n", m, (unsigned long long)best[m]);
            else printf("A351928(%d) >= %llu\n", m, (unsigned long long)NB);
    return 0;
}
