# xlsx_min.py - read an .xlsx file with the standard library only (no openpyxl here).
# sheets(path) yields (sheet name, rows); each row is a dict {column letters: value}.
import zipfile, re
import xml.etree.ElementTree as ET
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

def sheets(path):
    z = zipfile.ZipFile(path)
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.parse(z.open('xl/sharedStrings.xml')).getroot().findall('m:si', NS):
            shared.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    wb = ET.parse(z.open('xl/workbook.xml')).getroot()
    rels = ET.parse(z.open('xl/_rels/workbook.xml.rels')).getroot()
    target = {r.get('Id'): r.get('Target') for r in rels}
    for s in wb.find('m:sheets', NS):
        name = s.get('name')
        t = target[s.get('{%s}id' % NS['r'])]
        t = t.lstrip('/') if t.startswith('/') else 'xl/' + t
        rows = []
        for _, el in ET.iterparse(z.open(t)):
            if el.tag == '{%s}row' % NS['m']:
                row = {}
                for c in el.findall('m:c', NS):
                    v = c.find('m:v', NS)
                    if v is None or v.text is None:
                        continue
                    col = re.match(r'[A-Z]+', c.get('r')).group(0)
                    if c.get('t') == 's':
                        row[col] = shared[int(v.text)]
                    else:
                        try:
                            row[col] = float(v.text)
                        except ValueError:
                            row[col] = v.text
                rows.append((int(el.get('r')), row))
                el.clear()
        yield name, rows

if __name__ == '__main__':
    import sys
    for f in sys.argv[1:]:
        for name, rows in sheets(f):
            ncol = max((len(r) for _, r in rows), default=0)
            print('==', f, '|', name, '| rows', len(rows), '| max cells in a row', ncol)
            for n, r in rows[:6]:
                items = list(r.items())[:14]
                print(n, [(k, round(v, 4) if isinstance(v, float) else v) for k, v in items])
