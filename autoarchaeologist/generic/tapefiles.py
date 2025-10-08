#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Split unloved tapes into individual files
'''

class UnlovedTapes():
    def __init__(self, this):
        if not this.has_type("SimhTapContainer"):
            return
        if this.rp_interpretations:
            return
        print(this, self, len(this.rp_interpretations))
        start = None
        recs = []
        nf = 0
        for rec in this.iter_rec():
            #print("R", len(rec), rec)
            if start is None:
                start = rec
                recs = [ rec ]
            elif rec.key[0] != start.key[0]:
                #print(recs[0], recs[-1])
                #this.create(records = recs)
                that = this.create(start=start.lo, stop=rec.lo)
                print("T", nf, len(that), len(recs), min(len(x) for x in recs), max(len(x) for x in recs))
                start = rec
                recs = [ rec ]
                nf += 1
            else:
                recs.append(rec)
        #this.create(records = recs)
        this.create(start=start.lo, stop=len(this))
        this.add_interpretation(self, this.html_interpretation_children)
        this.taken = True
