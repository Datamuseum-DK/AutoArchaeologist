#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1014 - TAG 0x86 - Pipe
   ===========================

   FE_HANDBOOK.PDF 187p: Note: […] The D2 mapping is:

	[…]
	PIPE		1014
	[…]

   Layout based descriptions in pure segment ⟦d4fc19176⟧
'''

from ....base import bitview as bv
from . import common as cm

class PipeHead(bv.Struct):
    ''' ⟦d4fc19176⟧ @ 0x04a9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=bv.Array(2, bv.Pointer),	# P05
            m003_n_=bv.Pointer.to(P04),
            m004_p_=bv.Array(2, bv.Pointer.to(P03)),
        )

class P03(bv.Struct):
    ''' ⟦d4fc19176⟧ @ 0x35c9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            # pure-spec'ed as zero width, but one bit allocated.
            m000_c_=-1
        )

class P04A(bv.Struct):
    ''' ⟦d4fc19176⟧ @ 0x3fb9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_p_=-2,
            m001_p_=bv.Pointer,
        )

class P04(bv.Struct):
    ''' ⟦d4fc19176⟧ @ 0x3999 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_p_=bv.Pointer,
            m001_p_=bv.Pointer,
            m002_n_=-31,
            m003_n_=P04A,
        )

class V1014T86(cm.ManagerSegment):
    ''' Pipe Manager Segment - VPID 1014 - TAG 0x86 '''

    VPID = 1014
    TAG = 0x86
    TOPIC = "Pipe"

    def spelunk_manager(self):
        head = PipeHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
