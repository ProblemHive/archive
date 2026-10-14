import re, html
with open('farago2026.html', encoding='utf-8') as f:
    t = f.read()
t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
t = re.sub(r'<[^>]+>', ' ', t)
t = html.unescape(t)
t = re.sub(r'\s+', ' ', t)
# find the actual table data - look for the numbers in context
i = t.find('Table 2 shows')
print(t[i+6000:i+9000])
