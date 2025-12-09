#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Alpha LSI
   ~~~~~~~~~

   This is very rudimentary.

   Filenames are two 16 bit words, probably Radix-40 ?
   Data disks are an entirely different format.
   Some Texts have bit7 set.
   Some textfiles are in reverse byte order, and reversed lines:
   	dd conv=swab | dd conv=parnone | rev
'''

from autoarchaeologist.vendor.computer_automation import alpha_lsi

from autoarchaeologist.base import type_case

import ddhf

class AlphaLsi(ddhf.DDHFExcavation):

    ''' All AlphaLsi artifacts '''

    MAX_LINES=2000

    BITSTORE = (
        "COMPANY/COMPUTER_AUTOMATION",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(alpha_lsi.AlphaLsi)

        nt = type_case.TypeCase("AlphaLsi")
        for i, g in enumerate(self.type_case.slugs):
            if i < 0x80:
                nt.slugs[i] = g
                nt.slugs[i|0x80] = g
        self.type_case = nt

if __name__ == "__main__":
    ddhf.main(
        AlphaLsi,
        html_subdir="alphalsi",
        ddhf_topic = "Alpha LIS",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/',
    )
