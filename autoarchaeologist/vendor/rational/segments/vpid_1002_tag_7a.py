#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1002 - TAG 0x7a - DDB
   ==========================

   FE_HANDBOOK.PDF 187p: Note: […] The D2 mapping is:

	[…]
	DDB		1002
	[…]

   Layout based descriptions in pure segment ⟦f86217f0c⟧
'''

from ....base import bitview as bv
from . import common as cm

class DdbHeadA(bv.Struct):
    ''' ⟦f86217f0c⟧ @ 0x23cce49 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Array(2, bv.Pointer.to(D04)),		# D04
            m001_p_=bv.Pointer,				# D03
        )

class DdbHead(bv.Struct):
    ''' ⟦f86217f0c⟧ @ 0x23cc841 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=bv.Array(2, bv.Pointer),		# D06
            m003_s_=DdbHeadA,
            m004_p_=bv.Array(2, bv.Pointer),		# D05
        )


class D04A(bv.Struct):
    ''' ⟦f86217f0c⟧ @ 0x23d1e21 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-2,
            m001_p_=bv.Pointer,				# D08
        )

class D04(bv.Struct):
    ''' ⟦f86217f0c⟧ @ 0x23d1801 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=bv.Pointer.to(D08),				# D08
            m001_p_=bv.Pointer.to(D09),				# D09
            m002_n_=-31,
            m003_s_=D04A,
        )

class D07A(bv.Struct):
    ''' ⟦f86217f0c⟧ @ 0x23d2b39 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-2,
            m001_p_=bv.Pointer,					# D10
        )

class D07(bv.Struct):
    ''' ⟦f86217f0c⟧ @ 0x23d2519 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_p_=bv.Pointer.to(D10),				# D10
            m001_p_=bv.Pointer.to(D11),				# D11
            m002_n_=-31,
            m003_s_=D07A,
        )

class D08(bv.Struct):
    ''' ⟦f86217f0c⟧ @ 0x23d3231 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=bv.Array(2, -32),				# Object.kind
            m001_p_=bv.Pointer.to(D12),
            m002_p_=bv.Pointer.to(D08),
            m003_p_=bv.Pointer.to(D08),
            m004_n_=-1,
        )

class D09(bv.Struct):
    ''' ⟦f86217f0c⟧ @ 0x23d3d89 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_a_=bv.Array(0x2717, bv.Pointer.to(D08), vertical=True, elide=(0,)),
        )

class D10(bv.Struct):
    ''' ⟦f86217f0c⟧ @ 0x23d43d9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-31,
            #m001_s_ # Empty record
            m002_p_=bv.Pointer.to(D10),
            m003_p_=bv.Pointer.to(D10),
            m004_p_=-1,
        )

class D11(bv.Struct):
    ''' ⟦f86217f0c⟧ @ 0x23d4f09 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=bv.Array(0x71, bv.Pointer.to(D10), vertical=True, elide=(0,)),
        )

class D12A(bv.Struct):
    ''' ⟦f86217f0c⟧ @ 0x23d5559 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_p_=bv.Array(7, bv.Pointer.to(D07)),		# D07
            m001_p_=bv.Pointer,					# D03
        )

class D12(bv.Struct):
    ''' ⟦f86217f0c⟧ @ 0x23d5559 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_s_=D12A,
            m001_n_=-3,
            m002_n_=-32,
        )

class V1002T7A(cm.ManagerSegment):
    ''' DDB Manager Segment - VPID 1002 - TAG 0x7a '''

    VPID = 1002
    TAG = 0x7a
    TOPIC = "DDB"

    def spelunk_manager(self):
        head = DdbHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
