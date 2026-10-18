// Enumerate all numerical semigroups of genus <= G (the tree of Rosales et al.,
// with the decomposition numbers of Fromentin and Hivert), check Wilf's inequality
// e*L >= c (e embedding dimension, c conductor, L = c - g = number of elements below c),
// count the cases of equality, and count, per genus, the semigroups that no
// published general theorem covers:
//   c <= 3m (Eliahou 2018), 3e >= m (Eliahou 2020), m <= 18 (Bruns et al. 2020),
//   e <= 3, L <= 12 (both as listed by Delgado, Eliahou and Fromentin 2025).
// Also records, per genus, the least Wilf ratio e*L/c among those uncovered semigroups
// and the (e, m, c) of one attaining it (ties: smallest m, then smallest c).
// Usage: ./wilf G      (parallel over the subtrees at depth D with OpenMP)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>

#define MAXG 60
#define SIZE (3 * MAXG + 3)

typedef struct { int c, g, m; unsigned char dec[SIZE]; } sg;

static int G;
typedef struct {
  long long n[MAXG + 1], fail[MAXG + 1], unc[MAXG + 1], eq[MAXG + 1];
  long long bestnum[MAXG + 1], bestden[MAXG + 1];  // least e*L / c among uncovered semigroups
  int beste[MAXG + 1], bestm[MAXG + 1], bestc[MAXG + 1];
} stats;

static void visit(const sg *s, stats *st) {
  int e = 0;
  for (int y = 1; y < s->c + s->m && y < SIZE; y++) if (s->dec[y] == 1) e++;
  int g = s->g, c = s->c, m = s->m, L = c - g;
  st->n[g]++;
  long long num = (long long)e * L, den = c;
  if (num < den) st->fail[g]++;
  int covered = (c <= 3 * m) || (3 * e >= m) || (m <= 18) || (e <= 3) || (L <= 12);
  if (num == den) st->eq[g]++;
  if (covered) return;
  st->unc[g]++;
  if (st->bestden[g] == 0 || num * st->bestden[g] < st->bestnum[g] * den
      || (num * st->bestden[g] == st->bestnum[g] * den && (m < st->bestm[g] || (m == st->bestm[g] && c < st->bestc[g])))) {
    st->bestnum[g] = num; st->bestden[g] = den; st->beste[g] = e; st->bestm[g] = m; st->bestc[g] = c;
  }
}

static void child(const sg *s, int x, sg *t) {
  memcpy(t, s, sizeof(sg));
  for (int y = x; y < SIZE; y++) if (s->dec[y - x] > 0) t->dec[y]--;
  t->c = x + 1; t->g = s->g + 1;
  if (x == s->m) { int k = x + 1; while (t->dec[k] == 0) k++; t->m = k; }
}

static void walk(const sg *s, stats *st) {
  visit(s, st);
  if (s->g >= G) return;
  sg t;
  for (int x = s->c ? s->c : 1; x < (s->c ? s->c + s->m : 2) && x < SIZE; x++)
    if (s->dec[x] == 1) { child(s, x, &t); walk(&t, st); }
}

// collect the nodes at depth D for parallel work
static sg *front; static int nfront, capfront;
static void collect(const sg *s, int D, stats *st) {
  if (s->g == D || s->g == G) {
    if (nfront == capfront) { capfront = capfront ? 2 * capfront : 1024; front = realloc(front, capfront * sizeof(sg)); }
    front[nfront++] = *s; return;
  }
  visit(s, st);
  sg t;
  for (int x = s->c ? s->c : 1; x < (s->c ? s->c + s->m : 2) && x < SIZE; x++)
    if (s->dec[x] == 1) { child(s, x, &t); collect(&t, D, st); }
}

int main(int argc, char **argv) {
  G = atoi(argv[1]);
  if (G > MAXG) return 1;
  sg root; root.c = 0; root.g = 0; root.m = 1;
  for (int y = 0; y < SIZE; y++) root.dec[y] = 1 + y / 2;
  stats tot; memset(&tot, 0, sizeof tot);
  int D = G < 22 ? G / 2 : 18;
  collect(&root, D, &tot);
  fprintf(stderr, "threads %d, subtrees at genus %d: %d\n", omp_get_max_threads(), D, nfront);
  #pragma omp parallel
  {
    stats loc; memset(&loc, 0, sizeof loc);
    #pragma omp for schedule(dynamic, 16)
    for (int i = 0; i < nfront; i++) walk(&front[i], &loc);
    #pragma omp critical
    for (int g = 0; g <= G; g++) {
      tot.n[g] += loc.n[g]; tot.fail[g] += loc.fail[g]; tot.unc[g] += loc.unc[g]; tot.eq[g] += loc.eq[g];
      if (loc.bestden[g] && (tot.bestden[g] == 0 || loc.bestnum[g] * tot.bestden[g] < tot.bestnum[g] * loc.bestden[g]
          || (loc.bestnum[g] * tot.bestden[g] == tot.bestnum[g] * loc.bestden[g] && (loc.bestm[g] < tot.bestm[g] || (loc.bestm[g] == tot.bestm[g] && loc.bestc[g] < tot.bestc[g]))))) {
        tot.bestnum[g] = loc.bestnum[g]; tot.bestden[g] = loc.bestden[g];
        tot.beste[g] = loc.beste[g]; tot.bestm[g] = loc.bestm[g]; tot.bestc[g] = loc.bestc[g];
      }
    }
  }
  printf("g n_g wilf_failures equality(eL=c) uncovered least_eL/c_among_uncovered (e,m,c of one minimiser)\n");
  for (int g = 0; g <= G; g++)
    printf("%d %lld %lld %lld %lld %.6f (%d,%d,%d)\n", g, tot.n[g], tot.fail[g], tot.eq[g], tot.unc[g],
           tot.bestden[g] ? (double)tot.bestnum[g] / tot.bestden[g] : 0.0, tot.beste[g], tot.bestm[g], tot.bestc[g]);
  return 0;
}

