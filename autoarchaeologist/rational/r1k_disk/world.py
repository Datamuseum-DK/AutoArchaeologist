#!/usr/bin/env python3

'''
   Worlds and trees thereof
   ========================
'''

from ...base import bitview as bv

from .defs import SECTBITS, AdaArray, SectorBitView, LSECSHIFT, OBJECT_FIELDS
from .freelist import FreeList
from .segment import Segment

class WorldIndexRec(bv.Struct):
    ''' ... '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            world_=-10,
            snapshot_=-31,
            lba_=-24,
        )

class WorldIndex(bv.Struct):
    '''
    A node in the world tree
    ------------------------

    '''

    def __init__(self, ovtree, lba):
        sect = SectorBitView(ovtree, lba, 'WT', "WorldTree").insert()
        super().__init__(
            sect.bv,
            0,
            vertical=True,
            **OBJECT_FIELDS,
            f0_=-8,
            f1_=10,
            cnt_=-7,
            aa_=AdaArray,
            more=True,
        )
        self.add_field(
            "worldlists",
            bv.Array(self.cnt.val, WorldIndexRec, vertical=True)
        )
        self.done(SECTBITS)
        self.insert()
        for wir in self.worldlists:
            wir.obj = WorldList(ovtree, wir.lba.val)

    def __iter__(self):
        for wir in self.worldlists:
            yield from wir.obj


class WorldListRec(bv.Struct):
    ''' ... '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            world_=-10,
            snapshot_=-31,
            f2_=-75,
            f6_=-20,
            f5_=-44,
            volume_=-4,
            lba_=-24,
            f4_=-1,
        )

class WorldList(bv.Struct):
    '''
    A node in the world tree
    ------------------------

    '''

    def __init__(self, ovtree, lba):
        sect = SectorBitView(ovtree, lba, 'WT', "WorldTree").insert()
        super().__init__(
            sect.bv,
            0,
            vertical=True,
            **OBJECT_FIELDS,
            f0_=-8,
            f1_=-9,
            cnt_=-6,
            aa_=AdaArray,
            more=True,
        )
        self.add_field(
            "worlds",
            bv.Array(self.cnt.val, WorldListRec, vertical=True)
        )
        self.done(SECTBITS)
        self.insert()

    def __iter__(self):
        yield from self.worlds

class WorldPtr(bv.Struct):
    ''' ... '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f1_=-10,
            f2_=-24,
            snapshot_=-31,
            lba_=-24,
        )

class World(bv.Struct):
    '''
    A node in the world tree
    ------------------------

    '''

    def __init__(self, ovtree, lba):
        sect = SectorBitView(ovtree, lba, 'W', "World").insert()
        super().__init__(
            sect.bv,
            0,
            vertical=True,
            **OBJECT_FIELDS,
            wl0_=-9,
            more=True,
        )
        if self.wl0.val == 1:
            self.add_field("wl1", -9)
            self.add_field("cnt", -7)
            self.add_field("aa", AdaArray)
            self.add_field(
                "worlds1",
                bv.Array(self.cnt.val, WorldPtr, vertical=True)
            )
        else:
            self.add_field("wl2", -6)
            self.add_field("cnt", -4)
            self.add_field("aa", AdaArray)
            self.add_field(
                "worlds2",
                bv.Array(self.cnt.val, Segment, vertical=True)
            )
        self.done(SECTBITS)
        self.insert()

        if self.wl0.val == 1:
            for wptr in self.worlds1:
                if wptr.snapshot.val == 0:
                    continue
                World(ovtree, wptr.lba.val)
        elif 1:
            for seg in self.worlds2:
                if seg.vol.val != ovtree.sblk.volnbr.val:
                    print("DIFF VOL", seg.vol.val, ovtree.volnbr.val, seg)
                if seg.multiplier.val not in (0x1, 0xa2):
                    continue
                #seg.check(ovtree)
                #seg.traverse(ovtree)
