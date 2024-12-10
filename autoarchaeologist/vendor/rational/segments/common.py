#!/usr/bin/env python3

'''
   Segments - common stuff
   =========================================
'''

from ....base import bitview as bv
from ....base import dot_graph

class Unallocated(bv.Opaque):
    ''' ... '''

class SegHeap(bv.Struct):
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            first_free_=-32,
            max_=-32,
            zero_=-32,
            allocated_=-32,
        )

        unused = self.hi + self.first_free.val - 1
        if unused < bvtree.hi:
            self.unalloc = Unallocated(
                bvtree,
                lo = unused,
                hi = self.allocated.val + 1,
            )
            self.unalloc.insert()

class StdHead(bv.Struct):

    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            hd_000_n_=-32,
            hd_001_n_=-32,
            hd_002_n_=-32,
            hd_003_n_=-32,
            hd_004_n_=-32,
            hd_005_n_=-32,
            hd_006_n_=-32,
            hd_007_p_=bv.Pointer(),
            hd_008_n_=-32,
            hd_009_p_=bv.Pointer(),
            hd_010_n_=-32,
            hd_011_p_=bv.Pointer(),
            hd_012_n_=1,
            hd_013_n_=-32,
            hd_014_n_=-32,
        )

class PointerArray(bv.Struct):

    def __init__(self, bvtree, lo, cls=bv.Pointer_Class, dimension=None):
        super().__init__(
            bvtree,
            lo,
            vertical=True,
            more = True,
        )
        if dimension is None:
            self.add_field("pa_min", -32)
            self.add_field("pa_max", -32)
            assert self.pa_min.val == 0
            dimension = self.pa_max.val
        self.add_field("array", bv.Array(dimension, cls, vertical=True))
        self.done()

    def __iter__(self):
        yield from self.array

class StringArray(bv.Struct):
    ''' String on Array format'''
    def __init__(self, bvtree, lo):
        super().__init__(
            bvtree,
            lo,
            sa_min_=-32,
            sa_max_=-32,
            more = True,
        )
        assert self.sa_min.val == 1
        self.add_field("text", bv.Text(self.sa_max.val))
        self.txt = self.text.txt
        self.done()

    def render(self):
        yield '»' + self.txt + '«'

class Segment(bv.BitView):

    TAG = None
    VPID = None
    POINTER_WIDTH = 32

    def __init__(self, this):
        if self.TAG is not None and not this.has_note("tag_%02x" % self.TAG):
            return
        if self.VPID is not None and not this.has_note("vpid_%04d" % self.VPID):
            return
        print(this, "SEG", self.VPID, "%x" % self.TAG)
        super().__init__(bits = this.bits())
        self.this = this
        self.type_case = this.type_case
        print(self.__class__.__name__, this, self)
        self.spelunk()
        if True:
            for lo, hi in self.gaps():
                print(this, "GAP", hex(lo), hex(hi), hex(hi - lo))
        dot_graph.add_interpretation(this, self)
        self.add_interpretation()

    def add_interpretation(self, title="BitView", more=False, **kwargs):
        ''' Render via UTF-8 file '''
        with self.this.add_utf8_interpretation(title, more=more) as file:
            for line in self.render(default_width=128, **kwargs):
                file.write(line + '\n')
