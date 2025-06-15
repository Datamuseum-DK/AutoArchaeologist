#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Worlds and trees thereof
   ========================

FE_HANDBOOK.PDf 187p

Note: [...] The D2 mapping is:

	ADA		1001
	DDB		1002
	FILE		1003
	USER		1004
	GROUP		1005
	SESSION		1006
	TAPE		1007
	TERMINAL	1008
	DIRECTORY	1009
	CONFIGURATION	1010
	CODE_SEGMENT	1011
	LINK		1012
	NULL_DEVICE	1013
	PIPE		1014
	ARCHIVED_CODE	1015
	PROGRAM_LIBRARY	1016

'''

from ....base import bitview as bv

from .defs import AdaArray
from .object import ObjSector
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

class WorldIndex(ObjSector):
    '''
    A node in the world tree
    ------------------------

    '''

    def __init__(self, ovtree, lba):
        super().__init__(
            ovtree,
            lba,
            vertical=True,
            what="W",
            legend="World",
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
        self.done()
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

class WorldList(ObjSector):
    '''
    A node in the world tree
    ------------------------

    '''

    def __init__(self, ovtree, lba):
        super().__init__(
            ovtree,
            lba,
            what="W",
            legend="World",
            vertical=True,
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
        self.done()
        self.insert()

    def __iter__(self):
        yield from self.worlds

class WorldPtr(bv.Struct):
    ''' ... '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vpid_=-10,
            segid_=-24,
            snapshot_=-31,
            lba_=-24,
        )

class World(ObjSector):
    '''
    A node in the world tree
    ------------------------

    '''

    def __init__(self, ovtree, lba):
        super().__init__(
            ovtree,
            lba,
            what="W",
            legend="World",
            vertical=True,
            wl0_=-9,
            more=True,
        )
        assert self.wl0.val in (1, 2)
        if self.wl0.val == 1:
            self.add_field("wl1", -9)
            assert self.wl1.val == 0x57
            self.add_field("cnt", -7)
            self.add_field("aa", AdaArray)
            self.add_field(
                "worlds1",
                bv.Array(self.cnt.val, WorldPtr, vertical=True)
            )
        elif self.wl0.val == 2:
            self.add_field("wl2", -6)
            assert self.wl2.val == 0x28
            self.add_field("cnt", -4)
            self.add_field("aa", AdaArray)
            self.add_field(
                "segs",
                bv.Array(self.cnt.val, SegmentDesc, vertical=True)
            )
        else:
            print("BAD WL0", self.wl0.val, self)
        self.done()
        self.insert()
        self.ovtree = ovtree


    def iter_worlds(self):
        ''' ... '''
        yield self
        if self.wl0.val != 1:
            return
        for wptr in self.worlds1:
            world = World(self.ovtree, wptr.lba.val)
            yield from world.iter_worlds()

    def commit_segments(self, r1ksys):
        ''' ... '''
        if self.wl0.val != 2:
            return
        for segdesc in self.segs:
            segdesc.commit(r1ksys, r1ksys.volumes[segdesc.vol.val])
