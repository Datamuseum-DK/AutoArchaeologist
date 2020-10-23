'''
   Data General Relocatable Binary objects and libraries
   -----------------------------------------------------
'''

import struct

import autoarchaeologist

class Invalid(Exception):
    ''' Something's not right '''

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
    ''' A single RelBin record '''
    def __init__(self, this, i):
        self.padlen = 0
        while i < len(this) and not this[i]:
            self.padlen += 1
            i += 1
        if len(this[i:]) < 12:
            raise Invalid("Too Short")
        words = struct.unpack("<Hh", this[i:i+4])
        if words[0] not in REC_MAX_LEN:
            raise Invalid("RELBIN Bad Recno (0x%x) w1=%d" % (words[0],words[1]))
        if words[1] > -1:
            raise Invalid("RELBIN Invalid Length w0=0x%x (%d)" % (words[0], words[1]))
        if REC_MAX_LEN[words[0]] > words[1]:
            raise Invalid("RELBIN Bad Length w0=0x%x (%d)" % (words[0], words[1]))
        nwords = 6 + -words[1]
        if len(this[i:]) < nwords * 2:
            raise Invalid("Too Short")
        self.words = struct.unpack("<%dH" % nwords, this[i:i+nwords*2])
        self.chksum = sum(self.words) & 0xffff
        if False and self.chksum:
            print("RELBIN bad CS " + " ".join(["%04x" % i for i in self.words]))
            raise Invalid("RELBIN Bad checksum (0x%04x)" % self.chksum)
        if self.words[0] == 7:
            _i, j = b40(self.words[6:8])
            self.name = j + " "
        else:
            self.name = ""

    def length(self):
        ''' length in bytes of this record '''
        return self.padlen + 2 * len(self.words)

    def __repr__(self):
        return "<RBR " + self.render() + ">"

    def render(self):
        ''' render as hexdumped words '''
        if self.padlen:
            t = "(%d)" % self.padlen
        else:
            t = "   "
        t += " %2d" % self.words[0]
        t += " %3d" % (self.words[1] - 65536)
        t += " " + " ".join("%06o" % (x >> 1) for x in self.words[2:5])
        t += " " + " ".join(["%04x" % x for x in self.words[5:]])
        if self.chksum:
            t += "  CS=0x%04x" % self.chksum
        return t

    def symbols(self):
        ''' Iterate all symbols '''
        if self.words[0] in (7,3,4,5):
            for x in range(6, len(self.words) - 1, 4):
                y = b40(self.words[x:x+2])
                yield y[0].strip(), y[1].strip()

    def html_as_interpretation(self, fo):
        ''' Render as hexdump, list symbols '''
        fo.write(self.render() + "\n")
        for i, j in self.symbols():
            fo.write(" " * 10 + i + " " + j + "\n")

class RelBin():
    '''
       Data General Relocatable Binary object or library
    '''
    def __init__(self, this):
        if this.has_type("RelBin") or this.has_type("RelBinLib"):
            return

        idx = 0
        while idx < len(this) and not this[idx]:
            idx += 1

        pfx = idx

        self.this = this
        objs = []

        i = pfx
        while True:
            x = self.find_next(i)
            if not x[1]:
                break
            objs.append(x)
            i += x[0] + x[1]

        if not objs:
            return

        #print("??RELBIN", this, i, len(l), l[0][0])
        if len(objs) > 1:
            this.add_type("RelBinLib")
            offset = 0
            for a, b, _r in objs:
                this.slice(offset + a, b)
                offset += a + b
            return

        # Only a single RelBin

        r = objs[0][2]

        if r[0].words[0] not in VALID_FIRST:
            return

        this = this.slice(pfx, i - pfx)
        if this.has_type("RelBin"):
            return
        self.this = this

        this.add_type("RelBin")

        self.r = r
        self.this.add_interpretation(self, self.html_as_interpretation)
        for i in r:
            for j, k in sorted(i.symbols()):
                if j in (".ENT",):
                    this.add_note(k)
        if self.r[0].name:
            try:
                this.set_name(self.r[0].name.strip())
            except autoarchaeologist.core_classes.DuplicateName:
                pass

    def html_as_interpretation(self, fo, _this):
        ''' List all the records '''
        fo.write("\n")
        fo.write("<H3>RelBin</H3>\n")
        fo.write("<pre>\n")
        for r in self.r:
            r.html_as_interpretation(fo)
        fo.write("</pre>\n")


    def find_next(self, i):
        ''' Find boundaries of next relbin obj '''
        pfxlen = 0
        while i < len(self.this) and not self.this[i]:
            i += 1
            pfxlen += 1

        start = i
        r = []
        while i < len(self.this):
            try:
                j = RelBinRec(self.this, i)
            except Invalid as error:
                if r:
                    print("RELBIN", self.this, error)
                return 0, 0, None
            # print("RELBIN", self.this, j)
            r.append(j)
            i += j.length()
            if j.words[0] in VALID_LAST:
                break
        return pfxlen, i - start, r
