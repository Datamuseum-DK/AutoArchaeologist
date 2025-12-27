#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license
#
# Huge thanks to Mogens Kjær for providing a Perl5
# script which I have merely converted to Python3
#
# TODO:
#
#    Det checker signaturen for SAVE filer, hex:  FF FF 02 00
#    Den efterfølgende byte er 00 for uprotected og 01 for protected filer.
#
#    Dump navnetabel for indlejdrede og selvstændige binary-packages.
#
#    Repair missing tokens for protected programs.

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
    if 0xc0 < char <= 0xda:
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

class ForDo(Token):
    FLDS = []
    INDENT = 2

    def list(self, stack):
        stack[-1] += " DO"

class Repeat(Token):
    INDENT = 2
    def list(self, stack):
        stack.append("REPEAT")

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

class Goto(Token):
    FLDS = [RealVar, 1]
    def list(self, stack):
        stack.append("GOTO ")
        stack.append(str(self.f00))
        join_stack(stack, "")

class Interrupt(Token):
    FLDS = [RealVar]
    def list(self, stack):
        stack.append("INTERRUPT ")
        stack.append(str(self.f00))
        join_stack(stack, "")

class Label(Token):
    FLDS = [RealVar, 3]
    INDENT_THIS = -1000
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
    def __init__(self, *args, txt=None, indent=0, **kwargs):
        self.txt = txt
        self.INDENT = indent
        super().__init__(*args, **kwargs)

    def render(self):
        if self.INDENT:
            yield 'Push {Token=%s txt="%s", indent=%d}' % (str(self.token), self.txt, self.INDENT)
        else:
            yield 'Push {Token=%s txt="%s"' % (str(self.token), self.txt)

    def list(self, stack):
        stack.append(self.txt)

    @classmethod
    def this(cls, txt, indent=0):
        return (cls, {"txt": txt, "indent": indent})

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

class PrefixOpen(Token):
    def list(self, stack):
        stack.insert(0, "OPEN ")
        stack.insert(-1, ",")

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
    0x001: RealConstant,
    0x002: IntegerConstant,
    0x003: StringConstant,
    0x004: RVar,
    0x005: IVar,
    0x006: SVar,
    0x007: RVar,
    0x008: IVar,
    0x009: SVar,
    0x00a: CallRVar,
    0x00b: CallIVar,
    0x00c: CallSVar,
    0x00d: Join.suffix(","),
    0x00e: EndProc,
    0x00f: Join.suffix(","),
    0x010: Join.suffix(","),
    0x011: Join.suffix(","),
    0x012: Join.suffix(","),
    0x013: Join.suffix(")"),
    0x014: Wrap.inside("RETURN ", ""),
    0x015: Join.suffix(")"),
    0x016: Join.suffix(")"),
    0x017: Join.suffix(")"),
    0x018: Join.suffix(")"),
    0x019: Join.suffix(")"),
    0x01a: CallRVar,
    0x01b: Join.suffix(")"),
    0x01c: Join.suffix(")"),
    0x01d: Join.suffix(")"),
    0x01e: Join.suffix(")"),
    0x01f: Join.suffix(":"),
    0x020: Wrap.inside("+", ""),
    0x021: Wrap.inside("-", ""),
    0x022: Join.around("^"),
    0x023: Join.around("/"),
    0x024: Join.around("*"),
    0x025: Join.around(" DIV "),
    0x026: Join.around(" MOD "),
    0x027: Join.around("+"),
    0x028: Join.around("+"),
    0x029: Join.around("-"),
    0x02a: Join.around("<"),
    0x02b: Join.around("<"),
    0x02c: Join.around("="),
    0x02d: Join.around("="),
    0x02e: Join.around("<="),
    0x02f: Join.around("<="),
    0x030: Join.around(">"),
    0x031: Join.around(">"),
    0x032: Join.around("<>"),
    0x033: Join.around("<>"),
    0x034: Join.around(">="),
    0x035: Join.around(">="),
    0x036: Join.around(" IN "),
    0x037: Wrap.inside("NOT ", ""),
    0x038: Join.around(" AND "),
    0x039: Join.around(" OR "),
    0x03a: Join.around(":="),
    0x03b: Join.around(":="),
    0x03c: Join.around(":="),
    0x03d: Join.around(":+"),
    0x03e: Join.around(":+"),
    0x03f: Join.around(":+"),
    0x040: Join.around(":-"),
    0x041: Join.around(":-"),
    0x042: Join.around("; "),
    0x043: Push.this("TRUE"),
    0x044: Push.this("FALSE"),
    0x045: Push.this("ZONE"),
    0x046: Wrap.inside("ZONE ", ""),
    0x047: Wrap.inside("(", ")"),
    0x048: Wrap.inside("ABS(", ")"),
    0x049: Wrap.inside("ORD(", ")"),
    0x04a: Wrap.inside("ATN(", ")"),
    0x04b: Wrap.inside("CHR$(", ")"),
    0x04c: Wrap.inside("COS(", ")"),
    0x04d: Push.this("ESC"),
    0x04e: Wrap.inside("EXP(", ")"),
    0x04f: Wrap.inside("INT(", ")"),
    0x050: Wrap.inside("LEN(", ")"),
    0x051: Wrap.inside("LEN(", ")"),
    0x052: Wrap.inside("LOG(", ")"),
    0x053: Push.this("RND"),
    0x054: Wrap.inside("RND(", ")"),
    0x055: Join.around(","),
    0x056: Wrap.inside("SGN(", ")"),
    0x057: Wrap.inside("SIN(", ")"),
    0x058: Wrap.inside("SPC$(", ")"),
    0x059: Wrap.inside("SQR(", ")"),
    0x05a: Wrap.inside("TAN(", ")"),
    0x05b: Push.this("TIME"),
    0x05c: Push.this("EOD"),
    0x05d: Wrap.inside("EOF(", ")"),
    0x05e: Push.this("ERRFILE"),
    0x05f: Push.this("PRINT "),
    0x060: NoOpToken,
    0x061: Wrap.inside("", ","),
    0x062: Join.around("USING ", sfx=": "),
    0x063: Wrap.inside("TAB(", ")"),
    0x064: NoOpToken,
    0x065: NoOpToken,
    0x066: Wrap.inside("", ","),
    0x067: Wrap.inside("", ";"),
    0x068: Push.this("IF "),
    0x069: Then,
    0x06a: Wrap.inside("", " THEN "),
    0x06b: Loop,
    0x06c: Exit,
    0x06d: Elif,
    0x06e: Else,
    0x06f: Push.this("ENDIF", indent=-2),
    0x070: Proc,
    0x071: Push.this("NULL"),
    0x072: RVarComma,
    0x073: IVarComma,
    0x074: SVarComma,
    0x075: RefRVar,
    0x076: RefIVar,
    0x077: RefSVar,
    0x078: RealIndicies2,
    0x079: IntIndicies2,
    0x07a: StringIndicies2,
    0x07b: RealIndicies,
    0x07c: IntIndicies,
    0x07d: StringIndicies,
    0x07e: EndParams,
    0x07f: Closed,
    0x080: Dparas,
    0x081: RVar,
    0x082: ForRVar,
    0x083: ForIVar,
    0x084: Join.around(":="),
    0x085: Join.around(" TO "),
    0x086: Join.around(" STEP "),
    0x087: ForDo,
    0x088: Wrap.inside("", " DO "),
    0x089: Join.around(""),
    0x08a: EndForRVar,
    0x08b: EndForIVar,
    0x08c: Wrap.inside("DIM ", ""),
    0x08d: DimRVar,
    0x08e: DimIVar,
    0x08f: DimString,
    0x090: Join.suffix(":"),
    0x091: Join.suffix(","),
    0x092: Join.suffix(")"),
    0x093: Join.around(" OF "),
    0x094: Join.around(", "),
    0x095: Repeat,
    0x096: UntilFin,
    0x097: Push.this("WHILE "),
    0x098: WhileDo,
    0x099: Join.suffix(" DO "),
    0x09a: Join,
    0x09b: EndWhile,
    0x09c: Label,
    0x09d: Goto,
    0x09e: EndLoop,
    0x09f: Push.this("END"),
    0x0a0: Push.this("STOP"),
    0x0a1: Case,
    0x0a2: CaseOf,
    0x0a3: CaseOf,
    0x0a4: CaseWhen,
    0x0a5: Join.suffix(","),
    0x0a6: WhenEnd,
    0x0a7: Join.suffix(","),
    0x0a8: Otherwise,
    0x0a9: Push.this("ENDCASE", indent=-2),
    0x0aa: Push.this("DATA "),
    0x0ab: DataJoin,
    0x0ac: CaseWhen2,
    0x0ad: Wrap.inside("", ":"),
    0x0ae: Wrap.inside("", ":"),
    0x0af: Push.this("READ "),
    0x0b0: Wrap.inside("", ","),
    0x0b1: Join.suffix(","),
    0x0b2: Join.suffix(","),
    0x0b3: TrimLastChar,
    0x0b4: Push.this("RESTORE"),
    0x0b5: Push.this("INPUT "),
    0x0b6: Then2,
    0x0b7: InputPrompt,
    0x0b8: InputRVar,
    0x0b9: Join.suffix(","),
    0x0ba: Wrap.inside("", ","),
    0x0bb: TrimLastChar,
    0x0bc: CommaToSemi,
    0x0bd: Push.this("SELECT "),
    0x0be: Join.around("OUTPUT "),
    0x0bf: Push.this("TRAP "),
    0x0c0: Wrap.inside("", "ESC"),
    0x0c1: Wrap.inside("", "+"),
    0x0c2: Wrap.inside("", "-"),
    0x0c3: Push.this("WRITE "),
    0x0c4: Join.suffix(","),
    0x0c5: Join.suffix(","),
    0x0c6: Join.suffix(","),
    0x0c7: TrimLastChar,
    0x0c8: Join.around(",", pfx="FILE ", sfx=": "),
    0x0c9: Join.around(",", pfx="FILE ", sfx=": "),
    0x0ca: Join.around("FILE ", sfx=": "),
    0x0cb: Wrap.inside("", ";"),
    0x0cc: Join.around(" INPUT "),
    0x0cd: CharConstant,
    0x0ce: ByteConstant,
    0x0cf: Push.this(""),
    0x0d0: Push.this("EXIT WHEN "),
    0x0d1: ExitWhen,
    0x0d2: AndThen,
    0x0d3: BinConstant,
    0x0d4: UseName,
    0x0d5: Wrap.inside("GET$(", ")"),
    0x0d6: Join.suffix(","),
    0x0d7: Join.suffix(""),
    0x0d8: Wrap.inside("PEEK(", ")"),
    0x0d9: HexConstant,
    0x0da: Push.this("UNTIL ", indent=-2),
    0x0db: Interrupt,
    0x0dc: At,
    0x0dd: Push.this("INTERRUPT"),
    0x0de: Push.this("STATUS$"),
    0x0df: Wrap.inside("RETURN ", ""),
    0x0e0: Wrap.inside("RETURN ", ""),
    0x0e1: NoOpToken,
    0x0e2: Push.this("RETURN"),
    0x0e3: Func.kind(RealVar),
    0x0e4: Func.kind(IntVar),
    0x0e5: Func.kind(StringVar),
    0x0e6: EndFunc.kind(RealVar),
    0x0e7: EndFunc.kind(IntVar),
    0x0e8: EndFunc.kind(StringVar),
    0x0e9: Wrap.inside("VAL(", ")"),
    0x0ea: Wrap.inside("STR$(", ")"),
    0x0eb: Import,
    0x0ec: Join.around(" BITAND "),
    0x0ed: Join.around(" BITOR "),
    0x0ee: Join.around(" BITXOR "),
    0x0ef: TrimLastChar,
    0x0f0: Restore,
    0x0f1: Join.around(" AND THEN "),
    0x0f2: OrElse,
    0x0f3: Join.around(",", pfx="CURSOR "),
    0x0f4: Join.around(" OR ELSE "),
    0x0f5: CommaToCloseParan,
    0x0f6: Join.around(" EXTERNAL "),
    0x0f7: Wrap.inside("", "("),
    0x0f8: AssignSVar,
    0x0f9: Trap,
    0x0fa: AssignRVar,
    0x0fb: AssignIVar,
    0x0fc: Handler,
    0x0fd: Push.this("ENDTRAP", indent=-2),
    0x0fe: Push.this("ERR"),
















    0x110: Push.this("DELD-"),


    0x113: Push.this("OPEN"),
    0x114: Push.this("PI"),
    0x115: Push.this("PAGE"),

    0x117: Push.this("ERRTEXT$"),
    0x118: Push.this("CLOSE"),
    0x119: Join.around(" FILE "),
    0x11a: Push.this("CLOSE"),
    0x11b: Join.around(",", pfx="OPEN "),
    0x11c: Wrap.inside("CHAIN ", ""),
    0x11d: Join.around(","),
    0x11e: Wrap.inside("UNIT ", ""),
    0x11f: Push.this("KEY$"),
    0x120: Wrap.inside("FILE ", ""),
    0x121: Wrap.inside("MOUNT ", ""),
    0x122: PrefixOpen,
    0x123: Wrap.inside("", ",READ"),
    0x124: Wrap.inside("", ",WRITE"),
    0x125: Wrap.inside("", ",APPEND"),
    0x126: Join.around(",RANDOM "),
    0x127: Push.this("DIR"),
    0x128: Wrap.inside("DIR ", ""),
    0x129: Join.around(",", pfx="COPY "),
    0x12a: Join.suffix(","),
    0x12b: Join.around(",", pfx="POKE "),
    0x12c: Join.suffix(","),
    0x12d: Wrap.inside("SYS ", ""),
    0x12e: Push.this("UNIT$"),
    0x12f: Join.around(" UNTIL ", pfx="REPEAT "),
    0x130: Wrap.inside("STOP ", ""),
    0x131: Wrap.inside("TIME ", ""),
    0x132: Push.this("REPORT"),

    0x134: EndOfInput,
    0x135: Wrap.inside("PASS ", ""),
    0x136: Push.this("MOUNT"),
    0x137: Join.around(",", pfx="PASS "),
    0x138: Wrap.inside("END ", ""),
    0x139: Wrap.inside("DELETE ", ""),
    0x13a: Wrap.inside("RANDOMIZE ", ""),
    0x13b: Push.this("RANDOMIZE"),
    0x13c: Wrap.inside("REPORT ", ""),
    0x13d: Join.around(",", pfx="CREATE "),
    0x13e: Join.around(",", pfx="RENAME "),
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
                self.indent += y.INDENT
                self.indent_this += y.INDENT_THIS
                n += 1
            elif cls:
                y = self.add_field("t%02d" % n, cls)
                self.indent += y.INDENT
                self.indent_this += y.INDENT_THIS
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

class Csum(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            checksum_=ov.Le16,
        )

class ProcHead(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            magic_=ov.Octet,
            code_=ov.Le16,
            narg_=ov.Octet,
            vertical=True,
            more=True,
        )
        if self.narg.val > 0:
            self.add_field("arguments", ov.Array(self.narg.val, ov.Octet, vertical=True))
        self.add_field("term", ov.Octet)
        self.done()

class Procedure(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            name_=ov.PascalString,
            head_=ov.Le16,
        )

class PackProcs(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            more=True,
            vertical=True,
        )

        ptr = lo
        n = 0
        while tree.this[ptr]:
            n += 1
            ptr = Procedure(tree, ptr).hi
        self.add_field("procedures", ov.Array(n, Procedure, vertical=True))
        self.add_field("term", ov.Octet)
        self.done()

class Package(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            name_=ov.PascalString,
            tbl_=ov.Le16,
            init_=ov.Le16,
        )


class Module(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            map_=ov.Octet,
            end_=ov.Le16,
            signal_=ov.Le16,
            vertical=True,
            more=True,
        )
        n = 0
        ptr = self.hi
        while tree.this[ptr] and ptr < len(tree.this) - 1:
            n += 1
            ptr += tree.this[ptr] + 5
        self.add_field("packages", ov.Array(n, Package, vertical=True))
        self.add_field("term", ov.Octet)
        self.done()

class EndOfModule(ov.Dump):
    ''' ... '''

class ModuleHeader(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            id_=ov.Octet,
            map_=ov.Octet,
            base_=ov.Le16,
            mod_=Module,
            vertical=True,
        )
        offset = self.mod.lo - self.base.val
        EndOfModule(tree, self.mod.end.val + offset, width=1).insert()
        for pkg in self.mod.packages:
            self.tree.this.add_note("C64-UNICOMAL-PKG-" + pkg.name.txt)
            pp = PackProcs(tree, pkg.tbl.val + offset).insert()
            for ph in pp.procedures:
                ProcHead(tree, ph.head.val + offset).insert()

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
        if this[3] != 0x00:
            return


        super().__init__(this)
        this.add_note("C64-UNICOMAL")
        hdr = Hdr(self, 0).insert()

        if 2 + hdr.hi + hdr.f03.val <= len(this):
            csum = Csum(self, hdr.hi + hdr.f03.val).insert()
        else:
            csum = None
        if csum and csum.hi < len(this) and this[csum.hi] == 0x01:
            ModuleHeader(self, csum.hi).insert()
            this.add_note("C64-UNICOMAL-PKG")
        if csum and csum.hi < len(this) and this[csum.hi] == 0x02:
            print(this, "UNICOMAL unknown payload", hex(this[csum.hi]))

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
                break
                raise
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

        self.add_interpretation(more=False)
