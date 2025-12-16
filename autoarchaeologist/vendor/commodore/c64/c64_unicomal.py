#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

''' ... '''

from ....base import octetview as ov
from ....base import type_case

class Statement(ov.Struct):
    ''' One COMAL statement'''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            lineno_=ov.Le16,
            size_=ov.Octet,
            more = True,
        )
        if 0 and self.size.val > 3:
            self.add_field("body", self.size.val - 3)
        self.done()

class C64Unicomal(ov.OctetView):
    ''' ... '''

    def __init__(self, this):
        if len(this)  < 8:
            return

        if this[0] != 0xff:
            return
        if this[1] != 0xff:
            return

        print(this, self.__class__.__name__, len(this))

        super().__init__(this)
        this.add_note("C64-UNICOMAL")

        ptr = 0x9
        for n in range(500):
            y = Statement(self, ptr).insert()
            print(this, "Y", hex(ptr), y)
            ptr += y.size.val
            if y.lineno.val == 0 or y.size.val == 0 or ptr > len(this):
                break

        self.add_interpretation(elide=0)
