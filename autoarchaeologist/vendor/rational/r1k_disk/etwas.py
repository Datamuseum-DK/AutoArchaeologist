#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Etwas
   =====
'''

from ....base import bitview as bv

from .defs import SECTBITS, AdaArray
from .object import ObjSector

ADA_ARRAY_1 = bin((1<<32)|0x40)[3:]
ADA_ARRAY_3 = bin((1<<32)|1)[3:]

class Etwas(ObjSector):
    ''' Unknown sector content '''
    def __init__(self, ovtree, lba, span=0, **kwargs):
        super().__init__(
            ovtree,
            lba,
            vertical=True,
            more=True,
            **kwargs,
        )
        i = self.tree.bits[self.hi:SECTBITS]
        ptr = 0
        while True:
            j = i.find(ADA_ARRAY_1, ptr)
            if j == -1:
                break
            k = i.find(ADA_ARRAY_3, ptr)
            if j + 64 != k:
                ptr += 1
                continue
            #a0 = int(self.tree.bits[self.hi + j : self.hi + j + 32], 2)
            aa1 = int(self.tree.bits[self.hi + j + 32: self.hi + j + 64], 2)
            #a2 = int(self.tree.bits[self.hi + j + 64: self.hi + j + 96], 2)
            aa3 = int(self.tree.bits[self.hi + j + 96: self.hi + j + 128], 2)
            if aa3 == 0:
                ptr += 1
                continue
            cntwidth = len(bin(aa3)[2:])
            assert (aa1-64) % aa3 == 0
            width = (aa1-64) // aa3
            self.add_field("q0", j - cntwidth)
            self.add_field("cnt", -cntwidth)
            self.add_field("aa", AdaArray)
            self.add_field("ary", bv.Array(self.cnt.val, -width, vertical=True))
            self.done()
            return

        if span == 0:
            span = 128
        if (SECTBITS - self.hi)//span > 0:
            self.add_field(
                "q98",
                bv.Array((SECTBITS - self.hi)//span, -span, vertical=True)
            )
        self.add_field("q99", SECTBITS - self.hi)
        self.done()

##################################################################################

class Etwas58a(Etwas):
    ''' ... '''

class Etwas5e7(Etwas):
    ''' ... '''

class Etwas644(Etwas):
    ''' ... '''

class Etwas1331(Etwas):
    ''' ... '''

##################################################################################

class Etwas6a1ChildEntry(bv.Struct):
    ''' Unknown sector content '''
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            f0_=-21,	# As in Etwas6a1Entry
            f1_=-1,	# Speculative
            f2_=-10,	# Looks like a vpid ?
            f3_=-2,	# Speculative
            f4_=-32,	# Speculative
            f5_=-32,	# Speculative
            f6_=-64,	# Speculative, first two bytes look like a range?
            f7_=-64,	# Speculative
            f8_=-8,	# Speculative
        )

class Etwas6a1Child(ObjSector):
    ''' Unknown sector content '''
    def __init__(self, ovtree, lba):
        super().__init__(
            ovtree,
            lba,
            duplicated=True,
            vertical=True,
            more=True,
            f0_=-17,
            cnt_=-6,
            aa_=AdaArray,
        )
        self.add_field(
            "ary",
            bv.Array(self.cnt.val, Etwas6a1ChildEntry, vertical=True)
        )
        self.done()

class Etwas6a1Entry(bv.Struct):
    ''' Unknown sector content '''
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            f0_=-21,
            lba_=-24,
        )


class Etwas6a1(ObjSector):
    ''' Unknown sector content '''
    def __init__(self, ovtree, lba):
        super().__init__(
            ovtree,
            lba,
            duplicated=True,
            vertical=True,
            more=True,
            f0_=-19,
            cnt_=-8,
            aa_=AdaArray,
        )
        self.add_field(
            "ary",
            bv.Array(self.cnt.val, Etwas6a1Entry, vertical=True)
        )
        self.done()
        for i in self.ary:
            Etwas6a1Child(ovtree, i.lba.val).insert()
