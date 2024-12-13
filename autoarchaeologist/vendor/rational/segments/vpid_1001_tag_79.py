#!/usr/bin/env python3

'''
   VPID 1001 - TAG 0x79
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        ADA            1001
        […]


'''
    
from ....base import bitview as bv
from .common import Segment, Unallocated, SegHeap, StdHead, PointerArray, StringArray

class A00(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            hd_000_n_=-32,
            hd_001_n_=-32,
            hd_002_n_=-32,
            hd_003_n_=-32,
            hd_004_n_=-32,
            hd_005_n_=-32,
            hd_006_n_=-32,
            hd_007_p_=bv.Pointer(A13),
            hd_008_n_=-32,
            hd_009_p_=bv.Pointer(A07),
            hd_010_n_=-32,
            hd_011_p_=bv.Pointer(),
            hd_012_n_=-32,
            hd_013_n_=-1,
            hd_014_n_=bv.Pointer(A12),
        )

class A13(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a13_000_n_=-6,
            a13_001_n_=-32,
            a13_002_p_=-32,
            a13_003_n_=-32,
            a13_004_p_=bv.Pointer(A08),
            a13_005_n_=-32,
            a13_006_p_=bv.Pointer(),
            a13_007_n_=-32,
            a13_008_p_=bv.Pointer(A09),
            vertical=True,
        )

class A01(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a01_000_n_=-32,
            a01_001_n_=bv.Pointer(A05),
            a01_002_n_=-32,
            a01_003_n_=-32,
            a01_004_n_=-32,
            a01_005_n_=-32,
        )

class A02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a02_000_n_=-100,
            a02_001_n_=bv.Pointer(A02),
        )

class A03(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a03_050_n_=-32,
            a03_051_n_=-32,
            a03_052_n_=bv.Pointer(A04),
            a03_053_n_=bv.Pointer(A03),
            a03_054_n_=bv.Pointer(A03),
            a03_055_n_=-1,
        )

class A04(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a04_050_n_=bv.Pointer(A05),
            a04_051_n_=-35,
        )

class A05(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a05_000_n_=-0x3ae,
        )

class A06(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a06_045_n_=-32,
            a06_046_n_=-32,
            a06_047_n_=-32,
        )

class A07(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a07_049_n_=-205,
            a07_070_n_=bv.Pointer(A07),
            a07_090_n_=bv.Pointer(A07),
            a07_091_n_=bv.Pointer(A07),
            a07_092_n_=bv.Pointer(A07),
        )


class A08(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a08_050_n_=-32,
            a08_051_n_=bv.Pointer(A06),
            a08_052_n_=-96,
        )

class A09(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a09_050_n_=-32,
        )

class A10(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a10_050_n_=-0x3ae,
        )

class A11(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a11_050_n_=bv.Pointer(A10),
            a11_099_n_=-35,
        )

class A12(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            a12_000_n_=-64,
            a12_002_n_=bv.Pointer(A11),
            a12_003_n_=bv.Pointer(A12),
            a12_004_n_=-33,
        )

class V1001T79(Segment):

    VPID = 1001
    TAG = 0x79

    def spelunk(self):

        self.seg_heap = SegHeap(self, 0).insert()

        self.a00 = A00(self, self.seg_heap.hi).insert()

        y = PointerArray(
            self,
            self.a00.hd_007_p.dst().a13_006_p.val,
            dimension=1009,
            cls=A02,
        ).insert()

        PointerArray(
            self,
            self.a00.hd_011_p.val,
            dimension=1009,
            cls=A03,
        ).insert()

        if False:
            for lo, hi in self.gaps():
                self.pointers_internal(lo, hi)
                if lo > 0x40000:
                    self.pointers_inside(lo, hi)
                    self.pointers_into(lo, hi)
        if False:
            for i in self:
                if isinstance(i, A05):
                    self.pointers_internal(i.lo, i.hi)
                    #self.pointers_inside(i.lo, i.hi)
                    #self.pointers_into(i.lo, i.hi)
        return

    def pointers_internal(self, lo, hi):
        print("PEGO", hex(lo), hex(hi))
        for adr in range(lo, hi - 32):
            p = int(self.bits[adr:adr+32], 2)
            if p < lo or p > hi:
                continue
            for hit in self.find(p):
                if hit.lo != p:
                    continue
                print(
                    hex(lo),
                    "+", hex(adr - lo),
                    "->",
                    hex(hit.lo),
                    hit.__class__.__name__,
                )
    def pointers_inside(self, lo, hi):
        print("POUT", hex(lo), hex(hi))
        for adr in range(lo, hi - 32):
            p = int(self.bits[adr:adr+32], 2)
            if p < 0x1000:
                continue
            for hit in self.find(p):
                if hit.lo != p:
                    continue
                print(
                    hex(lo),
                    "+", hex(adr - lo),
                    "->",
                    hex(hit.lo),
                    hit.__class__.__name__,
                )

    def pointers_into(self, lo, hi):
        print("PIN", hex(lo), hex(hi))
        for adr in range(lo, hi):
            for hit in self.find_all(adr):
                w = list(self.find(hit))
                if not w:
                    print(
                        hex(lo),
                        "+",
                        hex(adr-lo),
                        "<-",
                        hex(hit),
                        "= .+",
                        hex(hit-lo),
                    )
                else:
                    for x in w:
                        print(
                            hex(lo),
                            "+",
                            hex(adr-lo),
                            "<-",
                            hex(hit),
                            x.__class__.__name__,
                            hex(hit - x.lo)
                        )

