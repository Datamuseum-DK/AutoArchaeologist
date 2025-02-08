#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Zilog MCZ/1 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.vendor.zilog import mcz
from autoarchaeologist.vendor.zilog import zdos_basic
from autoarchaeologist.generic import textfiles

import ddhf

class ZilogMCZ(ddhf.DDHFExcavation):

    ''' Zilog MCZ Floppy Disks '''

    BITSTORE = (
        "COMPANY/ZILOG",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(mcz.MCZRIO)
        self.add_examiner(zdos_basic.ZdosBasic)
        self.add_examiner(textfiles.TextFile)

if __name__ == "__main__":
    ddhf.main(
        ZilogMCZ,
        html_subdir="zilog_mcz",
        ddhf_topic = "Zilog MCZ Floppy Disks",
    )
