#!/usr/bin/env python3

'''
   Bad sector tables
   =================
'''

from ...base import octetview as ov
from ...base import bitview as bv

from ...generic import disk
from .defs import SECTBITS, LSECSHIFT, DoubleSectorBitView, ELIDE_BADLIST
from .freelist import FreeList

class BadEntry(ov.Struct):
    '''
    ...
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            cyl_=ov.Be16,
            head_=ov.Octet,
            sect_=ov.Octet,
        )
    def chs(self):
        return (self.cyl.val & 0xfff, self.head.val, self.sect.val)

    def render(self):
        yield "0x%x(%d/%d/%d)" % (self.cyl.val >> 12, self.cyl.val & 0xfff, self.head.val, self.sect.val)

class BadSector(disk.Sector):
    def render(self):
        yield "Bad Sector"

class BadSectorTable(ov.Struct):
    '''
    ...
    '''
    def __init__(self, ovtree, lo, hi):
        nelem = (hi - lo) // 4
        self.real_bad = {}
        super().__init__(
            ovtree,
            lo,
            vertical=True,
            bad_=ov.Array(nelem, BadEntry, vertical=True)
        )
        for i in self.bad.array:
            self.real_bad[i.chs()] = True
        del self.real_bad[(0,0,0)]

        done = set()
        ovtree.picture_legend['BS'] = "Bad Sector"
        for cyl,head,sect in self.real_bad.keys():
            lba = cyl
            lba *= ovtree.sblk.geometry.hd.val
            lba += head
            lba *= ovtree.sblk.geometry.sect.val
            lba += sect
            lba >>= 1
            if lba not in done:
                ovtree.set_picture('BS', lo = lba << LSECSHIFT)
                BadSector(
                    ovtree,
                    lo = lba << LSECSHIFT,
                ).insert()
                done.add(lba)
            

    def render(self):
        if ELIDE_BADLIST:
            yield "BadSectorTable(elided)"
        else:
            yield from super().render()

class ReplacementEntry(bv.Struct):
    '''
    ...
    '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            info_=-2,
            lba_=-24,
            f0_=-38,
        )

class ReplacementSector(disk.Sector):

    def render(self):
        yield "ReplacementSector"

class ReplacementSectorTable(bv.Struct):
    '''
    ...
    '''
    def __init__(self, ovtree, lba):
        sect = DoubleSectorBitView(ovtree, lba, 'RT', 'ReplacementTable').insert()
        super().__init__(
            sect.bv,
            0,
            vertical=True,
            f0_=-8,
            more=True,
        )
        if self.f0.val == 0x84:
            self.add_field("f1", -24)
            self.add_field("f2", -32)
            self.add_field("ary", bv.Array(127, ReplacementEntry)),
            for repl in self.ary.array:
                ReplacementSector(ovtree, lo = repl.lba.val << LSECSHIFT).insert()
                ovtree.set_picture('RS', lo = repl.lba.val << LSECSHIFT, legend = 'Replacement Sector')
        self.done(SECTBITS)

    def render(self):
        if ELIDE_BADLIST:
            yield "ReplacementSectorTable(elided)"
        else:
            yield from super().render()

