#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license
#
# Huge thanks to Mogens Kjær for providing a Perl5
# script which I have merely converted to Python3

''' Commodore C64= COMAL '''

from ....base import octetview as ov
from ....base import type_case

def join_stack(stack, glue):
    x = stack.pop(-1)
    y = stack.pop(-1)
    stack.append(y + glue + x)

def wrap_stack(stack, pfx, sfx):
    x = stack.pop(-1)
    stack.append(pfx + x + sfx)

def decode_char(tree, char, quote=True):
    if quote and char == 0x22:
        return '""'
    if 0x20 <= char <= 0x7f:
        return tree.this.type_case.decode_long([char])
    if 0xc0 <= char <= 0xda:
        return tree.this.type_case.decode_long([char])
    return '"%d"' % char

class LineNo(ov.Be16):

    def render(self):
        if self.val > 10000:
            yield "%04d" % (self.val - 10000)
        else:
            yield "%04d" % self.val

class TokNo(ov.Struct):
    ''' ... '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            more = True,
        )
        t = tree.this[self.lo]
        if t == 0xff:
            self.add_field("token", ov.Be16)
            self.token.val -= 0xfe00
        else:
            self.add_field("token", ov.Octet)
        self.done()

    def render(self):
        yield "T%03x|%d" % (self.token.val, self.token.val)

class Token(ov.Struct):
    ''' ... '''

    FLDS = []
    INDENT = 0
    INDENT_THIS = 0

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            token_ = TokNo,
            more = True,
        )
        for n, fld in enumerate(self.FLDS):
            self.add_field("f%02d" % n, fld)
        self.done()

    def list(self, stack):
        return False

class NoOpToken(Token):
    def list(self, stack):
        ''' ... '''

class StringConstant(Token):

    def __init__(self, tree, lo, **kwargs):
        l = tree.this[lo+1]
        self.FLDS = [ ov.Octet ]
        if l > 0:
            self.FLDS.append(ov.Text(l))
        super().__init__(tree, lo, **kwargs)

    def list(self, stack):
        if self.f00.val == 0:
            stack.append('""')
        else:
            l = list(decode_char(self.tree, x) for x in self.f01)
            stack.append('"' + "".join(l) + '"')

class IntVar(ov.Le16):
    ''' ... '''

    def render(self):
        v = self.tree.vars.get(self.val)
        if v:
            yield v.varname + "#"
        else:
            yield self.__class__.__name__ + "(%04x)" % self.val

class RealVar(ov.Le16):
    ''' ... '''

    def render(self):
        if self.val == 0xffff:
            return
        v = self.tree.vars.get(self.val)
        if v:
            yield v.varname
        else:
            yield self.__class__.__name__ + "(%04x)" % self.val

class StringVar(ov.Le16):
    ''' ... '''

    def render(self):
        v = self.tree.vars.get(self.val)
        if v:
            yield v.varname + "$"
        else:
            yield self.__class__.__name__ + "(%04x$)" % self.val

class SVar(Token):
    FLDS = [StringVar]
    def list(self, stack):
        stack.append(str(self.f00))

class RVar(Token):
    FLDS = [RealVar]
    def list(self, stack):
        stack.append(str(self.f00))

class RVarComma(Token):
    FLDS = [RealVar]
    def list(self, stack):
        stack.append(str(self.f00) + ",")

class IVarComma(Token):
    FLDS = [IntVar]
    def list(self, stack):
        stack.append(str(self.f00) + ",")

class SVarComma(Token):
    FLDS = [StringVar]
    def list(self, stack):
        stack.append(str(self.f00) + ",")

class RefRVar(Token):
    FLDS = [RealVar]
    def list(self, stack):
        stack[-1] += "REF "
        stack.append(str(self.f00) + ",")

class RefSVar(Token):
    FLDS = [StringVar]
    def list(self, stack):
        stack[-1] += "REF "
        stack.append(str(self.f00) + ",")

class RefIVar(Token):
    FLDS = [IntVar]
    def list(self, stack):
        stack[-1] += "REF "
        stack.append(str(self.f00) + ",")

class IVar(Token):
    FLDS = [IntVar]
    def list(self, stack):
        stack.append(str(self.f00))

class CallRVar(Token):
    FLDS = [RealVar]
    def list(self, stack):
        stack.append(str(self.f00))
        stack[-1] += "("

class CallIVar(Token):
    FLDS = [IntVar]
    def list(self, stack):
        stack.append(str(self.f00))
        stack[-1] += "("

class CallSVar(Token):
    FLDS = [StringVar]
    def list(self, stack):
        stack.append(str(self.f00))
        stack[-1] += "("

class UseName(Token):
    FLDS = [RealVar]

    def list(self, stack):
        stack.append(str(self.f00))
        stack.insert(-1, "USE ")

class Case(Token):
    INDENT = 2
    def list(self, stack):
        stack.append("CASE ")

class CaseOf(Token):
    FLDS = [2]
    def list(self, stack):
        wrap_stack(stack, "", " OF")

class CaseWhen(Token):
    FLDS = [2]
    INDENT_THIS = -2
    def list(self, stack):
        stack.append("WHEN ")

class CaseWhen2(Token):
    FLDS = [2]
    #INDENT_THIS = -2
    def list(self, stack):
        join_stack(stack, "")

class EndCase(Token):
    INDENT = -2
    def list(self, stack):
        stack.append("ENDCASE ") # XXX trailing space ?

class Otherwise(Token):
    FLDS = [2]
    INDENT_THIS = -2
    def list(self, stack):
        stack.append("OTHERWISE ")

class Exit(Token):
    FLDS = [3]
    def list(self, stack):
        stack.append("EXIT")

class ExitWhen(Token):
    FLDS = [3]
    def list(self, stack):
        join_stack(stack, "")

class AndThen(Token):
    FLDS = [1]
    def list(self, stack):
        ''' ... '''

class OrElse(Token):
    FLDS = [1]
    def list(self, stack):
        ''' ... '''

class WhenEnd(Token):
    FLDS = [2]
    def list(self, stack):
        join_stack(stack, "")

class Then(Token):
    FLDS = [2]
    INDENT = 2
    def list(self, stack):
        join_stack(stack, "")
        stack[-1] += " THEN "

class Then2(Token):
    FLDS = [2]
    INDENT = 2
    def list(self, stack):
        join_stack(stack, "")
        stack[-1] += " THEN"

class At(Token):
    def list(self, stack):
        join_stack(stack, ",")
        join_stack(stack, "AT ")
        stack[-1] += ": "

class Handler(Token):
    FLDS = [2]
    INDENT_THIS = -2
    def list(self, stack):
        stack.append("HANDLER")

class EndTrap(Token):
    INDENT = -2
    def list(self, stack):
        stack.append("ENDTRAP")

class Restore(Token):
    FLDS = [RealVar]
    def list(self, stack):
        stack.append(str(self.f00))
        stack.insert(-1, "RESTORE ")

class Import(Token):
    FLDS = [2]
    def list(self, stack):
        stack.append("IMPORT ")

class Loop(Token):
    INDENT = 2
    def list(self, stack):
        stack.append("LOOP")

class EndLoop(Token):
    FLDS = [2]
    INDENT = -2
    def list(self, stack):
        stack.append("ENDLOOP")

class Elif(Token):
    FLDS = [2]
    INDENT = -2
    INDENT_THIS = -2
    def list(self, stack):
        stack.append("ELIF ")

class Else(Token):
    FLDS = [2]
    INDENT_THIS = -2
    def list(self, stack):
        stack.append("ELSE")

class Endif(Token):
    INDENT = -2
    def list(self, stack):
        stack.append("ENDIF")

class ForRVar(Token):
    FLDS = [RealVar, 2]
    def list(self, stack):
        stack.append(str(self.f00))
        stack.insert(-1, "FOR ")

class ForIVar(Token):
    FLDS = [IntVar, 2]
    def list(self, stack):
        stack.append(str(self.f00))
        stack.insert(-1, "FOR ")

class EndForIVar(Token):
    FLDS = [IntVar, 2]
    INDENT = -2
    def list(self, stack):
        stack.append(str(self.f00))
        stack.insert(-1, "ENDFOR ")

class EndForRVar(Token):
    FLDS = [RealVar, 2]
    INDENT = -2
    def list(self, stack):
        stack.append(str(self.f00))
        stack.insert(-1, "ENDFOR ")

class ForFrom(Token):
    FLDS = []

    def list(self, stack):
        join_stack(stack, ":=")

class ForTo(Token):
    FLDS = []

    def list(self, stack):
        join_stack(stack, " TO ")

class ForDo(Token):
    FLDS = []
    INDENT = 2

    def list(self, stack):
        stack[-1] += " DO"

class Repeat(Token):
    INDENT = 2
    def list(self, stack):
        stack.append("REPEAT")

class Until(Token):
    INDENT = -2
    def list(self, stack):
        stack.append("UNTIL ")

class Trap(Token):
    FLDS = [2]
    INDENT = 2
    def list(self, stack):
        stack.append("TRAP")

class UntilFin(Token):
    FLDS = [2]
    def list(self, stack):
        join_stack(stack, "")

class WhileDo(Token):
    FLDS = [2]
    INDENT = 2
    def list(self, stack):
        join_stack(stack, "")
        stack[-1] += " DO"

class EndWhile(Token):
    FLDS = [2]
    INDENT = -2
    def list(self, stack):
        stack.append("ENDWHILE")

class Label(Token):
    FLDS = [RealVar, 3]
    #INDENT = -1000
    def list(self, stack):
        stack.append(str(self.f00))
        stack[-1] += ":"

class ByteConstant(Token):
    FLDS = [ov.Octet]
    def list(self, stack):
        stack.append(str(self.f00.val))

class CharConstant(Token):
    FLDS = [ov.Octet]
    def list(self, stack):
        stack.append('"' + decode_char(self.tree, self.f00.val) + '"')

class RealConstant(Token):
    FLDS = [ov.Octet, ov.Be32]
    def list(self, stack):
        if self.f00.val == 0:
            real = 0
        elif self.f01.val & (1<<31):
            mant = self.f01.val
            real = -mant * 2 ** (self.f00.val - 128 - 32)
        else:
            mant = self.f01.val | (1<<31)
            real = mant * 2 ** (self.f00.val - 128 - 32)
        x = "%g" % real
        if x[:2] == "0.":
            x = x[1:]
        stack.append(x)

class IntegerConstant(Token):
    FLDS = [ov.Bs16]
    def list(self, stack):
        stack.append(str(self.f00.val))

class HexConstant(Token):
    FLDS = [ov.Be16]
    def list(self, stack):
        if self.f00.val < 0x100:
            stack.append("$%02x" % self.f00.val)
        else:
            stack.append("$%04x" % self.f00.val) # XXX: Guessing

class BinConstant(Token):
    FLDS = [ov.Be16]
    def list(self, stack):
        if self.f00.val < 0x100:
            stack.append("%" + bin((1<<8)|self.f00.val)[3:])
        else:
            stack.append("%" + bin((1<<16)|self.f00.val)[3:])

class InputPrompt(Token):
    def list(self, stack):
        join_stack(stack, "")
        stack[-1] += ": "

class InputRVar(Token):
    def list(self, stack):
        join_stack(stack, "")
        stack[-1] += ","

class TrimLastChar(Token):
    def list(self, stack):
        stack[-1] = stack[-1][:-1]

class CommaToSemi(Token):
    def list(self, stack):
        if stack[-1][-1] == ',':
            stack[-1] = stack[-1][:-1]
        stack[-1] += ";"

class CommaToCloseParan(Token):
    def list(self, stack):
        if 0:
            if stack[-1][-1] == ',':
                stack[-1] = stack[-1][:-1]
            stack[-1] += ")"

class Param(Token):
    ''' ... '''
    def __init__(self, tree, lo):
        if tree.this[lo] == 0x72:
            self.FLDS=[RealVar]
        elif tree.this[lo] == 0x74:
            self.FLDS=[StringVar]
        elif tree.this[lo] == 0x75:
            self.FLDS=[RealVar]		# missing REF
        super().__init__(tree, lo)

class RealIndicies(Token):
    FLDS = [ ov.Octet, RealVar ]
    def list(self, stack):
        if self.tree.in_proc:
            stack.append("REF ")
        stack.append(str(self.f01) + "(" + "," * (self.f00.val-1) + ")")
        if self.tree.in_proc:
            stack[-1] += ","

class IntIndicies(Token):
    FLDS = [ ov.Octet, IntVar ]
    def list(self, stack):
        if self.tree.in_proc:
            stack.append("REF ")
        stack.append(str(self.f01) + "(" + "," * (self.f00.val-1) + ")")
        if self.tree.in_proc:
            stack[-1] += ","

class StringIndicies(Token):
    FLDS = [ ov.Octet, StringVar ]
    def list(self, stack):
        if self.tree.in_proc:
            stack.append("REF ")
        stack.append(str(self.f01) + "(" + "," * (self.f00.val-1) + ")")
        if self.tree.in_proc:
            stack[-1] += ","

class IntIndicies2(Token):
    FLDS = [ ov.Octet, IntVar ]
    def list(self, stack):
        stack[-1] += str(self.f01) + "(" + "," * (self.f00.val-1) + "),"

class RealIndicies2(Token):
    FLDS = [ ov.Octet, RealVar ]
    def list(self, stack):
        stack[-1] += str(self.f01) + "(" + "," * (self.f00.val-1) + "),"

class StringIndicies2(Token):
    FLDS = [ ov.Octet, StringVar ]
    def list(self, stack):
        stack[-1] += str(self.f01) + "(" + "," * (self.f00.val-1) + "),"

class EndFunc(Token):
    INDENT = -2
    def __init__(self, tree, lo, kind="XXX"):
        self.FLDS = [kind]
        super().__init__(tree, lo)

    def list(self, stack):
        stack.append("ENDFUNC ")
        stack.append(str(self.f00))

    @classmethod
    def kind(cls, kind):
        return (cls, {"kind": kind})

class Func(Token):
    def __init__(self, tree, lo, kind="XXX"):
        self.FLDS = [kind, 4, ov.Octet]
        super().__init__(tree, lo)

    def list(self, stack):
        self.tree.in_proc = True
        stack.append("FUNC ")
        stack.append(str(self.f00))
        if self.f02.val:
            self.tree.param_count = self.f02.val + 1
            stack[-1] += "("

    @classmethod
    def kind(cls, kind):
        return (cls, {"kind": kind})

class Proc(Token):
    FLDS = [RealVar, 4, ov.Octet]

    def list(self, stack):
        self.tree.in_proc = True
        stack.append("PROC ")
        stack.append(str(self.f00))
        if self.f02.val:
            self.tree.param_count = self.f02.val + 1
            stack[-1] += "("

class EndProc(Token):
    FLDS = [RealVar]
    INDENT = -2

    def list(self, stack):
        stack.append("ENDPROC ")
        stack.append(str(self.f00))

class AssignIVar(Token):
    FLDS = [IntVar]
    def list(self, stack):
        x = stack.pop(-1)
        stack.append(str(self.f00))
        stack[-1] += ":="
        stack[-1] += x

class AssignSVar(Token):
    FLDS = [StringVar]
    def list(self, stack):
        x = stack.pop(-1)
        stack.append(str(self.f00))
        stack[-1] += ":="
        stack[-1] += x

class AssignRVar(Token):
    FLDS = [RealVar]
    def list(self, stack):
        x = stack.pop(-1)
        stack.append(str(self.f00))
        stack[-1] += ":="
        stack[-1] += x

class EndParams(Token):
    FLDS = [2]
    INDENT = 2
    def list(self, stack):
        if 0 and stack[-1][-1] == ",":
            stack[-1] = stack[-1][:-1]
            stack.append(')')

class Closed(Token):
    FLDS = [4]
    INDENT = 2
    def list(self, stack):
        stack[-1] += " CLOSED"

class Dparas(Token):
    def list(self, stack):
        stack[-1] = stack[-1][:-1] + ")("

class DimString(Token):
    FLDS = [StringVar, ov.Octet]

    def list(self, stack):
        stack.append(str(self.f00))
        if self.f01.val:
            stack[-1] += "("

class DimIVar(Token):
    FLDS = [IntVar, ov.Octet]

    def list(self, stack):
        stack.append(str(self.f00))
        if self.f01.val:
            stack[-1] += "("

class DimRVar(Token):
    FLDS = [RealVar, ov.Octet]

    def list(self, stack):
        stack.append(str(self.f00))
        if self.f01.val:
            stack[-1] += "("

class Push(Token):
    def __init__(self, *args, txt=None, **kwargs):
        self.txt = txt
        super().__init__(*args, **kwargs)

    def render(self):
        yield 'Push {Token=%s txt="%s"}' % (str(self.token), self.txt)

    def list(self, stack):
        stack.append(self.txt)

    @classmethod
    def this(cls, txt):
        return (cls, {"txt": txt})

class Prepend(Token):
    def __init__(self, *args, txt=None, **kwargs):
        self.txt = txt
        super().__init__(*args, **kwargs)

    def list(self, stack):
        stack.insert(-1, self.txt)

    @classmethod
    def this(cls, txt):
        return (cls, {"txt": txt})

class Join(Token):
    def __init__(self, *args, pfx="", mid="", sfx="", **kwargs):
        self.pfx = pfx
        self.mid = mid
        self.sfx = sfx
        super().__init__(*args, **kwargs)

    def render(self):
        yield 'Join {Token=%s pfx="%s" mid="%s", sfx="%s"}' % (str(self.token), self.pfx, self.mid, self.sfx)

    def list(self, stack):
        join_stack(stack, self.mid)
        stack[-1] = self.pfx + stack[-1] + self.sfx

    @classmethod
    def around(cls, mid, pfx="", sfx=""):
        return (cls, {"mid": mid, "pfx": pfx, "sfx": sfx})

    @classmethod
    def suffix(cls, sfx):
        return (cls, {"sfx": sfx})

class Wrap(Token):
    def __init__(self, *args, pfx="", sfx="", **kwargs):
        self.pfx = pfx
        self.sfx = sfx
        super().__init__(*args, **kwargs)

    def render(self):
        yield 'Wrap {Token=%s pfx="%s", sfx="%s"}' % (str(self.token), self.pfx, self.sfx)

    def list(self, stack):
        stack[-1] = self.pfx + stack[-1] + self.sfx

    @classmethod
    def inside(cls, pfx, sfx):
        return (cls, {"pfx": pfx, "sfx": sfx})

class EndOfInput(Token):
    def list(self, stack):
        if stack[-1][-1] != ',':
            stack[-1] += ","

class DataJoin(Token):
    FLDS = [2]
    def list(self, stack):
        while len(stack) > 3:
            x = stack.pop(-1)
            y = stack.pop(-1)
            stack.append(y + "," + x)

TOKENS = {
    0x01: RealConstant,
    0x02: IntegerConstant,
    0x03: StringConstant,
    0x04: RVar,
    0x05: IVar,
    0x06: SVar,
    0x07: RVar,
    0x08: IVar,
    0x09: SVar,
    0x0a: CallRVar,
    0x0b: CallIVar,
    0x0c: CallSVar,
    0x0d: Join.suffix(","),
    0x0e: EndProc,
    0x0f: Join.suffix(","),
    0x10: Join.suffix(","),
    0x11: Join.suffix(","),
    0x12: Join.suffix(","),
    0x13: Join.suffix(")"),
    0x14: Join.suffix(""),
    0x15: Join.suffix(")"),
    0x16: Join.suffix(")"),
    0x17: Join.suffix(")"),
    0x18: Join.suffix(")"),
    0x19: Join.suffix(")"),
    0x1a: CallRVar,
    0x1b: Join.suffix(")"),
    0x1c: Join.suffix(")"),
    0x1d: Join.suffix(")"),
    0x1f: Join.suffix(":"),
    0x21: Wrap.inside("-", ""),
    0x22: Join.around("^"),
    0x23: Join.around("/"),
    0x24: Join.around("*"),
    0x25: Join.around(" DIV "),
    0x26: Join.around(" MOD "),
    0x27: Join.around("+"),
    0x28: Join.around("+"),
    0x29: Join.around("-"),
    0x2a: Join.around("<"),
    0x2b: Join.around("<"),
    0x2c: Join.around("="),
    0x2d: Join.around("="),
    0x2e: Join.around("<="),
    0x2f: Join.around("<="),
    0x30: Join.around(">"),
    0x31: Join.around(">"),
    0x32: Join.around("<>"),
    0x33: Join.around("<>"),
    0x34: Join.around(">="),
    0x35: Join.around(">="),
    0x36: Join.around(" IN "),
    0x37: Wrap.inside("NOT ", ""),
    0x38: Join.around(" AND "),
    0x39: Join.around(" OR "),
    0x3a: Join.around(":="),
    0x3b: Join.around(":="),
    0x3c: Join.around(":="),
    0x3d: Join.around(":+"),
    0x3e: Join.around(":+"),
    0x3f: Join.around(":+"),
    0x40: Join.around(":-"),
    0x41: Join.around(":-"),
    0x42: Join.around("; "),
    0x43: Push.this("TRUE"),
    0x44: Push.this("FALSE"),
    0x46: Wrap.inside("ZONE ", ""),
    0x47: Wrap.inside("(", ")"),
    0x48: Wrap.inside("ABS(", ")"),
    0x49: Wrap.inside("ORD(", ")"),
    0x4a: Wrap.inside("ATN(", ")"),
    0x4b: Wrap.inside("CHR$(", ")"),
    0x4c: Wrap.inside("COS(", ")"),
    0x4d: Push.this("ESC"),
    0x4e: Wrap.inside("EXP(", ")"),
    0x4f: Wrap.inside("INT(", ")"),
    0x50: Wrap.inside("LEN(", ")"),
    0x51: Wrap.inside("LEN(", ")"),
    0x52: Wrap.inside("LOG(", ")"),
    0x53: Push.this("RND"),
    0x54: Wrap.inside("RND(", ")"),
    0x55: Join.around(","),
    0x56: Wrap.inside("SGN(", ")"),
    0x57: Wrap.inside("SIN(", ")"),
    0x58: Wrap.inside("SPC$(", ")"),
    0x59: Wrap.inside("SQR(", ")"),
    0x5a: Wrap.inside("TAN(", ")"),
    0x5b: Push.this("TIME"),
    0x5c: Push.this("EOD"),
    0x5d: Wrap.inside("EOF(", ")"),
    0x5e: Push.this("ERRFILE"),
    0x5f: Push.this("PRINT "),
    0x61: Wrap.inside("", ","),
    0x60: NoOpToken,
    0x62: Join.around("USING ", sfx=": "),
    0x64: NoOpToken,
    0x65: NoOpToken,
    0x63: Wrap.inside("TAB(", ")"),
    0x66: Join.around("", sfx=","),
    0x67: Wrap.inside("", ";"),
    0x68: Push.this("IF "),
    0x69: Then,
    0x6a: Wrap.inside("", " THEN "),
    0x6b: Loop,
    0x6c: Exit,
    0x6d: Elif,
    0x6e: Else,
    0x6f: Endif,
    0x70: Proc,
    0x71: Push.this("NULL"),
    0x72: RVarComma,
    0x73: IVarComma,
    0x74: SVarComma,
    0x75: RefRVar,
    0x76: RefIVar,
    0x77: RefSVar,
    0x78: RealIndicies2,
    0x79: IntIndicies2,
    0x7a: StringIndicies2,
    0x7b: RealIndicies,
    0x7c: IntIndicies,
    0x7d: StringIndicies,
    0x7e: EndParams,
    0x7f: Closed,
    0x80: Dparas,
    0x81: RVar,
    0x82: ForRVar,
    0x83: ForIVar,
    0x84: ForFrom,
    0x85: ForTo,
    0x86: Join.around(" STEP "),
    0x87: ForDo,
    0x88: Wrap.inside("", " DO "),
    0x89: Join.around(""),
    0x8a: EndForRVar,
    0x8b: EndForIVar,
    0x8c: Wrap.inside("DIM ", ""),
    0x8d: DimRVar,
    0x8e: DimIVar,
    0x8f: DimString,
    0x90: Join.around("", sfx=":"),
    0x91: Join.around("", sfx=","),
    0x92: Join.suffix(")"),
    0x93: Join.around(" OF "),
    0x94: Join.around(", "),
    0x95: Repeat,
    0x96: UntilFin,
    0x97: Push.this("WHILE "),
    0x98: WhileDo,
    0x99: Join.suffix(" DO "),
    0x9a: Join,
    0x9b: EndWhile,
    0x9c: Label,
    0x9e: EndLoop,
    0x9f: Push.this("END"),
    0xa0: Push.this("STOP"),
    0xa1: Case,
    0xa2: CaseOf,
    0xa3: CaseOf,
    0xa4: CaseWhen,
    0xa5: Join.around("", sfx=","),
    0xa6: WhenEnd,
    0xa7: Join.around("", sfx=","),
    0xa8: Otherwise,
    0xa9: EndCase,
    0xaa: Push.this("DATA "),
    0xab: DataJoin,
    0xac: CaseWhen2,
    0xad: Wrap.inside("", ":"),
    0xae: Wrap.inside("", ":"),
    0xaf: Push.this("READ "),
    0xb0: Wrap.inside("", ","),
    0xb1: Join.around("", sfx=","),
    0xb2: Join.around("", sfx=","),
    0xb3: TrimLastChar,
    0xb5: Push.this("INPUT "),
    0xb6: Then2,
    0xb7: InputPrompt,
    0xb8: InputRVar,
    0xb9: Join.around("", sfx=","),
    0xba: Wrap.inside("", ","),
    0xbb: TrimLastChar,
    0xbc: CommaToSemi,
    0xbd: Push.this("SELECT "),
    0xbe: Join.around("OUTPUT "),
    0xbf: Push.this("TRAP"),
    0xc0: Wrap.inside("", " ESC"),
    0xc1: Wrap.inside("", "+"),
    0xc2: Wrap.inside("", "-"),
    0xc3: Push.this("WRITE "),
    0xc4: Join.around("", sfx=","),
    0xc5: Join.around("", sfx=","),
    0xc6: Join.around("", sfx=","),
    0xc7: TrimLastChar,
    0xc9: Join.around(",", pfx="FILE ", sfx=": "),
    0xca: Join.around("FILE ", sfx=": "),
    0xcb: Wrap.inside("", ";"),
    0xcd: CharConstant,
    0xce: ByteConstant,
    0xcf: Push.this(""),
    0xd0: Push.this("EXIT WHEN "),
    0xd1: ExitWhen,
    0xd2: AndThen,
    0xd3: BinConstant,
    0xd4: UseName,
    0xd5: Wrap.inside("GET$(", ")"),
    0xd6: Join.around("", sfx=","),
    0xd7: Join.around(""),
    0xd8: Wrap.inside("PEEK(", ")"),
    0xd9: HexConstant,
    0xda: Until,
    0xdc: At,
    0xdf: Join.around(""),
    0xe1: Push.this("RETURN "),
    0xe3: Func.kind(RealVar),
    0xe5: Func.kind(StringVar),
    0xe6: EndFunc.kind(RealVar),
    0xe8: EndFunc.kind(StringVar),
    0xe9: Wrap.inside("VAL(", ")"),
    0xea: Wrap.inside("STR$(", ")"),
    0xeb: Import,
    0xec: Join.around(" BITAND "),
    0xed: Join.around(" BITOR "),
    0xee: Join.around(" BITXOR "),
    0xef: TrimLastChar,
    0xf0: Restore,
    0xf1: Join.around(" AND THEN "),
    0xf2: OrElse,
    0xf3: Join.around(",", pfx="CURSOR "),
    0xf4: Join.around(" OR ELSE "),
    0xf5: CommaToCloseParan,
    0xf6: Join.around(" EXTERNAL "),
    0xf8: AssignSVar,
    0xf7: Wrap.inside("", "("),
    0xf9: Trap,
    0xfa: AssignRVar,
    0xfb: AssignIVar,
    0xfc: Handler,
    0xfd: EndTrap,
    0xfe: Push.this("ERR"),
    0x110: Push.this("DELD-"),
    0x113: Push.this("OPEN"),
    0x114: Push.this("PI"),
    0x115: Push.this("PAGE"),
    0x117: Push.this("ERRTEXT$"),
    0x118: Push.this("CLOSE"),
    0x119: Join.around(" FILE "),
    0x11a: Push.this("CLOSE"),
    0x11b: Join.around(","),
    0x11c: Wrap.inside("CHAIN ", ""),
    0x11d: Join.around(","),
    0x11e: Wrap.inside("UNIT ", ""),
    0x11f: Push.this("KEY$"),
    0x120: Wrap.inside("OPEN FILE ", ""),
    0x122: Join.around(","),
    0x123: Wrap.inside("", ",READ"),
    0x124: Wrap.inside("", ",WRITE"),
    0x125: Wrap.inside("", ",APPEND"),
    0x126: Join.around(",RANDOM "),
    0x12b: Join.around(",", pfx="POKE "),
    0x12e: Push.this("UNIT$"),
    0x12f: Join.around(" UNTIL ", pfx="REPEAT "),
    0x131: Wrap.inside("TIME ", ""),
    0x132: Push.this("REPORT"),
    0x134: EndOfInput,
    0x135: Wrap.inside("PASS ", ""),
    0x136: Push.this("MOUNT"),
    0x138: Prepend.this("END "),
    0x139: Prepend.this("DELETE "),
    0x13b: Push.this("RANDOMIZE"),
    0x13c: Wrap.inside("REPORT ", ""),
    0x13d: Join.around(",", pfx="CREATE "),
    0x13f: Join.around(",", pfx="REPORT "),
}

class Statement(ov.Struct):
    ''' One COMAL statement'''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            lineno_=LineNo,
            size_=ov.Octet,
            vertical = True,
            more = True,
        )
        self.rem = ""
        self.indent = 0
        self.indent_this = 0
        n = 0
        b = self.hi
        e = b + self.size.val - 3
        while b < e:
            t = TokNo(tree, b)
            cls = TOKENS.get(t.token.val)
            if isinstance(cls, tuple):
                y = self.add_field("t%02d" % n, cls)
                self.indent += cls[0].INDENT
                self.indent_this += cls[0].INDENT_THIS
                n += 1
            elif cls:
                y = self.add_field("t%02d" % n, cls)
                self.indent += cls.INDENT
                self.indent_this += cls.INDENT_THIS
                n += 1
            elif t.token.val == 0:
                y = self.add_field("comment", ov.Text(e - b))
                self.rem = "//" + ''.join(decode_char(tree, x, quote=False) for x in list(y)[1:])
                n += 1
            else:
                y = self.add_field("unknown", e - b)
            b = y.hi

        self.done()
        x = self.list()
        if '╬' in x or '▓' in x:
            print(tree.this, "INCOMPL", self.lineno, x)
            tree.this.add_note("ComalIncompl")

    def list(self):
        self.tree.param_count = 0
        self.tree.in_proc = False
        stack = [""]
        good = True
        for n,f in self.fields[2:]:
            if good is False:
                stack.append(str(f))
                continue
            if isinstance(f, Token):
                good = f.list(stack)
            elif n != "comment":
                if f[0] == 0xff:
                    stack.append("╬" + str(f[0]))
                    stack.append("╬" + str(f[1]))
                else:
                    stack.append("╬" + str(f[0]))
                stack.append(str(f))
                good = False
            if self.tree.param_count > 0:
                self.tree.param_count -= 1
                if self.tree.param_count == 0:
                    if stack[-1][-1] == ",":
                        stack[-1] = stack[-1][:-1]
                    stack[-1] += ')'

        if good is not False:
            sep = ""
        else:
            sep = " "
        stk = sep.join(stack)
        if self.rem:
            if stk and stk[-1:] != " ":
                stk += " "
            stk += self.rem
        return stk

    def render(self):
        yield from super().render()
        yield str(self.lineno) + " " + self.list()

class Variable(ov.Struct):
    ''' One COMAL variable'''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            size_=ov.Octet,
            f00_=ov.Octet,
            f01_=ov.Octet,
            f02_=ov.Octet,
            more = True,
        )
        self.add_field("name", ov.Text(self.size.val - 4))
        self.done()
        self.varname = "".join(decode_char(tree, x) for x in self.name)

class Hdr(ov.Struct):
    ''' One COMAL variable'''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            magic_=ov.Le16,
            f00_=ov.Octet,
            f01_=ov.Le16,
            f02_=ov.Le16,
            f03_=ov.Le16,
        )

class C64Unicomal(ov.OctetView):
    ''' ... '''

    def __init__(self, this):
        if len(this)  < 8:
            return

        if this[0] != 0xff:
            return
        if this[1] != 0xff:
            return
        if this[2] != 0x02:
            return

        # print(this, self.__class__.__name__, len(this))

        super().__init__(this)
        this.add_note("C64-UNICOMAL")
        hdr = Hdr(self, 0).insert()

        self.param_count = 0
        self.in_proc = False

        vbase = hdr.hi + hdr.f02.val
        adr = vbase
        self.vars = {}
        while adr + 1 < hdr.hi + hdr.f03.val:
            try:
                y = Variable(self, adr).insert()
                self.vars[adr - vbase] = y
                adr = y.hi
            except Exception as err:
                print(this, "BAD VAR", hex(adr), err)
                break

        ptr = hdr.hi
        stmt = []
        while ptr < hdr.hi + hdr.f02.val:
            try:
                y = Statement(self, ptr)
            except Exception as err:
                print(this, "BAD STMT", hex(adr), err)
                raise
                break
            if y.size.val == 0:
                break
            y.insert()
            stmt.append(y)
            ptr += y.size.val

        with self.this.add_utf8_interpretation("COMAL80") as file:
            indent = 0
            for i in stmt:
                if i.indent < -999:
                    indent = 0
                elif i.indent < 0:
                    indent += i.indent
                indent = max(indent, 0)
                file.write(str(i.lineno) + " " * (1 + indent + i.indent_this) + i.list() + "\n")
                if i.indent > 0:
                    indent += i.indent
                indent = max(indent, 0)
        with open("/tmp/C64Comal/" + this.digest + ".cml", "wb") as file:
            file.write(bytes(this))
        with open("/tmp/C64Comal/" + this.digest + ".lst", "w") as file:
            indent = 0
            for i in stmt:
                if i.indent < -999:
                    indent = 0
                elif i.indent < 0:
                    indent += i.indent
                indent = max(indent, 0)
                ri = max(1, 1 + indent + i.indent_this)
                file.write(str(i.lineno) + " " * ri + i.list() + "\n")
                if i.indent > 0:
                    indent += i.indent
                indent = max(indent, 0)

        self.add_interpretation(more=True)
