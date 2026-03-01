#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   RC4000/RC8000/RC9000 binout format
   ==================================

'''

from ...base import octetview as ov
from . import rc489k_utils as util

def parity(x):
    ''' calculate parity '''
    x ^= x >> 4
    x ^= x >> 2
    x ^= x >> 1
    return x & 1

PARITY = bytes(parity(x) for x in range(256))

#########################

class Rc489kBinOutNewCat(ov.Struct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            cmd__=ov.Text(6),
        )

class Rc489kBinOutCreate(ov.Struct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            cmd__=ov.Text(6),
            name_=ov.Text(12),
            entry_tail_=util.Rc489kEntryTail,
        )

class Rc489kBinOutPerman(ov.Struct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            cmd__=ov.Text(6),
            name_=ov.Text(12),
            catalog_key_=ov.Be24,
        )

class Rc489kBinOutLoad(ov.Struct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            cmd__=ov.Text(6),
            name_=ov.Text(12),
            nseg_=ov.Be24,
        )

class Rc489kBinOutEntry(ov.Struct):
    ''' One catlog entry '''

    def __init__(self, up, seg):
        super().__init__(up, seg.lo, more=True, vertical=True)
        self.namespace = None
        self.nseg = 0
        self.parts = []
        while self.hi < seg.hi:
            i = ov.Text(6)(up, self.hi)
            if i.txt == 'create':
                if self.namespace:
                    break
                self.add_field("create", Rc489kBinOutCreate)
                self.namespace = util.Rc489kNameSpace(
                    name = self.create.name.txt.rstrip(),
                    parent = self.tree.namespace,
                    priv = self,
                )
            elif i.txt == 'newcat':
                self.add_field("newcat", Rc489kBinOutNewCat)
            elif i.txt == 'perman':
                self.add_field("perman", Rc489kBinOutPerman)
            elif i.txt == 'load  ':
                self.add_field("load", Rc489kBinOutLoad)
                self.nseg = self.load.nseg.val
                break
            elif i.txt == 'end':
                self.add_field("end", ov.Text(3))
                break
            else:
                # print(up.this, self.__class__.__name__, "???", hex(self.hi), i)
                self.add_field("huh", ov.Text(6))
                break
        self.done()

    def ns_render(self):
        ''' ... '''
        return ["?"] + self.create.entry_tail.ns_render()

    def commit(self):
        ''' Commit and create artifact if possible '''
        if self.namespace and self.parts:
            that = self.tree.this.create(
                records = (x.octets() for x in self.parts),
                define_records = False,
            )
            self.namespace.ns_set_this(that)
            return True
        return False

class Rc489kBinOut(ov.OctetView):
    ''' A binout tape file '''

    def __init__(self, this):
        if not this.has_note("Rc489k_binout"):
            return
        super().__init__(this)

        self.namespace = util.Rc489kNameSpace(
            name='',
            separator='',
            root=this,
        )

        l = list(this.iter_rec())
        cnt = 0
        while l:
            seg = l.pop(0)
            y = Rc489kBinOutEntry(self, seg)
            for _i in range(y.nseg):
                seg = l.pop(0)
                z = ov.Opaque(self, lo=seg.lo, hi=seg.hi).insert()
                y.parts.append(z)
            if y.commit():
                y.insert()
                cnt += 1

        if cnt > 0:
            this.add_interpretation(self, self.namespace.ns_html_plain)
            self.add_interpretation(more=True)

#########################

class Rc489kBinOutSegment(ov.Opaque):
    ''' ... '''

    def octets(self):
        ''' Convert to octets '''
        for i in range(0, len(self), 4):
            yield ((self[i+0] << 2) & 0xfc) | ((self[i+1] & 0x3f) >> 4)
            yield ((self[i+1] << 4) & 0xf0) | ((self[i+2] & 0x3f) >> 2)
            yield ((self[i+2] << 6) & 0xc0) | (self[i+3] & 0x3f)

class Rc489kBinOutSegmentChecksum(ov.Opaque):
    ''' ... '''

class Rc489kBinOutEnd(ov.Dump):
    ''' ... '''

class Rc489kDataSet(ov.OctetView):
    '''
       From BINOUT (RCSL 31-D244):

       A binout segment is a stream of 8-bit characters with odd parity, the
       left-most bit of each character being the parity bit. The last character
       in the segment is a sumcharacter, which is charaterized by the second
       bit being one. The right-most 5 bits of this character form the sum modulo
       64 of all other characters in the segment.
       Each byte [12 bits!] of the input is output as two characters.  The second
       bit of these is always 0, wheras the right-most 6 bits are a copy of the cor-
       responding 6-bit group of the byte.
    '''

    def __init__(self, this):
        super().__init__(this)
        segments = []
        l = []
        lo = 0
        for n, i in enumerate(this):
            if not i and not segments:
                lo = n + 1
                continue
            if not i:
                y = Rc489kBinOutEnd(self, n, width=1).insert()
                y = ov.Opaque(self, n+1, hi=len(this)).insert()
                break
            if not PARITY[i]:
                if segments:
                    print(this, self.__class__.__name__, "Bail(parity) at", n)
                return
            if i & 0x40:
                if len(l) == 0:
                    return
                goodsum = (sum(l) & 0x3f) == (i & 0x3f)
                if not goodsum:
                    if segments:
                        print(this, self.__class__.__name__, "Bail(badseg) at", n)
                    return
                # print(this, "SEG", hex(lo), len(l), len(this))
                y = Rc489kBinOutSegment(self, lo=lo, width=len(l)).insert()
                segments.append(y)
                Rc489kBinOutSegmentChecksum(self, y.hi, width=1).insert()
                lo = n+1
                l = []
            else:
                l.append(i & 0x7f)
        if not segments:
            return
        r = []
        for seg in segments:
            r.append(bytes(seg.octets()))

        that = this.create(records = r)
        this.add_note("Rc489k_data_set")
        that.add_note("Rc489k_binout")
        self.this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation(more=True)

examiners = (
    Rc489kDataSet,
    Rc489kBinOut,
)
