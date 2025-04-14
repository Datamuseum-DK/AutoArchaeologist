#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   CR80 Wang WCS floppy disks
   ~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.generic import samesame
from autoarchaeologist.vendor.wang import wang_wps
from autoarchaeologist.vendor.wang import wang_text

import ddhf

class Wang(ddhf.DDHFExcavation):

    ''' CR80 Wang WCS floppy disks '''

    BITSTORE = (
        "CR/CR80/DOCS",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_examiner(wang_wps.WangWps)
        self.add_examiner(wang_text.WangText)
        self.add_examiner(samesame.SameSame)

if __name__ == "__main__":
    ddhf.main(
        Wang,
        html_subdir="cr80_wang",
        ddhf_topic = "CR80 Wang WCS documentation floppies",
        ddhf_topic_link = 'https://datamuseum.dk/wiki',
    )
