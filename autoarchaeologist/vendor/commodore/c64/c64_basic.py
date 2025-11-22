#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

''' ... '''

from ....base import octetview as ov
from ....base import type_case

BASIC_TOKENS = {
    0x80: "END",     0x81: "FOR",    0x82: "NEXT",   0x83: "DATA",
    0x84: "INPUT#",  0x85: "INPUT",  0x86: "DIM",    0x87: "READ",
    0x88: "LET",     0x89: "GOTO",   0x8A: "RUN",    0x8B: "IF",
    0x8C: "RESTORE", 0x8D: "GOSUB",  0x8E: "RETURN", 0x8F: "REM",
    0x90: "STOP",    0x91: "ON",     0x92: "WAIT",   0x93: "LOAD",
    0x94: "SAVE",    0x95: "VERIFY", 0x96: "DEF",    0x97: "POKE",
    0x98: "PRINT#",  0x99: "PRINT",  0x9A: "CONT",   0x9B: "LIST",
    0x9C: "CLR",     0x9D: "CMD",    0x9E: "SYS",    0x9F: "OPEN",
    0xA0: "CLOSE",   0xA1: "GET",    0xA2: "NEW",    0xA3: "TAB(",
    0xA4: "TO",      0xA5: "FN",     0xA6: "SPC(",   0xA7: "THEN",
    0xA8: "NOT",     0xA9: "STEP",   0xAA: "+",      0xAB: "-",
    0xAC: "*",       0xAD: "/",      0xAE: "↑",      0xAF: "AND",
    0xB0: "OR",      0xB1: ">",      0xB2: "=",      0xB3: "<",
    0xB4: "SGN",     0xB5: "INT",    0xB6: "ABS",    0xB7: "USR",
    0xB8: "FRE",     0xB9: "POS",    0xBA: "SQR",    0xBB: "RND",
    0xBC: "LOG",     0xBD: "EXP",    0xBE: "COS",    0xBF: "SIN",
    0xC0: "TAN",     0xC1: "ATN",    0xC2: "PEEK",   0xC3: "LEN",
    0xC4: "STR$",    0xC5: "VAL",    0xC6: "ASC",    0xC7: "CHR$",
    0xC8: "LEFT$",   0xC9: "RIGHT$", 0xCA: "MID$",   0xCB: "GO",
}

class C64BasicTypeCase(type_case.TypeCase):
    ''' A typecase augmented with BASIC tokens '''

    def __init__(self, model):
        super().__init__(model.name + "-BASIC")
        for n, s in enumerate(model.slugs):
            if s.flags != model.INVALID:
                self.set_slug(n, s.short, s.long, s.flags)
        for n, t in BASIC_TOKENS.items():
            self.set_slug(n, ' ', t + " ")
        self.set_slug(0, " ", " ", self.EOF)

class FileHdr(ov.Struct):
    ''' Load address ? '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            ptr_=ov.Le16,
        )

class Statement(ov.Struct):
    ''' One BASIC statement'''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            ptr_=ov.Le16,
            lno_=ov.Le16,
            more=True,
        )
        self.add_field("body", self.ptr.val - (self.lo + 0x803))
        self.done()

    def render(self):
        l = []
        quote = False
        for i in self.body:
            if i == 0x22:
                quote = not quote
            if quote:
                l.append(self.tree.this.type_case.decode_long([i]))
            else:
                l.append(self.tree.basic_type_case.decode_long([i]))

        yield " ".join(
            (
                "0x%04x" % self.ptr.val,
                "%05d" % self.lno.val,
                "".join(l),
            )
        )

class C64Basic(ov.OctetView):
    ''' ... '''

    def __init__(self, this):

        if this[0] != 0x01:
            return
        if this[1] != 0x08:
            return

        print(this, self.__class__.__name__, len(this))

        super().__init__(this)
        this.add_note("C64-BASIC")
        self.basic_type_case = C64BasicTypeCase(this.type_case)

        fh = FileHdr(self, 0).insert()
        ptr = fh.hi
        while ptr < len(this) - 8 and (this[ptr] or this[ptr + 1]):
            h = Statement(self, ptr).insert()
            if not 0x801 < h.ptr.val < 0x800 + len(this):
                break
            ptr = h.ptr.val - 0x7ff
            if this[ptr - 1] != 0:
                break

        self.add_interpretation(elide=0)
