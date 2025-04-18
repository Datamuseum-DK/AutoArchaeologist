#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   This is based on reverse-engineering a single
   DisplayWriter floppy disk, which transpired to
   have already been preserved.  More work needed.
'''

from ...base import octetview as ov

df = open("/tmp/_.dot", "w")
df.write('digraph {\n')
df.write('rankdir=LR\n')

class Hdr(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            used_=ov.Be16,
            tag_=ov.Octet,
        )

class TBD(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            hdr_=Hdr,
            more=True,
        )

        if self.hdr.tag.val and 0 < self.hdr.used.val < 0x800:
            w = self.hdr.used.val - 3
            self.add_field("f", w)
        else:
            self.add_field("f", 2)
        self.done()
        df.write('x%x [label="%02X\\n0x%x"]\n' % (self.lo, self.hdr.tag.val, self.lo))

    def render(self):
        return
        yield " ".join(
            (
                "TBD",
                str(self.hdr),
                *self.this.hexdump(self.f.lo, self.f.hi, width = len(self.f)),
            )
        )

class TextField(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            hdr_=Hdr,
            #x_=ov.Be16,
            more=True,
        )
        w = self.hdr.used.val - 3
        self.add_field("f_", w)
        self.done()

    def render(self):
        #return
        yield from super().render()
        yield from self.text()

    def text(self):
        #for i in self.this.hexdump(self.f_.lo, self.f_.hi):
        #    yield " " * 6 + i
        b = bytes(self.this[self.f_.lo:self.f_.hi])
        c = b.replace(b'\x2b\xd4\x02\x7a', b'')
        c = c.replace(b'\x2b\xd4\x02\x7e', b'')
        t = self.this.type_case.decode_long(c)
        mw = 100
        for i in t.split("\n"):
            while len(i) > mw:
                #yield " " * 12 + "»" + i[:mw] + "…"
                yield " " * 12 + i[:mw] + "…"
                i = i[mw:]
            #yield " " * 12 + "»" + i[:mw] + "«"
            yield " " * 12 + i[:mw]


class SectorEntry(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            a_=ov.Octet,
            b_=ov.Octet,
            c_=ov.Be16,
        )

    def render(self):
        yield '{0x%02x,0x%02x,0x%02x}' % (self.a.val, self.b.val, self.c.val)

class AllocEntry(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            a_=ov.Be16,
            b_=ov.Be16,
            more=True,
        )
        self.add_field("c", ov.Array(self.b.val, SectorEntry))
        self.done()


    def start(self):
        return self.a.val << 8

    def span(self):
        return sum(1+x.c.val for x in self.c)

    def iter_sectors(self):
        ptr = self.a.val << 8
        for i in self.c:
            yield ptr, i
            ptr += 1<<8

class AllocList(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            hdr_=Hdr,
            more=True,
        )
        df.write('x%x [label="AL\\n0x%x"]\n' % (self.lo, self.lo))
        w = self.hdr.used.val - 4
        self.add_field("e0x", 1)
        n = 1
        self.entries = []
        while len(self) < self.hdr.used.val:
            df.write('x%x -> x%x\n' % (self.lo, self.hi))
            y = self.add_field("f%d" % n, AllocEntry)
            self.entries.append(y)
            n += 1
        self.done()

    def iter_alloc_entries(self):
        yield from self.entries

    def traverse(self, prefix):
        for ae in self.entries:
            if ae.a.val == 0x750:
                continue
            #print('a' + prefix, hex(ae.lo), ae, ae.span())
            ptr = ae.start()
            end = ptr + ae.span()
            while ptr < end:
                y = make_rec(self.tree, ptr).insert()
                if isinstance(y, TextField):
                    #print('b' + prefix + "  ", hex(y.lo))
                    for i in y.text():
                        print('|' + prefix + "  ", i)
                #else:
                #    print('b' + prefix + "  ", hex(y.lo), y)
                ptr = y.hi
                if isinstance(y, AllocList):
                    y.traverse(prefix + "\t")

class Unallocated(ov.Dump):
    ''' ... '''

class FreeMap(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            hdr_=Hdr,
            x_=ov.Octet,
            more = True,
        )
        self.add_field("bits", self.hdr.used.val - 4)
        self.done()

def make_rec(tree, adr):
    typ = tree.this[adr + 2]
    if typ == 0xe0:
        return AllocList(tree, adr)
    if typ == 0xe8:
        return TextField(tree, adr)
    return TBD(tree, adr)

class EHL1(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            hdr_=Hdr,
            f0_=ov.Octet,
            f1_=ov.Text(12),
            f2_=ov.Be16,
            f3_=ov.Be32,
            f4_=ov.Be16,
            f5_=ov.Octet,
            free_=ov.Array(3, FreeMap, vertical=True),
            a0_=AllocList,
            p0_=2,
            a1_=AllocList,
            p1_=12,
            a2_=AllocList,
            p2_=4,
            a3_=AllocList,
        )
        if True:
            self.a0.traverse("")
            self.a1.traverse("")
            self.a2.traverse("")
            self.a3.traverse("")

        if True:
            for n, fb in enumerate(self.iter_free()):
                # print(n, hex(n<<8), fb)
                if fb:
                    Unallocated(self.tree, n<<8, width=0x100).insert()

    def iter_free(self):
        for fm in self.free:
            for b in self.tree.this[fm.bits.lo:fm.bits.hi]:
                for i in range(8):
                    if True:
                        yield (b>>7) & 1
                        b <<= 1
                    else:
                        yield b & 1
                        b >>= 1


class DisplayWriter(ov.OctetView):
    def __init__(self, this):
        if len(this) != 985088:
            return
        super().__init__(this)

        EHL1(self, 0x75000).insert()

        self.add_interpretation()
        df.write('}\n')
        df.flush()
