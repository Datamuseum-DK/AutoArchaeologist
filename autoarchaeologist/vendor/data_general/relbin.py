#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license
#
# Doc found in Appendix D in:
#	http://novasareforever.org/user/archive/public/docs/dg/sw/os/rdos.utils/
#		069-400019-01__RDOS-DOS_Assembly_Language_and_Program_Utilities__1983-1984.pdf
#
# TBD:
# ----
# DG and RC differs on specifics, and this class should properly be
# subclassed for RC's case.
#
# It also looks like DG messed up some of the asignments of record types
# and fixed it by changing the .TITL records from octal 4 to octal 14
# as a marker of the new assignment.  (See appendix B in versions of the
# DG assembler manual)

'''
   Data General Relocatable Binary objects and libraries
   -----------------------------------------------------
'''

from ...base import octetview as ov
from ...base import namespace as ns

REC_MAX_LEN = {
    1: -15,
    2: -15,
    3: -45,
    4: -45,
    5: -45,
    6: -2,
    7: -3,
    9: -3,
    10: -3,
    11: -15,
    12: -15,
    13: -15,
    14: -15,
    15: -15,
}

REC_SYMBOLS = {
    # Bool: do we show the value
    3: True,
    4: False,
    5: True,
    7: False,
}

RELOC_MARKERS = {
    '0': '⁰',
    '1': ' ',
    '2': "'",
    '3': '"',
    '4': '-',
    '5': '=',
    '6': '$',
    '7': '*',
}

def b40(x):
    '''
        Decode a radix-40 encoded symbol
        --------------------------------

        See:  RCSL-42-I-0833 DOMAC - Domus Macro Assembler, User's Guide
        Appendix C and D
    '''
    x = list(x)
    t = ""
    c = "_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.?/"
    for i in (x[1] >> 5, x[0]):
        while i:
            t += c[i % 40]
            i //= 40
    symtyp = {
        0x00: ".ENT",
        0x01: ".EXTN",
        0x02: ".EXTA",
        0x03: ".EXTD",
        0x04: ".TITL",
    }.get(x[1] & 0x1f)
    if symtyp is None:
        symtyp = ".SYM%02x" % (x[1] & 0x1f)
    return symtyp, t[::-1].rstrip('_')

class Reloc(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            r0_=ov.Le16,
            r1_=ov.Le16,
            r2_=ov.Le16,
        )
        self.reloc = "%05o%05o%05o" % (self.r0.val >> 1, self.r1.val >> 1, self.r2.val >> 1)

    def render(self):
        yield "Reloc {" + self.reloc + "}"

class Symb(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f0_=ov.Le16,
            f1_=ov.Le16,
            equiv_=ov.Le16,
        )
        self.kind, self.name = b40((self.f0.val, self.f1.val))

    def render(self):
        yield "Symbol {" + self.kind + ": " + self.name + " = 0x%04x}" % self.equiv.val

class InvalidRbRecord(ValueError):
    ''' ... '''

class RbRec(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            more=True,
            kind_=ov.Le16,
            wcnt_=ov.Ls16,
            reloc_=Reloc,
            csum_=ov.Le16,
        )
        lim = REC_MAX_LEN.get(self.kind.val)
        if lim is None:
            self.done()
            raise InvalidRbRecord()
        if self.wcnt.val < lim or self.hi + -2 * self.wcnt.val > len(tree.this):
            self.done()
            raise InvalidRbRecord()
        if self.kind.val in REC_SYMBOLS:
            self.add_field("s", ov.Array(-self.wcnt.val//3, Symb))
        else:
            self.add_field("w", ov.Array(-self.wcnt.val, ov.Le16))
        tmp = ov.Array((self.hi - self.lo)//2, ov.Le16)(tree, self.lo)
        self.rsum = sum(x.val for x in tmp) & 0xffff
        self.done()
        if self.kind.val > 0o17:
            raise InvalidRbRecord()
        if self.rsum:
            raise InvalidRbRecord()

    def interpretation(self, file):
        r = self.reloc.reloc
        file.write("%02x -%02x %s" % (self.kind.val, -self.wcnt.val, r))
        file.write(" %04x" % self.csum.val)
        if self.kind.val in REC_SYMBOLS:
            for rl, sym in zip(r, self.s):
                file.write("\n\t" + sym.kind.ljust(7) + sym.name.ljust(6))
                if self.kind.val in (3, 7):
                    self.tree.this.add_name(sym.name)
                if REC_SYMBOLS[self.kind.val]:
                    file.write(" = %04x" % sym.equiv.val + RELOC_MARKERS[rl])
        else:
            hwb = []
            hwl = []
            for rl, w in zip(r, self.w):
                if rl == '1':
                    hwb.append(self.tree.this.type_case.decode((w.val >> 8, w.val & 0xff)))
                    hwl.append(self.tree.this.type_case.decode((w.val & 0xff, w.val >> 8)))
                else:
                    hwb.append('  ')
                    hwl.append('  ')
                file.write(" %04x" % w.val + RELOC_MARKERS[rl])
            if len(self.w) > 1:
                file.write(" " * 6 * (15 - len(self.w)))
                file.write("  ┆" + ''.join(hwb[1:]).ljust(28) + "┆")
                file.write(''.join(hwl[1:]).ljust(28) + "┆")
        file.write("\n")

class NameSpace(ns.NameSpace):
    ''' ... '''
    KIND = "Relocatable Library"

class RelBin(ov.OctetView):
    def __init__(self, this):
        super().__init__(this)

        rbs = []
        kinds = []

        ptr = 0
        while ptr <= len(this) - 12:
            while ptr < len(this) and this[ptr] == 0:
                ptr += 1
            if ptr == len(this):
                break
            if ptr > len(this) - 12:
                break
            try:
                rb = RbRec(self, ptr)
            except InvalidRbRecord:
                break
            rbs.append(rb)
            kinds.append(rb.kind.val)
            ptr = rb.hi

        if len(rbs) == 0:
            return

        if ptr != len(this):
            #print(this, "OD", hex(ptr), hex(len(this)), hex(this[ptr]))
            # Other data follows.
            # Snip out the reloc records, which we will get back to.
            this.create(start=rbs[0].lo, stop=rbs[-1].hi)
            return

        if kinds.count(6) > 1:

            this.add_type("RelBinLib")
            rns = NameSpace(name = '', root = this, separator = "")

            def commit(recs):
                that = this.create(start=recs[0].lo, stop=recs[-1].hi)
                nm = "@0x%x" % recs[0].lo
                for rec in recs:
                    if rec.kind.val == 7:
                        nm = rec.s[0].name
                        break
                NameSpace(
                    name=nm,
                    parent=rns,
                    this=that,
                )

            c = []
            for k, rb in zip(kinds, rbs):
                c.append(rb)
                if k in (9, 10):
                    c = []
                    continue
                if k in (6,):
                    commit(c)
                    c = []
            if c:
                commit(c)
            this.add_interpretation(self, rns.ns_html_plain)
        else:
            this.add_type("RelBin")
            f = this.add_utf8_interpretation("RelBin")
            with open(f.filename, "w", encoding="utf8") as file:
                for i in rbs:
                    i.interpretation(file)

        for rb in rbs:
            rb.insert()
            if rb.kind.val == 7:
                this.add_name(rb.s[0].name)
        self.add_interpretation(title="RelBin", more=True)
