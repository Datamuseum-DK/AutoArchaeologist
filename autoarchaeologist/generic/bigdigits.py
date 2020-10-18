
# These are the byte-patterns we recognize, for instance:
#
# b'\xe1\x11\x09\x07' =
#
#     11100001
#     00010001
#     00001001
#     00000111
# =
#
#     ###----#
#     ---#---#
#     ----#--#
#     -----###
#
# = '7' rotated 90° with the clock

GLYPHS = {
    b'\x7e\x81\x81\x7e':	"0",
    b'\x81\xff\x80':		"1",
    b'\xe1\x91\x89\x86':	"2",
    b'\x89\x8d\x8b\x71':	"3",
    b'\x89\x91\x8b\x71':	"3", # misread ?
    b'\x08\x0c\x0a\xff':	"4",
    b'\x8f\x89\x89\xf1':	"5",
    b'\x7e\x89\x89\x71':	"6",
    b'\xe1\x11\t\x07':		"7",
    b'\x76\x89\x89\x76':	"8",
    b'\x86\x89\x49\x3e':	"9",
    b'\x08\x08\x08':		"-",
    b'\x08\x08\x08\x08':	"-",
    b'\xa8\x70\x70\xa8':	"*",
}

GLYPH_WIDTHS = {len(x) for x in GLYPHS}

class BigDigits():
    ''' Recognize visual digits punched in 8-hole paper-tape '''

    def __init__(self, this):
        if this.has_note("BigDigits"):
            return

        idx = 0
        while idx < len(this) and not this[idx]:
            idx += 1
        if idx == len(this):
            return

        j = ""
        z = 0

        pfxlen = idx
        last_idx = -1
        while idx < len(this):
            if not this[idx]:
                idx += 1
                z += 1
                if z > 10:
                    break
                continue
            for width in GLYPH_WIDTHS:
                t = GLYPHS.get(bytes(this[idx:idx+width]))
                if t and (idx+width == len(this) or not this[idx+width]):
                    j += t
                    idx += width
                    last_idx = idx
                    break
            if last_idx < idx:
                if len(j) > 0:
                    print("BigDigits ?", this[idx:idx+8].hex(), j, z, this, idx, this[idx:idx+8])
                return
            z = 0

        if not j:
            return

        this = this.slice(pfxlen, last_idx - pfxlen)
        if not this.has_note("BigDigits"):
            self.this = this
            this.add_type("BigDigits")
            this.add_note(j)
            this.add_interpretation(self, self.html_as_interpretation)

    def html_as_interpretation(self, fo, _this):
        ''' A table full of holes '''
        fo.write("<H3>Big Digits</H3>\n")
        fo.write('<table style="table-layout: fixed; border: 1px solid black;">\n')
        for b in range(8):
            bit = 1 << b
            t = "<tr>"
            for i in self.this:
                #t += '<td style="border: 1px solid black;">'
                t += '<td>'
                if i & bit:
                    t += '\u2b24'
                else:
                    t += '&nbsp;'
                t += "</td>"
            t += "</tr>"
            fo.write(t + "\n")
        fo.write('</table>\n')
