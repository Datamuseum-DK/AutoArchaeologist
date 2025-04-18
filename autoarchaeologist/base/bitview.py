#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Operating on artifacts in bit-alignment
   ---------------------------------------
'''

from . import bintree
from . import datastruct
from . import octetview as ov

class_cache = {}

class String():
    ''' ... '''

class OvBits(ov.Octets):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bv = BitView(
            bits = self.this.bits(lo = self.lo << 3, hi = self.hi << 3),
            type_case = self.this.type_case,
        )

    def render(self):
        l = list(x for x in self.bv.render())
        if len(l) == 1:
            yield "BitView = { " + l[0] + " }"
            return
        yield "BitView = {"
        for i in l:
            yield "    " + i
        yield "}"

class Bits(bintree.BinTreeLeaf):

    rendered = None

    def __init__(self, tree, lo, width=None, hi=None, name=None):
        if hi is None:
            assert width is not None
            hi = lo + width
        assert hi > lo
        self.tree = tree
        super().__init__(lo, hi)

    def __len__(self):
        return self.hi - self.lo

    def __getitem__(self, idx):
        return self.this[self.lo + idx]

    def __iter__(self):
        yield from self.this[self.lo:self.hi]

    def __str__(self):
        try:
            return " ".join(self.render())
        except:
            return str(super())

    def bits(self):
        ''' return contents '''
        return self.tree.bits[self.lo:self.hi]

    def insert(self):
        ''' Insert in tree (NB: Optional!) '''
        self.tree.insert(self)
        return self

    def render(self):
        ''' Render as bits '''
        if self.rendered is None:
            yield self.tree.bits[self.lo:self.hi]
        else:
            yield self.rendered

class BitView(bintree.BinTree):

    def __init__(self, octets=None, bits=None, type_case=None):
        self.octets = octets
        self.bits = bits
        self.type_case = type_case
        assert self.bits
        super().__init__(
            lo=0,
            hi=len(self.bits),
            leaf=Bits
        )

    def prefix(self, lo, hi):
        return "*0x" + self.adrfmt % lo + "…" + self.adrfmt % hi

class Opaque(Bits):

    def render(self):
        yield self.__class__.__name__

class Number(Bits):

    fmt = None

    fmts = ["0x%%0%dx" % ((x + 3) // 4) for x in range(129)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.val = int(self.bits(), 2)

    def render(self):
        if self.fmt:
            yield self.fmt % self.val
        elif len(self) < len(self.fmts):
            yield self.fmts[len(self)] % self.val
        else:
            fmt = "0x%%0%dx" % ((len(self) + 3) // 4)
            yield fmt % self.val

class Struct(datastruct.Struct, Bits):

    def __init__(self, *args, **kwargs):
        datastruct.Struct.__init__(self, *args, **kwargs)

    def base_init(self, **kwargs):
        Bits.__init__(self, self.tree, self.lo, hi=self.hi, **kwargs)

    def number_field(self, offset, width):
        if width < 0:
            return Number(self.tree, offset, width=-width)
        return Bits(self.tree, offset, width=width)

def Array(count, what, **kwargs):
    return datastruct.Array(Struct, count, what, **kwargs)

def Text(width, glyph_width=8, rstrip = False):

    class Text_Class(Bits):
        ''' Fixed width text String (convenient for Struct) '''

        WIDTH = width
        RSTRIP = rstrip
        GLYPH_WIDTH = glyph_width
        def __init__(self, *args, type_case=None, **kwargs):
            kwargs["width"] = self.WIDTH * self.GLYPH_WIDTH
            super().__init__(*args, **kwargs)
            if type_case is None:
                type_case = self.tree.type_case
            self.txt = type_case.decode(self.iter_glyphs())
            if self.RSTRIP:
                self.txt = self.txt.rstrip()

        def iter_glyphs(self):
            i = self.bits()
            for a in range(0, len(self), self.GLYPH_WIDTH):
                yield int(i[a:a+self.GLYPH_WIDTH], 2)

        def render(self):
            yield "»" + self.txt + "«"

    return Text_Class

class Pointer_Class(Bits):

    TARGET = None
    WIDTH = None
    ELIDE = None

    def __init__(self, bvtree, lo, width=None):
        if width is None:
            width = self.WIDTH
        if width is None:
            width = bvtree.POINTER_WIDTH
        super().__init__(bvtree, lo, width=width)
        self.val = int(self.bits(), 2)
        self.cached_dst = None
        if self.TARGET is not None:
            bvtree.points_to(self.val, self.TARGET)

    def dst(self):
        if self.cached_dst is None:
            i = list(self.tree.find(self.val, self.val+1))
            if len(i) == 0:
                return None
            if len(i) > 1:
                dst = set()
                for j in i:
                    t = j.__class__.__name__
                    if j.lo < self.val:
                        t += "+0x%x" % (self.val - j.lo)
                    dst.add(t)
                print(
                    self.tree.this,
                    "Pointer at",
                    hex(self.lo),
                    "points to",
                    hex(self.val),
                    "with",
                    len(i),
                    "destinations of class",
                    ",".join(list(dst)),
                )
                return None
            dst = i[0]
            if dst.lo != self.val:
                print(
                    "Pointer at",
                    hex(self.lo),
                    "Points to",
                    hex(self.val),
                    "which is",
                    hex(self.val - dst.lo),
                    "into object at",
                    hex(dst.lo),
                    "which is class",
                    dst.__class__.__name__,
                )
                return None
            self.cached_dst = dst
        return self.cached_dst

    def render(self):
        if self.ELIDE and self.val in self.ELIDE:
            return
        if not self.val:
            yield "∅"
            return
        i = self.dst()
        if i is None:
            yield "0x" + self.tree.adrfmt % self.val + "→NOTHING"
            return
        yield "0x" + self.tree.adrfmt % self.val + "→" + i.__class__.__name__

    def dot_edges(self, dot, src=None):
        if not self.val:
            return
        if src is None:
            src = self
        dot.add_edge(src, self.val)

def make_pointer(cls=None, width=None, elide=None):

    class ClsPointer(Pointer_Class):
        TARGET = cls
        WIDTH = width
        ELIDE = elide

    return ClsPointer

def Pointer(cls=None, width=None, elide=None):

    key = str(("Pointer", cls, width, elide))
    ptr = class_cache.get(key)
    if not ptr:
        ptr = make_pointer(cls, width, elide)
        class_cache[key] = ptr
    return ptr

def make_constant(width=32, value=0):
    class ClsConstant(Bits):
        def __init__(self, bvtree, lo, width=width, value=value):
            super().__init__(bvtree, lo, width=width)
            self.val = int(self.bits(), 2)
            if self.val != value:
                print(bvtree.this,
                    "WARNING: bv.Constant at 0x%x is 0x%x instead of 0x%x" % (
                        self.lo, self.val, value
                    )
                )

        def render(self):
            yield "CONST(0x%x)" % self.val

    return ClsConstant

def Constant(width=32, value=0):
    key = str(("Constant", width, value))
    ptr = class_cache.get(key)
    if not ptr:
        ptr = make_constant(width, value)
        class_cache[key] = ptr
    return ptr
