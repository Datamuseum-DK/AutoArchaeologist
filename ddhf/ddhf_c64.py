#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   C=64 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import ddhf

import autoarchaeologist.vendor.commodore.c64.c64_disk as c64d
from autoarchaeologist.generic import textfiles

class C64(ddhf.DDHFExcavation):
    ''' All C64 artifacts '''

    BITSTORE = (
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(c64d.C64Disk)
        self.add_examiner(textfiles.TextFile)

if __name__ == "__main__":
    ddhf.main(
        C64,
        html_subdir="c64",
        ddhf_topic = 'C=64',
        ddhf_topic_link = 'https://datamuseum.dk/wiki'
    )
