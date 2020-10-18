'''
   GIER Text / Flexowriter text
   ----------------------------

   See: https://datamuseum.dk/wiki/GIER/Flexowriter

   We reject if there is too many parity errors or non-printable characters.

'''

GIER_GLYPH = {
    1:   ('1', '∨',),
    2:   ('2', '\u2a2f',),
    3:   ('3', '/',),
    4:   ('4', '=',),
    5:   ('5', ';',),
    6:   ('6', '[',),
    7:   ('7', ']',),
    8:   ('8', '(',),
    9:   ('9', ')',),
    13:  ('å', 'Å',),
    14:  ('_', '|',),
    16:  ('0', '∧',),
    17:  ('<', '>',),
    18:  ('s', 'S',),
    19:  ('t', 'T',),
    20:  ('u', 'U',),
    21:  ('v', 'V',),
    22:  ('w', 'W',),
    23:  ('x', 'X',),
    24:  ('y', 'Y',),
    25:  ('z', 'Z',),
    27:  (',', '10',),
    32:  ('-', '+',),
    33:  ('j', 'J',),
    34:  ('k', 'K',),
    35:  ('l', 'L',),
    36:  ('m', 'M',),
    37:  ('n', 'N',),
    38:  ('o', 'O',),
    39:  ('p', 'P',),
    40:  ('q', 'Q',),
    41:  ('r', 'R',),
    43:  ('ø', 'Ø',),
    48:  ('æ', 'Æ',),
    49:  ('a', 'A',),
    50:  ('b', 'B',),
    51:  ('c', 'C',),
    52:  ('d', 'D',),
    53:  ('e', 'E',),
    54:  ('f', 'F',),
    55:  ('g', 'G',),
    56:  ('h', 'H',),
    57:  ('i', 'I',),
    59:  ('.', ':',),
}

GIER_CONTROL_SPACE = 0
GIER_CONTROL_STOP = 11
GIER_CONTROL_END = 12
GIER_CONTROL_CLEAR = 28
GIER_CONTROL_RED = 29
GIER_CONTROL_TAB = 30
GIER_CONTROL_PUNCH_OFF = 31
GIER_CONTROL_PUNCH_ON = 44
GIER_CONTROL_LOWER = 58
GIER_CONTROL_UPPER = 60
GIER_CONTROL_SUM = 61
GIER_CONTROL_BLACK = 62
GIER_CONTROL_TAPE_FEED = 63
GIER_CONTROL_CR = 64
GIER_CONTROL_FORM_FEED = 72
GIER_CONTROL_TAPE_FEED_CR = 127

GIER_CONTROL = {
    GIER_CONTROL_SPACE: "space",
    GIER_CONTROL_STOP: "stop",
    GIER_CONTROL_END: "end",
    GIER_CONTROL_CLEAR: "clear",
    GIER_CONTROL_RED: "red",
    GIER_CONTROL_TAB: "tab",
    GIER_CONTROL_PUNCH_OFF: "punch_off",
    GIER_CONTROL_PUNCH_ON: "punch_on",
    GIER_CONTROL_LOWER: "lower",
    GIER_CONTROL_UPPER: "upper",
    GIER_CONTROL_SUM: "sum",
    GIER_CONTROL_BLACK: "black",
    GIER_CONTROL_TAPE_FEED: "tape_feed",
    GIER_CONTROL_CR: "cr",
    GIER_CONTROL_FORM_FEED: "form_feed",
    GIER_CONTROL_TAPE_FEED_CR: "tape_feed_cr",
}

def parity(x):
    ''' Calculate the parity of a number '''
    return bin(x).count('1') & 1

class GIER_Text():

    ''' GIER Text artifacts '''

    def __init__(self, this):
        self.this = this
        self.page_len = {}
        self.page_width = {}

        self.svgf = None
        self.nsvg = 0
        self.svg_files = []

        bad = 0
        bads = set()
        ctrl = 0
        non_zero = 0
        parities = [0, 0]
        was_sum = False
        for i in this:

            if not i:
                continue
            non_zero += 1

            parities[parity(i)] += 1

            if was_sum:
                was_sum = False
                continue

            j = (i & 0x0f) | ((i & 0xe0)>>1)
            if j == GIER_CONTROL_SUM:
                was_sum = True
            if j in GIER_CONTROL:
                ctrl += 1
            elif j not in GIER_GLYPH:
                bad += 1
                bads.add(j)

        if not non_zero:
            return

        badness = 100 * bad / non_zero
        parityerrors = 100 * parities[0] / non_zero

        if badness > 1:
            # print("GIERTEXT", this, "Too many bad:", bad, "%.1f%%" % badness)
            return

        this.add_note("Gier Text")

        if parities[0]:
            this.add_note("Parity Errors")
            print("GIERTEXT", this, "Parity errors", parities[0], "%.1f%%" % parityerrors)

        if bad:
            this.add_note("Bad Chars")
            print("GIERTEXT", this, "BAD chars", bad, "%.1f%%" % badness)
            print("GIERTEXT", this, "BAD chars:", ["%d" % j for j in sorted(bads)])
        this.add_note("Gier Text")

        if parities[0]:
            this.add_comment(
                "%d parity errors (%.1f%%)" % (parities[0], parityerrors)
            )
            this.add_comment("Parity errors are marked in blue.")

        self.txt = list(self.render())

        # find page sizes
        for page, line, col, _red, _glyph in self.txt:
            if page not in self.page_len:
                self.page_len[page] = 0
                self.page_width[page] = 0
            self.page_len[page] = max(self.page_len[page], line)
            self.page_width[page] = max(self.page_width[page], col)

        this.add_interpretation(self, self.html_interpretation)


    def open_svg(self):
        ''' Open next SVG file, write header '''
        fn = self.this.top.filename_for(self.this, suf=".%d.svg" % self.nsvg)
        self.svg_files.append(fn)
        fn = self.this.top.html_dir + "/" + fn
        self.svgf = open(fn, "w")
        self.nsvg += 1
        self.svgf.write('<svg viewBox="0 0')
        #self.svgf.write(' %d' % (self.page_width[self.nsvg] + 1))
        self.svgf.write(' %d' % (80 + 1))
        self.svgf.write(' %d' % (self.page_len[self.nsvg] *2 + 4))
        self.svgf.write('" xmlns="http://www.w3.org/2000/svg">\n')
        self.svgf.write('  <style>\n')
        self.svgf.write('    text {\n')
        self.svgf.write('        font-family: Consolas, Monaco, Courier, monospace;\n')
        self.svgf.write('        font-size: 1.8px;\n')
        self.svgf.write('    }\n')
        self.svgf.write('    .e {\n')
        self.svgf.write('        fill: purple;\n')
        self.svgf.write('        font-size: 1.2px;\n')
        self.svgf.write('    }\n')
        self.svgf.write('    .p {\n')
        self.svgf.write('        fill: blue;\n')
        self.svgf.write('    }\n')
        self.svgf.write('    .r {\n')
        self.svgf.write('        fill: crimson;\n')
        self.svgf.write('    }\n')
        self.svgf.write('    .b10 {\n')
        self.svgf.write('        font-size: 1px;\n')
        self.svgf.write('    }\n')
        self.svgf.write('    .r10 {\n')
        self.svgf.write('        fill: red;\n')
        self.svgf.write('        font-size: 1px;\n')
        self.svgf.write('    }\n')
        self.svgf.write('    .p10 {\n')
        self.svgf.write('        fill: blue;\n')
        self.svgf.write('        font-size: 1px;\n')
        self.svgf.write('    }\n')
        self.svgf.write('  </style>\n')

    def close_svg(self):
        ''' Close SVG file '''
        self.svgf.write('</svg>\n')

    def make_svgs(self):
        ''' Render coordinate list as SVG '''
        self.open_svg()
        for page, line, col, red, glyph in self.txt:
            col = 1 + col
            line = 2 + line * 2
            if page > self.nsvg:
                self.close_svg()
                self.open_svg()
                page = self.nsvg
            self.svgf.write('<text x="%d" y="%d"' % (col, line))
            if glyph == "<":
                glyph = "&lt;"
            if glyph == "10":
                self.svgf.write(' class="%s10"' % "brep"[red])
            elif red:
                self.svgf.write(' class="%s"' % "brep"[red])
            self.svgf.write('>%s</text>\n' % glyph)

        self.close_svg()

    def render(self):
        ''' Produce coordinate list of (page, line, col, color, glyph) '''

        case = 0
        red = 0
        page = 1
        line = 0
        col = 0
        was_sum = False
        # XXX: Calculate the checksum

        for i in self.this:
            j = (i & 0x0f) | ((i & 0xe0)>>1)

            if was_sum:
                x = "[%03d]" % j
                for y in x:
                    yield page, line, col, 2, y
                    col += 1
                col += 1
                was_sum = False
                continue

            if j == GIER_CONTROL_SUM:
                was_sum = True

            if j in (
                GIER_CONTROL_TAPE_FEED,
                GIER_CONTROL_TAPE_FEED_CR,
            ):
                continue

            if col >= 80:
                col = 0
                line += 1

            if line >= 80:
                line = 0
                page += 1

            if j == GIER_CONTROL_CR:
                col =0
                line += 1
            elif j == GIER_CONTROL_FORM_FEED:
                if line or col:
                    line = 0
                    col = 0
                    page += 1
            elif j == 80:
                col = 0
            elif j == GIER_CONTROL_BLACK:
                red = 0
            elif j == GIER_CONTROL_LOWER:
                case = 0
            elif j == GIER_CONTROL_UPPER:
                case = 1
            elif j == GIER_CONTROL_SPACE:
                col += 1
            elif j in GIER_GLYPH:
                if not parity(i):
                    color = 3
                else:
                    color = red
                yield page, line, col, color, GIER_GLYPH[j][case]
                if j != 14:
                    col += 1
            elif j in GIER_CONTROL:
                x = "[" + GIER_CONTROL[j] + "]"
                for y in x:
                    yield page, line, col, 2, y
                    col += 1
                col += 1
            else:
                x = "%03d" % j
                for y in x:
                    yield page, line, col, 2, y
                    col += 1
                col += 1

    def html_interpretation(self, fo, _this):
        ''' Pull in the SVGs '''
        self.make_svgs()
        fo.write("<H3>GIER Text</H3>\n")
        fo.write("<pre>\n")
        for i in self.svg_files:
            fo.write('<img src="%s" width="50%%"/>\n' % i)
        fo.write("</pre>\n")
