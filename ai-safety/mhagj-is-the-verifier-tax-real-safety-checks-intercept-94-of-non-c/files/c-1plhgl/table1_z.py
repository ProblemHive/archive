# Table 1 of arXiv:2603.19328 (Sah et al.): SSR mean and standard error, percent.
# Triad = planning architecture without safety mediation; Triad-Safety = Triad plus the verifier.
# So the verifier's own effect is Triad-Safety minus Triad. Also shown: each against Tool-Calling.
# z-test, normal approximation, independent samples (seeds/tasks are shared, so pairing is ignored: rough).
from math import sqrt, erfc
T = {
 ("GPT-OSS-20B","Airline"): {"Tool-Calling":(0.0,0.0),"Triad":(0.7,1.2),"Triad-Safety":(0.0,0.0)},
 ("GPT-OSS-20B","Retail"):  {"Tool-Calling":(0.0,0.0),"Triad":(0.0,0.0),"Triad-Safety":(0.6,0.5)},
 ("GLM-4-9B","Airline"):    {"Tool-Calling":(0.7,1.2),"Triad":(5.3,1.2),"Triad-Safety":(4.7,3.1)},
 ("GLM-4-9B","Retail"):     {"Tool-Calling":(2.6,1.7),"Triad":(4.4,1.5),"Triad-Safety":(2.9,1.0)},
}
def cmp(m,d,a,b,row):
    (x,sx),(y,sy)=row[a],row[b]
    den=sqrt(sx*sx+sy*sy)
    z=(x-y)/den if den>0 else float('nan')
    p=erfc(abs(z)/sqrt(2)) if den>0 else float('nan')
    print(f"{m:12s} {d:8s} {a:13s} {x:4.1f} vs {b:12s} {y:4.1f}  diff {x-y:+5.1f}  z={z:5.2f}  p~{p:.2f}")
for (m,d),row in T.items():
    cmp(m,d,"Triad-Safety","Triad",row)      # verifier effect
for (m,d),row in T.items():
    cmp(m,d,"Triad-Safety","Tool-Calling",row)
