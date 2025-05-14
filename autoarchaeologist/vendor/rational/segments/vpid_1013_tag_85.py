#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1013 - TAG 0x85
   =========================================

   FE_HANDBOOK.PDF 187p

    Note: […] The D2 mapping is:

        […]
        NULL      1013
        […]

   Layout based descriptions in pure segment ⟦ebffc519d⟧
'''

from ....base import bitview as bv
from . import common as cm

class NullHead(bv.Struct):
    ''' ⟦ebffc519d⟧ @ 0x0a91 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=bv.Array(2, bv.Pointer),	# T04
            # m003_n_=0 zero length discrete
            m004_p_=bv.Array(2, bv.Pointer.to(N03)),
        )

class N03A(bv.Struct):
    ''' ⟦ebffc519d⟧ @ 0x41b9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=False,
            m000_d_=-2,
            m001_p_=bv.Pointer.to(N05),
        )

class N03(bv.Struct):
    ''' ⟦ebffc519d⟧ @ 0x3b99 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_c_=bv.Pointer.to(N05),
            m001_b_=bv.Pointer, # .to(N06),
            m002_b_=-31,
            m003_b_=N03A,
        )

class N05(bv.Struct):
    ''' ⟦ebffc519d⟧ @ 0x48b1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_=bv.Array(2, -32),
            m001_=bv.Pointer.to(N07),
            m002_=bv.Pointer.to(N05),
            m003_=bv.Pointer.to(N05),
            m004_=-1,
        )

class N07B(bv.Struct):
    ''' ⟦ebffc519d⟧ @ 0x5e69 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-1,
            m001_s_=cm.ObjRef,
            m002_s_=-32
       )

class N07A(bv.Struct):
    ''' ⟦ebffc519d⟧ @ 0x5b99 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-1,
            m001_s_=N07B,
            m002_s_=N07B,
            m003_s_=cm.TimedProperty,
            m004_s_=cm.TimedProperty,
            m005_s_=cm.TimedProperty,
       )

class N07(bv.Struct):
    ''' ⟦ebffc519d⟧ @ 0x5a59 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_=N07A,
            m001_=-3,
            m002_=-32,
        )


class V1013T85(cm.ManagerSegment):
    ''' Null Manager Segment - VPID 1013 - TAG 0x85 '''

    VPID = 1013
    TAG = 0x85
    TOPIC = "Null_Device"

    def spelunk_manager(self):
        head = NullHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
