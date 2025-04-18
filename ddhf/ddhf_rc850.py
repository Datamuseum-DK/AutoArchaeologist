#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Regnecentralen RC850 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
from ddhf import cpm_exc

class Rc850(cpm_exc.DdhfExcavationCpm):

    ''' All RC850 artifacts '''

    BITSTORE = (
        "RC/RC850/CPM",
    )

if __name__ == "__main__":
    ddhf.main(
        Rc850,
        html_subdir="rc850",
        ddhf_topic = 'RegneCentralen RC850',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC850'
    )
