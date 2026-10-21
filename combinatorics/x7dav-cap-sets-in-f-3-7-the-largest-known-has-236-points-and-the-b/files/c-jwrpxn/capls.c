// capls.c: plateau local search for large cap sets in F_3^n.
// usage: ./capls n seed iterations
// State: set S with no three distinct collinear points; cnt[p] = number of pairs {a,b} in S with a+b+p = 0.
// Moves: add any p with cnt[p]==0; swap: add p with cnt[p]==1 and remove one point of its pair; random kick.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int n, N;
static uint16_t *third; // third[x*N+y] = point z with x+y+z=0 (x != y)
static uint64_t rs;
static inline uint64_t rnd(void){ rs ^= rs<<13; rs ^= rs>>7; rs ^= rs<<17; return rs; }

static int digit(int x,int i){ for(int k=0;k<i;k++) x/=3; return x%3; }
static int mk(int *d){ int x=0; for(int i=n-1;i>=0;i--) x=x*3+d[i]; return x; }

static int *S, ns; static char *in; static int *cnt, *pos;

static void addp(int q){
  for(int i=0;i<ns;i++) cnt[third[S[i]*N+q]]++;
  in[q]=1; pos[q]=ns; S[ns++]=q;
}
static void delp(int q){
  int i=pos[q]; S[i]=S[--ns]; pos[S[i]]=i; in[q]=0;
  for(int j=0;j<ns;j++) cnt[third[S[j]*N+q]]--;
}
static int check(void){
  for(int i=0;i<ns;i++) for(int j=i+1;j<ns;j++){ if(in[third[S[i]*N+S[j]]]) return 0; }
  return 1;
}

int main(int argc,char**argv){
  n=atoi(argv[1]); rs=88172645463325252ULL ^ (uint64_t)atoll(argv[2])*0x9E3779B97F4A7C15ULL; long iters=atol(argv[3]);
  N=1; for(int i=0;i<n;i++) N*=3;
  third=malloc(sizeof(uint16_t)*N*N);
  for(int x=0;x<N;x++) for(int y=0;y<N;y++){
    int d[16]; for(int i=0;i<n;i++){ int a=digit(x,i)+digit(y,i); d[i]=(6-a)%3; } third[x*N+y]=mk(d); }
  S=malloc(sizeof(int)*N); in=calloc(N,1); cnt=calloc(N,sizeof(int)); pos=calloc(N,sizeof(int));
  int best=0; int *bestS=malloc(sizeof(int)*N);
  for(long it=0; it<iters; it++){
    // add all free points in random order
    int added=1;
    while(added){ added=0; int st=rnd()%N; for(int k=0;k<N;k++){ int p=(st+k)%N; if(!in[p] && cnt[p]==0){ addp(p); added=1; break; } } }
    if(ns>best){ best=ns; memcpy(bestS,S,sizeof(int)*ns); }
    // swap move: pick random p with cnt==1
    int tries=0, p=-1;
    while(tries<4000){ int c=rnd()%N; if(!in[c] && cnt[c]==1){ p=c; break; } tries++; }
    if(p<0 || (rnd()%2000)==0){ // kick: remove a few points
      int k=1+rnd()%3; for(int j=0;j<k && ns>0;j++) delp(S[rnd()%ns]); continue; }
    // find the pair generating p: a in S with third(p,a) in S
    int a=-1; for(int i=0;i<ns;i++){ int b=third[p*N+S[i]]; if(b!=S[i] && in[b]){ a=(rnd()&1)?S[i]:b; break; } }
    if(a<0) continue;
    delp(a); addp(p);
  }
  printf("n=%d seed=%s best=%d check=%d\n",n,argv[2],best,0);
  // verify best
  ns=0; memset(in,0,N); memset(cnt,0,sizeof(int)*N);
  for(int i=0;i<best;i++) addp(bestS[i]);
  // check via addp invariants: no point of S has cnt>0
  int ok=1; for(int i=0;i<ns;i++) if(cnt[S[i]]) ok=0;
  printf("verify: size=%d valid=%d (direct pair check: %d)\n",ns,ok,check());
  return 0;
}

