#!/usr/bin/env python3

'''
   Operating on artifacts in bit-alignment
   ---------------------------------------
'''

from ..base import bintree
from ..base import octetview as ov

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

    def __init__(self, tree, lo, width=None, hi=None, name=None):
        if hi is None:
            assert width is not None
            hi = lo + width
        assert hi > lo
        self.tree = tree
        if name is None:
            name = self.__class__.__name__
        self.bv_name = name
        self.bt_name = name
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
        ''' Render hexdumped + text-column '''
        yield self.tree.bits[self.lo:self.hi]

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
        yield "Opaque"

class Number(Bits):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.val = int(self.bits(), 2)
        self.fmt = "0x%%0%dx" % ((len(self) + 3) // 4)

    def render(self):
        yield self.fmt % self.val

class Struct(bintree.Struct, Bits):

    def __init__(self, *args, **kwargs):
        bintree.Struct.__init__(self, *args, **kwargs)

    def base_init(self, **kwargs):
        Bits.__init__(self, self.tree, self.lo, hi=self.hi, **kwargs)

    def number_field(self, offset, width):
        if width < 0:
            return Number(self.tree, offset, width=-width)
        return Bits(self.tree, offset, width=width)

def Array(count, what, **kwargs):
    return bintree.Array(Struct, count, what, **kwargs)

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

