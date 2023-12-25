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

    def __init__(self, octets=None, filename=None, verbose=False):
        super().__init__()
        if octets is None:
            octets = plain_file.PlainFileArtifact(filename).bdx
        octets = memoryview(octets).toreadonly()

        ovt = ov.OctetView(octets)
        adr = (0, 0)
        ptr = 0
        offset = 0
        while ptr < len(octets):
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
            frag = octets[ptr:ptr + i.val]
            ptr += j
            self.add_fragment(
                artifact.Record(
                    low=offset,
                    frag=frag,
                    key=adr,
                )
            )
            offset += len(frag)
            adr = (adr[0], adr[1] + 1)
            j = ov.Le32(ovt, ptr)
            if i.val != j.val:
                raise BadTAPFile("Pre & Post disagree")
            ptr = j.hi
        if ptr != len(octets):
            raise BadTAPFile("Stuff after EOT")
        self.completed()
