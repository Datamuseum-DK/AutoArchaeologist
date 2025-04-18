#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

# NB: This docstring is also used as interpretation

'''
   EEDB text files
   ===============

'''

from ....base import bitview as bv
from .common import SegHeap

class ETH(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            eth_0_=-33,
            eth_1_=-32,
        )

class EEDBText(bv.BitView):

    def __init__(self, this):
        if not this.has_note("tag_65"):
            return
        if len(this) > 1<<20:
            return
        super().__init__(bits = this.bits())
        self.this = this
        self.type_case = this.type_case

        self.seg_heap = SegHeap(self, 0).insert()
        hdr = ETH(self, self.seg_heap.hi).insert()
        if hdr.eth_1.val != 0x80:
            return
        lo = hdr.hi
        hi = len(self.seg_heap) + self.seg_heap.first_free.val
        if hi > 8 * len(self.this):
            hi = 8 * len(self.this)
        hi -= (hi - lo) & 7
        if hi <= lo:
            return
        l = []
        for adr in range(lo, hi, 8):
            g = int(self.bits[adr:adr+8], 2)
            slug = self.type_case[g]
            if slug is None:
                return
            l.append(slug.long)
        print(self.__class__.__name__, self.this, self, len(l))
        self.this.add_type("EEDBtext")
        with self.this.add_utf8_interpretation("EEDB Text") as file:
            file.write("".join(l))
