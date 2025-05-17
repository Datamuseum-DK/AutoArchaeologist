#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1001 - TAG 0x79 - Ada
   ==========================

   FE_HANDBOOK.PDF 187p: Note: […] The D2 mapping is:

	[…]
	ADA		1001
	[…]

   Layout based descriptions in pure segment ⟦adef73778⟧
'''

from ....base import bitview as bv
from . import common as cm

class AdaHead(bv.Struct):
    ''' ⟦adef73778⟧ @0x73593b1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=bv.Array(2, bv.Pointer),		# A05
            m003_p_=bv.Pointer.to(A04),
            m004_p_=bv.Array(2, bv.Pointer.to(A03)),
        )

class A03(bv.Struct):
    ''' ⟦adef73778⟧ @0x735c4d1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Array(2, bv.Pointer.to(A06)),	#AX06
        )

class A04A(bv.Struct):
    ''' ⟦adef73778⟧ @0x735ced9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_p_=-2,
            m001_p_=bv.Pointer,				#A07
        )

class A04(bv.Struct):
    ''' ⟦adef73778⟧ @0x735c8b9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Pointer,				#A07
            m001_p_=bv.Pointer.to(A08),			#A08
            m002_n_=-31,
            m003_n_=A04A,
        )

class A06(bv.Struct):
    ''' ⟦adef73778⟧ @0x735d5d1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-6,
            m001_p_=bv.Array(2, bv.Pointer.to(A11)),	#A11
            m002_p_=bv.Array(2, bv.Pointer.to(A10)),	#A10
            m003_p_=bv.Array(2, bv.Pointer.to(A09)),	#A09
        )

class A07(bv.Struct):
    ''' ⟦adef73778⟧ @0x735df59 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=bv.Array(2, -32),
            m001_p_=bv.Pointer.to(A12),			#A12
            m002_p_=bv.Pointer.to(A07),			#A07
            m003_p_=bv.Pointer.to(A07),			#A07
            m004_n_=-1,
        )


class A08(bv.Struct):
    ''' ⟦adef73778⟧ @0x735eab1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_a_=bv.Array(0x3f1, bv.Pointer.to(A07), vertical=True, elide=(0,)),	#A07
        )

class A09(bv.Struct):
    ''' ⟦adef73778⟧ @0x735f101 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_a_=bv.Pointer,				#A13
        )

class A10(bv.Struct):
    ''' ⟦adef73778⟧ @0x735f4e9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_a_=bv.Array(0x3f1, bv.Pointer.to(A14), vertical=True, elide=(0,)),	#A14
        )

class A11(bv.Struct):
    ''' ⟦adef73778⟧ @0x735fb39'''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_a_=bv.Array(5, bv.Pointer.to(A15), vertical=True, elide=(0,)),		#A15
        )

class A12(bv.Struct):
    ''' ⟦adef73778⟧ @0x7360189'''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Pointer.to(A16),			#A16
            m001_n_=-3,
            m002_n_=-32,
        )

class A14C(bv.Struct):
    ''' ⟦adef73778⟧ @0x73627d9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-31,
            m001_n_=-31,
        )

class A14B(bv.Struct):
    ''' ⟦adef73778⟧ @0x73627d9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-6,
            m001_n_=-31,
        )

class A14A(bv.Struct):
    ''' ⟦adef73778⟧ @0x7362699 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_s_=A14B,
            m001_s_=A14C,
        )

class A14(bv.Struct):
    ''' ⟦adef73778⟧ @0x73623c9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-1,
            m001_n_=A14A,
            m002_n_=bv.Pointer.to(A14),			#A14
        )

class A15C(bv.Struct):
    ''' ⟦adef73778⟧ @0x7363bd1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-32,
        )

class A15B(bv.Struct):
    ''' ⟦adef73778⟧ @0x7363881 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-32,
        )

class A15A(bv.Struct):
    ''' ⟦adef73778⟧ @00x7363741 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_s_=A15B,
            m001_s_=A15C,
        )

class A15(bv.Struct):
    ''' ⟦adef73778⟧ @0x7363601 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=A15A,
            m001_n_=bv.Pointer.to(A15),
        )

class A16C(bv.Struct):
    ''' ⟦adef73778⟧ @0x7366571 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-4,
            m001_n_=-31,
        )

class A16B(bv.Struct):
    ''' ⟦adef73778⟧ @0x7366431 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_s_=A16C,
            m001_p_=bv.Array(2, -32),		# A18
            m002_s_=cm.TimedProperty,
            m003_s_=cm.ObjRef,
            m004_n_=-32,
        )

class A16A(bv.Struct):
    ''' ⟦adef73778⟧ @0x73642c9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Array(2, -32),		# A17
            m001_p_=bv.Array(2, -32),		# A17
        )

class A16(bv.Struct):
    ''' ⟦adef73778⟧ @0x73642c9 '''

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
            m007_n_=bv.Array(2, bv.Pointer),		#A18
            m008_s_=A16A,
            m009_s_=A16B,
            m010_s_=A16B,
        )

class V1001T79(cm.ManagerSegment):
    ''' Ada Manager Segment - VPID 1001 - TAG 0x79 '''

    VPID = 1001
    TAG = 0x79
    TOPIC = "Ada"

    def spelunk_manager(self):
        head = AdaHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
