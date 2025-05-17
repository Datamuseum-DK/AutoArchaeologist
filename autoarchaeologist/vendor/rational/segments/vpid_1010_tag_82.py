#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1010 - TAG 0x82 - Configuration
   ====================================

   FE_HANDBOOK.PDF 187p: Note: […] The D2 mapping is:

	[…]
	CONFIGURATION	1010
	[…]

   Layout based descriptions in pure segment ⟦eca03ac96⟧
'''

from ....base import bitview as bv
from . import common as cm

class ConfigHead(bv.Struct):
    ''' ⟦eca03ac96⟧ @ 0x004a9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-31,
            m001_n_=bv.Array(2, -32),
            m002_p_=bv.Array(2, bv.Pointer),	# F05
            m003_p_=bv.Pointer.to(C04),			# F04
            m004_p_=bv.Array(2, bv.Pointer.to(C03)),	# F03
        )

class C03(bv.Struct):
    ''' ⟦eca03ac96⟧ @ 0x035c9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-1,
        )

class C04A(bv.Struct):
    ''' ⟦eca03ac96⟧ @ 0x3fa9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_p_=-2,
            m001_p_=bv.Pointer,				# C06
        )

class C04(bv.Struct):
    ''' ⟦eca03ac96⟧ @ 0x03989 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=bv.Pointer,				# C06
            m001_p_=bv.Pointer,				# C07
            m002_n_=-31,
            m003_n_=C04A,
        )

class V1010T82(cm.ManagerSegment):
    ''' Configuration Manager Segment - VPID 1010 - TAG 0x82 '''

    VPID = 1010
    TAG = 0x82
    TOPIC = "Configuration"

    def spelunk_manager(self):
        head = ConfigHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
