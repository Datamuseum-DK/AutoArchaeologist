#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Jet Computer Jet80 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
from ddhf import cpm_exc

class Jet80(cpm_exc.DdhfExcavationCpm):

    ''' All Jet80 artifacts '''

    BITSTORE = (
        "JET80",
    )

if __name__ == "__main__":
    ddhf.main(
        Jet80,
        html_subdir="jet80",
        ddhf_topic = 'Jet Computer Jet80',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Jet_Computer_JET-80'
    )
