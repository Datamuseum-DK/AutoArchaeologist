'''
   RC8000 binout format
   --------------------

   c39904456 starts with "newcat" but looks similar ?
'''

from ..base import octetview as ov
from .rc489k_utils import *

def parity(x):
    ''' calculate parity '''
    x ^= x >> 4
    x ^= x >> 2
    x ^= x >> 1
    return x & 1

#########################

class RC8000BinOutNewCat(ov.Struct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            cmd__=ov.Text(6),
        )

class RC8000BinOutCreate(ov.Struct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            cmd__=ov.Text(6),
            name_=ov.Text(12),
            entry_tail_=Rc489kEntryTail,
        )

class RC8000BinOutPerman(ov.Struct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            cmd__=ov.Text(6),
            name_=ov.Text(12),
            catalog_key_=ov.Be24,
        )

class RC8000BinOutLoad(ov.Struct):
    ''' ... '''
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            cmd__=ov.Text(6),
            name_=ov.Text(12),
            nseg_=ov.Be24,
        )

class RC8000BinOutEntry(ov.Struct):
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
                self.add_field("create", RC8000BinOutCreate)
                self.namespace = Rc489kNameSpace(
                    name = self.create.name.txt.rstrip(),
                    parent = self.tree.namespace,
                    priv = self.create.entry_tail,
                )
            elif i.txt == 'newcat':
                self.add_field("newcat", RC8000BinOutNewCat)
            elif i.txt == 'perman':
                self.add_field("perman", RC8000BinOutPerman)
            elif i.txt == 'load  ':
                self.add_field("load", RC8000BinOutLoad)
                self.nseg = self.load.nseg.val
                break
            elif i.txt == 'end':
                self.add_field("end", ov.Text(3))
                break
            else:
                print(up.this, self.__class__.__name__, "???", hex(self.hi), i)
                self.add_field("huh", ov.Text(6))
                break
        self.done()

    def commit(self):
        ''' Commit and create artifact if possible '''
        if self.namespace and self.parts:
            that = self.tree.this.create(
                records = (x.octets() for x in self.parts),
            )
            self.namespace.ns_set_this(that)

class RC8000BinOut(ov.OctetView):
    ''' A binout tape file '''

    def __init__(self, this):
        if not this.has_type("Rc8000_binout_segments"):
            return
        super().__init__(this)

        self.namespace = Rc489kNameSpace(
            name='',
            separator='',
            root=this,
        )

        l = list(this.iter_rec())
        while l:
            seg = l.pop(0)
            y = RC8000BinOutEntry(self, seg)
            for _i in range(y.nseg):
                seg = l.pop(0)
                z = ov.Opaque(self, lo=seg.lo, hi=seg.hi).insert()
                y.parts.append(z)
            y.insert()
            y.commit()

        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.add_interpretation(more=True)

#########################

class RC8000BinOutSegment(ov.Opaque):
    ''' ... '''

    def octets(self):
        ''' Convert to octets '''
        for i in range(0, len(self), 4):
            yield ((self[i] << 2) & 0xfc) | ((self[i+1] & 0x3f) >> 4)
            yield ((self[i+1] << 4) & 0xf0) | ((self[i+2] & 0x3f)>> 2)
            yield ((self[i+2] << 6) & 0xc0) | (self[i+3] & 0x3f)

class RC8000BinOutSegmentChecksum(ov.Opaque):
    ''' ... '''

class RC8000BinOutEnd(ov.Opaque):
    ''' ... '''

class RC8000BinOutTapeFile(ov.OctetView):
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
        if not parity(this[0]):
            return
        super().__init__(this)
        segments = []
        l = []
        lo = 0
        for n, i in enumerate(this):
            if not i:
                if not segments:
                    return
                y = RC8000BinOutEnd(self, n, width=1).insert()
                y = ov.Opaque(self, n+1, hi=len(this)).insert()
                break
            if not parity(i):
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
                y = RC8000BinOutSegment(self, lo=lo, width=len(l)).insert()
                segments.append(y)
                RC8000BinOutSegmentChecksum(self, y.hi, width=1).insert()
                lo = n+1
                l = []
            else:
                l.append(i & 0x7f)
        r = []
        for seg in segments:
            r.append(bytes(seg.octets()))

        that = this.create(records = r)
        this.add_type("Rc8000_binout_tape_file")
        that.add_type("Rc8000_binout_segments")
        self.this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation(more=True)

examiners = (
    RC8000BinOutTapeFile,
    RC8000BinOut,
)
