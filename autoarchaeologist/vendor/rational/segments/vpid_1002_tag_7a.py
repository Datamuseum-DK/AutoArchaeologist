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
from .common import ManagerSegment

class LinkHead(bv.Struct):
    ''' ⟦f86217f0c⟧ @ 0x23cc841 '''
 
    def __init__(self, bvtree, lo):
 
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_=bv.Array(2, bv.Pointer),
            #m003 zero length discrete
            m004_=bv.Array(2, bv.Pointer.to(T04)),
        )


class V1002T7A(ManagerSegment):
    ''' Terminal Manager Segment - VPID 1002 - TAG 0x7a '''

    VPID = 1002
    TAG = 0x7a
    TOPIC = "DDB"

    def spelunk_manager(self):
        bv.Array(12, -32, vertical=True)(self, self.seg_head.hi).insert()
        #head = LinkHead(self, self.seg_head.hi).insert()
        #bv.Pointer(self, head.hi, target=cm.BTree).insert()

