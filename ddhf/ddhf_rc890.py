#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Regnecentralen RC890 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
from ddhf import cpm_exc

class Rc890(cpm_exc.DdhfExcavationCpm):

    ''' All RC890 artifacts '''

    BITSTORE = (
        "RC/RC890",
    )

if __name__ == "__main__":
    ddhf.main(
        Rc890,
        html_subdir="rc890",
        ddhf_topic = 'RegneCentralen RC890',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC890'
    )
