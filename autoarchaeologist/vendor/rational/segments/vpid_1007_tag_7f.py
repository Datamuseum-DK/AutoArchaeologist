#!/usr/bin/env python3

'''
   VPID 1007 - TAG 0x7f
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        TAPE            1007
        […]


'''
    
from ....base import bitview as bv
from . import common as cm

class TapeHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            thd_001_n_=-32,
            thd_002_n_=-31,
            thd_003_n_=-32,
            thd_004_n_=-32,
            thd_005_n_=-32,
            thd_006_n_=bv.Pointer(TapeSubHead),
            thd_007_n_=-32,
            thd_008_n_=bv.Pointer(cm.BTree),
        )

class TapeSubHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            tsh_000_c_=-32,
            tsh_001_b_=bv.Pointer(T00),
            tsh_002_b_=-32,
            tsh_003_b_=-32,
            tsh_004_b_=-1,
        )

class TapeTerHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            tth_000_c_=-32,
            tth_010_c_=bv.Array(100, -32, vertical=True),
       )

class T00(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            t00_000_c_=bv.Pointer(T01),
            t00_001_c_=bv.Pointer(T01),
            t00_002_c_=bv.Pointer(T01),
            t00_003_c_=bv.Pointer(T01),
            #t00_003_c_=-32,
            #t00_004_c_=-32,
            #t00_005_c_=-32,
        )

class T01(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            t01_000_c_=-32,
            t01_001_c_=-32,
            t01_002_c_=bv.Pointer(T02),
            t01_003_c_=-32,
            t01_004_c_=-32,
            t01_005_c_=-1,
        )

class T02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            t02_000_c_=-2,
            t02_000_d_=cm.ObjRef,
            t02_001_c_=-32,
            t02_002_c_=cm.ObjRef,
            t02_003_c_=-32,
            t02_008_c_=cm.TimedProperty,
            t02_009_c_=cm.TimedProperty,
            t02_010_c_=cm.TimedProperty,
            t02_011_c_=-35,
            more=True
        )
        self.done()

class V1007T7F(cm.ManagerSegment):

    VPID = 1007
    TAG = 0x7F
    TOPIC = "Tape"

    def spelunk_manager(self):
        self.head = TapeHead(self, self.seg_head.hi).insert()
