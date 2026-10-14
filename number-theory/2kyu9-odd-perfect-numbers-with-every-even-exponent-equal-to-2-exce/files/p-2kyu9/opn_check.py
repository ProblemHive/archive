import sympy as sp

def ord_mod(a, m):
    return sp.n_order(a % m, m)

def sigma_pp(prime, exp):
    return (prime**(exp+1) - 1)//(prime - 1)

print("=== Check 1: Lemma 4 (ord_s(n) even => s does not divide sigma(n^q), q even) ===")
cnt=0; viol=0
primes=list(sp.primerange(3,200))
for s in primes:
    for n in primes:
        if n==s: continue
        o=ord_mod(n,s)
        if o%2==0:
            cnt+=1
            for q in (2,4,6):
                if sigma_pp(n,q)%s==0:
                    viol+=1; print("VIOLATION", s,n,q)
print(f"checked {cnt} (s,n) pairs with ord_s(n) even; violations={viol}")

print()
print("=== Check 2: biconditional sigma(m^2)==1 mod4 iff p==k mod8 ===")
# For Euler form N=p^k m^2, sigma(N)=sigma(p^k)sigma(m^2)=2N. Since p^k||N and
# gcd(p,m)=1, the 2-adic valuation of sigma(p^k) must supply exactly one factor of 2
# beyond what's in N (odd). So v2(sigma(p^k))=1, i.e. sigma(p^k)==2 mod4.
# sigma(p^k)=1+p+...+p^k; p==1 mod4,k odd => each term==1 mod4? No: p==1 mod4 so
# each term==1 mod4, sum has k+1 terms (even). Check parity of count vs mod8.
for p in list(sp.primerange(5,200)):
    if p%4!=1: continue
    for k in range(1,8,2):
        s=sigma_pp(p,k)
        bc = (s%4==1) == ((p-k)%8==0)
        if not bc:
            print("BICONDITIONAL FAIL", p,k,s%4,(p-k)%8)
print("biconditional check done for all p==1 mod4 primes<200, odd k<=7")

print()
print("=== Check 3: Lemma 7 shape (s==5 mod6 prime, sigma(s^2)=p^a n^b => p==1 mod3,n==1 mod6) ===")
found=[]
for s in sp.primerange(5,500):
    if s%6!=5: continue
    v=sigma_pp(s,2)
    fac=sp.factorint(v)
    if len(fac)==2:
        items=list(fac.items())
        (p,a),(n,b)=items[0],items[1]
        found.append((s,p%3,n%6))
print(f"primes s==5 mod6 with sigma(s^2) exactly two-prime-power form: {len(found)}")
if found:
    print("all had p==1 mod3 and n==1 mod6?", all(p3==1 and n6==1 for (_,p3,n6) in found))
