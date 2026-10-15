# Print sentences from the body of a JATS XML that match a pattern (results lookup).
# usage: python sentences.py FILE.xml regex [maxlen]
import re, sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
pat = re.compile(sys.argv[2], re.I)
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 400
body = root.find(".//body")
txt = re.sub(r"\s+", " ", "".join(body.itertext()))
for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", txt):
    if pat.search(s):
        print("*", s[:mx])
