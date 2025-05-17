#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   VPID 1008 - TAG 0x80 - Terminal
   ===============================

   FE_HANDBOOK.PDF 187p: Note: […] The D2 mapping is:

	[…]
	TERMINAL	1008
	[…]

   Layout based descriptions in pure segment ⟦c05ddcbe7⟧
'''

from ....base import bitview as bv
from . import common as cm

class TerminalHead(bv.Struct):
    ''' ⟦c05ddcbe7⟧ @ 0x3dbb1 '''

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

class T04A(bv.Struct):
    ''' ⟦c05ddcbe7⟧ @ 0x412d9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            t04_000_c_=-2,
            t04_001_b_=bv.Pointer,
        )

class T04(bv.Struct):
    ''' ⟦c05ddcbe7⟧ @ 0x419d1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=bv.Pointer,
            m001_p_=bv.Pointer.to(T06),
            m002_n_=-31,
            m003_s_=T04A,
        )

class T05(bv.Struct):
    ''' ⟦c05ddcbe7⟧ @ 0x419d1 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=bv.Array(2, -32),
            m001_p_=bv.Pointer.to(T07),
            m002_p_=bv.Pointer,
            m003_p_=bv.Pointer,
            m004_n_=-1,
        )


class T06(bv.Struct):
    ''' ⟦c05ddcbe7⟧ @ 0x42529 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=bv.Array(257, bv.Pointer.to(T05), vertical=True, elide=(0,)),
        )

class T07E(bv.Struct):
    ''' ⟦c05ddcbe7⟧ @ 0x48ac9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-1,
            m001_n_=-31,
            m002_n_=-31,
            m003_n_=cm.IndirectFieldRefComponent,

            # Not quite sure about the rest...

            x004_n_=-32,
            x005_n_=-32,
            x006_n_=bv.Array(0x14, -8),
        )

class T07D(bv.Struct):
    ''' ⟦c05ddcbe7⟧ @ 0x46401 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            m000_n_=-1,
            m001_n_=-31,
            m002_n_=-31,
            m003_n_=-32,
        )

class T07C(bv.Struct):
    ''' ⟦c05ddcbe7⟧ @ 0x430c9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-4,
            m001_n_=-1,
            m002_n_=-1,
            m003_n_=-1,
            m004_n_=-1,
            m005_n_=-1,
            m006_n_=-1,
            m007_n_=-4,
            m008_n_=-4,
            m009_n_=-2,
            m010_n_=-2,
            m011_n_=-2,
            m012_n_=-1,
            m013_n_=-8,
            m014_n_=-8,
            m015_s_=T07E,
            m016_n_=-31,
            m017_n_=-31,
        )

class T07B(bv.Struct):
    ''' ⟦c05ddcbe7⟧ @ 0x42f89 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_s_=T07C,
            m001_s_=T07D,
            m002_s_=-32,
        )

class T07A(bv.Struct):
    ''' ⟦c05ddcbe7⟧ @ 0x42cb9 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_n_=-9,
            m001_s_=T07B,
            m002_s_=T07B,
            m003_s_=cm.TimedProperty,
            m004_s_=cm.TimedProperty,
            m005_s_=cm.TimedProperty,
        )

class T07(bv.Struct):
    ''' ⟦c05ddcbe7⟧ @ 0x42b79 '''

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            m000_=T07A,
            m001_=-3,
            m002_=-32,
        )


class V1008T80(cm.ManagerSegment):
    ''' Terminal Manager Segment - VPID 1008 - TAG 0x80 '''

    VPID = 1008
    TAG = 0x80
    TOPIC = "Terminal"

    def spelunk_manager(self):
        head = TerminalHead(self, self.seg_head.hi).insert()
        bv.Pointer(self, head.hi, target=cm.BTree).insert()
