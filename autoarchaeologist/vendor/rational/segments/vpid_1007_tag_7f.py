#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1007 - TAG 0x7f - Tape
   ===========================

   FE_HANDBOOK.PDF 187p: Note: […] The D2 mapping is:

	[…]
	TAPE		1007
	[…]

   Layout based descriptions in pure segment ⟦f60d883ea⟧
'''

from ....base import bitview as bv
from . import common as cm

class TapeHead(bv.Struct):
    ''' ⟦f60d883ea⟧ @ 0x1e21 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=bv.Array(2, bv.Pointer),	# T04
            # m003_n_ zero length discrete
            m004_p_=bv.Array(2, bv.Pointer.to(T03)),
        )

class T03A(bv.Struct):
    ''' ⟦f60d883ea⟧ @ 0x5549 '''
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=False,
            t04_000_d_=-2,
            t04_001_p_=bv.Pointer.to(T05),
        )

class T03(bv.Struct):
    ''' ⟦f60d883ea⟧ @ 0x4f29 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_c_=bv.Pointer.to(T05),
            m001_b_=bv.Pointer.to(T06),
            m002_b_=-31,
            m003_b_=T03A,
        )

class T05(bv.Struct):
    ''' ⟦f60d883ea⟧ @ 0x5c41 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            t01_000_c_=bv.Array(2, -32),
            t01_002_c_=bv.Pointer.to(T07),
            t01_003_c_=bv.Pointer.to(T05),
            t01_004_c_=bv.Pointer.to(T05),
            t01_005_c_=-1,
        )


class T06(bv.Struct):
    ''' ⟦f60d883ea⟧ @ 0x4f29 '''
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_a_=bv.Array(4, bv.Pointer.to(T05), vertical=True),
        )

class T07B(bv.Struct):
    ''' ⟦f60d883ea⟧ @ 0x6f29 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            # m000_n_ zero length discrete
            m001_s_=cm.ObjRef,
            m002_s_=-32
       )

class T07A(bv.Struct):
    ''' ⟦f60d883ea⟧ @ 0x6f29 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-2,
            m001_s_=T07B,
            m002_s_=T07B,
            m003_s_=cm.TimedProperty,
            m004_s_=cm.TimedProperty,
            m005_s_=cm.TimedProperty,
       )

class T07(bv.Struct):
    ''' ⟦f60d883ea⟧ @ 0x6de9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_s_=T07A,
            m001_c_=-3,
            m002_c_=-32,
            more=True
        )
        self.done()

class V1007T7F(cm.ManagerSegment):
    ''' Tape Manager Segment - VPID 1007 - TAG 0x7f '''

    VPID = 1007
    TAG = 0x7F
    TOPIC = "Tape"

    def spelunk_manager(self):
        head = TapeHead(self, self.seg_head.hi).insert()
        y = bv.Pointer(self, head.hi, target=cm.BTree).insert()
        print("Y", hex(head.hi), y)
