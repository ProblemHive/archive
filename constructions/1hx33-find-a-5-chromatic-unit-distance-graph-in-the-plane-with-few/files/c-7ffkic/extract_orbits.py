import re
html = open('parts_v2.html', encoding='utf-8').read()
txt = re.sub(r'<[^>]+>', ' ', html)
txt = re.sub(r'\s+', ' ', txt)
# Find the full section about M-type graphs in Results (section 6) - look for orbit lists
m = re.search(r'M-type graphs\. The', txt)
if m:
    print(txt[m.start():m.start()+5000])
else:
    # try broader search
    ms = list(re.finditer(r'orbit.*?table|Table 1|Table 2', txt, re.I))
    for mm in ms[:3]:
        s=max(0,mm.start()-200)
        print(txt[s:mm.start()+800])
