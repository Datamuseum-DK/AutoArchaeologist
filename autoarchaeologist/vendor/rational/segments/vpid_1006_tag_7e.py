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

class S00(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            s00_000_c_=-64,
            s00_001_p_=bv.Pointer(S01),
            s00_002_z_=bv.Pointer(S00),
            s00_003_p_=bv.Pointer(S00),
            s00_005_p_=-1
        )

class S01(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            s01_000_c_=bv.Pointer(S02),
            s01_001_b_=-3,
            s01_002_b_=-32,
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
            s02_060_p_=-32,
            s02_070_p_=-32,
            s02_080_p_=S03,
            s02_090_p_=S03,
        )

class S03(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            s03_000_p_=bv.Array(2, bv.Pointer(S05)),
            s03_001_p_=-80,
            s03_002_p_=S04,
            s03_003_p_=S04,
        )

class S04(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            s04_000_p_=-17,
            s04_001_p_=-32,
        )

class S05(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            s05_001_p_=bv.Pointer(S06),
        )

class S06(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            s06_001_p_=cm.ObjRef,
            s06_005_p_=bv.Pointer(),
        )

class S07(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            s07_001_p_=bv.Pointer(),
            s07_002_p_=bv.Pointer(),
        )

class SessionHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            hd_001_n_=-31,
            hd_002_n_=-64,
            hd_003_=bv.Pointer(),
            hd_004_=bv.Pointer(),
            hd_sh_=bv.Pointer(SessionSubHead),
        )

class S09(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            s09_001_p_=-2,
            s09_002_p_=bv.Pointer(S00),
        )

class SessionSubHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            sh_001_p_=bv.Pointer(),
            sh_002_p_=bv.Pointer(),
            sh_003_n_=-31,
            sh_004_s_=S09,
        )


class V1006T7E(cm.ManagerSegment):

    VPID = 1006
    TAG = 0x7e
    TOPIC = "Session"

    def spelunk_manager(self):
        self.head = SessionHead(self, self.seg_head.hi).insert()

        y = S07(self, self.head.hi).insert()
        y = bv.Pointer(cm.BTree)(self, y.hi).insert()

        y = cm.PointerArray(
            self,
            self.head.hd_sh.dst().sh_002_p.val,
            dimension=101,
            cls=S00,
        ).insert()

        for i in self.find_all(0xaeee):
            print(self.this, "FF", hex(i))
