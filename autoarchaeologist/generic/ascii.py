
'''
   ASCII textfiles
   ---------------

   Textfiles under domus use (Danish) ASCII character set and
   several control characters which today are not in common use.
'''

from .parity import PARITY

# TAB only works if this is a multiple of 8
INDENT = " " * 8

CHARSET = [[0, "%c" % i] for i in range(256)]

# flag|1 -> end of line
for i in (10, 12, 13,):
    CHARSET[i][0] |= 1

# flag|2 -> graphical
for i in range(32, 128):
    CHARSET[i][0] |= 2

# flag|4 -> End of File
#CHARSET[0x03][0] |= 4

# flag|8 -> tabs
for i in (0x09, ):
    CHARSET[i][0] |= 8

# flag|16 -> ignore
# CHARSET[0x00][0] |= 16

CHARSET[0x03][1] = '\u2403'
CHARSET[0x0a][1] = '\n' + INDENT
CHARSET[0x0c][1] = '\u240c\n' + INDENT
CHARSET[0x0d][1] = ''
CHARSET[0x26][1] = '&amp;'
CHARSET[0x3c][1] = '&lt;'
CHARSET[0x7f][1] = '\u2421'

def DK_Tegn():
    ''' The canonical mapping of Danish vowels into ASCII '''
    CHARSET[0x5b][1] = 'Æ'
    CHARSET[0x5c][1] = 'Ø'
    CHARSET[0x5d][1] = 'Å'
    CHARSET[0x7b][1] = 'æ'
    CHARSET[0x7c][1] = 'ø'
    CHARSET[0x7d][1] = 'å'

class Ascii():
    ''' Recognize ASCII texts '''
    def __init__(self, this):

        if this.has_note("ASCII"):
            return

        par = [0, 0, 0, 0]
        pfx = None
        bodylen = 0
        lines = 0
        last_idx = None
        for idx, c in enumerate(this):
            if c:
                if pfx is None:
                    pfx = idx
                par[2 + PARITY[c]] += 1
                par[c >> 7] += 1
            elif pfx is None:
                continue

            j = CHARSET[c & 0x7f][0]
            if not j:
                return
            if not j & 16:
                last_idx = idx
                bodylen += 1
            if j & 4:
                break
            if j & 1:
                lines += 1

        if last_idx is None or bodylen < 10 or not lines:
            return

        if min(par) > 2:
            if bodylen > 64 and (1 in par or 2 in par):
                print("ASCII PARITY ERROR ?", this, bodylen, lines, par)
            return

        self.parsfx = ["-SET", "", "-ODD", "-EVEN"][par.index(min(par))]

        if pfx or last_idx != len(this):
            self.this = this.create(start=pfx, stop=last_idx)
            if self.this.has_note("ASCII"):
                return

        self.this.add_note("ASCII")
        if self.parsfx:
            self.this.add_note("ASCII" + self.parsfx)
        self.this.add_interpretation(self, self.html_as_interpretation)

    def html_as_interpretation(self, fo, _this):
        ''' Render as HTML '''
        fo.write("<H3>ASCII%s file</H3>\n" % self.parsfx)
        fo.write("<pre>\n")
        t = []
        after_cr = False
        after_ht = False
        for byte in self.this:
            byte &= 0x7f
            if CHARSET[byte][0] & 16:
                continue
            if after_cr and byte != 0x0a:
                t.append(CHARSET[0x0a][1])
            if byte != 0x7f or not after_ht:
                t.append(CHARSET[byte][1])
            after_cr = byte == 0x0d
            after_ht = byte == 0x09
        fo.write(INDENT + "".join(t))
        fo.write("</pre>\n")
