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

            last = min(len(this), pos + 12)
            while last < len(this) and this[last]:
                last += 1

            ty = bytes(x for x in this[pos:last+2])
            tx = bytes(x & 0x7f for x in ty)
            tail_p = tx.find(b'\r\n')
            if tail_p == -1:
                tail_p = 8
                txt = ""
            else:
                txt = tx[8:tail_p]
                tail_p += 2
            tail = ty[tail_p:tail_p+4] + b'\x00\x00\x00\x00'
            tail = tail[:4]

            tcsum = tail[0] | (tail[1] <<8)
            tcount = tail[2] | (tail[3] <<8)

            if tcount > 0:
                rcsum = sum(this[max(0, pos + 8 - tcount):pos+8])
            else:
                rcsum = sum(this[0:pos + tail_p])
            rcsum += rcsum >> 16
            rcsum &= 0xffff
            rcount = pos + 8

            that = this.create(start=pos, stop=last)
            that.add_type("DGC-PaperTapeCheckSum")

            nn = []

            if rcsum == tcsum:
                nn.append("Sum=OK")
            else:
                nn.append("Sum=BAD")

            p0 = rcount - tcount
            if p0 >= 0 and sum(this[:p0]) == 0:
                rcount = tcount
                nn.append("Len=OK")
            elif p0 > 0:
                nn.append("Len=BAD")
                this.add_comment("DGC-PaperTapeCheckSum starts at 0x%x" % p0)
            elif p0 < 0 and rcsum != tcsum:	# Changed spacing of two parts ?
                nn.append("Len=BAD")
                this.add_comment("DGC-PaperTapeCheckSum starts at -0x%x" % -p0)

            this.add_note("DGC-PaperTapeCheckSum", ",".join(nn))
            npos = last

            if last - pos > 12:
                b = this[pos+8:last].tobytes().split(b'\x8d\n')
                if len(b) > 1:
                    if evenpar_ascii is None:
                        evenpar_ascii = type_case.EvenPar(type_case.ascii)
                    txt = evenpar_ascii.decode_long(b[0])
                    that.add_note(txt)
