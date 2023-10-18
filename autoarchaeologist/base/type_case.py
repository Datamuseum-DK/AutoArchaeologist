'''
   A "TypeCase" is a deliberately different word for what is often
   called a "Code Page" to be able to handle character sets which
   never got an official code-page name to begin with.

   For all modern character sets where it is possible, we rely on
   Python and unicode to sort things out for us.
'''

import unicodedata
import html

class Slug():
    ''' One position in the type case '''

    def __init__(self, short, long=None, flags=0):
        self.short = short
        if long is None:
            self.long = short
        else:
            self.long = long
        self.flags = flags

    def __str__(self):
        return "<Slug '" + self.short + "' '" + self.long + "'>"


class TypeCase():
    '''
    A description of a character set and its rules.

    This is a base-class, it needs to get the .slugs
    array filled out before it will be useful.

    The strings in .slugs can be anything, but they
    should preferably all render to the same width.
    '''

    INVALID = 0x01
    IGNORE = 0x02
    EOF = 0x04

    noslug = Slug(' ', '', INVALID)

    def __init__(self, name, bitwidth=8):
        self.name = name
        self.bitwidth = bitwidth
        self.maxval = 1 << bitwidth
        self.slugs = [self.noslug] * self.maxval
        self.fmt = ' %%0%dx' % ((bitwidth + 3)//4)
        self.pad = ' ' * ((bitwidth + 3)//4 + 1)

    def __getitem__(self, idx):
        if idx >= self.maxval:
            return None
        slug = self.slugs[idx]
        if slug.flags & self.INVALID:
            return None
        return slug

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
        for j, octet in enumerate(that):
            i = j % width
            if not i:
                txt1 = prefix + "%04x " % offset
                txt2 = "  ┆"
            txt1 += self.fmt % octet
            txt2 += self.slugs[octet].short
            if i == width - 1:
                yield txt1 + txt2 + "┆"
            offset += 1
        i = len(that) % width
        if i:
            txt1 += self.pad * (width - i)
            txt2 += " " * (width - i)
            yield txt1 + txt2 + "┆"

    def hexdump_html(self, that, file, **kwargs):
        ''' Hexdump into a HTML file '''
        for i in self.hexdump(that, **kwargs):
            file.write(html.escape(i) + "\n")

    def decode(self, octets):
        ''' decode octets using short form, not checking flags '''
        return ''.join(self.slugs[x].short for x in octets)

    def set_slug(self, nbr, short, *args, **kwargs):
        ''' define a slug '''
        self.slugs[nbr] = Slug(short, *args, **kwargs)

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
            elif char == "\t":
                self.set_slug(i, ' ', '\t')
            elif char == "\n":
                self.set_slug(i, ' ', '\n')
            elif char == "\r":
                self.set_slug(i, ' ', '\\r')
            elif char == "\f":
                self.set_slug(i, ' ', '\\f')
            elif char == " ":
                self.set_slug(i, ' ', ' ')
            elif unicodedata.category(char)[0] in "LNPSZ":
                self.set_slug(i, char, char)

class Ascii(WellKnown):
    ''' Aka: ISO 646 '''
    def __init__(self):
        super().__init__("ascii")

class EvenPar(TypeCase):

    ODD = 0
    PARITY = "Even"

    def __init__(self, base=None):
        if base is None:
            base = Ascii()
        super().__init__(base.name + "_" + self.PARITY + "_Parity")
        for n, i in enumerate(base.slugs):
            if i != base.noslug:
                self.slugs[self.parity(n)] = i

    def parity(self, n):
        n &= 0x7f
        p = n ^ (n >> 4)
        p = p ^ (p >> 2)
        p = p ^ (p >> 1)
        p &= 1
        p ^= self.ODD
        p <<= 7
        return p | n

    def set_slug(self, nbr, *args, **kwargs):
        super().set_slug(self.parity(nbr), *args, **kwargs)

class OddPar(EvenPar):
    ODD = 1
    PARITY = "Odd"

class DS2089(WellKnown):
    '''
       Dansk Standard 2089:1974
       Elektronisk databehandling. Anvendelse af ISO 7-bit kodet tegnsæt
    '''
    def __init__(self):
        super().__init__("ascii")
        self.name = "DS2089"
        for i, j in (
            ( 0x5b, 'Æ',),
            ( 0x5c, 'Ø',),
            ( 0x5d, 'Å',),
            ( 0x7b, 'æ',),
            ( 0x7c, 'ø',),
            ( 0x7d, 'å',),
            ( 0x7d, 'ü',),
        ):
            self.set_slug(i, j, j)
