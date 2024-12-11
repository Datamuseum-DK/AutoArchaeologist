#!/usr/bin/env python3

'''
   VPID 1003 - TAG 0x7b
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        FILE            1003
        […]

   hd_002_n is highest file number ?

'''
    
from ....base import bitview as bv
from .common import Segment, Unallocated, SegHeap, StdHead, PointerArray, StringArray

class F00(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            f00_000_n_=-32,
            f00_001_n_=-32,
            f00_002_n_=bv.Pointer(F01),
            f00_003_n_=bv.Pointer(F00),
            f00_004_n_=bv.Pointer(F00),
            f00_099_n_=-1,
        )

class F01(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            f01_000_n_=bv.Pointer(F02),
            f01_099_n_=-0x23,
        )

class F02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            f02_099_n_=-1068,
        )
        # self.int_ptr()

    def int_ptr(self):
        for a in range(len(self)-32):
            for b in self.tree.find_all(self.lo + a, self.lo, self.hi):
                print("F02 0x%x" % self.lo, hex(a), hex(b), hex(b-self.lo))

class F03(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            f03_099_n_=-333,
        )

class V1003T7B(Segment):

    VPID = 1003
    TAG = 0x7b


    def spelunk(self):

        self.seg_heap = SegHeap(self, 0).insert()

        self.std_head = StdHead(self, self.seg_heap.hi).insert()

        y = PointerArray(
            self,
            self.std_head.hd_011_p.val,
            dimension=1009,
            cls = bv.Pointer(F00),
        ).insert()

        bv.Array(108, F03)(
            self,
            self.std_head.hd_009_p.val,
            vertical=True
        ).insert()
