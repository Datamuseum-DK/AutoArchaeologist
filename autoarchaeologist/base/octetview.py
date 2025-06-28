#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Toolkit for operating on artifacts on byte granularity
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


from itertools import zip_longest

from . import bintree
from . import datastruct

# Base leaf type

class Octets(bintree.BinTreeLeaf):
    ''' Base class, just some random octets '''

    def __init__(self, tree, lo, width=None, hi=None, maxlines=None, default_width=32):
        if hi is None:
            assert width is not None
            hi = lo + width
        assert hi > lo
        self.tree = tree
        self.this = tree.this
        self.maxlines = maxlines
        super().__init__(lo, hi)
        if width is None:
            width = len(self)
        self.width = width
        self.default_width = default_width

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

    def octets(self):
        ''' return contents '''

        return self.this[self.lo:self.hi]

    def iter_bytes(self):
        ''' Iterate bytes in specified order '''

        if self.this.byte_order is None:
            yield from self.octets()
            return

        def group(data, chunk):
            i = [iter(data)] * chunk
            return zip_longest(*i, fillvalue=0)

        for i in group(self.octets(), len(self.this.byte_order)):
            for j in self.this.byte_order:
                yield i[j]

    def insert(self):
        ''' Insert in tree (NB: You dont have to do this) '''
        self.tree.insert(self)
        return self

    def render(self):
        ''' Render hexdumped + text-column '''
        hd = self.this.hexdump(lo=self.lo, hi=self.hi, width=self.default_width)
        hd = list(hd)
        if self.maxlines is None:
            yield from hd
            return
        for _i,j in zip(range(self.maxlines), hd):
            yield j

# Bulk types

class FillRecord(Octets):
    ''' ... '''

    def __init__(self, tree, lo, hi):
        super().__init__(tree, lo=lo, hi=hi)

    def render(self):
        ''' ... '''
        yield "0x%02x" % self.this[self.lo] + "[0x%x]" % len(self)

class EmptyRecord(Octets):
    ''' ... '''

    def __init__(self, tree, lo, hi, width):
        super().__init__(tree, lo=lo, hi=hi)
        self.width = width

    def render(self):
        ''' ... '''
        yield from self.this.hexdump(self.lo, self.hi, width=self.width)

class Dump(Octets):
    ''' basic (hex)dump '''

    def render(self):
        ''' ... '''
        yield self.__class__.__name__ + " {"
        for i in self.this.hexdump(self.lo, self.hi):
            yield "  " + i
        yield "}"

class This(Octets):
    ''' A new artifact '''

    def __init__(self, tree, *args, **kwargs):
        super().__init__(tree, *args, **kwargs)
        self.that = tree.this.create(start=self.lo, stop=self.hi)

    def render(self):
        yield str(self.that)

class Hidden(Octets):
    ''' Hidden '''

    def render(self):
        yield "Hidden"

class Opaque(Octets):
    ''' Hide some octets '''

    def __init__(self, *args, rendered=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.rendered = rendered
        self.that = None

    def artifact(self):
        self.that = self.tree.this.create(start=self.lo, stop=self.hi)
        return self.that

    def render(self):
        if self.that:
            yield self.that
        elif self.rendered is None:
            yield self.__class__.__name__ + "[0x%x]" % (self.hi - self.lo)
        else:
            yield self.rendered

class HexOctets(Octets):
    ''' Octets rendered without text column '''

    def render(self):
        yield "".join("%02x" % i for i in self)

# Text types

def Text(width, rstrip=False):
    ''' Produce class for width text String (convenient for Struct) '''

    class Text_Class(Octets):
        ''' Fixed width text String (convenient for Struct) '''

        WIDTH = width
        RSTRIP = rstrip
        def __init__(self, *args, type_case=None, **kwargs):
            kwargs["width"] = self.WIDTH
            super().__init__(*args, **kwargs)
            if type_case is None:
                type_case = self.this.type_case
            self.type_case = type_case
            self.txt = type_case.decode(self.iter_bytes())
            if self.RSTRIP:
                self.txt = self.txt.rstrip()

        def full_text(self):
            ''' Full representation of the text '''
            return self.type_case.decode_long(self.iter_bytes())

        def render(self):
            yield "»" + self.txt + "«"

    return Text_Class

# Value types

class Octet(Octets):
    ''' A single octet (convenient for Struct) '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(tree, lo, width=1, **kwargs)
        self.val = self.this[lo]

    def render(self):
        yield "0x%02x" % self.val

class Le16(Octets):
    ''' Two bytes Little Endian '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(tree, lo, width=2, **kwargs)
        self.val = self.this[lo + 1] << 8
        self.val |= self.this[lo]

    def render(self):
        yield "0x%04x" % self.val

class Le24(Octets):
    ''' Three bytes Little Endian '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(tree, lo, width=3, **kwargs)
        self.val = self.this[lo + 2] << 16
        self.val |= self.this[lo + 1] << 8
        self.val |= self.this[lo]

    def render(self):
        yield "0x%06x" % self.val

class Le32(Octets):
    ''' Four bytes Little Endian '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(tree, lo, width=4, **kwargs)
        self.val = self.this[lo + 3] << 24
        self.val |= self.this[lo + 2] << 16
        self.val |= self.this[lo + 1] << 8
        self.val |= self.this[lo]

    def render(self):
        yield "0x%08x" % self.val

class Le64(Octets):
    ''' Eight bytes Little Endian '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(tree, lo, width=8, **kwargs)
        self.val = self.this[lo + 7] << 56
        self.val |= self.this[lo + 6] << 48
        self.val |= self.this[lo + 5] << 40
        self.val |= self.this[lo + 4] << 32
        self.val |= self.this[lo + 3] << 24
        self.val |= self.this[lo + 2] << 16
        self.val |= self.this[lo + 1] << 8
        self.val |= self.this[lo]

    def render(self):
        yield "0x%016x" % self.val

class Be16(Octets):
    ''' Two bytes Big Endian '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(tree, lo, width=2, **kwargs)
        self.val = self.this[lo] << 8
        self.val |= self.this[lo + 1]

    def render(self):
        yield "0x%04x" % self.val

class Be24(Octets):
    ''' Three bytes Big Endian '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(tree, lo, width=3, **kwargs)
        self.val = self.this[lo] << 16
        self.val |= self.this[lo + 1] << 8
        self.val |= self.this[lo + 2]

    def render(self):
        yield "0x%06x" % self.val

class Be32(Octets):
    ''' Four bytes Big Endian '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(tree, lo, width=4, **kwargs)
        self.val = self.this[lo + 0] << 24
        self.val |= self.this[lo + 1] << 16
        self.val |= self.this[lo + 2] << 8
        self.val |= self.this[lo + 3]

    def render(self):
        yield "0x%08x" % self.val

class Be64(Octets):
    ''' Eight bytes Big Endian '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(tree, lo, width=8, **kwargs)
        self.val = self.this[lo + 0] << 56
        self.val |= self.this[lo + 1] << 48
        self.val |= self.this[lo + 2] << 40
        self.val |= self.this[lo + 3] << 32
        self.val |= self.this[lo + 4] << 24
        self.val |= self.this[lo + 5] << 16
        self.val |= self.this[lo + 6] << 8
        self.val |= self.this[lo + 7]

    def render(self):
        yield "0x%016x" % self.val

class L2301(Octets):
    ''' Four bytes Deranged Endian '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(tree, lo, width=4, **kwargs)
        self.val = self.this[lo + 2] << 24
        self.val |= self.this[lo + 3] << 16
        self.val |= self.this[lo + 0] << 8
        self.val |= self.this[lo + 1]

    def render(self):
        yield "0x%08x" % self.val

class L1032(Octets):
    ''' Four bytes Demented Endian '''

    def __init__(self, tree, lo, **kwargs):
        super().__init__(tree, lo, width=4, **kwargs)
        self.val = self.this[lo + 1] << 24
        self.val |= self.this[lo + 0] << 16
        self.val |= self.this[lo + 3] << 8
        self.val |= self.this[lo + 2]

    def render(self):
        yield "0x%08x" % self.val

# Complex types

def cstruct_to_fields(text):
    ''' Create FIELDS from C struct(-ish) text '''
    retval = []
    for line in text.split("\n"):
        line = line.split('#', 1)[0]
        line = line.replace(';', '')
        fields = line.split(maxsplit=1)
        if not fields:
            continue
        assert len(fields) == 2
        ftyp, fname = fields
        if '[' not in fname:
            retval.append((fname, ftyp))
            continue
        assert ']' == fname[-1]
        f2 = fname[:-1].split('[')
        assert len(f2) == 2
        fname, dim = f2
        fname = fname.rstrip()
        dim = int(dim)
        retval.append((fname, ftyp, dim))
    return retval

class Struct(datastruct.Struct, Octets):

    TYPES = None
    FIELDS = None

    def __init__(self, *args, **kwargs):
        if self.FIELDS is None:
            datastruct.Struct.__init__(self, *args, **kwargs)
        else:
            datastruct.Struct.__init__(self, *args, more=True, **kwargs)
            assert self.TYPES is not None
            for i in self.FIELDS:
                if len(i) == 3:
                    name, cls, dim = i
                    if isinstance(cls, str):
                        cls = getattr(self.TYPES, cls)
                    self.add_field(name, Array(dim, cls))
                elif len(i) == 2:
                    name, cls = i
                    if isinstance(cls, str):
                        cls = getattr(self.TYPES, cls)
                    self.add_field(name, cls)
                else:
                    assert False
            self.done()

    def base_init(self, **kwargs):
        Octets.__init__(self, self.tree, self.lo, hi=self.hi, **kwargs)

    def number_field(self, offset, width):
        return HexOctets(self.tree, offset, width=width)

    def addfield(self, name, what):
        return self.add_field(name, what)

def Array(count, what, **kwargs):
    return datastruct.Array(Struct, count, what, **kwargs)

# The tree itself

class OctetView(bintree.BinTree):
    ''' ... '''

    def __init__(self, this, default_width=32):
        self.this = this
        self.separators = None
        self.separators_width = 0
        self.default_width = default_width
        hi = len(this)
        super().__init__(
            lo = 0,
            hi = hi,
            leaf = Octets,
        )

    def render(self):
        ''' Rendering iterator with padding '''
        self.separators = [
            (x.lo, " " + str(x.key)) for x in self.this.iter_rec() if x.key is not None
        ]

        if self.separators:
            self.separators.append((len(self.this),"The end"))
        for n in range(0, len(self.separators)-1):
            # Dump empty records individually, with uniform line length
            fm = self.separators[n]
            to = self.separators[n+1]
            i = list(self.find(fm[0], to[0]))
            if len(i) != 0:
                continue
            s = set(self.this[fm[0]:to[0]])
            if len(s) == 1:
                FillRecord(self, lo=fm[0], hi=to[0]).insert()
                continue
            wid = to[0] - fm[0]
            for o in range(0, wid, self.default_width):
                EmptyRecord(
                    self,
                    lo=fm[0] + o,
                    hi=fm[0] + min(o + self.default_width, wid),
                    width=self.default_width
                ).insert()

        if self.separators:
            self.separators.pop(-1)
            self.separators_width = max(len(y) for x, y in self.separators)
        else:
            self.separators_width = 0
        yield from super().render(default_width=self.default_width)

    def add_interpretation(self, title="OctetView", more=False, **kwargs):
        ''' Render via UTF-8 file '''
        with self.this.add_utf8_interpretation(title, more=more) as file:
            for line in self.render(**kwargs):
                file.write(line + '\n')
