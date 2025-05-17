#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1011 - TAG 0x83 - Code_Segment
   ===================================

   FE_HANDBOOK.PDF 187p: Note: […] The D2 mapping is:

	[…]
	CODE_SEGMENT	1011
	[…]

   Layout based descriptions in pure segment ⟦ebef7d413⟧
'''

from ....base import bitview as bv
from . import common as cm

class CodeSegHead(bv.Struct):
    ''' ⟦ebef7d413⟧ @ 0x10ac84c '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=bv.Array(2, bv.Pointer),			#CS05
            m003_p_=bv.Array(2, bv.Pointer.to(CS04)),		#CS04
            m004_p_=bv.Array(2, bv.Pointer.to(CS03)),		#CS03
        )

class CS03A(bv.Struct):
    ''' ⟦ebef7d413⟧ @ 0x10afe14 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_b__=-0x4000,
            m001_n_=-14,
            m002_n_=-14,
            m003_n_=-31,
        )

class CS03(bv.Struct):
    ''' ⟦ebef7d413⟧ @ 0x10af96c '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_a_=bv.Array(0x2ff, CS03A, vertical=True),
            m001_p_=bv.Pointer.to(CS06),
        )

class CS04A(bv.Struct):
    ''' ⟦ebef7d413⟧ @ 0x10b14c4 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-2,
            m001_p_=bv.Pointer.to(CS07), 			#CS07
        )

class CS04(bv.Struct):
    ''' ⟦ebef7d413⟧ @ 0x10b0ea4 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Pointer.to(CS07),			#CS07
            m001_p_=bv.Pointer.to(CS08), 			#CS08
            m002_n_=-31,
            m003_n_=CS04A,
        )

class CS06(bv.Struct):
    ''' ⟦ebef7d413⟧ @ 0x10b1bbc '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-31,
            m001_p_=bv.Pointer.to(CS06),
        )

class CS07(bv.Struct):
    ''' ⟦ebef7d413⟧ @ 0x10b2174 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=bv.Array(2, -32),
            m001_p_=bv.Pointer.to(CS09),
            m002_p_=bv.Pointer.to(CS07),
            m003_p_=bv.Pointer.to(CS07),
            m004_p_=-1,
        )

class CS08(bv.Struct):
    ''' ⟦ebef7d413⟧ @ 0x10b2ccc '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_a_=bv.Array(0x3f1, bv.Pointer.to(CS07), vertical=True, elide=(0,)),
        )

class CS09A(bv.Struct):
    ''' ⟦ebef7d413⟧ @ 0x10b345c '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-24,
            m001_n_=-24,
            m002_p_=bv.Array(2, -32),
            m003_n_=-1,
            m004_n_=-1,
            m005_n_=-1,
            m006_n_=cm.ObjRef,
            m007_n_=cm.ObjRef,
            m008_n_=-32,
            m009_n_=-32,
            m010_n_=cm.TimedProperty,
            m011_n_=cm.TimedProperty,
            m012_n_=cm.TimedProperty,
            m013_n_=cm.TimedProperty,
            m014_n_=-16,
            m015_n_=-16,
        )

class CS09(bv.Struct):
    ''' ⟦ebef7d413⟧ @ 0x10b331c '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_s_=CS09A,
            m001_n_=-3,
            m002_n_=-32,
        )

class V1011T83(cm.ManagerSegment):
    ''' Code Segment Manager Segment - VPID 1011 - TAG 0x83 '''

    VPID = 1011
    TAG = 0x83
    TOPIC = "Code_Segment"

    def spelunk_manager(self):
        head = CodeSegHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
