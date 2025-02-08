#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Christian Rovsing CP/M Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
import ddhf.cpm_exc

class CrCpm(ddhf.DDHFExcavation):

    ''' All CR CP/M artifacts '''

    BITSTORE = (
        "CR/CR7",
        "CR/CR8",
        "CR/CR16",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ddhf.cpm_exc.std_cpm_excavation(self)

if __name__ == "__main__":
    ddhf.main(
        CrCpm,
        html_subdir="cr_cpm",
        ddhf_topic = 'Christian Rovsing CR7, CR8 & CR16 CP/M',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Christian_Rovsing_A/S'
    )
