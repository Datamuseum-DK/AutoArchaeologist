#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license


'''
    D64 and D71 file containers
    ---------------------------

    As documented in:
       "D64 (Electronic form of a physical 1541 disk)"
	    version 1.11 bu Peter Schepers
       "D71 (Electronic form of a double-sided 1571 disk)"
	    version 1.5 bu Peter Schepers

'''

from ..base import artifact
from . import plain_file

class BadD64File(Exception):
    ''' ... '''

class D64Record(artifact.Record):
    ''' ... '''

class D64Container(artifact.ArtifactFragmented):
    ''' Create an artifact from an D64 or D71 file '''

    def __init__(self, top, octets=None, filename=None, _verbose=False):
        super().__init__(top)
        if octets is None:
            fcont = plain_file.PlainFileArtifact(filename)
        else:
            fcont = artifact.ArtifactStream(octets)

        tracks, errors, sides = {
            174848: (35, False, 1),
            175531: (35, True, 1),
            196608: (40, False, 1),
            197376: (40, True, 1),
            2*174848: (70, False, 2),
            2*175531: (70, True, 2),
        }.get(len(fcont), (None, None, None))
        if tracks is None:
            raise BadD64File("Wrong size (%d)" % len(fcont))

        spt = [0] + [21] * 17 + [19] * 7 + [18] * 6 + [17] * 10
        if sides == 2:
            spt += spt
        sectors = []
        ptr = 0
        for tno in range(1, tracks+1):
            for sno in range(spt[tno]):
                rec = D64Record(ptr, frag=fcont[ptr:ptr+256], key=(tno, 0, sno))
                rec.d64_error = 0
                sectors.append(rec)
                self.add_fragment(rec)
                ptr += 256
        #assert not errors

        self.completed()
