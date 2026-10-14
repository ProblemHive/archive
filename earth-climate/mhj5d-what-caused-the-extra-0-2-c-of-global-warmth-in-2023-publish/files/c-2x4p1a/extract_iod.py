import re, html
with open('farago2026.html', encoding='utf-8') as f:
    t = f.read()
t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
t = re.sub(r'<[^>]+>', ' ', t)
t = html.unescape(t)
t = re.sub(r'\s+', ' ', t)
# find section 2.2.4 or wherever IOD index is defined
i = t.find('2.2.4')
print(t[i:i+2000])
