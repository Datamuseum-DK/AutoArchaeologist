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

from .c64_unicomal_tables import *

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

class Bogon(Exception):
    ''' ... '''

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
        if self.size.val > 3:
            self.add_field("body", self.size.val - 3)
        self.stack = []
        self.stream = []
        self.listed = ""
        self.indent = 0
        self.done()

    def list(self):
        if not hasattr(self, "body"):
            return

        self.stream = list(x for x in self.body)
        self.stack = [""]


        roadblock = None
        while self.stream:
            roadblock = None
            b = self.stream.pop(0)
            if b == 0xff:
                if not self.stream:
                    yield "   ! missing aux token"
                    break
                b += 1 + self.stream.pop(0)
            stackop, extra, tok = DISPATCH.get(b, (None, None, None))
            if stackop is None:
                yield "   ! unknown token 0x%03x" % b
                break
            yield "   * %02x (%02x, %x, %02x) # %s" % (b, stackop, extra, tok, str(TOKENS[tok]))
            mname = "stackop_%02x" % stackop
            method = getattr(self, mname, None)
            if not method:
                yield "   ! " + mname + " not implemented"
                roadblock = mname
                break
            try:
                method(tok)
            except Exception as err:
                yield "   ! stackop_%02x raised %s %s" % (stackop, err.__class__.__name__, str(err))
                roadblock = mname
                break

            for _i in range(extra):
                if self.stream:
                    yield "   + %02x" % self.stream.pop(0)
                else:
                    yield "   ! missing extra"

            yield "   Stack: [" + "|".join(str(x) for x in self.stack) + "]"
            yield "   Stream = [" + bytes(self.stream).hex() + "]"

        if self.stream:
            self.stack.append("Residual=" + bytes(self.stream).hex())

        if roadblock:
            self.stack.append("Roadblock=" + roadblock)

        if self.stack[:1] == [""]:
            self.stack.pop(0)

        self.listed = "".join(self.stack)
        yield " LISTED: " + self.listed
        if self.indent:
            yield " INDENT: 0x%02x" % self.indent

        while self.stream:
            b = self.stream.pop(0)
            yield "   ? %02x" % b
            break

    def render(self):
        yield from super().render()
        yield str(self.lineno)
        yield from self.list()
        yield ""

    def stackop_00(self, tok):
        ''' NoOp '''

    def stackop_01(self, tok):
        ''' End of line comment '''
        if self.stack[-1][-1:] not in ('', ' '):
            self.stack_append(' ')
        self.stack_append(TOKENS[tok])
        while self.stream:
            self.stack_append(decode_char(self.tree, self.stream.pop(0), quote=False))

    def stackop_02(self, tok):
        ''' Constant '''
        if tok == 0:
            e = self.stream.pop(0)
            mant = self.stream.pop(0) << 24
            mant |= self.stream.pop(0) << 16
            mant |= self.stream.pop(0) << 8
            mant |= self.stream.pop(0)
            if e == 0:
                real = 0
            elif mant & (1<<31):
                real = -mant * 2 ** (e - 128 - 32)
            else:
                mant |= (1<<31)
                real = mant * 2 ** (e - 128 - 32)
            x = "%g" % real
            if x[:2] == "0.":
                x = x[1:]
            self.stack.append(x)
        elif tok == 1:
            v = self.stream.pop(0) << 8
            v |= self.stream.pop(0)
            if v & (1<<15):
                v -= 1<<16
            self.stack.append('%d' % v)
        elif tok == 2:
            l = self.stream.pop(0)
            txt = "".join(decode_char(self.tree, self.stream.pop(0)) for x in range(l))
            self.stack.append('"' + txt + '"')
        elif tok == 3:
            v = self.stream.pop(0)
            self.stack.append('%d' % v)
        elif tok == 4:
            v = self.stream.pop(0) << 8
            v |= self.stream.pop(0)
            if v < 0x100:
                self.stack.append('$%02x' % v)
            else:
                self.stack.append('$%04x' % v)
        elif tok == 5:
            v = self.stream.pop(0)
            self.stack.append('"' + decode_char(self.tree, v) + '"')
        elif tok == 6:
            v = self.stream.pop(0) << 8
            v |= self.stream.pop(0)
            if v < 0x100:
                self.stack.append('%' + bin((1<<8)|v)[3:])
            else:
                self.stack.append('%' + bin((1<<16)|v)[3:])
        else:
            raise Bogon()

    def stackop_04(self, tok):
        ''' Indent2_XXX_PushTok_AppendSpace_StringVar '''
        self.indent |= 2
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.stackop_05(2)
        self.stack_join()

    def stackop_05(self, tok):
        ''' Name '''
        idx = self.stream.pop(0)
        idx |= self.stream.pop(0) << 8
        if idx == 0xffff:
            return
        v = self.tree.vars.get(idx)
        if v:
            self.stack_push(v.varname)
        else:
            self.stack_push("VAR[0x%04x]" % idx)
        if tok == 1:
            self.stack_append("#")
        elif tok == 2:
            self.stack_append("$")

    def stackop_07(self, _tok):
        ''' RealName '''
        self.stackop_05(0)

    def stackop_06(self, tok):
        ''' AppendSpace_PushTok_Join '''
        self.stack_append(' ')
        self.stack_push(TOKENS[tok])
        self.stack_join()

    def stackop_08(self, tok):
        ''' VarReal_PushTok_Join '''
        self.stackop_05(0)
        self.stack_push(TOKENS[tok])
        self.stack_join()

    def stackop_09(self, tok):
        ''' VarInt_PushTok_Join '''
        self.stackop_05(1)
        self.stack_push(TOKENS[tok])
        self.stack_join()

    def stackop_0a(self, tok):
        ''' VarString_PushTok_Join '''
        self.stackop_05(2)
        self.stack_push(TOKENS[tok])
        self.stack_join()

    def stackop_0b(self, tok):
        ''' Join_PushTok_Join '''
        self.stack_join()
        self.stack_push(TOKENS[tok])
        self.stack_join()

    def stackop_0c(self, tok):
        ''' PushTok_Swap_Join '''
        self.stack_push(TOKENS[tok])
        self.stack_swap()
        self.stack_join()

    def stackop_0d(self, tok):
        ''' PushTok_Swap_Join_Join '''
        self.stack_push(TOKENS[tok])
        self.stack_swap()
        self.stack_join()
        self.stack_join()

    def stackop_0e(self, tok):
        ''' PushTok_AppendSpace_PrependSpace_Swap_Join_Join '''
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.stack[-1] = " " + self.stack[-1]
        self.stack_swap()
        self.stack_join()
        self.stack_join()

    def stackop_0f(self, tok):
        ''' PushTok_AppendSpace_Swap_Join '''
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.stack_swap()
        self.stack_join()

    def stackop_10(self, tok):
        ''' PushTok_AppendSpace_Swap_Join_Join '''
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.stack_swap()
        self.stack_join()
        self.stack_join()

    def stackop_11(self, tok):
        ''' PushTok '''
        self.stack_push(TOKENS[tok])

    def stackop_12(self, tok):
        ''' PushTok_Swap_Join_AppendClose '''
        self.stack_push(TOKENS[tok])
        self.stack_swap()
        self.stack_join()
        self.stack_append(')')

    def stackop_13(self, tok):
        ''' PushTok_AppendOpen_Swap_Join_AppendClose '''
        self.stack_push(TOKENS[tok])
        self.stack_append('(')
        self.stack_swap()
        self.stack_join()
        self.stack_append(')')

    def stackop_14(self, tok):
        ''' PushTok_AppendDollar_AppendOpen_Swap_Join_AppendClose '''
        self.stackop_3c(tok)
        self.stack_append('(')
        self.stack_swap()
        self.stack_join()
        self.stack_append(')')

    def stackop_15(self, tok):
        ''' PushTok_AppendSpace '''
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')

    def stackop_16(self, tok):
        ''' PushTok_AppendSpace_Indent2 '''
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.indent |= 2

    def stackop_17(self, tok):
        ''' PushTok_AppendSpace_Indent3 '''
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.indent |= 3

    def stackop_18(self, tok):
        ''' PushTok_AppendSpace_Indent1 '''
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.indent |= 1

    def stackop_19(self, _tok):
        ''' TrimLast '''
        self.stack[-1] = self.stack[-1][:-1]

    def stackop_1a(self, tok):
        ''' PushTok_AppendSpace_Swap_Join_Join_AppendColon_AppendSpace '''
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.stack_swap()
        self.stack_join()
        self.stack_join()
        self.stack_append(': ')

    def stackop_1b(self, tok):
        ''' PushTok_AppendOpen_Swap_Join_AppendClose_Join '''
        self.stack_push(TOKENS[tok])
        self.stack_append('(')
        self.stack_swap()
        self.stack_join()
        self.stack_append(')')
        self.stack_join()

    def stackop_1c(self, tok):
        ''' Join_Indent4_AppendSpace_PushTok_Join_AppendSpace '''
        self.stack_join()
        self.stackop_20(tok)

    def stackop_1d(self, tok):
        ''' TrimLast_PushTok_Join '''
        self.stack[-1] = self.stack[-1][:-1]
        self.stack_push(TOKENS[tok])
        self.stack_join()

    def stackop_1e(self, tok):
        ''' PushTok_Join '''
        self.stack_push(TOKENS[tok])
        self.stack_join()

    def stackop_1f(self, tok):
        ''' Indent1_AppendSpace_PushTok_Join '''
        self.indent |= 1
        self.stack_append(' ')
        self.stack_push(TOKENS[tok])
        self.stack_join()

    def stackop_20(self, tok):
        ''' Indent4_AppendSpace_PushTok_Join_AppendSpace '''
        self.indent |= 4
        self.stack_append(' ')
        self.stack_push(TOKENS[tok])
        self.stack_join()
        self.stack_append(' ')

    def stackop_23(self, tok):
        ''' Indent2_XXX_PushTok_AppendSpace_RealVar '''
        self.indent |= 2
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.stackop_05(0)
        self.stack_join()

    def stackop_24(self, tok):
        ''' Indent2_XXX_PushTok_AppendSpace_IntVar '''
        self.indent |= 2
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.stackop_05(1)
        self.stack_join()

    def stackop_25(self, _tok):
        ''' ... '''
        # more if 0x08 & 0xc7d8 ?
        self.stackop_05(0)
        self.stack_append('(')

    def stackop_26(self, tok):
        self.indent = 0x10
        if self.stack[-1][-1] == ',':
            self.stack[-1] = self.stack[-1][:-1] + ")"
        else:
            self.stack[-1] = self.stack[-1][:-1]
        self.stack_append(' ')
        self.stack_push(TOKENS[tok])
        self.stack_join()
        self.stack_append(' ')

    def stackop_27(self, tok):
        ''' PushTok_AppendSpace_VarReal_Join '''
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.stackop_05(0)
        self.stack_join()

    def stackop_28(self, tok):
        ''' PushTok_AppendSpace_VarInt_Join '''
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.stackop_05(1)
        self.stack_join()

    def stackop_29(self, tok):
        ''' DIM-magic
                StackOp_PushTok_AppendSpace_Swap_Join_Join_
            or
                StackOp_PushTok_AppendSpace_PrependSpace_Swap_Join_Join_
        '''
        if self.stack[-2][-1] == '(':
            self.stack[-2] = self.stack[-2][:-1]

        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.stack_prepend(' ')
        self.stack_swap()
        self.stack_join()
        self.stack_join()

    def stackop_2a(self, tok):
        ''' Join_AppendColon_PushTok '''
        self.stack_join()
        self.stack_append(':')
        self.stack_push(TOKENS[tok])

    def stackop_2c(self, _tok):
        ''' DataJoin '''
        while self.stack[-2] != "DATA ":
            x = self.stack.pop(-1)
            self.stack[-1] += "," + x
        self.stack_join()

    def stackop_2d(self, tok):
        ''' VarAssign '''
        self.stackop_05(tok)
        self.stack_push(TOKENS[0x68])
        self.stack_join()
        self.stack_swap()
        self.stack_join()

    def stackop_2f(self, tok):
        ''' Join_Indent1_AppendSpace_PushTok_Join '''
        self.stack_join()
        self.stackop_1f(tok)

    def stackop_31(self, tok):
        ''' PrependComma_Join_PushTok_AppendSpace_Swap_Join_Join_AppendColon_AppendSpace '''
        self.stack_prepend(',')
        self.stack_join()
        self.stackop_1a(tok)

    def stackop_32(self, tok):
        ''' PrependComma_Join_PushTok_AppendSpace_Swap_Join '''
        self.stack_prepend(',')
        self.stack_join()
        self.stackop_0f(tok)

    def stackop_3a(self, tok):
        ''' Indent8_VarReal_PushTok_Join '''
        self.indent |= 8
        self.stackop_08(tok)

    def stackop_3b(self, _tok):
        ''' Join_AppendColon_AppendSpace '''
        self.stack_join()
        self.stack_append(': ')

    def stackop_3c(self, tok):
        ''' PushTok_AppendDollar '''
        self.stack_push(TOKENS[tok])
        self.stack_append('$')

    def stackop_3e(self, tok):
        ''' PrependComma_Join_PushTok_AppendSpace_Swap_Join_AppendComma '''
        self.stack_prepend(',')
        self.stack_join()
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.stack_swap()
        self.stack_join()
        self.stack_append(',')

    def stackop_39(self, tok):
        ''' EndProcFunc '''
        self.stream.pop(0)
        self.stream.pop(0)
        if self.stack[-1][-1] == ',':
            self.stack[-1] = self.stack[-1][:-1] + ")"
        else:
            self.stack[-1] = self.stack[-1][:-1]
        self.stack_append(' ')
        self.stack_push(TOKENS[tok])
        self.stack_join()

    def stackop_21(self, tok):
        self.procfunc(tok, 0)

    def stackop_22(self, tok):
        self.procfunc(tok, 1)

    def stackop_03(self, tok):
        self.procfunc(tok, 2)

    def modtyp(self, mod, typ):

        if mod == 0:
            self.stream.pop(0)
            self.stackop_05(typ)
            self.stack_join()
            self.stack_append(',')
        elif mod == 1:
            self.stream.pop(0)
            self.stackop_05(typ)
            self.stack_prepend('REF ')
            self.stack_join()
            self.stack_append(',')
        elif mod == 2:
            self.stream.pop(0)
            d = self.stream.pop(0)
            self.stackop_05(typ)
            self.stack_append('(' + ',' * (d - 1) + ')')
            self.stack_join()
            self.stack_append(',')
        elif mod == 3:
            self.stream.pop(0)
            d = self.stream.pop(0)
            self.stackop_05(typ)
            self.stack_prepend('REF ')
            self.stack_append('(' + ',' * (d - 1) + ')')
            self.stack_join()
            self.stack_append(',')
        else:
            raise Bogon()

    def procfunc(self, tok, ret):
        ''' ProcFuncReal '''
        self.indent |= 1
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.stackop_05(ret)
        self.stream.pop(0)
        self.stream.pop(0)
        self.stream.pop(0)
        self.stream.pop(0)
        self.stream.pop(0)
        self.stack_join()
        self.stack_append('(')
        while True:
            x = self.stream[0]
            if x >= 0x7e:
                return
            if x < 0x72:
                raise Bogon()
            typ = (x - 0x72) % 3
            mod = (x - 0x72) // 3
            self.modtyp(mod, typ)

    def stackop_2e(self, tok):
        ''' ... '''
        self.stackop_0e(tok)
        self.stackop_0f(0x3d)

    def stackop_33(self, tok):
        ''' ImportMagic '''
        self.stack_push(TOKENS[tok])
        self.stack_append(' ')
        self.stream.pop(0)
        self.stream.pop(0)
        while self.stream:
            x = self.stream[0]
            if x >= 0x7e:
                return
            if x < 0x72:
                raise Bogon()
            typ = (x - 0x72) % 3
            mod = (x - 0x72) // 3
            self.modtyp(mod, typ)

    def stackop_36(self, tok):
        ''' Exec '''
        ndim = self.stream.pop(0)
        self.stackop_05(tok)
        self.stack_append('(' + ',' * (ndim - 1) + ')')

    def stackop_3d(self, _tok):
        ''' TrimLast_AppendClose_AppendOpen '''
        self.stack[-1] = self.stack[-1][:-1]
        self.stack_append(')(')

    def stack_push(self, txt):
        if txt is None:
            txt = ""
        self.stack.append(txt)

    def stack_prepend(self, txt):
        self.stack[-1] = txt + self.stack[-1]

    def stack_append(self, txt):
        self.stack[-1] += txt

    def stack_swap(self):
        self.stack.append(self.stack.pop(-2))

    def stack_join(self):
        x = self.stack.pop(-1)
        y = self.stack.pop(-1)
        self.stack.append(y + x)

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
            fsum = (sum(this[:hdr.hi + hdr.f03.val]) & 0xffff) ^ 0xaaaa
            if fsum != csum.checksum.val:
                print(
                    this,
                    "CSUM",
                    "%04x" % fsum,
                    "%04x" % csum.checksum.val,
                    "%04x" % (csum.checksum.val ^ fsum),
                    fsum == csum.checksum.val,
                )
                this.add_note("C64-UNICOMAL-CSUMERR")
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
        self.stmt = []
        while ptr < hdr.hi + hdr.f02.val:
            try:
                y = Statement(self, ptr)
            except Exception as err:
                print(this, "BAD STMT", hex(adr), err)
                break
            if y.size.val == 0:
                break
            y.insert()
            for _x in y.list():
                # This parses the bytecode
                continue
            self.stmt.append(y)
            ptr += y.size.val

        with self.this.add_utf8_interpretation("COMAL80") as file:
            for j in self.list():
                file.write(j + "\n")

        with open("/tmp/C64Comal/" + this.digest + ".cml", "wb") as file:
            file.write(bytes(this))

        with open("/tmp/C64Comal/" + this.digest + ".lst", "w", encoding="utf8") as file:
            for j in self.list():
                file.write(j + "\n")

        self.add_interpretation(more=True)

    def list(self):
        ''' List the COMAL program '''
        indent = 0
        for i in self.stmt:
            if i.indent & 2:
                indent -= 2
            if i.indent & 8:
                xi = 1
            else:
                xi = 1 + indent
            yield (str(i.lineno) + " " * xi + i.listed).rstrip()
            if i.indent & 1:
                indent += 2
            indent = max(0, indent)
