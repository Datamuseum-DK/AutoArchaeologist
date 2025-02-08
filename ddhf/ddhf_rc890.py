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
import ddhf.cpm_exc

class Rc890(ddhf.DDHFExcavation):

    ''' All RC890 artifacts '''

    BITSTORE = (
        "RC/RC890",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ddhf.cpm_exc.std_cpm_excavation(self)

if __name__ == "__main__":
    ddhf.main(
        Rc890,
        html_subdir="rc890",
        ddhf_topic = 'RegneCentralen RC890',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC890'
    )
