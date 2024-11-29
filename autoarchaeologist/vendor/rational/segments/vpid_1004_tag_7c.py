#!/usr/bin/env python3

'''
   VPID 1004 - TAG 0x7c
   =========================================

   20240304 accounts for all bits in 20b035c69 from disk08
'''
    
from ....base import bitview as bv
from .common import Segment, Unallocated, SegHeap, StdHead, PointerArray, StringArray

class U00(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u00_000_c__=-32,
            u00_001_b_=-32,
            u00_002_p_=bv.Pointer(U02),
            u00_003_z__=-32,
            u00_004_p_=bv.Pointer(U01),
            u00_005_n_=-1,
            **kwargs,
        )
        assert self.u00_000_c_.val == 4
        assert self.u00_003_z_.val == 0

class U01(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u01_000_c__=-32,
            u01_001_p_=-32,
            u01_002_p_=bv.Pointer(U06),
            u01_003_z__=-32,
            u01_004_z__=-33,
            **kwargs,
        )
        assert self.u01_000_c_.val == 4
        assert self.u01_003_z_.val == 0
        assert self.u01_004_z_.val == 0

class U02(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u02_000_p_=bv.Pointer(U03),
            u02_001_b_=-32,
            u02_002_b_=-3,
            **kwargs,
        )

class U03(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            u03_000_b_=U10,
            u03_001_b_=U10,
            u03_002_b_=U10,
            u03_003_b_=U10,
            u03_004_b_=-254,
            u03_005_p_=U11,
            u03_012_p_=U11,
            u03_013_z__=-128,
            **kwargs,
        )
        assert self.u03_013_z_.val == 0

class U04(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u04_000_z_=-77,
            u04_001_p_=bv.Pointer(U05),
            u04_002_p_=bv.Pointer(U05),
            u04_003_p_=bv.Pointer(U05),
            u04_004_p_=bv.Pointer(U05),
            **kwargs,
        )

class U05(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u05_000_z_=-128,
            **kwargs,
        )

class U06(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u06_000_p_=bv.Pointer(U03),
            u06_001_n_=-32,
            u06_002_n_=-3,
            **kwargs,
        )

class U07(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u07_000_p_=bv.Pointer(U08),
            **kwargs,
        )

class U08(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u08_000_p_=-32,
            u08_001_p_=-32,
            u08_002_c__=-31,
            u08_003_p_=bv.Pointer(U08),
            **kwargs,
        )
        assert self.u08_002_c_.val == 1

class U09(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u09_000_p_=-94,
            u09_001_z__=-103,
            u09_002_n_=-8,
            u09_003_p_=bv.Pointer(U09),
            u09_004_p_=bv.Pointer(U09),
            u09_005_p_=bv.Pointer(U09),
            u09_006_p_=bv.Pointer(U09),
            **kwargs,
        )
        assert self.u09_001_z_.val == 0

class U10(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            u10_000_b_=-49,
            u10_001_b_=-24,
        )

class U11(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            u11_300_c_=-32,
            u11_200_c__=-32,
            u11_201_c_=-32,
            u11_100_c__=-32,
            u11_101_n_=-32,
            u11_102_n_=-30,
            u11_000_c__=-32,
            u11_001_z__=-32,
            u11_002_p_=bv.Pointer(U07),
            u11_003_z__=-32,
            u11_004_p_=bv.Pointer(U07),
        )
        assert self.u11_200_c_.val == 0x80000005
        assert self.u11_100_c_.val == 2
        assert self.u11_000_c_.val == 1
        assert self.u11_001_z_.val == 0
        assert self.u11_003_z_.val == 0

class U11Ptr(bv.Pointer_Class):
    TARGET = U11

class V1004T7C(Segment):

    VPID = 1004
    TAG = 0x7c

    def spelunk(self):
        open("/tmp/_b", "w").write(self.bits[0x6654d:].replace('0', '-'))

        self.seg_heap = SegHeap(self, 0).insert()
        self.std_head = StdHead(self, self.seg_heap.hi).insert()

        y = PointerArray(self, self.std_head.hd_011_p.val, dimension=101).insert()
        for i in y:
            U00(self, i.val, vertical=True).insert()

        if True:
            for i in range(128):
                U04(self, 0x301 + 333 * i).insert()

        if False:
           U09(self, 0x6654d).insert()
           U09(self, 0x70bcd).insert()
           U09(self, 0x7b24d).insert()
           U09(self, 0x858cd).insert()
           U09(self, 0x8ff4d).insert()
           U09(self, 0x9a5cd).insert()
           U09(self, 0xa4c4d).insert()
           U09(self, 0xaf2cd).insert()
           U09(self, 0xb994d).insert()
           U09(self, 0xc3fcd).insert()

        if False:
            for o in range(-160, 160):
                for a in (
                    0x6654d,
                    0x70bcd,
                    0x7b24d,
                    0x858cd,
                    0x9a5cd,
                    0xa4c4d,
                    0xaf2cd,
                    0xb994d,
                    0xc3fcd,
                ):
                    p = bin((1<<31)|(a+o))[3:]
                    j = self.bits.find(p)
                    if j > -1:
                        print("F07", hex(a), o, hex(a+o), hex(j), p)

