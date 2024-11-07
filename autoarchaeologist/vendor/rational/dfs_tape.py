'''
   Rational 1000 DFS tapes
   -----------------------
'''

from ...base import octetview as ov
from ...base import namespace

class NameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ( "r", "nbyte"),
        ( "r", "nsect"),
        ( "r", "flags"),
        ( "r", "time"),
        ( "r", "date"),
        ( "r", "length"),
        ( "l", "name"),
        ( "l", "artifact"),
    )

    def time(self, arg):
        arg *= 2
        second = arg % 60
        minute = arg // 60
        hour = minute // 60
        minute %= 60
        return "%02d:%02d:%02d" % (hour, minute, second)

    def date(self, arg):
        day = arg % 0x1f
        month = (arg >> 5) & 0xf
        year = 1 + (arg >> 9)
        return "%02d-%02d-%02d" % (year, month, day)

    def ns_render(self):
        meta = self.ns_priv
        return [
            meta.nbyte.val,
            meta.nsect.val,
            hex(meta.f2.val),
            self.time(meta.f3.val),
            self.date(meta.f4.val),
            meta.length,
        ] + super().ns_render()

class Meta(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            name_=ov.Text(30),
            nsect_=ov.Be16,
            nbyte_=ov.Be16,
            f2_=ov.Be16,
            f3_=ov.Be16,
            f4_=ov.Be16,
            f5_=ov.Be16,
            more=True,
        )
        self.name.txt = self.name.txt.rstrip()
        self.done(pad=0x40)
        self.length = ((self.nsect.val-1) << 10) + self.nbyte.val
        assert self.f5.val == 1

class R1K_DFS_Tape(ov.OctetView):

    def __init__(self, this):
        if this[:13] != b'DFS_BOOTSTRAP':
            return
        if not this.has_type("SimhTapContainer"):
            return

        print("?R1KDFS", this, this.has_type("TAPE file"))

        super().__init__(this)

        self.namespace = NameSpace(
            name='',
            separator='',
            root=this,
        )
        this.add_interpretation(self, self.namespace.ns_html_plain)

        self.files = []
        offset = 0
        for r in this.iter_rec():
            if len(r) == 64:
                hdr = Meta(self, offset).insert()
                offset += len(r)

                y = ov.This(
                    self,
                    lo=offset,
                    width=hdr.length,
                ).insert()

                NameSpace(
                    name=hdr.name.txt,
                    parent=self.namespace,
                    priv = hdr,
                    this=y.that,
                )

                i = hdr.name.txt.split(".")
                y.that.add_type(i[-1])
            else:
                offset += len(r)
        this.taken = True

        # Comment in for debugging 
        # self.add_interpretation()
