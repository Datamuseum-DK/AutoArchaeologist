#!/usr/bin/env python3

'''
   Worlds and trees thereof
   ========================
'''

from ...base import bitview as bv

from .defs import SECTBITS, AdaArray, SectorBitView, LSECSHIFT, OBJECT_FIELDS
from .freelist import FreeList
from .segment import SegmentDesc

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
            vertical=False,
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
            f6_=-21,
            f5_=-42,
            volume_=-5,
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
            vertical=False,
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
            vertical=False,
            **OBJECT_FIELDS,
            wl0_=-9,
            more=True,
        )
        if self.id_kind.val not in (0x0, 0x92, 0xbe, 0x125):
            print("BAD WORLD KIND", hex(self.id_kind.val))
        if self.id_lba.val != lba:
            print("BAD WORLD LBA", hex(lba), hex(self.id_lba.val))
        if self.wl0.val == 1:
            self.add_field("wl1", -9)
            self.add_field("cnt", -7)
            self.add_field("aa", AdaArray)
            self.add_field(
                "worlds1",
                bv.Array(self.cnt.val, WorldPtr, vertical=True)
            )
        elif self.wl0.val == 2:
            self.add_field("wl2", -6)
            self.add_field("cnt", -4)
            self.add_field("aa", AdaArray)
            self.add_field(
                "worlds2",
                bv.Array(self.cnt.val, SegmentDesc, vertical=True)
            )
        else:
            print("BAD WL0", self.wl0.val, self)
        self.done(SECTBITS)
        self.insert()
        self.ovtree = ovtree


    def iter_worlds(self):
        yield self
        if self.wl0.val != 1:
            return
        for wptr in self.worlds1:
            world = World(self.ovtree, wptr.lba.val)
            yield from world.iter_worlds()

    def commit_segments(self):
        if self.wl0.val != 2:
            return
        for segdesc in self.worlds2:
            i = segdesc.commit(self.ovtree)
            if i:
                print("W", self)
                for j in i:
                    print(j)
            
