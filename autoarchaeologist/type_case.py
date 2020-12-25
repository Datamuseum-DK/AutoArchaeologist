'''
   A "TypeCase" is a deliberately different word for what is often
   called a "Code Page" to be able to handle character sets which
   never got an official code-page name to begin with.

   For all modern character sets where it is possible, we rely on
   Python and unicode to sort things out for us.
'''

import unicodedata
import html

class TypeCase():
    '''
    A description of a character set and its rules.

    This is a base-class, it needs to get the .slugs
    array filled out before it will be useful.

    The strings in .slugs can be anything, but they
    should preferably all render to the same width.
    '''

    def __init__(self, name, bitwidth=8):
        self.name = name
        self.bitwidth = bitwidth
        self.maxval = (1 << bitwidth)
        self.slugs = [' '] * self.maxval
        self.fmt = ' %%0%dx' % ((bitwidth + 3)//4)
        self.pad = ' ' * ((bitwidth + 3)//4 + 1)

    def hexdump(
        self,
        that,
        width=16,
        prefix="",
        offset=0,
    ):
        ''' Hexdump in canonical format '''
        txt1 = ""
        txt2 = ""
        for j, x in enumerate(that):
            n = offset + j
            i = j % width
            if not i:
                txt1 = prefix + "%04x " % n
                txt2 = "  ┆"
            txt1 += self.fmt % x
            txt2 += self.slugs[x]
            if i == width - 1:
                yield txt1 + txt2 + "┆"
        i = len(that) % width
        if i:
            txt1 += self.pad * (width - i)
            txt2 += " " * (width - i)
            yield txt1 + txt2 + "┆"

    def hexdump_html(self, that, fo, **kwargs):
        ''' Hexdump into a HTML file '''
        for i in self.hexdump(that, **kwargs):
            fo.write(html.escape(i) + "\n")

class WellKnown(TypeCase):
    '''
       Use pythons built in decoder to do the job
    '''

    def __init__(self, encoding):
        super().__init__(encoding)
        i = bytes(x for x in range(256))
        j = i.decode(encoding, 'replace')
        for i, char in enumerate(j):
            if char == '\ufffd':
                pass
            elif char == "\n":
                self.slugs[i] = '\u21b2'    # Show LF explicitly
            elif char == "\r":
                self.slugs[i] = '\u21e4'    # Show CR explicitly
            elif char == " ":
                self.slugs[i] = '\u2423'    # Show SP explicitly
            elif unicodedata.category(char)[0] in "LNPSZ":
                self.slugs[i] = char

class Ascii(WellKnown):
    ''' Aka: ISO 646 '''
    def __init__(self):
        super().__init__("ascii")

class DS2089(Ascii):
    '''
       Dansk Standard 2089:1974
       Elektronisk databehandling. Anvendelse af ISO 7-bit kodet tegnsæt
    '''
    def __init__(self):
        super().__init__()
        self.name = "DS2089"
        self.slugs[0x5b] = 'Æ'
        self.slugs[0x5c] = 'Ø'
        self.slugs[0x5d] = 'Å'
        self.slugs[0x5e] = 'Ü'
        self.slugs[0x7b] = 'æ'
        self.slugs[0x7c] = 'ø'
        self.slugs[0x7d] = 'å'
        self.slugs[0x7e] = 'ü'
