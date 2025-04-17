#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Intergraph disk partitioning
   ----------------------------

   See pdf page 960 in :
      http://bitsavers.org/pdf/intergraph/clix/DSYS18412_Edition1_CLIX_Programmers_and_Users_Reference_Manual_199001.pdf

   Note that the stated magic number is wrong, it spells "sane" in
   lower case rather than upper case ASCII.
'''

from ...base import octetview as ov
from ...base import namespace as ns

class NameSpace(ns.NameSpace):
    ''' ... '''

    TABLE = (
        ("r", "number"),
        ("r", "modifier"),
        ("r", "size"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        return self.ns_priv + super().ns_render()

class Hdr(ov.Struct):
    ''' ... '''

    def __init__(self, up, lo):
        super().__init__(
            up,
            lo,
            naked=True,
            partno_=ov.Octet,
            modifier_=ov.Octet,
            size_=ov.Le32,
            magic_=ov.Le32,
        )

class DiskPar(ov.OctetView):
    ''' ... '''

    def __init__(self, this):
        if not this.top in this.parents:
            return

        super().__init__(this)

        self.namespace = NameSpace(
            name = '',
            root = this,
            separator = "",
        )

        adr = 0
        while adr < len(this):
            y = Hdr(self, adr)
            if y.magic != 0x656e6173:
                break
            if y.size == 0:
                break
            if adr + (y.size << 9) > len(this):
                break
            # z = this.create(start=adr, stop=adr + (1<<9))
            adr += 1<<9
            w = this.create(start=adr, stop=adr + (y.size<<9))
            w.add_note("partno_%02x" % y.partno)
            w.add_note("modifier_%02x" % y.modifier)
            w.add_type("intergraph_partition")
            adr += y.size << 9
            NameSpace(
                name = "%02x.%02x" % (y.partno, y.modifier),
                parent = self.namespace,
                this = w,
                priv = [hex(y.partno), hex(y.modifier), hex(y.size)]
            )
        if adr > 0:
            this.add_interpretation(self, self.namespace.ns_html_plain)
