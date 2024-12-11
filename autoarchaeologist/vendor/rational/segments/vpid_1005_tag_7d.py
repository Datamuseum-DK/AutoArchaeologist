#!/usr/bin/env python3

'''
   VPID 1005 - TAG 0x7d
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        GROUP           1005
        […]

'''
    
from ....base import bitview as bv
from .common import Segment, SegHeap, StdHead, PointerArray

class Bla99(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            b99_000_b_=512,
        )

class G00(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g00_000_c_=-32,
            g00_001_b_=-32,
            g00_002_p_=bv.Pointer(G01),
            g00_003_z_=-32,
            g00_004_p_=bv.Pointer(G03),
            g00_005_n_=-1,
            #g00_004_p_=Pointer,
        )
        #assert self.g00_000_c_.val == 4
        #assert self.g00_003_z_.val == 0
        #self.points_to(bvtree, self.g00_002_p.val, G02)
        #self.points_to(bvtree, self.g00_004_p.val, G01)

class G01(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g01_000_c_=bv.Pointer(G02),
            g01_001_p_=-35,
        )
        #self.points_to(bvtree, self.g01_002_p.val, G06)
        #assert self.u01_000_c_.val == 4
        #assert self.u01_003_z_.val == 0
        #assert self.u01_004_z_.val == 0

class G02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g02_000_p_=-0x236,
        )

class G03(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g03_000_b_=-32,
            g03_001_b_=-32,
            g03_002_p_=bv.Pointer(G01),
            g03_004_b_=-32,
            g03_005_b_=-32,
            g03_006_b_=-1,
        )
        #assert self.u03_013_z_.val == 0

class G04(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g04_000_z_=-0xcd,
            g04_096_p_=bv.Pointer(G04),
            g04_097_p_=bv.Pointer(G04),
            g04_098_p_=bv.Pointer(G04),
            g04_099_p_=bv.Pointer(G04),
        )

class V1005T7D(Segment):

    VPID = 1005
    TAG = 0x7d

    def spelunk(self):

        self.seg_heap = SegHeap(self, 0).insert()
        self.std_head = StdHead(self, self.seg_heap.hi).insert()

        y = PointerArray(
            self,
            self.std_head.hd_011_p.val,
            dimension=101
        ).insert()

        for i in y:
            G00(self, i.val).insert()

        adr = self.std_head.hd_009_p.val
        y = G04(self, adr).insert()
