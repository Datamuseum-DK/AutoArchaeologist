#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

''' 
   Q1 Text
   =======
'''

from ...base import octetview as ov

class Q1Text():

    def __init__(self, this):
        if len(this.rp_interpretations):
            return
        histo = [0 for x in range(256)]
        for x in this:
            histo[x] += 1
        ctl = sum(histo[:32])
        text = sum(histo[32:128])
        high = sum(histo[128:])
        text = True
        if high > 0:
            text = False
        if sum(histo[:8]):
            text = False
        l = []
        for n, i in enumerate(histo[:32]):
            if i:
                l.append(n)
        if histo[127]:
            l.append(127)
        if text:
            #print("T", this, len(this), ctl, text, high, l)
            this.add_type("Q1_Text")
            tf = this.add_utf8_interpretation("Text")
            with open(tf.filename, "w") as file:
                for rec in this.iter_rec():
                    file.write(this.type_case.decode_long(rec.frag) + "\n")
        else:
            #print("H", this, len(this), ctl, text, high, len(l))
            this.add_type("Q1_HexDump")
            tmp = ov.OctetView(this)
            w = 64
            for rec in this.iter_rec():
                if len(rec) <= 128:
                    w = len(rec)
                ov.Octets(tmp, lo = rec.lo, hi = rec.hi, line_length=w, ).insert()
            tmp.add_interpretation(title="HexDump")
