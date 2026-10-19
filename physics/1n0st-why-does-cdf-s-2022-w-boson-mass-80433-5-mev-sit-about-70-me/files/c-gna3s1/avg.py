from math import sqrt, erfc
d={'LEP2':(80.376,.033),'D0':(80.383,.023),'ATLAS':(80.3665,.0159),'CMS':(80.3602,.0099),'LHCb':(80.354,.032)}
w=sum(1/s**2 for m,s in d.values()); a=sum(m/s**2 for m,s in d.values())/w; e=w**-.5
chi=sum(((m-a)/s)**2 for m,s in d.values())
print("naive uncorrelated avg without CDF: %.4f +- %.4f  chi2=%.2f (4 dof)"%(a,e,chi))
c,sc=80.4335,.0094
z=(c-a)/sqrt(sc**2+e**2); print("CDF minus avg = %.1f MeV, z=%.2f, two-sided p=%.1e"%((c-a)*1e3,z,erfc(z/sqrt(2))))
sm,ssm=80.357,.006
for n,(m,s) in {'CDF':(c,sc),'CMS':d['CMS'],'ATLAS':d['ATLAS']}.items():
    z=(m-sm)/sqrt(s**2+ssm**2); print(n,"vs SM fit %.2f sigma"%z)
# CDF vs CMS only
z=(c-d['CMS'][0])/sqrt(sc**2+d['CMS'][1]**2); print("CDF vs CMS %.1f MeV, %.2f sigma (uncorrelated)"%((c-d['CMS'][0])*1e3,z))
# with a common 7 MeV correlated PDF uncertainty between CDF and CMS (hadron-collider average assumption in PDG text)
for r in (0,7e-3):
    sd=sqrt(sc**2+d['CMS'][1]**2-2*r**2); print("corr %.0f MeV: %.2f sigma"%(r*1e3,(c-d['CMS'][0])/sd))

