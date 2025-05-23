#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1015 - TAG 0x87 - Archived_Code
   ====================================

   FE_HANDBOOK.PDF 187p: Note: […] The D2 mapping is:

	[…]
	ARCHIVED_CODE	1015
	[…]


   Layout based descriptions in pure segment ⟦25d5b4dea⟧
'''

from ....base import bitview as bv
from . import common as cm

class ArchCodeHead(bv.Struct):
    ''' ⟦25d5b4dea⟧ @ 0x150d9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=bv.Array(2, bv.Pointer.to(AC05)),
            m003_p_=bv.Pointer.to(AC04),
            m004_p_=cm.FarPointer.to(AC03),
        )

class AC03(bv.Struct):
    ''' ⟦25d5b4dea⟧ @ '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_a_=bv.Array(1, 32, vertical=True),
        )


class AC04A(bv.Struct):
    ''' ⟦25d5b4dea⟧ @ 0x18c01 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_p_=-2,
            m001_p_=bv.Pointer.to(AC07),
        )

class AC04(bv.Struct):
    ''' ⟦25d5b4dea⟧ @ 0x185e1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Pointer.to(AC07),
            m001_p_=bv.Pointer.to(AC08),
            m002_b_=-31,
            m003_b_=AC04A,
        )

class AC05(bv.Struct):
    ''' ⟦25d5b4dea⟧ @ '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_a_=bv.Array(1, 32, vertical=True),
        )


class AC07(bv.Struct):
    ''' ⟦25d5b4dea⟧ @ '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_a_=cm.ObjName,
            m001_=bv.Pointer.to(AC10),
            m002_=bv.Pointer.to(AC07),
            m003_=bv.Pointer.to(AC07),
            m004_=-1,
        )

class AC08(bv.Struct):
    ''' ⟦25d5b4dea⟧ @0x1a239 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_a_=bv.Array(0x3b, bv.Pointer.to(AC07), vertical=True, elide=(0,)),
        )

class AC10(bv.Struct):
    ''' ⟦25d5b4dea⟧ @ '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_=bv.Pointer.to(AC12),
            m001_=-3,
            m002_=-32,
        )

class AC12B(bv.Struct):
    ''' ⟦25d5b4dea⟧ @ 0x1f019 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            # m000 empty record
            m001_s_=cm.FarPointer,	# AC14
            m002_s_=cm.TimedProperty,
            m003_s_=cm.ObjRef,
            m004_n_=-32,
        )

class AC12A(bv.Struct):
    ''' ⟦25d5b4dea⟧ @ 0x1eac9'''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=cm.FarPointer,	# AC13
            m001_p_=cm.FarPointer,	# AC13
        )

class AC12(bv.Struct):
    ''' ⟦25d5b4dea⟧ @ 0x1ceb1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_s_=cm.TimedProperty,
            m001_s_=cm.TimedProperty,
            m002_p_=-1,
            m003_p_=-2,
            m004_p_=-1,
            m005_p_=-1,
            m006_p_=-1,
            m007_p_=cm.FarPointer,	# AC14
            m008_s_=AC12A,
            m009_s_=AC12B,
            m010_s_=AC12B,
        )

class V1015T87(cm.ManagerSegment):
    ''' Archived Code Manager Segment - VPID 1015 - TAG 0x87 '''

    VPID = 1015
    TAG = 0x87
    TOPIC = "Archived_Code"

    def spelunk_manager(self):
        head = ArchCodeHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
