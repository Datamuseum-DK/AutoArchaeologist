#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   ICL Comet32 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.base import type_case

from autoarchaeologist.generic import textfiles
from autoarchaeologist.generic import samesame

from autoarchaeologist.os.unix import unix_fs

from autoarchaeologist.vendor.icl import comet32

import ddhf

class Comet32(ddhf.DDHFExcavation):

    '''
    Comet32 hard-disk images
    '''

    BITSTORE = (
        "COMPANY/ICL/COMET/DISK",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # The demo programs for Hanovermesse 1985 are in german.
        self.type_case = type_case.WellKnown("iso8859-1")

        self.add_examiner(*comet32.ALL)
        self.add_examiner(unix_fs.FindUnixFs)
        self.add_examiner(textfiles.TextFile)
        self.add_examiner(samesame.SameSame)

if __name__ == "__main__":
    ddhf.main(
        Comet32,
        html_subdir="comet32",
        ddhf_topic = "ICL Comet 32",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/ICL_Comet',
    )
