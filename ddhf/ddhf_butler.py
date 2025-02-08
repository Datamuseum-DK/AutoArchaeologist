#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   ICL Butler Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
import ddhf.cpm_exc

class Butler(ddhf.DDHFExcavation):
    ''' All Butler artifacts '''

    BITSTORE = (
        "COMPANY/BOGIKA",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        ddhf.cpm_exc.std_cpm_excavation(self)

if __name__ == "__main__":
    ddhf.main(
        Butler,
        html_subdir="butler",
        ddhf_topic = 'Bogika Butler',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/BDS_Butler'
    )
