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

class Sector():
    ''' ... '''

    def __init__(self, line):
        flds = line.split()
        self.src = flds[1]
        self.offset = int(flds[2])
        self.phys_chs = CHS(flds[3])
        self.am_chs = CHS(flds[4])
        self.data = bytes.fromhex(flds[5])
        self.flags = flds[6:]

class FloppyToolsContainer(artifact.ArtifactFragmented):
    ''' ... '''

    def __init__(self, top, filename):
        super().__init__(top)
        psects = {}
        asects = {}
        for line in open(filename):
            if line[:7] != "sector ":
                continue
            sec = Sector(line)
            asects[sec.am_chs.chs] = sec
            osec = psects.get(sec.phys_chs.chs)
            if osec is None:
                psects[sec.phys_chs.chs] = sec
            else:
                assert osec.data == sec.data
        if not psects:
            raise EOFError
        if len(psects) == len(asects):
            order = asects
        else:
            order = psects
        offset = 0
        for chs, sect in sorted(order.items()):
            self.add_fragment(
                artifact.Record(
                    low=offset,
                    frag=sect.data,
                    key=chs,
                )
            )
            offset += len(sect.data)
        self.completed()
        if order == psects:
            self.add_note("Using phyical address_marks")
