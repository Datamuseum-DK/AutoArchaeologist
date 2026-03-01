#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   RC3600 Tapes
   ============

'''

class RC3600Tape():
    ''' ... '''
    def __init__(self, this):
        if not this.top in this.parents:
            return

        files = []
        names = {}
        for rec in this.iter_rec():
            if len(rec.key) != 2:
                # disk
                return
            if rec.key[-1] != 0:
                files[-1].append(rec)
                continue
            files.append([])
            name = self.is_name(rec)
            if name is not None:
                names[rec.key] = name
            files[-1].append(rec)
        if not names:
            return
        for frags in files:
            name = names.get(frags[0].key)
            if name:
                that = this.create(start = frags[0].lo, stop=frags[-1].hi, records = frags[1:])
                that.add_name(this.type_case.decode_long(name))
            else:
                this.create(start = frags[0].lo, stop=frags[-1].hi, records = frags)
        this.taken = True

    def is_name(self, rec):
        ''' Determine if a tape-record holds a file name '''
        if len(rec) > 128:
            return None
        b = rec.frag.tobytes().rstrip(b'\x00')
        while b[-1] in (10, 13):
            b = b[:-1]
        if max(b) > 126:
            return None
        if min(b) < 32:
            return None
        return b
