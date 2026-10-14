import sympy as sp

def sigma_pp(prime, exp):
    return (prime**(exp+1) - 1)//(prime - 1)

print("=== Check 2: biconditional from arXiv:2002.12139v1 ===")
print("Claim: sigma(m^2)==1 mod4 iff p==k mod8, for N=p^k m^2 an OPN.")
print("Mechanism: v2(sigma(p^k))=1 forces sigma(m^2) odd. The biconditional is about")
print("when that odd value is 1 vs 3 mod4. We test the contrapositive direction:")
print("if p==k mod8 then sigma(p^k)==2 mod4 (v2=1), and if p!=k mod8 (but both==1 mod4)")
print("then v2(sigma(p^k))>=2, forcing sigma(m^2) even -- but that contradicts N being odd")
print("unless the biconditional is about a different quantity. Let us just check:")
print("For p==1 mod4 prime, k odd: compute sigma(p^k) mod 8 and v2.")
ok=0; fail=[]
cases=[]
for p in list(sp.primerange(5,300)):
    if p%4!=1: continue
    for k in range(1,9,2):
        s=sigma_pp(p,k)
        t=s; v2=0
        while t%2==0: t//=2; v2+=1
        cases.append((p,k,s%8,v2,(p-k)%8))
# The paper's biconditional is about sigma(m^2), not sigma(p^k). But the proof of the
# biconditional uses that when p==k mod8, v2(sigma(p^k))==1 exactly. Let us check:
for (p,k,s8,v2,pk8) in cases:
    if pk8==0 and v2!=1:
        fail.append(("p==k mod8 but v2!=1",p,k,s8,v2))
    if pk8!=0 and v2==1:
        fail.append(("v2==1 but p!=k mod8",p,k,s8,v2,pk8))
print(f"total (p,k) cases checked: {len(cases)}")
print(f"failures of the mechanism (v2=1 <=> p==k mod8): {len(fail)}")
if fail:
    print("first few failures:", fail[:5])
else:
    print("mechanism confirmed: v2(sigma(p^k))==1 exactly when p==k mod8.")

print()
print("=== Check 3: Lemma 7 shape ===")
found=[]
for s in sp.primerange(5,1000):
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
