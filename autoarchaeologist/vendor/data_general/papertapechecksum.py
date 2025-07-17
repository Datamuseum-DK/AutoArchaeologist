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

   See: 093-000005-00 User's Manual Program Tape Duplicator
'''

from ...base import type_case

class PaperTapeCheckSum():

    ''' ... '''

    def __init__(self, this):
        if this.has_type("DGC-PaperTapeCheckSum"):
            return

        evenpar_ascii = None
        npos = 0
        for pos, octet in enumerate(this):
            if octet != 0xaa or pos < npos:
                continue
            if this[pos:pos+8].tobytes() != b'\xaa\x55\xaa\x55\xaa\x55\xaa\x55':
                continue

            tail = list(x for x in this[pos+8:pos+12]) + [0, 0, 0, 0]
            tcsum = tail[0] | (tail[1] <<8)
            tcount = tail[2] | (tail[3] <<8)
            rcsum = sum(this[max(0, pos + 8 - tcount):pos+8])
            rcsum += rcsum >> 16
            rcsum &= 0xffff
            rcount = pos + 8
            # print(this, "DGC", hex(rcount), hex(rcsum), hex(tcount), hex(tcsum))
            for last in range(pos, min(pos + 30, len(this))):
                if this[last] == 0:
                    break
            if this[last]:
                if last < len(this) - 1:
                    continue
                last += 1
            p0 = pos + 8 - tcount
            if p0 > 0 and sum(this[:p0]) == 0:
                if p0 != 0x80:
                    print(this, "DGC extra zero leader", hex(p0))
                rcount = tcount
            elif p0 != 0 and 0:
                print(
                    this,
                    "DGC bad len",
                    "p0",
                    hex(p0),
                    "pos+8",
                    hex(pos+8),
                    "tcount",
                    hex(tcount),
                    "len(this)",
                    hex(len(this))
                )
            that = this.create(start=pos, stop=last)
            that.add_type("DGC-PaperTapeCheckSum")
            if rcsum == tcsum and rcount == tcount:
                this.add_type("DGC-PaperTapeCheck_OK")
            elif rcsum != tcsum and rcount == tcount:
                this.add_type("DGC-PaperTapeCheck_Len_OK")
            elif rcsum == tcsum and rcount != tcount:
                this.add_type("DGC-PaperTapeCheck_Sum_OK")
            else:
                this.add_type("DGC-PaperTapeCheck_BAD")
            npos = last

            if last - pos > 0xc:
                b = this[pos+8:last].tobytes().split(b'\x8d\n')
                if len(b) > 1:
                    if evenpar_ascii is None:
                        evenpar_ascii = type_case.EvenPar(type_case.ascii)
                    txt = evenpar_ascii.decode_long(b[0])
                    that.add_note(txt)
