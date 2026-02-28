#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   MCZ BASIC files
   ===============

   Usage
   -----

   .. code-block:: none
 
       from autoarchaeologist.vendor.zilog.zdos_basic import MczBasic
       …
       self.add_examiner(MczBasic)

   Notes
   -----

   Reverse engineered from samples.

   Test input
   ----------

   * COMPANY/ZILOG

   Documentation
   -------------

   https://datamuseum.dk/wiki/Bits:30001638

   * BASIC Interpreter, Preliminary User's Manual
   * Contains no information about the file format.

'''

from ...base import octetview as ov

class BasicHead(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            variables_=ov.Le16,
            stms_=ov.Le16,
            f2_=ov.Le16,
            f3_=14,
        )

class VarDef(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f0_=ov.Be16,
            f1_=ov.Octet,
            f2_=ov.Octet,
        )
        self.name = ""
        if self.f1.val & 0x10:
            self.name += "FN"
        self.name += "%c" % ((self.f2.val & 0x1f) + 0x41)
        i = self.f1.val & 0xf
        if i <= 9:
            self.name += "%d" % i
        if self.f2.val & 0x20:
            self.name += "%"
        if self.f2.val & 0x40:
            self.name += "$"
        if self.f2.val & 0x80:
            self.name += "'"
        if self.f1.val & 0xa0:
            self.name += "<%02x%02x>" % (self.f1.val, self.f2.val)
        self.idx = None

    def render(self):
        i = [ ]
        i += super().render()
        i.append(self.name)
        i.append(hex(self.idx))
        yield ' '.join(i)

class Statement(ov.Octets):
    ''' ... '''

    def __init__(self, lineno, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lineno = lineno

        self.rendered = None
        if self[0] == 0xb:
            self.rem()
        elif self[0] == 0x00:
            self.toklist("GOTO", 1)
        elif self[0] == 0x01:
            self.toklist("GOSUB", 1)
        elif self[0] == 0x02:
            self.on()
        elif self[0] == 0x03:
            self.toklist("IF", 1)
        elif self[0] == 0x04:
            self.toklist("ELSE", 1)
        elif self[0] == 0x05:
            self.toklist("RETURN", 1)
        elif self[0] == 0x07:
            self.toklist("END", 1)
        elif self[0] == 0x08:
            self.toklist("DOEND", 1)
        elif self[0] == 0x09:
            self.toklist("COM", 1)
        elif self[0] == 0x0a:
            self.toklist("DIM", 1)
        elif self[0] == 0x0d:
            self.toklist("DEF", 1)
        elif self[0] == 0x0e:
            self.toklist("FNEND", 1)
        elif self[0] == 0x0f:
            self.toklist("PRINT", 1)
        elif self[0] == 0x10:
            self.toklist("INPUT", 1)
        elif self[0] == 0x11:
            self.toklist("LINPUT", 1)
        elif self[0] == 0x12:
            self.toklist("READ", 1)
        elif self[0] == 0x15:
            self.toklist("RESTORE", 1)
        elif self[0] == 0x18:
            self.toklist("CHAIN", 1)
        elif self[0] == 0x1b:
            self.toklist("LET", 1)
        elif self[0] == 0x1c:
            self.trap()
        elif self[0] == 0x1f:
            self.toklist("SYSTEM", 1)
        elif self[0] == 0x21:
            self.toklist("SPACE", 1)

    def toklist(self, what, idx):
        self.rendered = what
        while idx < len(self):
            self.rendered += " "
            tok = self[idx]
            if 0 <= tok <= 0x3f:
                self.rendered += "%d" % tok
                idx += 1
                continue
            if tok == 0x40:
                self.rendered += "var("
                try:
                    self.rendered += self.tree.variables[self[idx+1] + 0x2d].name
                except:
                    self.rendered += "A0x%02x" % self[idx+1]
                self.rendered += ")"
                idx += 2
                continue
            if 0x41 <= tok <= 0x6d:
                self.rendered += "var("
                try:
                    self.rendered += self.tree.variables[tok - 0x41].name
                except:
                    self.rendered += "B0x%02x" % tok
                self.rendered += ")"
                idx += 1
                continue
            if tok == 0x64:
                self.rendered += "USING"
                idx += 1
                continue
            if tok == 0x67:
                self.rendered += "67()"
                idx += 1
                continue
            if tok == 0x6b:
                self.rendered += "6b()"
                idx += 1
                continue
            if tok == 0x6c:
                self.rendered += "6c()"
                idx += 1
                continue
            if tok == 0x6e:
                # 0333300000000081 -> 3.333
                # 0360.000000000083 -> 360
                mantissa = ""
                mantissa += "%02x" % (self[idx + 1] & 0x7f)
                for j in range(2,8):
                    mantissa += "%02x" % self[idx + j]
                j = self[idx+8]
                j -= 0x80
                nbr = int(mantissa, 10) * 10**(j - 13)
                if self[idx+1] & 0x80:
                    self.rendered += "-"
                self.rendered += "%g" % nbr
                idx += 9
                continue
                self.rendered += " 6e("
                idx += 1
                for i in range(8):
                    self.rendered += "%02x" % self[idx]
                    idx += 1
                self.rendered += ")"
                continue
            if tok == 0x6f:
                self.rendered += "%%%d" % (self[idx+1] + self[idx+2] * 256)
                idx += 3
                continue
            if tok == 0x70:
                idx += 1
                j = self[idx]
                idx += 1
                self.rendered += "»"
                for i in range(j):
                    slug = self.tree.this.type_case[self[idx]]
                    if slug:
                        self.rendered += slug.long
                    else:
                        self.rendered += "\\x%02x" % self[idx]
                    idx += 1
                self.rendered += "«"
                continue
            if tok == 0x71:
                self.rendered += "="
                idx += 1
                continue
            if tok == 0x72:
                self.rendered += "ELEMENT"
                idx += 1
                continue
            if tok == 0x73:
                self.rendered += "("
                idx += 1
                continue
            if tok == 0x74:
                self.rendered += ")"
                idx += 1
                continue
            if tok == 0x75:
                self.rendered += "USING"
                idx += 1
                continue
            if tok == 0x9f:
                self.rendered += "[]"
                idx += 1
                continue
            if tok == 0xa2:
                self.rendered += "?ABS"
                idx += 1
                continue
            if tok == 0xa3:
                self.rendered += "?SGN"
                idx += 1
                continue
            if tok == 0xa4:
                self.rendered += "SQR"
                idx += 1
                continue
            if tok == 0xab:
                self.rendered += "LEN"
                idx += 1
                continue
            if tok == 0xad:
                self.rendered += "VAL"
                idx += 1
                continue
            if tok == 0xe1:
                self.rendered += "SUB1"
                idx += 1
                continue
            if tok == 0xe3:
                self.rendered += "SUB2"
                idx += 1
                continue
            if tok == 0xe2:
                self.rendered += "PLUS"
                idx += 1
                continue
            if tok == 0xe4:
                self.rendered += "MULT"
                idx += 1
                continue
            if tok == 0xe5:
                self.rendered += "DIV"
                idx += 1
                continue
            if tok == 0xe6:
                self.rendered += "POW"
                idx += 1
                continue
            if tok == 0xe7:
                self.rendered += "EQ"
                idx += 1
                continue
            if tok == 0xe8:
                self.rendered += "?<"
                idx += 1
                continue
            if tok == 0xea:
                self.rendered += ">"
                idx += 1
                continue
            if tok == 0xec:
                self.rendered += "<>"
                idx += 1
                continue
            if tok == 0xed:
                self.rendered += "AND"
                idx += 1
                continue
            if tok == 0xee:
                self.rendered += "OR"
                idx += 1
                continue
            if tok == 0xf1:
                self.rendered += "COMMA"
                idx += 1
                continue
            if tok == 0xf2:
                self.rendered += "SEMI"
                idx += 1
                continue
            if tok == 0xf3:
                self.rendered += "EOS"
                idx += 1
                continue
            if tok == 0xf4:
                self.rendered += "%d#" % self[idx+1]
                idx += 2
                continue

            self.rendered += " → "
            break
        while idx < len(self):
            self.rendered += "%02x" % self[idx]
            idx += 1

    def lineref(self, idx):
        self.rendered += "%02x%02x" % (self[idx+1], self[idx])

    def trap(self):
        self.rendered = "TRAP"
        if self[1] == 1:
            self.rendered += " ERR "
        elif self[1] == 2:
            self.rendered += " ESC "
        else:
            self.rendered += " %d " % self[1]
        if self[2] == 0xf6:
            self.rendered += "OFF"
        else:
            self.lineref(2)

    def on(self):
        self.toklist("ON", 1)

    def rem(self):
        assert self[1] == 0x70
        i = self[2]
        self.rendered = "REM " + self.tree.this.type_case.decode(self.octets()[3:3+i])

    def render(self):
        if self.rendered:
            yield "%04x " % self.lineno + self.rendered
        else:
            yield "%04x " % self.lineno + self.octets().hex()

class StmtPtr(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            nbr_=ov.Be16,
            offset_=ov.Be16,
        )
        self.stmt = None

    def commit(self, adr, width):
        self.stmt = Statement(self.nbr.val, self.tree, adr, width).insert()

    def render(self):
        if self.stmt:
            yield "Statement %05d @0x%x" % (self.nbr.val, self.stmt.lo)

class MczBasic(ov.OctetView):
    ''' Zilog MCZ BASIC'''

    def __init__(self, this):
        if len(this) < 24:
            return
        for a in range(6, 20):
            if this[a]:
                return
        super().__init__(this)

        head = BasicHead(self, 0).insert()
        if head.variables.val == 0:
            return
        if head.stms.val == 0:
            return
        if head.variables.val + head.stms.val > len(this):
            this.add_note("ZILOG_BASIC_short")
            return
        self.head = head

        print(this, self.__class__.__name__, len(this))
        this.add_note("MCZ_BASIC")

        vbase = self.head.hi
        variables = ov.Vector(
            self,
            vbase,
            count=self.head.variables.val//4,
            target=VarDef,
            vertical=True,
        ).insert()
        self.variables = {}
        for n, i in enumerate(reversed(list(x for x in variables))):
            i.idx = n
            self.variables[n] = i

        self.stmts = []
        sbase = vbase + self.head.variables.val
        for adr in range(0, self.head.stms.val, 4):
            y = StmtPtr(self, adr + sbase).insert()
            self.stmts.append(y)

        nbase = y.hi
        prev = len(this)
        for stmt in self.stmts:
            adr = nbase + stmt.offset.val
            if prev < adr:
                self.this.add_note("Mangled BASIC Statement")
                break
            stmt.commit(adr, prev-adr)
            prev = adr

        self.add_interpretation(more=True)
