#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
    SIMH-TAP file containers
    ------------------------

'''

from ..base import artifact
from ..base import octetview as ov
from . import plain_file

class BadTAPFile(Exception):
    ''' ... '''

class SimhTapContainer(artifact.ArtifactFragmented):
    ''' Create an artifact from a SIMH-TAP file '''

    def __init__(self, top, octets=None, filename=None, verbose=False):
        super().__init__(top)
        if octets is None:
            octets = plain_file.PlainFileArtifact(filename).bdx
        octets = memoryview(octets).toreadonly()

        ovt = ov.OctetView(octets)
        adr = (0, 0)
        ptr = 0
        offset = 0
        while ptr <= len(octets) - 4:
            i = ov.Le32(ovt, ptr)
            if verbose:
                print("M", adr, hex(i.val))
            ptr = i.hi
            if i.val == 0:
                # Tape mark
                adr = (adr[0] + 1, 0)
                continue
            if i.val == 0xffffffff:
                if ptr != len(octets):
                    raise BadTAPFile("Stuff after EOT")
                break
            if (i.val >> 24) == 0xff:
                # reserved magic words
                continue
            j = (i.val + 1) & ~1
            if ptr + 8 + j > len(octets):
                if len(self) == 0:
                    raise BadTAPFile("Does not look like a SIMH-TAP file")
                print("Truncated SIMH-TAP file", filename)
                break
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
                print("Pre & Post disagree (0x%x vs. 0x%x)" % (i.val, j.val))
                if len(self) == 0:
                    raise BadTAPFile("Pre & Post disagree")
                break
            ptr = j.hi
        self.completed()
        self.add_type('SimhTapContainer')
