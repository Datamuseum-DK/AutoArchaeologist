#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Zilog MCZ/1 Artifacts from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.vendor import zilog
from autoarchaeologist.generic import textfiles

import ddhf

class ZilogMCZ(ddhf.DDHFExcavation):

    ''' Zilog MCZ Floppy Disks '''

    BITSTORE = (
        "COMPANY/ZILOG",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        zilog.mcz_defaults(self)
        self.add_examiner(textfiles.TextFile)

if __name__ == "__main__":
    ddhf.main(
        ZilogMCZ,
        html_subdir="zilog_mcz",
        ddhf_topic = "Zilog MCZ Floppy Disks",
    )
