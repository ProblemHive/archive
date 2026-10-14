import re, html
with open('farago2026.html', encoding='utf-8') as f:
    t = f.read()
t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
t = re.sub(r'<[^>]+>', ' ', t)
t = html.unescape(t)
t = re.sub(r'\s+', ' ', t)
# find the section that defines AMV index
i = t.find('Atlantic Meridional Overturning Circulation (AMOC)')
print(t[i-1500:i+2500])
