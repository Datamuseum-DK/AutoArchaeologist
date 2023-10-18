'''
   DOMUS FCOPY
   -----------

'''

from ..generic import disk
from ..base import namespace
from ..generic import octetview as ov

# Size of sectors
SEC_SIZE = (1 << 9)

class NameSpace(namespace.NameSpace):
    ''' ... '''

    def ns_render(self):
        fc = self.ns_priv
        return [
            fc.w03.val,
            fc.w04.val,
            fc.w05.val,
            fc.w06.val,
            fc.last_sect.val,
            fc.w08.val,
            fc.w09.val,
            fc.last_bytes.val,
            fc.w0b.val,
            fc.w0c.val,
            fc.w0d.val,
            fc.w0e.val,
            fc.w0f.val,
        ] + super().ns_render()

class Fcopy(ov.Struct):

    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            vertical=False,
            name_=ov.Text(6),
            w03_=ov.Be16,
            w04_=ov.Be16,
            w05_=ov.Be16,
            w06_=ov.Be16,
            last_sect_=ov.Be16,
            w08_=ov.Be16,
            w09_=ov.Be16,
            last_bytes_=ov.Be16,
            w0b_=ov.Be16,
            w0c_=ov.Be16,
            w0d_=ov.Be16,
            w0e_=ov.Be16,
            w0f_=ov.Be16,
            magic_=ov.Text(16),
        )

class Domus_FCOPY(disk.Disk):

    def __init__(self, this):

        if not this.top in this.parents:
            return

        if this[0x20:0x30] != b'RC3600 FCOPY\x00\x00\x00\x00':
            return

        for geom in (
            [  77, 1, 26, 128],
            [ 203, 2, 12, 512],
            [   0, 0,  0,   0],
        ):
            if len(this) == geom[0] * geom[1] * geom[2] * geom[3]:
                break

        if not sum(geom):
            return
        this.add_type("DOMUS FCOPY")
        super().__init__(
            this,
            [ geom ]
        )

        self.namespace = NameSpace(
            name = "",
            root = this,
        )
        this.add_interpretation(self, self.namespace.ns_html_plain)

        adr = 0
        while this[adr + 0x20:adr + 0x30] == b'RC3600 FCOPY\x00\x00\x00\x00':
            y = Fcopy(self, adr)
            adr = y.lo + ((y.last_sect.val + 1) << 9)
            print("FC", hex(adr), y)
            y.insert()
            print(y)
            stop = y.lo + (y.last_sect.val<<9) + y.last_bytes.val
            that = this.create(start=y.lo + 512, stop = stop)
            print("YY", y.name.txt)
            ns = NameSpace(
                name = y.name.txt,
                parent = self.namespace,
                this=that,
                priv=y,
            )

        # self.fill_gaps()

        # self.render()
