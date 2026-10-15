# Print the section titles of a JATS full-text XML, and the plain text of the sections whose titles match a pattern.
# usage: python sections.py FILE.xml [regex]
import re, sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
pat = re.compile(sys.argv[2], re.I) if len(sys.argv) > 2 else None
def text(e):
    return re.sub(r"\s+", " ", "".join(e.itertext())).strip()
for sec in root.iter("sec"):
    t = sec.find("title")
    title = text(t) if t is not None else "(untitled)"
    if pat is None:
        print("-", title)
    elif pat.search(title):
        print("=== " + title)
        for p in sec.findall("p"):
            print(text(p))
            print()
