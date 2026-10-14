# Minimal reader for an R .rds file holding one data frame (XDR serialisation, version 2 or 3).
# Written for the BioTIME 2.0 query file; reads only the object types that occur in plain data frames.
# String columns are returned as integer codes plus a list of distinct values, to keep memory down.
import gzip
import struct

import numpy as np


class Reader:
    def __init__(self, path):
        with gzip.open(path, "rb") as f:
            self.b = f.read()
        self.p = 0
        self.refs = []
        assert self.b[:2] == b"X\n", "not an XDR serialisation"
        self.p = 2
        version = self.i4()
        self.i4(); self.i4()
        if version == 3:
            n = self.i4()
            self.p += n

    def i4(self):
        v = struct.unpack_from(">i", self.b, self.p)[0]
        self.p += 4
        return v

    def charsxp(self):
        flags = self.i4()
        assert flags & 0xFF == 9, f"expected CHARSXP, got {flags & 0xFF}"
        n = self.i4()
        if n == -1:
            return None
        s = self.b[self.p:self.p + n]
        self.p += n
        return s

    def strvec(self, n):
        b, p = self.b, self.p
        unpack = struct.unpack_from
        table, levels = {}, []
        codes = np.empty(n, dtype=np.int32)
        for k in range(n):
            ln = unpack(">ii", b, p)[1]
            p += 8
            if ln == -1:
                codes[k] = -1
                continue
            s = b[p:p + ln]
            p += ln
            c = table.get(s)
            if c is None:
                c = len(levels)
                table[s] = c
                levels.append(s)
            codes[k] = c
        self.p = p
        return {"codes": codes, "levels": [s.decode("utf-8", "replace") for s in levels]}

    def item(self):
        flags = self.i4()
        t = flags & 0xFF
        has_attr = bool(flags & 0x200)
        has_tag = bool(flags & 0x400)
        if t == 254:                                   # NULL
            return None
        if t == 255:                                   # reference to an earlier symbol
            idx = flags >> 8
            if idx == 0:
                idx = self.i4()
            return self.refs[idx - 1]
        if t == 1:                                     # symbol
            name = self.charsxp().decode()
            self.refs.append(name)
            return name
        if t == 2:                                     # pairlist, read without recursion on the tail
            out = []
            while True:
                if has_attr:
                    self.item()
                tag = self.item() if has_tag else None
                out.append((tag, self.item()))
                flags = self.i4()
                t = flags & 0xFF
                if t == 254:
                    return out
                assert t == 2, f"pairlist tail of type {t}"
                has_attr = bool(flags & 0x200)
                has_tag = bool(flags & 0x400)
        if t == 9:
            self.p -= 4
            return self.charsxp()
        if t in (10, 13):
            n = self.i4()
            v = np.frombuffer(self.b, dtype=">i4", count=n, offset=self.p).astype(np.int32)
            self.p += 4 * n
        elif t == 14:
            n = self.i4()
            v = np.frombuffer(self.b, dtype=">f8", count=n, offset=self.p).astype(np.float64)
            self.p += 8 * n
        elif t == 16:
            self.i4() if False else None
            n = self.i4()
            v = self.strvec(n)
        elif t == 19:
            n = self.i4()
            v = [self.item() for _ in range(n)]
        elif t == 238:                                 # ALTREP: class info, state, attributes
            info = self.item()
            state = self.item()
            attr = self.item()
            cls = info[0][1]
            if cls == "compact_intseq":
                n, start, step = (int(x) for x in state)
                v = np.arange(start, start + n * step, step, dtype=np.int32)
            elif cls.startswith("wrap_"):
                v = state[0]
            else:
                raise ValueError(f"ALTREP class {cls} not handled")
            return (v, dict(attr)) if attr else v
        else:
            raise ValueError(f"object type {t} not handled at byte {self.p}")
        if has_attr:
            attr = dict(self.item())
            return (v, attr)
        return v


def read_frame(path):
    r = Reader(path)
    obj = r.item()
    cols, attr = obj
    names = attr["names"]
    names = names["levels"] if isinstance(names, dict) else names
    if isinstance(attr["names"], dict):
        names = [attr["names"]["levels"][c] for c in attr["names"]["codes"]]
    out = {}
    for nm, col in zip(names, cols):
        if isinstance(col, tuple):                     # a vector with attributes (factor, Date ...)
            v, a = col
            if "levels" in a:
                lv = a["levels"]
                lv = [lv["levels"][c] for c in lv["codes"]]
                col = {"codes": v - 1, "levels": lv}
            else:
                col = v
        out[nm] = col
    return out
