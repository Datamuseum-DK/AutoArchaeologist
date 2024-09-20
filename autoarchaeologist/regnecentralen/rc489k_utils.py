'''
   RC4000/RC8000/RC9000 Namespace and catalog extension
   ----------------------------------------------------

'''

import time
import html

from ..base import namespace

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

class EntryTail():

    def __init__(self, this, words):
        self.this = this
        self.words = words
        if self.words[0] >> 23:
            self.kind = self.words[0] & 0xfff
            self.mode = self.words[0] >> 12
            self.nseg = 0
        else:
            self.kind = 4
            self.mode = 0
            self.nseg = self.words[0]
        self.key = self.words[8] >> 12
        self.docname = self.this.type_case.decode_long(
            words_to_bytes(self.words[1:5])
        )

    def __str__(self):
        return ",".join(self.ns_render())

    def ns_render(self):
        return [
            "%d" % self.mode,
            "%d" % self.kind,
            "%d" % self.key,
            "%d" % self.nseg,
            short_clock(self.words[5]),
            self.docname,
            "0x%x" % self.words[6],
            "0x%x" % self.words[7],
            "0x%x" % self.words[8],
            "0x%x" % self.words[9],
        ]

