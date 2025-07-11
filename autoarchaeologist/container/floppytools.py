'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from ..base import artifact

class CHS():
    ''' ... '''

    def __init__(self, chs):
        self.c, self.h, self.s = (int(x) for x in chs.split(","))
        self.chs = (self.c, self.h, self.s)

    def __lt__(self, other):
        return self.chs < other.chs

    def __repr__(self):
        return str(self.chs)

class FloppyToolsContainer(artifact.ArtifactFragmented):
    ''' ... '''

    def __init__(self, top, filename):
        super().__init__(top)
        sects = {}
        for line in open(filename):
            flds = line.split()
            if not flds or flds[0] != "sector":
                continue
            chs = CHS(flds[2])
            b = bytes.fromhex(flds[3])
            sects[chs.chs] = b
        if not sects:
            raise EOFError
        hasbad = False
        if False:
            for cyl in range(0, 77):
                for sect in range(1, 27):
                    chs = (cyl, 0, sect)
                    if chs in sects:
                        continue
                    sects[chs] = b'_UNREAD_' * 16
                    print("UNREAD", chs, filename)
                    hasbad = True
        offset = 0
        for chs, octets in sorted(sects.items()):
            # print(chs, offset, octets)
            self.add_fragment(
                artifact.Record(
                    low=offset,
                    frag=octets,
                    key=chs,
                )
            )
            offset += len(octets)
        if hasbad:
            self.add_note("BADSECTs")
        self.completed()
        print("SELF", self)
