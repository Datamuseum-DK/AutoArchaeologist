#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Data General Papertape checksum
   -------------------------------

   At the end of original (and some copies of) Data General
   papertapes, an identifier is punched in ASCII with even
   parity:

       "U*U*U*U*" [something]

   We suspect the last two characters is a checksum, but we
   have not been able to identify the algorithm.  Sometimes
   a product number is part of [something].
'''

from ...base import type_case

class PaperTapeCheckSum():

    ''' ... '''

    def __init__(self, this):
        if this.has_note("DGC-PaperTapeCheckSum"):
            return

        evenpar_ascii = None
        npos = 0
        for pos, octet in enumerate(this):
            if octet != 0xaa or pos < npos:
                continue
            if this[pos:pos+8].tobytes() != b'\xaa\x55\xaa\x55\xaa\x55\xaa\x55':
                continue
            for last in range(pos, min(pos + 30, len(this))):
                if this[last] == 0:
                    break
            if this[last]:
                if last < len(this) - 1:
                    continue
                last += 1
            that = this.create(start=pos, stop=last)
            that.add_type("DGC-PaperTapeCheckSum")
            npos = last

            if last - pos > 0xc:
                b = this[pos+8:last].tobytes().split(b'\x8d\n')
                if len(b) > 1:
                    if evenpar_ascii is None:
                        evenpar_ascii = type_case.EvenPar(type_case.ascii)
                    txt = evenpar_ascii.decode_long(b[0])
                    that.add_note(txt)
