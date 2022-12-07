#!/usr/bin/env python3

'''
   Operating on artifacts in bit-alignment
   ---------------------------------------
'''

from autoarchaeologist.generic.ascii import Str2Html
import autoarchaeologist.generic.tree as tree

class Bits(tree.TreeLeaf):
    ''' ... '''

    def __init__(self, up, lo, width=None, hi=None, name=""):
        if hi is None:
            assert width is not None
            hi = lo + width
        if hi - lo > 1>>16:
            assert hi - lo < 1<<16, "Too big 0x%x-0x%x" % (lo, hi)
        self.up = up
        self.this = up.this
        self.hidden = False
        self.name = name
        super().__init__(lo, hi)
        up.insert(self)

    def __len__(self):
        return self.hi - self.lo

    def render(self):
        bits = self.this.bits(self.lo, hi = self.hi)
        if len(bits) > 8 and '1' not in bits:
            yield "0[0x%x]" % len(bits)
            return
        if len(bits) > 8 and '0' not in bits:
            yield "1[0x%x]" % len(bits)
            return
        fmt = "(0x%%0%dx)" % ((3 + self.hi - self.lo) >> 2)
        yield fmt % self.this.bitint(self.lo, hi=self.hi) + " " + bits

class Ignore(Bits):
    ''' ... '''

    def __init__(self, *args, name="ignored", **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

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

    def __init__(self, up, lo, length = None):
        self.val = []
        if length is None:
            hi = lo
            while True:
                j = up.this.bitint(hi, 8)
                self.val.append(j)
                hi += 8
                if not j:
                    break
        else:
            hi = lo
            for _i in range(length):
                j = up.this.bitint(hi, 8)
                self.val.append(j)
                hi += 8

        super().__init__(up, lo, hi = hi)
        self.txt = Str2Html(self.val)

    def render(self):
        yield '"' + self.txt + '"'


class Struct(Bits):
    ''' ... '''

    def __init__(self, up, lo, vertical=False, more=False, **kwargs):
        self.fields = {}
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
            self.done()

    def addfield(self, name, what):
        if name is None:
            name = "at%04x" % (self.hi - self.lo)
        if isinstance(what, int):
            if what > 0:
                y = Int(self.up, self.hi, width=what)
                setattr(self, name, y.val)
            else:
                y = Bits(self.up, self.hi, width=-what)
                setattr(self, name, y)
        else:
            y = what(self.up, self.hi)
            setattr(self, name, y)
        self.hi = y.hi
        y.hidden = True
        self.fields[name] = y
        return y

    def hide_the_rest(self, size):
        assert self.lo + size >= self.hi
        if self.lo + size != self.hi:
            self.addfield("at%x_" % self.hi, self.lo + size - self.hi)

    def done(self):
        super().__init__(self.up, self.lo, hi = self.hi, **self.args)

    def render(self):
        if not self.vertical:
            i = []
            for name, obj in self.fields.items():
                if name[-1] == "_":
                    continue
                i.append(name + "=" + "|".join(obj.render()))
            yield self.name + " {" + ", ".join(i) + "}"
        else:
            yield self.name + " {"
            for name, obj in self.fields.items():
                if name[-1] == "_":
                    continue
                j = list(obj.render())
                yield "  " + name + " = " + j[0] + "\t// @0x%x" % (obj.lo - self.lo)
                if len(j) > 1:
                    for i in j[1:-1]:
                        yield "    " + i
                    yield "  " + j[-1]
            yield "}"

class BitView(tree.Tree):
    ''' ... '''

    def __init__(self, this):
        self.this = this
        super().__init__(0, len(this) * 8)

    def x__len__(self):
        return len(self.this) * 8

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

    def render(self, title="BitView"):
        self.tfn = self.this.add_utf8_interpretation(title)

        def pad_out():
            lo = 0
            last = None
            for i in sorted(self):
                if i.hidden:
                    continue
                if i.lo < lo:
                    print("Overlap", hex(i.lo>>13), i, last)
                if i.lo > lo:
                    yield from self.pad(lo, i.lo)
                yield i
                lo = i.hi
                last = i
            if lo < self.hi:
                yield from self.pad(lo, self.hi)

        with open(self.tfn.filename, "w") as file:
            for i in pad_out():
                for j in i.render():
                    file.write(self.prefix(i.lo, i.hi) + " " + j + "\n")
