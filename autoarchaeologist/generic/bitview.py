#!/usr/bin/env python3

'''
   Operating on artifacts in bit-alignment
   ---------------------------------------
'''

from ..generic.ascii import Str2Html
import ..base import bintree

class Bits(bintree.BinTreeLeaf):
    ''' ... '''

    def __init__(self, up, lo, width=None, hi=None, name=None):
        if hi is None:
            assert width is not None
            hi = lo + width
        if hi - lo > (1>>13):
            assert hi - lo <= (1<<13), "Too big 0x%x-0x%x" % (lo, hi)
        self.up = up
        self.this = up.this
        if name is None:
            name = self.__class__.__name__
        self.name = name
        super().__init__(lo, hi)

    def __len__(self):
        return self.hi - self.lo

    def insert(self):
        self.up.insert(self)
        return self

    def render(self):
        bits = self.this.bits(self.lo, hi = self.hi)
        if len(bits) > 8 and '1' not in bits:
            yield "0[0x%x]" % len(bits)
            return
        if len(bits) > 8 and '0' not in bits:
            yield "1[0x%x]" % len(bits)
            return
        fmt = "(0x%%0%dx)" % ((3 + self.hi - self.lo) >> 2)
        yield fmt % int(bits, 2) + " " + bits

class Ignore(Bits):
    ''' ... '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self):
        yield "[" + self.name + "]"

class Int(Bits):
    ''' ... '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.val = self.this.bitint(self.lo, hi=self.hi)

    def render(self):
        fmt = "0x%%0%dx" % ((3 + self.hi - self.lo) >> 2)
        yield fmt % self.val

class Char(Bits):
    ''' ... '''

    def __init__(self, up, lo):
        super().__init__(up, lo, lo + 8)
        self.val = self.this.bitint(self.lo, 8)

    def render(self):
        yield "'" + Str2Html([self.val]) + "'"

class String(Bits):
    ''' ... '''

    def __init__(self, up, lo, length = None, term=0, **kwargs):
        val = []
        if length is None:
            hi = lo
            while True:
                j = up.this.bitint(hi, 8)
                val.append(j)
                hi += 8
                if j == term:
                    break
        else:
            hi = lo
            for _i in range(length):
                j = up.this.bitint(hi, 8)
                val.append(j)
                hi += 8

        super().__init__(up, lo, hi = hi, **kwargs)
        self.txt = Str2Html(val)

    def render(self):
        yield '"' + self.txt + '"'


class Struct(Bits):
    ''' ... '''

    def __init__(self, up, lo, vertical=False, more=False, pad=0, **kwargs):
        self.fields = []
        self.vertical = vertical
        self.lo = lo
        self.hi = lo
        self.up = up
        self.args = {}
        for name, width in kwargs.items():
            if name[-1] == "_":
                self.addfield(name[:-1], width)
            else:
                self.args[name] = width
        if not more:
            self.done(pad=pad)

    def done(self, pad=0):
        if pad:
            self.hide_the_rest(pad)
        super().__init__(self.up, self.lo, hi = self.hi, **self.args)
        del self.args

    def addfield(self, name, what):
        assert hasattr(self, "args")
        if name is None:
            name = "at%04x" % (self.hi - self.lo)
        if isinstance(what, int):
            if what > 0:
                y = Int(self.up, self.hi, width=what)
                z = y.val
            else:
                y = Bits(self.up, self.hi, width=-what)
                z = y
        else:
            y = what(self.up, self.hi)
            z = y
        self.hi = y.hi
        setattr(self, name, z)
        self.fields.append((name, y))
        return y

    def hide_the_rest(self, size):
        assert hasattr(self, "args")
        assert self.lo + size >= self.hi
        if self.lo + size != self.hi:
            self.addfield("at%x_" % self.hi, self.lo + size - self.hi)

    def suffix(self, adr):
        return "\t// @0x%x" % (adr - self.lo)

    def render(self):
        assert not hasattr(self, "args")
        if not self.vertical:
            i = []
            for name, obj in self.fields:
                if name[-1] != "_":
                    i.append(name + "=" + "|".join(obj.render()))
            yield self.name + " {" + ", ".join(i) + "}"
        else:
            yield self.name + " {"
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

class BitView(bintree.BinTree):
    ''' ... '''

    def __init__(self, this):
        self.this = this
        hi = len(this) * 8
        i = 1
        while i < hi:
            i += i
        hi = i
        super().__init__(
            lo = 0,
            hi = hi,
            limit = 1<<16,
        )

    def pad(self, lo, hi):
        width = 128
        if hi - lo <= width:
            yield Bits(self, lo, hi=hi)
            return
        i = lo % width
        if i:
            yield Bits(self, lo, width - i)
            lo += width - i
        while lo < hi:
            yield Bits(self, lo, hi = min(lo + width, hi))
            lo += width

    def prefix(self, lo, hi):
        fmt = "%%0%dx" % len("%x" % self.hi)
        return "0x" + fmt % lo + "…" + fmt % hi

    def pad_out(self):
        lo = 0
        prev = None
        for i in sorted(self):
            if i.lo < lo:
                print("Overlap", hex(i.lo>>13), i, prev)
            if i.lo > lo:
                yield from self.pad(lo, i.lo)
            yield i
            lo = i.hi
            prev = i
        if lo < self.hi:
            yield from self.pad(lo, self.hi)

    def render(self, title="BitView", maxlines=10000):
        print(self.this, "Rendering", self.gauge, "bitview-leaves")
        self.tfn = self.this.add_utf8_interpretation(title)
        n = 0
        with open(self.tfn.filename, "w") as file:
            for i in self.pad_out():
                for j in i.render():
                    file.write(self.prefix(i.lo, i.hi) + " " + j + "\n")
                    n += 1
                    if n > maxlines:
                        file.write("[…truncated at %d lines…]\n" % max_lines)
                        return
