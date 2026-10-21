// Local search for an additive instance with no EFX allocation.
// usage: efx n m V seed seconds [ef]
// Values are integers in 0..V. EFX0 (strict version): v_i(X_i) >= v_i(X_j) - min_{g in X_j} v_i(g) for every nonempty X_j.
// With the optional last argument "ef" the test is plain envy-freeness (a control: it fails easily).
// Objective: number of allocations (of n^m) that satisfy the test; we try to reach 0. Hill climbing with
// ties accepted, random restarts after stagnation.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
static int n, m, V, ef;
static int val[8][1<<12], thr[8][1<<12];
static int v[8][12];
static uint64_t rs;
static inline uint64_t rnd(void){ rs ^= rs<<13; rs ^= rs>>7; rs ^= rs<<17; return rs; }
static void tables(void){
    for (int i=0;i<n;i++){
        val[i][0]=0; thr[i][0]=0;
        for (int S=1;S<(1<<m);S++){
            int low=__builtin_ctz(S); val[i][S]=val[i][S&(S-1)]+v[i][low];
            int mn=1<<30; for (int g=0;g<m;g++) if (S>>g&1) if (v[i][g]<mn) mn=v[i][g];
            thr[i][S]= ef ? val[i][S] : val[i][S]-mn;
        }
    }
}
static long cnt; static int X[8];
static void rec(int g){
    if (g==m){
        for (int i=0;i<n;i++) for (int j=0;j<n;j++) if (i!=j && X[j] && val[i][X[i]]<thr[i][X[j]]) return;
        cnt++; return;
    }
    for (int a=0;a<n;a++){ X[a]|=1<<g; rec(g+1); X[a]&=~(1<<g); }
}
static long count(void){ tables(); cnt=0; memset(X,0,sizeof X); 
    // symmetry: good 0 goes to agent 0 only is not valid (values differ), so full enumeration
    rec(0); return cnt; }
int main(int argc,char**argv){
    n=atoi(argv[1]); m=atoi(argv[2]); V=atoi(argv[3]); rs=0x9E3779B97F4A7C15ULL*(atoll(argv[4])+1); double secs=atof(argv[5]); ef=argc>6;
    time_t t0=time(0); long best=1L<<60; long evals=0; int bv[8][12];
    while (difftime(time(0),t0)<secs){
        for (int i=0;i<n;i++) for (int g=0;g<m;g++) v[i][g]=rnd()%(V+1);
        long cur=count(); evals++; int stag=0;
        while (stag<300 && difftime(time(0),t0)<secs){
            int i=rnd()%n,g=rnd()%m,old=v[i][g],nv=rnd()%(V+1); if (nv==old) continue;
            v[i][g]=nv; long c=count(); evals++;
            if (c<=cur){ if (c<cur) stag=0; else stag++; cur=c; } else { v[i][g]=old; stag++; }
            if (cur<best){ best=cur; memcpy(bv,v,sizeof v); }
            if (cur==0) break;
        }
        if (best==0) break;
    }
    printf("n=%d m=%d V=%d seed=%s evals=%ld best_count=%ld\n",n,m,V,argv[4],evals,best);
    if (best<=3){ for (int i=0;i<n;i++){ for(int g=0;g<m;g++) printf("%d ",bv[i][g]); printf("\n"); } }
    return 0;
}
