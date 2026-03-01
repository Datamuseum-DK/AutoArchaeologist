#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   RC3600 Flexible disc MT Emulator
   ================================

   See: RCSL 43-GL-7420

   Some disks use sector interleave = 7

'''

import struct

from ...base import octetview as ov
from ...base import namespace

SIGNATURE_RAW = bytes.fromhex('''
    54 49 4d 45 20 4f 55 54 20 44 49 53 43 00
    42 0e 0c 02
    48 41 52 44 20 45 52 52 4f 52 20 4f 4e 20 44 49 53 43 2c 53 54 41
    54 45 3a 20 00
''')

SIGNATURE_INTERLEAVE = bytes.fromhex('''
    54 49 4d 45 20 4f 55 54 20 44 49 53 43 00
    42 0b 0c 02
    48 41 52 44 20 45 52 52 4f 52 20 4f 4e 20 44 49 53 43 2c 53 54 41
    54 45 3a 20 00
''')

print(SIGNATURE_RAW)
print(SIGNATURE_INTERLEAVE)

class NameSpace(namespace.NameSpace):
    ''' ... '''

class Filedata(ov.Opaque):
    ''' ... '''

    def __init__(self, tree, lo, fn):
        super().__init__(tree, lo, width=1<<7)
        #self.rendered = "Filedata(%s, 0x%d)" % (fn, nbr)
        self.rendered = "Filedata(%s)" % (fn)

class Rc3600FdTape(ov.OctetView):
    ''' RCSL 43-GL-7420 '''
    def __init__(self, this):
        if not this.top in this.parents:
            return
        if this.has_type("RC3600_FD_Tape"):
            return
        if len(this) != 77 * 26 * 128:
            return

        if this.tobytes().find(SIGNATURE_RAW) > 0:
            self.interleave = False
            self.this = this
        elif this.tobytes().find(SIGNATURE_INTERLEAVE) > 0:
            self.interleave = True
            self.this = this
        else:
            return

        super().__init__(this)

        idx = ov.Array(64, ov.Be16, vertical=True)(self, 0xb80).insert()

        prev_offset = 26 << 7
        objs = []
        for n, v in enumerate(idx[:-1]):
            if idx[n+1].val & 0x8000:
                break
            this_offset = v.val << 7
            if this_offset == 0 or this_offset > len(this):
                continue
            if this_offset < prev_offset:
                break
            next_offset = idx[n+1].val << 7
            objs.append((idx[n].val, idx[n+1].val))
            prev_offset = this_offset

        if len(objs) == 0:
            return

        this.add_note("Rc3600FdTape")

        ns = NameSpace(
            name="",
            root=this,
        )

        for n, w in enumerate(objs):
            fm, to = w
            p = self.xlat(fm)
            yn = ov.Text(128)(self, p).insert()
            nm = yn.txt.strip()
            if nm == "":
                nm="#%02d" % n
            frags = []
            for b in range(fm + 1, to):
                p = self.xlat(b)
                frags.append(self.this[p:p+0x80])
                Filedata(self, p, nm).insert()
            y = this.create(records=frags)
            y.add_name(nm)
            NameSpace(
                parent=ns,
                name=nm,
                this=y,
            )

        this.add_interpretation(self, ns.ns_html_plain)
        self.add_interpretation(more=True, title="Rc3600FdTape")


    def xlat(self, n):
        if not self.interleave:
            return n << 7
        cyl = n // 26
        sect = n % 26
        isect = (sect * 7) % 26
        phys = cyl * 26 + isect
        return phys << 7
