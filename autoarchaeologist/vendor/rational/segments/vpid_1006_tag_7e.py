#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1006 - TAG 0x7e
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        SESSION          1006
        […]


'''
    
from ....base import bitview as bv
from . import common as cm


class SessionHead(bv.Struct):

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
            hd_013_n_=-33,
        )

class S00(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            s00_000_c_=-32,
            s00_001_b_=-32,
            s00_002_p_=bv.Pointer(S01),
            s00_003_z_=bv.Pointer(S00),
            s00_004_p_=bv.Pointer(S00),
            s00_005_p_=-1
        )

class S01(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            s01_000_c_=bv.Pointer(S02),
            s01_001_b_=-35,
        )

class S02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            s02_000_p_=cm.TimedProperty,
            s02_010_p_=cm.TimedProperty,
            s02_020_p_=cm.TimedProperty,
            s02_030_p_=cm.TimedProperty,
            s02_040_p_=cm.ObjRef,
            s02_050_p_=cm.ObjRef,
            #s02_050_p_=-32,
            #s02_060_p_=-32,
            #s02_070_p_=-31,
            s02_080_p_=-32,
            s02_090_p_=-32,
            s02_098_p_=-10,
            s02_099_p_=-10,

            s02_100_p_=S04,
            #s02_100_p_=-124,
            #s02_105_p_=cm.TimedProperty,
            #s02_110_p_=-45,

            s02_200_p_=S04,
            #s02_201_p_=-124,
            #s02_205_p_=cm.TimedProperty,
            #s02_210_p_=-45,

            s02_251_p_=-12,
            s02_300_p_=-32,
            more=True,
        )
        self.add_field("s02_400", -32)
        if self.s02_400.val:
            self.add_field("s02_401", S03)
        self.add_field("s02_500", -32)
        if self.s02_500.val:
            self.add_field("s02_501", S03)
        self.done()

class S03(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            s04_000_p_=cm.ObjRef,
            s04_010_p_=-32,
        )

class S04(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            s04_000_p_=-124,
            s04_010_p_=cm.TimedProperty,
            s04_020_p_=-45,
        )

class V1006T7E(cm.ManagerSegment):

    VPID = 1006
    TAG = 0x7e
    TOPIC = "Session"

    def spelunk_manager(self):
        self.head = SessionHead(self, self.seg_head.hi).insert()

        y = cm.PointerArray(
            self,
            self.head.hd_011_p.val,
            dimension=101,
            cls=S00,
        ).insert()
