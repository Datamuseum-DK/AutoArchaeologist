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
from . import common as cm

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

class F04(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            f04_000_n_=-1,
            f04_001_n_=cm.TimeStampPrecise,
            f04_002_n_=-15,
            f04_003_n_=-24,
        )

class F06(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            f06_000_n_=bv.Array(7, cm.AclEntry, vertical=True),
            f06_002_n_=-64,
            f06_updated_=cm.TimedProperty,
            f06_004_n_=cm.ObjRef,
            f06_version_=-32,
        )

class F02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,

            f02_000_n_=cm.TimedProperty,
            f02_001_n_=cm.TimedProperty,

            f02_040_n_=-70,

            f02_050_n_=-64,
            f02_051_n_=-64,

            f02_068_n_=F06,
            f02_091_n_=F06,
        )

class FileHead(bv.Struct):

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
            hd_007_p_=bv.Pointer(),
            hd_008_n_=-32,
            hd_009_p_=bv.Pointer(cm.BTree),
            hd_010_n_=-32,
            hd_011_p_=bv.Pointer(),
            hd_012_n_=-32,
            hd_013_n_=-32,
        )

class V1003T7B(cm.ManagerSegment):

    VPID = 1003
    TAG = 0x7b
    TOPIC = "File"

    def spelunk_manager(self):

        self.std_head = FileHead(self, self.seg_head.hi).insert()

        cm.PointerArray(
            self,
            self.std_head.hd_011_p.val,
            dimension=1009,
            cls = F00,
        ).insert()
