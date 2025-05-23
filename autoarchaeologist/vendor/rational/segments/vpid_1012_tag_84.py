#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1012 - TAG 0x84 - Link
   ===========================

   FE_HANDBOOK.PDF 187p: Note: […] The D2 mapping is:

	[…]
	LINK		1012
	[…]

   Layout based descriptions in pure segment ⟦d0b0577a2⟧
'''

from ....base import bitview as bv
from . import common as cm

class LinkHead(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x296101 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=cm.FarPointer,			# LH05
            m003_p_=bv.Pointer.to(LH04),		# LH04
            m004_p_=cm.FarPointer.to(LH03),
        )

class LH03(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x299221 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Array(2, bv.Pointer.to(LH06)),	# Not Far
        )

class LH04A(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x299c29 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-0x2,
            m001_p_=bv.Pointer.to(LH07),
        )

class LH04(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x299609 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=bv.Pointer.to(LH07),
            m001_p_=bv.Pointer.to(LH08),
            m002_n_=-0x1f,
            m003_s_=LH04A,
        )

class LH06A(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x29a941 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-0x2,
            m001_p_=bv.Pointer.to(LH09),
        )


class LH06(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x29a321 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Pointer.to(LH09),
            m001_p_=bv.Pointer.to(LH10),
            m002_n_=-0x1f,
            m003_s_=LH06A,
        )

class LH07(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x29b039 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=cm.ObjName,
            m001_p_=bv.Pointer.to(LH11),
            m002_p_=bv.Pointer.to(LH07),
            m003_p_=bv.Pointer.to(LH07),
            m004_n_=-1,
        )

class LH08(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x29bb91 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Array(0x3b, bv.Pointer.to(LH07), vertical=True),
        )

class LH09(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x29c1e1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=False,
            m000_n_=cm.ObjName,
            m001_s_=cm.ObjRef,
            m002_p_=bv.Pointer.to(LH09),
            m003_p_=bv.Pointer.to(LH09),
            m004_n_=-1,
        )

class LH10(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x29d5d9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Array(0x3b, bv.Pointer.to(LH09), vertical=True),
        )

class LH11(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x29dc29 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Pointer.to(LH12),
            m001_n_=-3,
            m002_n_=-32,
        )

class LH12A(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x29ffc9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            #vertical=True,
            m000_n_=cm.FarPointer,
            m001_n_=cm.FarPointer,
        )

class LH12B(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x2a0519 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=LH12C,
            m001_n_=cm.FarPointer,			# LH14
            m002_s_=cm.TimedProperty,
            m003_s_=cm.ObjRef,
            m004_n_=-32,
        )

class LH12C(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x2a2be1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m001_n_=bv.Array(2, -32),
            m000_s_=cm.ObjRef,
        )

class LH12(bv.Struct):
    ''' ⟦d0b0577a2⟧ @ 0x29e3b1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_s_=cm.TimedProperty,
            m001_s_=cm.TimedProperty,
            m002_n_=-1,
            m003_n_=-2,
            m004_n_=-1,
            m005_n_=-1,
            m006_n_=-1,
            m007_p_=cm.FarPointer,			# LH14
            m008_s_=LH12A,
            m009_s_=LH12B,
            m010_s_=LH12B,
        )

class V1012T84(cm.ManagerSegment):
    ''' Link - VPID 1012 - TAG 0x84 '''

    VPID = 1012
    TAG = 0x84
    TOPIC = "Link"

    def spelunk_manager(self):
        head = LinkHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
