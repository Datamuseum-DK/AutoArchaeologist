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
from ddhf import cpm_exc

class Butler(cpm_exc.DdhfExcavationCpm):
    ''' All Butler artifacts '''

    BITSTORE = (
        "COMPANY/BOGIKA",
    )

if __name__ == "__main__":
    ddhf.main(
        Butler,
        html_subdir="butler",
        ddhf_topic = 'Bogika Butler',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/BDS_Butler'
    )
