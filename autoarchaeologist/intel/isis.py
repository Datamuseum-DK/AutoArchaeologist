
'''
   Intel ISIS floppies

'''

import struct

import autoarchaeologist.generic.octetview as ov

class Sector(ov.Octets):
    def __init__(self, up, cyl_no=None, sec_no=None, lo=None, desc=None):
        if lo is None:
            lo = (cyl_no * 52 + (sec_no - 1)) * 128
        self.cyl_no = cyl_no
        self.sec_no = sec_no
        super().__init__(up, lo, width=128)
        self.desc = desc

class LinkageBlock(Sector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __iter__(self):
        for i in range(64):
            yield self[i]

    def __getitem__(self, idx):
        return self.up.this[self.lo + idx * 2 + 1], self.up.this[self.lo + idx * 2]

class Linkage():
    def __init__(self, up, cyl, sect):
        self.up = up
        self.cyl = cyl
        self.sect = sect
        self.lbs = []
        lb = LinkageBlock(up, cyl, sect)
        if lb[0] != (0,0):
            return
        self.lbs.append(lb)
        self.lbs[-1].insert()
        nxt = self.lbs[-1][1]
        while nxt != (0,0):
            self.lbs.append(LinkageBlock(up, nxt[0], nxt[1]))
            nxt = self.lbs[-1][1]

    def insert(self):
        for lb in self.lbs:
            lb.insert()

    def __iter__(self):
        for lb in self.lbs:
            for i in range(2, 64):
                if lb[i] == (0,0):
                    return
                yield Sector(self.up, lb[i][0], lb[i][1])

class DirEnt(ov.Octets):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activity = self[0]
        self.attribute = self[0xa]
        self.tail = self[0xb]
        self.blocks = self[0xc] + self[0xd] * 256
        self.linkadr = (self[0xf], self[0xe])
        self.name = ""
        for i in range(1, 7):
            c = self[i]
            if 32 < c < 126:
                self.name += "%c" % c
            else:
                break
        self.name += "."
        for i in range(7, 10):
            c = self[i]
            if 32 < c < 126:
                self.name += "%c" % c
            else:
                break

    def render(self):
        for i in super().render():
            yield " ".join(
                (
                ".DIRENT",
                self.name.ljust(10),
                "%02x" % self.activity,
                "%02x" % self.attribute,
                "%02x" % self.tail,
                "%02x" % self.blocks,
                "%d,%d" % self.linkadr
                )
            )

    def commit(self):
        self.linkage = Linkage(self.up, *self.linkadr)
        that = []
        for sec in self.linkage:
            sec.insert()
            that.append(sec.octets())
        if that:
            y = self.up.this.create(b''.join(that)[:self.blocks * 128 + self.tail - 128])
            y.set_name(self.name)
 

class Directory():
    def __init__(self, up, linkage):
        self.up = up
        self.linkage = linkage
        self.dirents = {}
        for sec in linkage:
            for off in range(0, 128, 16):
                y = DirEnt(up, sec.lo + off, width = 16)
                y.insert()
                self.dirents[y.name] = y

    def __iter__(self):
        yield from self.dirents.values()

class Intel_Isis(ov.OctetView):

    def __init__(self, this):
        if len(this) not in (77*52*128,):
            return

        print("Intel_ISIS", this)
        super().__init__(this)

        l0 = Linkage(self, 1, 1)
        dir = Directory(self, l0)
        for dirent in dir:
            if not dirent.activity and dirent.name != "ISIS.DIR":
                dirent.commit()

        self.render()
