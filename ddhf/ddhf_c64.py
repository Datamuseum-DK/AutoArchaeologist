#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   C64 artifacts
   ~~~~~~~~~~~~~
'''

from autoarchaeologist.base import type_case

from autoarchaeologist.generic import samesame
from autoarchaeologist.generic import textfiles
from autoarchaeologist.vendor.commodore import c64

import ddhf

class C64(ddhf.DDHFExcavation):

    ''' All C64 artifacts '''

    BITSTORE = (
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # self.type_case = DomusDS2089()

        self.add_examiner(*c64.EXAMINERS)
        self.add_examiner(textfiles.TextFile)
        self.add_examiner(samesame.SameSame)


if __name__ == "__main__":
    ddhf.main(
        C64,
        html_subdir="c64",
        ddhf_topic = "Commodore 64",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Commodore_64',
    )
