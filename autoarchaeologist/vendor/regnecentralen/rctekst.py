
from ...base import octetview as ov

class FormFeed(ov.Dump):
    ''' ... '''

class Params(ov.Dump):
    ''' ... '''

class RcTekst(ov.OctetView):

    def __init__(self, this):
        if this[0x7e] != 0xff:
             return
        if this[0x7f] != 0x04:
             return
        this.add_type("RcTekst")
        super().__init__(this)

        with self.this.add_utf8_interpretation("RcTekst") as file:
             i = 0x47
             while i < len(this):
                 c = this[i]
                 if c == 0x20:
                     file.write(" ")
                     i += 1
                 elif 0x21 <= c <= 0x7f:
                     file.write(this.type_case.decode_long([c]))
                     i += 1
                 elif c == 0x09:
                     file.write("╞\t")
                     i += 1
                 elif c == 0x0a:
                     file.write("↓\n")
                     i += 1
                 elif c == 0x0d and i + 1 < len(this) and this[i+1] == 0x0a:
                     file.write("↲\n")
                     i += 2
                 elif c == 0x0d:
                     file.write("←\n")
                     i += 1
                 elif c == 0x04:
                     y = Params(self, lo=i, hi=i+57).insert()
                     file.write("\n╱" + "".join("%02x" % i for i in y) + "╱\n")
                     i = y.hi
                 elif c == 0x0c:
                     y = FormFeed(self, lo=i, hi=i+3).insert()
                     file.write("\n" + "═" * 72 + "\n")
                     i = y.hi
                 elif c == 0x16:
                     file.write("«index»")
                     i += 1
                 elif c == 0x80:
                     file.write("┄")
                     i += 1
                 else:
                     file.write("┆%02x┆" % c)
                     i += 1

        self.add_interpretation(more=True)

