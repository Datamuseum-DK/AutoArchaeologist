#!/usr/bin/env python3

'''
   Freelist bitmaps
   ================
'''

from ..base import bitview as bv
from .r1k_disk_defs import OBJECT_FIELDS, SECTBITS, DoubleSectorBitView, ELIDE_FREELIST

class BitMap(bv.Struct):
    '''
    The fundamental 1024 wide bitmap of 1K sector status
    ----------------------------------------------------
    '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(
            tree,
            lo,
            f0_=-10,
            bits_=1024,
            **kwargs,
        )

    def get_bit(self, lba):
        ''' Get status of bit of sector lba '''
        return self.bits.bits()[lba]

class BitMapSect(bv.Struct):
    '''
    A sector with 7 bitmaps
    -----------------------
    '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(
            tree,
            lo,
            **OBJECT_FIELDS,
            flg_=1,
            vertical=True,
            map_=bv.Array(7, BitMap, vertical=True),
            more = True,
            **kwargs,
        )
        self.done(SECTBITS)

    def get_bit(self, lba):
        ''' Get status of bit of sector lba '''
        return self.map[lba // 1024].get_bit(lba % 1024)

    def render(self):
        if ELIDE_FREELIST:
            yield self.bt_name
        else:
            yield from super().render()

class FreeMapEntry(bv.Struct):
    '''
    A pointer to a BitMapSect
    -------------------------
    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f0_=-10,
            lba_=-24
        )

class FreeMapSect(bv.Struct):
    '''
    A sector full of FreeMapEntry's
    -------------------------------
    '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(
            tree,
            lo,
            **OBJECT_FIELDS,
            f0_=-0x20,
            vertical=True,
            fme_=bv.Array(237, FreeMapEntry, vertical=True),
            more = True,
            **kwargs,
        )
        self.done(SECTBITS)

        # Prune unused entries in the array
        while self.fme.array:
            if self.fme.array[-1].lba.val != 0:
                break
            if self.fme.array[-1].f0.val == 3:
                break
            self.fme.array.pop(-1)
        self.bitmaps = []

    def render(self):
        if ELIDE_FREELIST:
            yield self.bt_name
        else:
            yield from super().render()

    def get_bit(self, lba):
        ''' Get status of bit of sector lba '''
        return self.bitmaps[lba // (7*1024)].get_bit(lba % (7*1024))

class FreeHead(bv.Struct):
    '''
    A pointer to a FreeMapSect
    --------------------------
    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f0_=-110,
            lba_=-24
        )

class FreeList(bv.Struct):
    '''
    As represented in the SuperBlock
    --------------------------------
    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            fh_=bv.Array(2, FreeHead, vertical=True),
        )
        self.fms = []
        self.bms = []

    def commit(self, ovtree):
        ''' Commit the tree of bitmaps '''
        for freehead in self.fh:
            fmsect = DoubleSectorBitView(
                ovtree,
                freehead.lba.val,
                'FM',
                'FreeMap',
            ).insert()
            freemap = FreeMapSect(fmsect.bv, 0).insert()
            self.fms.append(freemap)
            for fme in freemap.fme:
                bmsect = DoubleSectorBitView(
                    ovtree,
                    fme.lba.val,
                    'BM',
                    'BitMap',
                ).insert()
                bitmap = BitMapSect(bmsect.bv, 0).insert()
                self.bms.append(bitmap)

    def get_bit(self, lba):
        ''' Get status of bit of sector lba '''
        return self.bms[lba // (7*1024)].get_bit(lba % (7*1024))
