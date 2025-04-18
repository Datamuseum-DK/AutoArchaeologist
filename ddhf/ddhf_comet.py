#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   ICL Comet Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
from ddhf import cpm_exc

class Comet(cpm_exc.DdhfExcavationCpm):

    ''' All Comet artifacts '''

    BITSTORE = (
        "COMPANY/ICL/COMET",
    )

if __name__ == "__main__":
    ddhf.main(
        Comet,
        html_subdir="comet",
        ddhf_topic = 'ICL Comet',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/ICL_Comet'
    )
