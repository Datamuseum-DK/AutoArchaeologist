#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Christian Rovsing A/S CR80 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.vendor.christianrovsing import cr80_sysone
from autoarchaeologist.vendor.christianrovsing import cr80_fs2
from autoarchaeologist.vendor.intel import isis
from autoarchaeologist.generic import textfiles
from autoarchaeologist.vendor.zilog import mcz

import ddhf

class Cr80Floppy(ddhf.DDHFExcavation):
    ''' CR80 Floppy disk images'''

    BITSTORE = (
        "CR/CR80/SW",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(cr80_sysone.Cr80SystemOneInterleave)
        self.add_examiner(cr80_sysone.Cr80SystemOneFs)
        self.add_examiner(cr80_fs2.CR80_FS2Interleave)
        self.add_examiner(cr80_fs2.CR80_FS2)
        self.add_examiner(isis.IntelIsis)
        self.add_examiner(mcz.MCZRIO)
        self.add_examiner(textfiles.TextFile)

if __name__ == "__main__":
    ddhf.main(
        Cr80Floppy,
        html_subdir="cr80",
        ddhf_topic = "CR80 Hard and Floppy Disks",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/CR80',
    )
