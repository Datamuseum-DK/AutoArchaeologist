#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Intel HEX files
'''

from ..base import octetview as ov

class Record(ov.Octets):
    def __init__(self, tree, lo, hi, octets):
        super().__init__(tree, lo = lo, hi = hi)
        self.octets = octets

    def __getitem__(self, idx):
        return self.octets[idx]

    def render(self):
        yield ':' + self.octets.hex()

class IntelHex(ov.OctetView):

    def __init__(self, this):
        if this.has_type("IntelHex"):
            return
        super().__init__(this)

        self.recs = []
        ptr = 0
        while ptr < len(this):
            at = ptr
            while ptr < len(this) and this[ptr] in (0x00, 0x20, 0x80, 0xa0):
                ptr += 1
            if ptr >= len(this):
                break
            b = this[ptr] & 0x7f
            ptr += 1
            if b != 0x3a:
                continue
            l = []
            while ptr < len(this):
                b = this[ptr] & 0x7f
                if b not in b'0123456789abcdefABCDEF':
                    break
                ptr += 1
                l.append(b)
            if not l:
                continue
            txt = bytes(l).decode('ascii')
            if len(txt) & 1:
                print("ODD length", txt)
                continue
            rec = bytes.fromhex(txt)
            if 5 + rec[0] != len(rec):
                print("WRONG length", rec.hex())
                continue
            if sum(rec) & 0xff:
                print("BAD checksum", rec.hex(), sum(rec))
                continue
            
            while ptr < len(this) and this[ptr] & 0x7f in (10, 13):
                ptr += 1
            self.recs.append(Record(self, at, ptr, rec).insert())
        if not self.recs:
            return
        lo = None
        hi = None
        l = []
        for rec in self.recs:
            #print("R", hex(rec.lo), hex(rec.hi), rec)
            if lo is None:
                lo = rec.lo
            if hi is not None and rec.lo != hi:
                self.mkchild(lo, hi, l)
                print("Range", hex(lo), hex(hi))
                hi = None
                lo = rec.lo
                continue
            l.append(rec)
            hi = rec.hi
            if rec[3] == 0x01:
                self.mkchild(lo, hi, l)
                print("File", hex(lo), hex(hi))
                hi = None
                lo = None
        if lo is not None:
            print("RangeZ", hex(lo), hex(hi))
            self.mkchild(lo, hi, l)

    def mkchild(self, lo, hi, recs):
        l = []
        for i in recs:
            frag = (':' + i.octets.hex() + '\n').encode('ascii')
            l.append(frag)
        that = self.this.create(
            start=lo,
            stop=hi,
            records=l,
        )
        that.add_type("IntelHex")
