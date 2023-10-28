#!/usr/bin/env python3

'''
    SIMH-TAP file containers
    ------------------------

'''

from ..base import artifact
from ..base import type_case
from ..base import octetview as ov
from . import plain_file

class BadTAPFile(Exception):
    ''' ... '''

class SimhTapContainer(artifact.ArtifactFragmented):
    ''' Create an artifact from a SIMH-TAP file '''

    def __init__(self, filename, verbose=False):
        super().__init__()
        fcont = plain_file.PlainFileArtifact(filename)

        fcont.type_case = type_case.ascii

        ovt = ov.OctetView(fcont)
        adr = (0, 0)
        ptr = 0
        while ptr < len(fcont):
            i = ov.Le32(ovt, ptr)
            if verbose:
                print("M", adr, hex(i.val))
            ptr = i.hi
            if i.val == 0:
                adr = (adr[0] + 1, 0)
                continue
            if i.val == 0xffffffff:
                break
            if i.val > 0x00ffffff:
                continue
            j = (i.val + 1) & ~1
            frac = fcont[ptr:ptr + i.val]
            ptr += j
            rec = self.add_part(adr, frac)
            adr = (adr[0], adr[1] + 1)
            j = ov.Le32(ovt, ptr)
            if i.val != j.val:
                raise BadTAPFile("Pre & Post disagree")
            ptr = j.hi
        if ptr != len(fcont):
            raise BadTAPFile("Stuff after EOT")
        self.completed()
