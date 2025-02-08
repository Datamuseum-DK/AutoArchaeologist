#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   GIER Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.vendor.regnecentralen import gier_text
from autoarchaeologist.generic import samesame

import ddhf

class GIER(ddhf.DDHFExcavation):

    ''' All GIER artifacts '''

    BITSTORE = (
        "GIER/ALGOL_4",
        "GIER/ALGOL_II",
        "GIER/ALGOL_III",
        "GIER/ASTRONOMY",
        "GIER/CHEMISTRY",
        "GIER/DEMO",
        "GIER/GAMES",
        "GIER/HELP",
        "GIER/HELP3",
        "GIER/MATHEMATICS",
        "GIER/MISC",
        "GIER/MUSIC",
        "GIER/OTHER_SCIENCE",
        "GIER/TEST",
        "GIER/UTIL",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(gier_text.GIER_Text)
        self.add_examiner(samesame.SameSame)

if __name__ == "__main__":
    ddhf.main(
        GIER,
        html_subdir="gier",
        ddhf_topic = "RegneCentralen GIER Computer",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/GIER',
    )
