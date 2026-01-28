#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Philips Data Systems
   ~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.generic import samesame
from autoarchaeologist.generic import textfiles

from autoarchaeologist.vendor.philipsdatasystems import pts_tape
from autoarchaeologist.vendor.philipsdatasystems import pts_source

import ddhf

class Philips(ddhf.DDHFExcavation):
    ''' '''

    BITSTORE = (
        "COMPANY/PHILIPS/TAPE",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(pts_tape.PtsTape)
        self.add_examiner(pts_source.PtsSource)
        self.add_examiner(textfiles.TextFile)
        self.add_examiner(samesame.SameSame)

        self.type_case.set_slug(0x5c, " ", "\t")

if __name__ == "__main__":
    ddhf.main(
        Philips,
        html_subdir="philips",
        ddhf_topic = "Philips Data Systems",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Philips',
    )
