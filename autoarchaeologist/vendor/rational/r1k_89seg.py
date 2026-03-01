#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   R1000 "89" segments
   ===================

   Based on number of blocks in different snapshots, this is probably the "Ada"
   daemon's metadata.
'''

from ...generic import bitview as bv

class OurStruct(bv.Struct):
    def __init__(self, up, lo, **kwargs):

        # Set these early for diags, .done() may happen much later
        self.lo = lo
        self.name = self.__class__.__name__
        super().__init__(up, lo, name=self.name, **kwargs)

class SegHeap(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=True,
            used_=32,
            f1_=32,
            f2_=32,
            alloc_=32,
            **kwargs
        )

class Head(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=True,
            f0a_=32,
            f0b_=32,
            f0c_=32,
            f0d_=32,
            f1a_=32,
            f1b_=32,
            f1c_=32,
            f1d_=32,
            f2a_=32,
            f2b_=32,
            f2c_=32,
            f2d_=32,
            **kwargs
        )

class Hash(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            ptr_=32,
        )
        up.done.add(self.lo)
        if self.ptr:
            up.todo.append((Thing1, self.ptr))

class Thing0(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            a_=-32,
            b_=-32,
            ptr_=27,
        )
        up.done.add(self.lo)

class Thing1(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            seg_=24,
            bla_=24,
            ptr_=32,
        )
        up.done.add(self.lo)
        if self.ptr:
            up.todo.append((Thing1, self.ptr))

class Thing2(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            seg_=24,
            bla_=24,
            ptr_=32,
        )
        up.done.add(self.lo)

class Thing3(OurStruct):
    def __init__(self, up, lo, **kwargs):
        super().__init__(
            up,
            lo,
            vertical=False,
            bla_=205,
            ptr96_=32,
            ptr97_=32,
            ptr98_=32,
            ptr99_=32,
        )
        up.done.add(self.lo)
        if self.ptr96:
            up.todo.append((Thing3, self.ptr96))
        if self.ptr97:
            up.todo.append((Thing3, self.ptr97))
        if self.ptr98:
            up.todo.append((Thing3, self.ptr98))
        if self.ptr99:
            up.todo.append((Thing3, self.ptr99))
        # self.dot(up.fdot)

    def dot(self, file):
        if self.ptr96:
            file.write("A%06x -> A%06x [color=red]\n" % (self.lo, self.ptr96))
        if self.ptr97:
            file.write("A%06x -> A%06x [color=green]\n" % (self.lo, self.ptr97))
        if self.ptr98:
            file.write("A%06x -> A%06x [color=blue]\n" % (self.lo, self.ptr98))
        if self.ptr99:
            file.write("A%06x -> A%06x\n" % (self.lo, self.ptr99))

class R1kSeg89(bv.BitView):
    ''' ... '''
    def __init__(self, this):
        print("P0", this)
        if not hasattr(this, "r1ksegment"):
            return
        print("P1", this, this.r1ksegment.tag)
        if this.r1ksegment.tag != 0x89:
            return
        super().__init__(this)
        self.heap = SegHeap(self, 0).insert()
        self.hi = self.heap.used
        self.done = set()
        self.todo = []

        #self.fdot = open("/tmp/_.dot", "w")
        #self.fdot.write("digraph {\n")

        self.head = Head(self, 0x80).insert()

        i = Thing0(self, self.head.f2a).insert()

        # Hash table indexed by (seg# % 10007)
        # for instance 0xf641e % 10007 -> 7959
        # 0x2bc + 7959 * 32 = 0x3e59c, and
        #   0x3e59c…3e5bc Hash {ptr=0x000a890c}
        #   0xa890c…a895c Thing1 {seg=0x0f6413, bla=0x000000, ptr=0x00000000}
        a = i.ptr
        for j in range(10007):
            i = Hash(self, a).insert()
            a = i.hi

        if False:
            a = i.ptr
            while a < 0x4e580:
                i = OurStruct(self, i.hi, bla_=32).insert()
                if i.bla:
                    j = Thing1(self, i.bla).insert()
                a = i.hi

        i = Thing3(self, self.head.f2c).insert()

        i = OurStruct(self, self.head.f2d, f0_=32, f1_=32, f2_=32, f3_=1, f4_=32, f5_=32).insert()
        OurStruct(self, i.f2, x_=-35).insert()
        i = Thing3(self, i.hi).insert()

        while self.todo:
            i, j = self.todo.pop(0)
            if j not in self.done:
                i(self, j).insert()

        if False:
            # ⟦10300a03a⟧
            i = Thing1(self, 0x4e59c).insert()
            while i.hi < 0x80aec:
                i = Thing1(self, i.hi).insert()

            # Two Older trees ?
            i = Thing3(self, 0xb7a6e).insert()
            i = Thing3(self, 0xc1216).insert()

            while self.todo:
                i, j = self.todo.pop(0)
                if j not in self.done:
                    i(self, j).insert()

        self.render()
        #self.fdot.write("}\n")
        #self.fdot.close()
