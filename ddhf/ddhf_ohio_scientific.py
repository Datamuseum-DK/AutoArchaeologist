#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Ohio Scientific Floppies
   ~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.base import type_case

from autoarchaeologist.generic import textfiles
from autoarchaeologist.generic import samesame

from autoarchaeologist.vendor.ohio_scientific import ohio_scientific

import ddhf

class OsiDS2089(type_case.DS2089):
    ''' RC3600 typical use charset '''

    def __init__(self):
        super().__init__()
        self.set_slug(0x00, ' ', '«nul»', self.EOF)
        self.set_slug(0x0a, ' ', '\n')
        self.set_slug(0x0d, ' ', '\n')

class TextFile(textfiles.TextFile):
    ''' ... '''

    TYPE_CASE = OsiDS2089()
    MAX_TAIL = 11 << 10

class OhioScientific(ddhf.DDHFExcavation):
    ''' ... '''

    BITSTORE = (
        "COMPANY/OHIO_SCIENTIFIC",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(*ohio_scientific.examiners)
        self.add_examiner(TextFile)
        self.add_examiner(samesame.SameSame)

if __name__ == "__main__":
    ddhf.main(
        OhioScientific,
        html_subdir="ohio_scientific",
        ddhf_topic = "Ohio Scientific Inc.",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/',
    )
