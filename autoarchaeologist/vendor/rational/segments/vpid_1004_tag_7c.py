#!/usr/bin/env python3

'''
   VPID 1004 - TAG 0x7c
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        USER            1004
        […]

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
            u01_002_p_=bv.Pointer(U02),
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
            u02_001_n_=-3,
            u02_002_n_=-32,
            **kwargs,
        )

    def dot_node(self, dot):
        return None, ["color=red"]

class U03(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u03_000_b_=U10,	# = {0x1, 0x4, 0x12, 0x23
            u03_001_b_=U10,
            u03_002_b_=U10,
            u03_003_b_=U10,
            u03_004_c_=U04,
            u03_005_c_=U04,
            u03_006_c_=-32,	# = 0x01
            u03_007_n_=-32,	# = {0x0, 0x1}
            u03_009_s_=U17,
            u03_020_s_=U17,
            u03_099_z__=-128,	# = 0x0
            vertical=True,
            **kwargs,
        )
        assert self.u03_006_c.val == 1
        #assert self.u03_015_z_.val == 0
        #assert self.u03_026_z_.val == 0
        assert self.u03_099_z_.val == 0

    def dot_node(self, dot):
        return None, ["color=orange"]

class U04(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            u04_000_n_=-63,
            u04_001_c_=-32,
            **kwargs,
        )
        assert self.u04_001_c.val == 1

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

    def dot_node(self, dot):
        return None, ["color=green"]

class U10(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            u10_000_b_=-49,
            u10_010_b_=-24,
        )

class U13(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            u13_010_n_=bv.Pointer(U15),
        )

    def dot_node(self, dot):
        return None, ["shape=plaintext"]

class U14(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            u14_010_n_=bv.Pointer(U16),
        )

    def dot_node(self, dot):
        return None, ["shape=plaintext"]

class U15(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            u15_010_c_=-32,	# 0x80000005
            u15_020_n_=-31,
            u15_030_c_=-32,	# 0x01
            u15_040_n_=bv.Pointer(U15),
        )
        assert self.u15_010_c.val == 0x80000005
        assert self.u15_030_c.val == 0x1

    def dot_node(self, dot):
        return None, ["color=cyan"]

class U16(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            u16_010_c_=-32,	# 0x80000006
            u16_020_n_=-31,	#
            u16_030_c_=-32,	# 0x1
            u16_040_n_=bv.Pointer(U16),
        )
        assert self.u16_010_c.val == 0x80000006
        assert self.u16_030_c.val == 0x1

class U17(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            u17_000_n_=-32,
            u17_010_c_=-32,	# 0x80000005
            u17_020_n_=-31,
            u17_030_c_=-32,	# 0x01
            u17_040_n_=-32,
            u17_050_n_=-31,
            u17_060_n_=-32,
            u17_070_n_=-32,
            u17_080_p_=bv.Pointer(U13),
            u17_090_z_=-32,
            u17_100_p_=bv.Pointer(U14),
        )
        assert self.u17_010_c.val == 0x80000005
        assert self.u17_030_c.val == 0x1


class U26(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            u26_010_n_=-32,
            u26_020_n_=-32,
        )


class V1004T7C(Segment):

    VPID = 1004
    TAG = 0x7c

    def find_ptr(self, adr, width=32):
        print("FF", hex(adr), hex(self.bits.find(bin((1<<width)|adr)[3:])))

    def spelunk(self):


        self.seg_heap = SegHeap(self, 0).insert()
        self.std_head = StdHead(self, self.seg_heap.hi).insert()

        if True:
            # Possibly the array limits of hd_009_p
            U26(self, self.std_head.hd_007_p.val).insert()


        if True:
            U09(self, self.std_head.hd_009_p.val).insert()

        y = PointerArray(
            self,
            self.std_head.hd_011_p.val,
            dimension=101,
            cls=U00,
        ).insert()
