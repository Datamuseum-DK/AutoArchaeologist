#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1016 - TAG 0x88 - Program_Library
   ======================================

   FE_HANDBOOK.PDF 187p: Note: […] The D2 mapping is:

	[…]
	PROGRAM_LIBRARY	1016
	[…]

   Layout based descriptions in pure segment ⟦bfac457fc⟧
'''

from ....base import bitview as bv
from . import common as cm

class ProgLibHead(bv.Struct):
    ''' ⟦bfac457fc⟧ @ 0x101115 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=bv.Array(2, bv.Pointer),	# PL05
            m003_p_=bv.Pointer.to(PL04),	# PL04
            m004_p_=bv.Array(2, bv.Pointer.to(PL03)),    # PL03
        )

class PL03(bv.Struct):
    ''' ⟦bfac457fc⟧ @ 0x104235 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_p_=bv.Array(2, bv.Pointer.to(PL06)),
        )

class PL04A(bv.Struct):
    ''' ⟦bfac457fc⟧ @ 0x104c3d '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_p_=-2,
            m001_p_=bv.Pointer.to(PL07),
        )

class PL04(bv.Struct):
    ''' ⟦bfac457fc⟧ @ 0x10461d '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=bv.Pointer.to(PL07),
            m001_p_=bv.Pointer.to(PL08),
            m002_n_=-31,
            m003_n_=PL04A,
        )

class PL06(bv.Struct):
    ''' ⟦bfac457fc⟧ @ 0x105335 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_h_=bv.Array(2, bv.Pointer.to(PL09)),
        )

class PL07(bv.Struct):
    ''' ⟦bfac457fc⟧ @ 0x10571d '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_=bv.Array(2, -32),
            m001_=bv.Pointer.to(PL10),
            m002_=bv.Pointer.to(PL07),
            m003_=bv.Pointer.to(PL07),
            m004_=-1,
        )

class PL08(bv.Struct):
    ''' ⟦bfac457fc⟧ @ 0x106275 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_=bv.Array(0x3b, bv.Pointer.to(PL07), vertical=True),
        )

class PL09(bv.Struct):
    ''' ⟦bfac457fc⟧ @ 0x1068c5 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_h_=bv.Pointer,
        )

class PL10(bv.Struct):
    ''' ⟦bfac457fc⟧ @ 0x106cad '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_=bv.Pointer.to(PL12),
            m001_=-3,
            m002_=-32,
        )

class PL12A(bv.Struct):
    ''' ⟦bfac457fc⟧ @ 0x10ab05 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_s_=bv.Array(2, -32),
            m001_s_=bv.Array(2, -32),
        )

class PL12B(bv.Struct):
    ''' ⟦bfac457fc⟧ @ 0x10b055 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-1,
            m001_h_=bv.Array(2, -32),
            m002_s_=cm.TimedProperty,
            m003_s_=cm.ObjRef,
            m004_n_=-32,
        )

class PL12(bv.Struct):
    ''' ⟦bfac457fc⟧ @ 0x108eed '''

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
            m007_h_=bv.Array(2, -32),
            m008_s_=PL12A,
            m009_s_=PL12B,
            m010_s_=PL12B,
        )

class V1016T88(cm.ManagerSegment):
    ''' Program_Library Manager Segment - VPID 1016 - TAG 0x88 '''

    VPID = 1016
    TAG = 0x88
    TOPIC = "Program_Library"

    def spelunk_manager(self):
        head = ProgLibHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
