#!/usr/bin/env python3

'''
   VPID 1011 - TAG 0x83
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        CODE_SEGMENT    1011
        […]

'''
    
from ....base import bitview as bv
from .common import Segment, SegHeap, StdHead, PointerArray, StringArray

class CS94(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            cs94_000_z_=-32,
            cs94_001_z_=-32,
            cs94_002_z_=bv.Pointer(),
        )

class CS95(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            cs95_099_z_=-128,
        )

class CS96(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            cs96_049_z_=-205,
            cs96_096_z_=bv.Pointer(CS96),
            cs96_097_z_=bv.Pointer(CS96),
            cs96_098_z_=bv.Pointer(CS96),
            cs96_099_z_=bv.Pointer(CS96),
        )

class CS97(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            cs97_099_z_=-728,
        )

class CS98(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            cs98_000_z_=-32,
            cs98_001_z_=-32,
            cs98_002_z_=bv.Pointer(CS97),
            cs98_003_z_=bv.Pointer(CS98),
            cs98_004_z_=bv.Pointer(CS98),
            cs98_099_z_=-1,
            #cs98_099_z_=-364,
        )

class CS99(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            cs99_099_z_=-16443,
        )

class CS99A(CS99):
    ''' ... '''

class CS99B(CS99):
    ''' ... '''

class CS99C(CS99):
    ''' ... '''


class V1011T83(Segment):

    VPID = 1011
    TAG = 0x83

    def spelunk(self):

        self.seg_heap = SegHeap(self, 0).insert()
        self.std_head = StdHead(self, self.seg_heap.hi).insert()

        y = PointerArray(
            self,
            self.std_head.hd_012_n.val,
            dimension=1009,
            cls=CS98,
        ).insert()

        CS96(self, self.std_head.hd_010_n.val).insert()

        # This looks like a huge bitmap...
        bv.Array(0x2fe, CS99A)(self, self.std_head.hd_008_n.val, vertical=True).insert()

     
 
