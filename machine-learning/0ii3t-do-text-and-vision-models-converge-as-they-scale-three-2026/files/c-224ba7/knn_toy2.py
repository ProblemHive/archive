import numpy as np, sys
from scipy.spatial import cKDTree
# Toy with known ground truth: shared latent z in R^dz; two "encoders" see z through
# fixed random linear maps plus independent noise of std s. Metric: mutual kNN overlap
# (mean fraction of shared k nearest neighbours between the two feature spaces).
def knn_idx(X,k,ch=2000):
    X=X.astype(np.float32); sq=(X*X).sum(1); out=np.empty((len(X),k),dtype=np.int64)
    for i in range(0,len(X),ch):
        D=sq[i:i+ch,None]-2*X[i:i+ch]@X.T+sq[None,:]
        D[np.arange(D.shape[0]),np.arange(i,i+D.shape[0])]=np.inf
        out[i:i+ch]=np.argpartition(D,k,axis=1)[:,:k]
    return out
def overlap(X,Y,k):
    A=knn_idx(X,k); B=knn_idx(Y,k)
    return np.mean([len(set(a)&set(b)) for a,b in zip(A,B)])/k
def run(N,k,s,dz=8,dx=64,seed=0):
    r=np.random.default_rng(seed)
    z=r.normal(size=(N,dz))
    A=r.normal(size=(dz,dx))/np.sqrt(dz); B=r.normal(size=(dz,dx))/np.sqrt(dz)
    X=z@A+s*r.normal(size=(N,dx)); Y=z@B+s*r.normal(size=(N,dx))
    return overlap(X,Y,k)
def null(N,k,dx=64,seed=0):
    r=np.random.default_rng(seed); return overlap(r.normal(size=(N,dx)),r.normal(size=(N,dx)),k)
print("N k s overlap chance(k/(N-1)) calibrated=(o-c)/(1-c) | null_indep_random")
for s in (0.3,0.6):
  for N in (1000,4000,16000):
    for k in (10, int(round(0.01*N))):
        o=np.mean([run(N,k,s,seed=i) for i in range(2)]); c=k/(N-1)
        n=null(N,k) 
        print(f"{N} {k} {s} {o:.3f} {c:.4f} {(o-c)/(1-c):.3f} | {n:.4f}",flush=True)
