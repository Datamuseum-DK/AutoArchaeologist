#!/usr/bin/env python3

'''
   VPID 1008 - TAG 0x80
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        TERMINAL       1008
        […]

'''
    
from ....base import bitview as bv
from .common import Segment, SegHeap, StdHead, PointerArray, StringArray


class T97(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            t97_000_z_=-177,
            t97_006_z_=StringArray,
            t97_007_z_=-357,
            t97_008_z_=StringArray,
            t97_099_z_=-443,
        )

class T98(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            t98_000_z_=-32,
            t98_001_z_=-32,
            t98_002_z_=bv.Pointer(T97),
            t98_099_z_=-65,
        )

class T99(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            t99_049_z_=-205,
            t99_096_z_=bv.Pointer(T99),
            t99_097_z_=bv.Pointer(T99),
            t99_098_z_=bv.Pointer(T99),
            t99_099_z_=bv.Pointer(T99),
        )

class V1008T80(Segment):

    VPID = 1008
    TAG = 0x80

    def spelunk(self):

        self.seg_heap = SegHeap(self, 0).insert()
        self.std_head = StdHead(self, self.seg_heap.hi).insert()

        y = PointerArray(
            self,
            self.std_head.hd_010_n.val,
            dimension=257,
            cls=T98,
        ).insert()

        bv.Pointer(T99)(self, 0x34e).insert()

 
