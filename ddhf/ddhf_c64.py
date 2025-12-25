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

    XBITSTORE = (
        #"-30001762",		# Defective
        #"RC/RC3600/COMAL",
        #"RC/RC3600/DOMUS",
        #"RC/RC3600/SW",
        #"RC/RC3600/HW",
        #"RC/RC3600/LOADER",
        #"RC/RC3600/MUSIL",
        #"RC/RC3600/PAPERTAPE",
        "COMPANY/DATA_GENERAL/NOVA",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # self.type_case = DomusDS2089()

        self.add_examiner(*c64.EXAMINERS)
        self.add_examiner(textfiles.TextFile)
        self.add_examiner(samesame.SameSame)


if __name__ == "__main__":
    #import sys
    #sys.argv.append('/critter/DDHF/2025/20251120_mz80_fd/C64/50004990/_.ft.CBM64.cache')
    #sys.argv.append('/critter/DDHF/2025/20251120_mz80_fd/C64/50004991/_.ft.CBM64.cache')
    #sys.argv.append('/critter/DDHF/2025/20251120_mz80_fd/C64/50004992/_.ft.CBM64.cache')
    ddhf.main(
        C64,
        html_subdir="c64",
        ddhf_topic = "Commodore 64",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC/RC7000',
    )
