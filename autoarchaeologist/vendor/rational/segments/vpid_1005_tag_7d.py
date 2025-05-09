#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1005 - TAG 0x7d
   =========================================

   FE_HANDBOOK.PDf 187p

    Note: […] The D2 mapping is:

        […]
        GROUP           1005
        […]

'''

from ....base import bitview as bv
from . import common as cm

class G00(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g00_000_n_=bv.Array(2, -32),
            g00_002_p_=bv.Pointer(G01),
            g00_003_p_=bv.Pointer(G01),
            g00_004_p_=bv.Pointer(G00),
            g00_005_n_=-1,
        )

class G01(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g01_000_p_=bv.Pointer(G02),
            g01_001_n_=-3,
            g01_002_n_=-32,
        )

class G02(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g02_000_p_=cm.TimedProperty,
            g02_010_p_=cm.TimedProperty,
            g02_020_p_=cm.TimedProperty,
            g02_030_p_=cm.TimedProperty,
            # The next three fields are doubled in the description
            # we cheat and use an Array(2).
            g02_obj_=bv.Array(2, cm.ObjRef),
            g02_valid_=bv.Array(2, -32),
            g02_nbr_n_=bv.Array(2, -10),
            vertical=True,
        )

class GroupHead(bv.Struct):
    '''
       Based on ⟦31d12fb28⟧ group.pure description

       NB:
       The MgrHead is not a separate RecordComponent

       NB:
       We assume that a 0x40 wide HeapAccessComponent means
       that there are two pointers, but this is unconfirmed.
    '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            mgr_=cm.MgrHead,
            hd_sh_=bv.Pointer(GroupSubHead),
            hd_000_n_=bv.Array(2, bv.Pointer(GroupBitMap)),
            #hd_001_p_=bv.Pointer(GroupBitMap),
            #hd_002_n_=bv.Array(2, bv.Pointer(cm.BTree)),
        )

class G03(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            g03_000_c_=-2,
            g03_001_b_=bv.Pointer(),
        )

class GroupSubHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            sh_001_n_=bv.Pointer(),
            sh_002_p_=bv.Pointer(GroupHash),
            sh_003_n_=-31,
            sh_004_n_=G03,
        )

class GroupBitMap(bv.Struct):
   
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            gb_001_b_=-1024, # Should be array(1) but this is more compact.
            gb_002_b_=-10,
        )

class GroupHash(bv.Struct):
    def __init__(self, bvtree, lo, **kwargs):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            hash_=bv.Array(101, bv.Pointer(G00), vertical=True),
            **kwargs,
        )

class V1005T7D(cm.ManagerSegment):

    VPID = 1005
    TAG = 0x7d
    TOPIC = "Group"

    def spelunk_manager(self):

        self.head = GroupHead(self, self.seg_head.hi).insert()

        # Accoring to the ⟦31d12fb28⟧ group.pure description
        # The BTree pointer is not part of GroupHead{}
        bv.Pointer(cm.BTree)(self, self.head.hi).insert()
