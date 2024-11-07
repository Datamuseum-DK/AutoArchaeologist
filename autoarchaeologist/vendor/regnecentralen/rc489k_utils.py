'''
   RC4000/RC8000/RC9000 Namespace and catalog extension
   ----------------------------------------------------

'''

import time
import html

from ...base import namespace
from ...base import octetview as ov

def words_to_bytes(words):
    a = []
    for i in words:
        a.append(i >> 16)
        a.append((i >> 8) & 0xff)
        a.append(i & 0xff)
    return bytes(a).rstrip(b'\x00')

def words_to_text(this, words):
    return this.type_case.decode_long(words_to_bytes(words))

class Rc489kNameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ( "r", "entry-base"),
        ( "r", "mode"),
        ( "r", "kind"),
        ( "r", "key"),
        ( "r", "nseg"),
        ( "l", "date"),
        ( "l", "docname"),
        ( "r", "w7"),
        ( "r", "w8"),
        ( "r", "w9"),
        ( "r", "w10"),
        ( "l", "name"),
        ( "l", "artifact"),
    )

    def ns_render(self):
        meta = self.ns_priv
        if hasattr(meta, "ns_render"):
            return meta.ns_render() + super().ns_render()
        return [html.escape(str(type(meta)))] + ["-"] * (len(self.TABLE)-3) + super().ns_render()

def short_clock(word):
    '''
       Time is kept in a double word (=48 bits) counting units of
       100µs since 1968-01-01T00:00:00 local time.

       A ShortClock throws the 5 MSB and 19 LSB bits away, which
       gives a resolution a tad better than a minute and a range
       of almost 28 years.

       Render as ISO8601 without timezone
    '''
    if word == 0:
        return "                "
    ut = (word << 19) * 100e-6
    t0 = (366+365)*24*60*60
    return time.strftime("%Y-%m-%dT%H:%M", time.gmtime(ut - t0 ))

class ShortClock(ov.Be24):
    '''
       Time is kept in a double word (=48 bits) counting units of
       100µs since 1968-01-01T00:00:00 local time.

       A ShortClock throws the 5 MSB and 19 LSB bits away, which
       gives a resolution a tad better than a minute and a range
       of almost 28 years.
    '''

    def render(self):
        ''' Render as ISO8601 without timezone '''
        yield short_clock(self.val)

class DWord(ov.Struct):
    ''' A double word '''

    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            w0_=ov.Be24,
            w1_=ov.Be24,
        )

    def render(self):
        yield "(0x%x" % self.w0.val + ",0x%x)" % self.w1.val

class Rc489kBasePair(DWord):

    def render(self):
        if 0 and self.w0.val == self.w1.val:
            yield "├" + str(self.w0.val) + "┤"
        else:
            lo = min(self.w0.val, self.w1.val)
            hi = max(self.w0.val, self.w1.val)
            yield "├0x%06x" % lo + "┄0x%06x" % hi + "┤"

    def __eq__(self, other):
        return self.w0.val == other.w0.val and self.w1.val == other.w1.val

class Rc489kEntryTail(ov.Struct):
    ''' The ten words which describe a file '''

    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            w_=ov.Array(10, ov.Be24),
        )
        if self.w[0].val >> 23:
            self.kind = self.w[0].val & 0xfff
            self.mode = self.w[0].val >> 12
            self.nseg = 0
        else:
            self.kind = 4
            self.mode = 0
            self.nseg = self.w[0].val
        self.key = self.w[8].val >> 12
        self.docname = self.this.type_case.decode_long(
            words_to_bytes((x.val for x in self.w[1:5]))
        )

    def render(self):
        yield "-".join(self.ns_render())

    def ns_render(self):
        return [
            "%d" % self.mode,
            "%d" % self.kind,
            "%d" % self.key,
            "%d" % self.nseg,
            short_clock(self.w[5].val),
            self.docname,
            "0x%x" % self.w[6].val,
            "0x%x" % self.w[7].val,
            "0x%x" % self.w[8].val,
            "0x%x" % self.w[9].val,
        ]

