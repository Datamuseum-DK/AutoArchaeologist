#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Sharp MZ80 floppy interleave
   ============================
'''

from ...base import artifact

class Mz80BFloppies():

    def __init__(self, this):
        if this.top not in this.parents:
            return
        keys = set(x.key for x in this.iter_rec())
        key2 = set((x[0],0, x[2]) for x in keys)
        if len(keys) != len(key2):
            print(this, "MZ80-B K1", len(keys), "K2", len(key2))
            return

        if len(keys) == len(key2):
            for i in keys:
                if i[1] == 0 and i[2] == 11:
                    return
                if i[1] == 1 and i[2] == 10:
                    return

        l = [] 
        for frag in this.iter_rec():
            if len(keys) != len(key2):
                chs=(frag.key[0], frag.key[1], frag.key[2])
            else:
                chs=(frag.key[0], 0, frag.key[2])
            l.append(
                artifact.Record(
                    low=frag.lo,
                    frag=bytes(x^0xff for x in frag.frag),
                    key=chs,
                )
            )
        that = this.create(records=l)
        that.add_note("MZ-80B")
        if len(keys) == len(key2):
            that.add_note("Probe-CPM")
        #this.add_interpretation(self, this.html_interpretation_children)
        

