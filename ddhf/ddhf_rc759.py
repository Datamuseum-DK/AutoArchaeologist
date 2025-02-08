#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Regnecentralen RC759 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf
import ddhf.cpm_exc

class Rc759(ddhf.DDHFExcavation):

    ''' All RC759 artifacts '''

    BITSTORE = (
        "-30002875",
        "RC/RC759",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ddhf.cpm_exc.std_cpm_excavation(self)

if __name__ == "__main__":
    ddhf.main(
        Rc759,
        html_subdir="rc759",
        ddhf_topic = 'RegneCentralen RC759 "Piccoline"',
        ddhf_topic_link = 'https://datamuseum.dk/wiki/RC_Piccoline'
    )
