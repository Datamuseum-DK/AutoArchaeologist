#!/usr/bin/env python3

'''
   Toolkit for operating on artifacts on byte granularity
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import html

from itertools import zip_longest

from ..base import artifact
from . import bintree

class Octets(bintree.BinTreeLeaf):
    ''' Base class, just some random octets '''

    def __init__(self, tree, lo, width=None, hi=None, name=None):
        if hi is None:
            assert width is not None
            hi = lo + width
        assert hi > lo
        self.tree = tree
        self.this = tree.this
        if name is None:
            name = self.__class__.__name__
        self.ov_name = name
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
        ''' Insert in tree (NB: Optional!) '''
        self.tree.insert(self)
        return self

    def render(self):
        ''' Render hexdumped + text-column '''
        octets = self.this[self.lo:self.hi]
        fmt = "%02x"
        tcase = self.this.type_case.decode(octets)
        yield " ".join(fmt % x for x in octets) + "   ┆" + tcase + "┆"

class This(Octets):
    ''' A new artifact '''

    def __init__(self, tree, *args, **kwargs):
        super().__init__(tree, *args, **kwargs)
        self.this = tree.this.create(start=self.lo, stop=self.hi)

    def render(self):
        yield self.this

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
            yield "Opaque[0x%x]" % (self.hi - self.lo)
        else:
            yield self.rendered

def Text(width):
    ''' Produce class for width text String (convenient for Struct) '''

    class Text_Class(Octets):
        ''' Text String '''

        WIDTH = width
        def __init__(self, *args, **kwargs):
            kwargs["width"] = self.WIDTH
            super().__init__(*args, **kwargs)
            self.txt = self.this.type_case.decode(self.this[self.lo:self.hi])
            self.txt = self.this.type_case.decode(self.iter_bytes())

        def render(self):
            yield "»" + self.txt + "«"

    return Text_Class

class HexOctets(Octets):
    ''' Octets rendered without text column '''

    def render(self):
        yield "".join("%02x" % i for i in self)

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
        self.val = self.tree[lo + 2] << 16
        self.val |= self.tree[lo + 1] << 8
        self.val |= self.tree[lo]

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
        super().__init__(tree, lo, width=2, **kwargs)
        self.val = self.tree[lo] << 16
        self.val |= self.tree[lo + 1] << 8
        self.val |= self.tree[lo + 2]

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

class Struct(Octets):
    '''
        A composite data structure

        A trivial example:

                leaf = Struct(
                    tree,
                    some_address,
                    vertical=True,
                    first_field_=Le32,
                    second_field__=7,
                    last_field_=text_field(8),
                    size=0x100,              
                )

        Note the trailing underscores which designates arguments
        as field names.

        The fields definition can be either an integer, which creates
        a 'HexOctets' that wide or it can be a class which will be
        instantiated with arguments of

                Le32(tree, some_address + field_offset)

        Which allows fields to be defined with all the classes in
        this file, notably including subclasses of Struct itself.

        Each field creates an attribute without the trailing
        underscore, holding the instance of the class, so for
        instance:

                leaf.first_field.val

        is the 32 bit little-endian value and

                leaf.last_field.txt

        is the decoded text-string.

        The extra underscore on the second field name hides the
        field when rendering but still adds the attribute
        '.second_field_'

        The 'vertical' argument controls rendering (one line vs one
        line per field)

        The 'size' defines the total size for cases where the fields
        do not add up.

        Variant structs can be built incrementally, but must then be
        explicitly completed:

                leaf = Struct(
                    tree,
                    some_address,
                    n_elem_=Le16,
                   incomplete=True,
                )
                for i in range(leaf.n_elem.val):
                    leaf.add_field("f%d" % i, Le32)
                leaf.complete(size = 512);

    '''


    def __init__(self, tree, lo, vertical=False, more=False, pad=0, **kwargs):
        self.fields = []
        self.vertical = vertical
        self.lo = lo
        self.hi = lo
        self.tree = tree
        self.args = {}
        for name, width in kwargs.items():
            if name[-1] == "_":
                self.addfield(name[:-1], width)
            else:
                self.args[name] = width
        if not more:
            self.done(pad=pad)

    def done(self, pad=0):
        ''' Struct is complete, finish up '''
        if pad:
            self.hide_the_rest(pad)
        super().__init__(self.tree, self.lo, hi = self.hi, **self.args)
        del self.args

    def add_field(self, name, what):
        ''' add a field to the structure '''
        assert hasattr(self, "args")
        if name is None:
            name = "at%04x" % (self.hi - self.lo)
        if isinstance(what, int):
            y = HexOctets(self.tree, self.hi, width=what)
            z = y
        else:
            y = what(self.tree, self.hi)
            z = y
        self.hi = y.hi
        setattr(self, name, z)
        self.fields.append((name, y))
        return y

    def addfield(self, name, what):
        return self.add_field(name, what)

    def hide_the_rest(self, size):
        ''' hide the rest of the space occupied by the structure '''
        assert hasattr(self, "args")
        assert self.lo + size >= self.hi
        if self.lo + size != self.hi:
            self.addfield("at%x_" % self.hi, self.lo + size - self.hi)

    def suffix(self, adr):
        ''' Suffix in vertical mode is byte offset of field '''
        return "\t// @0x%x" % (adr - self.lo)

    def render(self):
        assert not hasattr(self, "args")
        if not self.vertical:
            i = []
            for name, obj in self.fields:
                if name[-1] != "_":
                    i.append(name + "=" + "|".join(obj.render()))
            yield self.ov_name + " {" + ", ".join(i) + "}"
        else:
            yield self.ov_name + " {"
            for name, obj in self.fields:
                if name[-1] != "_":
                    j = list(obj.render())
                    j[0] += self.suffix(obj.lo)
                    yield "  " + name + " = " + j[0]
                    if len(j) > 1:
                        for i in j[1:-1]:
                            yield "    " + i
                        yield "  " + j[-1]
            yield "}"

def Array(count, what):
    ''' An array of things '''
 
    class Array_Class(Struct):
        WHAT = what
        COUNT = count

        def __init__(self, *args, **kwargs):
            super().__init__(*args, more = True, **kwargs)
            self._elem = []
            for i in range(self.COUNT):
                f = self.add_field("f%d" % i, self.WHAT)
                self._elem.append(f)
            self.done()

        def __getitem__(self, idx):
            return self._elem[idx]

        def __iter__(self):
            yield from self._elem

        def render(self):
            yield '[' + ", ".join("".join(x.render()) for x in self._elem) + ']'

    return Array_Class

class OctetView(bintree.BinTree):
    ''' ... '''

    def __init__(self, this, max_render=None, default_width=16):
        self.this = this
        hi = len(this)
        super().__init__(
            lo = 0,
            hi = hi,
            limit = 1<<16,
        )
        if max_render is None:
            max_render = hi
        self.max_render = max_render
        self.default_width = default_width
        self.adrfmt = "%%0%dx" % len("%x" % self.hi)

    def pad(self, lo, hi):
        assert hi > lo
        width = self.default_width
        if hi - lo <= width:
            yield Octets(self, lo, hi=hi)
            return
        i = lo % width
        if i:
            yield Octets(self, lo, width - i)
            lo += width - i
        while lo + width <= hi:
            yield Octets(self, lo, width)
            lo += width
        if lo < hi:
            yield Octets(self, lo, hi = hi)

    def prefix(self, lo, hi):
        return "0x" + self.adrfmt % lo + "…" + self.adrfmt % hi

    def pad_out(self):
        lo = 0
        prev = None
        for i in sorted(self):
            if i.lo < lo:
                print("Overlap", self.this)
                print("  this: ", hex(i.lo), hex(i.hi), i)
                for n, j in enumerate(i.render()):
                    print("\t" + str(j))
                    if n > 5:
                        break
                if prev is None:
                    print("  prev: None")
                else:
                    print("  prev: ", hex(prev.lo), hex(prev.hi), prev)
                    for n, j in enumerate(prev.render()):
                        print("\t" + str(j))
                        if n > 5:
                            break
            if i.lo > lo:
                yield from self.pad(lo, i.lo)
            yield i
            lo = i.hi
            prev = i
        if lo < self.hi:
            yield from self.pad(lo, self.hi)

    def add_interpretation(self, title="OctetView"):
        ''' Render via utf8 file '''
        # print(self.this, "Rendering", self.gauge, "octetview-leaves")
        tfn = self.this.add_html_interpretation(title)
        with open(tfn.filename, "w", encoding="utf-8") as file:
            file.write("<pre>\n")
            last = None
            lasti = None
            trunc = ""
            rpt = 0
            for i in self.pad_out():
                if i.lo > self.max_render:
                    trunc = "[Truncated]\n"
                    break
                for j in i.render():
                    if isinstance(j, artifact.Artifact):
                        j = j.summary(types=False)
                    else:
                        j = html.escape(j)
                    if j == last:
                        rpt += 1
                        lasti = i
                        continue
                    if rpt == 1:
                        file.write(self.prefix(lasti.lo, lasti.hi) + " " + last + "\n")
                        rpt = 0
                    elif rpt:
                        file.write(self.prefix(lasti.lo, lasti.hi) + " …[0x%x]\n" % rpt)
                        rpt = 0
                    last = j
                    file.write(self.prefix(i.lo, i.hi) + " " + j + "\n")
            if rpt:
                file.write(self.prefix(lasti.lo, lasti.hi) + " …[0x%x]\n" % rpt)
            file.write(trunc)
            file.write("</pre>\n")

    
