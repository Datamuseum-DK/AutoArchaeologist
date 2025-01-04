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
from .common import ManagerSegment, PointerArray, StdHead, TimeStampPrecise, ObjRef

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
            g02_000_p_=G10,
            g02_010_p_=G10,
            g02_020_p_=G10,
            g02_030_p_=G10,
            g02_040_p_=ObjRef,
            g02_050_p_=-32,
            g02_060_p_=-32,
            g02_070_p_=-31,
            g02_080_p_=-32,
            g02_090_p_=-32,
            g02_098_p_=-10,
            g02_099_p_=-10,
            vertical=True,
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

class G10(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            u10_000_b_=-1,
            u10_002_b_=TimeStampPrecise,
            u10_003_b_=-15,
            u10_010_b_=-24,
        )

class GroupHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            hd_001_n_=-32,
            hd_002_n_=-32,
            hd_003_n_=-32,
            hd_004_n_=-32,
            hd_005_n_=-32,
            hd_006_n_=-31,
            hd_007_p_=bv.Pointer(bv.Array(1024, -1)),
            hd_008_n_=-32,
            hd_009_p_=bv.Pointer(G04),
            hd_010_n_=-32,
            hd_011_p_=bv.Pointer(),
            hd_012_n_=-32,
            hd_013_n_=-33,
        )

class V1005T7D(ManagerSegment):

    VPID = 1005
    TAG = 0x7d
    TOPIC = "Group"

    def spelunk_manager(self):

        self.head = GroupHead(self, self.seg_head.hi).insert()

        y = PointerArray(
            self,
            self.head.hd_011_p.val,
            dimension=101,
            cls=G00,
        ).insert()
