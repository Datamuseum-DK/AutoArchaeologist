#!/usr/bin/env python3

'''
   Bad sector tables
   =================
'''

from ...base import bitview as bv

from ...generic import disk
from .defs import SECTBITS, LSECSHIFT, DoubleSectorBitView, ELIDE_BADLIST, DiskAddress

class BadSector(disk.Sector):
    ''' Flagged bad sector '''
    def render(self):
        yield "BadSector"

class BadSectorTable(bv.Struct):
    '''
    ...
    '''
    def __init__(self, ovtree, lba):
        sect = DoubleSectorBitView(ovtree, lba, 'BT', 'BadSectorTable').insert()
        super().__init__(
            sect.bv,
            0,
            vertical=True,
            bad_=bv.Array(256, DiskAddress, vertical=True),
            more=True,
        )
        self.done(SECTBITS * 2)
        while len(self.bad.array) > 1 and self.bad.array[-1].chs() == (0, 0, 0):
            self.bad.array.pop(-1)
        done = set()
        done.add(0)
        for bad_entry in self.bad:
            lba = ovtree.sblk.diskaddress_to_lba(bad_entry)
            if lba in done:
                continue
            done.add(lba)
            ovtree.set_picture('BS', lo = lba << LSECSHIFT, legend = "Bad Sector")
            BadSector(ovtree, lo = lba << LSECSHIFT).insert()

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
    ''' Sector reserved to replace grown bad sectors '''
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
            f0_=-4,
            more=True,
        )
        if self.f0.val == 0x8:
            self.add_field("f2", -4)
            self.add_field("f3", -24)
            self.add_field("f4", -32)
            self.add_field("ary", bv.Array(127, ReplacementEntry))
            for repl in self.ary.array:
                offset = repl.lba.val << LSECSHIFT
                ReplacementSector(ovtree, lo = offset).insert()
                ovtree.set_picture('RS', lo = offset, legend = 'Replacement Sector')
        self.done(SECTBITS * 2)

    def render(self):
        if ELIDE_BADLIST:
            yield "ReplacementSectorTable(elided)"
        else:
            yield from super().render()
