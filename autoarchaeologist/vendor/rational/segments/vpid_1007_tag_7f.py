#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

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
            mgr_001_n_=-31,
            mgr_002_n_=bv.Array(2, -32),
            mgr_003_p_=bv.Array(2, bv.Pointer()),
            hd_sh_=bv.Pointer(TapeSubHead),
            hd_002_n_=bv.Pointer(),
        )

class TapeSubHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            sh_000_c_=bv.Pointer(),
            sh_001_b_=bv.Pointer(T00),
            sh_002_b_=-31,
            sh_003_b_=T04,
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
            vertical=True,
            t00_000_c_=bv.Array(4, bv.Pointer(T01), vertical=True),
        )

class T01(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            t01_000_c_=bv.Array(2, -32),
            t01_002_c_=bv.Pointer(T02),
            t01_003_c_=bv.Pointer(T02),
            t01_004_c_=bv.Pointer(T02),
            t01_005_c_=-1,
        )

class T02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            t02_000_c_=-2,
            t02_000_s_=T03,
            t02_001_s_=T03,
            t02_008_c_=cm.TimedProperty,
            t02_009_c_=cm.TimedProperty,
            t02_010_c_=cm.TimedProperty,
            t02_011_c_=-3,
            t02_012_c_=-32,
            more=True
        )
        self.done()

class T03(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=False,
            t03_000_d_=cm.ObjRef,
            t03_001_c_=-32,
        )

class T04(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=False,
            t04_000_d_=-2,
            t04_001_c_=-32,
        )

class V1007T7F(cm.ManagerSegment):

    VPID = 1007
    TAG = 0x7F
    TOPIC = "Tape"

    def spelunk_manager(self):
        self.head = TapeHead(self, self.seg_head.hi).insert()
        bv.Pointer(cm.BTree)(self, self.head.hi).insert()
