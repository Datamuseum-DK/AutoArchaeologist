#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Rational R1000/400 Diag Processor Firmware from Datamuseum.dk's BitStore
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from autoarchaeologist.vendor.rational import r1k_diag

import ddhf

class R1KDIPROC(ddhf.DDHFExcavation):

    ''' Rational R1000/400 Diag Processor firmware '''

    BITSTORE = (
        "30002517",
        "30003041",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_examiner(r1k_diag.R1kDiagFirmWare)

if __name__ == "__main__":
    ddhf.main(
        R1KDIPROC,
        html_subdir="r1k_diproc",
        ddhf_topic = "Rational R1000/400 Diag Processor Firmware",
        ddhf_topic_link = 'https://datamuseum.dk/wiki/Rational/R1000s400',
    )
