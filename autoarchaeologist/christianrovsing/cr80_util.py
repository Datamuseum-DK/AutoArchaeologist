

'''
   CR80 Filesystem type 2

   See https://ta.ddhf.dk/wiki/Bits:30004479
'''

import autoarchaeologist.generic.octetview as ov

class Text(ov.Octets):
    def __init__(self, up, lo, *args, **kwargs):
        super().__init__(up, lo, width=self.width, *args, **kwargs)
        t = []
        for a in range(self.width):
            if a & 1:
                 t.append(self.this[lo + a])
                 t.append(b)
            else:
                 b = self.this[lo + a]
        try:
            i = t.index(0)
            if i > 0:
                t = t[:i]
        except ValueError:
            pass
        self.txt = "".join("%c" % x for x in t)

    def render(self):
        yield '»' + self.txt + '«' + " " * (self.width - len(self.txt))

class Text6(Text):
    width = 6

class Text16(Text):
    width = 16
