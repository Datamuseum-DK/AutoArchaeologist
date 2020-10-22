import struct

import autoarchaeologist

class Invalid(Exception):
    pass

VALID_FIRST = set([2, 6, 7, 9,])
VALID_LAST = set([6,])

REC_MAX_LEN = {
    1: -15,
    2: -15,
    3: -45,
    4: -45,
    5: -45,
    6: -2,
    7: -3,
    9: -3,
    11: -15,
    12: -15,
    13: -15,
}

def b40(x):
    '''
        Decode a radix-40 encoded symbol
        --------------------------------

        See:  RCSL-42-I-0833 DOMAC - Domus Macro Assembler, User's Guide
        Appendix C and D
    '''
    x = list(x)
    t = ""
    c = "_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.?/"
    for i in (x[1] >> 5, x[0]):
        while i:
            t += c[i % 40]
            i //= 40
    symtyp = {
        0x00: ".ENT",
        0x01: ".EXTN",
        0x02: ".EXTA",
        0x03: ".EXTD",
        0x04: ".TITL",
    }.get(x[1] & 0x1f)
    if symtyp is None:
        symtyp = ".SYM%02x" % (x[1] & 0x1f)
    return symtyp, t[::-1]


class RelBinRec():
    def __init__(self, this, i):
        self.padlen = 0
        while i < len(this) and not this[i]:
            self.padlen += 1
            i += 1
        if len(this[i:]) < 12:
            raise Invalid("Too Short")
        w = struct.unpack("<Hh", this[i:i+4])
        if w[0] not in REC_MAX_LEN:
            raise Invalid("RELBIN Bad Recno (0x%x) w1=%d" % (w[0],w[1]))
        if w[1] > -1:
            raise Invalid("RELBIN Invalid Length w0=0x%x (%d)" % (w[0], w[1]))
        if REC_MAX_LEN[w[0]] > w[1]:
            raise Invalid("RELBIN Bad Length w0=0x%x (%d)" % (w[0], w[1]))
        nw = 6 + -w[1]
        if len(this[i:]) < nw * 2:
            raise Invalid("Too Short")
        self.w = struct.unpack("<%dH" % nw, this[i:i+nw*2])
        self.cs = sum(self.w) & 0xffff
        if False and self.cs:
            print("RELBIN bad CS " + " ".join(["%04x" % i for i in self.w]))
            raise Invalid("RELBIN Bad checksum (0x%04x)" % self.cs)
        if self.w[0] == 7:
            _i, j = b40(self.w[6:8])
            self.nm = j + " "
        else:
            self.nm = ""

    def length(self):
        return self.padlen + 2 * len(self.w)

    def __repr__(self):
        return "<RBR " + self.render() + ">"

    def render(self):
        if self.padlen:
            t = "(%d)" % self.padlen
        else:
            t = "   "
        t += " %2d" % self.w[0]
        t += " %3d" % (self.w[1] - 65536)
        t += " " + " ".join("%06o" % (x >> 1) for x in self.w[2:5])
        t += " " + " ".join(["%04x" % x for x in self.w[5:]])
        if self.cs:
            t += "  CS=0x%04x" % self.cs
        return t

    def symbols(self):
        if self.w[0] in (7,3,4,5):
            for x in range(6, len(self.w) - 1, 4):
                y = b40(self.w[x:x+2])
                yield y[0].strip() + "=" + y[1].strip()

    def html_as_interpretation(self, fo):
        fo.write(self.render() + "\n")
        for i in self.symbols():
            fo.write(" " * 10 + i + "\n")

class RelBin():
    def __init__(self, this):
        if this.has_type("RelBin") or this.has_type("RelBinLib"):
            return

        idx = 0
        while idx < len(this) and not this[idx]:
            idx += 1

        pfx = idx

        self.this = this
        l = []

        i = pfx
        while True:
            x = self.find_next(i)
            if not x[1]:
                break
            l.append(x)
            i += x[0] + x[1]

        if not l:
            return

        #print("??RELBIN", this, i, len(l), l[0][0])
        if len(l) > 1:
            this.add_type("RelBinLib")
            o = 0
            for a, b, _r in l:
                this.slice(o + a, b)
                o += a + b
            return

        # Only a single RelBin with no padding

        r = l[0][2]

        if r[0].w[0] not in VALID_FIRST:
            return

        this = this.slice(pfx, i - pfx)
        if this.has_type("RelBin"):
            return
        self.this = this

        this.add_type("RelBin")

        self.r = r
        self.this.add_interpretation(self, self.html_as_interpretation)
        for i in r:
            for j in sorted(i.symbols()):
                this.add_note(j)
        if self.r[0].nm:
            try:
                this.set_name(self.r[0].nm.strip())
            except autoarchaeologist.core_classes.DuplicateName:
                pass

    def html_as_interpretation(self, fo, _this):

        fo.write("\n")
        fo.write("<H3>RelBin</H3>\n")
        fo.write("<pre>\n")
        for r in self.r:
            r.html_as_interpretation(fo)
        fo.write("</pre>\n")


    def find_next(self, i):

        pfxlen = 0
        while i < len(self.this) and not self.this[i]:
            i += 1
            pfxlen += 1

        i0 = i
        r = []
        while i < len(self.this):
            try:
                j = RelBinRec(self.this, i)
            except Invalid as e:
                if r:
                    print("RELBIN", self.this, e)
                return 0, 0, None
            # print("RELBIN", self.this, j)
            r.append(j)
            i += j.length()
            if j.w[0] in VALID_LAST:
                break
        return pfxlen, i - i0, r
