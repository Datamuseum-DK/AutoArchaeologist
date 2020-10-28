'''
   RC7000/RC3600 COMAL SAVE files
   ------------------------------
'''

import struct

class ComalSyntax(Exception):
    ''' COMAL syntax error '''

TOPVAR = 218

COMAL_TOKEN = {
    0x0025: (0, "DIGITS", ),
    0x0026: (0, "RESET", ),
    0x0027: (0, "PROTECT", ),
    0x0028: (0, "LOWBOUND", ),
    0x0029: (0, "CONNECT", ),
    0x002a: (0, "RELEASE", ),
    0x002b: (0, "DELAY", ),
    0x002c: (0, "RENAME", ),
    0x002d: (1, "TAB", ),
    0x002e: (0, "PAGE", ),
    0x0030: (0, "CREATE", ),
    0x0031: (0, "DELETE", ),
    0x0032: (0, "OF", ),
    0x0033: (0, "ENDPROC", ),
    0x0034: (0, "EXEC", ),
    0x0035: (0, "PROC", ),
    0x0036: (0, "ENDCASE", ),
    0x0037: (0, "WHEN", ),
    0x0038: (0, "CASE", ),
    0x0039: (0, "ENDWHILE", ),
    0x003a: (0, "ENDIF", ),
    0x003b: (0, "UNTIL", ),
    0x003c: (0, "REPEAT", ),
    0x003d: (0, "WHILE", ),
    0x003e: (0, "ELSE", ),
    0x003f: (0, "DO", ),
    0x0041: (0, "NEW", ),
    0x0042: (0, "BYE", ),
    0x0043: (0, "SAVE", ),
    0x0044: (0, "ENTER", ),
    0x0045: (0, "CHAIN", ),
    0x0046: (0, "OPEN", ),
    0x0047: (0, "CLOSE", ),
    0x0049: (0, "RANDOMIZE", ),
    0x004a: (0, "GOTO", ),
    0x004b: (0, "GOSUB", ),
    0x004c: (0, "IF", ),
    0x004d: (0, "ON", ),
    0x004e: (0, "CALL", ),
    0x004f: (0, "STOP", ),
    0x0050: (0, "DEF", ),
    0x0051: (0, "END", ),
    0x0052: (0, "RETURN", ),
    0x0053: (0, "FOR", ),
    0x0054: (0, "NEXT", ),
    0x0055: (0, "DATA", ),
    0x0056: (0, "REM", ),
    0x0057: (0, "LET", ),
    0x0058: (0, "MAT", ),
    0x0059: (0, "DIM", ),
    0x005a: (0, "RESTORE", ),
    0x005b: (0, "INPUT", ),
    0x005c: (0, "PRINT", ),
    0x005d: (0, "READ", ),
    0x005e: (0, "WRITE", ),
    0x005f: (1, "ABS", ),
    0x0060: (1, "SGN", ),
    0x0061: (1, "RND", ),
    0x0062: (1, "SQR", ),
    0x0063: (1, "LOG", ),
    0x0064: (1, "EXP", ),
    0x0065: (1, "SIN", ),
    0x0066: (1, "COS", ),
    0x0067: (1, "ATN", ),
    0x0068: (1, "TAN", ),
    0x0069: (1, "DET", ),
    0x006a: (1, "EOF", ),
    0x006b: (1, "INT", ),
    0x006c: (1, "SYS", ),
    0x006d: (1, "ORD", ),
    0x006e: (1, "CHR", ),
    0x0079: (1, "LEN", ),
    0x007a: (0, "TRN", ),
    0x007b: (4, "INV", ),
    0x007c: (4, "ZER", ),
    0x007d: (4, "CON", ),
    0x007e: (4, "IDN", ),
    # 0x007f: (0, "CONL", ),
    # 0x0080: (0, "RUN", ),
    # 0x0081: (0, "LIST", ),
    # 0x0082: (0, "SIZE", ),
    # 0x0083: (0, "AUTO", ),
    # 0x0084: (0, "RENUMBER", ),
    # 0x0085: (0, "RUNL", ),
    # 0x0087: (0, "BATCH", ),
    # 0x0088: (0, "SCRATCH", ),
    # 0x0089: (0, "LOAD", ),
    # 0x008a: (0, "EOJ", ),
    # 0x008b: (0, "TIME", ),
    # 0x008d: (0, "PUNCH", ),
    # 0x0091: (0, "INIT", ),
    # 0x0092: (0, "LOCK", ),
    # 0x0093: (0, "USERS", ),
    # 0x0094: (0, "LOOKUP", ),
    # 0x0095: (0, "COPY", ),
    0x00de: (0, "FILE", ),
    0x00df: (0, "ESC", ),
    0x00e0: (0, "ERR", ),
    0x00e1: (0, "USING", ),
    0x00e3: (2, "OR", ),
    0x00e4: (0, "TO", ),
    0x00e6: (0, "STEP", ),
    0x00e7: (0, "THEN", ),
    0x00e8: (2, "AND", ),
    0x00ea: (1, "<>", ),
    0x00eb: (1, ">", ),
    0x00ec: (1, ">=", ),
    0x00ed: (1, "=", ),
    0x00ee: (1, "<=", ),
    0x00ef: (1, "<", ),
    0x00f0: (0, ";", ),
    0x00f1: (0, ",", ),
    0x00f2: (1, "(", ),
    0x00f3: (1, "(", ),
    0x00f6: (1, ")", ),
    0x00f7: (1, ")", ),
    0x00f8: (1, "-", ),
    0x00f9: (1, "+", ),
    0x00fa: (1, "/", ),
    0x00fb: (1, "*", ),
    0x00fc: (1, "^", ),
    0x00fd: (2, "MOD", ),
    0x00fe: (2, "DIV", ),
    0x00ff: (2, "NOT", ),
}

def get_token(n, flag=0):
    ''' Convert byte value to token, masked by flag '''
    token = COMAL_TOKEN.get(n)
    if token is None:
        return token
    if flag and not flag & token[0]:
        return None
    return token[1]

def number(b):
    ''' A floating point number (RCSL-43-GL-9698 2.5.1.1) '''
    i = struct.unpack(">L", bytes(b[:4]))[0]
    b.pop(0)
    b.pop(0)
    b.pop(0)
    b.pop(0)
    sign = -1 if i & (1<<31) else 1
    mantissa = (i & 0xffffff) / 2**24
    exponent = (i >> 24) & 0x07f
    value = sign * mantissa * 16**(exponent - 64)
    return "%g" % value

def string(b):
    ''' A String Constant '''
    assert b[0] == 0xe9
    b.pop(0)
    txt = '"'
    length = b.pop(0)
    for _j in range(length):
        char = b.pop(0)
        glyph = {
            0x22: "<34>",
            0x3c: "<60>",
            0x5b: "Æ",
            0x5c: "Ø",
            0x5d: "Å",
            0x7b: "æ",
            0x7c: "ø",
            0x7d: "å",
        }.get(char)
        if glyph:
            txt += glyph
        elif 32 <= char <= 126:
            txt += "%c" % char
        else:
            txt += "<%d>" % char
    return txt + '"'


class ComalStatement():
    ''' A single COMAL statement encode as byte sequence '''
    def __init__(self, up, lno, this):
        self.up = up
        self.lineno = lno
        self.this = this
        self.lvar = "[LVAR]"
        self.indent = 0
        self.outdent = 0

    def expect(self, stream, what):
        ''' Next byte should be token `what` '''
        tval = stream.pop(0)
        token = get_token(tval)
        if not token:
            raise ComalSyntax("Expected '%s' got 0x%02x'" % (str(what), tval))
        if isinstance(what, str) and token != what:
            raise ComalSyntax("Expected '%s' got '%s'" % (what, str(token)))
        if token not in what:
            raise ComalSyntax("Expected '%s' got '%s'" % (str(what), str(token)))
        yield token

    def peek(self, stream, what):
        ''' Peek at next byte and see if it is token `what` '''
        tval = stream[0]
        token = get_token(tval)
        if not token:
            return False
        if isinstance(what, str) and token != what:
            return False
        if token not in what:
            return False
        stream.pop(0)
        return True

    def expect_comment(self, stream):
        ''' comment '''
        t = ""
        while stream and stream[0] != 0xe2:
            t += "%c" % stream.pop(0)
        yield t

    def expect_expr(self, stream):
        ''' expr '''
        is_string = False
        parens = 0
        while stream:

            if stream[0] == 0xe2:
                break

            if not parens and get_token(stream[0]) == ")":
                break

            if stream[0] in (0x7f, 0x40,):
                yield from self.expect_number(stream)
                continue

            if 0x80 <= stream[0] <= TOPVAR:
                i = list(self.expect_var(stream))
                for j in i:
                    if '$' in j:
                        is_string = True
                yield from i
                continue

            if self.peek(stream, '('):
                parens += 1
                yield "("
                continue

            if self.peek(stream, ')'):
                assert parens > 0
                parens -= 1
                yield ")"
                continue

            if stream[0] == 0xe9:
                is_string = True
                yield string(stream)
                continue

            token = get_token(stream[0], 3)
            if token:
                yield token
                stream.pop(0)
                continue

            if is_string and self.peek(stream, ","):
                yield ","
                continue

            break

    def expect_file(self, stream):
        ''' FILE ( number [ , expr ] ) '''
        yield from self.expect(stream, "FILE")
        yield from self.expect(stream, "(")
        yield from self.expect_number(stream)
        if self.peek(stream, ","):
            yield ","
            yield from self.expect_expr(stream)
        yield from self.expect(stream, ")")

    def expect_number(self, stream):
        ''' number '''
        if stream[0] == 0x40 and stream[1] == 0x00:
            stream.pop(0)
            stream.pop(0)
            yield "0"
        elif stream[0] == 0x7f:
            stream.pop(0)
            if len(stream) & 1:
                stream.pop(0)
            yield number(stream)
        else:
            assert False, "expect_number: " + bytes(stream).hex()

    def expect_stringlit(self, stream):
        ''' string '''
        yield string(stream)

    def expect_var(self, stream):
        ''' var '''
        var = stream.pop(0)
        assert 0x80 <= var <= TOPVAR, "Bad Var 0x%02x" % var
        assert var & 0x80, "VAR 0x%02x" % var
        if var == 0x80:
            yield self.lvar
        yield self.up.udas.variables[var & 0x7f].name
        if get_token(stream[0]) == "(":
            yield from self.expect(stream, "(")
            yield from self.expect_expr(stream)
            if get_token(stream[0]) == ",":
                yield from self.expect(stream, ",")
                yield from self.expect_expr(stream)
            yield from self.expect(stream, ")")

    def render_call(self, stream):
        ''' CALL expr [ , expr ] ... '''
        yield from self.expect_stringlit(stream)
        while self.peek(stream, ','):
            yield ","
            yield from self.expect_expr(stream)

    def render_case(self, stream):
        ''' CASE expr OF '''
        self.indent += 1
        yield from self.expect_expr(stream)
        yield from self.expect(stream, "OF")

    def render_close(self, stream):
        ''' CLOSE [ file ] '''
        if stream[0] != 0xe2:
            yield from self.expect_file(stream)

    def render_data(self, stream):
        ''' DATA expr [ , expr ] ... '''
        yield from self.expect_expr(stream)
        while self.peek(stream, ','):
            yield from self.expect_expr(stream)

    def render_dim(self, stream):
        ''' DIM var [ , var ] ... '''
        while stream and stream[0] != 0xe2:
            yield from self.expect_var(stream)
            if not self.peek(stream, ','):
                break
            yield ","

    def render_else(self, stream):
        ''' ELSE [ comment ] '''
        self.indent += 1
        self.outdent += 1
        stream.pop(0)
        stream.pop(0)
        yield ""

    def render_endcase(self, _stream):
        ''' ENDCASE [ comment ] '''
        self.outdent += 1
        yield ""

    def render_endif(self, stream):
        ''' ENDIF [ comment ] '''
        self.outdent += 1
        stream.pop(0)
        stream.pop(0)
        yield ""

    def render_endproc(self, stream):
        ''' ENDPROC [ comment ] '''
        self.outdent += 1
        stream.pop(0)
        stream.pop(0)
        yield ""

    def render_endwhile(self, stream):
        ''' ENDWHILE '''
        self.outdent += 1
        stream.pop(0)
        stream.pop(0)
        yield ""

    def render_exec(self, stream):
        ''' EXEC name '''
        yield from self.expect_var(stream)

    def render_for(self, stream):
        ''' FOR var = expr TO expr [ STEP expr ] '''
        self.indent += 1
        yield from self.expect_var(stream)
        yield from self.expect(stream, "=")
        yield from self.expect_expr(stream)
        yield from self.expect(stream, "TO")
        yield from self.expect_expr(stream)
        if stream[0] != 0xe2:
            yield from self.expect(stream, "STEP")
            yield from self.expect_expr(stream)

    def render_goto(self, stream):
        ''' GOTO lineno '''
        lno = stream.pop(0) << 8
        lno |= stream.pop(0)
        yield "%04d" % lno

    def render_if(self, stream):
        ''' if expr THEN [ statement ] '''
        yield from self.expect_expr(stream)
        yield from self.expect(stream, "THEN")
        if stream[0] == 0xe2:
            self.indent += 1
            return
        yield from self.statement(stream)

    def render_input(self, stream):
        ''' INPUT string , var [ , string , var ] ... '''
        if get_token(stream[0]) == "FILE":
            yield from self.expect_file(stream)
        while stream and stream[0] != 0xe2:
            if stream[0] == 0xe9:
                yield from self.expect_stringlit(stream)
                yield from self.expect(stream, ",")
            yield from self.expect_var(stream)
            if not stream or stream[0] == 0xe2:
                break
            yield from self.expect(stream, (",", ";",))

    def render_let(self, stream):
        ''' LET var = expr [ ; var = expr ] ... '''
        while stream and stream[0] != 0xe2:
            yield from self.expect_var(stream)
            yield from self.expect(stream, "=")
            yield from self.expect_expr(stream)
            if not stream or stream[0] == 0xe2:
                break
            yield from self.expect(stream, (";", ",",))

    def render_next(self, stream):
        ''' NEXT var '''
        self.outdent += 1
        stream.pop(0)
        stream.pop(0)
        yield ""

    def render_open(self, stream):
        ''' OPEN file_mode [ , ] expr '''
        yield from self.expect_file(stream)
        yield from self.expect_expr(stream)

    def render_proc(self, stream):
        ''' PROC name '''
        self.indent += 1
        yield from self.expect_var(stream)

    def render_print(self, stream):
        ''' PRINT [ file ] [ USING string . ] [expr] [ {,|;} expr ] ... [{,|;}]'''
        if get_token(stream[0]) == "FILE":
            yield from self.expect_file(stream)
        if self.peek(stream, "USING"):
            yield from self.expect_expr(stream)
            yield from self.expect(stream, (",", ";",))
        while stream and stream[0] != 0xe2:
            yield from self.expect_expr(stream)
            if stream and stream[0] != 0xe2:
                yield from self.expect(stream, (",", ";",))
            else:
                break

    def render_read(self, stream):
        ''' READ var [ , var ] ... '''
        if get_token(stream[0]) == "FILE":
            yield from self.expect_file(stream)
        yield from self.expect_var(stream)
        while self.peek(stream, ","):
            yield ","
            yield from self.expect_var(stream)

    def render_rem(self, stream):
        ''' REM comment '''
        yield from self.expect_comment(stream)

    def render_repeat(self, stream):
        ''' REPEAT [ comment ]'''
        self.indent = 1
        stream.pop(0)
        stream.pop(0)
        yield ""

    def render_reset(self, _stream):
        ''' RESET { ESC | ERR } '''
        yield ""

    def render_restore(self, stream):
        ''' RESET lineno '''
        lno = stream.pop(0) << 8
        lno |= stream.pop(0)
        if lno:
            yield "%04d" % lno

    def render_tab(self, stream):
        ''' TAB expr '''
        yield from self.expect_expr(stream)

    def render_until(self, stream):
        ''' UNTIL expr '''
        self.outdent = 1
        yield from self.expect_expr(stream)

    def render_when(self, stream):
        ''' WHEN expr [ , expr ] ... '''
        self.outdent = 1
        self.indent = 1
        yield from self.expect_expr(stream)
        while self.peek(stream, ","):
            yield ","
            yield from self.expect_expr(stream)

    def render_while(self, stream):
        ''' WHILE expr DO '''
        self.indent = 1
        yield from self.expect_expr(stream)
        stream.pop(0)
        stream.pop(0)

    def statement(self, stream):
        token = get_token(stream[0])
        if not token:
            return
        try:
            rfunc = getattr(self, "render_" + token.lower())
        except AttributeError:
            print("NO RENDER", token)
            return
        yield from self.expect(stream, token)
        yield from rfunc(stream)

    def render(self):
        stream = list(self.this[3:])
        tokens = list(self.statement(stream))
        txt = " ".join(tokens)
        if not stream or stream[0] == 0xe2:
            return txt
        return txt + "[" + bytes(stream).hex() + "]"

    def html_render(self):
        r = self.render()
        if r:
            yield r
        else:
            yield "[" + self.this[:3].hex() + " " + self.this[3:].hex() + "]"


class ComalUPAS():
    ''' program segment '''
    def __init__(self, up, this):
        self.up = up
        self.this = this
        this.add_type("RC7000_COMAL_SAVE.UPAS")
        self.statements = []
        offset = 66 * 2
        while offset < len(self.this):
            i = struct.unpack(">HB", self.this[offset:offset + 3])
            self.statements.append(
                ComalStatement(
                    self.up,
                    i[0],
                    self.this[offset:offset + i[1] * 2]
                )
            )
            offset += i[1] * 2
        if this[4] == 0xe9:
            self.filename = string(list(this[4:65*2]))
        else:
            self.filename = None

    def html_detailed(self, fo, _this):
        fo.write("<h3>UPAS Segment</h3>\n")
        fo.write("<pre>\n")

        if self.filename:
            fo.write("SAVE filename: " + self.filename + "\n\n")
        pfx = 0
        for i in self.statements:
            x = list(i.html_render())
            if i.outdent:
                pfx -= 1
            for j in x:
                fo.write(" %04d " % i.lineno + "  " * pfx + j + "\n")
            if i.indent:
                pfx += 1

        fo.write("</pre>\n")

class ComalVariable():
    ''' A COMAL variable '''
    def __init__(self, up, this):
        self.up = up
        self.this = this
        self.name = ""
        self.bits = 0
        for i in range(8):
            x = this[i]
            if i == 0 and x > 127:
                self.bits |= 1 << i
                x -= 128
            elif i == 1:
                if x & 1:
                    self.bits |= 1 << i
                x >>= 1
            if not x:
                break
            if 32 < x < 127:
                self.name += "%c" % x
            else:
                self.name += "{%d}" % x

        if self.bits & 2:
            self.name += "$"

        self.ptr = struct.unpack(">H", this[8:10])[0]

        # print("VAR", self.name, self.bits, self.ptr, this.hex())

    def html_render(self):
        return "0x%04x 0x%02x %s" % (self.ptr, self.bits, self.name)

class ComalUDAS():
    ''' Data segment '''
    def __init__(self, up, this):
        self.up = up
        self.this = this
        this.add_type("RC7000_COMAL_SAVE.UDAS")

        self.variables = []
        for offset in range(104*2, self.up.u_dvs * 2, 10):
            self.variables.append(ComalVariable(self.up, self.this[offset:offset + 10]))

    def html_detailed(self, fo, _this):
        fo.write("<h3>UDAS Segment</h3>\n")
        fo.write("<pre>\n")
        words = list(struct.unpack(">104H", self.this[:104*2]))

        for i in range(29):
            fo.write("    FN%c definition = 0x%04x\n" % (0x41 + i, words.pop(0)))

        def stack7(what):
            fo.write("    %s stack pointer = 0x%04x\n" % (what, words.pop(0)))
            for i in range(7):
                fo.write("      stack[%d] = 0x%04x\n" % (i, words.pop(0)))

        stack7("GOSUB-RETURN")

        fo.write("    FOR-NEXT stack pointer = 0x%04x\n" % words.pop(0))
        for i in range(7):
            fo.write("      Var# = 0x%04x\n" % words.pop(0))
            fo.write("      Loop Top = 0x%04x\n" % words.pop(0))
            for j in ("To", "Step"):
                x = words.pop(0)
                y = words.pop(0)
                z = number([x >> 8, x & 0xff, y >> 8, y & 0xff])
                fo.write("      %s Val = %s" % (j, z))
                fo.write("   (0x%04x%04x)\n" % (x, y))

        stack7("REPEAT-UNTIL")
        stack7("WHILE-ENDWHILE")
        stack7("IF-ELSE")
        assert not words
        fo.write("Variables:\n")
        for i in self.variables:
            fo.write("    %s\n" % i.html_render())
        # XXX values
        fo.write("</pre>\n")


class ComalSaveFile():
    ''' A RC7000 COMAL SAVE file '''
    def __init__(self, this):
        if len(this) < 64 or this[:2] not in (b'SV', b'N2', b'RO'):
            return
        if this.has_type("RC7000_COMAL_SAVE"):
            return

        self.head = struct.unpack(">BBHH", this[0:6])

        offset = 6 + 2 * sum(self.head[2:])
        self.uvars =  (
            ("dvs", "Start på savede variabel indhold (word adr)"),
            ("nds", "Address på næste prog.sætning (word adr)"),
            ("cps", "Address på curr prog.sætning (word adr)"),
            ("tll", "Page størrelse"),
            ("tts", "TAP størrelse"),
            ("ran", "Random tal"),
            ("cdl", "Current DATA sætning ptr"),
            ("cdb", "Current DATA byte ptr"),
            ("esa", "ON ESE (word adr)"),
            ("era", "ON ERR (word adr)"),
            ("cas", "CASE dybde"),
            ("las", "last (-1)"),
        )

        for b, _c in self.uvars:
            i = struct.unpack(">H", this[offset:offset + 2])
            setattr(self, "u_" + b, i[0])
            offset += 2

        if self.u_las != 0xffff:
            return

        this = this.slice(0, offset)
        self.this = this
        this.add_type("RC7000_COMAL_SAVE")

        offset = 6
        length = self.head[2] * 2
        self.upas = ComalUPAS(self, this.slice(offset, length))

        offset += length
        length = self.head[3] * 2
        self.udas = ComalUDAS(self, this.slice(offset, length))

        this.add_interpretation(self, self.upas.html_detailed)
        this.add_interpretation(self, self.udas.html_detailed)
        this.add_interpretation(self, self.html_detailed)

    def html_detailed(self, fo, _this):
        fo.write("<h3>Wrapper</h3>\n")
        fo.write("<pre>\n")

        words = struct.unpack(">BBHH", self.this[0:6])
        fo.write(".magic = 0x%02x%02x\n" % (words[0], words[1]))
        fo.write(".u_pas = 0x%04x  // Length of UPAS in words\n" % words[2])
        fo.write(".u_das = 0x%04x  // Length of UDAS in words\n" % words[3])
        for b, c in self.uvars:
            i = getattr(self, "u_" + b)
            fo.write(".u_%s = 0x%04x  // %s\n" % (b, i, c))

        fo.write("</pre>\n")
