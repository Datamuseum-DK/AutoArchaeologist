#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

''' ... '''

from ...base import octetview as ov

class Rec():
    def __init__(self, tree, frag):
        self.tree = tree
        self.frag = frag
        self.next = (frag.frag[0] << 8) | frag.frag[1]
        self.next_rec = None
        self.prev_rec = []

    def commit(self):
        if self.prev_rec:
            return
        p = self
        frags = []
        tsum = 0
        while p:
            frags.append(p.frag.frag[2:])
            tsum += sum(p.frag[2:])
            if 0 and tsum:
                 ov.Opaque(self.tree, p.frag.lo, hi = p.frag.hi).insert()
            p = p.next_rec
        if not tsum:
            return

        y = self.tree.this.create(records=frags)
        y.add_name("AT%02x%1x_%02x" % (self.frag.key[0], self.frag.key[2], len(frags)))

class DirEnt(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            w0_=ov.Be16,
            w1_=ov.Be16,
            w2_=ov.Be16,
            w3_=ov.Be16,
        )

    def render(self):
        a = list(super().render())
        D=64
        yield a[0] + "  " + ", ".join(
             (
                 bin(self.w2.val | 0x10000)[3:],
                 bin(self.w3.val | 0x10000)[3:],
                 "%2d" % (self.w2.val % D),
                 "%2d" % ((self.w2.val//D) % D),
                 "%2d" % ((self.w2.val//D) // D),
                 "%2d" % (self.w3.val % D),
                 "%2d" % ((self.w3.val//D) % D),
                 "%2d" % ((self.w3.val//D) // D),
             )
        )

class Bar(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            w0_=ov.Be16,
            w1_=ov.Be16,
            w2_=ov.Be16,
            w3_=ov.Be16,
            w4_=ov.Be16,
            w5_=ov.Be16,
            w6_=ov.Be16,
            w7_=ov.Be16,
        )

class SecData(ov.Struct):

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            w0_=ov.Be16,
            x__=256,
        )
        self.rendered = "?"

    def render(self):
        a = list(super().render())
        yield a[0] + " " + self.rendered

class AlphaLsi(ov.OctetView):

    def __init__(self, this):
        if this.top not in this.parents:
            return
        super().__init__(this)

        dirents = []
        if this[1] == 0x90:
            for s in (6, 7):
                f = this.get_frag((0,0,s))
                if f:
                    y = ov.Array(32, DirEnt, vertical=True)(self, f.lo + 2).insert()
                    for de in y:
                        if de.w1.val:
                            dirents.append(de)

            for s in (8, 9):
                f = this.get_frag((0,0,s))
                if f:
                    ov.Array(16, Bar, vertical=True)(self, f.lo + 2).insert()

        if this[1] == 0x00:
            f = this.get_frag((0,0,0))
            if f:
                ov.Array(32, DirEnt, vertical=True)(self, f.lo + 2).insert()
            for t in range(1, 76, 4):
                f = this.get_frag((t,0,0))
                if f:
                    ov.Array(16, Bar, vertical=True)(self, f.lo + 2).insert()
                f = this.get_frag((t,0,1))
                if f:
                    ov.Array(16, Bar, vertical=True)(self, f.lo + 2).insert()

        for de in dirents:
            fn = "B%04x%04x" % (de.w2.val, de.w3.val)
            frags = []
            sec = de.w0.val & 0xfff
            n = 0
            while sec:
                f = this.get_frag((sec >> 4,0,sec & 0xf))
                if not f:
                    print(this, "FRAG not found", hex(sec), de)
                    break
                if n > de.w1.val:
                    print(this, "End of", n, de)
                    break
                z = SecData(self, lo=f.lo).insert()
                z.rendered = "@" + fn + "_%x" % n
                frags.append(f.frag[2:])
                sec = (f.frag[0] << 8) | f.frag[1]
                n += 1
            if n != de.w1.val:
                print(this, "MISMATCH", hex(n), hex(len(frags)), de)
            if frags:
                y = this.create(records=frags)
                y.add_name(fn)
                z = bytes(y)
                if bytes.fromhex('b0 b0 b0 b0 a0 c5 d2 d2 cf d2 d3') in z:
                    y.add_type("ZERO_ERRORS")
                if bytes.fromhex('d0 d7 d2 a0 c6 c1 c9 cc') in z:
                    y.add_type("PWR_FAIL")
                
        this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation(title="HexDump", elide=0)
