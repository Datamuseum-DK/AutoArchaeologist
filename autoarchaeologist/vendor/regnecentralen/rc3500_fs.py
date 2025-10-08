

from ...base import octetview as ov


class DirEnt(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f00_=3,
            f01_=3,
            f02_=3,
            f03_=ov.Text(12),
            f04_=3,
            f05_=ov.Text(6),
            flds_=21,
        )


class Rc3500Filesystem(ov.OctetView):


    def __init__(self, this):
        if len(this) != 516096:
            return
        super().__init__(this)

        for ptr in range(0x300, 0x1800, 0x300):
            for n in range(12):
                y = DirEnt(self, ptr).insert()
                ptr = y.hi

        self.add_interpretation()
