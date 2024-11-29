#!/usr/bin/env python3

'''
   Source code Segments - TAG 0xe3
   ===============================

'''

from ....base import octetview as ov
from ....base import bitview as bv

class E300(bv.Struct):
    ''' Head of source code '''
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            f00_=-19,
            f01_=-77,
            f02_=-19,
            f03_=-8,
            f04_=-63,
            f05_=-12,
            f06_=-16,
            f07_=-16,
            f08_=-16,
            f09_=-1,
            f10_=bv.Array(100, E301, vertical=True),
        )

class E300A(bv.Struct):
    ''' Continuation Head of source code '''
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            f08_=-16,
            f09_=-1,
            f10_=bv.Array(100, E301, vertical=True),
        )

class E301(bv.Struct):
    ''' Page reference in Head '''
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            count_=-8,
            e301_001_c_=-8,
            page_=-8,
            e301_003_c_=-11,
        )

class E302(ov.Struct):
    ''' Text page '''
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            next_= ov.Be16,
            end_= ov.Be16,
            more=True,
            vertical=True,
        )
        self.txt = []
        while self.hi < self.lo + 4 + self.end.val:
            y = self.add_field("txt_%03d" % len(self.txt), E303)
            self.txt.append(y)
        self.done(0x400)

class DummyText():
    ''' pseudo field for empty text-records '''
    txt = ''

class E303(ov.Struct):
    ''' Text fragment, typically a full line '''
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            flags_= ov.Octet,
            len_= ov.Octet,
            more=True,
        )
        if self.len.val:
            self.add_field("text", ov.Text(self.len.val))
        else:
            self.text = DummyText()
        self.add_field("len2_", ov.Octet)
        self.done()

class TE3(ov.OctetView):

    ''' Tag=0xe3 segments contain Ada source code '''

    TAG = 0xe3

    def __init__(self, this):
        if not this.has_note("tag_%02x" % self.TAG):
            return

        super().__init__(this)

        bits = bv.OvBits(self, lo=0x0, hi=0x400).insert()
        self.head = E300(bits.bv, 0x0).insert()

        if self.head.f06.val:
            adr = self.head.f06.val << 10
            bits = bv.OvBits(self, lo=adr, hi=adr + 0x400).insert()
            E300A(bits.bv, lo=0).insert()

        recs = []
        recno = 1
        while recno:
            rec = E302(self, (recno << 10)).insert()
            recs.append((recno, rec))
            recno = rec.next.val

        self.add_interpretation(more=True)

        for more in (True, False):
            txt = []
            with self.this.add_utf8_interpretation("Ada Source Code", more=more) as file:
                for m, rec in enumerate(recs):
                    recno, rec = rec
                    for n, i in enumerate(rec.txt):
                        if i.flags.val == 0:
                            file.write('\n')
                            txt.append('\n')
                        if more or i.flags.val not in (0x00, 0x80):
                            file.write("┣%03x.%04x.%02x %02x┫" % (m + 1, recno, n+1, i.flags.val))
                        file.write(i.text.txt)
                        txt.append(i.text.txt)
        if False:
            txt = ''.join(txt)
            lines = txt.split('\n')
            i = 0
            while i < len(lines):
                t = lines[i].strip()
                if len(t) == 0 or t[:2] == '--':
                    lines.pop(i)
                    continue
                lines[i] = t
                i += 1
            for i in lines:
                print("\t", i)
