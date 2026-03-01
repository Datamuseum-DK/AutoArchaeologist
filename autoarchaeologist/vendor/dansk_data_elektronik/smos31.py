#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   SMOS new style boot images
   ==========================
'''

import time

from ...base import octetview as ov
from ...base import namespace as ns

class NameSpace(ns.NameSpace):
    ''' ... '''

    TABLE = [
        ("l", "timestamp"),
        ("r", "start"),
        ("r", "length"),
        ("r", "f03"),
        ("r", "f04"),
        ("r", "f05"),
    ] + ns.NameSpace.TABLE

class DirEnt(ov.Struct):
    ''' ... '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            name_=ov.Text(8),
            timestamp_=ov.Be32,
            start_=ov.Be32,
            length_=ov.Be32,
            f03_=ov.Be32,
            f04_=ov.Be32,
            f05_=ov.Be32,
        )

class Smos31(ov.OctetView):
    ''' SMOS new style boot images '''

    def __init__(self, this):
        if not this.top in this.parents:
            return

        if this[:8] != b'smos V31':
            return

        this.add_note("smos.v31")
        super().__init__(this)

        pns = NameSpace(name="", root=this)
        for adr in range(0x20, 0x200, 0x20):
            if this[adr] == 0:
                break
            y = DirEnt(self, adr).insert()
            z = ov.This(
                self,
                lo=y.start.val,
                hi = y.start.val + y.length.val
            ).insert()
            NameSpace(
                name = y.name.txt.rstrip(),
                this = z.that,
                parent = pns,
                flds = [
                    time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(y.timestamp.val)),
                    hex(y.start.val),
                    hex(y.length.val),
                    "0x%08x" % y.f03.val,
                    "0x%08x" % y.f04.val,
                    "0x%08x" % y.f05.val,
                ],
            )

        this.add_interpretation(self, pns.ns_html_plain)
        self.add_interpretation(more=True)
