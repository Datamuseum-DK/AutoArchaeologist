#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   CBM900 ar(1) files
   ------------------
'''

from ....base import octetview as ov
from ....base import namespace
from ....os.unix.unix_stat import UnixStat

class ArHdr(ov.Struct):
    ''' see ⟦309830465⟧ '''

    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            name_=ov.Text(14),
            time_=ov.Le32,
            gid_=ov.Le16,
            uid_=ov.Le16,
            mode_=ov.Le16,
            size_=ov.L1032,
        )
        self.name.txt = self.name.txt.rstrip()

class NameSpace(namespace.NameSpace):
    ''' ... '''

    stat = UnixStat()

    TABLE = (
        ( "l", "mode"),
        ( "r", "uid"),
        ( "r", "gid"),
        ( "r", "size"),
        ( "r", "time"),
        ( "l", "name"),
        ( "l", "artifact"),
    )

    def ns_render(self):
        arhdr = self.ns_priv
        return [
            self.stat.mode_bits(arhdr.mode.val),
            arhdr.uid.val,
            arhdr.gid.val,
            arhdr.size.val,
            self.stat.timestamp(arhdr.time.val),
        ] + super().ns_render()

class CBM900Ar(ov.OctetView):
    ''' CBM900 ar(1) files '''

    def __init__(self, this):
        if len(this) < 30:
            return
        super().__init__(this)
        y = ov.Le16(self, 0)
        if y.val != 0o177535:
            return
        y.insert()
        this.type = "Ar_file"
        this.add_note("Ar_file")
        offset = y.hi
        self.namespace = NameSpace(
            name='',
            root=this,
            separator="",
        )
        while offset < len(this):
            y = ArHdr(self, offset).insert()
            offset = y.hi
            if offset + y.size.val > len(this):
                break
            z = ov.This(self, lo=offset, width=y.size.val).insert()
            offset = z.hi
            NameSpace(y.name.txt, self.namespace, this=z.that, priv=y)
        this.add_interpretation(self, self.namespace.ns_html_plain)
        self.add_interpretation()
