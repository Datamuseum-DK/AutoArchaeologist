#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Q1 computer artifacts
   ~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.base import type_case
from autoarchaeologist.generic import samesame

from autoarchaeologist.vendor.q1 import q1_microlite
from autoarchaeologist.vendor.q1 import q1_text

import ddhf

class Q1TypeCase(type_case.Ascii):
    ''' ... '''

    def __init__(self):
        super().__init__()
        self.set_slug(0x5b, "Ä", "Ä")
        self.set_slug(0x5c, "Ö", "Ö")
        self.set_slug(0x5d, "Å", "Å")
        self.set_slug(0x7b, "ä", "ä")
        self.set_slug(0x7c, "ö", "ö")
        self.set_slug(0x7d, "å", "å")
        self.set_slug(0x7f, " ", "¬")
        for i in range(32):
            if i not in self.slugs:
                self.set_slug(i, " ", "┣%02x┫" % i)

class Q1(ddhf.DDHFExcavation):

    ''' Q1 computer artifacts '''

    #MAX_LINES = 1000

    BITSTORE = (
        #"30006592",
        "-30006119",
        "-30006120",
        "-30006121",
        "-30006122",
        "-30006123",
        "-30006124",
        "-30006125",
        "-30006126",
        "COMPANY/Q1_CORPORATION",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_examiner(q1_microlite.Q1Microlite)
        self.add_examiner(samesame.SameSame)
        self.add_examiner(q1_text.Q1Text)
        self.type_case = Q1TypeCase()

if __name__ == "__main__":
    ddhf.main(
        Q1,
        html_subdir="q1",
        ddhf_topic = "Q1 computer",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Q1_Microlite',
    )
