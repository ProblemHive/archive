from fractions import Fraction as F
from math import isqrt
# srg(v=k^2+1, k, 0, 1): eigenvalues are roots of x^2 + x - (k-1) = 0, disc = 4k-3
def mults(k):
    v=k*k+1; D=4*k-3; sd=isqrt(D)
    if sd*sd!=D: return None
    r=F(-1+sd,2); s=F(-1-sd,2)
    g=(-k-r*(v-1))/(s-r)      # multiplicity of s, from trace: k + r*f + s*g = 0, f+g = v-1
    f=(v-1)-g
    return v,r,s,f,g
def krein(k,r,s):
    return ((r+1)*(k+r+2*r*s)<=(k+r)*(s+1)**2, (s+1)*(k+s+2*r*s)<=(k+s)*(r+1)**2)
for k in (3,7,57):
    v,r,s,f,g=mults(k)
    print("k=%d v=%d r=%s s=%s f=%s g=%s  trace check=%s  f+g+1=%s  Krein=%s"%(k,v,r,s,f,g,k+r*f+s*g,f+g+1,krein(k,r,s)))
    print("   absolute bound v<=f(f+3)/2:",v<=f*(f+3)/2," v<=g(g+3)/2:",v<=g*(g+3)/2)
# control: integrality of multiplicities over all k up to 10^5 (Hoffman-Singleton: only 2,3,7,57)
good=[2]  # k=2: eigenvalues irrational, multiplicities 2 and 2
for k in range(3,100001):
    m=mults(k)
    if m and m[3].denominator==1: good.append(k)
print("k <= 100000 with integral eigenvalues and integral multiplicities (plus k=2 by hand):",good)

