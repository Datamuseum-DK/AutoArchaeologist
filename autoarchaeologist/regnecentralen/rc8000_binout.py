'''
   RC8000 binout format
   --------------------
'''

from ..base import octetview as ov
from .rc489k_utils import *

RC8000_BINOUT_MAGIC = bytes.fromhex("98 37 89 25 98 97 91 25")

def parity(x):
    x ^= x >> 4
    x ^= x >> 2
    x ^= x >> 1
    return x & 1

def wtotxt(x):
    return "%c" % ((x >> 16) & 0xff) + "%c" % ((x >> 8) & 0xff) + "%c" % ((x >> 0) & 0xff)

class BinOutName():

    def __init__(self, *args, **kwargs):
        self.nspace = Rc489kNameSpace(*args, **kwargs, priv=self)
        self.nload = 0
        self.cat_key = 0
        self.entry_tail = None
        self.load_segments = []

    def commit(self, this):
        if not self.load_segments:
            return
        print("COMMIT", this, self, self.load_segments[0])
        that = this.create(
             bits = words_to_bytes(self.load_segments[0].words)
        )
        self.nspace.ns_set_this(that)

    def ns_render(self):
        return self.entry_tail.ns_render()

class BinOutSegment(ov.Octets):

    def __init__(self, tree, lo, payload):
        super().__init__(tree, lo, width = len(payload) + 1)
        self.payload = payload
        self.hwords = []
        for n in range(0, len(payload), 2):
            self.hwords.append((payload[n] << 6) | payload[n+1])
        self.words = []
        for n in range(0, len(self.hwords), 2):
            self.words.append((self.hwords[n] << 12) | self.hwords[n+1])

    def decode_command_segment(self):
        n = 0
        retval = None
        while n < len(self.words):
            t = words_to_text(self.this, self.words[n:n+2])
            n += 2
            if t == 'create':
                if retval:
                    yield retval
                fn = words_to_text(self.this, self.words[n:n+4])
                n += 4
                retval = BinOutName(name = fn, parent=self.tree.namespace)
                retval.entry_tail = EntryTail(self.this, self.words[n:n+10])
                n += 10
                print("CW", [t, fn, str(retval.entry_tail)])
            elif t == 'perman':
                fn = words_to_text(self.this, self.words[n:n+4])
                n += 4
                retval.cat_key = self.words[n]
                n += 1
                print("CW", [t, fn, retval.cat_key])
            elif t == 'load':
                fn = words_to_text(self.this, self.words[n:n+4])
                n += 4
                retval.nload = self.words[n]
                n += 1
                print("CW", [t, fn, retval.nload])
            else:
                print("CW?", [t], self)
                break
        if retval:
            yield retval

    def render(self):
        yield "-".join("%06x" % x for x in self.words)

class RC8000BinOut(ov.OctetView):

    def __init__(self, this):
        if this[0:8] != RC8000_BINOUT_MAGIC:
            return
        super().__init__(this)

        self.namespace = Rc489kNameSpace(
            name='',
            separator='',
            root=this,
        )
        segments = []
        l = []
        lo = 0
        for n, i in enumerate(this):
            if not parity(i):
                break
            if i & 0x40:
                goodsum = (sum(l) & 0x3f) == (i& 0x3f)
                if not goodsum:
                    return
                segments.append(BinOutSegment(self, lo, l).insert())
                lo = n+1
                l = []
            else:
                l.append(i & 0x7f)
        if not segments:
            return
        print(this, self.__class__.__name__, len(segments))
        n = 0
        names = []
        while n < len(segments):
            seg = segments[n]
            n += 1
            names.append(*seg.decode_command_segment())
            names[-1].load_segments += segments[n:n + names[-1].nload]
            n += names[-1].nload
        for i in names:
            i.commit(self.this)
            print("NN", i)
        this.add_note("Rc8000_binout")
        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.add_interpretation() 
