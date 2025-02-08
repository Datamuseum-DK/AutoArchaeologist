#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Intel ISIS Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.vendor.intel import isis
from autoarchaeologist.generic import textfiles

import ddhf

class IntelISIS(ddhf.DDHFExcavation):
    ''' Intel ISIS Floppy Disks '''

    BITSTORE = (
        "COMPANY/INTEL/ISIS",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_examiner(isis.IntelIsis)
        self.add_examiner(textfiles.TextFile)

if __name__ == "__main__":
    ddhf.main(
        IntelISIS,
        html_subdir="intel_isis",
        ddhf_topic = "Intel ISIS Floppy Disks",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/CR80',
    )
