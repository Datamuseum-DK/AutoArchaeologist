'''
   Logical Disk filesystem
   -----------------------

   See chapter 7 & 8 in: https://datamuseum.dk/wiki/Bits:30000044
'''

from ..generic import disk
from ..base import namespace
from ..base import octetview as ov

class NameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ("r", "kind"),
        ("r", "f00"),
        ("r", "f01"),
        ("r", "f02"),
        ("r", "length"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        ''' ... '''
        de = self.ns_priv
        retval = [ de.kind, str(de.f00.val), str(de.f01.val) ]
        if de.kind == 'S':
            retval += [ str(de.f02.val) ]
        elif de.kind == 'R':
            retval += [ str(0xffff - de.f02.val) ]
        else:
            retval += [ str(de.f02.val) ]
        retval += [ str(de.length.val) ]
        return retval + super().ns_render()

class Hdr(ov.Struct):
    ''' The LD header record in first sector '''

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            ptr_=ov.Be16,
            lbl_=ov.Text(126),
            **kwargs
        )

class MainCat():
    ''' Main catalog, can only contain logical disks '''

    def __init__(self, tree, start, stop):
        self.tree = tree
        self.start = start
        self.stop = stop

        ptr = stop
        acc = start
        while True:
            ptr -= 0x10
            y = DirEnt(self.tree, ptr).insert()
            if y.name.txt == "$FREE   ":
                break
            y.kind = 'D'
            ns = NameSpace(
                name = y.name.txt.rstrip(),
                parent = self.tree.namespace,
                separator = "::",
                priv = y,
            )
            LogicalDisk(self.tree, acc, acc + (y.length.val<<7), ns)
            acc += y.length.val << 7

class LogicalDisk():
    ''' Logical Disk '''

    def __init__(self, tree, start, stop, pns):
        self.tree = tree
        self.start = start
        self.stop = stop

        ptr = stop
        acc = start
        while True:
            ptr -= 0x10
            y = DirEnt(self.tree, ptr).insert()
            sstart = acc
            sstop = acc + ((y.length.val-1) << 7)
            acc += y.length.val << 7

            if y.name.txt == "$FREE   ":
                break

            ns = NameSpace(
                name = y.name.txt.rstrip(),
                parent = pns,
                priv = y,
            )

            if y.f02.val <= 0x80:
                y.kind = 'S'
                sstop += y.f02.val
                z = ov.This(tree, lo=sstart, hi=sstop).insert()
                z.that.add_note(y.name.txt)
                ns.ns_set_this(z.that)
                if y.f02.val < 0x80:
                    ov.Opaque(tree, lo=sstop, width=0x80-y.f02.val).insert()
            else:
                y.kind = 'R'
                recsize = 0xffff - y.f02.val
                reccount = y.f01.val
                z = ov.This(tree, lo=sstart, width=recsize*reccount).insert()
                ns.ns_set_this(z.that)
                rest = (y.length.val << 7) - recsize * reccount
                if rest > 0:
                    ov.Opaque(tree, lo=z.hi, width=rest).insert()
                z.that.add_note(y.name.txt)


class DirEnt(ov.Struct):
    ''' Directory Entry '''

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            f00_=ov.Be16,
            f01_=ov.Be16,
            f02_=ov.Be16,
            length_=ov.Be16,
            name_=ov.Text(8),
            **kwargs
        )
        self.kind = ''

class LdFs(disk.Disk):
    ''' Logical Disk Filesytem '''

    def __init__(self, this):

        if not this.top in this.parents:
            return

        # Presently only found on 77c1h26s128b floppies
        if this[0] != 0x07 or this[1] != 0x3b:
            return

        for geom in (
            [  77, 1, 26, 128],
            [   0, 0,  0,   0],
        ):
            if len(this) == geom[0] * geom[1] * geom[2] * geom[3]:
                break

        if not sum(geom):
            return
        super().__init__(
            this,
            [ geom ]
        )

        print(this, self.__class__.__name__)

        self.namespace = NameSpace(
            name = '',
            root = this,
            separator = "",
        )

        self.hdr = Hdr(self, 0).insert()

        ptr = (self.hdr.ptr.val - 1) << 7
        self.root = MainCat(self, 0x80, ptr)

        this.add_interpretation(self, self.namespace.ns_html_plain)

        self.add_interpretation(more=True)
