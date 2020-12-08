'''
   ANSI tape labels
   ----------------

   Implemented based on Ecma-13 .

'''

import html

class TapeLabel():
    ''' One tape label record '''

    template = '╰─╯╵╰──────────────────────────────────────────────────────────────────────────╯'

    def __init__(self, _this, block):
        self.block = block

    def render(self):
        ''' Render as ascii with allowance for out-of-range values '''
        t = ''
        for i in bytes(self.block):
            if 32 <= i <= 126:
                t += " "
            else:
                t += "%x" % (i >> 4)
        if t.replace(" ", ""):
            yield t
        t = ''
        for i in bytes(self.block):
            if 32 <= i <= 126:
                t += "%c" % i
            else:
                t += "%x" % (i & 0xf)
        yield t
        yield self.template

class TapeLabelVol1(TapeLabel):

    template = '╰─╯╵╰────╯╵╰───────────╯╰───────────╯╰────────────╯╰──────────────────────────╯╵'

    def __init__(self, this, block):
        super().__init__(this, block)
        this.add_note("Volume=" + block[4:10].decode("ASCII").strip())

class TapeLabelEov1(TapeLabel):

    template = '╰─╯╵╰───────────────╯╰────╯╰──╯╰──╯╰──╯╰╯╰────╯╰────╯╵╰────╯╰───────────╯╰─────╯'

class TapeLabelEov2(TapeLabel):

    template = '╰─╯╵╵╰───╯╰───╯╰─────────────────────────────────╯╰╯╰──────────────────────────╯'

class TapeLabelHdr1(TapeLabel):

    template = '╰─╯╵╰───────────────╯╰────╯╰──╯╰──╯╰──╯╰╯╰────╯╰────╯╵╰────╯╰───────────╯╰─────╯'

    def __init__(self, this, block):
        super().__init__(this, block)
        this.add_note("File=" + block[4:21].decode("ASCII").strip())

class TapeLabelHdr2(TapeLabel):
    template = '╰─╯╵╵╰───╯╰───╯╰─────────────────────────────────╯╰╯╰──────────────────────────╯'

class TapeLabelEof1(TapeLabel):
    template = '╰─╯╵╰───────────────╯╰────╯╰──╯╰──╯╰──╯╰╯╰────╯╰────╯╵╰────╯╰───────────╯╰─────╯'

class TapeLabelEof2(TapeLabel):
    template = '╰─╯╵╵╰───╯╰───╯╰─────────────────────────────────╯╰╯╰──────────────────────────╯'

ANSI_HEADERS = {
    b'VOL1': TapeLabelVol1,
    b'VOL': TapeLabel,
    b'UVL': TapeLabel,
    b'HDR1': TapeLabelHdr1,
    b'HDR2': TapeLabelHdr2,
    b'HDR': TapeLabel,
    b'UHL': TapeLabel,
    b'EOV1': TapeLabelEov1,
    b'EOV2': TapeLabelEov2,
    b'EOV': TapeLabel,
    b'EOF1': TapeLabelEof1,
    b'EOF2': TapeLabelEof2,
    b'EOF': TapeLabel,
    b'UTL': TapeLabel,
}

class AnsiTapeLabels():
    ''' ANSI Tape Labels '''

    def __init__(self, this):
        if not this.has_type("TAPE file"):
            return
        # print("?ANSI", this)
        self.parts = []
        for tour in range(2):
            if tour:
                this.add_type("ANSI Tape Label")
            for label in this.iterrecords():
                if len(label) != 80:
                    return
                label=label.tobytes()
                t = ANSI_HEADERS.get(label[:4])
                # \x01 allows for mistake on 30000544/0x58cd75c1
                if not t and label[3] in b'123456789\x01':
                    t = ANSI_HEADERS.get(label[:3])
                if not t:
                    print("ANSITAPELABEL", this, "Unknown label", label[:4])
                    return
                if tour:
                    self.parts.append(t(this, label))
        self.this = this
        this.add_interpretation(self, self.html_list)

    def html_list(self, fo, _this):
        ''' Render with a handy ruler '''
        fo.write("<H3>ANSI tape labels</H3>\n")
        fo.write("<pre>\n")
        fo.write("".join(["%01d" % (x // 10) for x in range(1,81)]) + "\n")
        fo.write("".join(["%01d" % (x % 10) for x in range(1,81)]) + "\n")
        fo.write("━" * 80 + "\n")
        for label in self.parts:
            for i in label.render():
                fo.write(html.escape(i) + "\n")
        fo.write("</pre>\n")
