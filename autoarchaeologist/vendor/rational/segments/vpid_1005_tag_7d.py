#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1005 - TAG 0x7d - Group
   ============================

   FE_HANDBOOK.PDF 187p: Note: […] The D2 mapping is:

	[…]
	GROUP		1005
	[…]

   Layout based descriptions in pure segment ⟦31d12fb28⟧
'''

from ....base import bitview as bv
from . import common as cm

class GroupHead(bv.Struct):
    ''' ⟦31d12fb28⟧ @ 0x31929 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=bv.Array(2, bv.Pointer),	#5
            m003_p_=bv.Pointer.to(G04),
            m004_p_=bv.Array(2, bv.Pointer.to(G03)),
        )

class G03A(bv.Struct):
    ''' ⟦31d12fb28⟧ @ 0x34b89 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_b_=-1024, # Should be array(1) but this is more compact.
            m001_n_=-10,
        )

class G03(bv.Struct):
    ''' ⟦31d12fb28⟧ @ 0x34a49 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_s_=G03A,
        )

class G04A(bv.Struct):
    ''' ⟦31d12fb28⟧ @ 0x35bf1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_c_=-2,
            m001_b_=bv.Pointer, # 6
        )

class G04(bv.Struct):
    ''' ⟦31d12fb28⟧ @ 0x355d1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            sh_000_n_=bv.Pointer.to(G06),
            sh_001_p_=bv.Pointer.to(G07),
            sh_002_n_=-31,
            sh_003_n_=G04A,
        )

class G06(bv.Struct):
    ''' ⟦31d12fb28⟧ @ 0x362e9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=bv.Array(2, -32),
            m001_p_=bv.Pointer.to(G08),
            m002_p_=bv.Pointer.to(G06),
            m003_p_=bv.Pointer.to(G06),
            m004_n_=-1,
        )


class G07(bv.Struct):
    ''' ⟦31d12fb28⟧ @ 0x36e41 '''

    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            hash_=bv.Array(101, bv.Pointer.to(G06), vertical=True),
            **kwargs,
        )


class G08(bv.Struct):
    ''' ⟦31d12fb28⟧ @ 0x37491 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g01_000_p_=bv.Pointer.to(G09),
            g01_001_n_=-3,
            g01_002_n_=-32,
        )

class G09(bv.Struct):
    ''' ⟦31d12fb28⟧ @ 0x37c19 '''
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_p_=cm.TimedProperty,
            m001_p_=cm.TimedProperty,
            m002_p_=cm.TimedProperty,
            m003_p_=cm.TimedProperty,
            m004_s_=cm.ObjRef,
            m005_s_=cm.ObjRef,
            m006_s_=-32,
            m007_s_=-32,
            m008_s_=-10,
            m009_s_=-10,
        )

class V1005T7D(cm.ManagerSegment):
    ''' Group Manager Segment - VPID 1005 - TAG 0x7d '''

    VPID = 1005
    TAG = 0x7d
    TOPIC = "Group"

    def spelunk_manager(self):

        head = GroupHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()

        # Accoring to the ⟦31d12fb28⟧ group.pure description
        # The BTree pointer is not part of GroupHead{}
        #bv.Pointer(self, self.head.hi, target=cm.BTree).insert()
