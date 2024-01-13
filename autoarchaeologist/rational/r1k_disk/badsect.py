#!/usr/bin/env python3

'''
   Bad sector tables
   =================
'''

from ...base import octetview as ov

from ...generic import disk
from .defs import SECTBITS, LSECSHIFT
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
        yield "BadSectorTable(l=%d)" % len(self.real_bad) + ", ".join(str(x) for x in sorted(self.real_bad.keys()))
