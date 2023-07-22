#!/usr/bin/env python3

'''
   Operating on artifacts in Byte-alignment
   ----------------------------------------
'''

import autoarchaeologist.generic.tree as tree

class Octets(tree.TreeLeaf):
    ''' ... '''

    def __init__(self, up, lo, width=None, hi=None, name=None):
        if hi is None:
            assert width is not None
            hi = lo + width
        if hi - lo > (1<<16):
            print("Big Octets 0x%x" % (hi - lo), hex(lo), hex(hi), up, up.this)
        self.up = up
        self.this = up.this
        if name is None:
            name = self.__class__.__name__
        self.name = name
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

    def insert(self):
        self.up.insert(self)
        return self

    def render(self):
        # yield str(self)
        octets = self.this[self.lo:self.hi]
        fmt = "%02x"
        tc = self.this.type_case.decode(octets)
        yield " ".join(fmt % x for x in octets) + "   |" + tc + "|"

class Le16(Octets):
    def __init__(self, up, lo, **kwargs):
        super().__init__(up, lo, width=2, **kwargs)
        self.val = self.this[lo + 1] << 8
        self.val |= self.this[lo]

    def render(self):
        yield "0x%04x" % self.val

class Le32(Octets):
    def __init__(self, up, lo, **kwargs):
        super().__init__(up, lo, width=4, **kwargs)
        self.val = self.this[lo + 3] << 24
        self.val |= self.this[lo + 2] << 16
        self.val |= self.this[lo + 1] << 8
        self.val |= self.this[lo]

    def render(self):
        yield "0x%08x" % self.val

class Be16(Octets):
    def __init__(self, up, lo, **kwargs):
        super().__init__(up, lo, width=2, **kwargs)
        self.val = self.this[lo] << 8
        self.val |= self.this[lo + 1]

    def render(self):
        yield "0x%04x" % self.val

class Struct(Octets):
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
            y = Octets(self.up, self.hi, width=what)
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



class OctetView(tree.Tree):
    ''' ... '''

    def __init__(self, this):
        self.this = this
        hi = len(this)
        super().__init__(
            lo = 0,
            hi = hi,
            limit = 1<<16,
        )

    def pad(self, lo, hi):
        width = 16
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
            yield Octets(self, lo, hi)

    def prefix(self, lo, hi):
        fmt = "%%0%dx" % len("%x" % self.hi)
        return "0x" + fmt % lo + "…" + fmt % hi

    def pad_out(self):
        lo = 0
        prev = None
        for i in sorted(self):
            if i.lo < lo:
                print("Overlap", self.this)
                print("  this: ", hex(i.lo), hex(i.hi), i)
                for n, j in enumerate(i.render()):
                    print("\t" + j)
                    if n > 5:
                        break
                print("  prev: ", hex(prev.lo), hex(prev.hi), prev)
                for n, j in enumerate(prev.render()):
                    print("\t" + j)
                    if n > 5:
                        break
            if i.lo > lo:
                yield from self.pad(lo, i.lo)
            yield i
            lo = i.hi
            prev = i
        if lo < self.hi:
            yield from self.pad(lo, self.hi)

    def render(self, title="OctetView"):
        print(self.this, "Rendering", self.gauge, "octetview-leaves")
        self.tfn = self.this.add_utf8_interpretation(title)
        with open(self.tfn.filename, "w") as file:
            last = None
            lasti = None
            rpt = 0
            for i in self.pad_out():
                for j in i.render():
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

