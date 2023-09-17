'''
   Rational 1000 DFS tapes
   -----------------------
'''

import html
import struct

import autoarchaeologist
from autoarchaeologist.generic import octetview as ov

class NameSpace(autoarchaeologist.NameSpace):
    ''' ... '''

    TABLE = (
        ( "r", "nbyte"),
        ( "r", "nsect"),
        ( "r", "f2"),
        ( "r", "f3"),
        ( "r", "f4"),
        ( "r", "f5"),
        ( "r", "length"),
        ( "l", "name"),
        ( "l", "artifact"),
    )

    def ns_render(self):
        meta = self.ns_priv
        return [
            meta.nbyte.val,
            meta.nsect.val,
            meta.f2.val,
            meta.f3.val,
            meta.f4.val,
            meta.f5.val,
            meta.length,
        ] + super().ns_render()

class Meta(ov.Struct):
    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            name_=ov.Text(30),
            nsect=ov.Be16,
            nbyte=ov.Be16,
            f2_=ov.Be16,
            f3_=ov.Be16,
            f4_=ov.Be16,
            f5_=ov.Be16,
            more=True,
        )
        self.name.txt = self.name.txt.rstrip()
        self.done(pad=0x40)
        self.length = ((self.nsect.val-1) << 10) + self.nbyte.val

class R1K_DFS_Tape(ov.OctetView):

    def __init__(self, this):
        if this[:13].tobytes() != b'DFS_BOOTSTRAP':
            return
        if not this.has_type("TAPE file"):
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
        for r in this.iterrecords():
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
                    this=y.this,
                )
                
                i = hdr.name.txt.split(".")
                y.this.add_type(i[-1])
            else:
                offset += len(r)

        self.render()
