import re
html = open('parts_v2.html', encoding='utf-8').read()
# Find tables (ltx_tabular) and print their text content
tables = re.findall(r'<table[^>]*class="[^"]*ltx_tabular[^"]*"[^>]*>(.*?)</table>', html, re.S)
print('num tables:', len(tables))
for k,t in enumerate(tables):
    txt = re.sub(r'<[^>]+>', ' ', t)
    txt = re.sub(r'\s+', ' ', txt)
    print(f'== TABLE {k} ==')
    print(txt[:3000])
