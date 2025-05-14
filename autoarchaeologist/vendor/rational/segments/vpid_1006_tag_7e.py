#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1006 - TAG 0x7e
   =========================================

   FE_HANDBOOK.PDF 187p

    Note: […] The D2 mapping is:

        […]
        SESSION          1006
        […]

   Layout based descriptions in pure segment ⟦1ba808117⟧
'''

from ....base import bitview as bv
from . import common as cm

class SessionHead(bv.Struct):
    ''' ⟦1ba808117⟧ @ 0x887e9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_=bv.Array(2, bv.Pointer), #5
            m003_=bv.Pointer.to(S04),
            m004_=bv.Array(2, bv.Pointer.to(S03)),
        )

class S03(bv.Struct):
    ''' ⟦1ba808117⟧ @ 0x8b909 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Array(2, bv.Pointer), # 6
        )

class S04A(bv.Struct):
    ''' ⟦1ba808117⟧ @ 0x8c311 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_c_=-2,
            m001_b_=bv.Pointer.to(S07),
        )

class S04(bv.Struct):
    ''' ⟦1ba808117⟧ @ 0x8bcf1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Pointer.to(S07),
            m001_p_=bv.Pointer.to(S08),
            m002_n_=-31,
            m003_s_=S04A,
        )

class S07(bv.Struct):
    ''' ⟦1ba808117⟧ @ 0x8cc19 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Array(2, -32),
            m001_p_=bv.Pointer.to(S09),
            m002_p_=bv.Pointer.to(S07),
            m003_p_=bv.Pointer.to(S07),
            m004_n_=-1,
        )

class S08(bv.Struct):
    ''' ⟦1ba808117⟧ @ 0x8d771 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Array(101, bv.Pointer.to(S07), vertical=True),
        )

class S09(bv.Struct):
    ''' ⟦1ba808117⟧ @ 0x8ddc1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_p_=bv.Pointer.to(S10),
            m001_n_=-3,
            m002_n_=-32,
        )

class S10A(bv.Struct):
    ''' ⟦1ba808117⟧ @ 0x920f9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Array(2, bv.Pointer.to(S11)),
            m001_n_=bv.Array(10, bv.Char),
            m002_s_=cm.DayTime,
            m003_s_=cm.DayTime,
        )

class S10(bv.Struct):
    ''' ⟦1ba808117⟧ @ 0x8e549 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=cm.TimedProperty,
            m001_p_=cm.TimedProperty,
            m002_p_=cm.TimedProperty,
            m003_p_=cm.TimedProperty,
            m004_p_=cm.ObjRef,
            m005_p_=cm.ObjRef,
            m006_p_=-32,
            m007_p_=-32,
            m008_p_=S10A,
            m009_p_=S10A,
        )

class S11(bv.Struct):
    ''' ⟦1ba808117⟧ @ 0x94c79 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            s05_001_p_=bv.Pointer.to(S12),
        )

class S12(bv.Struct):
    ''' ⟦1ba808117⟧ @ 0x95061 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            s06_001_p_=cm.ObjRef,
            s06_005_p_=bv.Pointer.to(S12),
        )

class V1006T7E(cm.ManagerSegment):
    ''' Session Manager Segment - VPID 1006 - TAG 0x7e '''

    VPID = 1006
    TAG = 0x7e
    TOPIC = "Session"

    def spelunk_manager(self):
        head = SessionHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
