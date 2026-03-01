#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   PtsSource
   =========

   Source (.SC) files, rendered as text

   Usage
   -----

   .. code-block:: none

       from autoarchaeologist.vendor.philipsdatasystems import pts_source
       …
       self.add_examiner(*pts_source.ALL)

   Notes
   -----

   Reverse engineered from samples.

   Test input
   ----------

   * COMPANY/PHILIPS/TAPE

   Documentation
   -------------

   None identified.

'''

from ...base import octetview as ov


class Head(ov.Struct):
    ''' ... '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            h00_=ov.Be16,
            h01_=ov.Be16,
            more=True,
        )
        if self.h00.val >= 84:
            pass
        elif self.h00.val == 4:
            self.add_field("t00", ov.Be16)
            self.add_field("t01", ov.Be16)
        elif self.h00.val < 4:
            pass
        elif self.hi + self.h00.val > len(self.tree.this):
            pass
        else:
            self.add_field("text", ov.Text(self.h00.val - 4))
            self.add_field("t00", ov.Be16)
            self.add_field("t01", ov.Be16)
        self.done()

class PtsSource(ov.OctetView):
    ''' ... '''

    def __init__(self, this):
        i = this.get_note("pts_type")
        if not i or i[0]['args'] not in ("SC", "UF",):
            return

        #print(this, "PtsSource", i, hex(len(this)))
        self.this = this

        super().__init__(this, line_length=80)

        with this.add_utf8_interpretation("PTS(SC)") as file:
            ptr = 0
            while ptr + 8 < len(this):
                y = Head(self, ptr).insert()
                ptr = y.hi
                if hasattr(y, "text"):
                    file.write(y.text.full_text() + "\n")
                elif y.h00.val == 4:
                    file.write("\n")

                if y.h00.val & 0xe000:
                    break

        self.add_interpretation(title="HexDump", more=True)

ALL= [
    PtsSource
]
