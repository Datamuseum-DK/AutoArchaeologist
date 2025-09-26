#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   IBM Series/1 libraries
'''

from ...base import octetview as ov

class DirHdr(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            f00_=ov.Be32,
            f01_=ov.Be32,
            f02_=ov.Be16,
            f03_=ov.Be16,
            f04_=ov.Be16,
            f05_=ov.Be16,
            f06_=ov.Text(8),
            f08_=ov.Text(8),
        )

class DirEnt(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            name_=ov.Text(8),
            first_=ov.Be32,
            last_=ov.Be32,
            f03_=ov.Be16,
            f04_=ov.Be32,
            f05_=ov.Be32,
            f06_=ov.Be16,
            f07_=ov.Be32,
        )

class S1EdxLib(ov.OctetView):

    def __init__(self, this):
        if not this.has_name("EDXLIB"):
            return
        super().__init__(this)
        print(this, "EDXLIB")

        hdr = DirHdr(self, 0).insert()

        ptr = hdr.hi
        while this[ptr] > 0:
            y = DirEnt(self, ptr).insert()
            print(this, y.name.txt)
            z = ov.This(
                self,
                lo=y.first.val << 8,
                hi=(y.last.val + 1)<<8
            ).insert()
            z.that.add_name(y.name.txt)
            ptr = y.hi

        this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation(title="S1 EDXLIB")


